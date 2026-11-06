"""B-10: los textos del usuario se exportan a Excel como texto literal,
nunca como formula; las formulas de control de la aplicacion se conservan."""
import io
import re
import zipfile
from decimal import Decimal

import pandas as pd
import pytest
from openpyxl import Workbook, load_workbook

from calculations.balance_sheet import compute_balance_sheet
from calculations.dupont import compute_dupont
from calculations.income_statement import compute_income_statement
from calculations.vertical_analysis import compute_vertical_balance, compute_vertical_income
from components.celdas_excel import agregar_fila, escribir, formula, texto
from database import connection
from database.connection import init_db, session_scope
from database.enums import CategoriaPrincipal as Cat
from database.enums import NaturalezaSaldo as Nat
from database.enums import Subcategoria as Sub
from database.enums import TipoEstadoFinanciero as Tipo
from database.repositories import (
    create_account,
    get_account_by_codigo,
    get_company,
    get_or_create_fiscal_period,
    save_company,
    upsert_entry,
)
from database.seed import seed_default_accounts
from reports.excel_export import export_balance_excel, export_dupont_excel, export_income_excel, export_vertical_excel

PELIGROSOS = [
    '=HYPERLINK("http://ejemplo.invalid","clic")',
    "=1+1",
    "+1+1",
    "-1+1",
    "@SUM(A1:A2)",
    "=cmd|' /C calc'!A0",
    "\t=1+1",
    "\r=1+1",
]
ESPECIALES = [
    "  Caja chica  ",
    "Línea 1\nLínea 2",
    "Ñandú & <b>€</b> 'x' \"y\" ; , | % $",
    "",
    "1001",
    "-",
    "=",
]
# Unicas formulas que genera la aplicacion (columnas D, E y F).
FORMULA_LEGITIMA = re.compile(r"^=(SUM\(C\d+:C\d+\)|0|-?C\d+([+-]C\d+)*|C\d+-D\d+|-?C\d+/\$C\$\d+\*100)$")


def _guardar_y_leer(wb):
    datos = io.BytesIO()
    wb.save(datos)
    return datos.getvalue(), load_workbook(io.BytesIO(datos.getvalue()))


@pytest.mark.parametrize("valor", PELIGROSOS + ESPECIALES)
def test_texto_se_guarda_como_cadena_literal(valor):
    wb = Workbook()
    texto(wb.active, 1, 1, valor)
    escribir(wb.active, 2, 1, valor)
    crudo, leido = _guardar_y_leer(wb)
    for fila in (1, 2):
        celda = leido.active.cell(fila, 1)
        if valor == "":
            assert celda.value is None  # openpyxl no guarda cadenas vacias
            continue
        # XML normaliza un retorno de carro a salto de linea al leer.
        assert celda.value == valor.replace("\r", "\n")
        assert celda.data_type == "s"
        assert celda.quotePrefix is bool(valor.startswith(("=", "+", "-", "@", "\t", "\r")))
    assert b"<f>" not in zipfile.ZipFile(io.BytesIO(crudo)).read("xl/worksheets/sheet1.xml")


def test_caracteres_de_control_no_admitidos_se_eliminan():
    wb = Workbook()
    texto(wb.active, 1, 1, "=A\x01B\x1fC")
    _, leido = _guardar_y_leer(wb)
    celda = leido.active["A1"]
    assert celda.value == "=ABC" and celda.data_type == "s"


def test_escribir_conserva_numeros_y_vacios():
    wb = Workbook()
    ws = wb.active
    escribir(ws, 1, 1, 1234.56)
    escribir(ws, 2, 1, -7)
    escribir(ws, 3, 1, None)
    _, leido = _guardar_y_leer(wb)
    assert [leido.active.cell(f, 1).value for f in (1, 2, 3)] == [1234.56, -7, None]
    assert leido.active["A1"].data_type == "n"


def test_formula_solo_admite_formulas():
    wb = Workbook()
    assert formula(wb.active, 1, 1, "=SUM(C1:C2)").data_type == "f"
    with pytest.raises(ValueError):
        formula(wb.active, 1, 1, "SUM(C1:C2)")


def test_agregar_fila_equivale_a_append_con_texto_literal():
    wb = Workbook()
    ws = wb.active
    assert agregar_fila(ws, ["Código", "Nombre"]) == 1
    assert agregar_fila(ws, ["=1+1", 5]) == 2
    assert ws["A2"].data_type == "s" and ws["A2"].value == "=1+1" and ws["B2"].value == 5


# ------------------------------------------------------- reportes completos

NOMBRE_EMPRESA = '=HYPERLINK("http://ejemplo.invalid","Alutech")'
CUENTAS = {  # codigo nuevo -> (nombre, categoria, subcategoria, naturaleza, tipo)
    "1901": ("=1+1", Cat.ACTIVO, Sub.CORRIENTE, Nat.DEUDORA, Tipo.BALANCE),
    "1902": ("+SUM(C1:C9)", Cat.ACTIVO, Sub.NO_CORRIENTE, Nat.DEUDORA, Tipo.BALANCE),
    "2901": ("-2+3", Cat.PASIVO, Sub.CORRIENTE, Nat.ACREEDORA, Tipo.BALANCE),
    "3901": ("@SUM(A1)", Cat.PATRIMONIO, Sub.OTRAS_PATRIMONIALES, Nat.ACREEDORA, Tipo.BALANCE),
    "4901": ("Ventas\ncon salto", Cat.INGRESOS, None, Nat.ACREEDORA, Tipo.RESULTADOS),
    "5901": ("  Costo & <ñ>  ", Cat.COSTOS, None, Nat.DEUDORA, Tipo.RESULTADOS),
}


def _crear_bd(ruta, malicioso: bool):
    init_db(db_path=ruta)
    with session_scope() as s:
        seed_default_accounts(s)
        save_company(s, nombre_legal=NOMBRE_EMPRESA if malicioso else "Empresa", nombre_comercial="x",
                     actividad_economica="x", pais="SV", moneda="=USD" if malicioso else "USD", anio_inicial_analisis=2021)
        for codigo, (nombre, cat, sub, nat, _) in CUENTAS.items():
            create_account(s, codigo=codigo, nombre=nombre if malicioso else f"Cuenta {codigo}", categoria_principal=cat,
                           subcategoria=sub, naturaleza_saldo=nat)
    with session_scope() as s:
        for anio in (2021, 2022):
            p, _ = get_or_create_fiscal_period(s, anio)
            for codigo, valor in (("1001", 500), ("1901", 300), ("1902", 200), ("2901", 400), ("3901", 600),
                                  ("4901", 1000), ("5901", 400)):
                tipo = CUENTAS.get(codigo, (None, None, None, None, Tipo.BALANCE))[4]
                upsert_entry(s, fiscal_period_id=p.id, account_id=get_account_by_codigo(s, codigo).id, valor=str(valor),
                             tipo=tipo)


def _exportar(ruta, malicioso: bool) -> dict[str, bytes]:
    _crear_bd(ruta, malicioso)
    try:
        with session_scope() as s:
            c = get_company(s)
            p, _ = get_or_create_fiscal_period(s, 2022)
            bs, inc = compute_balance_sheet(s, p.id), compute_income_statement(s, p.id)
            vb, vi = compute_vertical_balance(s, p.id), compute_vertical_income(s, p.id)
            df = pd.DataFrame([{"Código": l.codigo, "Cuenta": l.etiqueta, "Valor": float(l.valor),
                                "Participación %": float(l.porcentaje)} for l in vb.lineas if l.tipo == "cuenta"])
            return {
                "balance": export_balance_excel(c, p, bs),
                "resultados": export_income_excel(c, p, inc),
                "vertical_balance": export_vertical_excel(c, p, "Vertical", None, vb.base_total_activo, "Total Activo",
                                                          lineas=vb.lineas),
                "vertical_resultados": export_vertical_excel(c, p, "Vertical", None, vi.base_ingresos_netos,
                                                             "Ingresos netos", lineas=vi.lineas),
                "vertical_df": export_vertical_excel(c, p, "Vertical", df, vb.base_total_activo, "Total Activo"),
                "dupont": export_dupont_excel(c, p, compute_dupont(s, p)),
            }
    finally:
        connection.dispose_engine()


@pytest.fixture(scope="module")
def libros(tmp_path_factory):
    d = tmp_path_factory.mktemp("b10")
    return _exportar(d / "maliciosa.db", True), _exportar(d / "normal.db", False)


def _celdas(datos):
    hoja = load_workbook(io.BytesIO(datos)).active
    return {(c.row, c.column): c for fila in hoja.iter_rows() for c in fila if c.value is not None}


@pytest.mark.parametrize("reporte", ["balance", "resultados", "vertical_balance", "vertical_resultados", "vertical_df", "dupont"])
def test_reportes_exportan_los_textos_del_usuario_como_texto(libros, reporte):
    celdas = _celdas(libros[0][reporte])
    textos_usuario = {NOMBRE_EMPRESA} | {n for n, *_ in CUENTAS.values()}
    for celda in celdas.values():
        if celda.data_type == "f":
            # Toda formula es de control: columnas D-F y con la forma esperada.
            assert celda.column in (4, 5, 6) and FORMULA_LEGITIMA.match(celda.value), (celda.coordinate, celda.value)
        if celda.value in textos_usuario:
            assert celda.data_type == "s", (celda.coordinate, celda.value)
    assert celdas[(1, 1)].value == NOMBRE_EMPRESA and celdas[(1, 1)].data_type == "s" and celdas[(1, 1)].quotePrefix
    escritos = {c.value for c in celdas.values() if c.data_type == "s"}
    if reporte != "dupont":  # el DuPont no lista cuentas
        esperados = {n for n, cat, *_ in CUENTAS.values()
                     if (cat in (Cat.ACTIVO, Cat.PASIVO, Cat.PATRIMONIO)) == reporte.endswith(("balance", "df"))}
        if reporte == "vertical_df":
            esperados = {n for n, cat, *_ in CUENTAS.values() if cat == Cat.ACTIVO or cat in (Cat.PASIVO, Cat.PATRIMONIO)}
        assert esperados <= escritos


@pytest.mark.parametrize("reporte", ["balance", "resultados", "vertical_balance", "vertical_resultados", "vertical_df", "dupont"])
def test_formulas_e_importes_no_cambian_por_los_textos(libros, reporte):
    """Mismos datos con nombres normales y con nombres peligrosos: las
    formulas de control y todos los numeros son identicos."""
    malicioso, normal = (_celdas(libros[i][reporte]) for i in (0, 1))
    formulas_m = {k: c.value for k, c in malicioso.items() if c.data_type == "f"}
    formulas_n = {k: c.value for k, c in normal.items() if c.data_type == "f"}
    assert formulas_m == formulas_n
    if reporte not in ("dupont",):
        assert formulas_m, "el reporte debe conservar sus fórmulas de control"
    numeros_m = {k: c.value for k, c in malicioso.items() if c.data_type == "n"}
    numeros_n = {k: c.value for k, c in normal.items() if c.data_type == "n"}
    assert numeros_m == numeros_n and numeros_m


def test_importes_del_balance_exportado(libros):
    celdas = _celdas(libros[0]["balance"])
    por_etiqueta = {celdas[(f, 2)].value: celdas.get((f, 3)) for f, c in celdas if c == 2 and (f, 2) in celdas}
    assert por_etiqueta["=1+1"].value == 300.0
    assert por_etiqueta["TOTAL ACTIVO"].value == 1000.0
    assert por_etiqueta["TOTAL PASIVO"].value == 400.0


def test_xml_de_los_reportes_no_tiene_formulas_con_datos_del_usuario(libros):
    for reporte, datos in libros[0].items():
        xml = zipfile.ZipFile(io.BytesIO(datos)).read("xl/worksheets/sheet1.xml").decode("utf-8")
        for f in re.findall(r"<f>(.*?)</f>", xml):
            assert FORMULA_LEGITIMA.match(f"={f}".replace("&amp;", "&")), (reporte, f)
        assert "HYPERLINK" in xml and "<f>HYPERLINK" not in xml


def test_plantilla_de_importacion_escribe_los_nombres_como_texto(tmp_path):
    from database.enums import BALANCE_CATEGORIAS
    from modules.excel_import import COLUMNAS, _generar_plantilla

    init_db(db_path=tmp_path / "plantilla.db")
    try:
        with session_scope() as s:
            seed_default_accounts(s)
            for codigo, (nombre, cat, sub, nat, _) in CUENTAS.items():
                create_account(s, codigo=codigo, nombre=nombre, categoria_principal=cat, subcategoria=sub,
                               naturaleza_saldo=nat)
        with session_scope() as s:
            datos = _generar_plantilla(s, BALANCE_CATEGORIAS)
    finally:
        connection.dispose_engine()
    hoja = load_workbook(io.BytesIO(datos))["Plantilla"]
    assert [c.value for c in hoja[1]] == COLUMNAS
    filas = {f[0].value: f[1] for f in hoja.iter_rows(min_row=2)}
    for codigo in ("1901", "1902", "2901", "3901"):
        assert filas[codigo].value == CUENTAS[codigo][0] and filas[codigo].data_type == "s"
    assert not any(c.data_type == "f" for fila in hoja.iter_rows() for c in fila)
    # La plantilla generada se sigue leyendo con los mismos nombres.
    leida = pd.read_excel(io.BytesIO(datos))
    assert leida.loc[leida["Código de cuenta"] == 1901, "Nombre de cuenta"].item() == "=1+1"
