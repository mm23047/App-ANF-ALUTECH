"""Helpers de presentacion de tablas financieras (reutilizado por los
reportes de Balance y Estado de Resultados)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from components.money import format_money


def mostrar_grupo(grupo, moneda: str) -> None:
    """Renderiza un Grupo (lineas + subtotal) como tabla + fila de subtotal."""
    if not grupo.lineas:
        return
    st.markdown(f"**{grupo.nombre}**")
    df = pd.DataFrame(
        [
            {"Código": l.cuenta.codigo, "Cuenta": l.cuenta.nombre, "Importe": format_money(l.valor, moneda)}
            for l in grupo.lineas
        ]
    )
    st.dataframe(df, hide_index=True, width="stretch")
    st.markdown(f"<div style='text-align:right'><b>Subtotal {grupo.nombre}: {format_money(grupo.subtotal, moneda)}</b></div>", unsafe_allow_html=True)
    st.markdown("---")


def mostrar_total(etiqueta: str, valor, moneda: str) -> None:
    st.markdown(
        f"<div style='text-align:right; font-size:1.1em'><b>{etiqueta}: {format_money(valor, moneda)}</b></div>",
        unsafe_allow_html=True,
    )
