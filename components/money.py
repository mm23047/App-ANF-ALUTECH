"""Utilidades de formato monetario/porcentual. Unico lugar que convierte
Decimal a texto para presentacion (seccion 15: dos decimales en
porcentajes, "veces" en rotacion/multiplicador, moneda configurada)."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

CERO = Decimal("0.00")
DOS_DECIMALES = Decimal("0.01")


def q2(valor: Decimal) -> Decimal:
    return valor.quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)


def format_money(valor: Decimal | None, moneda: str = "") -> str:
    if valor is None:
        return "No disponible"
    valor = q2(valor)
    texto = f"{valor:,.2f}"
    return f"{moneda} {texto}".strip()


def format_percent(valor: Decimal | None) -> str:
    if valor is None:
        return "No disponible"
    return f"{q2(valor):.2f}%"


def format_ratio(valor: Decimal | None) -> str:
    if valor is None:
        return "No disponible"
    return f"{q2(valor):.2f} veces"
