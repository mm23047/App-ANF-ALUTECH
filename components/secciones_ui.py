"""Presentacion en pantalla de las secciones del analisis 2021-2025 y sus
descargas (las mismas secciones que exportan el Excel y el PDF)."""
from __future__ import annotations

from types import SimpleNamespace

import pandas as pd
import streamlit as st

from components.tables import columnas_derecha
from components.texto import md
from reports.secciones import TEXTO, Seccion, formatear, tipo_celda


def a_dataframe(seccion: Seccion) -> pd.DataFrame:
    return pd.DataFrame(
        [[formatear(v, tipo_celda(seccion, fila, i)) for i, v in enumerate(fila)] for fila in seccion.filas],
        columns=[c.nombre for c in seccion.columnas],
    )


def mostrar_seccion(seccion: Seccion, *, notas_plegadas: bool = False) -> None:
    st.markdown(f"#### {md(seccion.titulo)}")
    if not seccion.filas:
        st.info("Sin datos para esta sección.")
    else:
        configuracion = columnas_derecha(*(c.nombre for c in seccion.columnas if c.tipo != TEXTO))
        if seccion.columnas[0].tipo == TEXTO:  # la denominacion de la partida no se corta
            configuracion[seccion.columnas[0].nombre] = st.column_config.TextColumn(width="large")
        st.dataframe(a_dataframe(seccion), hide_index=True, width="stretch", height="content", column_config=configuracion)
    if seccion.notas:
        if notas_plegadas and len(seccion.notas) > 3:
            with st.expander(f"Notas ({len(seccion.notas)})"):
                for nota in seccion.notas:
                    st.caption(md(nota))
        else:
            for nota in seccion.notas:
                st.caption(md(nota))


def descargas(company, titulo: str, hojas: list[tuple[str, list[Seccion]]], archivo: str, *, clave: str) -> None:
    from reports.exportar_secciones import secciones_a_excel, secciones_a_pdf

    col_pdf, col_xlsx = st.columns(2)
    secciones = [s for _, lista in hojas for s in lista]
    # El archivo se genera al pulsar el boton: asi no se rehace cada exportacion al redibujar la pagina. Se copian
    # los datos de la empresa porque, para entonces, la sesion de la base de datos ya esta cerrada.
    empresa = SimpleNamespace(nombre_legal=company.nombre_legal, moneda=company.moneda)
    with col_pdf:
        st.download_button("Descargar PDF", data=lambda: secciones_a_pdf(empresa, titulo, secciones), file_name=f"{archivo}.pdf",
                           mime="application/pdf", key=f"{clave}_pdf")
    with col_xlsx:
        st.download_button("Descargar Excel", data=lambda: secciones_a_excel(empresa, titulo, hojas), file_name=f"{archivo}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", key=f"{clave}_xlsx")
