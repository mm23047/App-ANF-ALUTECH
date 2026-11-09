"""Informe integral 2021-2025: estados originales, analisis horizontal y
vertical, indicadores, capital de trabajo, DuPont, WACC, origen y aplicacion
de fondos y trazabilidad.

Una sola funcion arma las hojas del informe; la pagina del informe y las
pruebas la usan, y el Excel y el PDF se generan de las mismas secciones.
El contraste con los valores de referencia no forma parte del informe: esta
completo en la pagina de validacion (reports/analisis_alutech.render_validacion).
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from calculations import indicadores as ind
from calculations.fuentes_usos import calcular_fuentes_usos
from calculations.rubros import DatosEjercicio, datos_todos
from calculations.wacc import calcular_wacc
from reports import secciones as sec


def titulo_informe(lista: list[DatosEjercicio]) -> str:
    """Titulo del PDF y del Excel con los ejercicios registrados (p. ej. 2021–2025)."""
    return f"Análisis financiero {sec.ejercicios_de([d for d in lista if d.tiene_datos])} — informe integral"


def archivo_ejercicios(lista: list[DatosEjercicio]) -> str:
    """Ejercicios para el nombre del archivo: 2021_2025, o 2021_2023_2025 si hay huecos."""
    return "_".join("".join(c if c.isdigit() else " " for c in sec.ejercicios_de([d for d in lista if d.tiene_datos])).split())


def pares_consecutivos(lista: list[DatosEjercicio]) -> list[tuple[DatosEjercicio, DatosEjercicio]]:
    con_balance = [d for d in lista if d.bs.tiene_datos]
    return [(a, b) for a, b in zip(con_balance, con_balance[1:]) if b.anio == a.anio + 1]


def hojas_informe(session: Session, lista: list[DatosEjercicio] | None = None) -> list[tuple[str, list[sec.Seccion]]]:
    lista = lista if lista is not None else datos_todos(session)
    con_datos = [d for d in lista if d.tiene_datos]
    wacc = [calcular_wacc(d) for d in con_datos if d.bs.tiene_datos and d.inc.tiene_datos]
    sin_clasificar = sec.clasificacion(con_datos)
    return ([("Cuentas sin clasificar", [sin_clasificar])] if sin_clasificar else []) + [
        ("Estados originales", [sec.estados_originales(lista, "BALANCE"), sec.estados_originales(lista, "RESULTADOS")]),
        ("Horizontal", [sec.horizontal(lista, "rubros"), sec.horizontal(lista, "grupos")]),
        ("Vertical", [sec.vertical(lista, "ER"), sec.vertical(lista, "BG")]),
        ("Indicadores", [sec.indicadores(lista, c) for c in ind.CATEGORIAS if c != ind.DUPONT]
                        + [sec.indicadores_complementarios(lista)]),
        ("Capital de trabajo", [sec.capital_trabajo(lista)]),
        ("DuPont", sec.dupont(lista)),
        ("WACC", [sec.wacc_resumen(wacc), sec.supuestos_wacc()] + [sec.wacc_detalle(r) for r in wacc]),
        ("Origen y aplicación", [sec.fuentes_usos(calcular_fuentes_usos(a, b)) for a, b in pares_consecutivos(lista)]),
        ("Trazabilidad", sec.trazabilidad(session, lista)),
    ]
