"""Abre con AppTest las paginas del analisis horizontal, los comparativos verticales y
de DuPont y los indicadores sobre la BD indicada, y escribe un JSON con lo que se ve.
Se ejecuta en un subproceso desde test_fase9_rubrica.py (razon: tests/humo_paginas.py).

Uso: python tests/humo_horizontal.py RUTA_BD
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


def foto(at) -> dict:
    return {
        "excepciones": [e.value for e in at.exception],
        "encabezados": [h.value for h in at.header],
        "pestanas": [t.label for t in at.tabs],
        "tablas": [t.value.astype(str).to_dict("records") for t in at.dataframe],
        "metricas": {m.label: m.value for m in at.metric},
        "descargas": [b.proto.label for b in at.get("download_button")],
        "textos": [c.value for c in at.caption] + [m.value for m in at.markdown] + [w.value for w in at.warning],
    }


def abrir(clave: str, **valores) -> dict:
    at = AppTest.from_file(str(PROYECTO / "app.py"), default_timeout=180)
    at.session_state[CLAVE_PAGINA] = clave
    at.run()
    for clave_widget, opcion in valores.items():
        widget = next(w for w in list(at.selectbox) + list(at.radio) if w.key == clave_widget)
        widget.set_value(next(o for o in widget.options if opcion in str(o)))
        at.run()
    resultado = foto(at)
    connection.dispose_engine()
    return resultado


salida = {
    "balance": abrir("report_horizontal_balance"),
    "balance_2024_cuentas": abrir("report_horizontal_balance", horizontal_balance_par="2024 vs 2023",
                                  horizontal_balance_nivel="Cuentas"),
    "resultados": abrir("report_horizontal_income"),
    "resultados_2025_grupos": abrir("report_horizontal_income", horizontal_resultados_nivel="Grupos"),
    "vertical_balance": abrir("report_vertical_balance"),
    "vertical_resultados": abrir("report_vertical_income"),
    "dupont": abrir("report_dupont"),
    "indicadores": abrir("report_indicadores"),
    "balance_general_2021": abrir("report_balance", periodo_reporte_balance_select="2021"),
}
print(json.dumps(salida))
