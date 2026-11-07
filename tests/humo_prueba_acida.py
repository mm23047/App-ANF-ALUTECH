"""Abre con AppTest la pagina de indicadores sobre una BD temporal y devuelve sus textos. Se ejecuta en un subproceso
desde test_fase14_prueba_acida.py (razon: tests/humo_paginas.py).

Uso: python tests/humo_prueba_acida.py RUTA_BD
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

at = AppTest.from_file(str(PROYECTO / "app.py"), default_timeout=180)
at.session_state[CLAVE_PAGINA] = "report_indicadores"
at.run()
assert not at.exception, [e.value for e in at.exception]
print(json.dumps({"textos": [c.value.replace("\\", "") for c in at.caption]}))
connection.dispose_engine()
