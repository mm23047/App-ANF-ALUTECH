"""Casos 10-11 de la sección 16: análisis vertical del balance y del
estado de resultados."""
from decimal import Decimal

from calculations.vertical_analysis import compute_vertical_balance, compute_vertical_income
from database.enums import TipoEstadoFinanciero as Tipo
from database.repositories import get_account_by_codigo, get_or_create_fiscal_period, upsert_entry


def test_analisis_vertical_del_balance(db_session):
    periodo, _ = get_or_create_fiscal_period(db_session, 2021)
    db_session.commit()

    def be(codigo, valor):
        cuenta = get_account_by_codigo(db_session, codigo)
        upsert_entry(db_session, fiscal_period_id=periodo.id, account_id=cuenta.id, valor=Decimal(valor), tipo=Tipo.BALANCE)

    be("1001", "300.00")
    be("1101", "700.00")
    db_session.commit()

    resultado = compute_vertical_balance(db_session, periodo.id)
    assert resultado.disponible is True
    assert resultado.base_total_activo == Decimal("1000.00")
    fila_1001 = next(f for f in resultado.filas if f.cuenta.codigo == "1001")
    assert fila_1001.porcentaje == Decimal("30.00")
    fila_1101 = next(f for f in resultado.filas if f.cuenta.codigo == "1101")
    assert fila_1101.porcentaje == Decimal("70.00")


def test_analisis_vertical_sin_datos_no_disponible(db_session):
    periodo, _ = get_or_create_fiscal_period(db_session, 2021)
    db_session.commit()
    resultado = compute_vertical_balance(db_session, periodo.id)
    assert resultado.disponible is False


def test_analisis_vertical_del_estado_de_resultados(db_session):
    periodo, _ = get_or_create_fiscal_period(db_session, 2021)
    db_session.commit()

    def ie(codigo, valor):
        cuenta = get_account_by_codigo(db_session, codigo)
        upsert_entry(db_session, fiscal_period_id=periodo.id, account_id=cuenta.id, valor=Decimal(valor), tipo=Tipo.RESULTADOS)

    ie("4001", "1000.00")  # ingresos netos (base)
    ie("5001", "250.00")   # costo de ventas -> 25%
    db_session.commit()

    resultado = compute_vertical_income(db_session, periodo.id)
    assert resultado.disponible is True
    assert resultado.base_ingresos_netos == Decimal("1000.00")
    fila_costo = next(f for f in resultado.filas if f.cuenta.codigo == "5001")
    assert fila_costo.porcentaje == Decimal("25.00")


def test_analisis_vertical_resultados_ingresos_cero_no_disponible(db_session):
    periodo, _ = get_or_create_fiscal_period(db_session, 2021)
    db_session.commit()

    cuenta = get_account_by_codigo(db_session, "5001")
    upsert_entry(db_session, fiscal_period_id=periodo.id, account_id=cuenta.id, valor=Decimal("100.00"), tipo=Tipo.RESULTADOS)
    db_session.commit()

    resultado = compute_vertical_income(db_session, periodo.id)
    assert resultado.disponible is False
