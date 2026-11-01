"""Dashboard principal (seccion 10).

Los indicadores muestran su estado (calculations/banderas.py, hallazgo
M-08): el ROE se presenta como definitivo, APROXIMADO (con la causa) o NO
INTERPRETABLE, y los importes de un estado incompleto se etiquetan como
tales en lugar de presentarse como definitivos.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy.orm import Session

from calculations.balance_sheet import compute_balance_sheet
from calculations.banderas import (
    APROXIMADO,
    DEFINITIVO,
    banderas_balance,
    banderas_dupont,
    banderas_resultados,
    resumen,
)
from calculations.controls import conciliar_resultado
from calculations.dupont import compute_dupont
from calculations.income_statement import compute_income_statement
from components.money import format_money, format_percent
from database.enums import EstadoRegistro, TipoEstadoFinanciero
from database.models import Company
from database.repositories import get_statement_status, list_fiscal_periods


def _etiqueta(nombre: str, estado: str) -> str:
    return nombre if estado == DEFINITIVO else f"{nombre} ({estado})"


def _estado_roe(dp) -> tuple[str, str, str | None]:
    """(etiqueta, valor, explicacion) del ROE para el Dashboard."""
    if not dp.interpretable:
        return "ROE (DuPont)", "NO INTERPRETABLE", dp.motivo_no_disponible
    if not dp.disponible:
        return "ROE (DuPont)", "No disponible", dp.motivo_no_disponible
    banderas = banderas_dupont(dp)
    estado = resumen(banderas)
    if any(b.codigo == APROXIMADO for b in banderas):
        return f"ROE (DuPont) — {estado}", format_percent(dp.roe_dupont_pct), dp.fuente_saldos_iniciales
    if banderas:
        return f"ROE (DuPont) — {estado}", format_percent(dp.roe_dupont_pct), " ".join(b.texto for b in banderas)
    return "ROE (DuPont) — definitivo", format_percent(dp.roe_dupont_pct), None


def render(session: Session, company: Company) -> None:
    st.header("Dashboard")
    st.subheader(company.nombre_legal)

    periodos = list_fiscal_periods(session)
    if not periodos:
        st.info("Todavía no hay ningún ejercicio fiscal registrado. Comienza en 'Ingreso de datos'.")
        return

    ultimo = periodos[-1]
    bs = compute_balance_sheet(session, ultimo.id)
    inc = compute_income_statement(session, ultimo.id)
    dp = compute_dupont(session, ultimo)
    conciliacion = conciliar_resultado(bs, inc)
    estado_bs = resumen(banderas_balance(bs, conciliacion))
    estado_inc = resumen(banderas_resultados(inc, conciliacion))

    st.caption(f"Último ejercicio disponible: {ultimo.anio}")

    col1, col2, col3 = st.columns(3)
    col1.metric(_etiqueta("Total Activos", estado_bs), format_money(bs.total_activo, company.moneda) if bs.tiene_datos else "No disponible")
    col2.metric(_etiqueta("Total Pasivos", estado_bs), format_money(bs.total_pasivo, company.moneda) if bs.tiene_datos else "No disponible")
    col3.metric(_etiqueta("Patrimonio", estado_bs), format_money(bs.total_patrimonio, company.moneda) if bs.tiene_datos else "No disponible")

    col4, col5, col6 = st.columns(3)
    col4.metric(_etiqueta("Ingresos Netos", estado_inc),
                format_money(inc.ingresos_netos.subtotal, company.moneda) if inc.tiene_datos else "No disponible")
    col5.metric(_etiqueta("Utilidad Neta", estado_inc),
                format_money(inc.utilidad_neta, company.moneda) if inc.tiene_datos else "No disponible")
    etiqueta_roe, valor_roe, explicacion_roe = _estado_roe(dp)
    col6.metric(etiqueta_roe, valor_roe)
    if explicacion_roe:
        (st.error if valor_roe == "NO INTERPRETABLE" else st.warning)(f"{etiqueta_roe}: {explicacion_roe}")

    if bs.tiene_datos:
        estado_balance = get_statement_status(session, ultimo.id, TipoEstadoFinanciero.BALANCE)
        estado_resultados = get_statement_status(session, ultimo.id, TipoEstadoFinanciero.RESULTADOS)
        etiqueta = lambda e: "Revisado ✅" if e == EstadoRegistro.REVISADO else "Borrador ✏️"
        validacion_eq = "✅ cuadra" if bs.cuadra else f"⚠️ no cuadra (dif. {format_money(bs.diferencia, company.moneda)})"
        st.info(
            f"Estado Balance General: {etiqueta(estado_balance)} ({validacion_eq}; {estado_bs}) · "
            f"Estado de Resultados: {etiqueta(estado_resultados)} ({estado_inc})"
        )

    st.markdown("### Evolución entre ejercicios")
    anios_disponibles = [p.anio for p in periodos]
    seleccionados = st.multiselect("Ejercicios a comparar", anios_disponibles, default=anios_disponibles)
    if not seleccionados:
        return

    filas = []
    for periodo in periodos:
        if periodo.anio not in seleccionados:
            continue
        bs_p = compute_balance_sheet(session, periodo.id)
        inc_p = compute_income_statement(session, periodo.id)
        conciliacion_p = conciliar_resultado(bs_p, inc_p)
        filas.append(
            {
                "Año": periodo.anio,
                "Activos": float(bs_p.total_activo) if bs_p.tiene_datos else None,
                "Pasivos": float(bs_p.total_pasivo) if bs_p.tiene_datos else None,
                "Patrimonio": float(bs_p.total_patrimonio) if bs_p.tiene_datos else None,
                "Ingresos netos": float(inc_p.ingresos_netos.subtotal) if inc_p.tiene_datos else None,
                "Utilidad neta": float(inc_p.utilidad_neta) if inc_p.tiene_datos else None,
                "Estado Balance": resumen(banderas_balance(bs_p, conciliacion_p)) if bs_p.tiene_datos else "Sin datos",
                "Estado Resultados": resumen(banderas_resultados(inc_p, conciliacion_p)) if inc_p.tiene_datos else "Sin datos",
            }
        )
    df = pd.DataFrame(filas).sort_values("Año")

    fig = go.Figure()
    for columna in ["Activos", "Pasivos", "Patrimonio", "Ingresos netos", "Utilidad neta"]:
        if df[columna].notna().any():
            fig.add_trace(go.Scatter(x=df["Año"], y=df[columna], mode="lines+markers", name=columna))
    fig.update_layout(title="Evolución financiera por ejercicio", xaxis_title="Año", yaxis_title=f"Importe ({company.moneda})")
    st.plotly_chart(fig, width="stretch")
    st.caption("Las cifras de un ejercicio con estado distinto de DEFINITIVO no son definitivas.")

    st.dataframe(df, hide_index=True, width="stretch")
