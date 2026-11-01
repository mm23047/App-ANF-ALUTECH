"""Utilidades de formato monetario/porcentual. Unico lugar que convierte
Decimal a texto para presentacion (seccion 15: dos decimales en
porcentajes, "veces" en rotacion/multiplicador, moneda configurada).

Tambien contiene la validacion unica de entradas (parse_importe y
parse_anio) que usan la captura manual, la edicion y la importacion
Excel (hallazgos A-07, M-01, M-02 y B-08 de AUDITORIA_INTEGRAL.md).
"""
from __future__ import annotations

import math
import operator
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

import pandas as pd

CERO = Decimal("0.00")
DOS_DECIMALES = Decimal("0.01")

# Rango de NUMERIC(18,2): 16 digitos enteros y 2 decimales.
IMPORTE_MAXIMO = Decimal("9999999999999999.99")
# Un float (widget de Streamlit, celda numerica de Excel) solo conserva con
# seguridad 15 digitos significativos; por encima se pierden centavos.
DIGITOS_FLOAT_SEGUROS = 15
# Diferencia por debajo de la cual un exceso de decimales se considera ruido
# de coma flotante (p. ej. 0.1 + 0.2 = 0.30000000000000004).
RUIDO_FLOAT = Decimal("0.000001")

ANIO_MINIMO = 1990
ANIO_MAXIMO = 2100


class ImporteInvalido(ValueError):
    """El valor no es un importe monetario aceptable. El mensaje es apto
    para mostrarse al usuario."""


class ImporteVacio(ImporteInvalido):
    """No se informo ningun importe (celda o campo vacio). Un dato faltante
    no es un cero."""


class ImporteNoNumerico(ImporteInvalido):
    """El valor no se puede interpretar como numero."""


class AnioInvalido(ValueError):
    """El valor no es un ejercicio fiscal aceptable."""


class AnioFueraDeRango(AnioInvalido):
    """Año entero, pero fuera de ANIO_MINIMO..ANIO_MAXIMO."""


def q2(valor: Decimal) -> Decimal:
    return valor.quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)


def es_vacio(valor) -> bool:
    if valor is None:
        return True
    if isinstance(valor, str):
        return valor.strip() == ""
    if isinstance(valor, float) and math.isnan(valor):
        return True
    if isinstance(valor, Decimal) and valor.is_nan():
        return True
    # pandas.NA, pandas.NaT y numpy.nan (celdas vacias leidas con pandas).
    return pd.api.types.is_scalar(valor) and bool(pd.isna(valor))


def _a_decimal(valor) -> Decimal:
    """Convierte sin pasar por redondeo binario. Un float se convierte por
    su representacion mas corta (repr), que es la que vio el usuario."""
    if isinstance(valor, bool):
        raise ImporteNoNumerico(f"'{valor}' no es un importe numérico.")
    if isinstance(valor, Decimal):
        return valor
    if isinstance(valor, int):
        return Decimal(valor)
    if isinstance(valor, float):
        if math.isinf(valor):
            raise ImporteInvalido("El importe no puede ser infinito.")
        # float.__repr__ y no repr(): en numpy 2, repr(np.float64(1.5)) es
        # "np.float64(1.5)".
        decimal = Decimal(float.__repr__(valor))
        # La precision que importa es la de los centavos: 0.30000000000000004
        # tiene 17 digitos, pero en centavos (0.30) solo 2.
        if len(q2(decimal).as_tuple().digits) > DIGITOS_FLOAT_SEGUROS:
            raise ImporteInvalido(
                f"El importe {valor!r} tiene más de {DIGITOS_FLOAT_SEGUROS} dígitos significativos y no "
                "puede leerse sin perder precisión. Escríbalo como texto (p. ej. '123456789012345.67')."
            )
        return decimal
    if isinstance(valor, str):
        texto = valor.strip()
        if "," in texto:
            raise ImporteNoNumerico(
                f"'{valor}' contiene comas. Use punto decimal y sin separador de miles (p. ej. 1234567.89)."
            )
        try:
            return Decimal(texto)
        except InvalidOperation:
            raise ImporteNoNumerico(f"'{valor}' no es un importe numérico.") from None
    # numpy.int64 y similares (numpy.float64 ya es subclase de float).
    try:
        return Decimal(operator.index(valor))
    except TypeError:
        raise ImporteNoNumerico(f"'{valor}' no es un importe numérico.") from None


def parse_importe_con_aviso(valor, *, redondear: bool = False) -> tuple[Decimal, str | None]:
    """Valida un importe y lo devuelve con exactamente dos decimales.

    - Rechaza vacio/None/NaN (ImporteVacio), infinitos, texto no numerico y
      valores fuera de NUMERIC(18,2).
    - Mas de dos decimales: si redondear=False se rechaza; si redondear=True
      se cuantiza con ROUND_HALF_UP y se devuelve un aviso (nunca en silencio).

    Devuelve (importe, aviso). aviso es None si no hubo redondeo.
    """
    if es_vacio(valor):
        raise ImporteVacio("El importe está vacío. Un campo vacío significa 'sin dato', no cero.")
    decimal = _a_decimal(valor)
    if not decimal.is_finite():
        raise ImporteInvalido("El importe no puede ser NaN ni infinito.")

    aviso = None
    cuantizado = q2(decimal)
    if cuantizado != decimal:
        if not redondear:
            raise ImporteInvalido(
                f"El importe {decimal} tiene más de dos decimales. Redondéelo a centavos antes de capturarlo."
            )
        aviso = f"El importe {decimal} se redondeó a {cuantizado} (dos decimales, redondeo comercial)."
    if cuantizado.is_zero():
        cuantizado = abs(cuantizado)  # -0.00 -> 0.00
    if abs(cuantizado) > IMPORTE_MAXIMO:
        raise ImporteInvalido(f"El importe {cuantizado} excede el máximo permitido (±{IMPORTE_MAXIMO}).")
    return cuantizado, aviso


def parse_importe(valor, *, redondear: bool = False) -> Decimal:
    """Igual que parse_importe_con_aviso, sin devolver el aviso. Solo debe
    usarse con redondear=True cuando el llamador no necesita informar el
    redondeo (por defecto, un exceso de decimales se rechaza)."""
    return parse_importe_con_aviso(valor, redondear=redondear)[0]


def es_ruido_float(valor) -> bool:
    """True si el exceso de decimales de `valor` es solo ruido binario
    (0.30000000000000004), no un tercer decimal real (2.675)."""
    try:
        decimal = _a_decimal(valor)
    except ImporteInvalido:
        return False
    return decimal.is_finite() and abs(decimal - q2(decimal)) < RUIDO_FLOAT


def parse_anio(valor) -> int:
    """Valida un ejercicio fiscal: entero exacto entre ANIO_MINIMO y
    ANIO_MAXIMO. Rechaza 2021.9 (no se trunca) y 21 (fuera de rango)."""
    if es_vacio(valor):
        raise AnioInvalido("El período está vacío.")
    try:
        decimal = _a_decimal(valor)
    except ImporteInvalido:
        raise AnioInvalido(f"'{valor}' no es un año válido.") from None
    if not decimal.is_finite() or decimal != decimal.to_integral_value():
        raise AnioInvalido(f"El período '{valor}' no es un año entero.")
    anio = int(decimal)
    if not ANIO_MINIMO <= anio <= ANIO_MAXIMO:
        raise AnioFueraDeRango(f"El período {anio} está fuera del rango permitido ({ANIO_MINIMO}–{ANIO_MAXIMO}).")
    return anio


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
