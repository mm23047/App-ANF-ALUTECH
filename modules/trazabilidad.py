"""Datos originales: trazabilidad de cada importe y controles de la carga.

Muestra, para cada importe cargado desde los documentos, el documento, la
pagina, el estado financiero y la denominacion original, y compara los
totales impresos con los calculados. Tambien el mapeo de cada cuenta a su
grupo de analisis y a los indicadores en los que participa. Solo lectura.
"""
from __future__ import annotations

import streamlit as st
from sqlalchemy.orm import Session

from calculations.controles_carga import OK
from calculations.rubros import datos_todos
from components.secciones_ui import descargas, mostrar_seccion
from database.models import Company
from reports import secciones as sec


def render(session: Session, company: Company) -> None:
    st.header("Datos originales — Trazabilidad y controles de carga")
    lista = [d for d in datos_todos(session) if d.tiene_datos]
    if not lista:
        st.info("No hay ejercicios con datos capturados.")
        return
    controles, fuentes, complementarios = sec.trazabilidad(session, lista)
    malos = [f for f in controles.filas if f[6] != OK]
    alterados = [f for f in fuentes.filas if f[8] != OK]
    col1, col2, col3 = st.columns(3)
    col1.metric("Totales impresos verificados", f"{len(controles.filas) - len(malos)}/{len(controles.filas)}")
    col2.metric("Importes con fuente documentada", len(fuentes.filas))
    col3.metric("Importes modificados después de la carga", len(alterados))
    if malos:
        st.error(f"{len(malos)} total(es) calculado(s) no coinciden con el documento. Revise la transcripción o la clasificación.")
    if alterados:
        st.warning(f"{len(alterados)} importe(s) ya no son los cargados desde el documento (ver columna Control).")
    if not controles.filas and not fuentes.filas:
        st.info("Los importes de esta base no se cargaron con el script de datos originales: no tienen fuente registrada. "
                "Para cargar Alutech 2021–2025 ejecute «python scripts/cargar_alutech.py» con la aplicación cerrada.")
    tab_controles, tab_fuentes, tab_compl, tab_mapeo = st.tabs(
        ["Controles de totales", "Fuente de cada importe", "Datos complementarios", "Mapeo de cuentas"])
    mapeo = sec.mapeo_cuentas(session)
    with tab_controles:
        mostrar_seccion(controles)
    with tab_fuentes:
        mostrar_seccion(fuentes, notas_plegadas=True)
    with tab_compl:
        mostrar_seccion(complementarios)
    with tab_mapeo:
        mostrar_seccion(mapeo)
    descargas(company, "Datos originales: trazabilidad y controles", [("Trazabilidad", [controles, fuentes, complementarios]),
                                                                      ("Mapeo de cuentas", [mapeo])],
              "trazabilidad_datos_originales", clave="trazabilidad")
