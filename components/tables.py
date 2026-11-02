"""Helpers de presentacion de tablas financieras (reutilizado por los
reportes de Balance y Estado de Resultados).

Subtotales y totales con st.markdown nativo (sin HTML): el nombre del
grupo y la moneda se escapan con components.texto.md (hallazgo B-04)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from components.money import format_money
from components.texto import md


def mostrar_grupo(grupo, moneda: str) -> None:
    """Renderiza un Grupo (lineas + subtotal) como tabla + fila de subtotal."""
    if not grupo.lineas:
        return
    st.markdown(f"**{md(grupo.nombre)}**")
    df = pd.DataFrame(
        [
            {"Código": l.cuenta.codigo, "Cuenta": l.cuenta.nombre, "Importe": format_money(l.valor, moneda)}
            for l in grupo.lineas
        ]
    )
    st.dataframe(df, hide_index=True, width="stretch")
    st.markdown(f"**Subtotal {md(grupo.nombre)}: {md(format_money(grupo.subtotal, moneda))}**", text_alignment="right")
    st.markdown("---")


def mostrar_total(etiqueta: str, valor, moneda: str) -> None:
    st.markdown(f"**{md(etiqueta)}: {md(format_money(valor, moneda))}**", text_alignment="right")
