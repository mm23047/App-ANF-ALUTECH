"""Fase 2: exactitud financiera (A-01, A-02, A-04, A-05, M-04, M-07, B-01, B-02)."""
import io
from decimal import Decimal

import pandas as pd
import pytest
import streamlit
from openpyxl import Workbook

from calculations.balance_sheet import compute_balance_sheet
from calculations.controls import CONCILIADO, DIFERENCIA, SIN_DATOS, conciliar_resultado
from calculations.banderas import banderas_dupont, resumen
from calculations.dupont import compute_dupont, generar_interpretacion
from calculations.income_statement import compute_income_statement
from calculations.validation import aviso_signo
from components.money import format_percent, format_ratio
from database import connection
from database.connection import init_db, render_scope, session_scope
from database.enums import TipoEstadoFinanciero as Tipo
from database.models import Account
from database.repositories import (
    get_account_by_codigo,
    get_company,
    get_entries_map,
    get_fiscal_period,
    get_initial_balances_map,
    get_or_create_fiscal_period,
    save_company,
    upsert_entry,
    upsert_initial_balance,
)
from database.seed import seed_default_accounts

CUATRO = Decimal("0.0001")


@pytest.fixture()
def bd(tmp_path):
    init_db(db_path=tmp_path / "fase2.db")
    with session_scope() as s:
        seed_default_accounts(s)
        save_company(s, nombre_legal="Empresa Prueba", nombre_comercial="EP", actividad_economica="x",
                     pais="SV", moneda="USD", anio_inicial_analisis=2021)
    yield
    connection.dispose_engine()


def _cuenta(s, codigo):
    return get_account_by_codigo(s, codigo)


def _capturar(s, anio, balance=None, resultados=None):
    p, _ = get_or_create_fiscal_period(s, anio)
    for datos, tipo in ((balance or {}, Tipo.BALANCE), (resultados or {}, Tipo.RESULTADOS)):
        for codigo, valor in datos.items():
            upsert_entry(s, fiscal_period_id=p.id, account_id=_cuenta(s, codigo).id, valor=str(valor), tipo=tipo)
    return p


def _completo(s, anio, activo, patrimonio, ingresos, utilidad):
    """Balance y Estado de Resultados completos: costo = ingresos - utilidad;
    gastos operativos e ISR capturados en 0; resultado del ejercicio = utilidad."""
    return _capturar(
        s, anio,
        {"1001": activo, "2001": activo - patrimonio, "3001": patrimonio - utilidad, "3004": utilidad},
        {"4001": ingresos, "5001": ingresos - utilidad, "6001": 0, "8001": 0},
    )


# ------------------------------------------------------------------ saldos al cierre (trabajo ANF, 8.4, 9.5 y 9.6)

def test_no_usa_el_balance_del_ejercicio_inmediato_anterior(bd):
    with session_scope() as s:
        _completo(s, 2021, 1000, 600, 1000, 100)
        r = compute_dupont(s, _completo(s, 2022, 1200, 700, 1200, 150))
    assert (r.activo_total, r.patrimonio_total) == (Decimal("1200.00"), Decimal("700.00"))
    assert r.roe_directo_pct == Decimal("21.43")  # 150 / 700
    assert not hasattr(r, "activo_promedio") and not hasattr(r, "patrimonio_promedio")


@pytest.mark.parametrize("balance_2022", [
    None,
    {"1001": 1000, "3001": 1000},  # incompleto (sin Pasivo)
    {"1001": 1000, "2001": 100, "3001": 500},  # no cuadra
    {"1001": 0, "2001": 0, "3001": 0},  # activo total cero
])
def test_el_estado_del_balance_anterior_no_afecta_ni_aproxima(bd, balance_2022):
    with session_scope() as s:
        _completo(s, 2021, 5000, 3000, 5000, 1)
        if balance_2022 is not None:
            _capturar(s, 2022, balance_2022)
        r = compute_dupont(s, _completo(s, 2023, 2000, 1000, 2000, 200))
    assert r.disponible and resumen(banderas_dupont(r)) == "DEFINITIVO"
    assert r.rotacion_activos == Decimal("1") and r.multiplicador_capital == Decimal("2")
    assert r.roe_dupont_pct == Decimal("20.00")
    assert not any("aproximad" in a.lower() for a in r.advertencias)


def test_saldos_manuales_completos_se_conservan_pero_no_se_usan(bd):
    with session_scope() as s:
        p = _completo(s, 2021, 1200, 700, 1200, 150)
        sin_manuales = compute_dupont(s, p)
        for codigo, valor in (("1001", "600"), ("1101", "400"), ("3001", "550"), ("3003", "50")):
            upsert_initial_balance(s, fiscal_period_id=p.id, account_id=_cuenta(s, codigo).id, valor=valor)
        r = compute_dupont(s, p)
        guardados = get_initial_balances_map(s, p.id)
    assert len(guardados) == 4  # la funcionalidad de saldos iniciales sigue guardando
    assert r.roe == sin_manuales.roe and r.multiplicador_capital == Decimal("1200") / Decimal("700")


@pytest.mark.parametrize("manuales", [{"3001": "500"}, {"1001": "800"}, {"1001": "0", "3001": "0"}])
def test_saldos_manuales_parciales_tampoco_afectan(bd, manuales):
    with session_scope() as s:
        p = _completo(s, 2021, 1000, 600, 1000, 100)
        for codigo, valor in manuales.items():
            upsert_initial_balance(s, fiscal_period_id=p.id, account_id=_cuenta(s, codigo).id, valor=valor)
        r = compute_dupont(s, p)
    assert r.disponible and r.rotacion_activos == Decimal("1") and r.roe_dupont_pct == Decimal("16.67")


# ------------------------------------------------------------------ A-04 patrimonio no positivo

def test_patrimonio_negativo_al_cierre_hace_el_roe_no_interpretable(bd):
    with session_scope() as s:
        _completo(s, 2021, 1000, -200, 1000, 0)  # perdida con patrimonio negativo
        r = compute_dupont(s, _completo(s, 2022, 1000, -200, 1000, -100))
    assert r.disponible is False and r.interpretable is False
    assert "ROE NO INTERPRETABLE" in r.motivo_no_disponible and "al cierre" in r.motivo_no_disponible
    assert r.margen_neto == Decimal("-0.1")  # los factores quedan solo como referencia
    assert generar_interpretacion(r).startswith("No es posible generar una interpretacion")
    assert any(c.nombre.startswith("Patrimonio") and not c.correcto for c in r.controles)


@pytest.mark.parametrize("patrimonio_anterior", [-100, 0])
def test_patrimonio_anterior_no_positivo_no_invalida_el_ejercicio(bd, patrimonio_anterior):
    """Con saldos al cierre, el patrimonio del ejercicio anterior no interviene."""
    with session_scope() as s:
        _completo(s, 2021, 1000, patrimonio_anterior, 1000, 0)
        r = compute_dupont(s, _completo(s, 2022, 1000, 400, 1000, -100))
    assert r.disponible and r.interpretable and r.roe_directo_pct == Decimal("-25.00")


def test_perdida_con_patrimonio_positivo_sigue_siendo_valida(bd):
    with session_scope() as s:
        r = compute_dupont(s, _completo(s, 2021, 1000, 500, 1000, -100))
    assert r.disponible and r.interpretable
    assert r.roe_directo_pct == Decimal("-20.00") and r.margen_neto == Decimal("-0.1")


def test_reporte_dupont_no_interpretable_no_muestra_roe_ni_interpretacion(bd, monkeypatch):
    from reports import dupont_report

    errores, escritos, tablas = [], [], []
    monkeypatch.setattr(streamlit, "error", lambda m, *a, **k: errores.append(m))
    monkeypatch.setattr(streamlit, "write", lambda m, *a, **k: escritos.append(m))
    monkeypatch.setattr(streamlit, "dataframe", lambda df, *a, **k: tablas.append(df))
    with session_scope() as s:
        p = _completo(s, 2021, 1000, -200, 1000, -100)
    monkeypatch.setattr(dupont_report, "select_fiscal_period", lambda session, **k: get_fiscal_period(session, 2021))
    with render_scope() as s:
        dupont_report.render(s, get_company(s))
    assert any("Estado del reporte: NO INTERPRETABLE" in e for e in errores)  # linea comun (fase 3)
    assert any(e.startswith("ROE NO INTERPRETABLE") for e in errores)
    assert escritos == []  # sin interpretacion automatica
    valores = dict(zip(tablas[0]["Componente"], tablas[0]["Valor"]))
    assert valores["RSP / ROE DuPont"] == "NO INTERPRETABLE"
    assert "50.00%" not in " ".join(valores.values())


# ------------------------------------------------------------------ B-01 precision

def test_factores_sin_redondeo_intermedio(bd):
    with session_scope() as s:
        _capturar(s, 2021, {"1001": "1000.01", "2001": "400.00", "3001": "600.01"})
        r = compute_dupont(s, _capturar(s, 2022, {"1001": "1000.00", "2001": "400.00", "3001": "600.00"},
                                        {"4001": "1000", "8001": "900"}))
    assert r.multiplicador_capital == Decimal("1000.00") / Decimal("600.00")
    assert r.rsa == r.margen_neto * r.rotacion_activos
    assert r.roe == r.rsa * r.multiplicador_capital


@pytest.mark.parametrize("activo, patrimonio, ingresos, utilidad", [
    (3333, 1111, 7777, 123),
    (987654.32, 123456.78, 2345678.91, 34567.89),
    (1000, 600, 1000, 100),
])
def test_factores_mostrados_con_cuatro_decimales_reproducen_el_roe(bd, activo, patrimonio, ingresos, utilidad):
    with session_scope() as s:
        p = _capturar(s, 2021, {"1001": activo, "2001": Decimal(str(activo)) - Decimal(str(patrimonio)), "3001": patrimonio},
                      {"4001": ingresos, "8001": Decimal(str(ingresos)) - Decimal(str(utilidad))})
        r = compute_dupont(s, p)
    margen = Decimal(format_percent(r.margen_neto * 100, 4).rstrip("%"))
    rotacion = Decimal(format_ratio(r.rotacion_activos, 4).split()[0])
    multiplicador = Decimal(format_ratio(r.multiplicador_capital, 4).split()[0])
    assert abs((margen * rotacion * multiplicador).quantize(Decimal("0.01")) - r.roe_dupont_pct) <= Decimal("0.01")


# ------------------------------------------------------------------ B-02 controles

def test_controles_utiles_en_lugar_de_la_identidad(bd):
    with session_scope() as s:
        _completo(s, 2021, 1000, 600, 1000, 100)
        bueno = compute_dupont(s, _completo(s, 2022, 1200, 700, 1200, 150))
        malo = compute_dupont(s, _capturar(s, 2024, {"1001": 1000, "2001": 300, "3004": 50},
                                           {"4001": 1000, "8001": 900}))
    assert [c.nombre for c in bueno.controles] == [
        "Balance del ejercicio cuadra", "Balance del ejercicio completo", "Estado de Resultados completo",
        "Resultado del ejercicio conciliado con la utilidad neta",
        "Signos según la convención", "Patrimonio total al cierre positivo",
    ]
    assert all(c.correcto for c in bueno.controles)
    fallidos = {c.nombre for c in malo.controles if not c.correcto}
    assert {"Balance del ejercicio cuadra", "Estado de Resultados completo",
            "Resultado del ejercicio conciliado con la utilidad neta"} <= fallidos
    assert "coincide" not in generar_interpretacion(bueno)


# ------------------------------------------------------------------ M-04 completitud

def test_ausencia_frente_a_cero_explicito(bd):
    with session_scope() as s:
        p = _capturar(s, 2021, {"1001": 100})
        solo_activo = compute_balance_sheet(s, p.id)
        _capturar(s, 2021, {"2001": 0, "3001": 0})
        con_ceros = compute_balance_sheet(s, p.id)
    assert solo_activo.completo is False and solo_activo.categorias_faltantes == ["Pasivo", "Patrimonio"]
    assert "2001" in [c.codigo for c in solo_activo.cuentas_sin_dato]
    assert con_ceros.completo is True and con_ceros.categorias_faltantes == []
    assert "2001" not in [c.codigo for c in con_ceros.cuentas_sin_dato]


def test_estado_de_resultados_completo_e_incompleto(bd):
    with session_scope() as s:
        p = _capturar(s, 2021, resultados={"4001": 1000, "5001": 600})
        incompleto = compute_income_statement(s, p.id)
        _capturar(s, 2021, resultados={"6001": 100, "8001": 0})
        completo = compute_income_statement(s, p.id)
    assert incompleto.completo is False
    assert incompleto.categorias_faltantes == ["Gastos operativos", "Impuesto sobre la renta"]
    assert completo.completo is True and completo.utilidad_neta == Decimal("300.00")


# ------------------------------------------------------------------ A-05 signos

@pytest.mark.parametrize("codigo, valor, avisa", [
    ("1102", "300", True), ("1102", "-300", False), ("1001", "-5", True), ("1001", "0", False),
    ("2001", "-10", True), ("3001", "-10", True), ("3003", "-500", False), ("3004", "-80", False),
    ("4001", "-1", True), ("5001", "-600", True), ("5001", "600", False), ("6003", "-5", True),
    ("7004", "-5", True), ("8001", "-25", True),
])
def test_convencion_de_signos(bd, codigo, valor, avisa):
    with session_scope() as s:
        assert (aviso_signo(_cuenta(s, codigo), Decimal(valor)) is not None) is avisa


def test_isr_negativo_pide_explicacion(bd):
    with session_scope() as s:
        assert "beneficio fiscal" in aviso_signo(_cuenta(s, "8001"), Decimal("-25"))


def test_signo_incorrecto_se_advierte_sin_modificar_el_importe(bd):
    with session_scope() as s:
        p = _capturar(s, 2021, {"1101": 1000, "1102": 300}, {"4001": 1000, "5001": -600})
        bs, inc = compute_balance_sheet(s, p.id), compute_income_statement(s, p.id)
        guardados = get_entries_map(s, p.id, Tipo.BALANCE)
    assert bs.activo_no_corriente.subtotal == Decimal("1300.00")  # no se invierte
    assert guardados[_cuenta(s, "1102").id] == Decimal("300.00")
    assert len(bs.advertencias_signo) == 1 and "1102" in bs.advertencias_signo[0]
    assert inc.utilidad_bruta == Decimal("1600.00") and "5001" in inc.advertencias_signo[0]


def _capturar_formulario(monkeypatch, valores, confirmar):
    from modules import data_entry

    monkeypatch.setattr(streamlit, "number_input", lambda label, *a, value=None, **k: valores.get(label.split(" — ")[0], value))
    monkeypatch.setattr(streamlit, "checkbox", lambda *a, **k: confirmar)
    monkeypatch.setattr(streamlit, "form_submit_button", lambda *a, **k: True)
    # Fase 4 (M-10): el usuario confirma el alcance mostrado antes de escribir.
    monkeypatch.setattr(streamlit, "button", lambda label, *a, **k: label == "Confirmar y guardar")
    monkeypatch.setattr(streamlit, "rerun", lambda *a, **k: None)
    with render_scope() as s:
        p = get_fiscal_period(s, 2021)
        data_entry._render_grupos(s, p, Tipo.RESULTADOS, data_entry.GRUPOS_RESULTADOS, "USD", "f")


@pytest.mark.parametrize("confirmar, esperado", [(False, {}), (True, {"4001": Decimal("1000.00"), "5001": Decimal("-600.00")})])
def test_captura_con_signo_atipico_requiere_confirmacion(bd, monkeypatch, confirmar, esperado):
    avisos = []
    monkeypatch.setattr(streamlit, "warning", lambda m, *a, **k: avisos.append(m))
    with session_scope() as s:
        get_or_create_fiscal_period(s, 2021)
    _capturar_formulario(monkeypatch, {"4001": 1000.0, "5001": -600.0}, confirmar)
    with session_scope() as s:
        p = get_fiscal_period(s, 2021)
        guardado = {s.get(Account, i).codigo: v for i, v in get_entries_map(s, p.id, Tipo.RESULTADOS).items()}
    assert guardado == esperado
    if not confirmar:
        assert avisos and "5001" in avisos[0]


def test_edicion_con_signo_atipico_requiere_confirmacion(bd, monkeypatch):
    from modules import data_edit

    with session_scope() as s:
        _capturar(s, 2021, {"1101": 1000, "1102": -300})

    def editor(df, **k):
        df = df.copy()
        df.loc[df["Código"] == "1102", "Valor"] = 300.0
        return df

    monkeypatch.setattr(streamlit, "data_editor", editor)
    # Fase 4 (M-10): "Guardar cambios" y despues "Confirmar y guardar".
    monkeypatch.setattr(streamlit, "button", lambda label, *a, **k: label in ("Guardar cambios", "Confirmar y guardar"))
    monkeypatch.setattr(streamlit, "rerun", lambda *a, **k: None)
    for confirmar, esperado in ((False, Decimal("-300.00")), (True, Decimal("300.00"))):
        monkeypatch.setattr(streamlit, "checkbox", lambda *a, _c=confirmar, **k: _c)
        with render_scope() as s:
            data_edit._tabla_editable(s, get_fiscal_period(s, 2021).id, Tipo.BALANCE, "USD", key="k")
        with session_scope() as s:
            assert get_entries_map(s, get_fiscal_period(s, 2021).id, Tipo.BALANCE)[_cuenta(s, "1102").id] == esperado


@pytest.mark.parametrize("confirmar, importados", [(False, 1), (True, 2)])
def test_importacion_con_signo_atipico_requiere_confirmacion(bd, monkeypatch, confirmar, importados):
    from modules import excel_import

    wb = Workbook()
    ws = wb.active
    ws.append(excel_import.COLUMNAS)
    ws.append(["1101", "PPE", "", "", 2021, 1000])
    ws.append(["1102", "Depreciación", "", "", 2021, 300])
    archivo = io.BytesIO()
    wb.save(archivo)
    archivo.seek(0)
    monkeypatch.setattr(streamlit, "file_uploader", lambda *a, **k: archivo)
    monkeypatch.setattr(streamlit, "button", lambda label, *a, **k: label == "Confirmar importación")
    monkeypatch.setattr(streamlit, "checkbox", lambda label, *a, **k: confirmar and "signo" in label)
    with render_scope() as s:
        excel_import.render(s, get_company(s))
    with session_scope() as s:
        assert len(get_entries_map(s, get_fiscal_period(s, 2021).id, Tipo.BALANCE)) == importados


def test_plantilla_documenta_la_convencion(bd):
    from database.enums import BALANCE_CATEGORIAS
    from modules.excel_import import _generar_plantilla

    with session_scope() as s:
        datos = _generar_plantilla(s, BALANCE_CATEGORIAS)
    hojas = pd.read_excel(io.BytesIO(datos), sheet_name=None)
    assert list(hojas) == ["Plantilla", "Convención de signos"]
    assert "correctoras" in " ".join(hojas["Convención de signos"].astype(str).values.ravel().tolist() +
                                     list(hojas["Convención de signos"].columns))


# ------------------------------------------------------------------ M-07 conciliacion

def test_conciliacion_cuadra_con_estados_completos(bd):
    with session_scope() as s:
        p = _completo(s, 2021, 1000, 600, 1000, 100)
        c = conciliar_resultado(compute_balance_sheet(s, p.id), compute_income_statement(s, p.id))
    assert c.estado == CONCILIADO and c.diferencia == Decimal("0.00")


def test_diferencia_real_con_estados_completos(bd):
    with session_scope() as s:
        p = _completo(s, 2021, 1000, 600, 1000, 100)
        _capturar(s, 2021, {"3004": 130, "3001": 470})  # patrimonio sigue en 600 y el balance cuadra
        c = conciliar_resultado(compute_balance_sheet(s, p.id), compute_income_statement(s, p.id))
        guardado = get_entries_map(s, p.id, Tipo.BALANCE)[_cuenta(s, "3004").id]
    assert c.estado == DIFERENCIA and c.diferencia == Decimal("30.00") and c.datos_faltantes is False
    assert "diferencia real" in c.mensaje and guardado == Decimal("130.00")  # no se corrige


def test_diferencia_con_estado_incompleto_apunta_a_datos_faltantes(bd):
    with session_scope() as s:
        # Utilidad neta 200 (ER sin gastos operativos ni ISR) frente a resultado del ejercicio 100.
        p = _capturar(s, 2021, {"1001": 1000, "2001": 400, "3001": 500, "3004": 100}, {"4001": 1000, "5001": 800})
        c = conciliar_resultado(compute_balance_sheet(s, p.id), compute_income_statement(s, p.id))
    assert c.estado == DIFERENCIA and c.datos_faltantes is True and "datos faltantes" in c.mensaje


def test_conciliacion_sin_datos(bd):
    with session_scope() as s:
        p = _capturar(s, 2021, {"1001": 1000, "2001": 400, "3001": 600}, {"4001": 1000})
        c = conciliar_resultado(compute_balance_sheet(s, p.id), compute_income_statement(s, p.id))
    assert c.estado == SIN_DATOS and c.diferencia is None and "Resultado del ejercicio" in c.mensaje
