"""Metodologia del trabajo ANF en el analisis vertical y en DuPont (secciones 7.1,
7.2, 8.4, 9.5 y 9.6), con los datos originales de Alutech cargados en una BD temporal.

Las tablas de este archivo son controles: los valores se calculan siempre a partir
de los importes de fuentes/alutech/, nunca de estas tablas.
"""
import io
import json
import subprocess
import sys
from collections import Counter
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pytest
from openpyxl import load_workbook
from reportlab import rl_config

from calculations import indicadores as ind
from calculations.banderas import banderas_balance, banderas_dupont, resumen
from calculations.comparacion_anf import COINCIDE, comparar
from calculations.comparativo import vertical_comparativo
from calculations.controls import SIN_DATOS, conciliar_resultado
from calculations.dupont import (
    compute_dupont,
    factores_controladora,
    factores_dupont,
    factores_total,
    filas_enfoque_controladora,
    filas_enfoque_total,
    formatear_fila,
)
from calculations.rubros import datos_ejercicio, datos_todos
from calculations.vertical_analysis import compute_vertical_balance, compute_vertical_income
from database import connection
from database.connection import init_db, session_scope
from database.enums import TipoEstadoFinanciero as Tipo
from database.repositories import (
    get_account_by_codigo,
    get_company,
    get_fiscal_period,
    get_initial_balances_map,
    get_or_create_fiscal_period,
    list_fiscal_periods,
    save_company,
    upsert_entry,
    upsert_initial_balance,
)
from database.seed import seed_default_accounts
from reports import secciones as sec
from reports.dupont_report import _tabla
from reports.excel_export import export_dupont_excel, export_vertical_excel
from reports.exportar_secciones import secciones_a_excel, secciones_a_pdf
from reports.informe_integral import hojas_informe
from reports.pdf_export import export_dupont_pdf, export_vertical_pdf
from scripts.cargar_alutech import cargar

PROYECTO = Path(__file__).resolve().parent.parent
ANIOS = (2021, 2022, 2023, 2024, 2025)
DUPONT = {
    "margen": ("13.09", "2.01", "2.79", "0.64", "2.71"),
    "rotacion": ("0.9459", "0.7435", "0.5915", "0.5791", "0.5622"),
    "rsa": ("12.38", "1.50", "1.65", "0.37", "1.52"),
    "maf": ("3.8119", "3.1421", "3.5538", "3.6591", "3.3831"),
    "rsp": ("47.21", "4.70", "5.86", "1.35", "5.15"),
}
CONTROLADORA = {
    "rsa": ("11.99", "1.27", "1.52", "0.37", "1.52"),
    "maf": ("3.8995", "3.2157", "3.5538", "3.6591", "3.3831"),
    "rsp": ("46.75", "4.10", "5.41", "1.35", "5.15"),
}
# (subtotal del reporte o None, grupos de analisis o None, porcentajes de la tabla 7.1)
TABLA_7_1 = [
    ("Ingresos netos", None, ("100.00", "100.00", "100.00", "100.00", "100.00")),
    ("Costo de ventas", None, ("-70.09", "-82.12", "-78.05", "-78.80", "-75.38")),
    ("UTILIDAD BRUTA", None, ("29.91", "17.88", "21.95", "21.20", "24.62")),
    (None, ("GASTOS_ADMINISTRACION",), ("-3.19", "-3.67", "-4.11", "-1.23", "-1.19")),
    (None, ("GASTOS_VENTA",), ("-6.96", "-7.95", "-9.18", "-5.51", "-4.31")),
    (None, ("DETERIORO_CXC",), ("-0.05", "-0.08", "-0.11", "0.00", "0.00")),
    (None, ("GASTOS_PERSONAL",), ("0.00", "0.00", "0.00", "-5.63", "-5.06")),
    (None, ("DEPRECIACION_AMORTIZACION",), ("0.00", "0.00", "0.00", "-1.48", "-1.63")),
    (None, ("OTROS_INGRESOS_OPERATIVOS", "OTROS_NO_OPERATIVOS"), ("0.06", "0.07", "0.78", "0.01", "-0.18")),
    ("UTILIDAD OPERATIVA", None, ("19.77", "6.24", "9.34", "7.35", "12.43")),
    (None, ("INGRESOS_FINANCIEROS",), ("0.00", "0.00", "0.00", "3.14", "3.30")),
    (None, ("GASTOS_FINANCIEROS", "GASTOS_FINANCIEROS_NETOS"), ("-4.16", "-3.44", "-4.60", "-9.00", "-11.81")),
    ("UTILIDAD ANTES DE IMPUESTOS", None, ("15.61", "2.81", "4.74", "1.50", "3.74")),
    ("Impuesto sobre la renta", None, ("-2.52", "-0.79", "-1.95", "-0.86", "-1.04")),
    ("UTILIDAD NETA", None, ("13.09", "2.01", "2.79", "0.64", "2.71")),
]
TABLA_7_2 = {
    "Activo corriente": ("69.30", "66.76", "53.12", "52.32", "31.67"),
    "Activo no corriente": ("30.70", "33.24", "46.88", "47.68", "68.33"),
    "TOTAL ACTIVO": ("100.00", "100.00", "100.00", "100.00", "100.00"),
    "Pasivo corriente": ("37.18", "34.51", "41.17", "43.88", "47.47"),
    "Pasivo no corriente": ("36.58", "33.66", "30.69", "28.79", "22.97"),
    "TOTAL PASIVO": ("73.77", "68.17", "71.86", "72.67", "70.44"),
    "TOTAL PATRIMONIO": ("26.23", "31.83", "28.14", "27.33", "29.56"),
}


def _q(valor: Decimal, decimales: int = 2) -> Decimal:
    return valor.quantize(Decimal(1).scaleb(-decimales), rounding=ROUND_HALF_UP)


def _guardar_empresa(s):
    save_company(s, nombre_legal="Alutech", nombre_comercial="Alutech", actividad_economica="metal", pais="HN", moneda="USD",
                 anio_inicial_analisis=2021)


@pytest.fixture(scope="module")
def ruta_bd(tmp_path_factory):
    ruta = tmp_path_factory.mktemp("fase8") / "financiera.db"
    informe = cargar(db_path=ruta, respaldar=False)
    assert informe.cuentas_creadas == 106
    init_db(db_path=ruta)
    with session_scope() as s:
        _guardar_empresa(s)
    connection.dispose_engine()
    return ruta


@pytest.fixture()
def s(ruta_bd):
    init_db(db_path=ruta_bd)
    with session_scope() as sesion:
        yield sesion
    connection.dispose_engine()


@pytest.fixture()
def bd_sintetica(tmp_path):
    init_db(db_path=tmp_path / "sintetica.db")
    with session_scope() as sesion:
        seed_default_accounts(sesion)
        _guardar_empresa(sesion)
    yield
    connection.dispose_engine()


def _capturar(s, anio, balance=None, resultados=None):
    p, _ = get_or_create_fiscal_period(s, anio)
    for datos, tipo in ((balance or {}, Tipo.BALANCE), (resultados or {}, Tipo.RESULTADOS)):
        for codigo, valor in datos.items():
            upsert_entry(s, fiscal_period_id=p.id, account_id=get_account_by_codigo(s, codigo).id, valor=str(valor), tipo=tipo)
    return p


# ------------------------------------------------- 1, 2 y 3. Factores, producto y ROE directo
@pytest.mark.parametrize("j, anio", enumerate(ANIOS))
def test_cinco_ejercicios_coinciden_con_las_tablas_del_trabajo(s, j, anio):
    r = compute_dupont(s, get_fiscal_period(s, anio))
    assert r.disponible and r.interpretable
    assert _q(r.margen_neto * 100) == Decimal(DUPONT["margen"][j])
    assert _q(r.rotacion_activos, 4) == Decimal(DUPONT["rotacion"][j])
    assert _q(r.rsa * 100) == Decimal(DUPONT["rsa"][j])
    assert _q(r.multiplicador_capital, 4) == Decimal(DUPONT["maf"][j])
    assert r.roe_dupont_pct == Decimal(DUPONT["rsp"][j])


@pytest.mark.parametrize("anio", ANIOS)
def test_el_producto_de_los_factores_es_el_roe_directo_antes_de_redondear(s, anio):
    r = compute_dupont(s, get_fiscal_period(s, anio))
    assert abs(r.rsa - r.margen_neto * r.rotacion_activos) < Decimal("1E-24")
    assert abs(r.roe - r.rsa * r.multiplicador_capital) < Decimal("1E-24")
    assert abs(r.roe - r.roe_directo) < Decimal("1E-24")
    assert abs(r.roe - r.utilidad_neta / r.patrimonio_total) < Decimal("1E-24")
    assert abs(r.rsa - r.rsa_directo) < Decimal("1E-24")
    assert r.roe_dupont_pct == r.roe_directo_pct


def test_formulas_con_un_caso_calculado_a_mano():
    f = factores_dupont(Decimal("100"), Decimal("1000"), Decimal("2000"), Decimal("500"))
    assert (f.margen_neto, f.rotacion_activos, f.rsa, f.maf) == (Decimal("0.1"), Decimal("0.5"), Decimal("0.05"), Decimal("4"))
    assert f.rsp == Decimal("0.2") == f.roe_directo


# ------------------------------------------------- 4 y 5. 2021 sin 2020; sin promedios
def test_2021_se_calcula_sin_balance_de_2020_y_no_es_aproximado(s):
    assert get_fiscal_period(s, 2020) is None
    r = compute_dupont(s, get_fiscal_period(s, 2021))
    assert r.disponible and r.roe_dupont_pct == Decimal("47.21")
    assert resumen(banderas_dupont(r)) == "DEFINITIVO"
    assert not any("aproximad" in texto.lower() for texto in r.advertencias + [c.detalle for c in r.controles])


def test_no_depende_del_ejercicio_anterior_ni_de_los_saldos_iniciales(bd_sintetica):
    balance = {"1001": 1000, "2001": 400, "3001": 500, "3004": 100}
    resultados = {"4001": 1000, "5001": 900, "6001": 0, "8001": 0}
    with session_scope() as s:
        p = _capturar(s, 2022, balance, resultados)
        solo = compute_dupont(s, p)
        _capturar(s, 2021, {"1001": 99999, "2001": 1, "3001": 99998}, {"4001": 5})
        upsert_initial_balance(s, fiscal_period_id=p.id, account_id=get_account_by_codigo(s, "1001").id, valor="7777")
        upsert_initial_balance(s, fiscal_period_id=p.id, account_id=get_account_by_codigo(s, "3001").id, valor="3333")
        con_otros = compute_dupont(s, p)
        assert get_initial_balances_map(s, p.id)  # los saldos iniciales se conservan
    assert (con_otros.roe, con_otros.rotacion_activos, con_otros.multiplicador_capital) == (
        solo.roe, solo.rotacion_activos, solo.multiplicador_capital)
    assert not hasattr(con_otros, "activo_promedio") and not hasattr(con_otros, "patrimonio_promedio")


def test_el_codigo_de_dupont_no_contiene_promedios_ni_saldos_iniciales():
    fuente = (PROYECTO / "calculations" / "dupont.py").read_text(encoding="utf-8")
    assert "get_initial_balances_map" not in fuente and "get_saldos_iniciales" not in fuente
    assert "/ DOS" not in fuente and "promedio =" not in fuente
    assert "calculations.dupont" not in (PROYECTO / "modules" / "data_entry.py").read_text(encoding="utf-8")


# ------------------------------------------------- 6. Enfoque total y de la controladora
@pytest.mark.parametrize("j, anio", enumerate(ANIOS))
def test_enfoque_de_la_controladora(s, j, anio):
    c = compute_dupont(s, get_fiscal_period(s, anio)).controladora
    assert _q(c.factores.rsa * 100) == Decimal(CONTROLADORA["rsa"][j])
    assert _q(c.factores.maf, 4) == Decimal(CONTROLADORA["maf"][j])
    assert _q(c.factores.rsp * 100) == Decimal(CONTROLADORA["rsp"][j])
    assert abs(c.factores.rsp - c.factores.roe_directo) < Decimal("1E-24")


def test_los_enfoques_no_se_confunden(s):
    r21 = compute_dupont(s, get_fiscal_period(s, 2021))
    assert r21.roe_dupont_pct == Decimal("47.21") and _q(r21.controladora.factores.rsp * 100) == Decimal("46.75")
    assert r21.utilidad_neta != r21.controladora.utilidad and r21.patrimonio_total != r21.controladora.patrimonio
    # Los activos son los totales de la empresa en ambos enfoques.
    assert r21.rotacion_activos == r21.controladora.factores.rotacion_activos
    r24 = compute_dupont(s, get_fiscal_period(s, 2024))
    assert r24.roe == r24.controladora.factores.rsp  # 2024 no presenta participaciones no controladoras
    etiquetas_total = {f.etiqueta for f in filas_enfoque_total(r21)}
    assert not any("controladora" in e for e in etiquetas_total)
    assert all("controladora" in f.etiqueta or f.etiqueta == "Rotación de activos" for f in filas_enfoque_controladora(r21))


# ------------------------------------------------- 7 y 8. Casos limite
def test_patrimonio_cero_no_se_calcula(bd_sintetica):
    with session_scope() as s:
        r = compute_dupont(s, _capturar(s, 2021, {"1001": 1000, "2001": 1000, "3001": 0}, {"4001": 1000, "8001": 900}))
    assert r.disponible is False and r.interpretable and "al cierre es cero" in r.motivo_no_disponible
    assert r.roe_dupont_pct is None


def test_patrimonio_negativo_no_es_interpretable_en_ningun_enfoque(bd_sintetica):
    with session_scope() as s:
        p = _capturar(s, 2021, {"1001": 1000, "2001": 1200, "3003": -200}, {"4001": 1000, "5001": 1100})
        r = compute_dupont(s, p)
        d = datos_ejercicio(s, p)
    assert r.disponible is False and r.interpretable is False and resumen(banderas_dupont(r)).startswith("NO INTERPRETABLE")
    total = {f.etiqueta: f.valor for f in filas_enfoque_total(r)}
    ctrl = {f.etiqueta: f.valor for f in filas_enfoque_controladora(r)}
    assert total["RSP / ROE DuPont"] == total["ROE directo (comprobación)"] == "NO INTERPRETABLE"
    assert ctrl["RSP / ROE (controladora)"] == "NO INTERPRETABLE"
    assert ind.calcular(d, "roe_dupont").valor is None and ind.calcular(d, "maf").valor is None
    assert ind.calcular(d, "roe").valor is None
    assert factores_total(d).rsp_interpretable is None and factores_controladora(d)[0].rsp_interpretable is None


def test_perdida_conserva_el_signo(bd_sintetica):
    with session_scope() as s:
        r = compute_dupont(s, _capturar(s, 2021, {"1001": 1000, "2001": 400, "3001": 600},
                                        {"4001": 1000, "5001": 1100, "6001": 0, "8001": 0}))
    assert r.disponible and r.roe_dupont_pct == Decimal("-16.67") == r.roe_directo_pct


@pytest.mark.parametrize("balance, resultados, texto", [
    (None, None, "Balance General"),
    ({"1001": 1000, "2001": 400, "3001": 600}, None, "Estado de Resultados"),
])
def test_sin_datos_no_hay_factores(bd_sintetica, balance, resultados, texto):
    with session_scope() as s:
        r = compute_dupont(s, _capturar(s, 2021, balance, resultados))
    assert r.disponible is False and texto in r.motivo_no_disponible and r.roe is None and r.controladora is None


def test_ejercicio_incompleto_lleva_bandera_y_ceros_no_inventados(bd_sintetica):
    with session_scope() as s:
        p = _capturar(s, 2021, {"1001": 1000, "2001": 400, "3001": 600}, {"4001": 1000, "8001": 100})
        r = compute_dupont(s, p)
        vi = compute_vertical_income(s, p.id)
    assert r.disponible and "INCOMPLETO" in resumen(banderas_dupont(r))
    sub = {l.etiqueta: l for l in vi.subtotales}
    assert sub["Costo de ventas"].valor is None and sub["Costo de ventas"].porcentaje is None


def test_ingresos_y_activo_cero_no_se_calculan(bd_sintetica):
    with session_scope() as s:
        sin_ingresos = compute_dupont(s, _capturar(s, 2021, {"1001": 1000, "2001": 400, "3001": 600}, {"4001": 0, "8001": 0}))
        sin_activo = compute_dupont(s, _capturar(s, 2022, {"1001": 0, "2001": 0, "3001": 0}, {"4001": 1000, "8001": 100}))
    assert sin_ingresos.disponible is False and "ingresos" in sin_ingresos.motivo_no_disponible
    assert sin_activo.disponible is False and "activo total al cierre" in sin_activo.motivo_no_disponible


# ------------------------------------------------- D-6. Sin datos para conciliar
@pytest.mark.parametrize("anio", (2021, 2022, 2023))
def test_sin_datos_para_conciliar_no_es_sin_conciliar(s, anio):
    p = get_fiscal_period(s, anio)
    d = datos_ejercicio(s, p)
    conciliacion = conciliar_resultado(d.bs, d.inc)
    assert conciliacion.estado == SIN_DATOS
    r = compute_dupont(s, p)
    assert resumen(banderas_dupont(r)) == resumen(banderas_balance(d.bs, conciliacion)) == "DEFINITIVO"
    control = next(c for c in r.controles if c.nombre.startswith("Resultado del ejercicio"))
    assert control.sin_datos and control.resultado == "Sin datos para conciliar"


def test_una_diferencia_real_sigue_siendo_sin_conciliar(bd_sintetica):
    with session_scope() as s:
        r = compute_dupont(s, _capturar(s, 2021, {"1001": 1000, "2001": 400, "3001": 550, "3004": 50},
                                        {"4001": 1000, "5001": 900, "6001": 0, "8001": 0}))
    assert "SIN CONCILIAR" in resumen(banderas_dupont(r))
    assert next(c for c in r.controles if c.nombre.startswith("Resultado del ejercicio")).resultado == "Revisar"


# ------------------------------------------------- 9. Signos del vertical del Estado de Resultados
@pytest.mark.parametrize("j, anio", enumerate(ANIOS))
def test_vertical_resultados_coincide_con_la_tabla_7_1(s, j, anio):
    vi = compute_vertical_income(s, get_fiscal_period(s, anio).id)
    sub = {l.etiqueta: l for l in vi.subtotales}
    for etiqueta, grupos, porcentajes in TABLA_7_1:
        if etiqueta:
            calculado = sub[etiqueta].porcentaje
        else:
            calculado = sum((f.porcentaje for f in vi.filas if f.cuenta.grupo_analisis in grupos), Decimal("0.00"))
        assert calculado == Decimal(porcentajes[j]), (anio, etiqueta or grupos)


@pytest.mark.parametrize("anio", ANIOS)
def test_signo_solo_en_el_porcentaje_y_una_sola_vez(s, anio):
    vi = compute_vertical_income(s, get_fiscal_period(s, anio).id)
    base = vi.base_ingresos_netos
    for linea in vi.lineas:
        if linea.valor is None:
            continue
        magnitud = _q(linea.valor / base * 100)
        assert linea.porcentaje == (-magnitud if linea.efecto == "resta" else magnitud), linea.etiqueta
        assert str(linea.porcentaje) != "-0.00"
    for linea in vi.lineas:
        if linea.efecto == "resta" and linea.valor is not None:
            assert linea.valor >= 0  # el importe no se invierte
    assert {l.efecto for l in vi.lineas} <= {"", "resta", "suma", "signo"}
    # Comparativo e individual presentan el mismo signo y magnitud.
    d = datos_ejercicio(s, get_fiscal_period(s, anio))
    comparativo = {f.clave: f.porcentajes[anio] for f in vertical_comparativo([d], "ER")}
    sub = {l.etiqueta: l.porcentaje for l in vi.subtotales}
    assert _q(comparativo["s_costo_ventas"]) == sub["Costo de ventas"]
    assert _q(comparativo["s_impuesto_renta"]) == sub["Impuesto sobre la renta"]


def test_cero_no_se_presenta_como_menos_cero_y_gasto_negativo_queda_positivo(bd_sintetica):
    with session_scope() as s:
        vi = compute_vertical_income(s, _capturar(s, 2021, resultados={"4001": 1000, "5001": 0, "8001": -50}).id)
    por_codigo = {f.cuenta.codigo: f.porcentaje for f in vi.filas}
    assert str(por_codigo["5001"]) == "0.00"
    assert por_codigo["8001"] == Decimal("5.00")  # beneficio fiscal: resta de un negativo


@pytest.mark.parametrize("j, anio", enumerate(ANIOS))
def test_vertical_balance_no_cambia(s, j, anio):
    vb = compute_vertical_balance(s, get_fiscal_period(s, anio).id)
    sub = {l.etiqueta: l.porcentaje for l in vb.subtotales}
    for etiqueta, porcentajes in TABLA_7_2.items():
        assert sub[etiqueta] == Decimal(porcentajes[j]), (anio, etiqueta)
    assert sub["TOTAL PASIVO + PATRIMONIO"] == Decimal("100.00")


# ------------------------------------------------- 10. Pantalla, PDF y Excel
@pytest.fixture()
def pdf_sin_compresion(monkeypatch):
    monkeypatch.setattr(rl_config, "pageCompression", 0)


def _valores_excel(ws):
    return {ws.cell(f, 1).value: ws.cell(f, 2).value for f in range(1, ws.max_row + 1) if ws.cell(f, 1).value}


@pytest.mark.parametrize("anio", ANIOS)
def test_dupont_igual_en_tabla_excel_y_pdf(s, pdf_sin_compresion, anio):
    p = get_fiscal_period(s, anio)
    r = compute_dupont(s, p)
    company = get_company(s)
    excel = _valores_excel(load_workbook(io.BytesIO(export_dupont_excel(company, p, r))).active)
    pdf = export_dupont_pdf(company, p, r).decode("latin-1")
    assert "Enfoque total" in pdf and "Enfoque de la controladora" in pdf
    assert "Activo total promedio" not in pdf and "Patrimonio promedio" not in pdf and "APROXIMADO" not in pdf
    for filas, tabla in ((filas_enfoque_total(r), _tabla(filas_enfoque_total(r), "USD")),
                         (filas_enfoque_controladora(r), _tabla(filas_enfoque_controladora(r), "USD"))):
        pantalla = dict(zip(tabla["Componente"], tabla["Valor"]))
        for f in filas:
            texto = formatear_fila(f, "USD")
            assert pantalla[f.etiqueta] == texto
            assert texto in pdf, (anio, f.etiqueta, texto)
            sufijo = {"importe": "", "porcentaje": " (%)", "veces": " (veces)"}[f.tipo]
            assert abs(Decimal(str(excel[f"{f.etiqueta}{sufijo}"])) - f.valor) < Decimal("0.000001"), (anio, f.etiqueta)


@pytest.mark.parametrize("anio", ANIOS)
def test_vertical_resultados_igual_en_excel_y_pdf(s, pdf_sin_compresion, anio):
    p = get_fiscal_period(s, anio)
    vi = compute_vertical_income(s, p.id)
    company = get_company(s)
    ws = load_workbook(io.BytesIO(export_vertical_excel(company, p, "V", None, vi.base_ingresos_netos, "Ingresos Netos", vi.lineas))).active
    fila_base = next(c.row for c in ws["A"] if c.value == "Base (100%)")
    cabecera = next(c.row for c in ws["A"] if c.value == "Código")
    pdf = export_vertical_pdf(company, p, "V", vi.lineas, vi.base_ingresos_netos, "Ingresos Netos").decode("latin-1")
    for i, linea in enumerate(vi.lineas, start=cabecera + 1):
        if linea.valor is None:  # grupo sin cuentas ese ejercicio: "Sin datos", no un cero
            assert ws.cell(i, 4).value == "No disponible" and ws.cell(i, 6).value is None
            continue
        assert Decimal(str(ws.cell(i, 4).value)) == linea.porcentaje
        assert Decimal(str(ws.cell(i, 3).value)) == linea.valor  # importe sin invertir
        formula = ws.cell(i, 6).value
        assert formula.startswith("=-C" if linea.efecto == "resta" else "=C") and f"$C${fila_base}" in formula
        assert f"{linea.porcentaje:.2f}%" in pdf


def test_pantallas_reales_de_los_reportes(ruta_bd, tmp_path):
    copia = tmp_path / "financiera.db"
    copia.write_bytes(ruta_bd.read_bytes())
    proceso = subprocess.run([sys.executable, str(PROYECTO / "tests" / "humo_vertical_dupont.py"), str(copia)],
                             capture_output=True, text=True, encoding="utf-8", timeout=900)
    assert proceso.returncode == 0, proceso.stderr[-3000:]
    salida = json.loads(proceso.stdout.strip().splitlines()[-1])
    for j, anio in enumerate(ANIOS):
        pag = salida["anios"][str(anio)]
        assert not any(p["excepciones"] for p in pag.values()), anio
        # DuPont
        d = pag["dupont"]
        assert d["metricas"]["RSP / ROE DuPont"] == f"{DUPONT['rsp'][j]}%"
        assert d["metricas"]["ROE directo (comprobación)"] == f"{DUPONT['rsp'][j]}%"
        assert d["metricas"]["Multiplicador del capital (MAF)"] == f"{DUPONT['maf'][j]} veces"
        total = {f["Componente"]: f["Valor"] for f in d["tablas"][0]}
        ctrl = {f["Componente"]: f["Valor"] for f in d["tablas"][1]}
        assert total["RSP / ROE DuPont"] == f"{DUPONT['rsp'][j]}%" and total["Rotación de activos"] == f"{DUPONT['rotacion'][j]} veces"
        assert ctrl["RSP / ROE (controladora)"] == f"{CONTROLADORA['rsp'][j]}%" and ctrl["MAF (controladora)"] == f"{CONTROLADORA['maf'][j]} veces"
        assert not d["avisos"]
        textos = " ".join(d["textos"]).lower()
        assert "aproximad" not in textos and "promedio" not in textos.replace("saldos promedio", "")
        assert "enfoque de la controladora" in textos
        # Vertical
        filas = {f["Concepto"]: f["Participación %"] for f in pag["vertical_resultados"]["tablas"][0] if not f["Código"]}
        assert filas["COSTO DE VENTAS"] == f"{TABLA_7_1[1][2][j]}%" and filas["UTILIDAD NETA"] == f"{TABLA_7_1[14][2][j]}%"
        balance = {f["Concepto"]: f["Participación %"] for f in pag["vertical_balance"]["tablas"][0] if not f["Código"]}
        assert balance["ACTIVO CORRIENTE"] == f"{TABLA_7_2['Activo corriente'][j]}%"
    # 11. Dashboard: los dos ROE son el mismo
    tablero = salida["dashboard"]
    assert not tablero["excepciones"]
    assert tablero["metricas"]["ROE (DuPont) — definitivo"] == tablero["metricas"]["ROE (al cierre)"] == "5.15%"
    assert not salida["informe"]["excepciones"]
    assert not salida["saldos_iniciales"]["excepciones"]
    assert "registro de apertura" in " ".join(salida["saldos_iniciales"]["textos"])


# ------------------------------------------------- 11. Informe integral e Indicadores
def test_informe_integral_usa_los_mismos_valores(s):
    lista = datos_todos(s)
    total, ctrl = sec.dupont(lista)
    filas_total = {f[0]: f[1:6] for f in total.filas}
    filas_ctrl = {f[0]: f[1:6] for f in ctrl.filas}
    for j, anio in enumerate(ANIOS):
        r = compute_dupont(s, get_fiscal_period(s, anio))
        assert filas_total[ind.POR_CLAVE["roe_dupont"].nombre][j] == r.roe * 100
        assert filas_total[ind.POR_CLAVE["maf"].nombre][j] == r.multiplicador_capital
        assert filas_total[ind.POR_CLAVE["rotacion_activos"].nombre][j] == r.rotacion_activos
        assert filas_ctrl[ind.POR_CLAVE["roe_controladora"].nombre][j] == r.controladora.factores.rsp * 100
    assert not any("usa saldos promedio" in n for n in total.notas)
    hojas = hojas_informe(s, lista)
    secciones = [x for nombre, grupo in hojas if nombre == "DuPont" for x in grupo]
    assert secciones_a_pdf(get_company(s), "I", secciones).startswith(b"%PDF")
    ws = load_workbook(io.BytesIO(secciones_a_excel(get_company(s), "I", [("DuPont", secciones)])))["DuPont"]
    fila = next(f for f in ws.iter_rows(values_only=True) if f[0] == ind.POR_CLAVE["roe_dupont"].nombre)
    assert [_q(Decimal(str(v))) for v in fila[1:6]] == [Decimal(v) for v in DUPONT["rsp"]]


@pytest.mark.parametrize("anio", ANIOS)
def test_indicadores_y_dupont_son_la_misma_cifra(s, anio):
    p = get_fiscal_period(s, anio)
    r = compute_dupont(s, p)
    d = datos_ejercicio(s, p)
    assert abs(ind.calcular(d, "roe").valor - r.roe * 100) < Decimal("1E-20")
    assert abs(ind.calcular(d, "roa").valor - r.rsa * 100) < Decimal("1E-20")
    assert abs(ind.calcular(d, "margen_neto").valor - r.margen_neto * 100) < Decimal("1E-20")
    assert ind.calcular(d, "rotacion_activos").valor == r.rotacion_activos
    assert ind.calcular(d, "roa_dupont").valor == r.rsa * 100
    assert ind.calcular(d, "maf").valor == r.multiplicador_capital
    assert ind.calcular(d, "roe_dupont").valor == r.roe * 100


def test_la_pagina_de_indicadores_sigue_sin_incluir_dupont():
    fuente = (PROYECTO / "reports" / "indicadores_financieros.py").read_text(encoding="utf-8")
    assert "DuPont no se incluye" in fuente and "categoria != ind.DUPONT" in fuente


def test_validacion_del_trabajo_coincide_en_las_secciones_auditadas(s):
    comparaciones = comparar(datos_todos(s))
    # Referencias al dia con la version vigente del trabajo; 8.3 C es una equivalencia, sin cifra publicada propia.
    assert Counter(c.estado for c in comparaciones) == Counter(
        {"Coincide": 711, "Resultado derivado": 5, "Diferencia": 6, "No aplica": 15, "Coincidencia por redondeo": 4})
    secciones = [c for c in comparaciones if c.referencia.seccion in ("7.1", "7.2", "9.5", "9.6")]
    assert len(secciones) == 171 and all(c.estado == COINCIDE for c in secciones)


# ------------------------------------------------- 12. Indicadores de actividad
ACTIVIDAD_CIERRE = {
    # (clave, formula con saldos del mismo ejercicio)
    "rotacion_activos": lambda d: d.inc.ingresos_netos.subtotal / d.bs.total_activo,
    "rotacion_inventarios": lambda d: d.inc.costo_ventas.subtotal / d.rubro("INVENTARIOS"),
    "ppi": lambda d: d.rubro("INVENTARIOS") / d.inc.costo_ventas.subtotal * 365,
    "ppc": lambda d: d.rubro("CXC_COMERCIALES_PRESENTADA") / d.inc.ingresos_netos.subtotal * 365,
    "ppp": lambda d: d.rubro("CXP_COMERCIALES_PRESENTADA") / d.inc.costo_ventas.subtotal * 365,
}


@pytest.mark.parametrize("clave", ACTIVIDAD_CIERRE)
def test_indicadores_de_actividad_no_cambian_de_metodologia(s, clave):
    assert clave in ind.POR_CLAVE, clave
    assert ind.POR_CLAVE[clave].categoria == ind.ACTIVIDAD
    for d in datos_todos(s):
        assert abs(ind.calcular(d, clave).valor - ACTIVIDAD_CIERRE[clave](d)) < Decimal("1E-20"), (clave, d.anio)


def test_rotacion_de_actividad_no_delega_ni_depende_de_dupont():
    fuente = (PROYECTO / "calculations" / "indicadores.py").read_text(encoding="utf-8")
    inicio = fuente.index("def _rotacion_activos(d):")
    assert "d.inc.ingresos_netos.subtotal, d.bs.total_activo" in fuente[inicio:inicio + 160]


def test_ejercicios_cargados_son_los_cinco(s):
    assert [p.anio for p in list_fiscal_periods(s)] == list(ANIOS)
