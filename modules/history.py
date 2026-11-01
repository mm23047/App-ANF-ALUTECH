"""Historial de cambios global (secciones 8 y 17)."""
from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session

from database.repositories import list_history

TABLAS = [
    "company",
    "fiscal_period",
    "account",
    "balance_entry",
    "income_entry",
    "initial_balance",
    "statement_status",
]


def render(session: Session) -> None:
    st.header("Historial de cambios")

    tabla_sel = st.selectbox("Filtrar por tabla", ["(Todas)"] + TABLAS)
    tabla_filtro = None if tabla_sel == "(Todas)" else tabla_sel

    registros = list_history(session, tabla_afectada=tabla_filtro)
    if not registros:
        st.info("No hay modificaciones registradas todavía.")
        return

    st.dataframe(
        pd.DataFrame(
            [
                {
                    "Fecha": h.fecha,
                    "Tabla": h.tabla_afectada,
                    "Registro": h.registro_id,
                    "Operación": h.operacion,
                    "Campo": h.campo,
                    "Valor anterior": h.valor_anterior,
                    "Valor nuevo": h.valor_nuevo,
                }
                for h in registros
            ]
        ),
        width="stretch",
        height=600,
    )
