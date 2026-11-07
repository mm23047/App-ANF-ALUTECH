"""Punto de entrada de la aplicacion Streamlit.

Ejecutar con: streamlit run app.py
"""
from __future__ import annotations

import logging

import streamlit as st

from components import confirmacion
from components.navigation import render_sidebar
from database import connection
from database.connection import init_db, render_scope, session_scope
from database.migrations import MigracionError
from database.repositories import get_company
from database.seed import seed_default_accounts

st.set_page_config(page_title="Análisis Financiero", layout="wide")

if st.session_state.get("pending_restore"):
    from pathlib import Path

    from database.backup_utils import RespaldoInvalido, RestauracionError, restaurar

    origen = Path(st.session_state.pop("pending_restore"))
    connection.dispose_engine()
    try:
        resultado = restaurar(origen, connection.DB_PATH, dir_respaldos=connection.DB_PATH.parent / "backups")
    except RespaldoInvalido as exc:
        logging.getLogger(__name__).exception("Restauración rechazada")
        st.error(f"No se restauró la copia: {exc} La base de datos actual no se modificó.")
    except RestauracionError as exc:
        logging.getLogger(__name__).exception("Restauración fallida")
        st.error(f"No se restauró la copia: {exc}")
    else:
        previo = resultado.respaldo_previo.name if resultado.respaldo_previo else "no aplica"
        st.success(
            f"Base de datos restaurada: {resultado.info.empresa} · ejercicios "
            f"{', '.join(str(a) for a, _ in resultado.info.ejercicios) or 'ninguno'}. "
            f"Copia automática de la base anterior: {previo}."
        )
    st.session_state["db_inicializada"] = False

if not st.session_state.get("db_inicializada"):
    connection.preparar_base_inicial()
    try:
        init_db()
    except MigracionError as exc:
        logging.getLogger(__name__).exception("Migración de esquema fallida")
        st.error(
            f"No se pudo actualizar la base de datos: {exc} No se aplicó ningún cambio; "
            "la copia previa (si se creó) está en data/backups/."
        )
        st.stop()
    with session_scope() as _s:
        seed_default_accounts(_s)
    st.session_state["db_inicializada"] = True

# Paginas del analisis 2021-2025 (reports/analisis_alutech.py): clave -> funcion.
PAGINAS_ANALISIS = {
    "report_horizontal": "render_horizontal",
    "report_horizontal_balance": "render_horizontal_balance",
    "report_horizontal_income": "render_horizontal_resultados",
    "report_vertical_comp": "render_vertical_comparativo",
    "report_indicadores": "render_indicadores",
    "report_wacc": "render_wacc",
    "report_fuentes_usos": "render_fuentes_usos",
    "report_integral": "render_informe_integral",
    "validacion_anf": "render_validacion",
}

PRIMARY = "#0B2447"
# Unico HTML habilitado: CSS constante, sin datos del usuario (B-04).
st.markdown(
    f"""
    <style>
    section[data-testid="stSidebar"] {{ background-color: {PRIMARY}; }}
    section[data-testid="stSidebar"] * {{ color: #FFFFFF; }}
    /* Menu lateral: encabezado, separador y opciones planas */
    section[data-testid="stSidebar"] h1 {{ font-size: 1.35rem; font-weight: 700; letter-spacing: .01em; padding-bottom: 0; }}
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {{ color: #A9BCD6; font-size: .8rem; }}
    section[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,.15); margin: .6rem 0 .8rem; }}
    section[data-testid="stSidebar"] .stButton {{ margin-bottom: -.35rem; }}
    section[data-testid="stSidebar"] .stButton button {{
        justify-content: flex-start; text-align: left; border: none; border-left: 3px solid transparent;
        border-radius: 8px; background: transparent; padding: .5rem .75rem; min-height: 2.4rem;
        font-size: .92rem; font-weight: 500; transition: background .15s ease;
    }}
    section[data-testid="stSidebar"] .stButton button > div {{ justify-content: flex-start; }}
    section[data-testid="stSidebar"] .stButton button p {{ text-align: left; white-space: normal; line-height: 1.25; }}
    section[data-testid="stSidebar"] .stButton button:hover {{ background: rgba(255,255,255,.08); }}
    section[data-testid="stSidebar"] .stButton button:focus:not(:active) {{ box-shadow: none; }}
    section[data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"] {{
        background: rgba(95,168,232,.22); border-left-color: #5FA8E8; font-weight: 600;
    }}
    section[data-testid="stSidebar"] .stButton button[data-testid="stBaseButton-primary"]:hover {{
        background: rgba(95,168,232,.28);
    }}
    section[data-testid="stSidebar"] [data-testid="stExpander"] details {{ border: none; background: transparent; }}
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary {{
        padding: .5rem .75rem; border-radius: 8px; font-size: .92rem; font-weight: 600; background: transparent;
    }}
    section[data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {{ background: rgba(255,255,255,.08); }}
    section[data-testid="stSidebar"] [data-testid="stExpanderDetails"] {{
        padding: .1rem 0 .3rem .7rem; border-left: 1px solid rgba(255,255,255,.15); margin-left: 1.05rem;
    }}
    section[data-testid="stSidebar"] [data-testid="stExpanderDetails"] .stButton button {{ font-size: .87rem; min-height: 2.2rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# La pagina se renderiza sin commit implicito: cada accion de escritura
# confirma por su cuenta (components/transacciones.py).
with render_scope() as session:
    company = get_company(session)
    pagina = render_sidebar(company_exists=company is not None)
    # Una operacion masiva sin confirmar no sobrevive a un cambio de pagina (M-10).
    # "Ingreso de datos" agrupa dos paginas de captura: cuenta como la que muestra.
    if pagina == "entry_data":
        from modules.data_entry import pagina_de_ingreso

        confirmacion.descartar_al_navegar(pagina_de_ingreso())
    else:
        confirmacion.descartar_al_navegar(pagina)

    if pagina == "company":
        from modules import company as mod_company

        mod_company.render(session)
    elif company is None:
        st.stop()
    elif pagina == "dashboard":
        from modules import dashboard as mod_dashboard

        mod_dashboard.render(session, company)
    elif pagina == "accounts":
        from modules import accounts as mod_accounts

        mod_accounts.render(session)
    elif pagina == "entry_data":
        from modules import data_entry as mod_entry

        mod_entry.render_ingreso(session, company)
    elif pagina == "entry_balance":
        from modules import data_entry as mod_entry

        mod_entry.render_balance(session, company)
    elif pagina == "entry_income":
        from modules import data_entry as mod_entry

        mod_entry.render_income(session, company)
    elif pagina == "entry_initial":
        from modules import data_entry as mod_entry

        mod_entry.render_initial_balances(session, company)
    elif pagina == "entry_excel":
        from modules import excel_import as mod_excel

        mod_excel.render(session, company)
    elif pagina == "edit_data":
        from modules import data_edit as mod_edit

        mod_edit.render(session, company)
    elif pagina == "report_balance":
        from reports import balance_report

        balance_report.render(session, company)
    elif pagina == "report_income":
        from reports import income_report

        income_report.render(session, company)
    elif pagina == "report_vertical_balance":
        from reports import vertical_report

        vertical_report.render_balance(session, company)
    elif pagina == "report_vertical_income":
        from reports import vertical_report

        vertical_report.render_income(session, company)
    elif pagina == "report_dupont":
        from reports import dupont_report

        dupont_report.render(session, company)
    elif pagina == "trazabilidad":
        from modules import trazabilidad as mod_trazabilidad

        mod_trazabilidad.render(session, company)
    elif pagina in PAGINAS_ANALISIS:
        from reports import analisis_alutech

        getattr(analisis_alutech, PAGINAS_ANALISIS[pagina])(session, company)
    elif pagina == "history":
        from modules import history as mod_history

        mod_history.render(session)
    elif pagina == "backup":
        from modules import backup as mod_backup

        mod_backup.render()
    elif pagina == "settings":
        from modules import company as mod_company

        mod_company.render(session)
