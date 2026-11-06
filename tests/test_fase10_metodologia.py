"""Metodologia del documento ANF en cuentas por cobrar, ciclo operativo, CCE y pagos fijos.

Los valores esperados se leen del documento o se calculan con fracciones desde los
estados originales (tests/concordancia_documento.py), nunca con calculations/.
"""
import ast
import io
import json
import subprocess
import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest
from openpyxl import load_workbook
from reportlab import rl_config

from calculations import indicadores as ind
from calculations.comparacion_anf import COINCIDE, DERIVADO, DIFERENCIA, ESTADOS, NO_APLICA, REDONDEO, comparar, referencias_derivadas, resumen
from calculations.rubros import datos_ejercicio, datos_todos
from components.money import redondear
from components.secciones_ui import a_dataframe
from concordancia_documento import ANIOS, EJERCICIOS, independiente, limpiar_celda, lineas_documento, numero, redondear as redondear_ref, tabla
from database import connection
from database.connection import init_db, session_scope
from database.enums import TipoEstadoFinanciero as Tipo
from database.repositories import get_account_by_codigo, get_company, get_fiscal_period, get_or_create_fiscal_period, upsert_entry
from database.seed import seed_default_accounts
from reports import secciones as sec
from reports.exportar_secciones import secciones_a_excel, secciones_a_pdf
from reports.indicadores_financieros import GRUPOS, _secciones_de
from scripts.cargar_alutech import cargar
from test_fase8_vertical_dupont import _guardar_empresa

PROYECTO = Path(__file__).resolve().parent.parent
FUENTE = json.loads((PROYECTO / "fuentes/alutech/estados_financieros_2021_2025.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def ruta_bd(tmp_path_factory):
    ruta = tmp_path_factory.mktemp("fase10") / "financiera.db"
    cargar(db_path=ruta, respaldar=False)
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
def por_anio(s):
    return {d.anio: d for d in datos_todos(s)}


def _publicado_9_3(encabezado: str) -> dict[int, Decimal]:
    lineas = lineas_documento()
    inicio = next(n for n, l in enumerate(lineas) if l.startswith("#### **9.1"))
    return {int(f[0]): numero(f[4])[0] for f in tabla(lineas, encabezado, inicio)[1:]}


def _cuenta(anio: int, codigo: str) -> Fraction:
    fila = next(r for r in FUENTE["ejercicios"][str(anio)]["BALANCE"] if r[0] == codigo)
    return Fraction(fila[2].replace(",", ""))


# ------------------------------------------------------------- cuentas por cobrar
@pytest.mark.parametrize("anio, codigos_comercial, codigos_cartera", [
    (2021, ["CB1104"], ["CB1104", "CB1106"]), (2022, ["CB1104"], ["CB1104", "CB1106"]), (2023, ["CB1104"], ["CB1104", "CB1106"]),
    (2024, ["CN1103"], ["CN1103"]), (2025, ["CN1103"], ["CN1103"]),
])
def test_las_dos_bases_se_reconstruyen_desde_las_cuentas(por_anio, anio, codigos_comercial, codigos_cartera):
    d = por_anio[anio]
    assert Fraction(d.rubro("CXC_COMERCIALES_PRESENTADA")) == sum(_cuenta(anio, c) for c in codigos_comercial)
    assert Fraction(d.rubro("CXC_COMERCIALES_Y_OTRAS")) == sum(_cuenta(anio, c) for c in codigos_cartera)


def test_el_indicador_principal_sigue_la_formula_de_9_3_en_los_cinco_anios(por_anio):
    publicado = _publicado_9_3("| Año | Cuentas por cobrar comerciales | Ingresos")
    for anio, valor in publicado.items():
        assert redondear(ind.calcular(por_anio[anio], "ppc").valor, 2) == valor, anio
        e = EJERCICIOS[anio]
        rotacion = e.ing / e.cxc
        assert abs(Fraction(ind.calcular(por_anio[anio], "rotacion_cxc").valor) - rotacion) < Fraction(1, 10**9), anio


def test_2023_no_tiene_un_tratamiento_propio_en_ninguna_base(por_anio):
    # Valores de 2023 con cada base: los dos se calculan con la misma regla de los demas ejercicios.
    d = por_anio[2023]
    assert redondear(ind.calcular(d, "rotacion_cxc").valor, 2) == Decimal("11.60") and redondear(ind.calcular(d, "ppc").valor, 2) == Decimal("31.47")
    assert redondear(ind.calcular(d, "rotacion_cxc_total").valor, 2) == Decimal("4.98") and redondear(ind.calcular(d, "ppc_total").valor, 1) == Decimal("73.3")


@pytest.mark.parametrize("nombre", ["_rotacion_cxc", "_ppc", "_rotacion_cxc_total", "_ppc_total", "_ppp", "_ppi", "_ciclo_operativo", "_cce",
                                    "_cobertura_intereses", "_cobertura_pagos_fijos"])
def test_las_funciones_no_tienen_excepciones_por_anio_ni_cifras(nombre):
    arbol = ast.parse((PROYECTO / "calculations/indicadores.py").read_text(encoding="utf-8"))
    funcion = next(n for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef) and n.name == nombre)
    numeros = [n.value for n in ast.walk(funcion) if isinstance(n, ast.Constant) and isinstance(n.value, (int, float))]
    assert not numeros, (nombre, numeros)
    assert "anio" not in ast.unparse(funcion)


def test_seccion_de_las_dos_bases_en_pantalla(por_anio):
    filas = {f[0]: f for f in a_dataframe(sec.bases_cxc(list(por_anio.values()))).values.tolist()}
    comercial, cartera = filas["Línea comercial presentada (9.3): saldo al cierre"], filas["Comerciales y otras: saldo al cierre"]
    assert comercial[1:6] == ["53,081,088", "32,581,092", "41,272,525", "97,204,415", "70,169,882"]
    assert cartera[1:6] == ["117,984,175", "85,022,305", "96,097,483", "97,204,415", "70,169,882"]
    assert filas["Línea comercial presentada (9.3): período de cobro"][3] == "31.47"
    assert filas["Comerciales y otras: período de cobro"][3] == "73.28"


# ------------------------------------------------------------- periodo de cobro 2025
def test_ppc_2025_se_redondea_una_sola_vez(por_anio):
    exacto = Fraction(70169882, 439704567) * 365
    valor = ind.calcular(por_anio[2025], "ppc").valor
    assert abs(Fraction(valor) - exacto) < Fraction(1, 10**9)
    assert redondear(valor, 2) == Decimal("58.25") and redondear(valor, 1) == Decimal("58.2")
    assert redondear(redondear(valor, 2), 1) == Decimal("58.3")  # el 58.3 del documento solo sale de redondear dos veces
    assert ind.formatear(ind.DIAS_U, valor) == "58.25 días" and sec.formatear(valor, sec.DIAS) == "58.25"


def test_interpretacion_y_tabla_presentan_la_misma_cifra(por_anio):
    r = ind.calcular(por_anio[2025], "ppc")
    assert "58.25" in ind.interpretacion(r)


@pytest.mark.parametrize("valor, esperado", [("1.005", "1.01"), ("2.675", "2.68"), ("-1.005", "-1.01")])
def test_presentacion_redondea_mitad_hacia_arriba_en_todos_los_formatos(valor, esperado):
    d = Decimal(valor)
    assert sec.formatear(d, sec.DIAS) == esperado and sec.formatear(d, sec.VECES) == esperado
    assert ind.formatear(ind.VECES, d) == f"{esperado} veces"


# ------------------------------------------------------------- ciclo operativo y CCE
def test_ciclo_operativo_reproduce_los_cinco_valores_de_9_3(por_anio):
    publicado = _publicado_9_3("| Año | EPI (días) | PPC (días)")
    assert list(publicado.values()) == [Decimal("184.51"), Decimal("149.28"), Decimal("169.72"), Decimal("186.98"), Decimal("135.14")]
    for anio, valor in publicado.items():
        assert ind.calcular(por_anio[anio], "ciclo_operativo").valor == valor, anio


def test_ciclo_operativo_suma_operandos_redondeados_no_el_valor_exacto(por_anio):
    for anio in (2022, 2023):
        d = por_anio[anio]
        exacto = ind.calcular(d, "ppi").valor + ind.calcular(d, "ppc").valor
        assert redondear(exacto, 2) != ind.calcular(d, "ciclo_operativo").valor  # el documento no redondea la suma


def test_cce_reproduce_los_cinco_valores_de_9_3(por_anio):
    publicado = _publicado_9_3("| Año | CO (días) | PPP (días)")
    assert list(publicado.values()) == [Decimal("28.86"), Decimal("63.33"), Decimal("-21.40"), Decimal("-30.72"), Decimal("-55.52")]
    for anio, valor in publicado.items():
        d = por_anio[anio]
        assert ind.calcular(d, "cce").valor == valor, anio
        assert ind.calcular(d, "cce").valor == ind.calcular(d, "ciclo_operativo").valor - redondear(ind.calcular(d, "ppp").valor, 2), anio


def test_el_signo_del_cce_2023_es_el_de_cada_base_y_no_se_fuerza():
    e = EJERCICIOS[2023]
    inv, cv, ing, comerciales, otras = e.inv, e.cv, e.ing, e.cxc, e.cxct - e.cxc
    otras_pagar = _cuenta(2023, "CB2110")
    ppi = 365 * inv / cv
    base_9_3 = ppi + 365 * comerciales / ing - 365 * e.cxp / cv
    cartera_8_2 = ppi + 365 * (comerciales + otras) / ing - 365 * e.cxp / cv
    ambas = ppi + 365 * (comerciales + otras) / ing - 365 * (e.cxp + otras_pagar) / cv
    a2 = lambda f: redondear_ref(Decimal(f.numerator) / Decimal(f.denominator), 2)  # noqa: E731
    assert (a2(base_9_3), a2(cartera_8_2), a2(ambas)) == (Decimal("-21.40"), Decimal("20.41"), Decimal("8.56"))


def test_la_regla_depende_de_los_importes_y_no_del_ejercicio(tmp_path):
    """Mismos importes en dos ejercicios distintos: mismo resultado. Calculo a mano: inventario 1000 / costo 2910 × 365 = 125.4296
    (125.43); CxC 500 / ingresos 7000 × 365 = 26.0714 (26.07); CO = 151.50, cuando la suma exacta redondea a 151.50 tambien;
    CxP 700 / 2910 × 365 = 87.8007 (87.80); CCE = 63.70."""
    init_db(db_path=tmp_path / "s.db")
    with session_scope() as sesion:
        seed_default_accounts(sesion)
        _guardar_empresa(sesion)
        for anio in (2022, 2024):
            p, _ = get_or_create_fiscal_period(sesion, anio)
            for codigo, valor, tipo in (("1003", 1000, Tipo.BALANCE), ("1002", 500, Tipo.BALANCE), ("2001", 700, Tipo.BALANCE),
                                        ("4001", 7000, Tipo.RESULTADOS), ("5001", 2910, Tipo.RESULTADOS)):
                upsert_entry(sesion, fiscal_period_id=p.id, account_id=get_account_by_codigo(sesion, codigo).id, valor=Decimal(valor), tipo=tipo)
    with session_scope() as sesion:
        for cuenta in ("1003", "1002", "2001", "4001", "5001"):
            get_account_by_codigo(sesion, cuenta).grupo_analisis = {"1003": "INVENTARIOS", "1002": "CXC_COMERCIALES", "2001": "CXP_COMERCIALES",
                                                                    "4001": "INGRESOS_ORDINARIOS", "5001": "COSTO_VENTAS"}[cuenta]
    with session_scope() as sesion:
        a, b = (datos_ejercicio(sesion, get_fiscal_period(sesion, x)) for x in (2022, 2024))
        for d in (a, b):
            assert ind.calcular(d, "ciclo_operativo").valor == Decimal("151.50")
            assert ind.calcular(d, "cce").valor == Decimal("63.70")
    connection.dispose_engine()


# ------------------------------------------------------------- cobertura de pagos fijos
def test_el_texto_de_8_3_c_establece_la_equivalencia_y_no_publica_cifras():
    parrafo = next(l for l in lineas_documento() if l.startswith("**C. Índice de cobertura de pagos fijos**"))
    assert "iguala matemáticamente a la razón de cargos de interés fijo" in parrafo
    assert "4.76" not in parrafo and "1.46" not in parrafo


@pytest.mark.parametrize("anio", ANIOS)
def test_pagos_fijos_se_calcula_con_la_funcion_de_8_3_b(por_anio, anio):
    d = por_anio[anio]
    esperado = independiente("cob", anio)
    assert abs(ind.calcular(d, "cobertura_pagos_fijos").valor - esperado) < Decimal("0.000001")
    assert ind.calcular(d, "cobertura_pagos_fijos").valor == ind.calcular(d, "cobertura_intereses").valor


def test_pagos_fijos_no_usa_valores_copiados():
    arbol = ast.parse((PROYECTO / "calculations/indicadores.py").read_text(encoding="utf-8"))
    funcion = next(n for n in ast.walk(arbol) if isinstance(n, ast.FunctionDef) and n.name == "_cobertura_pagos_fijos")
    assert "_cobertura_intereses" in ast.unparse(funcion)


def test_pagos_fijos_se_clasifica_como_derivado(por_anio):
    assert "E-CPF" in referencias_derivadas()
    comparaciones = comparar(list(por_anio.values()))
    derivados = [c for c in comparaciones if c.referencia.id == "E-CPF"]
    assert len(derivados) == 5 and all(c.estado == DERIVADO and c.causa for c in derivados)
    assert all(c.referencia.id == "E-CPF" for c in comparaciones if c.estado == DERIVADO)


# ------------------------------------------------------------- validacion
def test_validacion_refleja_la_metodologia(por_anio):
    comparaciones = comparar(list(por_anio.values()))
    assert DERIVADO in ESTADOS
    assert resumen(comparaciones) == {COINCIDE: 711, REDONDEO: 4, DERIVADO: 5, DIFERENCIA: 6, "No verificable": 0, NO_APLICA: 15}
    redondeo = {(c.referencia.id, c.anio) for c in comparaciones if c.estado == REDONDEO}
    assert redondeo == {("B-PPC", 2025), ("C-CO82", 2025), ("E-PCP", 2021), ("W-WACC", 2023)}
    assert all(c.causa for c in comparaciones if c.estado in (REDONDEO, DIFERENCIA, DERIVADO))


# ------------------------------------------------------------- pantalla, PDF y Excel
@pytest.fixture()
def pdf_sin_compresion(monkeypatch):
    monkeypatch.setattr(rl_config, "pageCompression", 0)


def test_actividad_y_deuda_iguales_en_pantalla_pdf_y_excel(s, por_anio, pdf_sin_compresion):
    lista = list(por_anio.values())
    company = get_company(s)
    for grupo in GRUPOS:
        if grupo.titulo not in ("Actividad", "Endeudamiento"):
            continue
        secciones = _secciones_de(grupo, lista)
        texto_pdf = secciones_a_pdf(company, "Ratios", secciones).decode("latin-1")
        hoja = load_workbook(io.BytesIO(secciones_a_excel(company, "Ratios", [("R", secciones)])))["R"]
        celdas = [c.value for fila in hoja.iter_rows() for c in fila if isinstance(c.value, (int, float))]
        for seccion in secciones:
            pantalla = a_dataframe(seccion).values.tolist()
            for fila, vista in zip(seccion.filas, pantalla):
                for i, valor in enumerate(fila):
                    if isinstance(valor, Decimal):
                        assert vista[i] == sec.formatear(valor, sec.tipo_celda(seccion, fila, i))
                        assert vista[i] in texto_pdf, (seccion.titulo, fila[0], i)
                        assert any(abs(float(valor) - c) < 1e-6 for c in celdas), (seccion.titulo, fila[0], i)


@pytest.fixture(scope="module")
def pantallas(ruta_bd, tmp_path_factory):
    copia = tmp_path_factory.mktemp("humo10") / "financiera.db"
    copia.write_bytes(ruta_bd.read_bytes())
    proceso = subprocess.run([sys.executable, str(PROYECTO / "tests" / "humo_horizontal.py"), str(copia)],
                             capture_output=True, text=True, encoding="utf-8", timeout=900)
    assert proceso.returncode == 0, proceso.stderr[-3000:]
    return json.loads(proceso.stdout.strip().splitlines()[-1])


def test_pantalla_real_de_indicadores_muestra_la_metodologia(pantallas):
    p = pantallas["indicadores"]
    assert not p["excepciones"]
    filas = [f for t in p["tablas"] for f in t if "Indicador" in f]
    co = next(f for f in filas if f["Indicador"] == "Ciclo operativo")
    cce = next(f for f in filas if f["Indicador"].startswith("Ciclo de conversión"))
    fijos = next(f for f in filas if f["Indicador"] == "Índice de cobertura de pagos fijos")
    assert [co[str(a)] for a in ANIOS] == ["184.51", "149.28", "169.72", "186.98", "135.14"]
    assert [cce[str(a)] for a in ANIOS] == ["28.86", "63.33", "-21.40", "-30.72", "-55.52"]
    assert [fijos[str(a)] for a in ANIOS] == ["4.76", "1.82", "2.03", "1.25", "1.46"]
    bases = [f for t in p["tablas"] for f in t if "Concepto" in f and f["Concepto"].startswith("Comerciales y otras: saldo")]
    assert bases and bases[0]["2023"] == "96,097,483"
    assert any("9.3" in texto and "2 decimales" in texto for texto in p["textos"] + p.get("avisos", []))
