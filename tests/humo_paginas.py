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

from components.navigation import _ETIQUETAS, CLAVE_PAGINA, PAGINAS  # noqa: E402

resultados = {}
# Cada pagina del catalogo (visible en el menu u oculta) se abre por su clave.
for etiqueta, clave in PAGINAS:
    at = AppTest.from_file(str(PROYECTO / "app.py"), default_timeout=60)
    at.session_state[CLAVE_PAGINA] = clave
    at.run()
    connection.dispose_engine()
    resultados[etiqueta] = {
        "pagina": _ETIQUETAS[at.session_state[CLAVE_PAGINA]],
        "encabezados": [h.value for h in at.header],
        "excepciones": [e.value for e in at.exception],
        "tablas": [t.value.astype(str).to_dict("records") for t in at.dataframe],
    }
# Menu visible: botones del lateral y la pagina que abre cada uno al hacer clic.
at = AppTest.from_file(str(PROYECTO / "app.py"), default_timeout=60)
at.run()
menu = {"inicial": at.session_state[CLAVE_PAGINA], "expansores": [e.label for e in at.sidebar.expander],
        "opciones": [b.label for b in at.sidebar.button], "clics": {}}
connection.dispose_engine()
# Cada clic desde una sesion nueva: AppTest reevalua los widgets de la pagina
# anterior con objetos ORM de una sesion ya cerrada (no ocurre en el navegador).
for clave_boton in [b.key for b in at.sidebar.button]:
    at = AppTest.from_file(str(PROYECTO / "app.py"), default_timeout=60)
    at.run()
    boton = at.sidebar.button(key=clave_boton)
    boton.click().run()
    connection.dispose_engine()
    activos = [b.label for b in at.sidebar.button if b.proto.type == "primary"]
    menu["clics"][boton.label] = {"pagina": at.session_state[CLAVE_PAGINA], "activos": activos,
                                  "encabezados": [h.value for h in at.header], "excepciones": [e.value for e in at.exception]}
connection.dispose_engine()
resultados["_menu"] = menu
print(json.dumps(resultados))
