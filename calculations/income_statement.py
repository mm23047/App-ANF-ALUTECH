"""Calculo del Estado de Resultados (seccion 9.2).

Reglas fijas de signo por categoria/subcategoria (no se infieren de la
naturaleza del saldo, para evitar bugs de doble signo -- ver resolucion
de ambiguedad en el plan):

  Utilidad bruta      = Ingresos netos - Costo de ventas
  Utilidad operativa  = Utilidad bruta - Gastos admin - Gastos ventas
                         + Otros ingresos operativos - Otros gastos operativos
  Utilidad antes imp. = Utilidad operativa + Ingresos financieros - Gastos financieros
                         + Otros ingresos no operativos - Otros gastos no operativos
  Utilidad neta       = Utilidad antes de impuestos - Impuesto sobre la renta

`completo` indica si Ingresos, Costo de ventas, Gastos operativos e ISR
tienen al menos una cuenta capturada (un 0 explicito cuenta); los demas
grupos son opcionales. Ver calculations/validation.py (M-04, A-05).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy.orm import Session

from calculations.validation import (
    OBLIGATORIAS_RESULTADOS,
    aviso_signo,
    categorias_faltantes,
    cuentas_sin_dato,
)
from components.money import q2
from database.enums import RESULTADOS_CATEGORIAS
from database.enums import CategoriaPrincipal as Cat
from database.enums import EfectoCuenta as Efecto
from database.enums import Subcategoria as Sub
from database.enums import TipoEstadoFinanciero
from database.models import Account
from database.repositories import list_accounts, list_entries

CERO = Decimal("0.00")


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
class IncomeStatementResult:
    tiene_datos: bool
    ingresos_netos: Grupo
    costo_ventas: Grupo
    utilidad_bruta: Decimal
    gastos_administracion: Grupo
    gastos_ventas: Grupo
    otros_ingresos_operativos: Grupo
    otros_gastos_operativos: Grupo
    utilidad_operativa: Decimal
    ingresos_financieros: Grupo
    gastos_financieros: Grupo
    resultado_financiero: Decimal
    otros_ingresos_no_operativos: Grupo
    otros_gastos_no_operativos: Grupo
    otros_resultados: Decimal
    utilidad_antes_impuestos: Decimal
    impuesto_renta: Grupo
    utilidad_neta: Decimal
    completo: bool = False
    categorias_faltantes: list[str] = field(default_factory=list)
    cuentas_sin_dato: list[Account] = field(default_factory=list)
    advertencias_signo: list[str] = field(default_factory=list)


def _grupo(nombre: str, lineas: list[Linea]) -> Grupo:
    subtotal = q2(sum((l.valor for l in lineas), CERO))
    return Grupo(nombre=nombre, lineas=lineas, subtotal=subtotal)


def compute_income_statement(session: Session, fiscal_period_id: int) -> IncomeStatementResult:
    entries = list_entries(session, fiscal_period_id, TipoEstadoFinanciero.RESULTADOS)

    def filtro(categoria: Cat, subcategoria: Sub | None = None, efecto: Efecto | None = None) -> list[Linea]:
        return [
            Linea(a, v)
            for a, v in entries
            if a.categoria_principal == categoria
            and (subcategoria is None or a.subcategoria == subcategoria)
            and (efecto is None or a.efecto == efecto)
        ]

    ingresos_netos = _grupo("Ingresos netos", filtro(Cat.INGRESOS))
    costo_ventas = _grupo("Costo de ventas", filtro(Cat.COSTOS))
    utilidad_bruta = q2(ingresos_netos.subtotal - costo_ventas.subtotal)

    gastos_administracion = _grupo(
        "Gastos de administracion", filtro(Cat.GASTOS_OPERATIVOS, Sub.ADMINISTRACION)
    )
    gastos_ventas = _grupo("Gastos de ventas", filtro(Cat.GASTOS_OPERATIVOS, Sub.VENTAS))
    otros_ingresos_operativos = _grupo(
        "Otros ingresos operativos",
        filtro(Cat.GASTOS_OPERATIVOS, Sub.OTROS_OPERATIVOS, Efecto.INGRESO),
    )
    otros_gastos_operativos = _grupo(
        "Otros gastos operativos",
        filtro(Cat.GASTOS_OPERATIVOS, Sub.OTROS_OPERATIVOS, Efecto.GASTO),
    )
    utilidad_operativa = q2(
        utilidad_bruta
        - gastos_administracion.subtotal
        - gastos_ventas.subtotal
        + otros_ingresos_operativos.subtotal
        - otros_gastos_operativos.subtotal
    )

    ingresos_financieros = _grupo("Ingresos financieros", filtro(Cat.INGRESOS_FINANCIEROS))
    gastos_financieros = _grupo("Gastos financieros", filtro(Cat.GASTOS_FINANCIEROS))
    resultado_financiero = q2(ingresos_financieros.subtotal - gastos_financieros.subtotal)

    otros_ingresos_no_operativos = _grupo(
        "Otros ingresos no operativos", filtro(Cat.OTROS_INGRESOS_GASTOS, efecto=Efecto.INGRESO)
    )
    otros_gastos_no_operativos = _grupo(
        "Otros gastos no operativos", filtro(Cat.OTROS_INGRESOS_GASTOS, efecto=Efecto.GASTO)
    )
    otros_resultados = q2(otros_ingresos_no_operativos.subtotal - otros_gastos_no_operativos.subtotal)

    utilidad_antes_impuestos = q2(utilidad_operativa + resultado_financiero + otros_resultados)

    impuesto_renta = _grupo("Impuesto sobre la renta", filtro(Cat.IMPUESTOS))
    utilidad_neta = q2(utilidad_antes_impuestos - impuesto_renta.subtotal)
    faltantes = categorias_faltantes(entries, OBLIGATORIAS_RESULTADOS)

    return IncomeStatementResult(
        tiene_datos=len(entries) > 0,
        ingresos_netos=ingresos_netos,
        costo_ventas=costo_ventas,
        utilidad_bruta=utilidad_bruta,
        gastos_administracion=gastos_administracion,
        gastos_ventas=gastos_ventas,
        otros_ingresos_operativos=otros_ingresos_operativos,
        otros_gastos_operativos=otros_gastos_operativos,
        utilidad_operativa=utilidad_operativa,
        ingresos_financieros=ingresos_financieros,
        gastos_financieros=gastos_financieros,
        resultado_financiero=resultado_financiero,
        otros_ingresos_no_operativos=otros_ingresos_no_operativos,
        otros_gastos_no_operativos=otros_gastos_no_operativos,
        otros_resultados=otros_resultados,
        utilidad_antes_impuestos=utilidad_antes_impuestos,
        impuesto_renta=impuesto_renta,
        utilidad_neta=utilidad_neta,
        completo=not faltantes,
        categorias_faltantes=faltantes,
        cuentas_sin_dato=cuentas_sin_dato(list_accounts(session, solo_activas=True), entries, RESULTADOS_CATEGORIAS),
        advertencias_signo=[a for a in (aviso_signo(c, v) for c, v in entries) if a],
    )
