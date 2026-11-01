"""Controles entre estados financieros (hallazgo M-07).

Conciliacion: el "Resultado del ejercicio" capturado en el patrimonio del
Balance debe coincidir con la utilidad neta del Estado de Resultados del
mismo ejercicio. Se informa la diferencia; nunca se corrige un importe.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from calculations.balance_sheet import BalanceSheetResult
from calculations.income_statement import IncomeStatementResult
from database.enums import Subcategoria as Sub

CONCILIADO = "CONCILIADO"
DIFERENCIA = "DIFERENCIA"
SIN_DATOS = "SIN_DATOS"


@dataclass
class Conciliacion:
    estado: str  # CONCILIADO, DIFERENCIA o SIN_DATOS
    resultado_patrimonio: Decimal | None  # None: no se capturo "Resultado del ejercicio"
    utilidad_neta: Decimal | None  # None: no hay Estado de Resultados
    diferencia: Decimal | None  # resultado_patrimonio - utilidad_neta
    datos_faltantes: bool  # True si algun estado esta incompleto (posible causa de la diferencia)
    mensaje: str


def conciliar_resultado(bs: BalanceSheetResult, inc: IncomeStatementResult) -> Conciliacion:
    lineas = [l for g in bs.patrimonio_grupos for l in g.lineas if l.cuenta.subcategoria == Sub.RESULTADO_EJERCICIO]
    resultado = sum((l.valor for l in lineas), Decimal("0.00")) if lineas else None
    utilidad = inc.utilidad_neta if inc.tiene_datos else None
    incompletos = [n for n, completo in (("Balance General", bs.completo), ("Estado de Resultados", inc.completo)) if not completo]

    if resultado is None or utilidad is None:
        falta = []
        if resultado is None:
            falta.append("no se capturó 'Resultado del ejercicio' en el patrimonio")
        if utilidad is None:
            falta.append("no hay Estado de Resultados capturado")
        return Conciliacion(SIN_DATOS, resultado, utilidad, None, True, "No se puede conciliar: " + " y ".join(falta) + ".")

    diferencia = resultado - utilidad
    if diferencia == 0:
        return Conciliacion(CONCILIADO, resultado, utilidad, diferencia, bool(incompletos),
                            "El resultado del ejercicio en el patrimonio coincide con la utilidad neta.")
    if incompletos:
        causa = (f"Posible causa: datos faltantes ({' y '.join(incompletos)} incompleto). "
                 "Complete la captura antes de concluir que existe una diferencia real.")
    else:
        causa = ("Ambos estados están completos: es una diferencia real. Revise los importes, o si en el ejercicio "
                 "hubo dividendos o traspasos que expliquen la diferencia.")
    return Conciliacion(DIFERENCIA, resultado, utilidad, diferencia, bool(incompletos),
                        f"El resultado del ejercicio en el patrimonio ({resultado}) difiere de la utilidad neta "
                        f"({utilidad}) en {diferencia}. {causa} Los importes no se modifican automáticamente.")
