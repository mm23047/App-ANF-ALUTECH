"""Prueba de humo: cada pagina del app.py real se renderiza sin excepciones
y sin modificar la BD (render_scope nunca confirma; hallazgo M-06).

AppTest se ejecuta en un subproceso (tests/humo_paginas.py): en el mismo
proceso, las pruebas que usan st.form sin servidor dejan estado global de
Streamlit y AppTest deja de navegar, con lo que la prueba aprobaria sin
haber renderizado la pagina.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from components.navigation import PAGINAS
from database import connection
from database.backup_utils import sha256_archivo
from database.connection import init_db, session_scope
from database.enums import TipoEstadoFinanciero as Tipo
from database.repositories import (
    close_fiscal_period,
    get_account_by_codigo,
    get_or_create_fiscal_period,
    save_company,
    upsert_entry,
)
from database.seed import seed_default_accounts

HUMO = Path(__file__).resolve().parent / "humo_paginas.py"


@pytest.fixture(scope="module")
def resultado_humo(tmp_path_factory):
    ruta = tmp_path_factory.mktemp("humo") / "financiera.db"
    init_db(db_path=ruta)
    with session_scope() as s:
        seed_default_accounts(s)
        save_company(s, nombre_legal="Empresa Humo", nombre_comercial="EH", actividad_economica="x", pais="SV",
                     moneda="USD", anio_inicial_analisis=2021)
        for anio, cerrar in ((2021, True), (2022, False)):
            p, _ = get_or_create_fiscal_period(s, anio)
            for codigo, valor, tipo in (("1001", "1000", Tipo.BALANCE), ("2001", "400", Tipo.BALANCE),
                                        ("3001", "600", Tipo.BALANCE), ("4001", "1000", Tipo.RESULTADOS),
                                        ("8001", "900", Tipo.RESULTADOS)):
                upsert_entry(s, fiscal_period_id=p.id, account_id=get_account_by_codigo(s, codigo).id, valor=valor, tipo=tipo)
            if cerrar:
                close_fiscal_period(s, p.id)
    connection.dispose_engine()
    hash_antes = sha256_archivo(ruta)
    proceso = subprocess.run([sys.executable, str(HUMO), str(ruta)], capture_output=True, text=True,
                             encoding="utf-8", timeout=600)
    assert proceso.returncode == 0, proceso.stderr[-3000:]
    resultados = json.loads(proceso.stdout.strip().splitlines()[-1])
    return resultados, hash_antes == sha256_archivo(ruta)


def test_recorrer_las_paginas_no_modifica_la_bd(resultado_humo):
    _, bd_sin_cambios = resultado_humo
    assert bd_sin_cambios


@pytest.mark.parametrize("etiqueta", [etiqueta for etiqueta, _ in PAGINAS])
def test_pagina_se_renderiza_sin_errores(resultado_humo, etiqueta):
    resultado = resultado_humo[0][etiqueta]
    # La navegacion debe haber llegado a la pagina pedida.
    assert resultado["pagina"] == etiqueta
    if etiqueta != "Dashboard":
        assert resultado["encabezados"] != ["Dashboard"]
    assert not resultado["excepciones"], resultado["excepciones"]


@pytest.mark.parametrize("etiqueta, esperado", [
    # Ejercicio 2022 (el ultimo, seleccionado por defecto): activo 1000, pasivo 400, patrimonio 600.
    ("Reportes › Análisis Vertical del Balance General",
     {"1001": ("USD 1,000.00", "100.00%"), "2001": ("USD 400.00", "40.00%"), "3001": ("USD 600.00", "60.00%")}),
    # Ingresos 1000 (base); ISR 900.
    ("Reportes › Análisis Vertical del Estado de Resultados", {"8001": ("USD 900.00", "90.00%")}),
])
def test_paginas_verticales_muestran_importes_y_porcentajes(resultado_humo, etiqueta, esperado):
    """Hallazgo M-11: con importes distintos de cero la pagina se renderiza
    y muestra los valores calculados con Decimal."""
    tablas = resultado_humo[0][etiqueta]["tablas"]
    assert len(tablas) == 1
    filas = {f["Código"]: (f["Valor"], f["Participación %"]) for f in tablas[0]}
    assert filas == esperado
