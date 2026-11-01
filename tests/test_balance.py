"""Casos 5-8 de la sección 16: cálculo de activos, pasivos, patrimonio y
validación de la ecuación contable, con datos sintéticos."""
from decimal import Decimal

from calculations.balance_sheet import compute_balance_sheet
from database.enums import TipoEstadoFinanciero as Tipo
from database.repositories import get_account_by_codigo, get_or_create_fiscal_period, upsert_entry


def _capturar_balance_cuadrado(session):
    periodo, _ = get_or_create_fiscal_period(session, 2021)
    session.commit()

    def be(codigo, valor):
        cuenta = get_account_by_codigo(session, codigo)
        upsert_entry(session, fiscal_period_id=periodo.id, account_id=cuenta.id, valor=Decimal(valor), tipo=Tipo.BALANCE)

    be("1001", "300.00")  # activo corriente
    be("1002", "200.00")  # activo corriente
    be("1101", "500.00")  # activo no corriente
    be("2001", "250.00")  # pasivo corriente
    be("2101", "150.00")  # pasivo no corriente
    be("3001", "500.00")  # capital social
    be("3004", "100.00")  # resultado del ejercicio
    session.commit()
    return periodo


def test_calculo_de_activos(db_session):
    periodo = _capturar_balance_cuadrado(db_session)
    bs = compute_balance_sheet(db_session, periodo.id)
    assert bs.activo_corriente.subtotal == Decimal("500.00")
    assert bs.activo_no_corriente.subtotal == Decimal("500.00")
    assert bs.total_activo == Decimal("1000.00")


def test_calculo_de_pasivos(db_session):
    periodo = _capturar_balance_cuadrado(db_session)
    bs = compute_balance_sheet(db_session, periodo.id)
    assert bs.pasivo_corriente.subtotal == Decimal("250.00")
    assert bs.pasivo_no_corriente.subtotal == Decimal("150.00")
    assert bs.total_pasivo == Decimal("400.00")


def test_calculo_del_patrimonio(db_session):
    periodo = _capturar_balance_cuadrado(db_session)
    bs = compute_balance_sheet(db_session, periodo.id)
    assert bs.total_patrimonio == Decimal("600.00")


def test_ecuacion_contable_cuadra(db_session):
    periodo = _capturar_balance_cuadrado(db_session)
    bs = compute_balance_sheet(db_session, periodo.id)
    assert bs.cuadra is True
    assert bs.diferencia == Decimal("0.00")


def test_ecuacion_contable_detecta_diferencia(db_session):
    periodo, _ = get_or_create_fiscal_period(db_session, 2021)
    db_session.commit()
    cuenta = get_account_by_codigo(db_session, "1001")
    upsert_entry(db_session, fiscal_period_id=periodo.id, account_id=cuenta.id, valor=Decimal("1000.00"), tipo=Tipo.BALANCE)
    db_session.commit()

    bs = compute_balance_sheet(db_session, periodo.id)
    assert bs.cuadra is False
    assert bs.diferencia == Decimal("1000.00")


def test_balance_sin_datos_no_inventa_totales(db_session):
    periodo, _ = get_or_create_fiscal_period(db_session, 2021)
    db_session.commit()
    bs = compute_balance_sheet(db_session, periodo.id)
    assert bs.tiene_datos is False
