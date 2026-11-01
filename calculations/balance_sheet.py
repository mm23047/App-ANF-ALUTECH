"""Calculo del Balance General (seccion 9.1).

Los subtotales y totales se derivan en memoria a partir de los
balance_entry vigentes -- nunca se almacenan (seccion 12).

Una cuenta sin importe no es un cero: `completo` indica si cada categoria
obligatoria (Activo, Pasivo, Patrimonio) tiene al menos una cuenta
capturada, y `cuentas_sin_dato` lista las cuentas activas sin importe
(hallazgo M-04). `advertencias_signo` aplica la convencion de signos sin
modificar ningun importe (A-05).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy.orm import Session

from calculations.validation import OBLIGATORIAS_BALANCE, aviso_signo, categorias_faltantes, cuentas_sin_dato
from components.money import q2
from database.enums import CategoriaPrincipal as Cat
from database.enums import Subcategoria as Sub
from database.enums import TipoEstadoFinanciero
from database.models import Account
from database.repositories import list_accounts, list_entries

CERO = Decimal("0.00")

PATRIMONIO_SUBCATEGORIAS = [
    (Sub.CAPITAL_SOCIAL, "Capital social"),
    (Sub.RESERVAS, "Reservas"),
    (Sub.RESULTADOS_ACUMULADOS, "Resultados acumulados"),
    (Sub.RESULTADO_EJERCICIO, "Resultado del ejercicio"),
    (Sub.OTRAS_PATRIMONIALES, "Otras cuentas patrimoniales"),
]


@dataclass
class Linea:
    cuenta: Account
    valor: Decimal


@dataclass
class Grupo:
    nombre: str
    lineas: list[Linea]
    subtotal: Decimal


@dataclass
class BalanceSheetResult:
    tiene_datos: bool
    activo_corriente: Grupo
    activo_no_corriente: Grupo
    total_activo: Decimal
    pasivo_corriente: Grupo
    pasivo_no_corriente: Grupo
    total_pasivo: Decimal
    patrimonio_grupos: list[Grupo]
    total_patrimonio: Decimal
    total_pasivo_patrimonio: Decimal
    diferencia: Decimal
    cuadra: bool
    completo: bool = False
    categorias_faltantes: list[str] = field(default_factory=list)
    cuentas_sin_dato: list[Account] = field(default_factory=list)
    advertencias_signo: list[str] = field(default_factory=list)


def _grupo(nombre: str, lineas: list[Linea]) -> Grupo:
    subtotal = q2(sum((l.valor for l in lineas), CERO))
    return Grupo(nombre=nombre, lineas=lineas, subtotal=subtotal)


def compute_balance_sheet(session: Session, fiscal_period_id: int) -> BalanceSheetResult:
    entries = list_entries(session, fiscal_period_id, TipoEstadoFinanciero.BALANCE)

    def filtro(categoria: Cat, subcategoria: Sub | None = None) -> list[Linea]:
        return [
            Linea(a, v)
            for a, v in entries
            if a.categoria_principal == categoria
            and (subcategoria is None or a.subcategoria == subcategoria)
        ]

    activo_corriente = _grupo("Activo corriente", filtro(Cat.ACTIVO, Sub.CORRIENTE))
    activo_no_corriente = _grupo("Activo no corriente", filtro(Cat.ACTIVO, Sub.NO_CORRIENTE))
    total_activo = q2(activo_corriente.subtotal + activo_no_corriente.subtotal)

    pasivo_corriente = _grupo("Pasivo corriente", filtro(Cat.PASIVO, Sub.CORRIENTE))
    pasivo_no_corriente = _grupo("Pasivo no corriente", filtro(Cat.PASIVO, Sub.NO_CORRIENTE))
    total_pasivo = q2(pasivo_corriente.subtotal + pasivo_no_corriente.subtotal)

    patrimonio_grupos = [
        _grupo(nombre, filtro(Cat.PATRIMONIO, sub)) for sub, nombre in PATRIMONIO_SUBCATEGORIAS
    ]
    total_patrimonio = q2(sum((g.subtotal for g in patrimonio_grupos), CERO))

    total_pasivo_patrimonio = q2(total_pasivo + total_patrimonio)
    diferencia = q2(total_activo - total_pasivo_patrimonio)
    cuadra = diferencia == CERO
    faltantes = categorias_faltantes(entries, OBLIGATORIAS_BALANCE)

    return BalanceSheetResult(
        tiene_datos=len(entries) > 0,
        activo_corriente=activo_corriente,
        activo_no_corriente=activo_no_corriente,
        total_activo=total_activo,
        pasivo_corriente=pasivo_corriente,
        pasivo_no_corriente=pasivo_no_corriente,
        total_pasivo=total_pasivo,
        patrimonio_grupos=patrimonio_grupos,
        total_patrimonio=total_patrimonio,
        total_pasivo_patrimonio=total_pasivo_patrimonio,
        diferencia=diferencia,
        cuadra=cuadra,
        completo=not faltantes,
        categorias_faltantes=faltantes,
        cuentas_sin_dato=cuentas_sin_dato(list_accounts(session, solo_activas=True), entries, OBLIGATORIAS_BALANCE),
        advertencias_signo=[a for a in (aviso_signo(c, v) for c, v in entries) if a],
    )
