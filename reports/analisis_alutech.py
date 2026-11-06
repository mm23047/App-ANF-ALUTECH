"""Paginas del analisis financiero 2021-2025 (adaptacion Alutech).

Todas leen los datos originales de la BD, calculan con calculations/ y
presentan las secciones de reports/secciones.py; las descargas Excel y PDF
contienen exactamente las mismas tablas que la pantalla.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session

from calculations.comparacion_anf import ESTADOS, comparar, fuera_de_alcance, resumen
from calculations.fuentes_usos import calcular_fuentes_usos
from calculations.rubros import datos_todos
from calculations.wacc import calcular_wacc
from components.secciones_ui import descargas, mostrar_seccion
from components.texto import md
from database.models import Company
from reports import secciones as sec
from reports.informe_integral import TITULO, hojas_informe, pares_consecutivos


def _datos(session: Session):
    lista = [d for d in datos_todos(session) if d.tiene_datos]
    if not lista:
        st.info("No hay ejercicios con datos capturados.")
    return lista


def _aviso_sin_grupo(lista) -> None:
    sin_grupo = [(d.anio, c) for d in lista for c, _, _ in d.sin_grupo]
    if sin_grupo:
        st.warning(
            f"{len(sin_grupo)} importe(s) distintos de cero pertenecen a cuentas sin grupo de análisis: participan en los "
            "totales pero no en los rubros ni en los indicadores que los usan. Asigne el grupo en «Catálogo de cuentas»."
        )


def render_horizontal(session: Session, company: Company) -> None:
    st.header("Reporte — Análisis Horizontal 2021–2025")
    lista = _datos(session)
    if not lista:
        return
    _aviso_sin_grupo(lista)
    nivel = st.radio("Nivel de detalle", ["rubros", "grupos", "cuentas"], horizontal=True,
                     format_func={"rubros": "Rubros y totales (trabajo ANF)", "grupos": "Grupos de análisis",
                                  "cuentas": "Cuentas (denominación original)"}.get, key="horizontal_nivel")
    seccion = sec.horizontal(lista, nivel)
    mostrar_seccion(seccion, notas_plegadas=True)
    descargas(company, "Análisis horizontal 2021–2025", [("Horizontal", [seccion])], f"analisis_horizontal_{nivel}",
              clave="horizontal")


NIVELES_HORIZONTAL = {"Rubros y totales": "rubros", "Grupos de análisis": "grupos", "Cuentas (denominación original)": "cuentas"}


def _pares_estado(lista, estado: str) -> list[tuple[int, int]]:
    """(anterior, actual) de los ejercicios consecutivos con datos del estado."""
    anios = [d.anio for d in lista if (d.bs.tiene_datos if estado == "BG" else d.inc.tiene_datos)]
    return [(a, b) for a, b in zip(anios, anios[1:]) if b == a + 1]


def _comparar_dos(lista, estado: str, clave: str) -> str:
    """Muestra la comparacion y devuelve el nivel elegido, que tambien usan las descargas."""
    pares = _pares_estado(lista, estado)
    if not pares:
        st.info("Se necesitan dos ejercicios consecutivos con datos.")
        return "rubros"
    opciones = {f"{b} vs {a}": (a, b) for a, b in pares}
    columna_par, columna_nivel = st.columns([1, 2])
    with columna_par:
        eleccion = st.selectbox("Ejercicios comparados", list(opciones), index=len(opciones) - 1, key=f"{clave}_par")
    with columna_nivel:
        nivel = st.radio("Nivel de detalle", list(NIVELES_HORIZONTAL), horizontal=True, key=f"{clave}_nivel")
    anterior, actual = opciones[eleccion]
    mostrar_seccion(sec.horizontal_dos_ejercicios(lista, actual, anterior, estado, NIVELES_HORIZONTAL[nivel]))
    st.caption(f"Las descargas incluyen todos los pares de ejercicios con el nivel seleccionado: {nivel.lower()}.")
    return NIVELES_HORIZONTAL[nivel]


def _hojas_dos_ejercicios(lista, estado: str, nivel: str) -> list[tuple[str, list[sec.Seccion]]]:
    return [(f"{b} vs {a}", [sec.horizontal_dos_ejercicios(lista, b, a, estado, nivel)]) for a, b in _pares_estado(lista, estado)]


def render_horizontal_balance(session: Session, company: Company) -> None:
    st.header("Reporte — Análisis Horizontal del Balance General")
    lista = [d for d in _datos(session) if d.bs.tiene_datos]
    if not lista:
        return
    _aviso_sin_grupo(lista)
    st.caption(f"{md(company.nombre_legal)}. Período {lista[0].anio}–{lista[-1].anio}, cifras en {md(company.moneda)}. Cada "
               "ejercicio se compara con el anterior (trabajo, secciones 6.3 a 6.6).")
    tablas = sec.horizontal_balance_tablas(lista)
    capital = [sec.capital_trabajo(lista), sec.capital_trabajo_interanual(lista)]
    trabajo, capital_tab, dos = st.tabs(["Tablas 3 y 4 del trabajo", "Capital de trabajo (Tablas 6 y 7)", "Comparar dos ejercicios"])
    with trabajo:
        for seccion in tablas:
            mostrar_seccion(seccion)
    with capital_tab:
        for seccion in capital:
            mostrar_seccion(seccion)
    with dos:
        nivel = _comparar_dos(lista, "BG", "horizontal_balance")
    descargas(company, f"Análisis horizontal del Balance General {lista[0].anio}–{lista[-1].anio}",
              [("Tablas 3 y 4", tablas), ("Capital de trabajo", capital)] + _hojas_dos_ejercicios(lista, "BG", nivel),
              f"analisis_horizontal_balance_{nivel}", clave="horizontal_balance")


def render_horizontal_resultados(session: Session, company: Company) -> None:
    st.header("Reporte — Análisis Horizontal del Estado de Resultados")
    lista = [d for d in _datos(session) if d.inc.tiene_datos]
    if not lista:
        return
    _aviso_sin_grupo(lista)
    st.caption(f"{md(company.nombre_legal)}. Período {lista[0].anio}–{lista[-1].anio}, cifras en {md(company.moneda)}. Cada "
               "ejercicio se compara con el anterior (trabajo, secciones 6.3 y 6.4).")
    tabla = sec.horizontal_resultados_tabla(lista)
    trabajo, dos = st.tabs(["Tabla 5 del trabajo", "Comparar dos ejercicios"])
    with trabajo:
        mostrar_seccion(tabla)
    with dos:
        nivel = _comparar_dos(lista, "ER", "horizontal_resultados")
    descargas(company, f"Análisis horizontal del Estado de Resultados {lista[0].anio}–{lista[-1].anio}",
              [("Tabla 5", [tabla])] + _hojas_dos_ejercicios(lista, "ER", nivel), f"analisis_horizontal_resultados_{nivel}",
              clave="horizontal_resultados")


def render_vertical_comparativo(session: Session, company: Company) -> None:
    st.header("Reporte — Análisis Vertical comparativo 2021–2025")
    lista = _datos(session)
    if not lista:
        return
    st.caption("El análisis vertical de un solo ejercicio, por cuenta, sigue disponible en los reportes «Análisis Vertical».")
    secciones = [sec.vertical(lista, "ER"), sec.vertical(lista, "BG")]
    for seccion in secciones:
        mostrar_seccion(seccion)
    descargas(company, "Análisis vertical comparativo 2021–2025", [("Vertical", secciones)], "analisis_vertical_comparativo",
              clave="vertical_comp")


def render_indicadores(session: Session, company: Company) -> None:
    from reports.indicadores_financieros import hojas_exportacion, render_grupos

    st.header("Indicadores financieros")
    lista = _datos(session)
    if not lista:
        return
    _aviso_sin_grupo(lista)
    st.caption(f"{md(company.nombre_legal)}. Saldos al cierre de cada ejercicio, criterio del trabajo ANF (secciones 8.2 y 8.4).")
    render_grupos(lista, company)
    st.markdown("##### Reporte completo de indicadores")
    descargas(company, "Indicadores financieros 2021–2025", hojas_exportacion(lista), "indicadores_financieros", clave="indicadores")


def render_wacc(session: Session, company: Company) -> None:
    st.header("Reporte — Costo promedio ponderado de capital (WACC)")
    lista = [d for d in _datos(session) if d.bs.tiene_datos and d.inc.tiene_datos]
    if not lista:
        return
    st.warning(
        "Las tasas de interés de la deuda y la tasa de ISR (30 %) son supuestos del trabajo ANF que no pueden verificarse "
        "con los documentos disponibles. El costo del patrimonio se estima con el ROE, como en el trabajo; no es un costo "
        "de capital exigido por los accionistas. El resultado es una estimación."
    )
    resultados = [calcular_wacc(d) for d in lista]
    resumen_ = sec.wacc_resumen(resultados)
    mostrar_seccion(resumen_)
    supuestos = sec.supuestos_wacc()
    with st.expander("Supuestos usados (fuentes/anf/supuestos_wacc.json)"):
        mostrar_seccion(supuestos)
    anio = st.selectbox("Detalle del ejercicio", [r.anio for r in resultados], index=len(resultados) - 1, key="wacc_anio")
    detalle = sec.wacc_detalle(next(r for r in resultados if r.anio == anio))
    mostrar_seccion(detalle)
    descargas(company, "WACC 2021–2025", [("WACC", [resumen_, supuestos] + [sec.wacc_detalle(r) for r in resultados])], "wacc",
              clave="wacc")


def render_fuentes_usos(session: Session, company: Company) -> None:
    st.header("Reporte — Estado de origen y aplicación de fondos")
    lista = _datos(session)
    if not lista:
        return
    pares = pares_consecutivos(lista)
    if not pares:
        st.info("Se necesitan dos ejercicios consecutivos con Balance General.")
        return
    etiquetas = [f"{b.anio} vs {a.anio}" for a, b in pares]
    eleccion = st.selectbox("Ejercicios comparados", etiquetas, index=len(etiquetas) - 1, key="fyu_par")
    a, b = pares[etiquetas.index(eleccion)]
    if (a.anio, b.anio) == (2023, 2024):
        st.warning("Entre 2023 y 2024 cambia la presentación (estados combinados a consolidados): varias partidas cambian de "
                   "denominación y de agrupación, por lo que las variaciones mezclan cambios reales y de presentación.")
    resultado = calcular_fuentes_usos(a, b)
    seccion = sec.fuentes_usos(resultado)
    mostrar_seccion(seccion)
    descargas(company, f"Origen y aplicación de fondos {b.anio} vs {a.anio}", [("Origen y aplicación", [seccion])],
              f"origen_aplicacion_{b.anio}_{a.anio}", clave="fyu")


def render_validacion(session: Session, company: Company) -> None:
    st.header("Validación — Comparación con el trabajo de investigación ANF")
    lista = _datos(session)
    if not lista:
        return
    st.caption("Datos originales → cálculo de la aplicación → comparación con el valor publicado en el trabajo. Los valores "
               "del trabajo nunca se usan como datos ni como resultados calculados.")
    comparaciones = comparar(lista)
    conteo = resumen(comparaciones)
    columnas = st.columns(len(ESTADOS))
    for columna, estado in zip(columnas, ESTADOS):
        columna.metric(estado, conteo[estado])
    filtro = st.multiselect("Estados a mostrar", list(ESTADOS), default=[e for e in ESTADOS if e != "Coincide"], key="val_estados")
    secciones_ref = sorted({c.referencia.seccion for c in comparaciones},
                           key=lambda s: [(0, int(x), "") if x.isdigit() else (1, 0, x) for x in s.replace(" ", ".").split(".")])
    elegidas = st.multiselect("Secciones del trabajo", secciones_ref, default=secciones_ref, key="val_secciones")
    visibles = [c for c in comparaciones if c.estado in filtro and c.referencia.seccion in elegidas]
    seccion = sec.comparacion(visibles)
    mostrar_seccion(seccion)
    with st.expander("Resumen por indicador"):
        df = pd.DataFrame([{"Ref.": c.referencia.id, "Concepto": c.referencia.concepto, "Estado": c.estado} for c in comparaciones])
        st.dataframe(df.groupby(["Concepto", "Estado"]).size().unstack(fill_value=0), width="stretch")
    with st.expander("Fuera del alcance de la comparación"):
        for texto in fuera_de_alcance():
            st.caption(md(texto))
    completa = sec.comparacion(comparaciones)
    descargas(company, "Comparación con el trabajo de investigación ANF", [("Comparación ANF", [completa])],
              "comparacion_trabajo_anf", clave="validacion")


def render_informe_integral(session: Session, company: Company) -> None:
    st.header("Reporte — Informe integral 2021–2025")
    lista = _datos(session)
    if not lista:
        return
    st.caption("Reúne los estados financieros originales, los análisis horizontal y vertical, los indicadores, el capital de "
               "trabajo, el DuPont, el WACC, el origen y aplicación de fondos, la comparación con el trabajo ANF, las "
               "observaciones sobre discrepancias y la trazabilidad de los datos.")
    hojas = hojas_informe(session, lista)
    descargas(company, TITULO, hojas, "informe_integral_2021_2025", clave="integral")
    for seccion in hojas[0][1]:
        mostrar_seccion(seccion)
