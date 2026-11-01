"""Analisis vertical del Balance General y del Estado de Resultados
(secciones 9.3 y 9.4). Incluye subtotales, totales y utilidades (M-03) y
las mismas banderas de estado que el reporte del estado correspondiente."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy.orm import Session

from calculations.balance_sheet import compute_balance_sheet
from calculations.banderas import banderas_balance, banderas_resultados
from calculations.controls import conciliar_resultado
from calculations.income_statement import compute_income_statement
from calculations.vertical_analysis import ETIQUETA_EFECTO, compute_vertical_balance, compute_vertical_income
from components.avisos import mostrar_estado
from components.money import format_money, format_percent
from components.navigation import select_fiscal_period
from database.models import Company


def _tabla_presentacion(lineas, moneda: str) -> pd.DataFrame:
    """Tabla de pantalla formateada directamente desde los Decimal del
    calculo (hallazgo M-11). "Sin datos": grupo sin cuentas capturadas;
    "No disponible": porcentaje sin base."""
    return pd.DataFrame(
        [
            {
                "Código": l.codigo,
                "Concepto": l.etiqueta if l.tipo == "cuenta" else l.etiqueta.upper(),
                "Valor": format_money(l.valor, moneda) if l.valor is not None else "Sin datos",
                "Participación %": format_percent(l.porcentaje),
                "Efecto": ETIQUETA_EFECTO.get(l.efecto, ""),
            }
            for l in lineas
        ],
        columns=["Código", "Concepto", "Valor", "Participación %", "Efecto"],
    )


def _grafico(resultado, titulo: str):
    """Grafico de las cuentas (presentacion; los calculos se hacen con Decimal)."""
    df = pd.DataFrame(
        [{"Cuenta": f.cuenta.nombre, "Participación %": float(f.porcentaje)} for f in resultado.filas if f.porcentaje is not None]
    )
    return px.bar(df, x="Cuenta", y="Participación %", title=titulo)


def _descargas(company, period, titulo: str, resultado, base, nombre_base: str, banderas, archivo: str) -> None:
    from reports.excel_export import export_vertical_excel
    from reports.pdf_export import export_vertical_pdf

    col_pdf, col_xlsx = st.columns(2)
    with col_pdf:
        st.download_button(
            "Descargar PDF",
            data=export_vertical_pdf(company, period, titulo, resultado.lineas, base, nombre_base, banderas),
            file_name=f"{archivo}_{period.anio}.pdf",
            mime="application/pdf",
        )
    with col_xlsx:
        st.download_button(
            "Descargar Excel",
            data=export_vertical_excel(company, period, titulo, None, base, nombre_base, resultado.lineas, banderas),
            file_name=f"{archivo}_{period.anio}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )


def render_balance(session: Session, company: Company) -> None:
    st.header("Reporte — Análisis Vertical del Balance General")
    period = select_fiscal_period(session, key="periodo_vertical_balance", allow_create=False)
    if period is None:
        return

    resultado = compute_vertical_balance(session, period.id)
    if not resultado.disponible:
        st.info("No hay datos suficientes (Balance capturado y Total Activo distinto de cero) para este ejercicio.")
        return

    bs = compute_balance_sheet(session, period.id)
    banderas = banderas_balance(bs, conciliar_resultado(bs, compute_income_statement(session, period.id)))
    mostrar_estado(banderas)
    st.caption(f"Base (100%): Total Activo = {format_money(resultado.base_total_activo, company.moneda)}")
    st.dataframe(_tabla_presentacion(resultado.lineas, company.moneda), hide_index=True, width="stretch")
    st.plotly_chart(_grafico(resultado, "Participación porcentual sobre el Total Activo"), width="stretch")
    _descargas(company, period, "Análisis Vertical — Balance General", resultado, resultado.base_total_activo,
               "Total Activo", banderas, "analisis_vertical_balance")


def render_income(session: Session, company: Company) -> None:
    st.header("Reporte — Análisis Vertical del Estado de Resultados")
    period = select_fiscal_period(session, key="periodo_vertical_resultados", allow_create=False)
    if period is None:
        return

    resultado = compute_vertical_income(session, period.id)
    if not resultado.disponible:
        st.info("No hay datos suficientes (Estado de Resultados capturado e Ingresos Netos distintos de cero) para este ejercicio.")
        return

    inc = compute_income_statement(session, period.id)
    banderas = banderas_resultados(inc, conciliar_resultado(compute_balance_sheet(session, period.id), inc))
    mostrar_estado(banderas)
    st.caption(
        f"Base (100%): Ingresos Netos = {format_money(resultado.base_ingresos_netos, company.moneda)} · "
        "Los costos, gastos e impuestos tienen porcentaje positivo y restan (columna Efecto)."
    )
    st.dataframe(_tabla_presentacion(resultado.lineas, company.moneda), hide_index=True, width="stretch")
    st.plotly_chart(_grafico(resultado, "Participación porcentual sobre los Ingresos Netos"), width="stretch")
    _descargas(company, period, "Análisis Vertical — Estado de Resultados", resultado, resultado.base_ingresos_netos,
               "Ingresos Netos", banderas, "analisis_vertical_resultados")
