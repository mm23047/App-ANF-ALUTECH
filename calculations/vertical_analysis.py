"""Analisis vertical del Balance General y del Estado de Resultados
(secciones 9.3 y 9.4). Porcentaje = valor_cuenta / base * 100.

Si la base es cero (o no hay datos), no se inventa un porcentaje: se
devuelve None y el reporte debe mostrar "No disponible".
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from calculations.balance_sheet import compute_balance_sheet
from calculations.income_statement import compute_income_statement
from components.money import q2
from database.models import Account

CERO = Decimal("0.00")
CIEN = Decimal("100")


@dataclass
class FilaVertical:
    cuenta: Account
    valor: Decimal
    porcentaje: Decimal | None


def _porcentaje(valor: Decimal, base: Decimal) -> Decimal | None:
    if base == CERO:
        return None
    return q2((valor / base) * CIEN)


@dataclass
class VerticalBalanceResult:
    base_total_activo: Decimal
    filas: list[FilaVertical]
    disponible: bool


def compute_vertical_balance(session: Session, fiscal_period_id: int) -> VerticalBalanceResult:
    bs = compute_balance_sheet(session, fiscal_period_id)
    base = bs.total_activo
    filas: list[FilaVertical] = []
    for grupo in (bs.activo_corriente, bs.activo_no_corriente, bs.pasivo_corriente, bs.pasivo_no_corriente):
        for linea in grupo.lineas:
            filas.append(FilaVertical(linea.cuenta, linea.valor, _porcentaje(linea.valor, base)))
    for grupo in bs.patrimonio_grupos:
        for linea in grupo.lineas:
            filas.append(FilaVertical(linea.cuenta, linea.valor, _porcentaje(linea.valor, base)))

    return VerticalBalanceResult(
        base_total_activo=base, filas=filas, disponible=bs.tiene_datos and base != CERO
    )


@dataclass
class VerticalIncomeResult:
    base_ingresos_netos: Decimal
    filas: list[FilaVertical]
    disponible: bool


def compute_vertical_income(session: Session, fiscal_period_id: int) -> VerticalIncomeResult:
    inc = compute_income_statement(session, fiscal_period_id)
    base = inc.ingresos_netos.subtotal
    filas: list[FilaVertical] = []
    grupos = (
        inc.costo_ventas,
        inc.gastos_administracion,
        inc.gastos_ventas,
        inc.otros_ingresos_operativos,
        inc.otros_gastos_operativos,
        inc.ingresos_financieros,
        inc.gastos_financieros,
        inc.otros_ingresos_no_operativos,
        inc.otros_gastos_no_operativos,
        inc.impuesto_renta,
    )
    for grupo in grupos:
        for linea in grupo.lineas:
            filas.append(FilaVertical(linea.cuenta, linea.valor, _porcentaje(linea.valor, base)))

    return VerticalIncomeResult(
        base_ingresos_netos=base, filas=filas, disponible=inc.tiene_datos and base != CERO
    )
