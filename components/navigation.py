"""Menu lateral (seccion 13) y selector de ejercicio fiscal compartido."""
from __future__ import annotations

import streamlit as st
from sqlalchemy.orm import Session

from database.models import FiscalPeriod
from database.repositories import get_or_create_fiscal_period, list_fiscal_periods

PAGINAS: list[tuple[str, str]] = [
    ("Dashboard", "dashboard"),
    ("Datos de la empresa", "company"),
    ("Catálogo de cuentas", "accounts"),
    ("Ingreso de datos › Balance General", "entry_balance"),
    ("Ingreso de datos › Estado de Resultados", "entry_income"),
    ("Ingreso de datos › Saldos iniciales", "entry_initial"),
    ("Ingreso de datos › Importación Excel", "entry_excel"),
    ("Modificación de datos", "edit_data"),
    ("Reportes › Balance General", "report_balance"),
    ("Reportes › Estado de Resultados", "report_income"),
    ("Reportes › Análisis Vertical del Balance General", "report_vertical_balance"),
    ("Reportes › Análisis Vertical del Estado de Resultados", "report_vertical_income"),
    ("Reportes › Análisis DuPont", "report_dupont"),
    ("Historial de cambios", "history"),
    ("Copias de seguridad", "backup"),
    ("Configuración", "settings"),
]

_ETIQUETAS = {clave: etiqueta for etiqueta, clave in PAGINAS}


def render_sidebar(company_exists: bool) -> str:
    st.sidebar.title("Análisis Financiero")
    if not company_exists:
        st.sidebar.info("Primero registra los datos de la empresa.")
        return "company"

    etiquetas = [etiqueta for etiqueta, _ in PAGINAS]
    seleccion = st.sidebar.radio("Menú", etiquetas, label_visibility="collapsed")
    clave = next(clave for etiqueta, clave in PAGINAS if etiqueta == seleccion)
    return clave


def select_fiscal_period(session: Session, *, key: str = "periodo_fiscal", allow_create: bool = True) -> FiscalPeriod | None:
    """Selector de ejercicio fiscal reutilizado por todos los modulos de
    captura/edicion/reportes. Devuelve None si no hay ningun ejercicio."""
    periodos = list_fiscal_periods(session)

    if allow_create:
        from database.repositories import get_company

        company = get_company(session)
        anio_sugerido = max((p.anio for p in periodos), default=(company.anio_inicial_analisis - 1 if company else 2020)) + 1
        with st.expander("Crear nuevo ejercicio fiscal"):
            nuevo_anio = st.number_input("Año", min_value=1900, max_value=2200, value=anio_sugerido, step=1, key=f"{key}_nuevo_anio")
            if st.button("Crear ejercicio", key=f"{key}_crear_btn"):
                _, creado = get_or_create_fiscal_period(session, int(nuevo_anio))
                session.commit()
                if creado:
                    st.success(f"Ejercicio {nuevo_anio} creado.")
                    st.rerun()
                else:
                    st.warning(f"El ejercicio {nuevo_anio} ya existe.")

    periodos = list_fiscal_periods(session)
    if not periodos:
        st.warning("No hay ningún ejercicio fiscal registrado todavía. Crea uno arriba.")
        return None

    opciones = [p.anio for p in periodos]
    default_index = len(opciones) - 1
    anio_sel = st.selectbox("Ejercicio fiscal", opciones, index=default_index, key=f"{key}_select")
    return next(p for p in periodos if p.anio == anio_sel)
