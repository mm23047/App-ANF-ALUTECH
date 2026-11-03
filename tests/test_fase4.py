"""Fase 4: seguridad HTML (B-04), dependencias (B-05), codigos contables
(B-06), datos de la empresa (B-07) y confirmacion de operaciones masivas
(M-10, paso 4.2)."""
import ast
import datetime
import io
import json
import re
import sqlite3
import string
import subprocess
import sys
from decimal import Decimal
from importlib import metadata
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import streamlit
from openpyxl import Workbook, load_workbook
from reportlab import rl_config

from calculations.balance_sheet import compute_balance_sheet
from components import confirmacion
from components.confirmacion import Cambio
from components.texto import md
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
    get_entries_map,
    get_fiscal_period,
    get_initial_balances_map,
    get_or_create_fiscal_period,
    list_accounts,
    list_history,
    save_company,
    upsert_entry,
)
from database.seed import DEFAULT_ACCOUNTS, seed_default_accounts

PROYECTO = Path(__file__).resolve().parent.parent
MALICIOSO = "<b>Alutech</b> & <script>alert(1)</script> *SV* :red[x] $1$ [y](javascript:alert(1))"


@pytest.fixture()
def bd(tmp_path):
    path = tmp_path / "fase4.db"
    init_db(db_path=path)
    with session_scope() as s:
        seed_default_accounts(s)
        save_company(s, nombre_legal="Empresa Prueba", nombre_comercial="EP", actividad_economica="x",
                     pais="SV", moneda="USD", anio_inicial_analisis=2021)
        get_or_create_fiscal_period(s, 2021)
    yield path
    connection.dispose_engine()


def _id(s, codigo):
    return get_account_by_codigo(s, codigo).id


def _balance(s):
    p = get_fiscal_period(s, 2021)
    return {s.get(type(get_account_by_codigo(s, "1001")), i).codigo: v for i, v in get_entries_map(s, p.id, Tipo.BALANCE).items()}


def _n_historial(s):
    return len(list_history(s))


# =========================================================== B-04 HTML

def _sin_escapes(texto):
    return re.sub(r"\\(.)", r"\1", texto)


@pytest.mark.parametrize("valor", [
    "<b>x</b>", "<script>alert(1)</script>", "**negrita**", "_x_", ":red[x]", ":smile:", "$x^2$", "&amp; &lt;",
    "[enlace](javascript:alert(1))", "# título", "1. lista", "`código`", "a\\b", "USD", "Q", "€", "", MALICIOSO,
])
def test_md_muestra_el_texto_literal(valor):
    escapado = md(valor)
    assert _sin_escapes(escapado) == valor
    # Ningun signo de puntuacion queda sin barra invertida delante.
    sin_pares = re.sub(r"\\.", "", escapado)
    assert not any(c in string.punctuation for c in sin_pares)


def test_md_une_saltos_de_linea_y_acepta_none():
    assert md("a\n# b") == "a \\# b"
    assert md(None) == ""


def _llamadas_unsafe_html(ruta: Path):
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Call):
            for kw in nodo.keywords:
                if kw.arg == "unsafe_allow_html" and not (isinstance(kw.value, ast.Constant) and kw.value.value is False):
                    yield nodo


def test_unico_html_habilitado_es_el_css_constante_de_app():
    fuentes = [p for p in PROYECTO.rglob("*.py") if ".venv" not in p.parts and "tests" not in p.parts]
    usos = {p.relative_to(PROYECTO).as_posix(): list(_llamadas_unsafe_html(p)) for p in fuentes}
    usos = {k: v for k, v in usos.items() if v}
    assert list(usos) == ["app.py"] and len(usos["app.py"]) == 1
    cuerpo = usos["app.py"][0].args[0]
    interpolados = [n.value.id for n in ast.walk(cuerpo) if isinstance(n, ast.FormattedValue)]
    assert interpolados == ["PRIMARY"]  # constante del codigo, no un dato del usuario
    assert not any(isinstance(n, ast.Call) for n in ast.walk(cuerpo))


def test_streamlit_no_admite_html_si_no_se_habilita():
    """La proteccion de Streamlit en la que se apoya md(): sin
    unsafe_allow_html el proto lleva allow_html = False."""
    from streamlit.proto.Markdown_pb2 import Markdown

    assert Markdown().allow_html is False


def test_tablas_usan_markdown_nativo_y_escapan_la_moneda(monkeypatch):
    from components import tables

    llamadas = []
    monkeypatch.setattr(streamlit, "markdown", lambda cuerpo, *a, **k: llamadas.append((cuerpo, a, k)))
    monkeypatch.setattr(streamlit, "dataframe", lambda *a, **k: None)

    class Cuenta:
        codigo, nombre = "1001", "Efectivo"

    class Linea:
        cuenta, valor = Cuenta(), Decimal("10")

    class Grupo:
        nombre, lineas, subtotal = "Activo <i>corriente</i>", [Linea()], Decimal("10")

    tables.mostrar_grupo(Grupo(), "<b>x</b>")
    tables.mostrar_total("Total *Activo*", Decimal("10"), "<b>x</b>")
    assert all(not a and not k.get("unsafe_allow_html") for _, a, k in llamadas)
    cuerpos = [c for c, _, _ in llamadas]
    assert "**Subtotal Activo \\<i\\>corriente\\<\\/i\\>: \\<b\\>x\\<\\/b\\> 10\\.00**" in cuerpos
    assert "**Total \\*Activo\\*: \\<b\\>x\\<\\/b\\> 10\\.00**" in cuerpos
    # Misma presentacion que antes: negrita y alineado a la derecha.
    assert sum(1 for _, _, k in llamadas if k.get("text_alignment") == "right") == 2


@pytest.fixture()
def pdf_sin_compresion(monkeypatch):
    monkeypatch.setattr(rl_config, "pageCompression", 0)


def _lineas_pdf(datos: bytes) -> list[str]:
    """Texto de cada linea del PDF sin comprimir: reportlab parte una linea
    en varios operadores Tj cuando contiene signos como '<'."""
    lineas = []
    for linea in datos.decode("latin-1").splitlines():
        trozos = re.findall(r"\(((?:\\.|[^\\)])*)\) Tj", linea)
        if trozos:
            # Escapes de cadena PDF: \( \) \\ y octales (\363 = ó).
            lineas.append(re.sub(r"\\([0-7]{1,3}|.)", lambda m: chr(int(m[1], 8)) if m[1].isdigit() else m[1],
                                 "".join(trozos)))
    return lineas


@pytest.mark.parametrize("moneda", ["<x", "<b>U</b>", "&", "<font color='red'>"])
def test_pdf_con_moneda_maliciosa_no_falla_y_la_muestra_literal(bd, pdf_sin_compresion, moneda):
    """reportlab interpreta etiquetas en Paragraph: sin escapar, '<x' hacia
    fallar el PDF del Balance descuadrado y del analisis vertical."""
    from calculations.vertical_analysis import compute_vertical_balance
    from reports.pdf_export import export_balance_pdf, export_vertical_pdf

    with session_scope() as s:
        c = get_company(s)
        save_company(s, nombre_legal=MALICIOSO, nombre_comercial="x", actividad_economica="x", pais="SV",
                     moneda=moneda, anio_inicial_analisis=2021)
        p = get_fiscal_period(s, 2021)
        upsert_entry(s, fiscal_period_id=p.id, account_id=_id(s, "1001"), valor="100", tipo=Tipo.BALANCE)
    with session_scope() as s:
        c, p = get_company(s), get_fiscal_period(s, 2021)
        bs = compute_balance_sheet(s, p.id)
        assert not bs.cuadra  # para que se genere el parrafo con la diferencia
        balance = _lineas_pdf(export_balance_pdf(c, p, bs))
        vertical = compute_vertical_balance(s, p.id)
        export_vertical_pdf(c, p, "Análisis Vertical", vertical.lineas, vertical.base_total_activo, "Total Activo")
    assert any(f"Diferencia: {moneda} 100.00." in linea for linea in balance)
    assert any(linea.startswith("<b>Alutech</b> & <script>") for linea in balance)


@pytest.fixture(scope="module")
def escenarios_app(tmp_path_factory):
    """Ejecuta tests/humo_fase4.py (AppTest, app.py real) en un subproceso."""
    ruta = tmp_path_factory.mktemp("fase4") / "financiera.db"
    init_db(db_path=ruta)
    with session_scope() as s:
        seed_default_accounts(s)
        save_company(s, nombre_legal=MALICIOSO, nombre_comercial="x", actividad_economica="x", pais="SV",
                     moneda="<i>U</i>", anio_inicial_analisis=2021)
        p, _ = get_or_create_fiscal_period(s, 2021)
        upsert_entry(s, fiscal_period_id=p.id, account_id=_id(s, "1002"), valor="50", tipo=Tipo.BALANCE)
    connection.dispose_engine()
    proceso = subprocess.run([sys.executable, str(PROYECTO / "tests" / "humo_fase4.py"), str(ruta)],
                             capture_output=True, text=True, encoding="utf-8", timeout=600)
    assert proceso.returncode == 0, proceso.stderr[-3000:]
    return json.loads(proceso.stdout.strip().splitlines()[-1])


def test_paginas_muestran_los_datos_maliciosos_como_texto(escenarios_app):
    r = escenarios_app
    assert not r["b04_excepciones"] and not r["b04_dashboard_excepciones"]
    for subheaders in (r["b04_subheaders"], r["b04_dashboard_subheaders"]):
        assert _sin_escapes(subheaders[0]).startswith(MALICIOSO)
        assert "<script>" not in subheaders[0] and "<b>" not in subheaders[0]
    assert "Moneda: \\<i\\>U\\<\\/i\\>" in r["b04_captions"]
    con_html = [m["valor"] for m in r["b04_markdown"] if m["html"]]
    assert len(con_html) == 1 and con_html[0].startswith("<style>")
    assert len(r["b04_dashboard_html"]) == 1
    assert "**Total Activo: \\<i\\>U\\<\\/i\\> 50\\.00**" in [m["valor"] for m in r["b04_markdown"]]


# =========================================================== B-05 dependencias

def _requisitos():
    lineas = (PROYECTO / "requirements.txt").read_text(encoding="utf-8").splitlines()
    return [l.strip() for l in lineas if l.strip() and not l.lstrip().startswith("#")]


def test_requirements_fija_las_versiones_instaladas_y_probadas():
    requisitos = _requisitos()
    assert len(requisitos) == 8
    for linea in requisitos:
        paquete, _, version = linea.partition("==")
        assert version, f"{linea}: la versión no está fijada"
        assert metadata.version(paquete) == version, f"{paquete}: instalado {metadata.version(paquete)}, fijado {version}"


def test_requirements_cubre_las_librerias_importadas():
    terceros = {"streamlit", "sqlalchemy", "pandas", "numpy", "plotly", "openpyxl", "reportlab", "pytest"}
    importados = set()
    for p in PROYECTO.rglob("*.py"):
        if ".venv" in p.parts:
            continue
        for nodo in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
            if isinstance(nodo, ast.Import):
                importados |= {a.name.split(".")[0] for a in nodo.names}
            elif isinstance(nodo, ast.ImportFrom) and nodo.module and nodo.level == 0:
                importados.add(nodo.module.split(".")[0])
    locales = {"app", "calculations", "components", "database", "modules", "reports", "scripts", "conftest", "humo_paginas"}
    externos = {m for m in importados - locales if m not in sys.stdlib_module_names}
    assert externos == terceros
    assert {l.partition("==")[0].lower() for l in _requisitos()} == terceros


def test_apis_de_streamlit_usadas_existen_en_la_version_fijada():
    import inspect

    assert "text_alignment" in inspect.signature(streamlit.markdown).parameters
    for funcion in (streamlit.dataframe, streamlit.plotly_chart, streamlit.data_editor):
        assert "width" in inspect.signature(funcion).parameters
    assert "border" in inspect.signature(streamlit.container).parameters


# =========================================================== B-06 codigos

@pytest.mark.parametrize("valor, esperado", [
    (1001.0, "1001"), (1001, "1001"), (np.int64(1001), "1001"), (np.float64(1001.0), "1001"), ("1001", "1001"),
    (" 1001 ", "1001"), ("1.1.01", "1.1.01"), ("A-10", "A-10"), ("0101", "0101"), (None, ""), (float("nan"), ""),
    (np.nan, ""), ("", ""), ("  ", ""), (pd.NA, ""),
])
def test_normalizar_codigo(valor, esperado):
    from modules.excel_import import normalizar_codigo

    assert normalizar_codigo(valor) == esperado


@pytest.mark.parametrize("valor", [1001.5, 1.1, True, np.bool_(False), float("inf"), 2.0**53, -(2.0**60),
                                   datetime.datetime(2021, 1, 1), pd.Timestamp("2021-01-01")])
def test_codigo_ambiguo_se_rechaza(valor):
    from modules.excel_import import CodigoAmbiguo, normalizar_codigo

    with pytest.raises(CodigoAmbiguo):
        normalizar_codigo(valor)


def test_los_codigos_del_catalogo_no_cambian_al_normalizar():
    from modules.excel_import import normalizar_codigo

    for codigo, *_ in DEFAULT_ACCOUNTS:
        assert normalizar_codigo(codigo) == codigo
        assert normalizar_codigo(int(codigo)) == codigo
        assert normalizar_codigo(float(codigo)) == codigo


def _fila(codigo, periodo=2021, valor=5):
    return {"Código de cuenta": codigo, "Nombre de cuenta": "x", "Categoría": "", "Subcategoría": "",
            "Período": periodo, "Valor monetario": valor}


def test_validacion_de_codigos_en_la_importacion(bd):
    from modules.excel_import import _validar_dataframe

    df = pd.DataFrame([_fila(1001.0), _fila(1002.5), _fila("1003.0"), _fila(9999.0), _fila(True), _fila(" 1004 ")])
    with session_scope() as s:
        filas = _validar_dataframe(s, df)
    assert [(f.codigo, f.estado) for f in filas] == [
        ("1001", "OK"), ("1002.5", "CODIGO_AMBIGUO"), ("1003.0", "CODIGO_AMBIGUO"), ("9999", "CUENTA_DESCONOCIDA"),
        ("True", "CODIGO_AMBIGUO"), ("1004", "OK")]
    assert filas[0].cuenta.codigo == "1001"
    assert "existe '1003'" in filas[2].mensaje and "No se corrige" in filas[2].mensaje


def test_codigo_numerico_sin_ceros_a_la_izquierda_se_reporta(bd):
    from modules.excel_import import _validar_dataframe

    with session_scope() as s:
        create_account(s, codigo="0105", nombre="Caja chica", categoria_principal=Cat.ACTIVO, subcategoria=Sub.CORRIENTE,
                       naturaleza_saldo=Nat.DEUDORA)
    with session_scope() as s:
        filas = _validar_dataframe(s, pd.DataFrame([_fila(105.0), _fila("0105")]))
    assert [(f.codigo, f.estado) for f in filas] == [("105", "CODIGO_AMBIGUO"), ("0105", "OK")]
    assert "0105" in filas[0].mensaje


def test_mismo_codigo_en_formatos_distintos_es_duplicado(bd):
    from modules.excel_import import _validar_dataframe

    with session_scope() as s:
        filas = _validar_dataframe(s, pd.DataFrame([_fila(1001.0), _fila("1001")]))
    assert [f.estado for f in filas] == ["OK", "DUPLICADA"]


def test_importar_excel_con_codigos_numericos_y_celdas_vacias(bd, monkeypatch):
    """Columna de codigos numerica con una fila vacia: pandas la lee como
    float (1001.0). Se importa con los codigos del catalogo sin cambiarlos."""
    from modules import excel_import

    wb = Workbook()
    ws = wb.active
    ws.append(excel_import.COLUMNAS)
    ws.append([1001, "Efectivo", "", "", 2021, 100])
    ws.append([None, None, None, None, None, None])
    ws.append([1002, "CxC", "", "", 2021, 50])
    archivo = io.BytesIO()
    wb.save(archivo)
    archivo.seek(0)
    assert pd.read_excel(io.BytesIO(archivo.getvalue()))["Código de cuenta"].dtype == float
    with session_scope() as s:
        codigos_antes = [(c.id, c.codigo) for c in list_accounts(s)]
    monkeypatch.setattr(streamlit, "file_uploader", lambda *a, **k: archivo)
    monkeypatch.setattr(streamlit, "button", lambda label, *a, **k: label == "Confirmar importación")
    monkeypatch.setattr(streamlit, "checkbox", lambda *a, **k: False)
    with render_scope() as s:
        excel_import.render(s, get_company(s))
    with session_scope() as s:
        assert _balance(s) == {"1001": Decimal("100.00"), "1002": Decimal("50.00")}
        assert [(c.id, c.codigo) for c in list_accounts(s)] == codigos_antes


# =========================================================== B-07 datos de la empresa

BD_REAL = connection.DATA_DIR / "financiera.db"


@pytest.mark.skipif(not BD_REAL.exists(), reason="sin BD de trabajo")
def test_bd_de_trabajo_tiene_los_datos_corregidos_y_conserva_la_evidencia():
    con = sqlite3.connect(f"file:{BD_REAL}?mode=ro", uri=True)
    empresa = con.execute(
        "select nombre_legal, nombre_comercial, actividad_economica, pais, moneda, anio_inicial_analisis from company"
    ).fetchall()
    evidencia = con.execute(
        "select campo, valor_anterior, valor_nuevo from change_history where tabla_afectada = 'company' "
        "and operacion = 'EDITAR' order by id"
    ).fetchall()
    # Desde la adaptacion Alutech, 2021 tambien tiene los importes reales (cuentas CB...);
    # los 19 ceros son los de las cuentas del catalogo estandar.
    ceros = con.execute(
        "select count(*), sum(b.valor = 0) from balance_entry b join fiscal_period p on p.id = b.fiscal_period_id "
        "join account a on a.id = b.account_id where p.anio = 2021 and a.codigo not like 'CB%' and a.codigo not like 'CN%'"
    ).fetchone()
    con.close()
    # Revision final Alutech (2026-11-02, autorizada): identificacion de la entidad analizada.
    assert empresa == [("Alutech, S. A. de C. V. y subsidiarias – División Acero", "Alutech – División Acero", "metal",
                        "Honduras", "USD", 2021)]
    # La correccion de la fase 4 sigue en el historial, seguida de la actualizacion final.
    assert evidencia[-6:-3] == [("nombre_legal", "alutech", "Alutech"), ("nombre_comercial", "aluetch sv", "Alutech SV"),
                                ("pais", "El Salvaodr", "El Salvador")]
    assert evidencia[-3:] == [("nombre_legal", "Alutech", "Alutech, S. A. de C. V. y subsidiarias – División Acero"),
                              ("nombre_comercial", "Alutech SV", "Alutech – División Acero"), ("pais", "El Salvador", "Honduras")]
    # El usuario autorizo (2026-11-02) borrar solo el 0.00 de «3004 Resultado del ejercicio» 2021; los otros 18 se conservan.
    assert ceros == (18, 18)
    con = sqlite3.connect(f"file:{BD_REAL}?mode=ro", uri=True)
    borrado = con.execute(
        "select h.valor_anterior, h.valor_nuevo from change_history h join account a on a.id = h.account_id "
        "where h.tabla_afectada = 'balance_entry' and h.operacion = 'ELIMINAR' and a.codigo = '3004'"
    ).fetchall()
    sigue = con.execute("select estado from account where codigo = '3004'").fetchall()
    con.close()
    assert borrado == [("0.00", None)] and sigue == [("ACTIVA",)]


@pytest.mark.skipif(not BD_REAL.exists(), reason="sin BD de trabajo")
def test_encabezados_de_reportes_con_los_datos_corregidos(tmp_path, pdf_sin_compresion):
    from reports.excel_export import export_balance_excel
    from reports.pdf_export import export_balance_pdf

    copia = tmp_path / "copia.db"
    origen = sqlite3.connect(f"file:{BD_REAL}?mode=ro", uri=True)
    destino = sqlite3.connect(copia)
    origen.backup(destino)
    origen.close()
    destino.close()
    init_db(db_path=copia)
    try:
        with session_scope() as s:
            c, p = get_company(s), get_fiscal_period(s, 2021)
            bs = compute_balance_sheet(s, p.id)
            hoja = load_workbook(io.BytesIO(export_balance_excel(c, p, bs))).active
            pdf = _lineas_pdf(export_balance_pdf(c, p, bs))
    finally:
        connection.dispose_engine()
    assert hoja.cell(1, 1).value == "Alutech, S. A. de C. V. y subsidiarias – División Acero"
    assert any("Alutech, S. A. de C. V. y subsidiarias" in l for l in pdf)  # titulo del encabezado
    assert not any("alutech" in l or "aluetch" in l or "Salvaodr" in l for l in pdf)


# =========================================================== D08 confirmaciones

def _botones(monkeypatch, *pulsados):
    monkeypatch.setattr(streamlit, "button", lambda label, *a, **k: label in pulsados)


def _op(cambios=None):
    return confirmacion.proponer("p", 1, resumen="r", cambios=cambios or [Cambio(1, "1001 — x", None, Decimal("1"))])


def test_confirmacion_sin_pulsar_no_devuelve_nada(monkeypatch):
    _botones(monkeypatch)
    _op()
    assert confirmacion.mostrar("p", 1) is None
    assert confirmacion.pendiente("p") is not None


def test_confirmacion_cancelar_descarta(monkeypatch):
    avisos = []
    monkeypatch.setattr(streamlit, "info", lambda m, *a, **k: avisos.append(m))
    _botones(monkeypatch, confirmacion.ETIQUETA_CANCELAR, confirmacion.ETIQUETA_CONFIRMAR)
    _op()
    assert confirmacion.mostrar("p", 1) is None  # cancelar prevalece
    assert confirmacion.pendiente("p") is None
    assert avisos == ["Operación cancelada. No se modificó ningún registro."]


def test_confirmacion_es_de_un_solo_uso(monkeypatch):
    _botones(monkeypatch, confirmacion.ETIQUETA_CONFIRMAR)
    op = _op()
    assert confirmacion.mostrar("p", 1) is op
    assert confirmacion.pendiente("p") is None
    assert confirmacion.mostrar("p", 1) is None  # doble clic / repeticion


def test_confirmacion_se_descarta_al_cambiar_de_contexto_o_de_pagina(monkeypatch):
    _botones(monkeypatch, confirmacion.ETIQUETA_CONFIRMAR)
    _op()
    assert confirmacion.mostrar("p", 2) is None and confirmacion.pendiente("p") is None
    confirmacion.descartar_al_navegar("entry_balance")
    _op()
    confirmacion.descartar_al_navegar("entry_balance")
    assert confirmacion.pendiente("p") is not None
    confirmacion.descartar_al_navegar("dashboard")
    assert confirmacion.pendiente("p") is None


def test_confirmacion_vigente_compara_los_valores_mostrados():
    op = _op([Cambio(1, "a", None, Decimal("1")), Cambio(2, "b", Decimal("5.00"), Decimal("6"))])
    assert confirmacion.vigente(op, {2: Decimal("5.00")})
    assert not confirmacion.vigente(op, {1: Decimal("0.00"), 2: Decimal("5.00")})
    assert not confirmacion.vigente(op, {2: Decimal("7.00")})


def _capturar(monkeypatch, valores, *botones):
    from modules import data_entry

    monkeypatch.setattr(streamlit, "number_input", lambda label, *a, value=None, **k: valores.get(label.split(" — ")[0], value))
    monkeypatch.setattr(streamlit, "form_submit_button", lambda *a, **k: "Guardar" in botones)
    _botones(monkeypatch, *botones)
    monkeypatch.setattr(streamlit, "rerun", lambda *a, **k: None)
    with render_scope() as s:
        p = get_fiscal_period(s, 2021)
        data_entry._render_grupos(s, p, Tipo.BALANCE, data_entry.GRUPOS_BALANCE, "USD", "form")


def _estado_bd(ruta):
    con = sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)
    datos = {t: con.execute(f"select * from {t}").fetchall() for t in ("balance_entry", "change_history", "fiscal_period")}
    con.close()
    return datos


def test_captura_guardar_solo_propone_y_cancelar_no_modifica_nada(bd, monkeypatch):
    antes = _estado_bd(bd)
    _capturar(monkeypatch, {"1001": 100.0, "1002": 0.0}, "Guardar")
    assert _estado_bd(bd) == antes
    op = confirmacion.pendiente("captura_form")
    assert op.resumen == ("Se modificarán 2 valor(es) de Balance General en el ejercicio 2021: "
                          "2 nuevo(s) y 0 modificado(s).")
    assert [(c.cuenta, c.previo, c.nuevo) for c in op.cambios] == [
        ("1001 — Efectivo y equivalentes", None, Decimal("100.00")), ("1002 — Cuentas por cobrar", None, Decimal("0.00"))]
    _capturar(monkeypatch, {"1001": 100.0, "1002": 0.0}, confirmacion.ETIQUETA_CANCELAR)
    assert confirmacion.pendiente("captura_form") is None
    assert _estado_bd(bd) == antes
    # Tras cancelar, confirmar ya no tiene efecto.
    _capturar(monkeypatch, {"1001": 100.0, "1002": 0.0}, confirmacion.ETIQUETA_CONFIRMAR)
    assert _estado_bd(bd) == antes


def test_captura_confirmada_escribe_lo_propuesto_en_un_lote(bd, monkeypatch):
    _capturar(monkeypatch, {"1001": 100.0, "1002": 2.675}, "Guardar")
    # Lo escrito es lo propuesto, aunque el formulario cambie despues sin reenviarse.
    _capturar(monkeypatch, {"1001": 999.0}, confirmacion.ETIQUETA_CONFIRMAR)
    with session_scope() as s:
        assert _balance(s) == {"1001": Decimal("100.00"), "1002": Decimal("2.68")}
        assert len({h.lote_id for h in list_history(s, tabla_afectada="balance_entry")}) == 1
    antes = _estado_bd(bd)
    _capturar(monkeypatch, {}, confirmacion.ETIQUETA_CONFIRMAR)  # repeticion del clic
    assert _estado_bd(bd) == antes


def test_captura_confirmada_con_datos_cambiados_no_escribe(bd, monkeypatch):
    errores = []
    monkeypatch.setattr(streamlit, "error", lambda m, *a, **k: errores.append(m))
    _capturar(monkeypatch, {"1001": 100.0}, "Guardar")
    with session_scope() as s:
        upsert_entry(s, fiscal_period_id=get_fiscal_period(s, 2021).id, account_id=_id(s, "1001"), valor="7",
                     tipo=Tipo.BALANCE)
    antes = _estado_bd(bd)
    _capturar(monkeypatch, {"1001": 100.0}, confirmacion.ETIQUETA_CONFIRMAR)
    assert _estado_bd(bd) == antes
    assert errores and "cambiaron después de la vista previa" in errores[0]


def test_captura_confirmada_falla_a_mitad_y_no_deja_nada(bd, monkeypatch):
    from modules import data_entry

    _capturar(monkeypatch, {"1001": 100.0, "1002": 5.0, "1003": 6.0}, "Guardar")
    original = data_entry.upsert_entry
    llamadas = []

    def falla_en_la_segunda(*a, **k):
        llamadas.append(1)
        if len(llamadas) == 2:
            raise ValueError("fallo simulado")
        return original(*a, **k)

    monkeypatch.setattr(data_entry, "upsert_entry", falla_en_la_segunda)
    monkeypatch.setattr(streamlit, "error", lambda *a, **k: None)
    antes = _estado_bd(bd)
    _capturar(monkeypatch, {}, confirmacion.ETIQUETA_CONFIRMAR)
    assert len(llamadas) == 2
    assert _estado_bd(bd) == antes


def test_saldos_iniciales_requieren_confirmacion(bd, monkeypatch):
    from modules import data_entry

    monkeypatch.setattr(streamlit, "number_input", lambda label, *a, value=None, **k: 500.0 if label.startswith("1001 ") else value)
    monkeypatch.setattr(streamlit, "form_submit_button", lambda *a, **k: True)
    monkeypatch.setattr(streamlit, "selectbox", lambda label, opciones, *a, **k: opciones[0])
    monkeypatch.setattr(streamlit, "rerun", lambda *a, **k: None)
    _botones(monkeypatch)
    with render_scope() as s:
        data_entry.render_initial_balances(s, get_company(s))
    with session_scope() as s:
        assert get_initial_balances_map(s, get_fiscal_period(s, 2021).id) == {}
        assert confirmacion.pendiente("captura_saldos_iniciales") is not None
    monkeypatch.setattr(streamlit, "form_submit_button", lambda *a, **k: False)
    _botones(monkeypatch, confirmacion.ETIQUETA_CONFIRMAR)
    with render_scope() as s:
        data_entry.render_initial_balances(s, get_company(s))
    with session_scope() as s:
        assert get_initial_balances_map(s, get_fiscal_period(s, 2021).id) == {_id(s, "1001"): Decimal("500.00")}


def _editar(monkeypatch, nuevo_valor, *botones):
    from modules import data_edit

    def editor(df, **k):
        df = df.copy()
        df.loc[df["Código"] == "1001", "Valor"] = nuevo_valor
        return df

    monkeypatch.setattr(streamlit, "data_editor", editor)
    monkeypatch.setattr(streamlit, "checkbox", lambda *a, **k: False)
    monkeypatch.setattr(streamlit, "rerun", lambda *a, **k: None)
    _botones(monkeypatch, *botones)
    with render_scope() as s:
        data_edit._tabla_editable(s, get_fiscal_period(s, 2021).id, Tipo.BALANCE, "USD", key="k")


def test_edicion_requiere_confirmacion_y_cancelar_no_modifica(bd, monkeypatch):
    with session_scope() as s:
        upsert_entry(s, fiscal_period_id=get_fiscal_period(s, 2021).id, account_id=_id(s, "1001"), valor="100",
                     tipo=Tipo.BALANCE)
    antes = _estado_bd(bd)
    _editar(monkeypatch, 150.0, "Guardar cambios")
    assert _estado_bd(bd) == antes
    assert [(c.previo, c.nuevo) for c in confirmacion.pendiente("k").cambios] == [(Decimal("100.00"), Decimal("150.00"))]
    _editar(monkeypatch, 150.0, confirmacion.ETIQUETA_CANCELAR)
    assert _estado_bd(bd) == antes and confirmacion.pendiente("k") is None
    _editar(monkeypatch, 150.0, "Guardar cambios")
    _editar(monkeypatch, 150.0, confirmacion.ETIQUETA_CONFIRMAR)
    with session_scope() as s:
        assert _balance(s) == {"1001": Decimal("150.00")}


def test_edicion_cambiada_despues_de_proponer_no_se_guarda(bd, monkeypatch):
    with session_scope() as s:
        upsert_entry(s, fiscal_period_id=get_fiscal_period(s, 2021).id, account_id=_id(s, "1001"), valor="100",
                     tipo=Tipo.BALANCE)
    antes = _estado_bd(bd)
    _editar(monkeypatch, 150.0, "Guardar cambios")
    _editar(monkeypatch, 175.0, confirmacion.ETIQUETA_CONFIRMAR)  # la tabla ya no es la propuesta
    assert _estado_bd(bd) == antes and confirmacion.pendiente("k") is None


def _importar(monkeypatch, archivo, *botones):
    from modules import excel_import

    archivo.seek(0)
    monkeypatch.setattr(streamlit, "file_uploader", lambda *a, **k: archivo)
    _botones(monkeypatch, *botones)
    monkeypatch.setattr(streamlit, "checkbox", lambda *a, **k: False)
    with render_scope() as s:
        excel_import.render(s, get_company(s))


def _xlsx(*filas):
    from modules.excel_import import COLUMNAS

    wb = Workbook()
    ws = wb.active
    ws.append(COLUMNAS)
    for f in filas:
        ws.append(f)
    b = io.BytesIO()
    wb.save(b)
    return b


def test_importacion_muestra_el_alcance_y_no_se_repite(bd, monkeypatch):
    avisos = []
    monkeypatch.setattr(streamlit, "warning", lambda m, *a, **k: avisos.append(m))
    with session_scope() as s:
        upsert_entry(s, fiscal_period_id=get_fiscal_period(s, 2021).id, account_id=_id(s, "1002"), valor="50",
                     tipo=Tipo.BALANCE)
    archivo = _xlsx(["1001", "x", "", "", 2021, 100], ["1002", "x", "", "", 2021, 50])
    antes = _estado_bd(bd)
    _importar(monkeypatch, archivo)  # vista previa
    assert _estado_bd(bd) == antes
    assert any("Alcance: 1 importe(s) nuevo(s), 0 sobrescrito(s) y 1 sin cambios en el/los ejercicio(s) 2021." in a
               for a in avisos)
    _importar(monkeypatch, archivo, "Confirmar importación")
    with session_scope() as s:
        assert _balance(s) == {"1001": Decimal("100.00"), "1002": Decimal("50.00")}
        n = _n_historial(s)
    # Segundo clic sobre la vista previa ya importada: no se ejecuta otra vez.
    avisos.clear()
    _importar(monkeypatch, archivo, "Confirmar importación")
    with session_scope() as s:
        assert _n_historial(s) == n
    assert any("La vista previa cambió" in a for a in avisos)


def test_importacion_con_bd_cambiada_tras_la_vista_previa_no_importa(bd, monkeypatch):
    monkeypatch.setattr(streamlit, "warning", lambda *a, **k: None)
    archivo = _xlsx(["1001", "x", "", "", 2021, 100])
    _importar(monkeypatch, archivo)  # vista previa: 1001 sin valor
    with session_scope() as s:
        upsert_entry(s, fiscal_period_id=get_fiscal_period(s, 2021).id, account_id=_id(s, "1001"), valor="7",
                     tipo=Tipo.BALANCE)
    antes = _estado_bd(bd)
    _importar(monkeypatch, archivo, "Confirmar importación")
    assert _estado_bd(bd) == antes


def test_importacion_cancelada_no_modifica_nada(bd, monkeypatch):
    archivo = _xlsx(["1001", "x", "", "", 2030, 100])
    antes = _estado_bd(bd)
    _importar(monkeypatch, archivo)
    _importar(monkeypatch, archivo, "Cancelar")
    assert _estado_bd(bd) == antes


def test_escenarios_de_confirmacion_en_la_app_real(escenarios_app):
    r = escenarios_app
    assert r["d08_propuesta_hash_igual"] and r["d08_propuesta_boton_confirmar"]
    assert r["d08_propuesta_tablas"] == [[
        {"Cuenta": "1001 — Efectivo y equivalentes", "Valor actual": "Sin dato", "Valor nuevo": "100.00"},
        {"Cuenta": "1002 — Cuentas por cobrar", "Valor actual": "50.00", "Valor nuevo": "75.00"}]]
    assert any("Se modificarán 2 valor(es) de Balance General en el ejercicio 2021: 1 nuevo(s) y 1 modificado(s)." in t
               for t in r["d08_propuesta_textos"])
    assert r["d08_cancelar_hash_igual"] and r["d08_cancelar_sin_boton_confirmar"]
    assert "Operación cancelada. No se modificó ningún registro." in r["d08_cancelar_textos"]
    assert r["d08_recarga_hash_igual"] and r["d08_recarga_sin_boton_confirmar"]
    assert r["d08_navegar_hash_igual"] and r["d08_navegar_sin_boton_confirmar"]
    assert r["d08_confirmar_importes"] == {"1001": 10000, "1002": 7500}  # centavos
    assert not r["d08_confirmar_excepciones"] and r["d08_confirmar_sin_boton_confirmar"]
    assert r["d08_repetir_hash_igual"] and r["d08_repetir_sin_boton_confirmar"]
    assert r["d08_obsoleta_importe_1003"] == 999  # el valor externo no se sobrescribio
    assert any("cambiaron después de la vista previa" in t for t in r["d08_obsoleta_textos"])
    assert r["d08_edicion_hash_igual"] and r["d08_edicion_sin_boton_confirmar"] and not r["d08_edicion_excepciones"]
