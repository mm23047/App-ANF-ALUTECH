"""Reporte de rentabilidad — Modelo DuPont con saldos al cierre (trabajo ANF,
secciones 8.4, 9.5 y 9.6). Enfoque total y enfoque de la controladora, por separado."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy.orm import Session

from calculations.banderas import banderas_dupont
from calculations.rubros import datos_todos
from calculations.dupont import (
    BASE_SALDOS,
    DuPontResult,
    compute_dupont,
    filas_enfoque_controladora,
    filas_enfoque_total,
    formatear_fila,
    generar_interpretacion,
    interpretacion_controladora,
)
from components.avisos import mostrar_estado
from components.money import format_percent, format_ratio
from components.navigation import select_fiscal_period
from components.secciones_ui import descargas, mostrar_seccion
from components.tables import columnas_derecha
from components.texto import md
from database.models import Company
from reports import secciones as sec

# Factores con 4 decimales: su producto reproduce el ROE mostrado (B-01).
DECIMALES_FACTOR = 4
ICONO_CONTROL = {"Correcto": "✅", "Revisar": "⚠️", "Sin datos para conciliar": "ℹ️"}


def _tabla(filas, moneda: str) -> pd.DataFrame:
    return pd.DataFrame([{"Componente": f.etiqueta, "Valor": formatear_fila(f, moneda)} for f in filas],
                        columns=["Componente", "Valor"])


def _comparativo(session: Session, company: Company) -> None:
    """Tablas de las secciones 9.5 y 9.6 del trabajo: todos los ejercicios, enfoque total y de la controladora."""
    lista = [d for d in datos_todos(session) if d.tiene_datos]
    if not lista:
        return
    st.markdown("### Comparativo de los ejercicios")
    secciones = sec.dupont(lista)
    for seccion in secciones:
        mostrar_seccion(seccion)
    descargas(company, f"Análisis DuPont {lista[0].anio}–{lista[-1].anio}", [("DuPont", secciones)], "analisis_dupont_comparativo",
              clave="dupont_comparativo")


def _mostrar_enfoques(resultado: DuPontResult, moneda: str, sufijo: str = "") -> None:
    st.markdown(f"### Enfoque total{sufijo}")
    st.dataframe(_tabla(filas_enfoque_total(resultado), moneda), hide_index=True, width="stretch", height="content",
                 column_config=columnas_derecha("Valor"))
    if resultado.controladora is None:
        return
    st.markdown(f"### Enfoque de la controladora{sufijo}")
    st.caption("Usa la ganancia y el patrimonio atribuibles a los propietarios de la controladora; los activos son los "
               f"totales de la empresa. Ganancia atribuible: {md(resultado.controladora.fuente)}.")
    st.dataframe(_tabla(filas_enfoque_controladora(resultado), moneda), hide_index=True, width="stretch", height="content",
                 column_config=columnas_derecha("Valor"))


def _mostrar_controles(resultado: DuPontResult) -> None:
    st.markdown("### Controles de los datos")
    # st.table ajusta el detalle en varias lineas (en st.dataframe se cortaba: hallazgo O-5).
    st.table(
        pd.DataFrame(
            [{"Control": c.nombre, "Resultado": f"{ICONO_CONTROL[c.resultado]} {c.resultado}", "Detalle": c.detalle}
             for c in resultado.controles]
        ),
        hide_index=True,
    )


def render(session: Session, company: Company) -> None:
    st.header("Reporte — Análisis de Rentabilidad (Modelo DuPont)")
    st.caption(BASE_SALDOS)
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
        _mostrar_enfoques(resultado, company.moneda, " (solo referencia)")
        _mostrar_controles(resultado)
        st.info("No se genera interpretación automática porque el ROE no es interpretable.")
        _descargas(company, period, resultado)
        _comparativo(session, company)
        return
    if not resultado.disponible:
        st.info(resultado.motivo_no_disponible)
        for advertencia in resultado.advertencias:
            st.warning(advertencia)
        return

    for advertencia in resultado.advertencias:
        st.warning(advertencia)

    col1, col2, col3 = st.columns(3)
    col1.metric("Margen neto", format_percent(resultado.margen_neto * 100, DECIMALES_FACTOR))
    col2.metric("Rotación de activos", format_ratio(resultado.rotacion_activos, DECIMALES_FACTOR))
    col3.metric("RSA / ROA", format_percent(resultado.rsa * 100, DECIMALES_FACTOR))

    col4, col5, col6 = st.columns(3)
    col4.metric("Multiplicador del capital (MAF)", format_ratio(resultado.multiplicador_capital, DECIMALES_FACTOR))
    col5.metric("RSP / ROE DuPont", format_percent(resultado.roe_dupont_pct))
    col6.metric("ROE directo (comprobación)", format_percent(resultado.roe_directo_pct))
    st.caption("Los factores se muestran con 4 decimales para que su producto reproduzca el ROE mostrado. "
               "El ROE DuPont y el ROE directo son iguales por construcción; no se usan como control.")

    _mostrar_enfoques(resultado, company.moneda)
    _mostrar_controles(resultado)

    st.markdown("### Representación gráfica de los tres componentes")
    fig = go.Figure(
        go.Bar(
            x=["Margen neto (%)", "Rotación de activos (veces)", "Multiplicador del capital (veces)"],
            y=[float(resultado.margen_neto * 100), float(resultado.rotacion_activos), float(resultado.multiplicador_capital)],
        )
    )
    fig.update_layout(title="Componentes del modelo DuPont (enfoque total)")
    st.plotly_chart(fig, width="stretch")

    st.markdown("### Interpretación financiera automática")
    st.write(generar_interpretacion(resultado))
    controladora = interpretacion_controladora(resultado)
    if controladora:
        st.write(controladora)
    _descargas(company, period, resultado)
    _comparativo(session, company)


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
