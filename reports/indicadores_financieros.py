"""Pagina «Indicadores financieros»: liquidez, actividad, endeudamiento y rentabilidad.

Solo presentacion. Todos los valores salen de calculations/indicadores.py, la
misma funcion que usan el dashboard, las exportaciones y la comparacion con el
trabajo ANF; aqui no se define ni se recalcula ningun indicador. Los nombres
son los del trabajo ANF (secciones 6.5, 8 y 9). Saldos al cierre.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from calculations import indicadores as ind
from calculations.rubros import DatosEjercicio
from components.secciones_ui import a_dataframe, descargas, mostrar_seccion
from components.tables import columnas_derecha
from components.texto import md
from reports import secciones as sec

MILLON = Decimal("1000000")
NO_CALCULABLE = "No calculable"
CLAVE_ANIO = "indicadores_anio"
_CITA_DUPONT = re.compile(r",\s*9\.[56]\b")


@dataclass(frozen=True)
class Fila:
    clave: str  # indicador en calculations/indicadores.py
    nombre: str  # denominacion del trabajo ANF
    tarjeta: str  # etiqueta corta de la tarjeta
    seccion: str  # seccion del trabajo ANF


@dataclass(frozen=True)
class Grupo:
    titulo: str
    descripcion: str
    filas: tuple[Fila, ...]
    advertencias: tuple[str, ...]
    grafico: tuple[list[str], str]
    variantes: tuple[Fila, ...] = field(default=())
    titulo_variantes: str = ""
    categoria: str = ""  # categoria de calculations/indicadores.py que exporta este apartado
    bases: tuple[str, ...] = ()  # importes de los que parten sus indicadores (calculations/comparativo.py)


GRUPOS: tuple[Grupo, ...] = (
    Grupo(
        "Liquidez",
        "Capacidad de cubrir las obligaciones de corto plazo con los recursos corrientes.",
        (
            Fila("ctn", "Capital de trabajo neto (CTN)", "Capital de trabajo neto", "6.5, 8.1 C, 9.2.1"),
            Fila("razon_corriente", "Razón corriente", "Razón corriente", "6.5, 8.1 A"),
            Fila("prueba_acida", "Prueba ácida", "Prueba ácida", "6.5, 8.1 B"),
        ),
        (
            "Saldos al cierre de cada ejercicio: no reflejan los movimientos de efectivo durante el año.",
            "El activo corriente incluye cuentas por cobrar a partes relacionadas. Los estados muestran su saldo, "
            "no su recuperabilidad efectiva (trabajo, sección 4).",
        ),
        (["razon_corriente", "prueba_acida"], "Razón corriente y prueba ácida (veces)"),
        categoria=ind.LIQUIDEZ,
        bases=("activo_corriente", "rubro:INVENTARIOS", "pasivo_corriente"),
    ),
    Grupo(
        "Actividad",
        "Velocidad con que se renuevan los recursos y días que tarda el ciclo de efectivo.",
        (
            Fila("rotacion_inventarios", "Rotación de inventarios", "Rotación de inventarios", "8.2 A"),
            Fila("ppi", "Período promedio de inventario (PPI)", "PPI", "8.2 A, 9.3"),
            Fila("rotacion_cxc", "Rotación de cuentas por cobrar", "Rotación de CxC", "8.2 B"),
            Fila("ppc", "Período promedio de cobro (PPC)", "PPC", "8.2 B, 9.3"),
            Fila("ppp", "Período promedio de pago (PPP)", "PPP", "9.3"),
            Fila("rotacion_activos", "Rotación de activos totales", "Rotación de activos", "8.2 D"),
            Fila("ciclo_operativo", "Ciclo operativo", "Ciclo operativo", "8.2 C, 9.3"),
            Fila("cce", "Ciclo de conversión del efectivo (CCE)", "CCE", "9.3"),
        ),
        (
            "Rotación de CxC y PPC usan la línea presentada, igual que la sección 9.3 del trabajo: solo «Cuentas por "
            "cobrar comerciales» en 2021–2023 y «Deudores comerciales y Otras Cuentas por Cobrar» en 2024–2025. La base "
            "cambia entre 2023 y 2024, por lo que esa comparación no es homogénea.",
            "La sección 8.2 B del trabajo usa en 2023 comerciales + otras (96,097,483), y la 9.3 solo comerciales "
            "(41,272,525). Aquí se sigue la 9.3; la variante de abajo muestra la otra base para los cinco años.",
            "El PPP mantiene su fórmula: cuentas por pagar de la línea presentada / costo de ventas × 365. El costo de "
            "ventas aproxima las compras y la línea incluye otras cuentas por pagar desde 2024.",
            "El CCE hereda ambos cambios de base. El signo de 2023 depende de la base usada: con comerciales + otras, "
            "tanto en cobros como en pagos, pasa de negativo a positivo. Esa variante del CCE no se calcula aquí.",
            "Ciclo operativo y CCE siguen el desarrollo escrito de la sección 9.3: CO = PPI + PPC y CCE = CO − PPP, con cada "
            "operando a 2 decimales. Los demás indicadores no usan redondeo intermedio.",
        ),
        (["ppi", "ppc", "ppp", "cce"], "Ciclo de conversión del efectivo (días)"),
        (
            Fila("rotacion_cxc_total", "Rotación de cuentas por cobrar comerciales y otras", "", "8.2 B (variante)"),
            Fila("ppc_total", "Período de cobro (comerciales y otras)", "", "8.2 B (variante)"),
        ),
        "Alternativa analítica: comerciales + otras cuentas por cobrar (comparabilidad no confirmada)",
        categoria=ind.ACTIVIDAD,
        bases=("costo_ventas", "rubro:INVENTARIOS", "ingresos", "rubro:CXC_COMERCIALES_PRESENTADA", "rubro:CXC_COMERCIALES_Y_OTRAS",
               "rubro:CXP_COMERCIALES_PRESENTADA", "total_activo"),
    ),
    Grupo(
        "Endeudamiento",
        "Proporción de los activos financiada con terceros, plazo de esas obligaciones y cobertura de los gastos financieros.",
        (
            Fila("endeudamiento", "Índice de endeudamiento", "Índice de endeudamiento", "8.3 A"),
            Fila("deuda_capital", "Razón deuda-capital", "Razón deuda-capital", "8.3 D"),
            Fila("pc_sobre_pasivo", "Pasivo corriente sobre pasivo total", "Pasivo corriente / pasivo", "8.3 A"),
            Fila("cobertura_intereses", "Razón de cargos de interés fijo (cobertura)", "Cobertura de intereses", "8.3 B"),
            Fila("cobertura_pagos_fijos", "Índice de cobertura de pagos fijos", "Cobertura de pagos fijos", "8.3 C"),
        ),
        (
            "El pasivo total incluye pasivos operativos sin costo explícito (proveedores, impuestos, provisiones), "
            "no solo deuda financiera.",
            "La cobertura usa gastos financieros netos, como el trabajo. En 2021–2023 los estados presentan directamente "
            "el neto; en 2024–2025 es gastos financieros menos ingresos financieros.",
            "La cobertura de pagos fijos iguala a la razón de cargos de interés fijo porque los estados no desglosan las cuotas de "
            "arrendamiento ni la amortización del principal (trabajo, 8.3 C): no mide la cobertura real con esos pagos.",
        ),
        (["endeudamiento", "pc_sobre_pasivo"], "Endeudamiento (%)"),
        (Fila("cobertura_intereses_bruta", "Cobertura con gastos financieros brutos", "", "Complementario"),),
        "Variante con gastos financieros brutos (no figura en el trabajo)",
        categoria=ind.ENDEUDAMIENTO,
        bases=("total_pasivo", "pasivo_corriente", "total_activo", "total_patrimonio", "utilidad_operativa", "gastos_financieros_netos"),
    ),
    Grupo(
        "Rentabilidad",
        "Capacidad de generar utilidad a partir de las ventas, los activos y el patrimonio.",
        (
            Fila("margen_bruto", "Margen de utilidad bruta", "Margen bruto", "8.4 A"),
            Fila("margen_operativo", "Margen de utilidad operativa", "Margen operativo", "8.4 B"),
            Fila("margen_neto", "Margen de utilidad neta", "Margen neto", "8.4 C"),
            Fila("roa", "Rendimiento sobre los activos totales (ROA)", "ROA", "8.4 E"),
            Fila("roe", "Retorno sobre el patrimonio (ROE)", "ROE", "8.4 F"),
            Fila("eps", "Ganancia por acción (EPS)", "EPS", "8.4 D"),
        ),
        (
            "ROA y ROE usan la utilidad neta total y el activo y el patrimonio totales al cierre, como la sección 8.4 "
            "del trabajo.",
            "La utilidad operativa de 2022 y 2023 no está impresa en los estados: se obtiene de sus partidas. En 2021–2023 "
            "incluye el deterioro y los otros ingresos netos; en 2024–2025 los otros ingresos o gastos quedan después de "
            "este resultado.",
        ),
        (["margen_bruto", "margen_operativo", "margen_neto", "roa", "roe"], "Márgenes y rendimientos (%)"),
        categoria=ind.RENTABILIDAD,
        bases=("ingresos", "utilidad_bruta", "utilidad_operativa", "utilidad_neta", "total_activo", "total_patrimonio"),
    ),
)
# Resto de indicadores de calculations/indicadores.py que el trabajo presenta fuera de estos cuatro grupos.
OTROS_INDICADORES: tuple[Fila, ...] = (
    Fila("razon_efectivo", "Razón de efectivo", "", "5.6 d"),
    Fila("razon_tesoreria", "Razón de tesorería", "", "9.1"),
    Fila("capitales_permanentes", "Capitales permanentes", "", "9.2.2"),
    Fila("fondo_maniobra_lp", "Fondo de maniobra a largo plazo", "", "9.2.2"),
    Fila("ebitda", "EBITDA", "", "6.7"),
)


def _valor_tarjeta(indicador: ind.Indicador, valor: Decimal | None) -> str:
    if valor is None:
        return NO_CALCULABLE
    if indicador.unidad == ind.USD:  # el importe exacto esta en la tabla
        return f"USD {valor / MILLON:,.2f} M"
    return ind.formatear(indicador.unidad, valor)


def _delta(indicador: ind.Indicador, valor: Decimal | None, previo: Decimal | None, anio_previo: int) -> str | None:
    """Cambio frente al ejercicio anterior: se muestra sin color porque subir no siempre es favorable."""
    if valor is None or previo is None:
        return None
    cambio = valor - previo
    if indicador.unidad == ind.USD:
        texto = f"{cambio / MILLON:+,.2f} M"
    elif indicador.unidad == ind.PCT:
        texto = f"{cambio:+,.2f} p. p."
    else:
        texto = f"{cambio:+,.2f} {indicador.unidad}"
    return f"{texto} vs {anio_previo}"


def _tarjetas(grupo: Grupo, datos: DatosEjercicio, anterior: DatosEjercicio | None) -> None:
    # Contenedor horizontal: las tarjetas pasan a la fila siguiente si no caben, sin cortar los valores.
    with st.container(horizontal=True):
        for fila in grupo.filas:
            indicador = ind.POR_CLAVE[fila.clave]
            valor = ind.calcular(datos, fila.clave).valor
            previo = ind.calcular(anterior, fila.clave).valor if anterior is not None else None
            st.metric(fila.tarjeta, _valor_tarjeta(indicador, valor),
                      delta=_delta(indicador, valor, previo, anterior.anio) if anterior is not None else None,
                      delta_color="off", help=f"{fila.nombre}. Fórmula: {indicador.formula}.", border=True)


def _tabla_anios(lista: list[DatosEjercicio], filas: tuple[Fila, ...]) -> pd.DataFrame:
    """Tabla comparativa con los anos en columnas; reutiliza el formato de los reportes."""
    seccion = sec.Seccion("", [sec.Columna("Indicador"), sec.Columna("Unidad")]
                          + [sec.Columna(str(d.anio), sec.POR_FILA) for d in lista], columna_unidad=1)
    for fila in filas:
        valores = [ind.calcular(d, fila.clave).valor for d in lista]
        seccion.filas.append([fila.nombre, ind.POR_CLAVE[fila.clave].unidad]
                             + [v if v is not None else NO_CALCULABLE for v in valores])
    return a_dataframe(seccion)


def _motivos(lista: list[DatosEjercicio], filas: tuple[Fila, ...]) -> list[str]:
    """Razon de cada indicador que no se puede calcular en algun ejercicio."""
    motivos = []
    for fila in filas:
        por_motivo: dict[str, list[int]] = {}
        for d in lista:
            resultado = ind.calcular(d, fila.clave)
            if resultado.valor is None:
                por_motivo.setdefault(resultado.motivo or NO_CALCULABLE, []).append(d.anio)
        for motivo, anios in por_motivo.items():
            cuando = "todos los ejercicios" if len(anios) == len(lista) else ", ".join(str(a) for a in anios)
            motivos.append(f"{fila.nombre} ({cuando}): {NO_CALCULABLE.lower()}. {motivo}")
    return motivos


def _formulas(grupo: Grupo, datos: DatosEjercicio) -> None:
    # st.table ajusta el texto en varias lineas; sus celdas admiten Markdown, por eso se escapan.
    st.table(pd.DataFrame([
        {"Indicador": md(fila.nombre),
         "Fórmula": md(ind.POR_CLAVE[fila.clave].formula),
         f"Interpretación ({datos.anio})": md(ind.interpretacion(ind.calcular(datos, fila.clave))),
         "Trabajo": md(fila.seccion)}
        for fila in grupo.filas
    ]), hide_index=True)


def _grafico(lista: list[DatosEjercicio], claves: list[str], titulo: str) -> go.Figure:
    fig = go.Figure()
    for clave in claves:
        valores = [ind.calcular(d, clave).valor for d in lista]
        fig.add_trace(go.Scatter(x=[d.anio for d in lista], y=[float(v) if v is not None else None for v in valores],
                                 mode="lines+markers", name=ind.POR_CLAVE[clave].nombre))
    fig.update_layout(title=titulo, xaxis_title="Ejercicio", xaxis=dict(dtick=1))
    return fig


def _mostrar_grupo(grupo: Grupo, lista: list[DatosEjercicio], datos: DatosEjercicio, anterior: DatosEjercicio | None) -> None:
    st.subheader(grupo.titulo)
    st.caption(grupo.descripcion)
    _tarjetas(grupo, datos, anterior)
    st.markdown("##### Comparativo 2021–2025")
    st.dataframe(_tabla_anios(lista, grupo.filas), hide_index=True, width="stretch", height="content",
                 column_config=columnas_derecha(*(str(d.anio) for d in lista)))
    if grupo.bases:
        mostrar_seccion(_base_de(grupo, lista))
    if grupo.categoria == ind.ACTIVIDAD:
        mostrar_seccion(sec.bases_cxc(lista))
    st.markdown("##### Fórmula e interpretación")
    _formulas(grupo, datos)
    st.markdown("##### Advertencias metodológicas")
    st.warning("\n".join(f"- {texto}" for texto in grupo.advertencias))
    if grupo.variantes:
        with st.expander(grupo.titulo_variantes):
            st.dataframe(_tabla_anios(lista, grupo.variantes), hide_index=True, width="stretch", height="content")
            for motivo in _motivos(lista, grupo.variantes):
                st.caption(md(motivo))
    motivos = _motivos(lista, grupo.filas)
    for motivo in motivos:
        st.caption(md(motivo))
    claves, titulo = grupo.grafico
    st.plotly_chart(_grafico(lista, claves, titulo), width="stretch", key=f"graf_{grupo.titulo}")


def _complementarios(lista: list[DatosEjercicio]) -> None:
    """Resultados que ya tenia esta pagina y no pertenecen a los cuatro grupos."""
    with st.expander("Otros resultados del trabajo: indicadores complementarios, razones de mercado y capital de trabajo"):
        otros, mercado, capital = st.tabs(["Otros indicadores", ind.MERCADO, "Capital de trabajo"])
        with otros:
            st.dataframe(_tabla_anios(lista, OTROS_INDICADORES), hide_index=True, width="stretch", height="content")
            for motivo in _motivos(lista, OTROS_INDICADORES):
                st.caption(md(motivo))
        with mercado:
            mostrar_seccion(sec.indicadores(lista, ind.MERCADO), notas_plegadas=False)
        with capital:
            mostrar_seccion(sec.capital_trabajo(lista))


def _indicadores_sin_citas_dupont(lista: list[DatosEjercicio], categoria: str) -> sec.Seccion:
    """Tabla de la categoria sin citar las secciones 9.5 y 9.6 del trabajo. Las citas se
    quitan solo en esta copia: calculations/indicadores.py las conserva para otros reportes."""
    seccion = sec.indicadores(lista, categoria)
    columna = next(i for i, c in enumerate(seccion.columnas) if c.nombre == "Sección del trabajo")
    for fila in seccion.filas:
        fila[columna] = _CITA_DUPONT.sub("", fila[columna])
    return seccion


def _base_de(grupo: Grupo, lista: list[DatosEjercicio]) -> sec.Seccion:
    return sec.base_financiera(lista, grupo.bases, f"Base financiera de {grupo.titulo.lower()} (saldos al cierre) [USD]")


def _secciones_de(grupo: Grupo, lista: list[DatosEjercicio]) -> list[sec.Seccion]:
    extra = [sec.bases_cxc(lista)] if grupo.categoria == ind.ACTIVIDAD else []
    return [_base_de(grupo, lista), *extra, _indicadores_sin_citas_dupont(lista, grupo.categoria)]


def hojas_exportacion(lista: list[DatosEjercicio]) -> list[tuple[str, list[sec.Seccion]]]:
    """Hojas de las descargas de esta pagina. DuPont no se incluye: tiene su propio reporte."""
    por_categoria = {grupo.categoria: grupo for grupo in GRUPOS}
    hojas = [(categoria, _secciones_de(por_categoria[categoria], lista) if categoria in por_categoria
              else [_indicadores_sin_citas_dupont(lista, categoria)])
             for categoria in ind.CATEGORIAS if categoria != ind.DUPONT]
    hojas.append(("Capital de trabajo", [sec.capital_trabajo(lista)]))
    return hojas


def render_grupos(lista: list[DatosEjercicio], company=None) -> None:
    """Selector de ejercicio de las tarjetas y los cuatro apartados."""
    anios = [d.anio for d in lista]
    elegido = st.segmented_control("Ejercicio de las tarjetas y la interpretación", anios, default=anios[-1], required=True,
                                   key=CLAVE_ANIO)
    if elegido not in anios:
        elegido = anios[-1]
    por_anio = {d.anio: d for d in lista}
    datos, anterior = por_anio[elegido], por_anio.get(elegido - 1)
    for pestana, grupo in zip(st.tabs([g.titulo for g in GRUPOS]), GRUPOS):
        with pestana:
            _mostrar_grupo(grupo, lista, datos, anterior)
            if company is not None:
                st.markdown("##### Reporte de este apartado")
                descargas(company, f"Ratios de {grupo.titulo.lower()} {lista[0].anio}–{lista[-1].anio}",
                          [(grupo.titulo, _secciones_de(grupo, lista))], f"ratios_{grupo.titulo.lower()}",
                          clave=f"ratios_{grupo.titulo.lower()}")
    _complementarios(lista)
