"""Modelo DuPont de tres factores (seccion 9.5).

ROE = Margen neto x Rotacion de activos x Multiplicador del capital
  Margen neto          = Utilidad neta / Ingresos netos
  Rotacion de activos  = Ingresos netos / Activos totales promedio
  Multiplicador capital= Activos totales promedio / Patrimonio promedio
  ROE directo          = Utilidad neta / Patrimonio promedio x 100
El patrimonio es el patrimonio total del Balance (criterio aprobado para el
consolidado de Alutech; revisable al disponer de los estados publicados).

Saldos iniciales del ejercicio N (hallazgos A-01 y A-02):
  1. Balance final del ejercicio N-1 (exactamente el inmediato anterior;
     nunca otro anterior) si esta completo, con activo total > 0 y cuadra.
  2. Si no, saldos iniciales capturados manualmente para N, solo si son
     completos: al menos una cuenta de Activo y una de Patrimonio, con
     activo total > 0.
  3. Si no, se usa el saldo final de N como aproximacion: aproximado=True y
     `fuente` indica la causa concreta.

Si el patrimonio inicial, final o promedio es <= 0, el ROE no es
interpretable (A-04): disponible=False, interpretable=False, y no se genera
interpretacion de los factores.

Todos los calculos usan Decimal sin redondeo intermedio (B-01); los
porcentajes roe_*_pct se cuantizan a 2 decimales solo como valor final de
presentacion.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy.orm import Session

from calculations.balance_sheet import BalanceSheetResult, compute_balance_sheet
from calculations.controls import CONCILIADO, conciliar_resultado
from calculations.income_statement import compute_income_statement
from components.money import format_money, q2
from database.enums import CategoriaPrincipal as Cat
from database.models import FiscalPeriod
from database.repositories import get_fiscal_period, get_initial_balances_map, list_accounts

CERO = Decimal("0.00")
CIEN = Decimal("100")
DOS = Decimal("2")
TOLERANCIA_PCT = Decimal("0.01")


@dataclass
class SaldosIniciales:
    activo: Decimal | None
    patrimonio: Decimal | None
    aproximado: bool
    fuente: str


@dataclass
class Control:
    nombre: str
    correcto: bool
    detalle: str


def _problemas_balance_inicial(bs: BalanceSheetResult) -> list[str]:
    if not bs.tiene_datos:
        return ["no tiene datos de Balance"]
    problemas = []
    if not bs.completo:
        problemas.append(f"está incompleto (sin datos de {', '.join(bs.categorias_faltantes)})")
    if bs.total_activo <= CERO:
        problemas.append("tiene un activo total menor o igual a cero")
    if not bs.cuadra:
        problemas.append(f"no cuadra (diferencia {format_money(bs.diferencia)})")
    return problemas


def evaluar_balance_anterior(session: Session, fiscal_period: FiscalPeriod) -> tuple[BalanceSheetResult | None, str | None]:
    """(balance de N-1, None) si es utilizable como saldo inicial de N; si
    no, (None, causa)."""
    anio_previo = fiscal_period.anio - 1
    anterior = get_fiscal_period(session, anio_previo)
    if anterior is None:
        return None, f"no existe el ejercicio {anio_previo}"
    bs = compute_balance_sheet(session, anterior.id)
    problemas = _problemas_balance_inicial(bs)
    if problemas:
        return None, f"el Balance del ejercicio {anio_previo} {'; '.join(problemas)}"
    return bs, None


def _saldos_manuales(session: Session, fiscal_period_id: int) -> tuple[Decimal | None, Decimal | None, str | None]:
    """(activo, patrimonio, None) si los saldos manuales son completos; si
    no, (None, None, causa) o (None, None, None) si no hay ninguno."""
    mapa = get_initial_balances_map(session, fiscal_period_id)
    if not mapa:
        return None, None, None
    cuentas = {a.id: a for a in list_accounts(session)}
    activos = [v for i, v in mapa.items() if cuentas[i].categoria_principal == Cat.ACTIVO]
    patrimonio = [v for i, v in mapa.items() if cuentas[i].categoria_principal == Cat.PATRIMONIO]
    faltan = [n for n, valores in (("Activo", activos), ("Patrimonio", patrimonio)) if not valores]
    if faltan:
        return None, None, f"los saldos iniciales manuales están incompletos (sin datos de {', '.join(faltan)})"
    total_activo = sum(activos, CERO)
    if total_activo <= CERO:
        return None, None, "los saldos iniciales manuales tienen un activo total menor o igual a cero"
    return total_activo, sum(patrimonio, CERO), None


def get_saldos_iniciales(
    session: Session, fiscal_period: FiscalPeriod, saldo_final_activo: Decimal, saldo_final_patrimonio: Decimal
) -> SaldosIniciales:
    bs_anterior, causa = evaluar_balance_anterior(session, fiscal_period)
    if bs_anterior is not None:
        return SaldosIniciales(
            activo=bs_anterior.total_activo,
            patrimonio=bs_anterior.total_patrimonio,
            aproximado=False,
            fuente=f"Balance final del ejercicio {fiscal_period.anio - 1}",
        )

    activo, patrimonio, causa_manual = _saldos_manuales(session, fiscal_period.id)
    if activo is not None:
        return SaldosIniciales(
            activo=activo,
            patrimonio=patrimonio,
            aproximado=False,
            fuente=f"Saldos iniciales capturados manualmente (porque {causa})",
        )
    causas = [causa] + ([causa_manual] if causa_manual else ["no hay saldos iniciales manuales"])
    return SaldosIniciales(
        activo=saldo_final_activo,
        patrimonio=saldo_final_patrimonio,
        aproximado=True,
        fuente=f"APROXIMADO: se usa el saldo final del propio ejercicio como saldo inicial porque {'; '.join(causas)}",
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
    margen_neto: Decimal | None  # fraccion (no x100), sin redondear
    rotacion_activos: Decimal | None  # veces, sin redondear
    multiplicador_capital: Decimal | None  # veces, sin redondear
    roe_dupont_pct: Decimal | None  # presentacion: 2 decimales
    roe_directo_pct: Decimal | None  # presentacion: 2 decimales
    coincide_redondeo: bool | None  # identidad algebraica; no es un control (B-02)
    saldos_aproximados: bool
    fuente_saldos_iniciales: str | None
    interpretable: bool = True
    roe: Decimal | None = None  # fraccion sin redondear
    advertencias: list[str] = field(default_factory=list)
    controles: list[Control] = field(default_factory=list)


def compute_dupont(session: Session, fiscal_period: FiscalPeriod) -> DuPontResult:
    bs = compute_balance_sheet(session, fiscal_period.id)
    inc = compute_income_statement(session, fiscal_period.id)

    def vacio(motivo: str, **datos) -> DuPontResult:
        base = dict(
            utilidad_neta=None, ingresos_netos=None, activo_inicial=None, activo_final=None, activo_promedio=None,
            patrimonio_inicial=None, patrimonio_final=None, patrimonio_promedio=None, margen_neto=None,
            rotacion_activos=None, multiplicador_capital=None, roe_dupont_pct=None, roe_directo_pct=None,
            coincide_redondeo=None, saldos_aproximados=False, fuente_saldos_iniciales=None,
        )
        base.update(datos)
        return DuPontResult(disponible=False, motivo_no_disponible=motivo, **base)

    if not bs.tiene_datos:
        return vacio("No hay datos de Balance General capturados para este ejercicio.")
    if not inc.tiene_datos:
        return vacio("No hay datos de Estado de Resultados capturados para este ejercicio.")

    saldos = get_saldos_iniciales(session, fiscal_period, bs.total_activo, bs.total_patrimonio)
    activo_promedio = (saldos.activo + bs.total_activo) / DOS
    patrimonio_promedio = (saldos.patrimonio + bs.total_patrimonio) / DOS
    utilidad_neta = inc.utilidad_neta
    ingresos_netos = inc.ingresos_netos.subtotal
    conciliacion = conciliar_resultado(bs, inc)

    advertencias = []
    if saldos.aproximado:
        advertencias.append(saldos.fuente + ". Los promedios y el ROE son aproximados.")
    if not bs.completo:
        advertencias.append(f"Balance General INCOMPLETO (sin datos de {', '.join(bs.categorias_faltantes)}).")
    if not inc.completo:
        advertencias.append(f"Estado de Resultados INCOMPLETO (sin datos de {', '.join(inc.categorias_faltantes)}).")
    if not bs.cuadra:
        advertencias.append(f"El Balance General no cuadra (diferencia {format_money(bs.diferencia)}).")
    if bs.advertencias_signo or inc.advertencias_signo:
        advertencias.append("Hay importes con signo distinto a la convención; revíselos en los reportes del Balance y de Resultados.")

    controles = [
        Control("Balance del ejercicio cuadra", bs.cuadra, f"Diferencia: {format_money(bs.diferencia)}"),
        Control("Balance del ejercicio completo", bs.completo,
                "Completo" if bs.completo else f"Sin datos de {', '.join(bs.categorias_faltantes)}"),
        Control("Estado de Resultados completo", inc.completo,
                "Completo" if inc.completo else f"Sin datos de {', '.join(inc.categorias_faltantes)}"),
        Control("Saldos iniciales reales (no aproximados)", not saldos.aproximado, saldos.fuente),
        Control("Resultado del ejercicio conciliado con la utilidad neta", conciliacion.estado == CONCILIADO,
                conciliacion.mensaje),
        Control("Signos según la convención", not (bs.advertencias_signo or inc.advertencias_signo),
                f"{len(bs.advertencias_signo) + len(inc.advertencias_signo)} importe(s) con signo atípico"),
    ]
    comunes = dict(
        utilidad_neta=utilidad_neta, ingresos_netos=ingresos_netos, activo_inicial=saldos.activo,
        activo_final=bs.total_activo, activo_promedio=activo_promedio, patrimonio_inicial=saldos.patrimonio,
        patrimonio_final=bs.total_patrimonio, patrimonio_promedio=patrimonio_promedio,
        saldos_aproximados=saldos.aproximado, fuente_saldos_iniciales=saldos.fuente,
        advertencias=advertencias, controles=controles,
    )

    if ingresos_netos == CERO:
        return vacio("Los ingresos netos son cero; no se puede calcular el margen neto ni la rotacion de activos.", **comunes)
    if activo_promedio <= CERO:
        return vacio("El activo total promedio es cero o negativo; no se puede calcular la rotacion de activos.", **comunes)
    if patrimonio_promedio == CERO:
        return vacio("El patrimonio promedio es cero; no se puede calcular el multiplicador del capital ni el ROE.", **comunes)

    margen_neto = utilidad_neta / ingresos_netos
    rotacion_activos = ingresos_netos / activo_promedio
    multiplicador_capital = activo_promedio / patrimonio_promedio
    roe = margen_neto * rotacion_activos * multiplicador_capital
    roe_directo = utilidad_neta / patrimonio_promedio
    factores = dict(
        margen_neto=margen_neto, rotacion_activos=rotacion_activos, multiplicador_capital=multiplicador_capital,
        roe_dupont_pct=q2(roe * CIEN), roe_directo_pct=q2(roe_directo * CIEN),
        coincide_redondeo=abs(q2(roe * CIEN) - q2(roe_directo * CIEN)) <= TOLERANCIA_PCT,
    )

    no_positivos = [
        f"{nombre} ({format_money(valor)})"
        for nombre, valor in (("inicial", saldos.patrimonio), ("final", bs.total_patrimonio), ("promedio", patrimonio_promedio))
        if valor <= CERO
    ]
    controles.append(Control("Patrimonio inicial, final y promedio positivos", not no_positivos,
                             "Positivos" if not no_positivos else "No positivo: " + ", ".join(no_positivos)))
    if no_positivos:
        motivo = (
            "ROE NO INTERPRETABLE: el patrimonio " + ", ".join(no_positivos) + " es cero o negativo. Con patrimonio "
            "negativo el cociente puede dar un ROE positivo aunque haya pérdidas, y el multiplicador pierde su "
            "significado. Los factores se muestran solo como referencia."
        )
        resultado = vacio(motivo, **comunes, **factores)
        resultado.interpretable = False
        resultado.roe = roe
        return resultado

    return DuPontResult(disponible=True, motivo_no_disponible=None, roe=roe, **comunes, **factores)


def generar_interpretacion(resultado: DuPontResult) -> str:
    """Interpretacion basada exclusivamente en los valores calculados. No se
    interpretan los factores si el ROE no es interpretable."""
    if not resultado.disponible:
        return f"No es posible generar una interpretacion: {resultado.motivo_no_disponible}"

    margen_pct = resultado.margen_neto * CIEN
    partes = [
        f"El margen neto fue de {margen_pct:.4f}%, es decir, de cada 100 unidades monetarias de ingresos netos "
        f"la empresa convirtio {margen_pct:.2f} en utilidad neta.",
        f"La rotacion de activos fue de {resultado.rotacion_activos:.4f} veces: los activos totales promedio "
        f"generaron {resultado.rotacion_activos:.2f} veces su valor en ingresos netos durante el ejercicio.",
        f"El multiplicador del capital fue de {resultado.multiplicador_capital:.4f} veces: los activos totales "
        f"promedio equivalen a {resultado.multiplicador_capital:.2f} veces el patrimonio promedio (a mayor "
        "multiplicador, mayor proporcion de los activos financiada con pasivos en lugar de patrimonio).",
        f"El producto de los tres factores da un ROE de {resultado.roe_dupont_pct:.2f}% (utilidad neta / "
        "patrimonio promedio, calculado con el patrimonio total).",
    ]
    if resultado.saldos_aproximados:
        partes.append(
            "Advertencia: no se dispuso de un saldo inicial real para este ejercicio, por lo que el activo y "
            "patrimonio promedio se aproximaron usando el saldo final como saldo inicial. Los resultados de este "
            "modelo DuPont deben interpretarse con esa limitacion."
        )
    if any("INCOMPLETO" in a for a in resultado.advertencias):
        partes.append("Advertencia: al menos un estado financiero del ejercicio está incompleto.")
    return " ".join(partes)
