"""Modulo de administracion de la empresa (seccion 4)."""
from __future__ import annotations

import streamlit as st
from sqlalchemy.orm import Session

from components.money import ANIO_MAXIMO, ANIO_MINIMO
from components.transacciones import ejecutar_escritura
from database.repositories import get_company, save_company


def render(session: Session) -> None:
    st.header("Datos de la empresa")
    company = get_company(session)

    with st.form("form_company"):
        nombre_legal = st.text_input("Nombre de la empresa", value=company.nombre_legal if company else "")
        nombre_comercial = st.text_input("Nombre comercial", value=company.nombre_comercial if company else "")
        actividad_economica = st.text_input("Actividad económica", value=company.actividad_economica if company else "")
        pais = st.text_input("País", value=company.pais if company else "")
        moneda = st.text_input("Moneda de presentación (ej. GTQ, USD)", value=company.moneda if company else "")
        anio_actual = company.anio_inicial_analisis if company else 2021
        anio_inicial = st.number_input(
            "Año inicial de análisis",
            min_value=min(ANIO_MINIMO, anio_actual),
            max_value=max(ANIO_MAXIMO, anio_actual),
            value=anio_actual,
            step=1,
        )
        enviado = st.form_submit_button("Guardar")

    if enviado:
        campos_obligatorios = [nombre_legal, nombre_comercial, actividad_economica, pais, moneda]
        if not all(c.strip() for c in campos_obligatorios):
            st.error("Todos los campos son obligatorios.")
            return
        guardado, _ = ejecutar_escritura(
            session,
            lambda: save_company(
                session,
                nombre_legal=nombre_legal.strip(),
                nombre_comercial=nombre_comercial.strip(),
                actividad_economica=actividad_economica.strip(),
                pais=pais.strip(),
                moneda=moneda.strip().upper(),
                anio_inicial_analisis=int(anio_inicial),
            ),
            descripcion="guardar los datos de la empresa",
        )
        if guardado:
            st.success("Datos de la empresa guardados correctamente.")
            st.rerun()

    if not company:
        st.info(
            "Registra primero los datos de la empresa para habilitar el resto de los módulos "
            "(catálogo de cuentas, captura de estados financieros, reportes)."
        )
