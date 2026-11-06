"""Fase 1.2: validacion unica de importes y años (A-07, M-01, M-02, B-08)."""
from decimal import Decimal

import numpy as np
import pandas as pd
import pytest

from components.money import (
    IMPORTE_MAXIMO,
    AnioFueraDeRango,
    AnioInvalido,
    ImporteInvalido,
    ImporteNoNumerico,
    ImporteVacio,
    es_ruido_float,
    parse_anio,
    parse_importe,
    parse_importe_con_aviso,
)


@pytest.mark.parametrize("entrada, esperado", [
    ("1234.56", Decimal("1234.56")),
    ("  -98765.4 ", Decimal("-98765.40")),
    (100, Decimal("100.00")),
    (Decimal("0.1"), Decimal("0.10")),
    (0.0, Decimal("0.00")),
    ("-0", Decimal("0.00")),
    (1234567890123.45, Decimal("1234567890123.45")),
    (np.int64(7), Decimal("7.00")),
    (np.float64(12.5), Decimal("12.50")),
    (str(IMPORTE_MAXIMO), IMPORTE_MAXIMO),
])
def test_importes_validos_con_dos_decimales(entrada, esperado):
    resultado = parse_importe(entrada)
    assert resultado == esperado
    assert resultado.as_tuple().exponent == -2
    assert str(resultado) == str(esperado)


def test_cero_negativo_se_normaliza():
    assert str(parse_importe("-0.00")) == "0.00"


@pytest.mark.parametrize("vacio", [None, "", "   ", float("nan"), Decimal("NaN"), np.nan, pd.NA, pd.NaT])
def test_vacio_no_es_cero(vacio):
    with pytest.raises(ImporteVacio):
        parse_importe(vacio)


@pytest.mark.parametrize("infinito", [float("inf"), float("-inf"), Decimal("Infinity"), "-Infinity"])
def test_infinitos_rechazados(infinito):
    with pytest.raises(ImporteInvalido):
        parse_importe(infinito)


@pytest.mark.parametrize("texto", ["abc", "1,234.56", "12,5", "(600)", True])
def test_no_numericos_rechazados(texto):
    with pytest.raises(ImporteNoNumerico):
        parse_importe(texto)


def test_mas_de_dos_decimales_rechazado_por_defecto():
    with pytest.raises(ImporteInvalido, match="más de dos decimales"):
        parse_importe("1.234")
    with pytest.raises(ImporteInvalido):
        parse_importe(Decimal("2.675"))


def test_redondeo_explicito_half_up_con_aviso():
    # 2.675 como float es 2.67499999... en binario: round() daba 2.67 (B-08).
    importe, aviso = parse_importe_con_aviso(2.675, redondear=True)
    assert importe == Decimal("2.68") and "2.68" in aviso
    importe, aviso = parse_importe_con_aviso(-2.675, redondear=True)
    assert importe == Decimal("-2.68")
    importe, aviso = parse_importe_con_aviso(0.1 + 0.2, redondear=True)
    assert importe == Decimal("0.30") and aviso is not None
    importe, aviso = parse_importe_con_aviso("5.00", redondear=True)
    assert importe == Decimal("5.00") and aviso is None


def test_fuera_de_rango_numeric_18_2():
    with pytest.raises(ImporteInvalido, match="máximo"):
        parse_importe(IMPORTE_MAXIMO + Decimal("0.01"))
    with pytest.raises(ImporteInvalido):
        parse_importe(-(IMPORTE_MAXIMO + Decimal("0.01")))


def test_float_con_demasiados_digitos_rechazado():
    # 16 digitos en centavos: un float ya no garantiza conservarlos.
    with pytest.raises(ImporteInvalido, match="dígitos significativos"):
        parse_importe(12345678901234.56)
    # Como texto si se acepta y es exacto.
    assert parse_importe("123456789012345.67") == Decimal("123456789012345.67")


def test_ruido_float_frente_a_tercer_decimal_real():
    assert es_ruido_float(0.1 + 0.2)
    assert es_ruido_float(1234.5600000000002)
    assert not es_ruido_float(2.675)
    assert not es_ruido_float("1.234")


@pytest.mark.parametrize("entrada, esperado", [(2021, 2021), (2021.0, 2021), ("2021", 2021), (" 1990 ", 1990), (2100, 2100), (np.int64(2022), 2022)])
def test_anios_validos(entrada, esperado):
    assert parse_anio(entrada) == esperado


@pytest.mark.parametrize("entrada", [2021.9, "2021.5", "abc", None, "", float("nan"), True])
def test_anios_invalidos(entrada):
    with pytest.raises(AnioInvalido):
        parse_anio(entrada)


@pytest.mark.parametrize("entrada", [21, 1989, 2101, -2021])
def test_anios_fuera_de_rango(entrada):
    with pytest.raises(AnioFueraDeRango):
        parse_anio(entrada)
