"""Reporte de rentabilidad — Modelo DuPont de tres factores (seccion 9.5)."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy.orm import Session

from calculations.banderas import banderas_dupont
from calculations.dupont import DuPontResult, compute_dupont, generar_interpretacion
from components.avisos import mostrar_estado
from components.money import format_money, format_percent, format_ratio
from components.navigation import select_fiscal_period
from database.models import Company

NO_INTERPRETABLE = "NO INTERPRETABLE"
# Factores con 4 decimales: su producto reproduce el ROE mostrado (B-01).
DECIMALES_FACTOR = 4


def _tabla_resultados(resultado: DuPontResult, moneda: str, roe_valido: bool) -> pd.DataFrame:
    roe = format_percent(resultado.roe_dupont_pct) if roe_valido else NO_INTERPRETABLE
    roe_directo = format_percent(resultado.roe_directo_pct) if roe_valido else NO_INTERPRETABLE
    return pd.DataFrame(
        [
            {"Componente": "Utilidad neta", "Valor": format_money(resultado.utilidad_neta, moneda)},
            {"Componente": "Ingresos netos", "Valor": format_money(resultado.ingresos_netos, moneda)},
            {"Componente": "Activo total inicial", "Valor": format_money(resultado.activo_inicial, moneda)},
            {"Componente": "Activo total final", "Valor": format_money(resultado.activo_final, moneda)},
            {"Componente": "Activo total promedio", "Valor": format_money(resultado.activo_promedio, moneda)},
            {"Componente": "Patrimonio inicial", "Valor": format_money(resultado.patrimonio_inicial, moneda)},
            {"Componente": "Patrimonio final", "Valor": format_money(resultado.patrimonio_final, moneda)},
            {"Componente": "Patrimonio promedio", "Valor": format_money(resultado.patrimonio_promedio, moneda)},
            {"Componente": "Margen neto", "Valor": format_percent(resultado.margen_neto * 100, DECIMALES_FACTOR)},
            {"Componente": "Rotación de activos", "Valor": format_ratio(resultado.rotacion_activos, DECIMALES_FACTOR)},
            {"Componente": "Multiplicador del capital", "Valor": format_ratio(resultado.multiplicador_capital, DECIMALES_FACTOR)},
            {"Componente": "ROE (DuPont)", "Valor": roe},
            {"Componente": "ROE directo (utilidad neta / patrimonio promedio)", "Valor": roe_directo},
        ]
    )


def _mostrar_controles(resultado: DuPontResult) -> None:
    st.markdown("### Controles de los datos")
    # st.table ajusta el detalle en varias lineas (en st.dataframe se cortaba: hallazgo O-5).
    st.table(
        pd.DataFrame(
            [{"Control": c.nombre, "Resultado": "✅ Correcto" if c.correcto else "⚠️ Revisar", "Detalle": c.detalle}
             for c in resultado.controles]
        ),
        hide_index=True,
    )


def render(session: Session, company: Company) -> None:
    st.header("Reporte — Análisis de Rentabilidad (Modelo DuPont)")
    st.caption("Criterio: el ROE se calcula con el patrimonio total del Balance (incluida, si se captura, la "
               "participación no controladora). Puede revisarse al disponer de los estados publicados.")
    period = select_fiscal_period(session, key="periodo_dupont", allow_create=False)
    if period is None:
        return

    resultado = compute_dupont(session, period)
    if resultado.disponible or not resultado.interpretable:
        mostrar_estado(banderas_dupont(resultado))
    if not resultado.interpretable:
        st.error(resultado.motivo_no_disponible)
        for advertencia in resultado.advertencias:
            st.warning(advertencia)
        st.markdown("### Tabla de resultados (solo referencia)")
        st.dataframe(_tabla_resultados(resultado, company.moneda, roe_valido=False), hide_index=True, width="stretch", height="content")
        _mostrar_controles(resultado)
        st.info("No se genera interpretación automática porque el ROE no es interpretable.")
        _descargas(company, period, resultado)
        return
    if not resultado.disponible:
        st.info(resultado.motivo_no_disponible)
        for advertencia in resultado.advertencias:
            st.warning(advertencia)
        return

    if resultado.saldos_aproximados:
        st.warning(f"ROE APROXIMADO. {resultado.fuente_saldos_iniciales}.")
    else:
        st.caption(f"Fuente de saldos iniciales: {resultado.fuente_saldos_iniciales}")
    for advertencia in resultado.advertencias:
        if not advertencia.startswith("APROXIMADO"):
            st.warning(advertencia)

    col1, col2, col3 = st.columns(3)
    col1.metric("Margen neto", format_percent(resultado.margen_neto * 100, DECIMALES_FACTOR))
    col2.metric("Rotación de activos", format_ratio(resultado.rotacion_activos, DECIMALES_FACTOR))
    col3.metric("Multiplicador del capital", format_ratio(resultado.multiplicador_capital, DECIMALES_FACTOR))

    col4, col5 = st.columns(2)
    sufijo = " (aproximado)" if resultado.saldos_aproximados else ""
    col4.metric(f"ROE (DuPont){sufijo}", format_percent(resultado.roe_dupont_pct))
    col5.metric(f"ROE directo{sufijo}", format_percent(resultado.roe_directo_pct))
    st.caption("Los factores se muestran con 4 decimales para que su producto reproduzca el ROE mostrado. "
               "El ROE DuPont y el ROE directo son iguales por construcción; no se usan como control.")

    st.markdown("### Tabla de resultados")
    st.dataframe(_tabla_resultados(resultado, company.moneda, roe_valido=True), hide_index=True, width="stretch", height="content")
    _mostrar_controles(resultado)

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
    _descargas(company, period, resultado)


def _descargas(company, period, resultado: DuPontResult) -> None:
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
