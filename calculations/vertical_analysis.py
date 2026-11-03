"""Analisis vertical del Balance General y del Estado de Resultados
(secciones 9.3 y 9.4). Porcentaje = valor / base * 100.

Si la base es cero (o no hay datos), no se inventa un porcentaje: se
devuelve None y el reporte debe mostrar "No disponible".

Ademas de las cuentas (`filas`), el resultado incluye los subtotales,
totales y utilidades (`subtotales`) y la presentacion completa en orden
(`lineas`), hallazgo M-03. Un grupo sin cuentas capturadas tiene valor
None ("Sin datos"), no 0. En el Estado de Resultados, `efecto` indica si
la linea resta o suma: los costos y gastos se capturan en positivo y se
restan, por lo que su porcentaje es positivo aunque disminuya la utilidad.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy.orm import Session

from calculations.balance_sheet import compute_balance_sheet
from calculations.income_statement import compute_income_statement
from components.money import q2
from database.models import Account

CERO = Decimal("0.00")
CIEN = Decimal("100")
RESTA = "resta"
SUMA = "suma"
SIGNO = "signo"  # resultados netos que se suman con su propio signo (financiero, no operativo)
ETIQUETA_EFECTO = {RESTA: "(−) resta", SUMA: "(+) suma", SIGNO: "(±) con su signo"}


@dataclass
class FilaVertical:
    cuenta: Account
    valor: Decimal
    porcentaje: Decimal | None


@dataclass
class LineaVertical:
    tipo: str  # "cuenta", "subtotal" o "total"
    etiqueta: str
    valor: Decimal | None  # None: grupo sin datos capturados
    porcentaje: Decimal | None
    codigo: str = ""
    efecto: str = ""  # RESTA, SUMA, SIGNO o "" (solo Estado de Resultados)


def _porcentaje(valor: Decimal, base: Decimal) -> Decimal | None:
    if base == CERO:
        return None
    return q2((valor / base) * CIEN)


def _linea(tipo: str, etiqueta: str, valor: Decimal | None, base: Decimal, codigo: str = "", efecto: str = "") -> LineaVertical:
    return LineaVertical(tipo, etiqueta, valor, None if valor is None else _porcentaje(valor, base), codigo, efecto)


def _cuentas(grupos, base: Decimal, efecto: str = "") -> list[LineaVertical]:
    return [_linea("cuenta", l.cuenta.nombre, l.valor, base, l.cuenta.codigo, efecto) for g in grupos for l in g.lineas]


def _si_hay(grupos, valor: Decimal) -> Decimal | None:
    return valor if any(g.lineas for g in grupos) else None


@dataclass
class VerticalBalanceResult:
    base_total_activo: Decimal
    filas: list[FilaVertical]
    disponible: bool
    subtotales: list[LineaVertical] = field(default_factory=list)
    lineas: list[LineaVertical] = field(default_factory=list)


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

    ac, anc, pc, pnc = bs.activo_corriente, bs.activo_no_corriente, bs.pasivo_corriente, bs.pasivo_no_corriente
    subtotales = {
        "ac": _linea("subtotal", "Activo corriente", _si_hay([ac], ac.subtotal), base),
        "anc": _linea("subtotal", "Activo no corriente", _si_hay([anc], anc.subtotal), base),
        "ta": _linea("total", "TOTAL ACTIVO", bs.total_activo, base),
        "pc": _linea("subtotal", "Pasivo corriente", _si_hay([pc], pc.subtotal), base),
        "pnc": _linea("subtotal", "Pasivo no corriente", _si_hay([pnc], pnc.subtotal), base),
        "tp": _linea("total", "TOTAL PASIVO", _si_hay([pc, pnc], bs.total_pasivo), base),
        "pat": _linea("total", "TOTAL PATRIMONIO", _si_hay(bs.patrimonio_grupos, bs.total_patrimonio), base),
        "tpp": _linea("total", "TOTAL PASIVO + PATRIMONIO", bs.total_pasivo_patrimonio, base),
    }
    lineas = (
        _cuentas([ac], base) + [subtotales["ac"]]
        + _cuentas([anc], base) + [subtotales["anc"], subtotales["ta"]]
        + _cuentas([pc], base) + [subtotales["pc"]]
        + _cuentas([pnc], base) + [subtotales["pnc"], subtotales["tp"]]
        + _cuentas(bs.patrimonio_grupos, base) + [subtotales["pat"], subtotales["tpp"]]
    )
    return VerticalBalanceResult(
        base_total_activo=base, filas=filas, disponible=bs.tiene_datos and base != CERO,
        subtotales=list(subtotales.values()), lineas=lineas,
    )


@dataclass
class VerticalIncomeResult:
    base_ingresos_netos: Decimal
    filas: list[FilaVertical]
    disponible: bool
    subtotales: list[LineaVertical] = field(default_factory=list)
    lineas: list[LineaVertical] = field(default_factory=list)


def compute_vertical_income(session: Session, fiscal_period_id: int) -> VerticalIncomeResult:
    inc = compute_income_statement(session, fiscal_period_id)
    base = inc.ingresos_netos.subtotal
    filas: list[FilaVertical] = []
    grupos = (
        inc.ingresos_netos,
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

    operativos = [inc.gastos_administracion, inc.gastos_ventas, inc.otros_ingresos_operativos, inc.otros_gastos_operativos]
    financieros = [inc.ingresos_financieros, inc.gastos_financieros]
    no_operativos = [inc.otros_ingresos_no_operativos, inc.otros_gastos_no_operativos]
    subtotales = {
        "ing": _linea("subtotal", "Ingresos netos", _si_hay([inc.ingresos_netos], inc.ingresos_netos.subtotal), base),
        "costo": _linea("subtotal", "Costo de ventas", _si_hay([inc.costo_ventas], inc.costo_ventas.subtotal), base, efecto=RESTA),
        "ub": _linea("total", "UTILIDAD BRUTA", inc.utilidad_bruta, base),
        # Gastos operativos netos = admin + ventas - otros ingresos op. + otros gastos op. (restan de la UB).
        "gop": _linea("subtotal", "Gastos operativos netos", _si_hay(operativos, inc.utilidad_bruta - inc.utilidad_operativa),
                      base, efecto=RESTA),
        "uo": _linea("total", "UTILIDAD OPERATIVA", inc.utilidad_operativa, base),
        "rf": _linea("subtotal", "Resultado financiero", _si_hay(financieros, inc.resultado_financiero), base, efecto=SIGNO),
        "or": _linea("subtotal", "Otros resultados no operativos", _si_hay(no_operativos, inc.otros_resultados), base,
                     efecto=SIGNO),
        "uai": _linea("total", "UTILIDAD ANTES DE IMPUESTOS", inc.utilidad_antes_impuestos, base),
        "isr": _linea("subtotal", "Impuesto sobre la renta", _si_hay([inc.impuesto_renta], inc.impuesto_renta.subtotal), base,
                      efecto=RESTA),
        "un": _linea("total", "UTILIDAD NETA", inc.utilidad_neta, base),
    }
    lineas = (
        _cuentas([inc.ingresos_netos], base) + [subtotales["ing"]]
        + _cuentas([inc.costo_ventas], base, RESTA) + [subtotales["costo"], subtotales["ub"]]
        + _cuentas([inc.gastos_administracion, inc.gastos_ventas], base, RESTA)
        + _cuentas([inc.otros_ingresos_operativos], base, SUMA)
        + _cuentas([inc.otros_gastos_operativos], base, RESTA) + [subtotales["gop"], subtotales["uo"]]
        + _cuentas([inc.ingresos_financieros], base, SUMA) + _cuentas([inc.gastos_financieros], base, RESTA)
        + [subtotales["rf"]]
        + _cuentas([inc.otros_ingresos_no_operativos], base, SUMA) + _cuentas([inc.otros_gastos_no_operativos], base, RESTA)
        + [subtotales["or"], subtotales["uai"]]
        + _cuentas([inc.impuesto_renta], base, RESTA) + [subtotales["isr"], subtotales["un"]]
    )
    return VerticalIncomeResult(
        base_ingresos_netos=base, filas=filas, disponible=inc.tiene_datos and base != CERO,
        subtotales=list(subtotales.values()), lineas=lineas,
    )
