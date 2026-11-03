"""Fase 5.2: flujo completo sobre una BD temporal.

empresa -> catalogo -> importar 2020-2025 (plantillas de la aplicacion)
-> reportes en pantalla (25 paginas, AppTest en subproceso) -> exportar
PDF y Excel -> respaldo -> cambio posterior -> restaurar.

Datos sinteticos generados por la prueba (no son datos de Alutech). Las
cifras exactas se verifican en test_fase5_controlado.py; aqui se
comprueba que el flujo funciona sin excepciones, que los estados quedan
cuadrados y conciliados, y que la restauracion devuelve exactamente la
BD respaldada.
"""
import io
import json
import sqlite3
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest
import streamlit
from openpyxl import Workbook, load_workbook

from calculations.balance_sheet import compute_balance_sheet
from calculations.banderas import banderas_balance, banderas_dupont, banderas_resultados, resumen
from calculations.controls import CONCILIADO, conciliar_resultado
from calculations.dupont import compute_dupont
from calculations.income_statement import compute_income_statement
from calculations.vertical_analysis import compute_vertical_balance, compute_vertical_income
from database import connection
from database.backup_utils import crear_respaldo, restaurar, sha256_archivo
from database.connection import init_db, render_scope, session_scope
from database.enums import BALANCE_CATEGORIAS, RESULTADOS_CATEGORIAS
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
    list_fiscal_periods,
    upsert_entry,
)
from database.seed import seed_default_accounts
from reports.excel_export import export_balance_excel, export_dupont_excel, export_income_excel, export_vertical_excel
from reports.pdf_export import export_balance_pdf, export_dupont_pdf, export_income_pdf, export_vertical_pdf

PROYECTO = Path(__file__).resolve().parent.parent
ANIOS = list(range(2020, 2026))
EMPRESA = {"Nombre de la empresa": "Integración Sintética, S. A.", "Nombre comercial": "IS",
           "Actividad económica": "Pruebas", "País": "El Salvador", "Moneda de presentación (ej. GTQ, USD)": "usd"}
CUENTA_NUEVA = ("1005", "Inversiones temporales")


def _datos(i: int) -> tuple[dict[str, Decimal], dict[str, Decimal]]:
    """Estados sinteticos coherentes del ejercicio 2020 + i (convencion de
    signos aprobada; el Balance cuadra y el resultado concilia)."""
    ingresos = Decimal(10000 + 1000 * i)
    costo = ingresos * Decimal("0.6")
    uai = ingresos - costo - Decimal(1500) - Decimal(500) - Decimal(200)
    isr = (uai * Decimal("0.25")).quantize(Decimal("0.01"))
    un = uai - isr
    resultados = {"4001": ingresos, "5001": costo, "6001": Decimal(1500), "6002": Decimal(500), "7002": Decimal(200),
                  "8001": isr}
    acumulados = Decimal(1000) + sum((_datos(j)[0]["3004"] for j in range(i)), Decimal(0))
    balance = {"1005": Decimal(100), "1101": Decimal(8000), "1102": Decimal(-1000) - 100 * i,
               "2001": Decimal(3000), "2101": Decimal(4000),
               "3001": Decimal(5000), "3003": acumulados, "3004": un}
    pasivo_patrimonio = sum(balance[c] for c in ("2001", "2101", "3001", "3003", "3004"))
    balance["1001"] = pasivo_patrimonio - sum(balance[c] for c in ("1005", "1101", "1102"))
    return balance, resultados


def _archivo_importacion(plantilla: bytes, tipo: str) -> io.BytesIO:
    """Rellena la plantilla descargada de la aplicacion: una fila por cuenta
    con dato y ejercicio (las cuentas sin dato quedan fuera)."""
    cuentas = pd.read_excel(io.BytesIO(plantilla), sheet_name="Plantilla", dtype={"Código de cuenta": str})
    wb = Workbook()
    ws = wb.active
    ws.append(list(cuentas.columns))
    for i, anio in enumerate(ANIOS):
        valores = _datos(i)[0 if tipo == "balance" else 1]
        for _, fila in cuentas.iterrows():
            if fila["Código de cuenta"] in valores:
                ws.append([fila["Código de cuenta"], fila["Nombre de cuenta"], fila["Categoría"], fila["Subcategoría"],
                           anio, float(valores[fila["Código de cuenta"]])])
    datos = io.BytesIO()
    wb.save(datos)
    datos.seek(0)
    return datos


def _volcado(ruta: Path) -> dict:
    con = sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)
    tablas = [r[0] for r in con.execute("select name from sqlite_master where type='table' order by name")]
    datos = {t: con.execute(f'select * from "{t}" order by rowid').fetchall() for t in tablas}
    datos["user_version"] = con.execute("pragma user_version").fetchone()
    con.close()
    return datos


@pytest.fixture(scope="module")
def flujo(tmp_path_factory):
    from modules import company, excel_import

    raiz = tmp_path_factory.mktemp("integracion")
    ruta = raiz / "financiera.db"
    r = {"ruta": ruta}
    init_db(db_path=ruta)
    with session_scope() as s:
        seed_default_accounts(s)

    with pytest.MonkeyPatch.context() as mp:
        # 1. Empresa, con la pantalla real (formulario simulado).
        mp.setattr(streamlit, "text_input", lambda label, *a, **k: EMPRESA[label])
        mp.setattr(streamlit, "number_input", lambda *a, **k: 2020)
        mp.setattr(streamlit, "form_submit_button", lambda *a, **k: True)
        mp.setattr(streamlit, "rerun", lambda *a, **k: None)
        with render_scope() as s:
            company.render(s)

        # 2. Catalogo: una cuenta nueva ademas del catalogo estandar.
        with session_scope() as s:
            create_account(s, codigo=CUENTA_NUEVA[0], nombre=CUENTA_NUEVA[1], categoria_principal=Cat.ACTIVO,
                           subcategoria=Sub.CORRIENTE, naturaleza_saldo=Nat.DEUDORA)

        # 3. Importar 2020-2025 con las plantillas de la aplicacion.
        with session_scope() as s:
            plantillas = {"balance": excel_import._generar_plantilla(s, BALANCE_CATEGORIAS),
                          "resultados": excel_import._generar_plantilla(s, RESULTADOS_CATEGORIAS)}
        mp.setattr(streamlit, "checkbox", lambda *a, **k: False)
        mp.setattr(streamlit, "button", lambda label, *a, **k: label == "Confirmar importación")
        exitos = []
        mp.setattr(streamlit, "success", lambda m, *a, **k: exitos.append(m))
        for tipo, plantilla in plantillas.items():
            archivo = _archivo_importacion(plantilla, tipo)
            mp.setattr(streamlit, "file_uploader", lambda *a, _f=archivo, **k: _f)
            streamlit.session_state.clear()
            with render_scope() as s:
                excel_import.render(s, get_company(s))
        r["mensajes_importacion"] = exitos
    connection.dispose_engine()

    # 4. Reportes en pantalla: las 25 paginas del app.py real (subproceso).
    hash_antes_paginas = sha256_archivo(ruta)
    proceso = subprocess.run([sys.executable, str(PROYECTO / "tests" / "humo_paginas.py"), str(ruta)],
                             capture_output=True, text=True, encoding="utf-8", timeout=600)
    assert proceso.returncode == 0, proceso.stderr[-3000:]
    r["paginas"] = json.loads(proceso.stdout.strip().splitlines()[-1])
    r["paginas_sin_cambios"] = sha256_archivo(ruta) == hash_antes_paginas

    # 5. Exportar PDF y Excel de cada reporte y ejercicio.
    init_db(db_path=ruta)
    r["exportaciones"] = {}
    with session_scope() as s:
        c = get_company(s)
        for anio in ANIOS:
            p = get_fiscal_period(s, anio)
            bs, inc = compute_balance_sheet(s, p.id), compute_income_statement(s, p.id)
            vb, vi, dp = compute_vertical_balance(s, p.id), compute_vertical_income(s, p.id), compute_dupont(s, p)
            r["exportaciones"][anio] = {
                "pdf": [export_balance_pdf(c, p, bs), export_income_pdf(c, p, inc),
                        export_vertical_pdf(c, p, "Vertical", vb.lineas, vb.base_total_activo, "Total Activo"),
                        export_vertical_pdf(c, p, "Vertical", vi.lineas, vi.base_ingresos_netos, "Ingresos netos"),
                        export_dupont_pdf(c, p, dp)],
                "excel": [export_balance_excel(c, p, bs), export_income_excel(c, p, inc),
                          export_vertical_excel(c, p, "Vertical", None, vb.base_total_activo, "Total Activo", lineas=vb.lineas),
                          export_vertical_excel(c, p, "Vertical", None, vi.base_ingresos_netos, "Ingresos netos",
                                                lineas=vi.lineas),
                          export_dupont_excel(c, p, dp)],
            }
    connection.dispose_engine()

    # 6. Respaldo, cambio posterior y restauracion.
    copia = crear_respaldo(ruta, raiz / "backups" / "financiera_integracion.db")
    r["volcado_respaldo"] = _volcado(copia)
    r["hash_copia"] = sha256_archivo(copia)
    init_db(db_path=ruta)
    with session_scope() as s:
        upsert_entry(s, fiscal_period_id=get_fiscal_period(s, 2025).id, account_id=get_account_by_codigo(s, "1003").id,
                     valor="777", tipo=Tipo.BALANCE)
    connection.dispose_engine()
    r["hash_antes_restaurar"] = sha256_archivo(ruta)
    r["restauracion"] = restaurar(copia, ruta, dir_respaldos=raiz / "backups")
    r["hash_restaurada"] = sha256_archivo(ruta)
    r["volcado_restaurada"] = _volcado(ruta)
    r["hash_copia_despues"] = sha256_archivo(copia)
    init_db(db_path=ruta)
    yield r
    connection.dispose_engine()


def test_empresa_y_catalogo(flujo):
    with session_scope() as s:
        c = get_company(s)
        assert (c.nombre_legal, c.pais, c.moneda, c.anio_inicial_analisis) == (
            "Integración Sintética, S. A.", "El Salvador", "USD", 2020)
        assert get_account_by_codigo(s, CUENTA_NUEVA[0]).nombre == CUENTA_NUEVA[1]


def test_importacion_de_los_seis_ejercicios(flujo):
    assert len(flujo["mensajes_importacion"]) == 2
    assert all("0 fila(s) con observaciones" in m for m in flujo["mensajes_importacion"]), flujo["mensajes_importacion"]
    with session_scope() as s:
        assert [p.anio for p in list_fiscal_periods(s)] == ANIOS
        for i, anio in enumerate(ANIOS):
            p = get_fiscal_period(s, anio)
            balance, resultados = _datos(i)
            for tipo, esperado in ((Tipo.BALANCE, balance), (Tipo.RESULTADOS, resultados)):
                guardado = {get_account_by_codigo(s, c).id: v for c, v in esperado.items()}
                assert get_entries_map(s, p.id, tipo) == {k: v.quantize(Decimal("0.01")) for k, v in guardado.items()}


@pytest.mark.parametrize("anio", ANIOS)
def test_estados_cuadrados_conciliados_y_con_estado_correcto(flujo, anio):
    with session_scope() as s:
        p = get_fiscal_period(s, anio)
        bs, inc = compute_balance_sheet(s, p.id), compute_income_statement(s, p.id)
        conciliacion = conciliar_resultado(bs, inc)
        dp = compute_dupont(s, p)
    assert bs.cuadra and bs.completo and inc.completo and conciliacion.estado == CONCILIADO
    assert resumen(banderas_balance(bs, conciliacion)) == "DEFINITIVO"
    assert resumen(banderas_resultados(inc, conciliacion)) == "DEFINITIVO"
    # 2020 es el primer ejercicio: sin Balance anterior ni saldos manuales, el ROE es APROXIMADO.
    assert dp.saldos_aproximados is (anio == 2020)
    assert resumen(banderas_dupont(dp)) == ("APROXIMADO" if anio == 2020 else "DEFINITIVO")
    if anio > 2020:
        assert dp.fuente_saldos_iniciales == f"Balance final del ejercicio {anio - 1}"


def test_las_16_paginas_se_renderizan_sin_modificar_la_bd(flujo):
    paginas = flujo["paginas"]
    # 16 paginas originales + 8 del analisis 2021-2025 + "Ingreso de datos" del menu simplificado.
    paginas = {k: v for k, v in paginas.items() if k != "_menu"}
    assert len(paginas) == 25
    for etiqueta, resultado in paginas.items():
        assert resultado["pagina"] == etiqueta and not resultado["excepciones"], (etiqueta, resultado["excepciones"])
    assert flujo["paginas_sin_cambios"]


@pytest.mark.parametrize("anio", ANIOS)
def test_exportaciones_pdf_y_excel(flujo, anio):
    exportado = flujo["exportaciones"][anio]
    assert all(d.startswith(b"%PDF") and len(d) > 1000 for d in exportado["pdf"])
    for datos in exportado["excel"]:
        hoja = load_workbook(io.BytesIO(datos)).active
        assert hoja["A1"].value == "Integración Sintética, S. A."
        assert f"Ejercicio fiscal: {anio}" in hoja["A3"].value
        assert hoja["A6"].value.startswith("Estado del reporte: ")


def test_restauracion_devuelve_exactamente_la_bd_respaldada(flujo):
    assert flujo["hash_antes_restaurar"] != flujo["hash_copia"]  # hubo un cambio despues del respaldo
    assert flujo["volcado_restaurada"] == flujo["volcado_respaldo"]
    assert flujo["hash_restaurada"] == flujo["hash_copia"]
    assert flujo["hash_copia_despues"] == flujo["hash_copia"]  # la copia no se altera al restaurar
    previo = flujo["restauracion"].respaldo_previo
    assert previo is not None and sha256_archivo(previo) == flujo["hash_antes_restaurar"]
    with session_scope() as s:
        p = get_fiscal_period(s, 2025)
        assert get_account_by_codigo(s, "1003").id not in get_entries_map(s, p.id, Tipo.BALANCE)
