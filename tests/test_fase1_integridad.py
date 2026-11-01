"""Fase 1.3-1.6: transacciones, catalogo, captura sin ceros, cierre de
ejercicios e historial (C-02, C-03, A-03, A-07, A-08, M-05, M-06)."""
import io
from decimal import Decimal

import pandas as pd
import pytest
import streamlit
from openpyxl import Workbook
from sqlalchemy.exc import IntegrityError

from database import connection
from database.connection import init_db, render_scope, session_scope
from database.enums import CategoriaPrincipal as Cat
from database.enums import EstadoEjercicio, EstadoRegistro
from database.enums import NaturalezaSaldo as Nat
from database.enums import TipoEstadoFinanciero as Tipo
from database.models import BalanceEntry, ChangeHistory, FiscalPeriod
from database.repositories import (
    CatalogoProtegidoError,
    EjercicioCerradoError,
    close_fiscal_period,
    delete_entry,
    delete_fiscal_period,
    delete_initial_balance,
    get_account_by_codigo,
    get_company,
    get_entries_map,
    get_fiscal_period,
    get_or_create_fiscal_period,
    list_fiscal_periods,
    list_history,
    lote,
    reopen_fiscal_period,
    save_company,
    set_statement_status,
    update_account,
    upsert_entry,
    upsert_initial_balance,
)
from database.seed import seed_default_accounts


@pytest.fixture()
def bd(tmp_path):
    path = tmp_path / "fase1.db"
    init_db(db_path=path)
    with session_scope() as s:
        seed_default_accounts(s)
        save_company(s, nombre_legal="Empresa Prueba", nombre_comercial="EP", actividad_economica="x",
                     pais="SV", moneda="USD", anio_inicial_analisis=2021)
    yield path
    connection.dispose_engine()


def _id(s, codigo):
    return get_account_by_codigo(s, codigo).id


def _historial(s):
    return s.query(ChangeHistory).count()


# --------------------------------------------------------------- 1.3 transacciones

def test_render_scope_nunca_confirma(bd):
    with render_scope() as s:
        get_or_create_fiscal_period(s, 2024)
        s.flush()
    with session_scope() as s:
        assert get_fiscal_period(s, 2024) is None


def test_ejecutar_escritura_revierte_y_muestra_error(bd, monkeypatch):
    from components.transacciones import ejecutar_escritura

    errores = []
    monkeypatch.setattr(streamlit, "error", lambda msg, *a, **k: errores.append(msg))
    with render_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.commit()
        n = _historial(s)

        def accion_que_falla():
            upsert_entry(s, fiscal_period_id=p.id, account_id=_id(s, "1001"), valor="10", tipo=Tipo.BALANCE)
            s.add(BalanceEntry(fiscal_period_id=p.id, account_id=_id(s, "1001"), valor=Decimal("5")))
            s.flush()  # UNIQUE (ejercicio, cuenta) -> IntegrityError

        ok, _ = ejecutar_escritura(s, accion_que_falla, descripcion="probar")
        assert ok is False
        assert errores and "ya existe un registro" in errores[0]
        assert get_entries_map(s, p.id, Tipo.BALANCE) == {}
        assert _historial(s) == n


def test_ejecutar_escritura_no_oculta_errores_inesperados(bd):
    from components.transacciones import ejecutar_escritura

    def falla():
        raise RuntimeError("defecto de programación")

    with render_scope() as s, pytest.raises(RuntimeError):
        ejecutar_escritura(s, falla, descripcion="probar")


# --------------------------------------------------------------- 1.4 catalogo

def test_cuenta_con_movimientos_permite_nombre_naturaleza_y_orden(bd):
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        upsert_entry(s, fiscal_period_id=p.id, account_id=_id(s, "1001"), valor="500", tipo=Tipo.BALANCE)
        cuenta = update_account(s, _id(s, "1001"), nombre="Caja y bancos", orden_presentacion=5,
                                naturaleza_saldo=Nat.DEUDORA, categoria_principal=Cat.ACTIVO)
        assert (cuenta.nombre, cuenta.orden_presentacion) == ("Caja y bancos", 5)
        h = s.query(ChangeHistory).filter_by(tabla_afectada="account", campo="nombre").one()
        assert h.account_id == cuenta.id and h.registro_id == cuenta.id


@pytest.mark.parametrize("cambio", [
    {"categoria_principal": Cat.PASIVO},
    {"subcategoria": None, "categoria_principal": Cat.INGRESOS},
])
def test_reclasificar_con_saldos_iniciales_tambien_bloqueado(bd, cambio):
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        upsert_initial_balance(s, fiscal_period_id=p.id, account_id=_id(s, "1001"), valor="10")
        with pytest.raises(CatalogoProtegidoError, match="cree una cuenta nueva"):
            update_account(s, _id(s, "1001"), **cambio)


def test_reclasificar_sin_movimientos_sigue_permitido(bd):
    from database.enums import Subcategoria as Sub

    with session_scope() as s:
        cuenta = update_account(s, _id(s, "1003"), subcategoria=Sub.NO_CORRIENTE)
        assert cuenta.subcategoria == Sub.NO_CORRIENTE


# --------------------------------------------------------------- 1.5 cierre y borrado

def test_ejercicio_cerrado_rechaza_todas_las_escrituras(bd):
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        upsert_entry(s, fiscal_period_id=p.id, account_id=_id(s, "1001"), valor="100", tipo=Tipo.BALANCE)
        close_fiscal_period(s, p.id)
        assert p.estado == EstadoEjercicio.CERRADO and p.fecha_cierre is not None
    with session_scope() as s:
        p = get_fiscal_period(s, 2021)
        acciones = [
            lambda: upsert_entry(s, fiscal_period_id=p.id, account_id=_id(s, "1002"), valor="1", tipo=Tipo.BALANCE),
            lambda: upsert_entry(s, fiscal_period_id=p.id, account_id=_id(s, "1001"), valor="2", tipo=Tipo.BALANCE),
            lambda: delete_entry(s, fiscal_period_id=p.id, account_id=_id(s, "1001"), tipo=Tipo.BALANCE),
            lambda: upsert_initial_balance(s, fiscal_period_id=p.id, account_id=_id(s, "1001"), valor="1"),
            lambda: delete_initial_balance(s, fiscal_period_id=p.id, account_id=_id(s, "1001")),
            lambda: set_statement_status(s, p.id, Tipo.BALANCE, EstadoRegistro.REVISADO),
            lambda: delete_fiscal_period(s, p.id),
            lambda: close_fiscal_period(s, p.id),
        ]
        for accion in acciones:
            with pytest.raises(EjercicioCerradoError):
                accion()
        assert get_entries_map(s, p.id, Tipo.BALANCE) == {_id(s, "1001"): Decimal("100.00")}


def test_disparadores_protegen_ejercicio_cerrado_aunque_se_salte_el_repositorio(bd):
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        upsert_entry(s, fiscal_period_id=p.id, account_id=_id(s, "1001"), valor="100", tipo=Tipo.BALANCE)
        close_fiscal_period(s, p.id)
    for sql in (
        "INSERT INTO balance_entry (fiscal_period_id, account_id, valor, created_at, updated_at) VALUES (1, 2, 5, '', '')",
        "UPDATE balance_entry SET valor = 1",
        "DELETE FROM balance_entry",
        "DELETE FROM fiscal_period",
    ):
        with pytest.raises(IntegrityError, match="EJERCICIO_CERRADO"):
            with session_scope() as s:
                s.connection().exec_driver_sql(sql)


def test_reabrir_permite_editar_y_queda_en_historial(bd):
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        close_fiscal_period(s, p.id)
        reopen_fiscal_period(s, p.id)
        assert p.fecha_cierre is None
        upsert_entry(s, fiscal_period_id=p.id, account_id=_id(s, "1001"), valor="1", tipo=Tipo.BALANCE)
        ops = [h.operacion for h in list_history(s, tabla_afectada="fiscal_period", fiscal_period_id=p.id)]
        assert ops == ["REABRIR", "CERRAR", "CREAR"]
        with pytest.raises(ValueError, match="no está cerrado"):
            reopen_fiscal_period(s, p.id)


def test_solo_se_eliminan_ejercicios_vacios(bd):
    with session_scope() as s:
        vacio, _ = get_or_create_fiscal_period(s, 2024)
        set_statement_status(s, vacio.id, Tipo.BALANCE, EstadoRegistro.REVISADO)
        con_datos, _ = get_or_create_fiscal_period(s, 2021)
        upsert_initial_balance(s, fiscal_period_id=con_datos.id, account_id=_id(s, "1001"), valor="0")
        with pytest.raises(ValueError, match="no se puede eliminar"):
            delete_fiscal_period(s, con_datos.id)
        vacio_id = vacio.id
        assert delete_fiscal_period(s, vacio_id) == 2024
    with session_scope() as s:
        assert [p.anio for p in list_fiscal_periods(s)] == [2021]
        ops = {(h.tabla_afectada, h.operacion) for h in list_history(s, fiscal_period_id=vacio_id)}
        assert ("fiscal_period", "ELIMINAR") in ops and ("statement_status", "ELIMINAR") in ops


def test_borrar_importe_queda_sin_dato_con_historial(bd):
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        upsert_entry(s, fiscal_period_id=p.id, account_id=_id(s, "1001"), valor="0", tipo=Tipo.BALANCE)
        entry_id = s.query(BalanceEntry).one().id
        assert delete_entry(s, fiscal_period_id=p.id, account_id=_id(s, "1001"), tipo=Tipo.BALANCE) is True
        assert get_entries_map(s, p.id, Tipo.BALANCE) == {}
        h = list_history(s, tabla_afectada="balance_entry")[0]
        assert (h.operacion, h.registro_id, h.valor_anterior, h.valor_nuevo) == ("ELIMINAR", entry_id, "0.00", None)
        assert delete_entry(s, fiscal_period_id=p.id, account_id=_id(s, "1001"), tipo=Tipo.BALANCE) is False


# --------------------------------------------------------------- 1.6 historial

def test_historial_identifica_registro_ejercicio_cuenta_y_lote(bd):
    with session_scope() as s:
        p21, _ = get_or_create_fiscal_period(s, 2021)
        p22, _ = get_or_create_fiscal_period(s, 2022)
        with lote(s) as lote_id:
            upsert_entry(s, fiscal_period_id=p21.id, account_id=_id(s, "1002"), valor="10", tipo=Tipo.BALANCE)
            upsert_entry(s, fiscal_period_id=p21.id, account_id=_id(s, "4001"), valor="50", tipo=Tipo.RESULTADOS)
        upsert_entry(s, fiscal_period_id=p21.id, account_id=_id(s, "1002"), valor="12.5", tipo=Tipo.BALANCE)
        upsert_entry(s, fiscal_period_id=p22.id, account_id=_id(s, "1002"), valor="7", tipo=Tipo.BALANCE)
        upsert_initial_balance(s, fiscal_period_id=p22.id, account_id=_id(s, "3001"), valor="3")
        set_statement_status(s, p22.id, Tipo.BALANCE, EstadoRegistro.REVISADO)
        s.flush()

        entry = s.query(BalanceEntry).filter_by(fiscal_period_id=p21.id, account_id=_id(s, "1002")).one()
        crear, editar = reversed(list_history(s, tabla_afectada="balance_entry", fiscal_period_id=p21.id))
        assert (crear.operacion, crear.registro_id, crear.account_id, crear.valor_nuevo) == ("CREAR", entry.id, _id(s, "1002"), "10.00")
        assert (editar.operacion, editar.registro_id, editar.valor_anterior, editar.valor_nuevo) == ("EDITAR", entry.id, "10.00", "12.50")
        assert crear.lote_id == lote_id and editar.lote_id is None
        assert {h.lote_id for h in list_history(s, fiscal_period_id=p21.id) if h.lote_id} == {lote_id}

        de_2022 = list_history(s, fiscal_period_id=p22.id)
        assert de_2022 and all(h.fiscal_period_id == p22.id for h in de_2022)
        assert {h.tabla_afectada for h in de_2022} == {"fiscal_period", "balance_entry", "initial_balance", "statement_status"}
        por_cuenta = list_history(s, account_id=_id(s, "1002"), tabla_afectada="balance_entry")
        assert len(por_cuenta) == 3


def test_historial_dataframe_muestra_anio_y_cuenta(bd):
    from modules.history import SIN_REGISTRAR, historial_dataframe

    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        upsert_entry(s, fiscal_period_id=p.id, account_id=_id(s, "1001"), valor="10", tipo=Tipo.BALANCE)
        s.add(ChangeHistory(tabla_afectada="balance_entry", registro_id=1, campo="valor", operacion="CREAR"))  # fila heredada
        s.flush()
        df = historial_dataframe(s, list_history(s, tabla_afectada="balance_entry"))
    filas = df.to_dict("records")
    nueva = next(f for f in filas if f["Cuenta"] != SIN_REGISTRAR)
    assert nueva["Ejercicio"] == "2021" and nueva["Cuenta"] == "1001 — Efectivo y equivalentes"
    heredada = next(f for f in filas if f["Cuenta"] == SIN_REGISTRAR)
    assert heredada["Ejercicio"] == SIN_REGISTRAR


# --------------------------------------------------------------- captura (widgets simulados)

def _capturar(monkeypatch, valores_por_codigo, tipo=Tipo.BALANCE):
    """Ejecuta data_entry._render_grupos con st.number_input simulado: devuelve
    el valor indicado para cada codigo de cuenta o el valor por defecto del
    campo (None si la cuenta no tiene importe guardado)."""
    from modules import data_entry

    def number_input(label, *a, value=None, **k):
        codigo = label.split(" — ")[0]
        return valores_por_codigo.get(codigo, value)

    monkeypatch.setattr(streamlit, "number_input", number_input)
    monkeypatch.setattr(streamlit, "form_submit_button", lambda *a, **k: True)
    monkeypatch.setattr(streamlit, "rerun", lambda *a, **k: None)
    grupos = data_entry.GRUPOS_BALANCE if tipo == Tipo.BALANCE else data_entry.GRUPOS_RESULTADOS
    with render_scope() as s:
        p = get_fiscal_period(s, 2021)
        data_entry._render_grupos(s, p, tipo, grupos, "USD", "form")


def test_captura_guarda_solo_lo_informado_y_cero_explicito(bd, monkeypatch):
    with session_scope() as s:
        get_or_create_fiscal_period(s, 2021)
    _capturar(monkeypatch, {"1001": 1500.0, "1102": 0.0, "2001": 2.675})
    with session_scope() as s:
        p = get_fiscal_period(s, 2021)
        valores = get_entries_map(s, p.id, Tipo.BALANCE)
        assert valores == {_id(s, "1001"): Decimal("1500.00"), _id(s, "1102"): Decimal("0.00"), _id(s, "2001"): Decimal("2.68")}
        assert len({h.lote_id for h in list_history(s, tabla_afectada="balance_entry")}) == 1


def test_captura_solo_guarda_cambios_y_vaciar_no_borra(bd, monkeypatch):
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        for codigo, valor in (("1001", "100"), ("1002", "200")):
            upsert_entry(s, fiscal_period_id=p.id, account_id=_id(s, codigo), valor=valor, tipo=Tipo.BALANCE)
    with session_scope() as s:
        n = _historial(s)
    # 1001 sin tocar, 1002 vaciado, 1003 nuevo
    _capturar(monkeypatch, {"1002": None, "1003": 5.0})
    with session_scope() as s:
        p = get_fiscal_period(s, 2021)
        assert get_entries_map(s, p.id, Tipo.BALANCE) == {
            _id(s, "1001"): Decimal("100.00"), _id(s, "1002"): Decimal("200.00"), _id(s, "1003"): Decimal("5.00")}
        assert _historial(s) == n + 1


def test_captura_con_un_error_no_guarda_nada(bd, monkeypatch):
    errores = []
    monkeypatch.setattr(streamlit, "error", lambda msg, *a, **k: errores.append(msg))
    with session_scope() as s:
        get_or_create_fiscal_period(s, 2021)
    _capturar(monkeypatch, {"1001": 100.0, "1002": 12345678901234.56})
    with session_scope() as s:
        assert get_entries_map(s, get_fiscal_period(s, 2021).id, Tipo.BALANCE) == {}
    assert errores and "1002" in errores[0]


def test_captura_en_ejercicio_cerrado_no_escribe(bd, monkeypatch):
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        close_fiscal_period(s, p.id)
    _capturar(monkeypatch, {"1001": 100.0})
    with session_scope() as s:
        assert get_entries_map(s, get_fiscal_period(s, 2021).id, Tipo.BALANCE) == {}


def test_edicion_en_ejercicio_cerrado_no_escribe(bd, monkeypatch):
    from modules import data_edit

    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        upsert_entry(s, fiscal_period_id=p.id, account_id=_id(s, "1001"), valor="100", tipo=Tipo.BALANCE)
        close_fiscal_period(s, p.id)

    def editor(df, **k):
        df = df.copy()
        df.loc[0, "Valor"] = 999.0
        return df

    monkeypatch.setattr(streamlit, "data_editor", editor)
    monkeypatch.setattr(streamlit, "button", lambda *a, **k: True)
    monkeypatch.setattr(streamlit, "rerun", lambda *a, **k: None)
    with render_scope() as s:
        data_edit._tabla_editable(s, get_fiscal_period(s, 2021).id, Tipo.BALANCE, "USD", key="k")
    with session_scope() as s:
        assert list(get_entries_map(s, get_fiscal_period(s, 2021).id, Tipo.BALANCE).values()) == [Decimal("100.00")]


# --------------------------------------------------------------- importacion

def _xlsx(filas):
    from modules.excel_import import COLUMNAS

    wb = Workbook()
    ws = wb.active
    ws.append(COLUMNAS)
    for f in filas:
        ws.append(f)
    b = io.BytesIO()
    wb.save(b)
    b.seek(0)
    return b


def _render_import(monkeypatch, archivo, boton=None):
    from modules import excel_import

    monkeypatch.setattr(streamlit, "file_uploader", lambda *a, **k: archivo)
    monkeypatch.setattr(streamlit, "button", lambda label, *a, **k: label == boton)
    monkeypatch.setattr(streamlit, "checkbox", lambda *a, **k: False)
    with render_scope() as s:
        excel_import.render(s, get_company(s))


def test_vista_previa_no_escribe_nada_y_marca_ejercicios_a_crear(bd, monkeypatch):
    from modules.excel_import import _validar_dataframe

    archivo = _xlsx([["1001", "Efectivo", "", "", 2024, 100], ["1002", "CxC", "", "", 2025, 50]])
    with session_scope() as s:
        n = _historial(s)
    _render_import(monkeypatch, archivo)
    with session_scope() as s:
        assert list_fiscal_periods(s) == [] and _historial(s) == n
        archivo.seek(0)
        filas = _validar_dataframe(s, pd.read_excel(archivo))
    assert [f.crea_ejercicio for f in filas] == [True, True]


def test_importacion_falla_a_mitad_y_no_deja_nada(bd, monkeypatch):
    from modules import excel_import

    llamadas = []
    original = excel_import.upsert_entry

    def upsert_que_falla(session, **kw):
        llamadas.append(kw)
        if len(llamadas) == 2:
            raise ValueError("fallo simulado")
        return original(session, **kw)

    monkeypatch.setattr(excel_import, "upsert_entry", upsert_que_falla)
    errores = []
    monkeypatch.setattr(streamlit, "error", lambda msg, *a, **k: errores.append(msg))
    with session_scope() as s:
        n = _historial(s)
    _render_import(monkeypatch, _xlsx([["1001", "x", "", "", 2023, 100], ["1002", "x", "", "", 2023, 50]]),
                   boton="Confirmar importación")
    with session_scope() as s:
        assert list_fiscal_periods(s) == [] and _historial(s) == n
    assert errores and "fila 3" in errores[0] and "No se guardó ningún cambio" in errores[0]


def test_importacion_en_ejercicio_cerrado_rechazada(bd, monkeypatch):
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        close_fiscal_period(s, p.id)
    _render_import(monkeypatch, _xlsx([["1001", "x", "", "", 2021, 100]]), boton="Confirmar importación")
    with session_scope() as s:
        assert get_entries_map(s, get_fiscal_period(s, 2021).id, Tipo.BALANCE) == {}


@pytest.mark.parametrize("valor, estado", [
    (2.675, "VALOR_INVALIDO"),           # tercer decimal real: no se redondea en silencio
    ("1,234.56", "VALOR_NO_NUMERICO"),
    (float("inf"), "VALOR_INVALIDO"),
    (None, "VALOR_VACIO"),
])
def test_validacion_de_valores_en_importacion(bd, valor, estado):
    from modules.excel_import import _validar_dataframe

    df = pd.DataFrame([{"Código de cuenta": "1001", "Nombre de cuenta": "x", "Categoría": "", "Subcategoría": "",
                        "Período": 2021, "Valor monetario": valor}])
    with session_scope() as s:
        assert _validar_dataframe(s, df)[0].estado == estado


def test_ruido_binario_de_excel_se_redondea_con_aviso_visible(bd):
    from modules.excel_import import _validar_dataframe

    df = pd.DataFrame([{"Código de cuenta": "1001", "Nombre de cuenta": "x", "Categoría": "", "Subcategoría": "",
                        "Período": 2021.0, "Valor monetario": 1234.5600000000002}])
    with session_scope() as s:
        fila = _validar_dataframe(s, df)[0]
    assert fila.estado == "OK" and fila.valor == Decimal("1234.56") and "redondeó" in fila.mensaje
