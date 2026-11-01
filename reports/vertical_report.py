"""Analisis vertical del Balance General y del Estado de Resultados
(secciones 9.3 y 9.4)."""
from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy.orm import Session

from calculations.vertical_analysis import compute_vertical_balance, compute_vertical_income
from components.money import format_money, format_percent
from components.navigation import select_fiscal_period
from database.models import Company


def _tabla(filas) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Código": f.cuenta.codigo,
                "Cuenta": f.cuenta.nombre,
                "Valor": float(f.valor),
                "Participación %": float(f.porcentaje) if f.porcentaje is not None else None,
            }
            for f in filas
        ]
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

    st.caption(
        f"Base (100%): Total Activo = {format_money(resultado.base_total_activo, company.moneda)}"
    )
    df = _tabla(resultado.filas)
    df_mostrar = df.copy()
    df_mostrar["Valor"] = df_mostrar["Valor"].map(lambda v: format_money(v, company.moneda))
    df_mostrar["Participación %"] = df_mostrar["Participación %"].map(
        lambda v: format_percent(v) if v is not None else "No disponible"
    )
    st.dataframe(df_mostrar, hide_index=True, width="stretch")

    fig = px.bar(df, x="Cuenta", y="Participación %", title="Participación porcentual sobre el Total Activo")
    st.plotly_chart(fig, width="stretch")

    from reports.excel_export import export_vertical_excel

    st.download_button(
        "Descargar Excel",
        data=export_vertical_excel(company, period, "Análisis Vertical — Balance General", df, resultado.base_total_activo, "Total Activo"),
        file_name=f"analisis_vertical_balance_{period.anio}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


def render_income(session: Session, company: Company) -> None:
    st.header("Reporte — Análisis Vertical del Estado de Resultados")
    period = select_fiscal_period(session, key="periodo_vertical_resultados", allow_create=False)
    if period is None:
        return

    resultado = compute_vertical_income(session, period.id)
    if not resultado.disponible:
        st.info("No hay datos suficientes (Estado de Resultados capturado e Ingresos Netos distintos de cero) para este ejercicio.")
        return

    st.caption(
        f"Base (100%): Ingresos Netos = {format_money(resultado.base_ingresos_netos, company.moneda)}"
    )
    df = _tabla(resultado.filas)
    df_mostrar = df.copy()
    df_mostrar["Valor"] = df_mostrar["Valor"].map(lambda v: format_money(v, company.moneda))
    df_mostrar["Participación %"] = df_mostrar["Participación %"].map(
        lambda v: format_percent(v) if v is not None else "No disponible"
    )
    st.dataframe(df_mostrar, hide_index=True, width="stretch")

    fig = px.bar(df, x="Cuenta", y="Participación %", title="Participación porcentual sobre los Ingresos Netos")
    st.plotly_chart(fig, width="stretch")

    from reports.excel_export import export_vertical_excel

    st.download_button(
        "Descargar Excel",
        data=export_vertical_excel(company, period, "Análisis Vertical — Estado de Resultados", df, resultado.base_ingresos_netos, "Ingresos Netos"),
        file_name=f"analisis_vertical_resultados_{period.anio}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
