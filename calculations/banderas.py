"""Banderas de calidad de un reporte (hallazgos M-04, M-08 y fase 3.3).

Unica fuente de los estados que se muestran en pantalla, PDF, Excel y
Dashboard, para que coincidan en todos los formatos. Un reporte sin
banderas es DEFINITIVO.
"""
from __future__ import annotations

from dataclasses import dataclass

from calculations.controls import DIFERENCIA, Conciliacion
from components.money import format_money

INCOMPLETO = "INCOMPLETO"
DESCUADRADO = "DESCUADRADO"
NO_INTERPRETABLE = "NO INTERPRETABLE"
SIGNO_ATIPICO = "SIGNO ATÍPICO"
SIN_CONCILIAR = "SIN CONCILIAR"
DEFINITIVO = "DEFINITIVO"


@dataclass(frozen=True)
class Bandera:
    codigo: str
    texto: str


def _comunes(resultado, nombre: str) -> list[Bandera]:
    banderas = []
    if not resultado.completo:
        banderas.append(Bandera(INCOMPLETO, f"{nombre} incompleto: sin datos de {', '.join(resultado.categorias_faltantes)}. "
                                            "Esos importes no son cero: no se capturaron."))
    if resultado.advertencias_signo:
        banderas.append(Bandera(SIGNO_ATIPICO, f"{len(resultado.advertencias_signo)} importe(s) con signo distinto a la "
                                               "convención (se muestran sin invertir): " + " | ".join(resultado.advertencias_signo)))
    return banderas


def _conciliacion(conciliacion: Conciliacion | None) -> list[Bandera]:
    if conciliacion is not None and conciliacion.estado == DIFERENCIA:
        return [Bandera(SIN_CONCILIAR, conciliacion.mensaje)]
    return []


def banderas_balance(bs, conciliacion: Conciliacion | None = None) -> list[Bandera]:
    banderas = _comunes(bs, "Balance General")
    if not bs.cuadra:
        banderas.insert(0, Bandera(DESCUADRADO, f"Activo − (Pasivo + Patrimonio) = {format_money(bs.diferencia)}; "
                                                "la ecuación contable no cuadra."))
    return banderas + _conciliacion(conciliacion)


def banderas_resultados(inc, conciliacion: Conciliacion | None = None) -> list[Bandera]:
    return _comunes(inc, "Estado de Resultados") + _conciliacion(conciliacion)


def banderas_dupont(dp) -> list[Bandera]:
    banderas = []
    if not dp.interpretable:
        banderas.append(Bandera(NO_INTERPRETABLE, dp.motivo_no_disponible))
    for control in dp.controles:
        if control.correcto:
            continue
        if control.nombre == "Balance del ejercicio cuadra":
            banderas.append(Bandera(DESCUADRADO, f"El Balance del ejercicio no cuadra ({control.detalle})."))
        elif control.nombre.endswith("completo"):
            banderas.append(Bandera(INCOMPLETO, f"{control.nombre.replace(' completo', '')}: {control.detalle}."))
        elif control.nombre == "Signos según la convención":
            banderas.append(Bandera(SIGNO_ATIPICO, control.detalle))
        elif control.nombre.startswith("Resultado del ejercicio") and not control.sin_datos:
            # Sin datos para conciliar no es una diferencia: mismo criterio que banderas_balance.
            banderas.append(Bandera(SIN_CONCILIAR, control.detalle))
    return banderas


def resumen(banderas: list[Bandera]) -> str:
    """"DEFINITIVO" o los codigos sin repetir, en orden: "INCOMPLETO · DESCUADRADO"."""
    codigos = list(dict.fromkeys(b.codigo for b in banderas))
    return " · ".join(codigos) if codigos else DEFINITIVO
