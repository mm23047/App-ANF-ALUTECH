"""Helpers de presentacion de tablas financieras (reutilizado por los
reportes de Balance y Estado de Resultados).

Subtotales y totales con st.markdown nativo (sin HTML): el nombre del
grupo y la moneda se escapan con components.texto.md (hallazgo B-04)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from calculations.validation import lineas_reportables
from components.money import format_money
from components.texto import md


def columnas_derecha(*nombres: str) -> dict:
    """Configuracion de st.dataframe: las cifras se presentan como texto ya formateado, alineadas a la derecha."""
    return {nombre: st.column_config.TextColumn(alignment="right") for nombre in nombres}


def mostrar_grupo(grupo, moneda: str) -> None:
    """Renderiza un Grupo (lineas + subtotal) como tabla + fila de subtotal."""
    lineas = lineas_reportables(grupo)
    if not lineas:
        return
    st.markdown(f"**{md(grupo.nombre)}**")
    df = pd.DataFrame(
        [
            {"Código": l.cuenta.codigo, "Cuenta": l.cuenta.nombre, "Importe": format_money(l.valor, moneda)}
            for l in lineas
        ]
    )
    st.dataframe(df, hide_index=True, width="stretch", height="content", column_config=columnas_derecha("Importe"))
    st.markdown(f"**Subtotal {md(grupo.nombre)}: {md(format_money(grupo.subtotal, moneda))}**", text_alignment="right")
    st.markdown("---")


def mostrar_total(etiqueta: str, valor, moneda: str) -> None:
    st.markdown(f"**{md(etiqueta)}: {md(format_money(valor, moneda))}**", text_alignment="right")
