"""Hallazgo M-11: las paginas de analisis vertical fallaban con importes
distintos de cero ('float' object has no attribute 'quantize').

Cubre el calculo (Decimal, base cero, negativos, ceros, HALF_UP), la tabla
de pantalla formateada desde Decimal y la pagina real (ver
test_fase1_paginas.py, que la renderiza con AppTest en un subproceso).
"""
import sqlite3
from decimal import Decimal

import pytest

from calculations.vertical_analysis import _porcentaje, compute_vertical_balance, compute_vertical_income
from database import connection
from database.connection import init_db, session_scope
from database.enums import TipoEstadoFinanciero as Tipo
from database.repositories import get_account_by_codigo, get_or_create_fiscal_period, upsert_entry
from database.seed import seed_default_accounts
from reports.vertical_report import _tabla_presentacion

BALANCE = {  # AC 1000, ANC 200 -> activo 1200 = pasivo 1300 + patrimonio -100
    "1001": "1000.00", "1002": "0.00", "1101": "500.00", "1102": "-300.00", "2001": "1300.00", "3003": "-100.00",
}
RESULTADOS = {  # base: ingresos 2000; ISR negativo (beneficio fiscal)
    "4001": "2000.00", "5001": "1200.00", "6001": "300.00", "6003": "50.00", "7002": "0.00", "8001": "-25.00",
}


@pytest.fixture()
def bd(tmp_path):
    ruta = tmp_path / "m11.db"
    init_db(db_path=ruta)
    with session_scope() as s:
        seed_default_accounts(s)
        p, _ = get_or_create_fiscal_period(s, 2023)
        for datos, tipo in ((BALANCE, Tipo.BALANCE), (RESULTADOS, Tipo.RESULTADOS)):
            for codigo, valor in datos.items():
                upsert_entry(s, fiscal_period_id=p.id, account_id=get_account_by_codigo(s, codigo).id, valor=valor, tipo=tipo)
        vacio, _ = get_or_create_fiscal_period(s, 2024)
        periodos = (p.id, vacio.id)
    yield ruta, periodos
    connection.dispose_engine()


def _por_codigo(resultado):
    return {f.cuenta.codigo: (f.valor, f.porcentaje) for f in resultado.filas}


def test_vertical_balance_con_positivos_negativos_y_ceros(bd):
    _, (p, _) = bd
    with session_scope() as s:
        r = compute_vertical_balance(s, p)
    assert r.disponible and r.base_total_activo == Decimal("1200.00")
    assert _por_codigo(r) == {
        "1001": (Decimal("1000.00"), Decimal("83.33")),
        "1002": (Decimal("0.00"), Decimal("0.00")),
        "1101": (Decimal("500.00"), Decimal("41.67")),
        "1102": (Decimal("-300.00"), Decimal("-25.00")),
        "2001": (Decimal("1300.00"), Decimal("108.33")),
        "3003": (Decimal("-100.00"), Decimal("-8.33")),
    }
    assert all(isinstance(v, Decimal) and isinstance(pct, Decimal) for v, pct in _por_codigo(r).values())


def test_vertical_resultados_con_positivos_negativos_y_ceros(bd):
    _, (p, _) = bd
    with session_scope() as s:
        r = compute_vertical_income(s, p)
    assert r.disponible and r.base_ingresos_netos == Decimal("2000.00")
    assert _por_codigo(r) == {
        "4001": (Decimal("2000.00"), Decimal("100.00")),  # desde M-03 (fase 3) se incluye la base
        "5001": (Decimal("1200.00"), Decimal("60.00")),
        "6001": (Decimal("300.00"), Decimal("15.00")),
        "6003": (Decimal("50.00"), Decimal("2.50")),
        "7002": (Decimal("0.00"), Decimal("0.00")),
        "8001": (Decimal("-25.00"), Decimal("-1.25")),
    }


def test_ejercicio_sin_datos_no_disponible(bd):
    _, (_, vacio) = bd
    with session_scope() as s:
        balance, resultados = compute_vertical_balance(s, vacio), compute_vertical_income(s, vacio)
    assert not balance.disponible and balance.filas == []
    assert not resultados.disponible and resultados.filas == []


def test_porcentaje_con_base_cero_es_none_y_redondeo_half_up():
    assert _porcentaje(Decimal("100.00"), Decimal("0.00")) is None
    assert _porcentaje(Decimal("1"), Decimal("800")) == Decimal("0.13")   # 0.125 -> 0.13 (no bancario)
    assert _porcentaje(Decimal("-1"), Decimal("800")) == Decimal("-0.13")


def test_tabla_de_pantalla_se_formatea_desde_decimal(bd):
    _, (p, _) = bd
    with session_scope() as s:
        balance = _tabla_presentacion(compute_vertical_balance(s, p).lineas, "USD")
        resultados = _tabla_presentacion(compute_vertical_income(s, p).lineas, "USD")
    filas = {f["Código"]: (f["Valor"], f["Participación %"]) for f in balance.to_dict("records") if f["Código"]}
    assert filas["1001"] == ("USD 1,000.00", "83.33%")
    assert filas["1002"] == ("USD 0.00", "0.00%")
    assert filas["1102"] == ("USD -300.00", "-25.00%")
    assert filas["2001"] == ("USD 1,300.00", "108.33%")
    filas = {f["Código"]: (f["Valor"], f["Participación %"]) for f in resultados.to_dict("records") if f["Código"]}
    assert filas["8001"] == ("USD -25.00", "-1.25%")


def test_tabla_de_pantalla_con_porcentaje_none_y_sin_filas():
    from calculations.vertical_analysis import LineaVertical

    tabla = _tabla_presentacion([LineaVertical("cuenta", "Efectivo", Decimal("123456789012345.67"), None, "1001")], "USD")
    assert tabla.to_dict("records") == [
        {"Código": "1001", "Concepto": "Efectivo", "Valor": "USD 123,456,789,012,345.67",
         "Participación %": "No disponible", "Efecto": ""}
    ]
    assert list(_tabla_presentacion([], "USD").columns) == ["Código", "Concepto", "Valor", "Participación %", "Efecto"]


def test_calcular_y_presentar_no_altera_los_centavos_almacenados(bd):
    ruta, (p, _) = bd
    connection.dispose_engine()

    def centavos():
        con = sqlite3.connect(ruta)
        try:
            return con.execute(
                "SELECT 'B', id, valor, typeof(valor) FROM balance_entry UNION ALL "
                "SELECT 'R', id, valor, typeof(valor) FROM income_entry ORDER BY 1, 2"
            ).fetchall()
        finally:
            con.close()

    antes = centavos()
    assert ("B", 4, -30000, "integer") in antes  # 1102 = -300.00
    init_db(db_path=ruta)
    with session_scope() as s:
        _tabla_presentacion(compute_vertical_balance(s, p).lineas, "USD")
        _tabla_presentacion(compute_vertical_income(s, p).lineas, "USD")
    connection.dispose_engine()
    assert centavos() == antes
