"""Historial de cambios global (secciones 8 y 17).

Cada fila identifica fecha, operacion, tabla, id real del registro,
ejercicio, cuenta (codigo y nombre), valores anterior y nuevo y lote
(hallazgo A-08). Las filas anteriores a la migracion v1 no tienen
ejercicio ni cuenta registrados y se marcan como tales.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session

from database.models import ChangeHistory
from database.repositories import list_accounts, list_fiscal_periods, list_history

TABLAS = [
    "company",
    "fiscal_period",
    "account",
    "balance_entry",
    "income_entry",
    "initial_balance",
    "statement_status",
]

SIN_REGISTRAR = "(no registrado)"
# Tablas en las que el historial actual siempre registra ejercicio / cuenta;
# si falta, la fila es anterior a la migracion v1.
TABLAS_CON_EJERCICIO = {"fiscal_period", "balance_entry", "income_entry", "initial_balance", "statement_status"}
TABLAS_CON_CUENTA = {"account", "balance_entry", "income_entry", "initial_balance"}


def historial_dataframe(session: Session, registros: list[ChangeHistory]) -> pd.DataFrame:
    anios = {p.id: p.anio for p in list_fiscal_periods(session)}
    cuentas = {c.id: c for c in list_accounts(session)}

    def ejercicio(h: ChangeHistory) -> str:
        if h.fiscal_period_id is None:
            return SIN_REGISTRAR if h.tabla_afectada in TABLAS_CON_EJERCICIO else "—"
        return str(anios.get(h.fiscal_period_id, f"(eliminado, id {h.fiscal_period_id})"))

    def cuenta(h: ChangeHistory) -> str:
        if h.account_id is None:
            return SIN_REGISTRAR if h.tabla_afectada in TABLAS_CON_CUENTA else "—"
        c = cuentas.get(h.account_id)
        return f"{c.codigo} — {c.nombre}" if c else f"(id {h.account_id})"

    return pd.DataFrame(
        [
            {
                "Fecha": h.fecha,
                "Operación": h.operacion,
                "Tabla": h.tabla_afectada,
                "Registro": h.registro_id,
                "Ejercicio": ejercicio(h),
                "Cuenta": cuenta(h),
                "Campo": h.campo,
                "Valor anterior": h.valor_anterior,
                "Valor nuevo": h.valor_nuevo,
                "Lote": h.lote_id[:8] if h.lote_id else "",
            }
            for h in registros
        ]
    )


def render(session: Session) -> None:
    st.header("Historial de cambios")
    st.caption(
        f"Los cambios anteriores a la actualización del historial no tienen ejercicio ni cuenta registrados "
        f"y se muestran como '{SIN_REGISTRAR}'. En ellos, 'Registro' puede corresponder al id de la cuenta."
    )

    periodos = list_fiscal_periods(session)
    cuentas = list_accounts(session)
    col1, col2, col3 = st.columns(3)
    with col1:
        tabla_sel = st.selectbox("Filtrar por tabla", ["(Todas)"] + TABLAS)
    with col2:
        periodo_sel = st.selectbox(
            "Filtrar por ejercicio", [None] + [p.id for p in periodos],
            format_func=lambda i: "(Todos)" if i is None else str(next(p.anio for p in periodos if p.id == i)),
        )
    with col3:
        cuenta_sel = st.selectbox(
            "Filtrar por cuenta", [None] + [c.id for c in cuentas],
            format_func=lambda i: "(Todas)" if i is None else next(f"{c.codigo} — {c.nombre}" for c in cuentas if c.id == i),
        )

    registros = list_history(
        session,
        tabla_afectada=None if tabla_sel == "(Todas)" else tabla_sel,
        fiscal_period_id=periodo_sel,
        account_id=cuenta_sel,
    )
    if not registros:
        st.info("No hay modificaciones registradas con estos filtros.")
        return

    st.dataframe(historial_dataframe(session, registros), width="stretch", height=600)
