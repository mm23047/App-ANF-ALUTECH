"""Abre con AppTest las paginas del analisis horizontal, elige un nivel y registra lo que la pagina
entrega a las descargas. Se ejecuta en un subproceso desde test_fase11_horizontal.py
(razon: tests/humo_paginas.py).

Uso: python tests/humo_exportes_nivel.py RUTA_BD
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
    registro.update(archivo=archivo, interanuales=[s.titulo for nombre, secciones in hojas if " vs " in nombre for s in secciones])


analisis_alutech.descargas = _descargas


def abrir(pagina: str, clave_nivel: str, opcion: str | None) -> dict:
    registro.clear()
    at = AppTest.from_file(str(PROYECTO / "app.py"), default_timeout=180)
    at.session_state[CLAVE_PAGINA] = pagina
    at.run()
    if opcion:
        widget = next(r for r in at.radio if r.key == clave_nivel)
        widget.set_value(next(o for o in widget.options if opcion in o))
        at.run()
    assert not at.exception, [e.value for e in at.exception]
    resultado = dict(registro)
    connection.dispose_engine()
    return resultado


print(json.dumps({
    "balance_defecto": abrir("report_horizontal_balance", "horizontal_balance_nivel", None),
    "balance_cuentas": abrir("report_horizontal_balance", "horizontal_balance_nivel", "Cuentas"),
    "balance_grupos": abrir("report_horizontal_balance", "horizontal_balance_nivel", "Grupos"),
    "resultados_cuentas": abrir("report_horizontal_income", "horizontal_resultados_nivel", "Cuentas"),
}))
