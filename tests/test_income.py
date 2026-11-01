"""Caso 9 de la sección 16: cálculo de utilidad neta y subtotales
intermedios del Estado de Resultados, incluida la resolución de
ambigüedad de 'otros ingresos/gastos operativos' (ver plan)."""
from decimal import Decimal

from calculations.income_statement import compute_income_statement
from database.enums import TipoEstadoFinanciero as Tipo
from database.repositories import get_account_by_codigo, get_or_create_fiscal_period, upsert_entry


def _ie(session, periodo_id, codigo, valor):
    cuenta = get_account_by_codigo(session, codigo)
    upsert_entry(session, fiscal_period_id=periodo_id, account_id=cuenta.id, valor=Decimal(valor), tipo=Tipo.RESULTADOS)


def test_calculo_de_utilidad_neta(db_session):
    periodo, _ = get_or_create_fiscal_period(db_session, 2021)
    db_session.commit()

    _ie(db_session, periodo.id, "4001", "1000.00")  # ingresos netos
    _ie(db_session, periodo.id, "5001", "600.00")   # costo de ventas
    _ie(db_session, periodo.id, "6001", "150.00")   # gastos admin
    _ie(db_session, periodo.id, "6002", "50.00")    # gastos ventas
    _ie(db_session, periodo.id, "7002", "50.00")    # gastos financieros
    _ie(db_session, periodo.id, "8001", "50.00")    # ISR
    db_session.commit()

    inc = compute_income_statement(db_session, periodo.id)
    assert inc.utilidad_bruta == Decimal("400.00")
    assert inc.utilidad_operativa == Decimal("200.00")
    assert inc.utilidad_antes_impuestos == Decimal("150.00")
    assert inc.utilidad_neta == Decimal("100.00")


def test_otros_operativos_ingreso_suma_y_gasto_resta(db_session):
    periodo, _ = get_or_create_fiscal_period(db_session, 2021)
    db_session.commit()

    _ie(db_session, periodo.id, "4001", "1000.00")
    _ie(db_session, periodo.id, "5001", "400.00")   # utilidad bruta 600
    _ie(db_session, periodo.id, "6003", "30.00")    # otros ingresos operativos (suma)
    _ie(db_session, periodo.id, "6004", "10.00")    # otros gastos operativos (resta)
    db_session.commit()

    inc = compute_income_statement(db_session, periodo.id)
    # utilidad operativa = 600 - 0 (admin) - 0 (ventas) + 30 - 10 = 620
    assert inc.utilidad_operativa == Decimal("620.00")


def test_income_sin_datos_no_inventa_totales(db_session):
    periodo, _ = get_or_create_fiscal_period(db_session, 2021)
    db_session.commit()
    inc = compute_income_statement(db_session, periodo.id)
    assert inc.tiene_datos is False
