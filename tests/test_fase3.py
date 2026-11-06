"""Fase 3: reportes y exportaciones (A-06, M-03, M-08, B-03 y banderas).

LibreOffice no esta instalado en este equipo, asi que las formulas de
control de los Excel se verifican con un evaluador propio (_evaluar) de la
gramatica que genera reports/excel_export.py: =SUM(Cn:Cm), =±Cn±Cm, =0,
=Cn-Dn y =Cn/$C$b*100 (con signo menos en las lineas que restan).
"""
import io
import re
from decimal import Decimal

import pytest
import streamlit
from openpyxl import load_workbook
from reportlab import rl_config

from calculations.balance_sheet import compute_balance_sheet
from calculations.banderas import (
    DEFINITIVO,
    INCOMPLETO,
    NO_INTERPRETABLE,
    banderas_balance,
    banderas_dupont,
    banderas_resultados,
    resumen,
)
from calculations.controls import conciliar_resultado
from calculations.dupont import compute_dupont
from calculations.income_statement import compute_income_statement
from calculations.vertical_analysis import compute_vertical_balance, compute_vertical_income
from database import connection
from database.connection import init_db, render_scope, session_scope
from database.enums import CategoriaPrincipal as Cat
from database.enums import NaturalezaSaldo as Nat
from database.enums import Subcategoria as Sub
from database.enums import TipoEstadoFinanciero as Tipo
from database.repositories import (
    create_account,
    get_account_by_codigo,
    get_company,
    get_fiscal_period,
    get_or_create_fiscal_period,
    save_company,
    upsert_entry,
)
from database.seed import seed_default_accounts
from reports.excel_export import export_balance_excel, export_dupont_excel, export_income_excel, export_vertical_excel
from reports.pdf_export import export_balance_pdf, export_dupont_pdf, export_income_pdf, export_vertical_pdf

BALANCE_COMPLETO = {"1001": "300.50", "1002": "200.25", "1101": "800.00", "1102": "-300.75", "2001": "250.00",
                    "2101": "150.00", "3001": "400.00", "3003": "100.00", "3004": "100.00"}
RESULTADOS_COMPLETO = {"4001": "10000", "5001": "6000", "6001": "1000", "6002": "800", "6003": "150", "6004": "50",
                       "7001": "120", "7002": "420", "7003": "30", "7004": "10", "8001": "605"}


@pytest.fixture()
def bd(tmp_path):
    init_db(db_path=tmp_path / "fase3.db")
    with session_scope() as s:
        seed_default_accounts(s)
        save_company(s, nombre_legal="Acero & Aluminio, S. A. de C. V.", nombre_comercial="AA", actividad_economica="x",
                     pais="SV", moneda="USD", anio_inicial_analisis=2021)
    yield
    connection.dispose_engine()


def _capturar(s, anio, balance=None, resultados=None):
    p, _ = get_or_create_fiscal_period(s, anio)
    for datos, tipo in ((balance or {}, Tipo.BALANCE), (resultados or {}, Tipo.RESULTADOS)):
        for codigo, valor in datos.items():
            upsert_entry(s, fiscal_period_id=p.id, account_id=get_account_by_codigo(s, codigo).id, valor=str(valor), tipo=tipo)
    return p


# ------------------------------------------------------------------ evaluador de formulas

def _numero(ws, ref: str) -> Decimal:
    valor = ws[ref.replace("$", "")].value
    assert isinstance(valor, (int, float)), f"{ref} no es numerico: {valor!r}"
    return Decimal(str(valor))


def _evaluar(ws, formula: str) -> Decimal:
    cuerpo = formula[1:]
    if m := re.fullmatch(r"SUM\(C(\d+):C(\d+)\)", cuerpo):
        return sum((_numero(ws, f"C{f}") for f in range(int(m[1]), int(m[2]) + 1)), Decimal(0))
    if m := re.fullmatch(r"(-?)C(\d+)/\$C\$(\d+)\*100", cuerpo):
        return (-1 if m[1] else 1) * _numero(ws, f"C{m[2]}") / _numero(ws, f"C{m[3]}") * 100
    if m := re.fullmatch(r"C(\d+)-D(\d+)", cuerpo):
        return _numero(ws, f"C{m[1]}") - _evaluar(ws, ws[f"D{m[2]}"].value)
    if cuerpo == "0":
        return Decimal(0)
    assert re.fullmatch(r"[+-]?C\d+([+-]C\d+)*", cuerpo), f"formula inesperada: {formula}"
    total = Decimal(0)
    for signo, fila in re.findall(r"([+-]?)C(\d+)", cuerpo):
        total += (-1 if signo == "-" else 1) * _numero(ws, f"C{fila}")
    return total


def _formulas(ws):
    return {c.coordinate: c.value for fila in ws.iter_rows() for c in fila if isinstance(c.value, str) and c.value.startswith("=")}


def _verificar_libro(datos: bytes):
    """Sin referencias circulares, columna C sin formulas, y cada control
    D (y diferencia E) cuadra con el importe C calculado por Python."""
    ws = load_workbook(io.BytesIO(datos)).active
    formulas = _formulas(ws)
    for celda, formula in formulas.items():
        assert celda not in re.findall(r"[A-Z]+\d+", formula.replace("$", "")), f"circular: {celda} {formula}"
        assert not celda.startswith("C"), f"la columna C debe tener valores, no formulas: {celda}"
    controles = {c: f for c, f in formulas.items() if c.startswith("D")}
    for celda, formula in controles.items():
        fila = celda[1:]
        assert abs(_evaluar(ws, formula) - _numero(ws, f"C{fila}")) < Decimal("0.005"), (celda, formula)
        assert abs(_evaluar(ws, ws[f"E{fila}"].value)) < Decimal("0.005")
    return ws, controles


def _fila(ws, etiqueta: str) -> int:
    return next(c.row for c in ws["B"] if c.value == etiqueta)


# ------------------------------------------------------------------ A-06 / B-03 Excel

def test_excel_balance_completo_controles_y_valores(bd):
    with session_scope() as s:
        p = _capturar(s, 2021, BALANCE_COMPLETO)
        bs = compute_balance_sheet(s, p.id)
        ws, controles = _verificar_libro(export_balance_excel(get_company(s), p, bs))
    assert len(controles) == 12  # 7 subtotales de grupos con datos + 5 totales
    assert _numero(ws, f"C{_fila(ws, 'TOTAL ACTIVO')}") == bs.total_activo == Decimal("1000.00")
    assert _numero(ws, f"C{_fila(ws, 'TOTAL PASIVO + PATRIMONIO')}") == bs.total_pasivo_patrimonio
    assert ws["A6"].value == "Estado del reporte: DEFINITIVO"


def test_excel_balance_con_grupos_vacios_sin_circulares(bd):
    with session_scope() as s:
        p = _capturar(s, 2021, {"1001": "100", "2001": "40", "3001": "60"})  # escenario G01
        bs = compute_balance_sheet(s, p.id)
        ws, _ = _verificar_libro(export_balance_excel(get_company(s), p, bs))
    sin_datos = [c.row for c in ws["B"] if c.value == "Sin datos"]
    assert len(sin_datos) == 6  # ANC, PNC y 4 grupos de patrimonio sin cuentas
    assert ws[f"D{_fila(ws, 'TOTAL ACTIVO')}"].value == f"=C{_fila(ws, 'Subtotal Activo corriente')}"


def test_excel_resultados_completo_y_parcial(bd):
    with session_scope() as s:
        p = _capturar(s, 2021, resultados=RESULTADOS_COMPLETO)
        inc = compute_income_statement(s, p.id)
        ws, _ = _verificar_libro(export_income_excel(get_company(s), p, inc))
        p2 = _capturar(s, 2022, resultados={"4001": "1000", "5001": "600"})  # escenario G02
        inc2 = compute_income_statement(s, p2.id)
        ws2, _ = _verificar_libro(export_income_excel(get_company(s), p2, inc2))
    for etiqueta, valor in (("UTILIDAD BRUTA", "4000"), ("UTILIDAD OPERATIVA", "2300"), ("RESULTADO FINANCIERO", "-300"),
                            ("OTROS RESULTADOS NO OPERATIVOS", "20"), ("UTILIDAD ANTES DE IMPUESTOS", "2020"),
                            ("UTILIDAD NETA", "1415")):
        assert _numero(ws, f"C{_fila(ws, etiqueta)}") == Decimal(valor)
    assert _numero(ws2, f"C{_fila(ws2, 'UTILIDAD NETA')}") == inc2.utilidad_neta == Decimal("400.00")
    assert ws2.cell(6, 1).value.startswith("Estado del reporte: INCOMPLETO")


def test_excel_legible_sin_recalcular(bd):
    """Un visor que no recalcula (data_only) ve todos los importes y totales."""
    with session_scope() as s:
        p = _capturar(s, 2021, BALANCE_COMPLETO)
        datos = export_balance_excel(get_company(s), p, compute_balance_sheet(s, p.id))
    ws = load_workbook(io.BytesIO(datos), data_only=True).active
    for etiqueta in ("TOTAL ACTIVO", "TOTAL PASIVO", "TOTAL PATRIMONIO", "TOTAL PASIVO + PATRIMONIO"):
        assert isinstance(ws[f"C{_fila(ws, etiqueta)}"].value, (int, float))


def test_excel_banderas_coinciden_con_pantalla(bd):
    with session_scope() as s:
        p = _capturar(s, 2021, {"1101": "1000", "1102": "300", "2001": "500", "3004": "50"}, {"4001": "100"})
        bs, inc = compute_balance_sheet(s, p.id), compute_income_statement(s, p.id)
        banderas = banderas_balance(bs, conciliar_resultado(bs, inc))
        ws = load_workbook(io.BytesIO(export_balance_excel(get_company(s), p, bs, banderas))).active
    estado = resumen(banderas)
    assert estado == "DESCUADRADO · SIGNO ATÍPICO · SIN CONCILIAR"
    assert ws["A6"].value == f"Estado del reporte: {estado}"
    assert [ws.cell(7 + i, 1).value.split(":")[0] for i in range(len(banderas))] == [b.codigo for b in banderas]


# ------------------------------------------------------------------ M-03 vertical

def test_vertical_balance_incluye_subtotales_y_totales(bd):
    with session_scope() as s:
        p = _capturar(s, 2021, BALANCE_COMPLETO)
        r = compute_vertical_balance(s, p.id)
    sub = {l.etiqueta: (l.valor, l.porcentaje) for l in r.subtotales}
    assert sub == {
        "Activo corriente": (Decimal("500.75"), Decimal("50.08")),
        "Activo no corriente": (Decimal("499.25"), Decimal("49.93")),
        "TOTAL ACTIVO": (Decimal("1000.00"), Decimal("100.00")),
        "Pasivo corriente": (Decimal("250.00"), Decimal("25.00")),
        "Pasivo no corriente": (Decimal("150.00"), Decimal("15.00")),
        "TOTAL PASIVO": (Decimal("400.00"), Decimal("40.00")),
        "TOTAL PATRIMONIO": (Decimal("600.00"), Decimal("60.00")),
        "TOTAL PASIVO + PATRIMONIO": (Decimal("1000.00"), Decimal("100.00")),
    }
    # La suma de los porcentajes de AC y ANC es 100 +/- 0.01 (redondeo de cada linea).
    assert abs(sub["Activo corriente"][1] + sub["Activo no corriente"][1] - 100) <= Decimal("0.01")
    assert [l.tipo for l in r.lineas].count("cuenta") == len(r.filas) == 9


def test_vertical_resultados_incluye_ingresos_utilidades_y_efecto(bd):
    with session_scope() as s:
        p = _capturar(s, 2021, resultados=RESULTADOS_COMPLETO)
        r = compute_vertical_income(s, p.id)
    sub = {l.etiqueta: (l.valor, l.porcentaje, l.efecto) for l in r.subtotales}
    assert sub["Ingresos netos"] == (Decimal("10000.00"), Decimal("100.00"), "")
    assert sub["Costo de ventas"] == (Decimal("6000.00"), Decimal("-60.00"), "resta")  # importe positivo, % negativo
    assert sub["UTILIDAD BRUTA"][:2] == (Decimal("4000.00"), Decimal("40.00"))
    assert sub["Gastos operativos netos"] == (Decimal("1700.00"), Decimal("-17.00"), "resta")
    assert sub["UTILIDAD OPERATIVA"][:2] == (Decimal("2300.00"), Decimal("23.00"))
    assert sub["Resultado financiero"][:2] == (Decimal("-300.00"), Decimal("-3.00"))
    assert sub["UTILIDAD ANTES DE IMPUESTOS"][:2] == (Decimal("2020.00"), Decimal("20.20"))
    assert sub["Impuesto sobre la renta"] == (Decimal("605.00"), Decimal("-6.05"), "resta")
    assert sub["UTILIDAD NETA"][:2] == (Decimal("1415.00"), Decimal("14.15"))
    # Margenes coherentes con los signos del trabajo: UB% + gastos% = UO%; UAI% + ISR% = UN%.
    assert sub["UTILIDAD BRUTA"][1] + sub["Gastos operativos netos"][1] == sub["UTILIDAD OPERATIVA"][1]
    assert sub["UTILIDAD ANTES DE IMPUESTOS"][1] + sub["Impuesto sobre la renta"][1] == sub["UTILIDAD NETA"][1]


def test_vertical_grupos_vacios_sin_datos_y_base_cero(bd):
    with session_scope() as s:
        p = _capturar(s, 2021, {"1001": "100"}, {"5001": "50"})
        balance, resultados = compute_vertical_balance(s, p.id), compute_vertical_income(s, p.id)
    sub = {l.etiqueta: (l.valor, l.porcentaje) for l in balance.subtotales}
    assert sub["Activo no corriente"] == (None, None) and sub["TOTAL PASIVO"] == (None, None)
    assert sub["TOTAL PASIVO + PATRIMONIO"] == (Decimal("0.00"), Decimal("0.00"))
    assert not resultados.disponible  # ingresos = 0: base cero
    assert all(l.porcentaje is None for l in resultados.lineas)


def test_excel_vertical_base_numerica_y_controles(bd):
    with session_scope() as s:
        p = _capturar(s, 2021, resultados=RESULTADOS_COMPLETO)
        r = compute_vertical_income(s, p.id)
        datos = export_vertical_excel(get_company(s), p, "Vertical", None, r.base_ingresos_netos, "Ingresos Netos", r.lineas)
    ws = load_workbook(io.BytesIO(datos)).active
    fila_base = next(c.row for c in ws["A"] if c.value == "Base (100%)")
    assert ws[f"C{fila_base}"].value == 10000.0
    controles = {c: f for c, f in _formulas(ws).items() if c.startswith("F")}
    assert controles
    for celda, formula in controles.items():
        assert abs(_evaluar(ws, formula) - Decimal(str(ws[f"D{celda[1:]}"].value))) <= Decimal("0.005")
    neta = next(c.row for c in ws["B"] if c.value == "UTILIDAD NETA")
    assert ws[f"D{neta}"].value == 14.15 and ws[f"E{_fila(ws, 'Costo de ventas')}"].value == "(−) resta"


def test_excel_vertical_formato_anterior_base_numerica(bd):
    import pandas as pd

    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2021)
        df = pd.DataFrame([{"Código": "1001", "Cuenta": "Efectivo", "Valor": 300.0, "Participación %": 30.0},
                           {"Código": "1002", "Cuenta": "CxC", "Valor": 0.0, "Participación %": None}])
        ws = load_workbook(io.BytesIO(export_vertical_excel(get_company(s), p, "V", df, Decimal("1000"), "Total Activo"))).active
    fila_base = next(c.row for c in ws["A"] if c.value == "Base (100%)")
    assert ws[f"C{fila_base}"].value == 1000.0
    assert [ws[f"D{fila_base + 3 + i}"].value for i in range(2)] == [30.0, "No disponible"]


# ------------------------------------------------------------------ DuPont Excel / PDF

def test_excel_dupont_primer_ejercicio_y_no_interpretable(bd):
    with session_scope() as s:
        primero = compute_dupont(s, _capturar(s, 2021, {"1001": "1000", "2001": "400", "3001": "600"}, {"4001": "1000", "8001": "900"}))
        ws = load_workbook(io.BytesIO(export_dupont_excel(get_company(s), get_fiscal_period(s, 2021), primero))).active
        malo = compute_dupont(s, _capturar(s, 2025, {"1001": "1000", "2001": "1200", "3003": "-200"}, {"4001": "1000", "8001": "1100"}))
        ws2 = load_workbook(io.BytesIO(export_dupont_excel(get_company(s), get_fiscal_period(s, 2025), malo))).active
    textos = [c.value for c in ws["A"] if isinstance(c.value, str)]
    assert any(t.startswith("Estado del reporte:") for t in textos)
    assert not any("APROXIMADO" in t or "promedio" in t.split(":")[0].lower() for t in textos)
    assert "Enfoque total" in textos and "Enfoque de la controladora" in textos
    valores = {ws2.cell(r, 1).value: ws2.cell(r, 2).value for r in range(1, ws2.max_row + 1)}
    assert valores["RSP / ROE DuPont (%)"] == "NO INTERPRETABLE" and valores["ROE directo (comprobación) (%)"] == "NO INTERPRETABLE"
    assert any(isinstance(v, str) and v.startswith(f"Estado del reporte: {NO_INTERPRETABLE}") for v in valores)


# ------------------------------------------------------------------ PDF

def _pdf_texto(datos: bytes) -> str:
    return datos.decode("latin-1")


@pytest.fixture()
def pdf_sin_compresion(monkeypatch):
    monkeypatch.setattr(rl_config, "pageCompression", 0)


def test_pdf_estados_con_banderas(bd, pdf_sin_compresion):
    with session_scope() as s:
        p = _capturar(s, 2021, {"1001": "100"}, {"4001": "1000", "5001": "600"})
        bs, inc = compute_balance_sheet(s, p.id), compute_income_statement(s, p.id)
        balance = _pdf_texto(export_balance_pdf(get_company(s), p, bs))
        resultados = _pdf_texto(export_income_pdf(get_company(s), p, inc))
        p2 = _capturar(s, 2022, BALANCE_COMPLETO)
        completo = _pdf_texto(export_balance_pdf(get_company(s), p2, compute_balance_sheet(s, p2.id)))
    assert INCOMPLETO in balance and "DESCUADRADO" in balance and "Sin datos capturados" in balance
    assert INCOMPLETO in resultados
    assert DEFINITIVO in completo and INCOMPLETO not in completo


def test_pdf_nombre_largo_no_se_corta(bd, pdf_sin_compresion):
    nombre = "Propiedades de inversion valuadas a valor razonable con cambios en resultados segun NIIF FINALDELNOMBRE"
    with session_scope() as s:
        create_account(s, codigo="1105", nombre=nombre, categoria_principal=Cat.ACTIVO, subcategoria=Sub.NO_CORRIENTE,
                       naturaleza_saldo=Nat.DEUDORA, orden_presentacion=135)
        p = _capturar(s, 2021, {"1001": "100", "1105": "123456789.01", "2001": "0", "3001": "123456889.01"})
        texto = _pdf_texto(export_balance_pdf(get_company(s), p, compute_balance_sheet(s, p.id)))
    assert "FINALDELNOMBRE" in texto  # la ultima palabra del nombre se imprime (ajuste de linea)
    assert "123,456,789.01" in texto and "123,456,889.01" in texto


def test_pdf_vertical_y_dupont(bd, pdf_sin_compresion):
    with session_scope() as s:
        p = _capturar(s, 2021, BALANCE_COMPLETO, RESULTADOS_COMPLETO)
        r = compute_vertical_income(s, p.id)
        inc = compute_income_statement(s, p.id)
        vertical = _pdf_texto(export_vertical_pdf(get_company(s), p, "Vertical", r.lineas, r.base_ingresos_netos,
                                                  "Ingresos Netos", banderas_resultados(inc)))
        dp = compute_dupont(s, p)
        dupont = _pdf_texto(export_dupont_pdf(get_company(s), p, dp))
        malo = compute_dupont(s, _capturar(s, 2025, {"1001": "1000", "2001": "1200", "3003": "-200"}, {"4001": "1000", "8001": "1100"}))
        dupont_malo = _pdf_texto(export_dupont_pdf(get_company(s), get_fiscal_period(s, 2025), malo))
    for texto in ("UTILIDAD NETA", "14.15%", "UTILIDAD BRUTA", "40.00%", "resta"):
        assert texto in vertical
    assert "APROXIMADO" not in dupont and "Controles de los datos" in dupont and "Enfoque total" in dupont
    assert NO_INTERPRETABLE in dupont_malo and "%PDF" in dupont_malo[:5]


# ------------------------------------------------------------------ M-08 Dashboard

def _metricas_dashboard(monkeypatch):
    from streamlit.delta_generator import DeltaGenerator

    from modules import dashboard

    metricas, avisos = {}, []
    monkeypatch.setattr(DeltaGenerator, "metric", lambda self, etiqueta, valor, *a, **k: metricas.__setitem__(etiqueta, valor))
    monkeypatch.setattr(streamlit, "warning", lambda m, *a, **k: avisos.append(m))
    monkeypatch.setattr(streamlit, "error", lambda m, *a, **k: avisos.append(m))
    monkeypatch.setattr(streamlit, "multiselect", lambda *a, **k: [])
    with render_scope() as s:
        dashboard.render(s, get_company(s))
    return metricas, avisos


def test_dashboard_primer_ejercicio_no_es_aproximado(bd, monkeypatch):
    with session_scope() as s:
        _capturar(s, 2021, {"1001": "1000", "2001": "400", "3001": "500", "3004": "100"},
                  {"4001": "1000", "5001": "900", "6001": "0", "8001": "0"})
    metricas, avisos = _metricas_dashboard(monkeypatch)
    assert metricas["ROE (DuPont) — definitivo"] == "16.67%"  # 100 / 600, saldos al cierre
    assert metricas["ROE (al cierre)"] == "16.67%" and not avisos
    assert metricas["Total Activos"] == "USD 1,000.00"  # balance completo y conciliado: sin etiqueta


def test_dashboard_roe_definitivo(bd, monkeypatch):
    with session_scope() as s:
        for anio in (2021, 2022):
            _capturar(s, anio, {"1001": "1000", "2001": "400", "3001": "500", "3004": "100"},
                      {"4001": "1000", "5001": "900", "6001": "0", "8001": "0"})
    metricas, avisos = _metricas_dashboard(monkeypatch)
    assert metricas["ROE (DuPont) — definitivo"] == "16.67%" and not avisos


def test_dashboard_roe_no_interpretable_e_indicadores_incompletos(bd, monkeypatch):
    with session_scope() as s:
        _capturar(s, 2021, {"1001": "1000", "2001": "1200", "3003": "-200"}, {"4001": "1000", "8001": "1100"})
    metricas, avisos = _metricas_dashboard(monkeypatch)
    assert metricas["ROE (DuPont)"] == "NO INTERPRETABLE"
    assert any("ROE NO INTERPRETABLE" in a for a in avisos)
    assert "Ingresos Netos (INCOMPLETO)" in metricas  # sin costo de ventas ni gastos operativos
