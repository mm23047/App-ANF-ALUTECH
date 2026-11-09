"""Menu lateral (seccion 13) y selector de ejercicio fiscal compartido."""
from __future__ import annotations

import streamlit as st
from sqlalchemy.orm import Session

from components.money import ANIO_MAXIMO, ANIO_MINIMO
from components.transacciones import ejecutar_escritura
from database.models import FiscalPeriod
from database.repositories import get_fiscal_period, get_or_create_fiscal_period, list_fiscal_periods

# Catalogo completo de paginas (etiqueta, clave). Todas siguen existiendo y
# app.py las enruta; el menu lateral solo muestra las de MENU_PRINCIPAL y
# MENU_REPORTES. Las demas quedan ocultas (no eliminadas): se muestran en
# "Más opciones" si la variable de entorno ANF_MENU_COMPLETO vale 1.
PAGINAS: list[tuple[str, str]] = [
    ("Ingreso de datos", "entry_data"),
    ("Dashboard", "dashboard"),
    ("Datos de la empresa", "company"),
    ("Catálogo de cuentas", "accounts"),
    ("Ingreso de datos › Balance General", "entry_balance"),
    ("Ingreso de datos › Estado de Resultados", "entry_income"),
    ("Ingreso de datos › Saldos iniciales", "entry_initial"),
    ("Ingreso de datos › Importación Excel", "entry_excel"),
    ("Modificación de datos", "edit_data"),
    ("Datos originales › Trazabilidad y controles", "trazabilidad"),
    ("Reportes › Balance General", "report_balance"),
    ("Reportes › Estado de Resultados", "report_income"),
    ("Reportes › Análisis Vertical del Balance General", "report_vertical_balance"),
    ("Reportes › Análisis Vertical del Estado de Resultados", "report_vertical_income"),
    ("Reportes › Análisis Horizontal del Balance General", "report_horizontal_balance"),
    ("Reportes › Análisis Horizontal del Estado de Resultados", "report_horizontal_income"),
    ("Reportes › Análisis DuPont", "report_dupont"),
    ("Reportes › Análisis Horizontal comparativo", "report_horizontal"),
    ("Reportes › Análisis Vertical comparativo", "report_vertical_comp"),
    ("Reportes › Indicadores financieros", "report_indicadores"),
    ("Reportes › WACC", "report_wacc"),
    ("Reportes › Origen y aplicación de fondos", "report_fuentes_usos"),
    ("Reportes › Informe integral", "report_integral"),
    ("Validación › Contraste de resultados", "validacion_anf"),
    ("Historial de cambios", "history"),
    ("Copias de seguridad", "backup"),
    ("Configuración", "settings"),
]

_ETIQUETAS = {clave: etiqueta for etiqueta, clave in PAGINAS}

# Menu visible: (clave, etiqueta en el menu, icono Material).
MENU_PRINCIPAL: list[tuple[str, str, str]] = [
    ("entry_data", "Ingreso de datos", ":material/edit_note:"),
    ("edit_data", "Modificación de datos", ":material/edit_document:"),
    ("report_indicadores", "Indicadores financieros", ":material/query_stats:"),
]
MENU_REPORTES: list[tuple[str, str, str]] = [
    ("report_balance", "Balance General", ":material/account_balance:"),
    ("report_income", "Estado de Resultados", ":material/receipt_long:"),
    ("report_vertical_balance", "Análisis Vertical del Balance General", ":material/stacked_bar_chart:"),
    ("report_vertical_income", "Análisis Vertical del Estado de Resultados", ":material/percent:"),
    ("report_horizontal_balance", "Análisis Horizontal del Balance General", ":material/compare_arrows:"),
    ("report_horizontal_income", "Análisis Horizontal del Estado de Resultados", ":material/swap_horiz:"),
    ("report_dupont", "Rentabilidad mediante fórmula DuPont", ":material/trending_up:"),
]
TITULO_REPORTES = "Generación de reportes"
PAGINA_INICIAL = "entry_data"
CLAVE_PAGINA = "pagina_activa"  # st.session_state: clave de la pagina abierta

_VISIBLES = {clave for clave, _, _ in MENU_PRINCIPAL + MENU_REPORTES}
PAGINAS_OCULTAS: list[tuple[str, str]] = [(e, c) for e, c in PAGINAS if c not in _VISIBLES]


def menu_completo() -> bool:
    import os

    return os.environ.get("ANF_MENU_COMPLETO") == "1"


def _ir(clave: str) -> None:
    st.session_state[CLAVE_PAGINA] = clave


def _opcion(clave: str, etiqueta: str, icono: str | None, activa: str) -> None:
    st.button(etiqueta, key=f"nav_{clave}", icon=icono, type="primary" if clave == activa else "secondary",
              width="stretch", on_click=_ir, args=(clave,))


def render_sidebar(company_exists: bool) -> str:
    # Solo elementos nativos: el unico HTML habilitado es el CSS de app.py (B-04).
    st.sidebar.title("Análisis Financiero")
    st.sidebar.caption("Estados financieros e indicadores")
    if not company_exists:
        st.sidebar.info("Primero registra los datos de la empresa.")
        return "company"

    activa = st.session_state.get(CLAVE_PAGINA, PAGINA_INICIAL)
    if activa not in _ETIQUETAS:
        activa = PAGINA_INICIAL
    st.session_state[CLAVE_PAGINA] = activa

    with st.sidebar:
        st.divider()
        for clave, etiqueta, icono in MENU_PRINCIPAL:
            _opcion(clave, etiqueta, icono, activa)
        with st.expander(TITULO_REPORTES, expanded=True, icon=":material/insert_chart:"):
            for clave, etiqueta, icono in MENU_REPORTES:
                _opcion(clave, etiqueta, icono, activa)
        if menu_completo():
            with st.expander("Más opciones", expanded=activa not in _VISIBLES, icon=":material/more_horiz:"):
                for etiqueta, clave in PAGINAS_OCULTAS:
                    _opcion(clave, etiqueta, None, activa)
    return activa


def select_fiscal_period(session: Session, *, key: str = "periodo_fiscal", allow_create: bool = True) -> FiscalPeriod | None:
    """Selector de ejercicio fiscal reutilizado por todos los modulos de
    captura/edicion/reportes. Devuelve None si no hay ningun ejercicio."""
    periodos = list_fiscal_periods(session)

    if allow_create:
        from database.repositories import get_company

        company = get_company(session)
        anio_sugerido = max((p.anio for p in periodos), default=(company.anio_inicial_analisis - 1 if company else 2020)) + 1
        anio_sugerido = min(max(anio_sugerido, ANIO_MINIMO), ANIO_MAXIMO)
        with st.expander("Crear nuevo ejercicio fiscal"):
            nuevo_anio = st.number_input(
                "Año", min_value=ANIO_MINIMO, max_value=ANIO_MAXIMO, value=anio_sugerido, step=1, key=f"{key}_nuevo_anio"
            )
            if st.button("Crear ejercicio", key=f"{key}_crear_btn"):
                if get_fiscal_period(session, int(nuevo_anio)) is not None:
                    st.warning(f"El ejercicio {int(nuevo_anio)} ya existe.")
                else:
                    creado, _ = ejecutar_escritura(
                        session,
                        lambda: get_or_create_fiscal_period(session, int(nuevo_anio)),
                        descripcion=f"crear el ejercicio {int(nuevo_anio)}",
                    )
                    if creado:
                        st.success(f"Ejercicio {int(nuevo_anio)} creado.")
                        st.rerun()

    periodos = list_fiscal_periods(session)
    if not periodos:
        st.warning("No hay ningún ejercicio fiscal registrado todavía. Crea uno arriba.")
        return None

    opciones = [p.anio for p in periodos]
    cerrados = {p.anio for p in periodos if p.cerrado}
    default_index = len(opciones) - 1
    anio_sel = st.selectbox(
        "Ejercicio fiscal",
        opciones,
        index=default_index,
        format_func=lambda a: f"{a} (cerrado)" if a in cerrados else str(a),
        key=f"{key}_select",
    )
    return next(p for p in periodos if p.anio == anio_sel)
