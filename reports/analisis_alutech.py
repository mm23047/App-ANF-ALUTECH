"""Paginas del analisis financiero 2021-2025 (adaptacion Alutech).

Todas leen los datos originales de la BD, calculan con calculations/ y
presentan las secciones de reports/secciones.py; las descargas Excel y PDF
contienen exactamente las mismas tablas que la pantalla.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session

from calculations.comparacion_anf import ESTADOS, comparar, resumen
from calculations.fuentes_usos import calcular_fuentes_usos
from calculations.rubros import datos_todos
from calculations.wacc import calcular_wacc
from components.avisos import mostrar_sin_grupo
from components.secciones_ui import descargas, mostrar_seccion
from components.texto import md
from database.models import Company
from reports import secciones as sec
from reports.informe_integral import archivo_ejercicios, hojas_informe, pares_consecutivos, titulo_informe


def _datos(session: Session):
    lista = [d for d in datos_todos(session) if d.tiene_datos]
    if not lista:
        st.info("No hay ejercicios con datos capturados.")
    return lista


def _aviso_sin_grupo(lista) -> None:
    mostrar_sin_grupo(lista)


def _aviso_integridad(lista, estado: str | None = None) -> list[tuple[str, list[sec.Seccion]]]:
    """Avisa en pantalla si un balance esta descuadrado o un estado incompleto, y devuelve la hoja para las descargas.
    No modifica ningun importe."""
    seccion = sec.integridad(lista, estado)
    sin_clasificar = sec.clasificacion(lista)
    secciones = [s for s in (seccion, sin_clasificar) if s is not None]
    if not secciones:
        return []
    for ejercicio, estado_financiero, problema, diferencia in (seccion.filas if seccion else []):
        detalle = f" Diferencia: {sec.formatear(diferencia, sec.VAR_USD)} {md('USD')}." if diferencia is not None else ""
        st.warning(md(f"{ejercicio}, {estado_financiero}. {problema}{detalle} La aplicación no corrige los datos."))
    return [("Avisos de integridad", secciones)]


def render_horizontal(session: Session, company: Company) -> None:
    encabezado = st.empty()
    lista = _datos(session)
    encabezado.header(f"Reporte — Análisis Horizontal {_rango(lista)}".rstrip())
    if not lista:
        return
    _aviso_sin_grupo(lista)
    avisos = _aviso_integridad(lista)
    nivel = st.radio("Nivel de detalle", ["rubros", "grupos", "cuentas"], horizontal=True,
                     format_func={"rubros": "Rubros y totales", "grupos": "Grupos de análisis",
                                  "cuentas": "Cuentas (denominación original)"}.get, key="horizontal_nivel")
    seccion = sec.horizontal(lista, nivel)
    mostrar_seccion(seccion, notas_plegadas=True)
    descargas(company, f"Análisis horizontal {_rango(lista)}", avisos + [("Horizontal", [seccion])], f"analisis_horizontal_{nivel}",
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


def _rango(lista) -> str:
    """Ejercicios analizados, tal como estan registrados (p. ej. 2021–2025)."""
    return sec.ejercicios_de([d for d in lista if d.tiene_datos])


def render_horizontal_balance(session: Session, company: Company) -> None:
    st.header("Reporte — Análisis Horizontal del Balance General")
    lista = [d for d in _datos(session) if d.bs.tiene_datos]
    if not lista:
        return
    _aviso_sin_grupo(lista)
    avisos = _aviso_integridad(lista, "BG")
    st.caption(f"{md(company.nombre_legal)}. Período {_rango(lista)}, cifras en {md(company.moneda)}. Cada "
               "ejercicio se compara con el anterior.")
    tablas = sec.horizontal_balance_tablas(lista)
    capital = [sec.capital_trabajo(lista), sec.capital_trabajo_interanual(lista)]
    trabajo, capital_tab, dos = st.tabs(["Análisis de la situación financiera", "Capital de trabajo", "Comparar dos ejercicios"])
    with trabajo:
        for seccion in tablas:
            mostrar_seccion(seccion)
    with capital_tab:
        for seccion in capital:
            mostrar_seccion(seccion)
    with dos:
        nivel = _comparar_dos(lista, "BG", "horizontal_balance")
    descargas(company, f"Análisis horizontal del Balance General {_rango(lista)}",
              avisos + [("Situación financiera", tablas), ("Capital de trabajo", capital)] + _hojas_dos_ejercicios(lista, "BG", nivel),
              f"analisis_horizontal_balance_{nivel}", clave="horizontal_balance")


def render_horizontal_resultados(session: Session, company: Company) -> None:
    st.header("Reporte — Análisis Horizontal del Estado de Resultados")
    lista = [d for d in _datos(session) if d.inc.tiene_datos]
    if not lista:
        return
    _aviso_sin_grupo(lista)
    avisos = _aviso_integridad(lista, "ER")
    st.caption(f"{md(company.nombre_legal)}. Período {_rango(lista)}, cifras en {md(company.moneda)}. Cada "
               "ejercicio se compara con el anterior.")
    tabla = sec.horizontal_resultados_tabla(lista)
    trabajo, dos = st.tabs(["Análisis del estado de resultados", "Comparar dos ejercicios"])
    with trabajo:
        mostrar_seccion(tabla)
    with dos:
        nivel = _comparar_dos(lista, "ER", "horizontal_resultados")
    descargas(company, f"Análisis horizontal del Estado de Resultados {_rango(lista)}",
              avisos + [("Estado de resultados", [tabla])] + _hojas_dos_ejercicios(lista, "ER", nivel), f"analisis_horizontal_resultados_{nivel}",
              clave="horizontal_resultados")


def render_vertical_comparativo(session: Session, company: Company) -> None:
    encabezado = st.empty()
    lista = _datos(session)
    encabezado.header(f"Reporte — Análisis Vertical comparativo {_rango(lista)}".rstrip())
    if not lista:
        return
    _aviso_sin_grupo(lista)
    st.caption("El análisis vertical de un solo ejercicio, por cuenta, sigue disponible en los reportes «Análisis Vertical».")
    secciones = [sec.vertical(lista, "ER"), sec.vertical(lista, "BG")]
    for seccion in secciones:
        mostrar_seccion(seccion)
    descargas(company, f"Análisis vertical comparativo {_rango(lista)}", [("Vertical", secciones)], "analisis_vertical_comparativo",
              clave="vertical_comp")


def render_indicadores(session: Session, company: Company) -> None:
    from reports.indicadores_financieros import hojas_exportacion, render_grupos

    st.header("Indicadores financieros")
    lista = _datos(session)
    if not lista:
        return
    _aviso_sin_grupo(lista)
    st.caption(f"{md(company.nombre_legal)}. Indicadores calculados con los saldos al cierre de cada ejercicio.")
    render_grupos(lista, company)
    st.markdown("##### Reporte completo de indicadores")
    descargas(company, f"Indicadores financieros {_rango(lista)}", hojas_exportacion(lista), "indicadores_financieros", clave="indicadores")


def render_wacc(session: Session, company: Company) -> None:
    st.header("Reporte — Costo promedio ponderado de capital (WACC)")
    lista = [d for d in _datos(session) if d.bs.tiene_datos and d.inc.tiene_datos]
    if not lista:
        return
    _aviso_sin_grupo(lista)
    st.warning(
        "Las tasas de interés de la deuda y la tasa de ISR (30 %) son supuestos de entrada que no pueden verificarse "
        "con los documentos disponibles. El costo del patrimonio se estima con el ROE al cierre; no es un costo "
        "de capital exigido por los accionistas. El resultado es una estimación."
    )
    resultados = [calcular_wacc(d) for d in lista]
    resumen_ = sec.wacc_resumen(resultados)
    mostrar_seccion(resumen_)
    supuestos = sec.supuestos_wacc()
    with st.expander("Supuestos de tasas utilizados"):
        mostrar_seccion(supuestos)
    anio = st.selectbox("Detalle del ejercicio", [r.anio for r in resultados], index=len(resultados) - 1, key="wacc_anio")
    detalle = sec.wacc_detalle(next(r for r in resultados if r.anio == anio))
    mostrar_seccion(detalle, ancho_concepto="medium")  # todas las columnas a la vista
    descargas(company, f"WACC {sec.ejercicios_de(resultados)}", [("WACC", [resumen_, supuestos] + [sec.wacc_detalle(r) for r in resultados])], "wacc",
              clave="wacc")


def render_fuentes_usos(session: Session, company: Company) -> None:
    st.header("Reporte — Estado de origen y aplicación de fondos")
    lista = _datos(session)
    if not lista:
        return
    _aviso_sin_grupo(lista)
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
    st.header(f"Validación — {sec.TITULO_CONTRASTE}")
    lista = _datos(session)
    if not lista:
        return
    _aviso_sin_grupo(lista)
    st.caption("Control de consistencia: datos financieros registrados → cálculo de la aplicación → contraste con un "
               "valor de referencia externo. Los valores de referencia no intervienen en ningún cálculo.")
    comparaciones = comparar(lista)
    conteo = resumen(comparaciones)
    columnas = st.columns(len(ESTADOS))
    for columna, estado in zip(columnas, ESTADOS):
        columna.metric(estado, conteo[estado])
    filtro = st.multiselect("Estados a mostrar", list(ESTADOS), default=[e for e in ESTADOS if e != "Coincide"], key="val_estados")
    seccion = sec.comparacion([c for c in comparaciones if c.estado in filtro])
    mostrar_seccion(seccion, ancho_concepto="medium")  # nueve columnas: todas a la vista
    with st.expander("Resumen por indicador"):
        df = pd.DataFrame([{"Concepto": c.referencia.concepto.rstrip("*").rstrip(), "Estado": c.estado} for c in comparaciones])
        st.dataframe(df.groupby(["Concepto", "Estado"]).size().unstack(fill_value=0), width="stretch")
    completa = sec.comparacion(comparaciones)
    descargas(company, sec.TITULO_CONTRASTE, [("Contraste", [completa])], "contraste_de_resultados", clave="validacion")


def render_informe_integral(session: Session, company: Company) -> None:
    encabezado = st.empty()
    lista = _datos(session)
    encabezado.header(f"Reporte — Informe integral {_rango(lista)}".rstrip())
    if not lista:
        return
    _aviso_sin_grupo(lista)
    st.caption("Reúne los estados financieros originales, los análisis horizontal y vertical, los indicadores, el capital de "
               "trabajo, el DuPont, el WACC, el origen y aplicación de fondos y la trazabilidad de los datos.")
    hojas = hojas_informe(session, lista)
    descargas(company, titulo_informe(lista), hojas, f"informe_integral_{archivo_ejercicios(lista)}", clave="integral")
    for seccion in hojas[0][1]:
        mostrar_seccion(seccion)
