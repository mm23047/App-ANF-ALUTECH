"""Modelo DuPont de tres factores (seccion 9.5).

ROE = Margen neto x Rotacion de activos x Multiplicador del capital
  Margen neto          = Utilidad neta / Ingresos netos
  Rotacion de activos  = Ingresos netos / Activos totales promedio
  Multiplicador capital= Activos totales promedio / Patrimonio promedio
  ROE directo          = Utilidad neta / Patrimonio promedio x 100

Saldos iniciales (resolucion de ambiguedad confirmada con el usuario):
  1. Si existe un ejercicio fiscal anterior en el sistema (sin importar
     huecos) y tiene datos de Balance capturados, su Balance final se usa
     como saldo inicial del ejercicio actual (encadenamiento automatico).
  2. Si no existe ejercicio anterior con datos, se usan los registros de
     `initial_balance` capturados manualmente para este ejercicio.
  3. Si tampoco hay saldos iniciales capturados, se usa el saldo final del
     propio ejercicio como aproximacion del saldo inicial -- se marca
     `aproximado=True` y se debe mostrar la limitacion en el reporte.

Ningun calculo que dependa de una division entre cero o de un dato
inexistente se aproxima silenciosamente: se devuelve None y una razon.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from calculations.balance_sheet import compute_balance_sheet
from calculations.income_statement import compute_income_statement
from components.money import q2
from database.models import FiscalPeriod
from database.repositories import get_initial_balances_map, get_previous_period, list_accounts
from database.enums import CategoriaPrincipal as Cat

CERO = Decimal("0.00")
CIEN = Decimal("100")
TOLERANCIA_PCT = Decimal("0.01")


@dataclass
class SaldosIniciales:
    activo: Decimal | None
    patrimonio: Decimal | None
    aproximado: bool
    fuente: str


def _saldos_iniciales_desde_tabla(session: Session, fiscal_period_id: int) -> tuple[Decimal, Decimal] | None:
    mapa = get_initial_balances_map(session, fiscal_period_id)
    if not mapa:
        return None
    cuentas = {a.id: a for a in list_accounts(session)}
    total_activo = CERO
    total_patrimonio = CERO
    for account_id, valor in mapa.items():
        cuenta = cuentas.get(account_id)
        if cuenta is None:
            continue
        if cuenta.categoria_principal == Cat.ACTIVO:
            total_activo += valor
        elif cuenta.categoria_principal == Cat.PATRIMONIO:
            total_patrimonio += valor
    return q2(total_activo), q2(total_patrimonio)


def get_saldos_iniciales(
    session: Session, fiscal_period: FiscalPeriod, saldo_final_activo: Decimal, saldo_final_patrimonio: Decimal
) -> SaldosIniciales:
    anterior = get_previous_period(session, fiscal_period.anio)
    if anterior is not None:
        bs_anterior = compute_balance_sheet(session, anterior.id)
        if bs_anterior.tiene_datos:
            return SaldosIniciales(
                activo=bs_anterior.total_activo,
                patrimonio=bs_anterior.total_patrimonio,
                aproximado=False,
                fuente=f"Balance final del ejercicio {anterior.anio}",
            )

    desde_tabla = _saldos_iniciales_desde_tabla(session, fiscal_period.id)
    if desde_tabla is not None:
        activo, patrimonio = desde_tabla
        return SaldosIniciales(
            activo=activo,
            patrimonio=patrimonio,
            aproximado=False,
            fuente="Saldos iniciales capturados manualmente",
        )

    return SaldosIniciales(
        activo=saldo_final_activo,
        patrimonio=saldo_final_patrimonio,
        aproximado=True,
        fuente="Aproximacion: se usa el saldo final del propio ejercicio (no hay saldo inicial disponible)",
    )


@dataclass
class DuPontResult:
    disponible: bool
    motivo_no_disponible: str | None
    utilidad_neta: Decimal | None
    ingresos_netos: Decimal | None
    activo_inicial: Decimal | None
    activo_final: Decimal | None
    activo_promedio: Decimal | None
    patrimonio_inicial: Decimal | None
    patrimonio_final: Decimal | None
    patrimonio_promedio: Decimal | None
    margen_neto: Decimal | None  # fraccion (no x100)
    rotacion_activos: Decimal | None  # veces
    multiplicador_capital: Decimal | None  # veces
    roe_dupont_pct: Decimal | None
    roe_directo_pct: Decimal | None
    coincide_redondeo: bool | None
    saldos_aproximados: bool
    fuente_saldos_iniciales: str | None


def compute_dupont(session: Session, fiscal_period: FiscalPeriod) -> DuPontResult:
    bs = compute_balance_sheet(session, fiscal_period.id)
    inc = compute_income_statement(session, fiscal_period.id)

    def vacio(motivo: str) -> DuPontResult:
        return DuPontResult(
            disponible=False,
            motivo_no_disponible=motivo,
            utilidad_neta=None,
            ingresos_netos=None,
            activo_inicial=None,
            activo_final=None,
            activo_promedio=None,
            patrimonio_inicial=None,
            patrimonio_final=None,
            patrimonio_promedio=None,
            margen_neto=None,
            rotacion_activos=None,
            multiplicador_capital=None,
            roe_dupont_pct=None,
            roe_directo_pct=None,
            coincide_redondeo=None,
            saldos_aproximados=False,
            fuente_saldos_iniciales=None,
        )

    if not bs.tiene_datos:
        return vacio("No hay datos de Balance General capturados para este ejercicio.")
    if not inc.tiene_datos:
        return vacio("No hay datos de Estado de Resultados capturados para este ejercicio.")

    saldos = get_saldos_iniciales(session, fiscal_period, bs.total_activo, bs.total_patrimonio)

    activo_promedio = q2((saldos.activo + bs.total_activo) / Decimal("2"))
    patrimonio_promedio = q2((saldos.patrimonio + bs.total_patrimonio) / Decimal("2"))

    utilidad_neta = inc.utilidad_neta
    ingresos_netos = inc.ingresos_netos.subtotal

    if ingresos_netos == CERO:
        return vacio("Los ingresos netos son cero; no se puede calcular el margen neto ni la rotacion de activos.")
    if activo_promedio == CERO:
        return vacio("El activo total promedio es cero; no se puede calcular la rotacion de activos.")
    if patrimonio_promedio == CERO:
        return vacio("El patrimonio promedio es cero; no se puede calcular el multiplicador del capital ni el ROE.")

    margen_neto = utilidad_neta / ingresos_netos
    rotacion_activos = ingresos_netos / activo_promedio
    multiplicador_capital = activo_promedio / patrimonio_promedio

    roe_dupont = margen_neto * rotacion_activos * multiplicador_capital
    roe_dupont_pct = q2(roe_dupont * CIEN)
    roe_directo_pct = q2((utilidad_neta / patrimonio_promedio) * CIEN)

    coincide = abs(roe_dupont_pct - roe_directo_pct) <= TOLERANCIA_PCT

    return DuPontResult(
        disponible=True,
        motivo_no_disponible=None,
        utilidad_neta=utilidad_neta,
        ingresos_netos=ingresos_netos,
        activo_inicial=saldos.activo,
        activo_final=bs.total_activo,
        activo_promedio=activo_promedio,
        patrimonio_inicial=saldos.patrimonio,
        patrimonio_final=bs.total_patrimonio,
        patrimonio_promedio=patrimonio_promedio,
        margen_neto=q2(margen_neto * CIEN) / CIEN,
        rotacion_activos=q2(rotacion_activos),
        multiplicador_capital=q2(multiplicador_capital),
        roe_dupont_pct=roe_dupont_pct,
        roe_directo_pct=roe_directo_pct,
        coincide_redondeo=coincide,
        saldos_aproximados=saldos.aproximado,
        fuente_saldos_iniciales=saldos.fuente,
    )


def generar_interpretacion(resultado: DuPontResult) -> str:
    """Interpretacion basada exclusivamente en los valores calculados."""
    if not resultado.disponible:
        return f"No es posible generar una interpretacion: {resultado.motivo_no_disponible}"

    partes = []
    partes.append(
        f"El margen neto fue de {resultado.margen_neto * CIEN:.2f}%, es decir, de cada 100 unidades "
        f"monetarias de ingresos netos la empresa convirtio {resultado.margen_neto * CIEN:.2f} en utilidad neta."
    )
    partes.append(
        f"La rotacion de activos fue de {resultado.rotacion_activos:.2f} veces, lo que indica que "
        f"los activos totales promedio generaron {resultado.rotacion_activos:.2f} veces su valor en ingresos netos durante el ejercicio."
    )
    partes.append(
        f"El multiplicador del capital fue de {resultado.multiplicador_capital:.2f} veces, "
        f"reflejando que los activos totales promedio equivalen a {resultado.multiplicador_capital:.2f} veces el patrimonio promedio "
        "(a mayor multiplicador, mayor proporcion de los activos esta financiada con deuda en lugar de capital propio)."
    )
    partes.append(
        f"La combinacion de estos tres factores produce un ROE (DuPont) de {resultado.roe_dupont_pct:.2f}%, "
        f"que {'coincide' if resultado.coincide_redondeo else 'NO coincide'} con el ROE directo de {resultado.roe_directo_pct:.2f}% "
        "(considerando el redondeo)."
    )
    if resultado.saldos_aproximados:
        partes.append(
            "Advertencia: no se dispuso de un saldo inicial real para este ejercicio, por lo que el "
            "activo y patrimonio promedio se aproximaron usando el saldo final como saldo inicial. "
            "Los resultados de este modelo DuPont deben interpretarse con esa limitacion."
        )
    return " ".join(partes)
