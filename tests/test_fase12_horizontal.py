"""Correcciones autorizadas R-6, R-7, R-8, R-9 y R-16 del analisis horizontal.

Comprueba que cada celda sin valor diga su causa, la nota de la utilidad operativa, los avisos de
integridad sin corregir datos, el formato de los ceros y los metadatos de los auditores.
"""
from __future__ import annotations

import hashlib
import io
import json
import shutil
import sqlite3
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest
from openpyxl import load_workbook

from calculations.comparativo import NO_CALCULABLE, SIN_COMPARAR, SIN_DATO, FilaHorizontal, dos_ejercicios, horizontal_de_estado
from calculations.rubros import datos_todos
from components.secciones_ui import a_dataframe
from database.connection import init_db, session_scope
from reports import secciones as sec
from reports.exportar_secciones import secciones_a_excel, secciones_a_pdf
from scripts.cargar_alutech import cargar
from test_fase8_vertical_dupont import _guardar_empresa

PROYECTO = Path(__file__).resolve().parent.parent
FUENTE = PROYECTO / "fuentes" / "alutech" / "estados_financieros_2021_2025.json"
EMPRESA = SimpleNamespace(nombre_legal="Empresa", moneda="USD")
# Huella de los importes y las cuentas, tomada antes de corregir los metadatos.
HUELLA_IMPORTES = "6b3f85bc9aeee329bb8817adc75aa7b5c9355b86759791eb0b3674b0fe26a09f"


@pytest.fixture(scope="module")
def ruta_bd(tmp_path_factory):
    ruta = tmp_path_factory.mktemp("fase12") / "financiera.db"
    cargar(db_path=ruta, respaldar=False)
    init_db(db_path=ruta)
    with session_scope() as s:
        _guardar_empresa(s)
    return ruta


def _lista(ruta):
    init_db(db_path=ruta)
    with session_scope() as s:
        return [d for d in datos_todos(s) if d.tiene_datos]


@pytest.fixture
def lista(ruta_bd):
    return _lista(ruta_bd)


def _df(lista, anio, estado, nivel):
    return a_dataframe(sec.horizontal_dos_ejercicios(lista, anio, anio - 1, estado, nivel)).set_index("Partida")


def _editar(ruta, tmp_path, sql, *args):
    copia = tmp_path / "editada.db"
    shutil.copy2(ruta, copia)
    conexion = sqlite3.connect(copia)
    assert conexion.execute(sql, args).rowcount == 1
    conexion.commit()
    conexion.close()
    return copia


SALDO_BALANCE = ("update balance_entry set valor=? where fiscal_period_id=(select id from fiscal_period where anio=?) "
                 "and account_id=(select id from account where codigo=?)")


# ------------------------------------------------------------------- R-6
def test_partida_no_presentada_dice_sin_dato(lista):
    fila = _df(lista, 2024, "BG", "grupos").loc["Pasivos por beneficios post empleo"]
    assert fila["Saldo actual (2024)"] == SIN_DATO and fila["Variación absoluta"] == SIN_DATO and fila["Variación relativa"] == SIN_DATO
    assert fila["Saldo anterior (2023)"] == "932,485"


def test_base_negativa_dice_no_calculable_y_conserva_la_absoluta(lista):
    fila = _df(lista, 2025, "BG", "grupos").loc["Efecto de conversión de entidades extranjeras"]
    assert fila["Variación relativa"] == NO_CALCULABLE and fila["Variación absoluta"] == "-8,003,019"


def test_base_cero_dice_no_calculable(ruta_bd, tmp_path):
    lista = _lista(_editar(ruta_bd, tmp_path, SALDO_BALANCE, 0, 2022, "CB1107"))
    fila = _df(lista, 2023, "BG", "grupos").loc["Inventarios"]
    assert fila["Variación relativa"] == NO_CALCULABLE and fila["Variación absoluta"] == "+141,491,319"


@pytest.mark.parametrize("partida, saldo_actual", [("Cuentas por pagar comerciales", SIN_DATO), ("Activos intangibles", "38,005,433")])
def test_presentacion_cambiada_dice_no_comparable(lista, partida, saldo_actual):
    fila = _df(lista, 2024, "BG", "grupos").loc[partida]
    assert fila["Variación absoluta"] == SIN_COMPARAR and fila["Variación relativa"] == SIN_COMPARAR
    assert fila["Saldo actual (2024)"] == saldo_actual


def test_rubro_no_comparable_y_las_tablas_conservan_sus_cifras(lista):
    fila = _df(lista, 2024, "BG", "rubros").loc["Cuentas por cobrar comerciales (línea presentada)"]
    assert fila["Variación relativa"] == SIN_COMPARAR
    for seccion in sec.horizontal_balance_tablas(lista) + [sec.horizontal_resultados_tabla(lista), sec.capital_trabajo(lista), sec.capital_trabajo_interanual(lista)]:
        for f in a_dataframe(seccion).values.tolist():
            assert not {SIN_DATO, NO_CALCULABLE, SIN_COMPARAR, "—"} & set(f), f


def test_ejercicio_faltante_dice_sin_dato_en_las_tablas(ruta_bd, tmp_path):
    copia = tmp_path / "sin_2022.db"
    shutil.copy2(ruta_bd, copia)
    conexion = sqlite3.connect(copia)
    for tabla in ("balance_entry", "income_entry"):
        conexion.execute(f"delete from {tabla} where fiscal_period_id=(select id from fiscal_period where anio=2022)")
    conexion.commit()
    conexion.close()
    tabla_5 = a_dataframe(sec.horizontal_resultados_tabla(_lista(copia)))
    assert tabla_5["Var. rel. 21–23"].tolist() == [SIN_DATO] * 7


def test_las_causas_son_iguales_en_pantalla_excel_y_pdf(lista):
    pytest.importorskip("reportlab")
    seccion = sec.horizontal_dos_ejercicios(lista, 2024, 2023, "BG", "grupos")
    libro = load_workbook(io.BytesIO(secciones_a_excel(EMPRESA, "T", [("H", [seccion])])))
    filas = list(libro["H"].iter_rows(values_only=True))
    inicio = next(i for i, f in enumerate(filas) if f[0] == seccion.titulo) + 2
    for i, fila in enumerate(a_dataframe(seccion).itertuples(index=False)):
        for j in (1, 2, 3, 4):
            if isinstance(fila[j], str) and fila[j] in (SIN_DATO, NO_CALCULABLE, SIN_COMPARAR):
                assert filas[inicio + i][j] == fila[j]
    assert secciones_a_pdf(EMPRESA, "T", [seccion]).startswith(b"%PDF")


# ------------------------------------------------------------------- R-7
def test_tabla_5_advierte_la_utilidad_operativa_sin_cambiar_cifras(lista):
    seccion = sec.horizontal_resultados_tabla(lista)
    df = a_dataframe(seccion).set_index("Rubro del estado de resultados")
    assert "Utilidad de operación †" in df.index
    fila = df.loc["Utilidad de operación †"]
    assert fila["Var. rel. 23–24"] == "-21.25%" and fila["Var. abs. 23–24"] == "-9,495,103" and fila["Var. rel. 24–25"] == "+55.33%"
    nota = next(n for n in seccion.notas if n.startswith("† Utilidad de operación"))
    assert "2023–2024" in nota and "otros ingresos netos" in nota and "deterioro" in nota and "no es plenamente comparable" in nota


def test_la_advertencia_solo_afecta_al_par_con_el_cambio(lista):
    assert "plenamente comparable" in _df(lista, 2024, "ER", "rubros").loc["Utilidad de operación"]["Observación"]
    for anio in (2022, 2023, 2025):
        assert "plenamente comparable" not in _df(lista, anio, "ER", "rubros").loc["Utilidad de operación"]["Observación"]


def test_nota_de_utilidad_operativa_coherente_con_el_documento():
    texto = (PROYECTO / "Trabajo de investigación ANF.md").read_text(encoding="utf-8")
    assert "la variación de 2023–2024 (−21.25%) no es plenamente comparable" in texto


# ------------------------------------------------------------------- R-8
def test_con_los_datos_reales_no_hay_avisos(lista):
    assert sec.integridad(lista) is None


def test_balance_descuadrado_muestra_la_diferencia_y_no_corrige(ruta_bd, tmp_path):
    copia = _editar(ruta_bd, tmp_path, SALDO_BALANCE, (141069442 + 1000000) * 100, 2022, "CB1107")
    lista = _lista(copia)
    seccion = sec.integridad(lista)
    assert len(seccion.filas) == 1
    fila = seccion.filas[0]
    assert fila[0] == "2022" and fila[1] == "Balance General" and fila[3] == Decimal("1000000")
    assert "673,025,093" in fila[2] and "672,025,093" in fila[2]
    assert next(d for d in lista if d.anio == 2022).g("INVENTARIOS") == Decimal("142069442")  # el dato sigue como esta registrado


def test_estado_incompleto_indica_lo_que_falta(ruta_bd, tmp_path):
    copia = tmp_path / "incompleta.db"
    shutil.copy2(ruta_bd, copia)
    conexion = sqlite3.connect(copia)
    conexion.execute("delete from balance_entry where fiscal_period_id=(select id from fiscal_period where anio=2025) and account_id in "
                     "(select id from account where categoria_principal='PATRIMONIO')")
    conexion.execute("delete from income_entry where fiscal_period_id=(select id from fiscal_period where anio=2025) and account_id in "
                     "(select id from account where categoria_principal='COSTOS')")
    conexion.commit()
    conexion.close()
    lista = _lista(copia)
    problemas = {(f[1], f[2].split(":")[0]) for f in sec.integridad(lista).filas}
    assert ("Balance General", "Incompleto") in problemas and ("Balance General", "Descuadrado") in problemas
    assert ("Estado de Resultados", "Incompleto") in problemas
    assert {f[1] for f in sec.integridad(lista, "ER").filas} == {"Estado de Resultados"}


def test_pagina_y_descarga_muestran_el_aviso(ruta_bd, tmp_path):
    copia = _editar(ruta_bd, tmp_path, SALDO_BALANCE, (141069442 + 1000000) * 100, 2022, "CB1107")
    proceso = subprocess.run([sys.executable, str(PROYECTO / "tests" / "humo_integridad.py"), str(copia)],
                             capture_output=True, text=True, encoding="utf-8", timeout=280, cwd=str(PROYECTO))
    assert proceso.returncode == 0, proceso.stderr[-1500:]
    datos = json.loads(proceso.stdout.strip().splitlines()[-1])
    assert any("2022" in a and "Descuadrado" in a and "1,000,000" in a for a in datos["balance"]["avisos"])
    assert datos["balance"]["hojas"][0] == "Avisos de integridad"
    assert datos["resultados"]["avisos"] == [] and datos["resultados"]["hojas"][0] == "Estado de resultados"


# ------------------------------------------------------------------- R-9
def _fila(actual, anterior):
    return dos_ejercicios([FilaHorizontal("x", "x", "cuenta", {2001: Decimal(actual), 2000: Decimal(anterior)})], 2001, 2000)[0]


def test_saldo_sin_cambio_no_lleva_signo():
    fila = _fila("100", "100")
    assert sec.formatear(fila.var_abs, sec.VAR_USD) == "0" and sec.formatear(fila.var_pct, sec.VAR_PCT) == "0.00%"


def test_cambio_real_diminuto_conserva_su_signo():
    assert sec.formatear(Decimal("2000"), sec.VAR_USD) == "+2,000"
    assert sec.formatear(Decimal("0.0016"), sec.VAR_PCT) == "+0.00%" and sec.formatear(Decimal("-0.0016"), sec.VAR_PCT) == "-0.00%"


def test_excel_conserva_el_valor_y_muestra_lo_mismo_que_la_pantalla(lista):
    seccion = sec.horizontal_dos_ejercicios(lista, 2023, 2022, "BG", "grupos")
    fila_df = a_dataframe(seccion).set_index("Partida").loc["Certificados de depósito a plazo (no corrientes)"]
    assert fila_df["Variación absoluta"] == "0" and fila_df["Variación relativa"] == "0.00%"
    libro = load_workbook(io.BytesIO(secciones_a_excel(EMPRESA, "T", [("H", [seccion])])))
    celdas = next(f for f in libro["H"].iter_rows() if f[0].value == "Certificados de depósito a plazo (no corrientes)")
    assert celdas[3].value == 0 and celdas[3].number_format == "+#,##0;-#,##0;0"
    assert celdas[4].value == 0 and celdas[4].number_format == '+0.00"%";-0.00"%";0.00"%"'


def test_celda_vacia_en_excel_muestra_la_raya_de_la_pantalla():
    seccion = sec.Seccion("T", [sec.Columna("A"), sec.Columna("B", sec.USD)], filas=[["x", None]])
    libro = load_workbook(io.BytesIO(secciones_a_excel(EMPRESA, "T", [("H", [seccion])])))
    assert next(f for f in libro["H"].iter_rows(values_only=True) if f[0] == "x")[1] == "—"


# ------------------------------------------------------------------ R-16
def test_metadatos_de_auditores():
    datos = json.loads(FUENTE.read_text(encoding="utf-8"))["documentos"]
    assert "PricewaterhouseCoopers Honduras" in datos["CERT_2021"]["descripcion"]
    for clave, firma in (("CERT_2022", "KPMG, S. de R.L."), ("CERT_2023", "KPMG, Ltda de C.V.")):
        assert firma in datos[clave]["descripcion"] and "PwC" not in datos[clave]["descripcion"]


def test_la_correccion_no_toco_ningun_importe():
    datos = json.loads(FUENTE.read_text(encoding="utf-8"))
    contenido = json.dumps({"cuentas": datos["cuentas"], "ejercicios": datos["ejercicios"]}, ensure_ascii=False, sort_keys=True)
    assert hashlib.sha256(contenido.encode("utf-8")).hexdigest() == HUELLA_IMPORTES
