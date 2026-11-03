"""Pruebas de verificacion de la auditoria (A01-I03, ver MATRIZ_DE_PRUEBAS.md).

Cada prueba afirma el comportamiento CORRECTO esperado. Si una prueba
FALLA, el defecto descrito en su docstring queda comprobado.
Todas usan bases SQLite temporales; nunca tocan data/financiera.db
(conftest.py ademas redirige DB_PATH y verifica el hash de la BD real).

Origen: copia del test_auditoria.py de la auditoria (SHA-256
d9cb83a8a45b31e30cda45783a760e318218e7e0272e72205a11edadc018266c),
incorporada en la fase 0. Unico cambio: PROJECT se calcula relativo a
este archivo en lugar de una ruta fija. Los cuerpos de las pruebas no
se modificaron.
"""
import io
import sys
import warnings
from decimal import Decimal
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

import pandas as pd
import pytest
import streamlit
from openpyxl import Workbook, load_workbook

from database import connection
from database.connection import init_db, session_scope
from database.enums import CategoriaPrincipal as Cat
from database.enums import EfectoCuenta as Efecto
from database.enums import Subcategoria as Sub
from database.enums import TipoEstadoFinanciero as Tipo
from database.models import BalanceEntry, ChangeHistory, FiscalPeriod
from database.repositories import (
    get_account_by_codigo,
    get_company,
    get_entries_map,
    get_or_create_fiscal_period,
    list_fiscal_periods,
    save_company,
    update_account,
    upsert_entry,
    upsert_initial_balance,
)
from database.seed import seed_default_accounts
from calculations.balance_sheet import compute_balance_sheet
from calculations.income_statement import compute_income_statement
from calculations.vertical_analysis import compute_vertical_income, compute_vertical_balance
from calculations.dupont import compute_dupont


@pytest.fixture()
def db(tmp_path):
    path = tmp_path / "audit.db"
    init_db(db_path=path)
    with session_scope() as s:
        seed_default_accounts(s)
        save_company(s, nombre_legal="Empresa Prueba", nombre_comercial="EP", actividad_economica="x",
                     pais="SV", moneda="USD", anio_inicial_analisis=2021)
    yield path
    connection.dispose_engine()


def _be(s, periodo_id, codigo, valor):
    upsert_entry(s, fiscal_period_id=periodo_id, account_id=get_account_by_codigo(s, codigo).id,
                 valor=Decimal(valor), tipo=Tipo.BALANCE)


def _ie(s, periodo_id, codigo, valor):
    upsert_entry(s, fiscal_period_id=periodo_id, account_id=get_account_by_codigo(s, codigo).id,
                 valor=Decimal(valor), tipo=Tipo.RESULTADOS)


def _ejercicio(s, anio, activo, patrimonio, ingresos, utilidad):
    p, _ = get_or_create_fiscal_period(s, anio)
    s.flush()
    _be(s, p.id, "1001", str(activo))
    _be(s, p.id, "2001", str(activo - patrimonio))
    _be(s, p.id, "3001", str(patrimonio))
    _ie(s, p.id, "4001", str(ingresos))
    _ie(s, p.id, "8001", str(ingresos - utilidad))
    return p


# ---------------------------------------------------------------- DuPont

def test_A01_dupont_no_encadena_ejercicio_no_consecutivo(db):
    """2021 y 2023 registrados (sin 2022). El saldo inicial de 2023 NO debe
    tomarse silenciosamente del balance final de 2021."""
    with session_scope() as s:
        _ejercicio(s, 2021, 1000, 600, 1000, 100)
        p23 = _ejercicio(s, 2023, 2000, 1000, 2000, 200)
        s.flush()
        r = compute_dupont(s, p23)
        print("fuente:", r.fuente_saldos_iniciales, "aprox:", r.saldos_aproximados, "activo_ini:", r.activo_inicial)
        assert not (r.activo_inicial == Decimal("1000.00") and r.saldos_aproximados is False), \
            "Usa el balance de 2021 como saldo inicial de 2023 sin marcarlo como aproximacion"


def test_A02_dupont_patrimonio_promedio_negativo_advierte(db):
    """Patrimonio promedio negativo: el ROE no debe presentarse como valido."""
    with session_scope() as s:
        p = _ejercicio(s, 2021, 1000, -200, 1000, -100)
        s.flush()
        r = compute_dupont(s, p)
        print("disponible:", r.disponible, "ROE:", r.roe_directo_pct, "motivo:", r.motivo_no_disponible)
        assert r.disponible is False or r.motivo_no_disponible, \
            f"Perdida con patrimonio negativo produce ROE {r.roe_directo_pct}% sin advertencia"


def test_A03_dupont_saldo_inicial_cero_por_ejercicio_guardado_en_ceros(db):
    """Si el ejercicio anterior solo tiene ceros (el formulario guarda 0.00 en
    todas las cuentas), no debe usarse 0 como saldo inicial real."""
    with session_scope() as s:
        p22, _ = get_or_create_fiscal_period(s, 2022)
        s.flush()
        for cod in ("1001", "2001", "3001"):
            _be(s, p22.id, cod, "0")
        p23 = _ejercicio(s, 2023, 2000, 1000, 2000, 200)
        s.flush()
        r = compute_dupont(s, p23)
        print("activo_ini:", r.activo_inicial, "prom:", r.activo_promedio, "aprox:", r.saldos_aproximados, r.fuente_saldos_iniciales)
        assert r.activo_inicial != Decimal("0.00"), "Activo inicial 0 tomado como dato real"


def test_A04_dupont_saldos_iniciales_manuales_parciales(db):
    """Saldos iniciales manuales solo de patrimonio: el activo inicial no debe
    asumirse 0 sin advertencia."""
    with session_scope() as s:
        p = _ejercicio(s, 2021, 1000, 600, 1000, 100)
        s.flush()
        upsert_initial_balance(s, fiscal_period_id=p.id, account_id=get_account_by_codigo(s, "3001").id, valor=Decimal("500"))
        s.flush()
        r = compute_dupont(s, p)
        print("activo_ini:", r.activo_inicial, "aprox:", r.saldos_aproximados, "rot:", r.rotacion_activos)
        assert r.activo_inicial != Decimal("0.00") or r.saldos_aproximados


def test_A05_dupont_roe_coincide_con_roe_directo(db):
    """Control: identidad DuPont = ROE directo con datos validos."""
    with session_scope() as s:
        _ejercicio(s, 2021, 1000, 600, 1000, 100)
        p = _ejercicio(s, 2022, 1300, 700, 1234.56, 98.76)
        s.flush()
        r = compute_dupont(s, p)
        esperado = (Decimal("98.76") / ((Decimal("600") + Decimal("700")) / 2) * 100).quantize(Decimal("0.01"))
        print("dupont", r.roe_dupont_pct, "directo", r.roe_directo_pct, "esperado", esperado)
        assert r.roe_directo_pct == esperado and r.coincide_redondeo


def test_A06_dupont_factores_mostrados_reproducen_roe(db):
    """Los factores redondeados que se muestran deben reproducir el ROE
    mostrado (verificabilidad academica)."""
    with session_scope() as s:
        p = _ejercicio(s, 2021, 3333, 1111, 7777, 123)
        s.flush()
        r = compute_dupont(s, p)
        producto = (r.margen_neto * 100 * r.rotacion_activos * r.multiplicador_capital).quantize(Decimal("0.01"))
        print("margen%", r.margen_neto * 100, "rot", r.rotacion_activos, "mult", r.multiplicador_capital,
              "producto", producto, "ROE", r.roe_dupont_pct)
        assert abs(producto - r.roe_dupont_pct) <= Decimal("0.01")


def test_A07_dupont_ingresos_cero(db):
    with session_scope() as s:
        p = _ejercicio(s, 2021, 1000, 600, 0, -50)
        s.flush()
        r = compute_dupont(s, p)
        assert r.disponible is False


def test_A08_dupont_activo_promedio_cero(db):
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        _be(s, p.id, "1001", "0")
        _ie(s, p.id, "4001", "100")
        s.flush()
        r = compute_dupont(s, p)
        assert r.disponible is False


def test_A09_dupont_utilidad_negativa(db):
    with session_scope() as s:
        p = _ejercicio(s, 2021, 1000, 500, 1000, -100)
        s.flush()
        r = compute_dupont(s, p)
        assert r.roe_directo_pct == Decimal("-20.00") and r.margen_neto == Decimal("-0.1")


# ---------------------------------------------------------------- Catalogo / integridad historica

def test_B01_reclasificar_cuenta_con_movimientos_bloqueado(db):
    """Cambiar ACTIVO->INGRESOS de una cuenta con saldos historicos no debe
    hacer desaparecer el importe de ambos estados."""
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        _be(s, p.id, "1001", "500")
        s.flush()
        antes = compute_balance_sheet(s, p.id).total_activo
        try:
            update_account(s, get_account_by_codigo(s, "1001").id, categoria_principal=Cat.INGRESOS, subcategoria=None)
            s.flush()
        except ValueError as e:
            print("bloqueado:", e)
            return
        despues = compute_balance_sheet(s, p.id).total_activo
        ingresos = compute_income_statement(s, p.id).ingresos_netos.subtotal
        print("activo antes", antes, "despues", despues, "ingresos", ingresos)
        assert despues == antes, "El importe historico desaparecio del Balance (y no aparece en Resultados)"


def test_B02_cambio_efecto_altera_resultados_historicos(db):
    """Cambiar 'efecto' INGRESO->GASTO de una cuenta usada en 2021 no debe
    alterar retroactivamente la utilidad de 2021."""
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        _ie(s, p.id, "4001", "1000")
        _ie(s, p.id, "6003", "100")
        s.flush()
        antes = compute_income_statement(s, p.id).utilidad_neta
        try:
            update_account(s, get_account_by_codigo(s, "6003").id, efecto=Efecto.GASTO)
            s.flush()
        except ValueError as e:
            print("bloqueado:", e)
            return
        despues = compute_income_statement(s, p.id).utilidad_neta
        print("utilidad 2021 antes", antes, "despues", despues)
        assert antes == despues


def test_B03_cambio_corriente_a_no_corriente_retroactivo(db):
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        _be(s, p.id, "1003", "400")
        s.flush()
        antes = compute_balance_sheet(s, p.id).activo_corriente.subtotal
        try:
            update_account(s, get_account_by_codigo(s, "1003").id, subcategoria=Sub.NO_CORRIENTE)
            s.flush()
        except ValueError:
            return
        despues = compute_balance_sheet(s, p.id).activo_corriente.subtotal
        print("AC 2021 antes", antes, "despues", despues)
        assert antes == despues


def test_B04_movimiento_con_ejercicio_inexistente_rechazado(db):
    """FK: no se puede asociar un movimiento a un ejercicio inexistente."""
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError):
        with session_scope() as s:
            s.add(BalanceEntry(fiscal_period_id=999, account_id=get_account_by_codigo(s, "1001").id, valor=Decimal("1")))
            s.flush()


def test_B05_balance_entry_duplicado_rechazado(db):
    from sqlalchemy.exc import IntegrityError
    with pytest.raises(IntegrityError):
        with session_scope() as s:
            p, _ = get_or_create_fiscal_period(s, 2021)
            s.flush()
            a = get_account_by_codigo(s, "1001").id
            s.add(BalanceEntry(fiscal_period_id=p.id, account_id=a, valor=Decimal("1")))
            s.add(BalanceEntry(fiscal_period_id=p.id, account_id=a, valor=Decimal("2")))
            s.flush()


def test_B06_modificar_un_ejercicio_no_altera_otro(db):
    with session_scope() as s:
        p1 = _ejercicio(s, 2021, 1000, 600, 1000, 100)
        p2 = _ejercicio(s, 2022, 1200, 700, 1200, 150)
        s.flush()
        _be(s, p2.id, "1001", "1500")
        s.flush()
        assert compute_balance_sheet(s, p1.id).total_activo == Decimal("1000.00")


# ---------------------------------------------------------------- Historial

def test_C01_historial_identifica_ejercicio_y_registro(db):
    """El historial de un CREAR en balance_entry debe identificar el registro
    (id de balance_entry) y el ejercicio."""
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        cuenta = get_account_by_codigo(s, "1002")
        _be(s, p.id, "1002", "10")
        s.flush()
        entry = s.query(BalanceEntry).filter_by(account_id=cuenta.id).one()
        h = s.query(ChangeHistory).filter_by(tabla_afectada="balance_entry").order_by(ChangeHistory.id.desc()).first()
        print("entry.id", entry.id, "account.id", cuenta.id, "registro_id historial", h.registro_id,
              "columnas:", [c.name for c in ChangeHistory.__table__.columns])
        assert h.registro_id == entry.id and hasattr(ChangeHistory, "fiscal_period_id")


# ---------------------------------------------------------------- Importacion Excel (codigo real de render)

def _xlsx(filas):
    wb = Workbook()
    ws = wb.active
    from modules.excel_import import COLUMNAS
    ws.append(COLUMNAS)
    for f in filas:
        ws.append(f)
    b = io.BytesIO()
    wb.save(b)
    b.seek(0)
    return b


def _render_import(monkeypatch, archivo, boton=None, checkbox=False):
    """Ejecuta modules.excel_import.render dentro de session_scope, igual que
    app.py. Simulado: st.file_uploader (devuelve el archivo), st.button
    (True solo para la etiqueta `boton`) y st.checkbox."""
    from modules import excel_import
    monkeypatch.setattr(streamlit, "file_uploader", lambda *a, **k: archivo)
    monkeypatch.setattr(streamlit, "button", lambda label, *a, **k: label == boton)
    monkeypatch.setattr(streamlit, "checkbox", lambda *a, **k: checkbox)
    with session_scope() as s:
        excel_import.render(s, get_company(s))


def test_D01_vista_previa_no_crea_ejercicios(db, monkeypatch):
    archivo = _xlsx([["1001", "Efectivo", "ACTIVO", "CORRIENTE", 2024, 100]])
    _render_import(monkeypatch, archivo, boton=None)
    with session_scope() as s:
        anios = [p.anio for p in list_fiscal_periods(s)]
        hist = s.query(ChangeHistory).filter_by(tabla_afectada="fiscal_period").count()
    print("ejercicios tras solo ver la vista previa:", anios, "registros historial fiscal_period:", hist)
    assert 2024 not in anios


def test_D02_cancelar_importacion_no_deja_rastro(db, monkeypatch):
    archivo = _xlsx([["1001", "Efectivo", "ACTIVO", "CORRIENTE", 2025, 100]])
    _render_import(monkeypatch, archivo, boton="Cancelar")
    with session_scope() as s:
        anios = [p.anio for p in list_fiscal_periods(s)]
    print("ejercicios tras CANCELAR:", anios)
    assert 2025 not in anios


def test_D03_valor_vacio_no_se_acepta(db, monkeypatch):
    """Celda 'Valor monetario' vacia -> debe rechazarse, no importarse."""
    from modules.excel_import import _validar_dataframe
    archivo = _xlsx([["1001", "Efectivo", "ACTIVO", "CORRIENTE", 2021, None]])
    df = pd.read_excel(archivo)
    with session_scope() as s:
        filas = _validar_dataframe(s, df)
    print("estado fila con valor vacio:", filas[0].estado, filas[0].valor)
    assert filas[0].estado != "OK"


def test_D04_valor_vacio_confirmado_persistencia(db, monkeypatch):
    """Que ocurre si se confirma una importacion con valor vacio."""
    archivo = _xlsx([["1001", "Efectivo", "ACTIVO", "CORRIENTE", 2021, None]])
    err = None
    try:
        _render_import(monkeypatch, archivo, boton="Confirmar importación")
    except Exception as e:  # noqa
        err = e
    with session_scope() as s:
        p = s.query(FiscalPeriod).filter_by(anio=2021).first()
        vals = get_entries_map(s, p.id, Tipo.BALANCE) if p else {}
    print("excepcion:", repr(err), "valores guardados:", vals)
    assert err is None and not vals


def test_D05_periodo_decimal_rechazado(db):
    from modules.excel_import import _validar_dataframe
    df = pd.DataFrame([{"Código de cuenta": "1001", "Nombre de cuenta": "x", "Categoría": "", "Subcategoría": "",
                        "Período": 2021.9, "Valor monetario": 5}])
    with session_scope() as s:
        f = _validar_dataframe(s, df)[0]
    print("periodo 2021.9 ->", f.estado, f.periodo)
    assert f.estado != "OK"


def test_D06_periodo_fuera_de_rango_rechazado(db):
    from modules.excel_import import _validar_dataframe
    df = pd.DataFrame([{"Código de cuenta": "1001", "Nombre de cuenta": "x", "Categoría": "", "Subcategoría": "",
                        "Período": 21, "Valor monetario": 5}])
    with session_scope() as s:
        f = _validar_dataframe(s, df)[0]
    print("periodo 21 ->", f.estado)
    assert f.estado != "OK"


def test_D07_valor_mas_de_dos_decimales(db):
    """Valor con 3 decimales debe rechazarse o redondearse de forma explicita."""
    from modules.excel_import import _validar_dataframe
    df = pd.DataFrame([{"Código de cuenta": "1001", "Nombre de cuenta": "x", "Categoría": "", "Subcategoría": "",
                        "Período": 2021, "Valor monetario": 0.1 + 0.2}])
    with session_scope() as s:
        f = _validar_dataframe(s, df)[0]
    print("valor leido:", f.valor, f.estado)
    assert f.estado != "OK" or f.valor == f.valor.quantize(Decimal("0.01"))


def test_D08_codigo_numerico_leido_como_float(db):
    """Codigo '1001' guardado como numero en Excel; si la celda es 1001.0 no
    debe reportarse como cuenta desconocida."""
    from modules.excel_import import _validar_dataframe
    df = pd.DataFrame([{"Código de cuenta": 1001.0, "Nombre de cuenta": "x", "Categoría": "", "Subcategoría": "",
                        "Período": 2021, "Valor monetario": 5}])
    with session_scope() as s:
        f = _validar_dataframe(s, df)[0]
    print("codigo 1001.0 ->", f.estado)
    assert f.estado == "OK"


def test_D09_duplicado_en_archivo_detectado(db):
    from modules.excel_import import _validar_dataframe
    df = pd.DataFrame([
        {"Código de cuenta": "1001", "Nombre de cuenta": "x", "Categoría": "", "Subcategoría": "", "Período": 2021, "Valor monetario": 5},
        {"Código de cuenta": "1001", "Nombre de cuenta": "x", "Categoría": "", "Subcategoría": "", "Período": 2021, "Valor monetario": 6},
    ])
    with session_scope() as s:
        filas = _validar_dataframe(s, df)
    assert [f.estado for f in filas] == ["OK", "DUPLICADA"]


def test_D10_importacion_errores_parciales_importa_solo_validas(db, monkeypatch):
    archivo = _xlsx([["1001", "Efectivo", "ACTIVO", "CORRIENTE", 2021, 100],
                     ["XXXX", "No existe", "ACTIVO", "CORRIENTE", 2021, 50]])
    _render_import(monkeypatch, archivo, boton="Confirmar importación")
    with session_scope() as s:
        p = s.query(FiscalPeriod).filter_by(anio=2021).first()
        vals = get_entries_map(s, p.id, Tipo.BALANCE)
    print("importado:", vals)
    assert list(vals.values()) == [Decimal("100.00")]


def test_D11_reimportar_mismo_archivo_no_duplica(db, monkeypatch):
    archivo = lambda: _xlsx([["1001", "Efectivo", "ACTIVO", "CORRIENTE", 2021, 100]])
    _render_import(monkeypatch, archivo(), boton="Confirmar importación")
    _render_import(monkeypatch, archivo(), boton="Confirmar importación")
    with session_scope() as s:
        n = s.query(BalanceEntry).count()
    assert n == 1


# ---------------------------------------------------------------- Precision

def test_E01_persistencia_decimal_exacta(db):
    """Importe grande con centavos debe leerse exactamente igual."""
    valor = Decimal("123456789012345.67")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        with session_scope() as s:
            p, _ = get_or_create_fiscal_period(s, 2021)
            s.flush()
            _be(s, p.id, "1001", str(valor))
        connection.dispose_engine()
        init_db(db_path=db)
        with session_scope() as s:
            p = s.query(FiscalPeriod).filter_by(anio=2021).one()
            leido = get_entries_map(s, p.id, Tipo.BALANCE)[get_account_by_codigo(s, "1001").id]
    print("escrito", valor, "leido", leido, "warnings:", [str(x.message)[:120] for x in w])
    assert leido == valor


def test_E02_importes_tipicos_exactos(db):
    valores = ["0.10", "0.20", "1234567.89", "-98765.43", "99999999.99"]
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        for cod, v in zip(["1001", "1002", "1003", "1004", "1101"], valores):
            _be(s, p.id, cod, v)
    with session_scope() as s:
        p = s.query(FiscalPeriod).filter_by(anio=2021).one()
        bs = compute_balance_sheet(s, p.id)
    esperado = sum(Decimal(v) for v in valores)
    print("total", bs.total_activo, "esperado", esperado)
    assert bs.total_activo == esperado


def test_E03_captura_formulario_float(db):
    """Conversion usada por data_entry._to_decimal sobre floats de st.number_input."""
    from modules.data_entry import _to_decimal
    casos = {1234567890123.45: Decimal("1234567890123.45"), 0.1 + 0.2: Decimal("0.30"), 2.675: Decimal("2.68")}
    res = {k: _to_decimal(k) for k in casos}
    print(res)
    assert all(res[k] == v for k, v in casos.items())


# ---------------------------------------------------------------- Calculos

def test_F01_depreciacion_positiva_no_resta(db):
    """La depreciacion acumulada (cuenta correctora) capturada en positivo
    debe restar del activo o ser rechazada/advertida.

    Revision final (2026-11-02): la convencion aprobada por el usuario prohibe
    invertir signos (README 4.2, calculations/validation.py). La version
    anterior de esta prueba exigia que el total cambiara a 700 invirtiendo el
    signo en silencio, lo que contradice esa convencion; se actualiza para
    exigir la alternativa que la propia prueba admite ("advertida"): el importe
    no se altera, se advierte y el reporte deja de ser DEFINITIVO. La captura
    con el signo correcto (-300) resta (ver F02 y la ultima asercion)."""
    from calculations.banderas import SIGNO_ATIPICO, banderas_balance, resumen

    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        _be(s, p.id, "1101", "1000")
        _be(s, p.id, "1102", "300")
        s.flush()
        bs = compute_balance_sheet(s, p.id)
        print("activo no corriente con depreciacion +300:", bs.activo_no_corriente.subtotal)
        # No se invierte en silencio: el total refleja lo capturado...
        assert bs.activo_no_corriente.subtotal == Decimal("1300.00")
        # ...pero se advierte y el reporte no es DEFINITIVO.
        assert any("1102" in a and "correctora" in a for a in bs.advertencias_signo)
        assert SIGNO_ATIPICO in resumen(banderas_balance(bs))
        # Con el signo de la convencion la depreciacion resta.
        _be(s, p.id, "1102", "-300")
        s.flush()
        bs = compute_balance_sheet(s, p.id)
        assert bs.activo_no_corriente.subtotal == Decimal("700.00") and not bs.advertencias_signo


def test_F02_depreciacion_negativa_resta(db):
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        _be(s, p.id, "1101", "1000")
        _be(s, p.id, "1102", "-300")
        s.flush()
        assert compute_balance_sheet(s, p.id).activo_no_corriente.subtotal == Decimal("700.00")


def test_F03_costo_negativo_no_infla_utilidad(db):
    """Costo de ventas capturado como (600) negativo no debe sumar a la utilidad.

    Revision final (2026-11-02): con la convencion aprobada (los signos nunca se
    invierten) un costo negativo no se corrige en silencio; se advierte, exige
    confirmacion al capturarlo y el Estado de Resultados queda marcado SIGNO
    ATIPICO, de modo que la utilidad inflada nunca se presenta como DEFINITIVA.
    La version anterior exigia invertir el signo; se actualiza para comprobar
    esa proteccion y que la captura correcta (+600) da la utilidad de 400."""
    from calculations.banderas import DEFINITIVO, SIGNO_ATIPICO, banderas_resultados, resumen

    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        _ie(s, p.id, "4001", "1000")
        _ie(s, p.id, "5001", "-600")
        s.flush()
        inc = compute_income_statement(s, p.id)
        ub = inc.utilidad_bruta
        print("utilidad bruta con costo -600:", ub)
        assert ub == Decimal("1600.00")  # lo capturado, sin inversion silenciosa
        assert any("5001" in a and "negativo" in a for a in inc.advertencias_signo)
        estado = resumen(banderas_resultados(inc))
        assert SIGNO_ATIPICO in estado and estado != DEFINITIVO
        _ie(s, p.id, "5001", "600")
        s.flush()
        inc = compute_income_statement(s, p.id)
        assert inc.utilidad_bruta == Decimal("400.00") and not inc.advertencias_signo


def test_F04_estado_resultados_completo(db):
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        for cod, v in [("4001", "10000"), ("5001", "6000"), ("6001", "1000"), ("6002", "800"), ("6003", "150"),
                       ("6004", "50"), ("7001", "120"), ("7002", "420"), ("7003", "30"), ("7004", "10"), ("8001", "605")]:
            _ie(s, p.id, cod, v)
        s.flush()
        r = compute_income_statement(s, p.id)
    # UB 4000; UO 4000-1000-800+150-50=2300; RF -300; OR 20; UAI 2020; UN 1415
    assert (r.utilidad_bruta, r.utilidad_operativa, r.resultado_financiero, r.otros_resultados,
            r.utilidad_antes_impuestos, r.utilidad_neta) == tuple(Decimal(x) for x in
            ("4000.00", "2300.00", "-300.00", "20.00", "2020.00", "1415.00"))


def test_F05_balance_con_pasivo_y_patrimonio_negativos(db):
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        _be(s, p.id, "1001", "100")
        _be(s, p.id, "2001", "300")
        _be(s, p.id, "3003", "-200")
        s.flush()
        bs = compute_balance_sheet(s, p.id)
    assert bs.total_patrimonio == Decimal("-200.00") and bs.cuadra


def test_F06_vertical_resultados_incluye_ingresos_y_subtotales(db):
    """El analisis vertical del ER debe mostrar ingresos (100%) y utilidades."""
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        _ie(s, p.id, "4001", "1000")
        _ie(s, p.id, "5001", "600")
        s.flush()
        r = compute_vertical_income(s, p.id)
    codigos = [f.cuenta.codigo for f in r.filas]
    print("filas vertical ER:", codigos, "atributos:", list(vars(r).keys()))
    assert "4001" in codigos


def test_F07_vertical_balance_incluye_subtotales(db):
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        _be(s, p.id, "1001", "300")
        _be(s, p.id, "1101", "700")
        s.flush()
        r = compute_vertical_balance(s, p.id)
    print("atributos:", list(vars(r).keys()))
    assert any(k for k in vars(r) if "subtotal" in k or "total" in k and k != "base_total_activo")


def test_F08_ausencia_vs_cero(db):
    """Un balance con solo activo capturado no debe confundirse con pasivo=0."""
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        _be(s, p.id, "1001", "100")
        s.flush()
        bs = compute_balance_sheet(s, p.id)
    print("tiene_datos", bs.tiene_datos, "total_pasivo", bs.total_pasivo, "atributos", [k for k in vars(bs)])
    assert any("complet" in k or "faltante" in k for k in vars(bs))


# ---------------------------------------------------------------- Exportaciones

def _formulas(ws):
    return {c.coordinate: c.value for row in ws.iter_rows() for c in row if isinstance(c.value, str) and c.value.startswith("=")}


def test_G01_excel_balance_sin_referencias_circulares(db):
    """Balance con grupo 'Activo no corriente' vacio -> el TOTAL ACTIVO no
    debe referenciarse a si mismo."""
    from reports.excel_export import export_balance_excel
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        _be(s, p.id, "1001", "100")
        _be(s, p.id, "2001", "40")
        _be(s, p.id, "3001", "60")
        s.flush()
        data = export_balance_excel(get_company(s), p, compute_balance_sheet(s, p.id))
    ws = load_workbook(io.BytesIO(data)).active
    import re
    circulares = [(k, v) for k, v in _formulas(ws).items() if k in re.findall(r"C\d+", v)]
    print("formulas:", _formulas(ws))
    print("circulares:", circulares)
    assert not circulares


def test_G02_excel_resultados_sin_referencias_circulares(db):
    from reports.excel_export import export_income_excel
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        _ie(s, p.id, "4001", "1000")
        _ie(s, p.id, "5001", "600")
        s.flush()
        data = export_income_excel(get_company(s), p, compute_income_statement(s, p.id))
    ws = load_workbook(io.BytesIO(data)).active
    f = _formulas(ws)
    import re
    circ = [(k, v) for k, v in f.items() if k in re.findall(r"C\d+", v)]
    print("formulas:", f)
    print("circulares:", circ)
    assert not circ


def test_G03_pdf_nombre_con_ampersand(db):
    from reports.pdf_export import export_balance_pdf
    with session_scope() as s:
        save_company(s, nombre_legal="Acero & Aluminio, S. A. de C. V.", nombre_comercial="x",
                     actividad_economica="x", pais="SV", moneda="USD", anio_inicial_analisis=2021)
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        _be(s, p.id, "1001", "100")
        s.flush()
        pdf = export_balance_pdf(get_company(s), p, compute_balance_sheet(s, p.id))
    assert pdf.startswith(b"%PDF")


def test_G04_exportacion_no_modifica_bd(db):
    import hashlib
    from reports.excel_export import export_balance_excel, export_income_excel
    from reports.pdf_export import export_balance_pdf, export_income_pdf
    with session_scope() as s:
        p = _ejercicio(s, 2021, 1000, 600, 1000, 100)
    connection.dispose_engine()
    h1 = hashlib.sha256(Path(db).read_bytes()).hexdigest()
    init_db(db_path=db)
    with session_scope() as s:
        p = s.query(FiscalPeriod).one()
        c = get_company(s)
        bs, inc = compute_balance_sheet(s, p.id), compute_income_statement(s, p.id)
        export_balance_excel(c, p, bs); export_income_excel(c, p, inc)
        export_balance_pdf(c, p, bs); export_income_pdf(c, p, inc)
    connection.dispose_engine()
    assert hashlib.sha256(Path(db).read_bytes()).hexdigest() == h1


# ---------------------------------------------------------------- Restauracion (app.py real via AppTest)

def _apptest_restore(db_path, origen):
    from streamlit.testing.v1 import AppTest
    connection.dispose_engine()
    connection.DB_PATH = Path(db_path)  # simulado: redirige la BD de la app a la BD temporal
    at = AppTest.from_file(str(PROJECT / "app.py"), default_timeout=60)
    at.session_state["pending_restore"] = str(origen)
    at.run()
    return at


def test_H01_restaurar_archivo_corrupto_no_destruye_bd(db, tmp_path):
    corrupto = tmp_path / "corrupto.db"
    corrupto.write_bytes(b"esto no es una base sqlite" * 100)
    original = Path(db).read_bytes()
    try:
        at = _apptest_restore(db, corrupto)
        excepciones = [e.value for e in at.exception]
    finally:
        connection.dispose_engine()
        connection.DB_PATH = connection.DATA_DIR / "financiera.db"
    print("excepciones app:", excepciones)
    print("BD temporal sobrescrita con el archivo corrupto:", Path(db).read_bytes() == corrupto.read_bytes())
    assert Path(db).read_bytes() == original


def test_H02_restaurar_sqlite_ajena_no_se_acepta(db, tmp_path):
    import sqlite3
    ajena = tmp_path / "ajena.db"
    con = sqlite3.connect(ajena); con.execute("create table x(a)"); con.commit(); con.close()
    try:
        at = _apptest_restore(db, ajena)
        excepciones = [e.value for e in at.exception]
        exitos = [m.value for m in at.success]
    finally:
        connection.dispose_engine()
        connection.DB_PATH = connection.DATA_DIR / "financiera.db"
    init_db(db_path=db)
    with session_scope() as s:
        empresa = get_company(s)
    print("excepciones:", excepciones, "mensajes exito:", exitos, "empresa tras restaurar:", empresa)
    assert empresa is not None


# ---------------------------------------------------------------- Captura / edicion (codigo real con widgets simulados)

def test_I01_formulario_guarda_ceros_en_cuentas_no_capturadas(db, monkeypatch):
    """Al guardar el formulario de Balance sin tocar nada, no deberian crearse
    registros 0.00 que luego se confundan con datos reales."""
    from modules import data_entry
    monkeypatch.setattr(streamlit, "form_submit_button", lambda *a, **k: True)
    monkeypatch.setattr(streamlit, "rerun", lambda *a, **k: None)
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
    with session_scope() as s:
        p = s.query(FiscalPeriod).one()
        data_entry._render_grupos(s, p, Tipo.BALANCE, data_entry.GRUPOS_BALANCE, "USD", "form_balance")
    with session_scope() as s:
        p = s.query(FiscalPeriod).one()
        vals = get_entries_map(s, p.id, Tipo.BALANCE)
        bs = compute_balance_sheet(s, p.id)
    print("registros creados:", len(vals), "todos cero:", all(v == 0 for v in vals.values()),
          "tiene_datos:", bs.tiene_datos, "cuadra:", bs.cuadra)
    assert not (bs.tiene_datos and all(v == 0 for v in vals.values()))


def test_I02_edicion_celda_vacia_manejada(db, monkeypatch):
    """Vaciar una celda en Modificacion de datos no debe provocar una
    excepcion no controlada."""
    from modules import data_edit
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        _be(s, p.id, "1001", "100")

    def editor(df, **k):
        df = df.copy()
        df.loc[0, "Valor"] = float("nan")
        return df
    monkeypatch.setattr(streamlit, "data_editor", editor)
    monkeypatch.setattr(streamlit, "button", lambda label, *a, **k: label == "Guardar cambios")
    monkeypatch.setattr(streamlit, "rerun", lambda *a, **k: None)
    err = None
    try:
        with session_scope() as s:
            p = s.query(FiscalPeriod).one()
            data_edit._tabla_editable(s, p.id, Tipo.BALANCE, "USD", key="k")
    except Exception as e:  # noqa
        err = e
    print("excepcion:", repr(err)[:200])
    assert err is None


def test_I03_tipo_de_almacenamiento_sqlite(db):
    import sqlite3
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        s.flush()
        _be(s, p.id, "1001", "1234.56")
    connection.dispose_engine()
    con = sqlite3.connect(db)
    r = con.execute("select valor, typeof(valor) from balance_entry").fetchall()
    con.close()
    print("almacenado:", r)
    assert r[0][1] in ("text", "integer")  # esperado: representacion decimal exacta
