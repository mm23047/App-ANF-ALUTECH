"""Abre con AppTest las paginas del analisis horizontal sobre una BD con datos inconsistentes y registra los
avisos en pantalla y las hojas que reciben las descargas. Se ejecuta en un subproceso desde
test_fase12_horizontal.py (razon: tests/humo_paginas.py).

Uso: python tests/humo_integridad.py RUTA_BD
"""
import json
import sys
from pathlib import Path

PROYECTO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROYECTO))

from database import connection  # noqa: E402

connection.DB_PATH = Path(sys.argv[1])  # antes de importar app.py: nunca la BD real

from streamlit.testing.v1 import AppTest  # noqa: E402

from components.navigation import CLAVE_PAGINA  # noqa: E402
from reports import analisis_alutech  # noqa: E402

registro = {}


def _descargas(company, titulo, hojas, archivo, *, clave):
    registro["hojas"] = [nombre for nombre, _ in hojas]


analisis_alutech.descargas = _descargas


def abrir(pagina: str) -> dict:
    registro.clear()
    at = AppTest.from_file(str(PROYECTO / "app.py"), default_timeout=180)
    at.session_state[CLAVE_PAGINA] = pagina
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    resultado = {"avisos": [w.value.replace("\\", "") for w in at.warning], "hojas": registro.get("hojas", [])}
    connection.dispose_engine()
    return resultado


print(json.dumps({"balance": abrir("report_horizontal_balance"), "resultados": abrir("report_horizontal_income")}))
