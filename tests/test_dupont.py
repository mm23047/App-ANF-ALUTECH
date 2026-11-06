"""Casos 12-16 de la sección 16: margen neto, rotación de activos,
multiplicador del capital, ROE DuPont y su coincidencia con el ROE
directo."""
from decimal import Decimal

from calculations.banderas import banderas_dupont, resumen
from calculations.dupont import compute_dupont
from components.money import q2
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
    # Primer ejercicio: se calcula con sus saldos al cierre, sin necesitar un balance anterior.
    assert resultado.margen_neto == Decimal("0.10")  # 10%
    assert resultado.rotacion_activos == Decimal("1.00")  # 1000 ingresos / 1000 activos al cierre
    # 1000 / 600 ~= 1.67. Desde la fase 2 (hallazgo B-01) el factor se conserva sin
    # redondear; se compara al redondeo de presentacion (q2, ROUND_HALF_UP). Cambio
    # autorizado por el usuario: ver PLAN_DE_CORRECCION.md, fase 3.
    assert q2(resultado.multiplicador_capital) == Decimal("1.67")
    assert resultado.multiplicador_capital == Decimal("1000") / Decimal("600")


def test_roe_dupont_y_coincidencia_con_roe_directo(db_session):
    periodo = _capturar_ejercicio(db_session, 2021, activo_total=1000, patrimonio=600, ingresos=1000, utilidad_neta=100)
    resultado = compute_dupont(db_session, periodo)

    roe_esperado = (Decimal("100") / Decimal("600") * 100).quantize(Decimal("0.01"))
    assert resultado.roe_directo_pct == roe_esperado
    assert abs(resultado.roe_dupont_pct - resultado.roe_directo_pct) <= Decimal("0.01")
    assert resultado.coincide_redondeo is True


def test_cada_ejercicio_usa_solo_sus_saldos_al_cierre(db_session):
    _capturar_ejercicio(db_session, 2021, activo_total=1000, patrimonio=600, ingresos=1000, utilidad_neta=100)
    periodo_2022 = _capturar_ejercicio(db_session, 2022, activo_total=1200, patrimonio=700, ingresos=1200, utilidad_neta=150)

    resultado = compute_dupont(db_session, periodo_2022)
    assert resultado.activo_total == Decimal("1200.00")
    assert resultado.patrimonio_total == Decimal("700.00")
    assert resultado.rotacion_activos == Decimal("1200") / Decimal("1200")
    assert resultado.multiplicador_capital == Decimal("1200") / Decimal("700")


def test_primer_ejercicio_no_es_aproximado(db_session):
    periodo = _capturar_ejercicio(db_session, 2021, activo_total=1000, patrimonio=600, ingresos=1000, utilidad_neta=100)
    resultado = compute_dupont(db_session, periodo)
    assert resultado.disponible and "APROXIMADO" not in resumen(banderas_dupont(resultado))
    assert resultado.activo_total == Decimal("1000.00")


def test_dupont_no_calcula_con_patrimonio_al_cierre_cero(db_session):
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
