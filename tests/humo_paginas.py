"""Recorre las paginas de app.py con AppTest sobre la BD indicada y escribe
un JSON con el resultado de cada una. Se ejecuta en un subproceso desde
test_fase1_paginas.py: otras pruebas que usan widgets sin servidor dejan
estado global de Streamlit (context_dg_stack) que impide navegar con
AppTest en el mismo proceso.

Uso: python tests/humo_paginas.py RUTA_BD
"""
import json
import sys
from pathlib import Path

PROYECTO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROYECTO))

from database import connection  # noqa: E402

connection.DB_PATH = Path(sys.argv[1])  # antes de importar app.py: nunca la BD real

from streamlit.testing.v1 import AppTest  # noqa: E402

from components.navigation import PAGINAS  # noqa: E402

resultados = {}
for etiqueta, _ in PAGINAS:
    at = AppTest.from_file(str(PROYECTO / "app.py"), default_timeout=60)
    at.run()
    at.sidebar.radio[0].set_value(etiqueta).run()
    connection.dispose_engine()
    resultados[etiqueta] = {
        "pagina": at.sidebar.radio[0].value,
        "encabezados": [h.value for h in at.header],
        "excepciones": [e.value for e in at.exception],
        "tablas": [t.value.astype(str).to_dict("records") for t in at.dataframe],
    }
print(json.dumps(resultados))
