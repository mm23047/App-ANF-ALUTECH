"""Reporte de rentabilidad — Modelo DuPont de tres factores (seccion 9.5)."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy.orm import Session

from calculations.dupont import compute_dupont, generar_interpretacion
from components.money import format_money, format_percent, format_ratio
from components.navigation import select_fiscal_period
from database.models import Company


def render(session: Session, company: Company) -> None:
    st.header("Reporte — Análisis de Rentabilidad (Modelo DuPont)")
    period = select_fiscal_period(session, key="periodo_dupont", allow_create=False)
    if period is None:
        return

    resultado = compute_dupont(session, period)
    if not resultado.disponible:
        st.info(resultado.motivo_no_disponible)
        return

    if resultado.saldos_aproximados:
        st.warning(
            f"Saldos iniciales aproximados: {resultado.fuente_saldos_iniciales}. "
            "Los promedios (y por lo tanto el ROE) deben interpretarse con esta limitación."
        )
    else:
        st.caption(f"Fuente de saldos iniciales: {resultado.fuente_saldos_iniciales}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Margen neto", format_percent(resultado.margen_neto * 100))
    col2.metric("Rotación de activos", format_ratio(resultado.rotacion_activos))
    col3.metric("Multiplicador del capital", format_ratio(resultado.multiplicador_capital))

    col4, col5 = st.columns(2)
    col4.metric("ROE (DuPont)", format_percent(resultado.roe_dupont_pct))
    col5.metric("ROE directo", format_percent(resultado.roe_directo_pct))

    if resultado.coincide_redondeo:
        st.success("El ROE calculado por el modelo DuPont coincide con el ROE directo (considerando el redondeo).")
    else:
        st.error("El ROE calculado por el modelo DuPont NO coincide con el ROE directo. Revisar los datos capturados.")

    st.markdown("### Tabla de resultados")
    df = pd.DataFrame(
        [
            {"Componente": "Utilidad neta", "Valor": format_money(resultado.utilidad_neta, company.moneda)},
            {"Componente": "Ingresos netos", "Valor": format_money(resultado.ingresos_netos, company.moneda)},
            {"Componente": "Activo total inicial", "Valor": format_money(resultado.activo_inicial, company.moneda)},
            {"Componente": "Activo total final", "Valor": format_money(resultado.activo_final, company.moneda)},
            {"Componente": "Activo total promedio", "Valor": format_money(resultado.activo_promedio, company.moneda)},
            {"Componente": "Patrimonio inicial", "Valor": format_money(resultado.patrimonio_inicial, company.moneda)},
            {"Componente": "Patrimonio final", "Valor": format_money(resultado.patrimonio_final, company.moneda)},
            {"Componente": "Patrimonio promedio", "Valor": format_money(resultado.patrimonio_promedio, company.moneda)},
            {"Componente": "Margen neto", "Valor": format_percent(resultado.margen_neto * 100)},
            {"Componente": "Rotación de activos", "Valor": format_ratio(resultado.rotacion_activos)},
            {"Componente": "Multiplicador del capital", "Valor": format_ratio(resultado.multiplicador_capital)},
            {"Componente": "ROE (DuPont)", "Valor": format_percent(resultado.roe_dupont_pct)},
            {"Componente": "ROE directo", "Valor": format_percent(resultado.roe_directo_pct)},
        ]
    )
    st.dataframe(df, hide_index=True, width="stretch")

    st.markdown("### Representación gráfica de los tres componentes")
    fig = go.Figure(
        go.Bar(
            x=["Margen neto (%)", "Rotación de activos (veces)", "Multiplicador del capital (veces)"],
            y=[float(resultado.margen_neto * 100), float(resultado.rotacion_activos), float(resultado.multiplicador_capital)],
        )
    )
    fig.update_layout(title="Componentes del modelo DuPont")
    st.plotly_chart(fig, width="stretch")

    st.markdown("### Interpretación financiera automática")
    st.write(generar_interpretacion(resultado))

    from reports.excel_export import export_dupont_excel
    from reports.pdf_export import export_dupont_pdf

    col_pdf, col_xlsx = st.columns(2)
    with col_pdf:
        st.download_button(
            "Descargar PDF",
            data=export_dupont_pdf(company, period, resultado),
            file_name=f"analisis_dupont_{period.anio}.pdf",
            mime="application/pdf",
        )
    with col_xlsx:
        st.download_button(
            "Descargar Excel",
            data=export_dupont_excel(company, period, resultado),
            file_name=f"analisis_dupont_{period.anio}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
