"""Punto de entrada de la aplicacion Streamlit.

Ejecutar con: streamlit run app.py
"""
from __future__ import annotations

import streamlit as st

from components.navigation import render_sidebar
from database.connection import init_db, session_scope
from database.repositories import get_company
from database.seed import seed_default_accounts

st.set_page_config(page_title="Análisis Financiero", layout="wide")

if st.session_state.get("pending_restore"):
    import shutil

    from database.connection import DB_PATH, dispose_engine

    origen = st.session_state.pop("pending_restore")
    dispose_engine()
    shutil.copy2(origen, DB_PATH)
    st.session_state["db_inicializada"] = False
    st.success("Base de datos restaurada correctamente.")

if not st.session_state.get("db_inicializada"):
    init_db()
    with session_scope() as _s:
        seed_default_accounts(_s)
    st.session_state["db_inicializada"] = True

PRIMARY = "#0B2447"
st.markdown(
    f"""
    <style>
    section[data-testid="stSidebar"] {{ background-color: {PRIMARY}; }}
    section[data-testid="stSidebar"] * {{ color: #FFFFFF; }}
    </style>
    """,
    unsafe_allow_html=True,
)

with session_scope() as session:
    company = get_company(session)
    pagina = render_sidebar(company_exists=company is not None)

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
    elif pagina == "history":
        from modules import history as mod_history

        mod_history.render(session)
    elif pagina == "backup":
        from modules import backup as mod_backup

        mod_backup.render()
    elif pagina == "settings":
        from modules import company as mod_company

        mod_company.render(session)
