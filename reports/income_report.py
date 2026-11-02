"""Reporte de Estado de Resultados (seccion 9.2)."""
from __future__ import annotations

import streamlit as st
from sqlalchemy.orm import Session

from calculations.balance_sheet import compute_balance_sheet
from calculations.banderas import banderas_resultados
from calculations.controls import conciliar_resultado
from calculations.income_statement import compute_income_statement
from calculations.validation import CONVENCION_SIGNOS
from components.avisos import mostrar_avisos_signo, mostrar_completitud, mostrar_conciliacion, mostrar_estado
from components.navigation import select_fiscal_period
from components.tables import mostrar_grupo, mostrar_total
from components.texto import md
from database.models import Company


def render(session: Session, company: Company) -> None:
    st.header("Reporte — Estado de Resultados")
    period = select_fiscal_period(session, key="periodo_reporte_resultados", allow_create=False)
    if period is None:
        return

    inc = compute_income_statement(session, period.id)
    if not inc.tiene_datos:
        st.info("No hay datos de Estado de Resultados capturados para este ejercicio.")
        return

    st.subheader(f"{md(company.nombre_legal)} — Estado de Resultados del ejercicio {period.anio}")
    st.caption(f"Moneda: {md(company.moneda)} · Los costos, gastos e impuestos se capturan en positivo y se restan.")
    conciliacion = conciliar_resultado(compute_balance_sheet(session, period.id), inc)
    banderas = banderas_resultados(inc, conciliacion)
    mostrar_estado(banderas)
    mostrar_completitud(inc, "Estado de Resultados")
    mostrar_avisos_signo(inc)

    mostrar_grupo(inc.ingresos_netos, company.moneda)
    mostrar_grupo(inc.costo_ventas, company.moneda)
    mostrar_total("Utilidad bruta", inc.utilidad_bruta, company.moneda)
    st.markdown("---")

    mostrar_grupo(inc.gastos_administracion, company.moneda)
    mostrar_grupo(inc.gastos_ventas, company.moneda)
    mostrar_grupo(inc.otros_ingresos_operativos, company.moneda)
    mostrar_grupo(inc.otros_gastos_operativos, company.moneda)
    mostrar_total("Utilidad operativa", inc.utilidad_operativa, company.moneda)
    st.markdown("---")

    mostrar_grupo(inc.ingresos_financieros, company.moneda)
    mostrar_grupo(inc.gastos_financieros, company.moneda)
    mostrar_total("Resultado financiero", inc.resultado_financiero, company.moneda)
    mostrar_grupo(inc.otros_ingresos_no_operativos, company.moneda)
    mostrar_grupo(inc.otros_gastos_no_operativos, company.moneda)
    mostrar_total("Otros resultados", inc.otros_resultados, company.moneda)
    mostrar_total("Utilidad antes de impuestos", inc.utilidad_antes_impuestos, company.moneda)
    st.markdown("---")

    mostrar_grupo(inc.impuesto_renta, company.moneda)
    mostrar_total("Utilidad neta", inc.utilidad_neta, company.moneda)

    mostrar_conciliacion(conciliacion, company.moneda)
    st.caption(CONVENCION_SIGNOS)

    st.markdown("### Exportar")
    col1, col2 = st.columns(2)
    with col1:
        from reports.pdf_export import export_income_pdf

        st.download_button(
            "Descargar PDF",
            data=export_income_pdf(company, period, inc, banderas),
            file_name=f"estado_resultados_{period.anio}.pdf",
            mime="application/pdf",
        )
    with col2:
        from reports.excel_export import export_income_excel

        st.download_button(
            "Descargar Excel",
            data=export_income_excel(company, period, inc, banderas),
            file_name=f"estado_resultados_{period.anio}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
