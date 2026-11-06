"""Abre con AppTest los reportes verticales, DuPont, Dashboard, Informe integral y
Validacion sobre la BD indicada, para cada ejercicio, y escribe un JSON con lo que se
ve en pantalla. Se ejecuta en un subproceso desde test_fase8_vertical_dupont.py (ver
la razon en tests/humo_paginas.py).

Uso: python tests/humo_vertical_dupont.py RUTA_BD
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


def abrir(clave: str, selector: str | None = None, anio: int | None = None) -> dict:
    at = AppTest.from_file(str(PROYECTO / "app.py"), default_timeout=120)
    at.session_state[CLAVE_PAGINA] = clave
    at.run()
    if selector:
        caja = next(x for x in at.selectbox if x.key == f"{selector}_select")
        caja.set_value(next(o for o in caja.options if str(anio) in str(o)))
        at.run()
    resultado = {
        "excepciones": [e.value for e in at.exception],
        "encabezados": [h.value for h in at.header],
        "tablas": [t.value.astype(str).to_dict("records") for t in at.dataframe],
        "metricas": {m.label: m.value for m in at.metric},
        "avisos": [w.value for w in at.warning],
        "textos": [c.value for c in at.caption] + [m.value for m in at.markdown],
    }
    connection.dispose_engine()
    return resultado


salida = {"anios": {}}
for anio in (2021, 2022, 2023, 2024, 2025):
    salida["anios"][str(anio)] = {
        "vertical_balance": abrir("report_vertical_balance", "periodo_vertical_balance", anio),
        "vertical_resultados": abrir("report_vertical_income", "periodo_vertical_resultados", anio),
        "dupont": abrir("report_dupont", "periodo_dupont", anio),
    }
salida["dashboard"] = abrir("dashboard")
salida["informe"] = abrir("report_integral")
salida["saldos_iniciales"] = abrir("entry_initial")
print(json.dumps(salida))
