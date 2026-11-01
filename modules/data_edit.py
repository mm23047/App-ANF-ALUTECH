"""Modificacion de datos (seccion 8): consultar y modificar registros ya
capturados en un unico tablero por ejercicio, con historial de cambios.

La clasificacion de cuentas (categoria/subcategoria/estado) se edita en
el modulo Catalogo de cuentas -- aqui solo se modifican los IMPORTES
capturados, para no duplicar la logica de validacion de clasificacion.
"""
from __future__ import annotations

from decimal import Decimal

import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session

from calculations.balance_sheet import compute_balance_sheet
from components.money import format_money
from components.navigation import select_fiscal_period
from database.enums import TipoEstadoFinanciero as Tipo
from database.models import Company
from database.repositories import list_entries, list_history, upsert_entry


def _tabla_editable(session: Session, period_id: int, tipo: Tipo, moneda: str, key: str) -> None:
    entradas = list_entries(session, period_id, tipo)
    if not entradas:
        st.info("No hay cuentas con valores capturados todavía para este ejercicio.")
        return

    df = pd.DataFrame(
        [
            {
                "account_id": cuenta.id,
                "Código": cuenta.codigo,
                "Nombre": cuenta.nombre,
                "Categoría": cuenta.categoria_principal.value,
                "Subcategoría": cuenta.subcategoria.value if cuenta.subcategoria else "",
                "Valor": float(valor),
            }
            for cuenta, valor in entradas
        ]
    )

    editado = st.data_editor(
        df,
        hide_index=True,
        width="stretch",
        disabled=["account_id", "Código", "Nombre", "Categoría", "Subcategoría"],
        column_config={"Valor": st.column_config.NumberColumn(format="%.2f", step=0.01)},
        key=key,
    )

    col_guardar, col_cancelar = st.columns(2)
    with col_guardar:
        if st.button("Guardar cambios", key=f"{key}_guardar"):
            cambios = 0
            for _, fila in editado.iterrows():
                original = df.loc[df["account_id"] == fila["account_id"], "Valor"].iloc[0]
                if round(float(fila["Valor"]), 2) != round(float(original), 2):
                    upsert_entry(
                        session,
                        fiscal_period_id=period_id,
                        account_id=int(fila["account_id"]),
                        valor=Decimal(str(round(float(fila["Valor"]), 2))),
                        tipo=tipo,
                    )
                    cambios += 1
            if cambios:
                session.commit()
                st.success(f"{cambios} valor(es) actualizado(s).")
                st.rerun()
            else:
                st.info("No se detectaron cambios.")
    with col_cancelar:
        if st.button("Cancelar modificaciones", key=f"{key}_cancelar"):
            st.rerun()


def render(session: Session, company: Company) -> None:
    st.header("Modificación de datos")
    period = select_fiscal_period(session, key="periodo_edicion", allow_create=False)
    if period is None:
        return

    bs = compute_balance_sheet(session, period.id)
    if bs.tiene_datos:
        estado_eq = "✅ La ecuación contable cuadra." if bs.cuadra else f"⚠️ Diferencia de {format_money(bs.diferencia, company.moneda)} entre Activo y Pasivo+Patrimonio."
        st.caption(
            f"Activo: {format_money(bs.total_activo, company.moneda)} · "
            f"Pasivo+Patrimonio: {format_money(bs.total_pasivo_patrimonio, company.moneda)} · {estado_eq}"
        )

    tab_balance, tab_resultados, tab_historial = st.tabs(
        ["Balance General", "Estado de Resultados", "Historial de este ejercicio"]
    )

    with tab_balance:
        _tabla_editable(session, period.id, Tipo.BALANCE, company.moneda, key=f"editor_balance_{period.id}")
    with tab_resultados:
        _tabla_editable(session, period.id, Tipo.RESULTADOS, company.moneda, key=f"editor_resultados_{period.id}")
    with tab_historial:
        registros = [
            h for h in list_history(session, tabla_afectada="balance_entry")
            + list_history(session, tabla_afectada="income_entry")
        ]
        registros.sort(key=lambda h: h.fecha, reverse=True)
        if not registros:
            st.info("Sin modificaciones registradas.")
        else:
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "Fecha": h.fecha,
                            "Tabla": h.tabla_afectada,
                            "Operación": h.operacion,
                            "Campo": h.campo,
                            "Valor anterior": h.valor_anterior,
                            "Valor nuevo": h.valor_nuevo,
                        }
                        for h in registros
                    ]
                ),
                width="stretch",
            )
