"""Casos 12-16 de la sección 16: margen neto, rotación de activos,
multiplicador del capital, ROE DuPont y su coincidencia con el ROE
directo."""
from decimal import Decimal

from calculations.dupont import compute_dupont
from database.enums import TipoEstadoFinanciero as Tipo
from database.repositories import get_account_by_codigo, get_or_create_fiscal_period, upsert_entry


def _capturar_ejercicio(session, anio, activo_total, patrimonio, ingresos, utilidad_neta):
    periodo, _ = get_or_create_fiscal_period(session, anio)
    session.commit()

    def be(codigo, valor):
        cuenta = get_account_by_codigo(session, codigo)
        upsert_entry(session, fiscal_period_id=periodo.id, account_id=cuenta.id, valor=Decimal(valor), tipo=Tipo.BALANCE)

    def ie(codigo, valor):
        cuenta = get_account_by_codigo(session, codigo)
        upsert_entry(session, fiscal_period_id=periodo.id, account_id=cuenta.id, valor=Decimal(valor), tipo=Tipo.RESULTADOS)

    pasivo = activo_total - patrimonio
    be("1001", str(activo_total))
    be("2001", str(pasivo))
    be("3001", str(patrimonio))

    ie("4001", str(ingresos))
    ie("8001", str(ingresos - utilidad_neta))  # todo el gasto como ISR para simplificar
    session.commit()
    return periodo


def test_margen_neto_rotacion_y_multiplicador(db_session):
    periodo = _capturar_ejercicio(db_session, 2021, activo_total=1000, patrimonio=600, ingresos=1000, utilidad_neta=100)
    resultado = compute_dupont(db_session, periodo)

    assert resultado.disponible is True
    # Primer ejercicio sin saldo inicial -> se aproxima con el saldo final (activo=patrimonio promedio = final)
    assert resultado.margen_neto == Decimal("0.10")  # 10%
    assert resultado.rotacion_activos == Decimal("1.00")  # 1000 ingresos / 1000 activo promedio
    assert resultado.multiplicador_capital == Decimal("1.67")  # 1000 / 600 ~= 1.67


def test_roe_dupont_y_coincidencia_con_roe_directo(db_session):
    periodo = _capturar_ejercicio(db_session, 2021, activo_total=1000, patrimonio=600, ingresos=1000, utilidad_neta=100)
    resultado = compute_dupont(db_session, periodo)

    roe_esperado = (Decimal("100") / Decimal("600") * 100).quantize(Decimal("0.01"))
    assert resultado.roe_directo_pct == roe_esperado
    assert abs(resultado.roe_dupont_pct - resultado.roe_directo_pct) <= Decimal("0.01")
    assert resultado.coincide_redondeo is True


def test_saldos_iniciales_se_encadenan_entre_ejercicios(db_session):
    _capturar_ejercicio(db_session, 2021, activo_total=1000, patrimonio=600, ingresos=1000, utilidad_neta=100)
    periodo_2022 = _capturar_ejercicio(db_session, 2022, activo_total=1200, patrimonio=700, ingresos=1200, utilidad_neta=150)

    resultado = compute_dupont(db_session, periodo_2022)
    assert resultado.saldos_aproximados is False
    assert resultado.activo_inicial == Decimal("1000.00")
    assert resultado.activo_promedio == Decimal("1100.00")  # (1000+1200)/2
    assert resultado.patrimonio_inicial == Decimal("600.00")
    assert resultado.patrimonio_promedio == Decimal("650.00")  # (600+700)/2


def test_sin_saldo_inicial_se_aproxima_con_saldo_final(db_session):
    periodo = _capturar_ejercicio(db_session, 2021, activo_total=1000, patrimonio=600, ingresos=1000, utilidad_neta=100)
    resultado = compute_dupont(db_session, periodo)
    assert resultado.saldos_aproximados is True
    assert resultado.activo_inicial == resultado.activo_final


def test_dupont_no_calcula_con_patrimonio_promedio_cero(db_session):
    periodo, _ = get_or_create_fiscal_period(db_session, 2021)
    db_session.commit()

    def be(codigo, valor):
        cuenta = get_account_by_codigo(db_session, codigo)
        upsert_entry(db_session, fiscal_period_id=periodo.id, account_id=cuenta.id, valor=Decimal(valor), tipo=Tipo.BALANCE)

    def ie(codigo, valor):
        cuenta = get_account_by_codigo(db_session, codigo)
        upsert_entry(db_session, fiscal_period_id=periodo.id, account_id=cuenta.id, valor=Decimal(valor), tipo=Tipo.RESULTADOS)

    be("1001", "1000.00")
    be("2001", "1000.00")  # patrimonio = 0
    ie("4001", "500.00")
    ie("8001", "450.00")
    db_session.commit()

    resultado = compute_dupont(db_session, periodo)
    assert resultado.disponible is False
    assert resultado.motivo_no_disponible is not None
