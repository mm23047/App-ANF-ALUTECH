"""Reporte de Balance General (seccion 9.1)."""
from __future__ import annotations

import streamlit as st
from sqlalchemy.orm import Session

from calculations.balance_sheet import compute_balance_sheet
from calculations.banderas import banderas_balance
from calculations.controls import conciliar_resultado
from calculations.income_statement import compute_income_statement
from components.avisos import mostrar_avisos_signo, mostrar_completitud, mostrar_conciliacion, mostrar_estado
from components.money import format_money
from components.navigation import select_fiscal_period
from components.tables import mostrar_grupo, mostrar_total
from components.texto import md
from database.models import Company


def render(session: Session, company: Company) -> None:
    st.header("Reporte — Balance General")
    period = select_fiscal_period(session, key="periodo_reporte_balance", allow_create=False)
    if period is None:
        return

    bs = compute_balance_sheet(session, period.id)
    if not bs.tiene_datos:
        st.info("No hay datos de Balance General capturados para este ejercicio.")
        return

    st.subheader(f"{md(company.nombre_legal)} — Balance General al cierre del ejercicio {period.anio}")
    st.caption(f"Moneda: {md(company.moneda)}")
    conciliacion = conciliar_resultado(bs, compute_income_statement(session, period.id))
    banderas = banderas_balance(bs, conciliacion)
    mostrar_estado(banderas)

    if bs.cuadra:
        st.success("La ecuación contable cuadra: Activo total = Pasivo total + Patrimonio total.")
    else:
        st.error(
            f"La ecuación contable NO cuadra. Diferencia: {md(format_money(bs.diferencia, company.moneda))} "
            "(Activo total − (Pasivo total + Patrimonio total))."
        )
    mostrar_completitud(bs, "Balance General")
    mostrar_avisos_signo(bs)

    st.markdown("### Activo")
    mostrar_grupo(bs.activo_corriente, company.moneda)
    mostrar_grupo(bs.activo_no_corriente, company.moneda)
    mostrar_total("Total Activo", bs.total_activo, company.moneda)

    st.markdown("### Pasivo")
    mostrar_grupo(bs.pasivo_corriente, company.moneda)
    mostrar_grupo(bs.pasivo_no_corriente, company.moneda)
    mostrar_total("Total Pasivo", bs.total_pasivo, company.moneda)

    st.markdown("### Patrimonio")
    for grupo in bs.patrimonio_grupos:
        mostrar_grupo(grupo, company.moneda)
    mostrar_total("Total Patrimonio", bs.total_patrimonio, company.moneda)

    mostrar_total("Total Pasivo + Patrimonio", bs.total_pasivo_patrimonio, company.moneda)

    mostrar_conciliacion(conciliacion, company.moneda)

    st.markdown("### Exportar")
    col1, col2 = st.columns(2)
    with col1:
        from reports.pdf_export import export_balance_pdf

        st.download_button(
            "Descargar PDF",
            data=export_balance_pdf(company, period, bs, banderas),
            file_name=f"balance_general_{period.anio}.pdf",
            mime="application/pdf",
        )
    with col2:
        from reports.excel_export import export_balance_excel

        st.download_button(
            "Descargar Excel",
            data=export_balance_excel(company, period, bs, banderas),
            file_name=f"balance_general_{period.anio}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
