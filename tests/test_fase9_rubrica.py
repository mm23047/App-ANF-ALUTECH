"""Concordancia de la aplicacion con el documento ANF y cumplimiento de la rubrica.

Los valores esperados salen de tests/concordancia_documento.py: se leen del propio
documento y se recalculan de los estados originales, sin usar calculations/.
"""
import io
import json
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest
from openpyxl import load_workbook
from reportlab import rl_config
from reportlab.pdfbase.pdfmetrics import stringWidth

from calculations import indicadores as ind
from calculations.balance_sheet import compute_balance_sheet
from calculations.comparacion_anf import DIFERENCIA, Contexto, comparar, resumen
from calculations.comparativo import APARECE, AUMENTO, DESAPARECE, DISMINUCION, SIN_VARIACION, dos_ejercicios, horizontal_de_estado, tendencia, variacion
from calculations.rubros import datos_ejercicio, datos_todos
from calculations.validation import lineas_reportables
from calculations.vertical_analysis import compute_vertical_balance
from components.secciones_ui import a_dataframe
from concordancia_documento import ANIOS, independiente, limpiar_celda, lineas_documento, numero, redondear, tabla, valores_publicados
from database import connection
from database.connection import init_db, session_scope
from database.enums import TipoEstadoFinanciero as Tipo
from database.repositories import get_account_by_codigo, get_company, get_fiscal_period, get_or_create_fiscal_period, list_entries, upsert_entry
from database.seed import seed_default_accounts
from reports import secciones as sec
from reports.excel_export import export_balance_excel
from reports.exportar_secciones import _anchos_columnas, secciones_a_excel, secciones_a_pdf
from reports.indicadores_financieros import GRUPOS, hojas_exportacion
from reports.pdf_export import export_balance_pdf
from scripts.cargar_alutech import cargar
from test_fase8_vertical_dupont import _guardar_empresa

PROYECTO = Path(__file__).resolve().parent.parent
PUBLICADOS = valores_publicados()

# Unicas diferencias admitidas, todas documentales (informe final, seccion 8). Se comprueba
# el conjunto exacto: una diferencia nueva, o que una de estas desaparezca, hace fallar la prueba.
DISCREPANCIAS_DOCUMENTADAS = {
    ("8.2 B", "CxC", 2023),            # 8.2 B mezcla comerciales + otras solo desde 2023; 9.3 usa comerciales
    ("8.2 B", "Rotación CxC", 2023),
    ("8.2 B", "PPC", 2023),
    ("8.2 B", "PPC", 2025),            # 58.248 publicado como 58.3 (doble redondeo)
    ("8.2 C", "Ciclo operativo", 2025),  # hereda el 58.3 de 8.2 B (76.9 + 58.3); 9.3 publica 135.14
}


@pytest.fixture(scope="module")
def ruta_bd(tmp_path_factory):
    ruta = tmp_path_factory.mktemp("fase9") / "financiera.db"
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
def lista(s):
    return datos_todos(s)


@pytest.fixture()
def pdf_sin_compresion(monkeypatch):
    monkeypatch.setattr(rl_config, "pageCompression", 0)


# ------------------------------------------------------- matriz de concordancia
def test_la_matriz_abarca_todas_las_tablas_y_los_cinco_ejercicios():
    assert len(PUBLICADOS) >= 800
    tablas = {v.tabla for v in PUBLICADOS}
    assert {"Tabla 3", "Tabla 4", "Tabla 5", "Tabla 6", "Tabla 7", "Vertical ER", "Vertical BG", "Liquidez", "Inventarios", "CxC", "Activos",
            "Endeudamiento", "Cobertura", "Deuda-capital", "Rentabilidad", "Síntesis", "DuPont RSA", "DuPont RSP", "DuPont controladora"} <= tablas
    for nombre in ("Vertical ER", "Vertical BG", "Liquidez", "DuPont RSP", "DuPont controladora"):
        assert {v.anio for v in PUBLICADOS if v.tabla == nombre} == set(ANIOS), nombre


def test_la_aplicacion_iguala_el_recalculo_independiente_sin_redondear(lista):
    contexto = Contexto(lista)
    for v in PUBLICADOS:
        app = contexto.valor(v.clave_app, v.anio)
        assert app is not None, v
        assert abs(app - independiente(v.metrica, v.anio, v.variacion)) < Decimal("0.000001"), v


def test_la_aplicacion_reproduce_el_documento_salvo_las_discrepancias_documentadas(lista):
    contexto = Contexto(lista)
    diferencias = {v.id for v in PUBLICADOS if redondear(contexto.valor(v.clave_app, v.anio), v.decimales) != v.publicado}
    assert diferencias == DISCREPANCIAS_DOCUMENTADAS


def test_las_discrepancias_no_vienen_de_los_datos_sino_del_documento():
    # El recalculo independiente tampoco obtiene el valor publicado: la cifra no se sustenta con la formula.
    for v in PUBLICADOS:
        if v.id in DISCREPANCIAS_DOCUMENTADAS:
            assert redondear(independiente(v.metrica, v.anio, v.variacion), v.decimales) != v.publicado, v


def test_la_base_de_8_2_b_de_2023_esta_disponible_como_variante_homogenea(lista):
    d = next(x for x in lista if x.anio == 2023)
    assert redondear(ind.calcular(d, "rotacion_cxc_total").valor, 2) == Decimal("4.98")
    assert redondear(ind.calcular(d, "ppc_total").valor, 1) == Decimal("73.3")
    assert d.rubro("CXC_COMERCIALES_Y_OTRAS") == Decimal("96097483")


def test_validacion_de_la_aplicacion_usa_las_referencias_vigentes(lista):
    comparaciones = comparar(lista)
    assert resumen(comparaciones)[DIFERENCIA] == 6
    assert {c.referencia.id for c in comparaciones if c.estado == DIFERENCIA} == {"B-CXC", "B-RCC", "B-PPC", "FU25-CXCR_LP", "FU25-TOTAL", "FU25-CXCR-NETO"}
    assert all(c.causa for c in comparaciones if c.estado == DIFERENCIA)


# ------------------------------------------------------- presentacion en pantalla
def _sin_marcas(celda: str) -> str:
    return limpiar_celda(celda).replace("$", "").replace("x", "") if numero(celda) else limpiar_celda(celda)


def _publicada(doc: str, tabla_app: list[str]) -> None:
    assert _sin_marcas(doc) == tabla_app, (doc, tabla_app)


def test_tablas_3_y_4_se_presentan_como_en_el_documento(lista):
    lineas = lineas_documento()
    tablas = sec.horizontal_balance_tablas(lista)
    assert [t.titulo.split(".")[0] for t in tablas] == ["Tabla 3", "Tabla 4"]
    for seccion, marca in zip(tablas, ("Tabla 3\\.", "Tabla 4\\.")):
        filas_doc = tabla(lineas, marca)[1:]
        pantalla = a_dataframe(seccion).values.tolist()
        assert len(filas_doc) == len(pantalla)
        for doc, app in zip(filas_doc, pantalla):
            assert [_sin_marcas(c) for c in doc[1:]] == app[1:], doc[0]


def test_tabla_5_se_presenta_como_en_el_documento(lista):
    filas_doc = tabla(lineas_documento(), "Tabla 5\\.")[1:]
    pantalla = a_dataframe(sec.horizontal_resultados_tabla(lista)).values.tolist()
    for doc, app in zip(filas_doc, pantalla):
        assert [_sin_marcas(c) for c in doc[1:6]] == app[1:6], doc[0]  # saldos
        assert [_sin_marcas(c) for c in doc[6:10]] == app[10:14], doc[0]  # variaciones relativas


def test_tablas_6_y_7_se_presentan_como_en_el_documento(lista):
    lineas = lineas_documento()
    for doc, app in zip(tabla(lineas, "Tabla 6\\.")[1:], a_dataframe(sec.capital_trabajo(lista)).values.tolist()):
        assert [_sin_marcas(c) for c in doc[1:8]] == app[1:8], doc[0]
    filas_7 = tabla(lineas, "Tabla 7\\.")[1:]
    pantalla_7 = a_dataframe(sec.capital_trabajo_interanual(lista)).values.tolist()
    assert len(filas_7) == len(pantalla_7) == 4
    for doc, app in zip(filas_7, pantalla_7):
        assert [_sin_marcas(c) for c in doc[1:]] == app[1:], doc[0]


@pytest.mark.parametrize("estado, marca", [("ER", "Partida (% de ingresos)"), ("BG", "Partida (% de activos totales)")])
def test_tablas_verticales_se_presentan_como_en_el_documento(lista, estado, marca):
    filas_doc = tabla(lineas_documento(), marca)[1:]
    pantalla = a_dataframe(sec.vertical(lista, estado)).values.tolist()
    assert len(filas_doc) == len(pantalla)
    for doc, app in zip(filas_doc, pantalla):
        assert doc[0] == app[0]  # misma denominacion y mismo orden
        assert [_sin_marcas(c) for c in doc[1:6]] == app[1:6], doc[0]


@pytest.mark.parametrize("anio", ANIOS)
def test_bases_financieras_de_los_ratios(lista, anio):
    d = next(x for x in lista if x.anio == anio)
    for grupo in GRUPOS:
        seccion = next(s for s in hojas_exportacion(lista) if s[0] == grupo.categoria)[1][0]
        assert seccion.titulo.startswith("Base financiera") and len(seccion.filas) == len(grupo.bases)
    assert grupo.bases and d.tiene_datos


# ------------------------------------------------------- horizontal: casos limite
@pytest.mark.parametrize("actual, anterior, esperado", [
    (Decimal(10), Decimal(5), AUMENTO), (Decimal(5), Decimal(10), DISMINUCION), (Decimal(5), Decimal(5), SIN_VARIACION),
    (Decimal(5), None, APARECE), (None, Decimal(5), DESAPARECE), (None, None, ""),
])
def test_sentido_del_cambio(actual, anterior, esperado):
    assert tendencia(actual, anterior) == esperado


def test_no_se_inventa_el_porcentaje_sin_base_valida():
    assert variacion(Decimal(10), Decimal(0))[:2] == (Decimal(10), None)
    assert variacion(Decimal(10), Decimal(-5))[:2] == (Decimal(15), None)
    assert variacion(Decimal(10), None)[:2] == (None, None)
    assert variacion(Decimal(-50), Decimal(100))[:2] == (Decimal(-150), Decimal(-150))


def test_cuentas_que_aparecen_y_desaparecen_entre_2023_y_2024(lista):
    filas = dos_ejercicios(horizontal_de_estado(lista, "BG", "cuentas"), 2024, 2023)
    por_clave = {f.clave: f for f in filas}
    assert por_clave["CB1101"].tendencia == DESAPARECE and por_clave["CB1101"].var_pct is None and por_clave["CB1101"].var_abs is None
    aparece = next(f for f in filas if f.tendencia == APARECE)
    assert aparece.anterior is None and aparece.var_pct is None and "sin base" in aparece.nota
    assert por_clave["total_activo"].actual == Decimal("827176374") and por_clave["total_activo"].tendencia == AUMENTO


def test_el_balance_por_cuentas_suma_sus_subtotales(lista):
    filas = horizontal_de_estado(lista, "BG", "cuentas")
    corrientes = [f for f in filas if f.tipo == "cuenta" and f.clave in {c.cuenta.codigo for c in lista[-1].bs.activo_corriente.lineas}]
    total = sum(f.valores[2025] for f in corrientes if f.valores[2025] is not None)
    assert total == next(f for f in filas if f.clave == "activo_corriente").valores[2025]


def test_otros_no_operativos_conserva_el_signo_al_pasar_de_ingreso_a_gasto(lista):
    fila = next(f for f in horizontal_de_estado(lista, "ER", "grupos") if f.clave == "grupo:OTROS_NO_OPERATIVOS")
    assert fila.valores[2025] == Decimal("-811571") and fila.valores[2024] > 0
    comparada = next(f for f in dos_ejercicios(horizontal_de_estado(lista, "ER", "grupos"), 2025, 2024) if f.clave == fila.clave)
    assert comparada.tendencia == DISMINUCION and "signo" in comparada.nota


def test_reporte_de_dos_ejercicios_trae_saldos_variaciones_y_sentido(lista):
    seccion = sec.horizontal_dos_ejercicios(lista, 2025, 2024, "ER", "rubros")
    assert [c.nombre for c in seccion.columnas] == ["Partida", "Saldo actual (2025)", "Saldo anterior (2024)", "Variación absoluta",
                                                    "Variación relativa", "Sentido", "Observación"]
    fila = a_dataframe(seccion).set_index("Partida").loc["Costo de ventas"]
    assert fila["Saldo actual (2025)"] == "331,430,173" and fila["Saldo anterior (2024)"] == "377,459,424"
    assert fila["Variación absoluta"] == "-46,029,251" and fila["Variación relativa"] == "-12.19%" and fila["Sentido"] == DISMINUCION


# ------------------------------------------------------- indicadores
@pytest.mark.parametrize("anio", ANIOS)
def test_cobertura_de_pagos_fijos_iguala_la_de_intereses_como_dice_8_3_c(lista, anio):
    d = next(x for x in lista if x.anio == anio)
    resultado = ind.calcular(d, "cobertura_pagos_fijos")
    assert resultado.valor == ind.calcular(d, "cobertura_intereses").valor
    assert "8.3 C" in resultado.nota


def test_los_cuatro_apartados_de_ratios_reunen_los_indicadores_del_documento():
    claves = {g.titulo: [f.clave for f in g.filas] for g in GRUPOS}
    assert {"ctn", "razon_corriente", "prueba_acida"} <= set(claves["Liquidez"])
    assert {"rotacion_inventarios", "ppi", "rotacion_cxc", "ppc", "ppp", "rotacion_activos", "ciclo_operativo", "cce"} <= set(claves["Actividad"])
    assert {"endeudamiento", "deuda_capital", "cobertura_intereses", "cobertura_pagos_fijos"} <= set(claves["Endeudamiento"])
    assert {"margen_bruto", "margen_operativo", "margen_neto", "roa", "roe", "eps"} <= set(claves["Rentabilidad"])


# ------------------------------------------------------- PDF y Excel
def _secciones_rubrica(lista):
    return [*sec.horizontal_balance_tablas(lista), sec.horizontal_resultados_tabla(lista), sec.capital_trabajo(lista),
            sec.capital_trabajo_interanual(lista), sec.vertical(lista, "ER"), sec.vertical(lista, "BG"), *sec.dupont(lista),
            sec.horizontal_dos_ejercicios(lista, 2025, 2024, "BG", "cuentas"),
            *[x for _, hoja in hojas_exportacion(lista) for x in hoja]]


def test_ninguna_cifra_del_pdf_se_parte(lista):
    ancho = 25 * 28.35
    for seccion in _secciones_rubrica(lista):
        for tamano in (7.5, 7, 6.5, 6, 5.5, 5):
            anchos, caben = _anchos_columnas(seccion, ancho, tamano)
            if caben:
                break
        assert caben, seccion.titulo
        for i, columna in enumerate(seccion.columnas):
            if columna.tipo == sec.TEXTO:
                continue
            for fila in seccion.filas:
                texto = sec.formatear(fila[i], sec.tipo_celda(seccion, fila, i))
                assert stringWidth(texto, "Helvetica-Bold", tamano) + 6 <= anchos[i], (seccion.titulo, columna.nombre, texto)


def test_pdf_y_excel_contienen_las_cifras_de_pantalla(s, lista, pdf_sin_compresion):
    company = get_company(s)
    secciones = [*sec.horizontal_balance_tablas(lista), sec.horizontal_resultados_tabla(lista)]
    pdf = secciones_a_pdf(company, "Análisis horizontal 2021–2025", secciones)
    assert pdf.startswith(b"%PDF")
    texto = pdf.decode("latin-1")
    libro = load_workbook(io.BytesIO(secciones_a_excel(company, "Análisis horizontal 2021–2025", [("Horizontal", secciones)])))
    hoja = libro["Horizontal"]
    celdas = {c.value for fila in hoja.iter_rows() for c in fila if isinstance(c.value, (int, float))}
    assert hoja["A1"].value == company.nombre_legal and hoja["A2"].value == "Análisis horizontal 2021–2025"
    for seccion in secciones:
        for fila in seccion.filas:
            for i, valor in enumerate(fila):
                if isinstance(valor, Decimal):
                    assert sec.formatear(valor, sec.tipo_celda(seccion, fila, i)) in texto, (seccion.titulo, fila[0], i)
                    assert any(abs(float(valor) - c) < 1e-6 for c in celdas), (seccion.titulo, fila[0], i)


def test_excel_tiene_columnas_suficientes_para_no_mostrar_almohadillas(s, lista):
    libro = load_workbook(io.BytesIO(secciones_a_excel(get_company(s), "T", [("H", sec.horizontal_balance_tablas(lista))])))
    hoja = libro["H"]
    for fila in hoja.iter_rows():
        for celda in fila:
            if isinstance(celda.value, float) or isinstance(celda.value, int):
                ancho = hoja.column_dimensions[celda.column_letter].width
                assert ancho >= len(f"{celda.value:+,.0f}"), celda.coordinate


def test_formatos_de_excel_iguales_a_la_pantalla(s, lista):
    libro = load_workbook(io.BytesIO(secciones_a_excel(get_company(s), "T", [("H", [sec.horizontal_resultados_tabla(lista)])])))
    formatos = {c.number_format for fila in libro["H"].iter_rows() for c in fila if isinstance(c.value, (int, float))}
    assert formatos == {"#,##0", "+#,##0;-#,##0;0", '+0.00"%";-0.00"%";0.00"%"'}


@pytest.mark.parametrize("nombre, secciones", [
    ("liquidez", 0), ("actividad", 1), ("endeudamiento", 2), ("rentabilidad", 3)])
def test_cada_apartado_de_ratios_genera_su_reporte(s, lista, nombre, secciones):
    from reports.indicadores_financieros import _secciones_de

    grupo = GRUPOS[secciones]
    contenido = _secciones_de(grupo, lista)
    assert secciones_a_pdf(get_company(s), f"Ratios de {nombre}", contenido).startswith(b"%PDF")
    hoja = load_workbook(io.BytesIO(secciones_a_excel(get_company(s), f"Ratios de {nombre}", [(grupo.titulo, contenido)])))[grupo.titulo]
    textos = {c.value for fila in hoja.iter_rows() for c in fila if isinstance(c.value, str)}
    assert {ind.POR_CLAVE[f.clave].nombre for f in grupo.filas if ind.POR_CLAVE[f.clave].categoria == grupo.categoria} <= textos


# ------------------------------------------------------- ceros del catalogo estandar
@pytest.fixture()
def con_ceros(tmp_path):
    """BD con el catalogo estandar y sus cuentas en cero en 2021, como la BD real."""
    ruta = tmp_path / "ceros.db"
    init_db(db_path=ruta)
    with session_scope() as sesion:
        seed_default_accounts(sesion)
    connection.dispose_engine()
    cargar(db_path=ruta, respaldar=False)
    init_db(db_path=ruta)
    with session_scope() as sesion:
        _guardar_empresa(sesion)
        periodo = get_fiscal_period(sesion, 2021)
        cuenta = get_account_by_codigo(sesion, "1001")
        upsert_entry(sesion, fiscal_period_id=periodo.id, account_id=cuenta.id, valor=Decimal("0"), tipo=Tipo.BALANCE)
    with session_scope() as sesion:
        yield sesion
    connection.dispose_engine()


def test_ceros_sin_mapear_no_aparecen_en_los_reportes_ni_alteran_totales(con_ceros, pdf_sin_compresion):
    s = con_ceros
    p = get_fiscal_period(s, 2021)
    bs = compute_balance_sheet(s, p.id)
    assert "1001" in {l.cuenta.codigo for l in bs.activo_corriente.lineas}  # sigue en los calculos y en la BD
    assert "1001" in {c.codigo for c, _ in list_entries(s, p.id, Tipo.BALANCE)}
    assert "1001" not in {l.cuenta.codigo for l in lineas_reportables(bs.activo_corriente)}
    assert bs.total_activo == Decimal("553955185") and bs.cuadra
    assert "1001" not in {l.codigo for l in compute_vertical_balance(s, p.id).lineas}
    company = get_company(s)
    pdf = export_balance_pdf(company, p, bs).decode("latin-1")
    assert "Efectivo y equivalentes" not in pdf and "553,955,185.00" in pdf and "No se muestran 1" in pdf
    hoja = load_workbook(io.BytesIO(export_balance_excel(company, p, bs))).active
    valores = [c.value for fila in hoja.iter_rows() for c in fila]
    assert "1001" not in valores and any(isinstance(v, str) and v.startswith("No se muestran 1") for v in valores)


def test_un_cero_de_un_catalogo_sin_mapear_si_se_presenta(tmp_path):
    init_db(db_path=tmp_path / "s.db")
    with session_scope() as sesion:
        seed_default_accounts(sesion)
        _guardar_empresa(sesion)
        p, _ = get_or_create_fiscal_period(sesion, 2021)
        for codigo, valor in (("1001", "100"), ("1002", "0"), ("2001", "40"), ("3001", "60")):
            upsert_entry(sesion, fiscal_period_id=p.id, account_id=get_account_by_codigo(sesion, codigo).id, valor=Decimal(valor), tipo=Tipo.BALANCE)
    with session_scope() as sesion:
        bs = compute_balance_sheet(sesion, get_fiscal_period(sesion, 2021).id)
        assert "1002" in {l.cuenta.codigo for l in lineas_reportables(bs.activo_corriente)}
    connection.dispose_engine()


# ------------------------------------------------------- modificacion de datos
def test_modificar_un_ejercicio_no_altera_los_demas(tmp_path, ruta_bd):
    ruta = tmp_path / "edicion.db"
    ruta.write_bytes(ruta_bd.read_bytes())
    connection.dispose_engine()
    init_db(db_path=ruta)

    def foto():
        with session_scope() as sesion:
            return {a: {c.codigo: v for c, v in list_entries(sesion, get_fiscal_period(sesion, a).id, Tipo.BALANCE)} for a in ANIOS}

    antes = foto()
    with session_scope() as sesion:
        cuenta = get_account_by_codigo(sesion, "CN1101")
        upsert_entry(sesion, fiscal_period_id=get_fiscal_period(sesion, 2025).id, account_id=cuenta.id, valor=antes[2025]["CN1101"] + 1, tipo=Tipo.BALANCE)
    despues = foto()
    assert despues[2025]["CN1101"] == antes[2025]["CN1101"] + 1
    assert all(despues[a] == antes[a] for a in (2021, 2022, 2023, 2024))
    assert {k: v for k, v in despues[2025].items() if k != "CN1101"} == {k: v for k, v in antes[2025].items() if k != "CN1101"}
    with session_scope() as sesion:
        assert not datos_ejercicio(sesion, get_fiscal_period(sesion, 2025)).bs.cuadra  # el descuadre se ve, no se oculta
    connection.dispose_engine()


# ------------------------------------------------------- pantallas reales
@pytest.fixture(scope="module")
def pantallas(ruta_bd, tmp_path_factory):
    copia = tmp_path_factory.mktemp("humo9") / "financiera.db"
    copia.write_bytes(ruta_bd.read_bytes())
    proceso = subprocess.run([sys.executable, str(PROYECTO / "tests" / "humo_horizontal.py"), str(copia)],
                             capture_output=True, text=True, encoding="utf-8", timeout=900)
    assert proceso.returncode == 0, proceso.stderr[-3000:]
    return json.loads(proceso.stdout.strip().splitlines()[-1])


def test_ninguna_pantalla_tiene_excepciones(pantallas):
    for nombre, pagina in pantallas.items():
        assert not pagina["excepciones"], nombre


def test_pantalla_horizontal_del_balance(pantallas):
    p = pantallas["balance"]
    assert p["encabezados"] == ["Reporte — Análisis Horizontal del Balance General"]
    assert p["pestanas"] == ["Tablas 3 y 4 del trabajo", "Capital de trabajo (Tablas 6 y 7)", "Comparar dos ejercicios"]
    assert p["tablas"][0][0]["Var. rel. 21–22"] == "+85.92%" and p["tablas"][1][1]["Var. abs. 24–25"] == "-27,034,533"
    assert p["tablas"][2][4]["Var. relativa CTN"] == "-277.02%"
    assert set(p["descargas"]) == {"Descargar PDF", "Descargar Excel"}
    # Por defecto compara los dos ultimos ejercicios
    assert "Saldo actual (2025)" in p["tablas"][4][0]


def test_pantalla_horizontal_con_seleccion_de_periodo_y_nivel(pantallas):
    filas = pantallas["balance_2024_cuentas"]["tablas"][4]
    assert "Saldo actual (2024)" in filas[0] and "Saldo anterior (2023)" in filas[0]
    assert {"Aparece", "Desaparece"} <= {f["Sentido"] for f in filas}


def test_pantalla_horizontal_de_resultados(pantallas):
    p = pantallas["resultados"]
    assert p["encabezados"] == ["Reporte — Análisis Horizontal del Estado de Resultados"]
    assert p["tablas"][0][0]["2021"] == "523,965,227" and p["tablas"][0][6]["Var. rel. 24–25"] == "+288.73%"
    assert "Otros ingresos (gastos) no operativos" in {f["Partida"] for f in pantallas["resultados_2025_grupos"]["tablas"][1]}


@pytest.mark.parametrize("pagina, tabla_doc, fila, anio, esperado", [
    ("vertical_balance", "7.2", "Activos corrientes", "2025", "31.67%"),
    ("vertical_resultados", "7.1", "Costo de ventas", "2022", "-82.12%"),
])
def test_pantallas_verticales_incluyen_el_comparativo(pantallas, pagina, tabla_doc, fila, anio, esperado):
    p = pantallas[pagina]
    assert any(tabla_doc in t for t in p["pestanas"])
    comparativo = {f["Partida"]: f for f in p["tablas"][-1]}
    assert comparativo[fila][anio] == esperado


def test_pantalla_dupont_incluye_los_cinco_ejercicios(pantallas):
    total, controladora = pantallas["dupont"]["tablas"][-2:]
    rsp = next(f for f in total if "RSP" in f["Concepto"])
    assert [rsp[str(a)] for a in ANIOS] == ["47.21%", "4.70%", "5.86%", "1.35%", "5.15%"]
    assert next(f for f in controladora if "ROE) de la controladora" in f["Concepto"])["2021"] == "46.75%"


def test_pantalla_de_indicadores_muestra_bases_y_descargas_por_apartado(pantallas):
    p = pantallas["indicadores"]
    assert p["pestanas"][:4] == ["Liquidez", "Actividad", "Endeudamiento", "Rentabilidad"]
    assert p["descargas"].count("Descargar PDF") == 5 and p["descargas"].count("Descargar Excel") == 5  # 4 apartados + completo
    columnas = [t for t in p["tablas"] if t and "Concepto" in t[0]]
    assert len(columnas) >= 4
    assert any(f["Concepto"] == "Costo de ventas" and f["2025"] == "331,430,173" for t in columnas for f in t)


def test_balance_general_2021_coincide_con_los_totales_originales(pantallas):
    p = pantallas["balance_general_2021"]
    textos = " ".join(p["textos"])
    textos = textos.replace("\\", "")
    assert "553,955,185.00" in textos and "408,633,995.00" in textos and "145,321,190.00" in textos
