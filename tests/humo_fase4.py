"""Escenarios de la fase 4 con el app.py real (AppTest). Se ejecuta en un
subproceso desde test_fase4.py por la misma razon que humo_paginas.py
(st.form sin servidor deja estado global que impide navegar con AppTest).

Uso: python tests/humo_fase4.py RUTA_BD
La BD debe tener empresa, catalogo y el ejercicio 2021 sin importes de
balance salvo 1002 = 50.00. Escribe un JSON con el resultado de cada
escenario.
"""
import json
import sqlite3
import sys
from pathlib import Path

PROYECTO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROYECTO))

from database import connection  # noqa: E402

RUTA = Path(sys.argv[1])
connection.DB_PATH = RUTA  # antes de importar app.py: nunca la BD real

from streamlit.testing.v1 import AppTest  # noqa: E402

from database.backup_utils import sha256_archivo  # noqa: E402

CAPTURA = "Ingreso de datos › Balance General"
EDICION = "Modificación de datos"


def importes():
    con = sqlite3.connect(f"file:{RUTA}?mode=ro", uri=True)
    filas = con.execute(
        "select a.codigo, b.valor from balance_entry b join account a on a.id = b.account_id order by a.codigo"
    ).fetchall()
    con.close()
    return dict(filas)


def abrir(pagina):
    at = AppTest.from_file(str(PROYECTO / "app.py"), default_timeout=60)
    at.run()
    at.sidebar.radio[0].set_value(pagina).run()
    assert at.sidebar.radio[0].value == pagina, at.sidebar.radio[0].value
    return at


def boton(at, etiqueta):
    return next(b for b in at.button if b.label == etiqueta)


def hay_boton(at, etiqueta):
    return any(b.label == etiqueta for b in at.button)


def campo(at, codigo):
    return next(n for n in at.number_input if n.label.startswith(f"{codigo} — "))


def proponer_captura(at, valores):
    for codigo, valor in valores.items():
        campo(at, codigo).set_value(valor)
    boton(at, "Guardar").click().run()
    return at


def textos(at):
    return [m.value for m in at.warning] + [m.value for m in at.info] + [m.value for m in at.success] + [
        m.value for m in at.error]


def cerrar(at):
    connection.dispose_engine()


r = {}

# ---- B-04: datos de empresa maliciosos en pantalla
at = abrir("Reportes › Balance General")
r["b04_markdown"] = [{"valor": m.value, "html": m.allow_html} for m in at.markdown]
r["b04_subheaders"] = [h.value for h in at.subheader]
r["b04_captions"] = [c.value for c in at.caption]
r["b04_excepciones"] = [e.value for e in at.exception]
cerrar(at)
at = abrir("Dashboard")
r["b04_dashboard_subheaders"] = [h.value for h in at.subheader]
r["b04_dashboard_html"] = [m.value for m in at.markdown if m.allow_html]
r["b04_dashboard_excepciones"] = [e.value for e in at.exception]
cerrar(at)

# ---- D08: proponer y cancelar
hash0 = sha256_archivo(RUTA)
at = proponer_captura(abrir(CAPTURA), {"1001": 100.0, "1002": 75.0})
r["d08_propuesta_hash_igual"] = sha256_archivo(RUTA) == hash0
r["d08_propuesta_tablas"] = [t.value.astype(str).to_dict("records") for t in at.dataframe]
r["d08_propuesta_textos"] = textos(at)
r["d08_propuesta_boton_confirmar"] = hay_boton(at, "Confirmar y guardar")
boton(at, "Cancelar").click().run()
r["d08_cancelar_hash_igual"] = sha256_archivo(RUTA) == hash0
r["d08_cancelar_textos"] = textos(at)
r["d08_cancelar_sin_boton_confirmar"] = not hay_boton(at, "Confirmar y guardar")
cerrar(at)

# ---- D08: recarga (sesion nueva) con una propuesta pendiente
at = proponer_captura(abrir(CAPTURA), {"1001": 100.0})
cerrar(at)
at = abrir(CAPTURA)  # navegador recargado: sesion nueva
r["d08_recarga_sin_boton_confirmar"] = not hay_boton(at, "Confirmar y guardar")
r["d08_recarga_hash_igual"] = sha256_archivo(RUTA) == hash0
cerrar(at)

# ---- D08: navegar a otra pagina y volver
at = proponer_captura(abrir(CAPTURA), {"1001": 100.0})
at.sidebar.radio[0].set_value("Dashboard").run()
at.sidebar.radio[0].set_value(CAPTURA).run()
r["d08_navegar_sin_boton_confirmar"] = not hay_boton(at, "Confirmar y guardar")
r["d08_navegar_hash_igual"] = sha256_archivo(RUTA) == hash0
cerrar(at)

# ---- D08: confirmar escribe exactamente lo propuesto, en un lote
at = proponer_captura(abrir(CAPTURA), {"1001": 100.0, "1002": 75.0})
boton(at, "Confirmar y guardar").click().run()
r["d08_confirmar_importes"] = importes()
r["d08_confirmar_excepciones"] = [e.value for e in at.exception]
con = sqlite3.connect(f"file:{RUTA}?mode=ro", uri=True)
r["d08_confirmar_lotes"] = con.execute(
    "select count(distinct lote_id), count(*) from change_history where tabla_afectada = 'balance_entry'"
).fetchone()
con.close()
r["d08_confirmar_sin_boton_confirmar"] = not hay_boton(at, "Confirmar y guardar")
hash1 = sha256_archivo(RUTA)
# Repeticion: un nuevo "Guardar" sin cambios no propone nada.
boton(at, "Guardar").click().run()
r["d08_repetir_sin_boton_confirmar"] = not hay_boton(at, "Confirmar y guardar")
r["d08_repetir_hash_igual"] = sha256_archivo(RUTA) == hash1
cerrar(at)

# ---- D08: los datos cambian entre la propuesta y la confirmacion
at = proponer_captura(abrir(CAPTURA), {"1003": 10.0})
con = sqlite3.connect(RUTA)
con.execute(
    "insert into balance_entry (fiscal_period_id, account_id, valor, created_at, updated_at) "
    "select p.id, a.id, 999, '2026-11-01', '2026-11-01' from fiscal_period p, account a "
    "where p.anio = 2021 and a.codigo = '1003'"
)
con.commit()
con.close()
boton(at, "Confirmar y guardar").click().run()
r["d08_obsoleta_importe_1003"] = importes().get("1003")
r["d08_obsoleta_textos"] = textos(at)
cerrar(at)

# ---- D08: la pagina de edicion se abre sin proponer ni escribir nada
# (AppTest no permite editar celdas de st.data_editor: el flujo de la tabla
# se prueba con widgets simulados en test_fase4.py).
hash2 = sha256_archivo(RUTA)
at = abrir(EDICION)
r["d08_edicion_sin_boton_confirmar"] = not hay_boton(at, "Confirmar y guardar")
r["d08_edicion_hash_igual"] = sha256_archivo(RUTA) == hash2
r["d08_edicion_excepciones"] = [e.value for e in at.exception]
cerrar(at)

print(json.dumps(r, default=str))
