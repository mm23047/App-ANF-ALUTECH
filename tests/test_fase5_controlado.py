"""Fase 5.4: caso sintetico controlado de 3 ejercicios consecutivos.

Los valores esperados (tests/fixtures/caso_controlado.json) se calcularon
a mano y se verificaron con un calculo independiente en fracciones
exactas, sin codigo de la aplicacion. Aceptacion del plan: diferencia
0,00 en importes y <= 0,01 pp en porcentajes. Los factores DuPont se
comparan con la fraccion exacta.

No son datos de Alutech: la conciliacion con Alutech (5.5) esta pendiente.
"""
import json
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest

from calculations.balance_sheet import compute_balance_sheet
from calculations.banderas import banderas_balance, banderas_dupont, banderas_resultados, resumen
from calculations.controls import CONCILIADO, conciliar_resultado
from calculations.dupont import compute_dupont
from calculations.income_statement import compute_income_statement
from calculations.vertical_analysis import compute_vertical_balance, compute_vertical_income
from database import connection
from database.connection import init_db, session_scope
from database.enums import TipoEstadoFinanciero as Tipo
from database.repositories import (
    get_account_by_codigo,
    get_fiscal_period,
    get_or_create_fiscal_period,
    save_company,
    upsert_entry,
    upsert_initial_balance,
)
from database.seed import seed_default_accounts

CASO = json.loads((Path(__file__).parent / "fixtures" / "caso_controlado.json").read_text(encoding="utf-8"))
ANIOS = sorted(CASO["ejercicios"])
TOLERANCIA_PP = Decimal("0.01")
TOLERANCIA_FACTOR = Decimal("1e-20")


@pytest.fixture(scope="module")
def bd(tmp_path_factory):
    init_db(db_path=tmp_path_factory.mktemp("caso_controlado") / "caso.db")
    with session_scope() as s:
        seed_default_accounts(s)
        save_company(s, **CASO["empresa"])
        for anio in ANIOS:
            p, _ = get_or_create_fiscal_period(s, int(anio))
            for clave, tipo in (("balance", Tipo.BALANCE), ("resultados", Tipo.RESULTADOS)):
                for codigo, valor in CASO["ejercicios"][anio][clave].items():
                    upsert_entry(s, fiscal_period_id=p.id, account_id=get_account_by_codigo(s, codigo).id, valor=valor,
                                 tipo=tipo)
        p2021 = get_fiscal_period(s, 2021)
        for codigo, valor in CASO["saldos_iniciales_2021"].items():
            upsert_initial_balance(s, fiscal_period_id=p2021.id, account_id=get_account_by_codigo(s, codigo).id, valor=valor)
    yield
    connection.dispose_engine()


def _periodo(s, anio):
    return get_fiscal_period(s, int(anio))


@pytest.mark.parametrize("anio", ANIOS)
def test_balance_general(bd, anio):
    esperado = CASO["esperado"][anio]["balance"]
    with session_scope() as s:
        bs = compute_balance_sheet(s, _periodo(s, anio).id)
    calculado = {
        "activo_corriente": bs.activo_corriente.subtotal, "activo_no_corriente": bs.activo_no_corriente.subtotal,
        "total_activo": bs.total_activo, "pasivo_corriente": bs.pasivo_corriente.subtotal,
        "pasivo_no_corriente": bs.pasivo_no_corriente.subtotal, "total_pasivo": bs.total_pasivo,
        "total_patrimonio": bs.total_patrimonio, "total_pasivo_patrimonio": bs.total_pasivo_patrimonio,
        "diferencia": bs.diferencia,
    }
    for clave, valor in calculado.items():
        assert valor - Decimal(esperado[clave]) == 0, (anio, clave, valor, esperado[clave])
    assert bs.cuadra is esperado["cuadra"] and bs.completo is esperado["completo"]
    assert not bs.advertencias_signo  # todo el caso respeta la convencion de signos


@pytest.mark.parametrize("anio", ANIOS)
def test_estado_de_resultados(bd, anio):
    esperado = CASO["esperado"][anio]["resultados"]
    with session_scope() as s:
        inc = compute_income_statement(s, _periodo(s, anio).id)
    calculado = {
        "ingresos_netos": inc.ingresos_netos.subtotal, "costo_ventas": inc.costo_ventas.subtotal,
        "utilidad_bruta": inc.utilidad_bruta, "utilidad_operativa": inc.utilidad_operativa,
        "resultado_financiero": inc.resultado_financiero, "otros_resultados": inc.otros_resultados,
        "utilidad_antes_impuestos": inc.utilidad_antes_impuestos, "impuesto_renta": inc.impuesto_renta.subtotal,
        "utilidad_neta": inc.utilidad_neta,
    }
    for clave, valor in calculado.items():
        assert valor - Decimal(esperado[clave]) == 0, (anio, clave, valor, esperado[clave])
    assert inc.completo is esperado["completo"]
    assert not inc.advertencias_signo


def _comparar_vertical(anio, lineas, esperado):
    calculado = {l.codigo or l.etiqueta: l for l in lineas}
    assert set(calculado) == set(esperado), (anio, set(calculado) ^ set(esperado))
    for clave, (valor, porcentaje) in esperado.items():
        linea = calculado[clave]
        if valor is None:
            assert linea.valor is None and linea.porcentaje is None, (anio, clave)
            continue
        assert linea.valor - Decimal(valor) == 0, (anio, clave, linea.valor, valor)
        assert abs(linea.porcentaje - Decimal(porcentaje)) <= TOLERANCIA_PP, (anio, clave, linea.porcentaje, porcentaje)


@pytest.mark.parametrize("anio", ANIOS)
def test_analisis_vertical_del_balance(bd, anio):
    with session_scope() as s:
        vb = compute_vertical_balance(s, _periodo(s, anio).id)
    assert vb.disponible
    _comparar_vertical(anio, vb.lineas, CASO["esperado"][anio]["vertical_balance"])


@pytest.mark.parametrize("anio", ANIOS)
def test_analisis_vertical_de_resultados(bd, anio):
    with session_scope() as s:
        vi = compute_vertical_income(s, _periodo(s, anio).id)
    assert vi.disponible
    _comparar_vertical(anio, vi.lineas, CASO["esperado"][anio]["vertical_resultados"])


@pytest.mark.parametrize("anio", ANIOS)
def test_dupont(bd, anio):
    esperado = CASO["esperado"][anio]["dupont"]
    with session_scope() as s:
        dp = compute_dupont(s, _periodo(s, anio))
    assert dp.disponible and dp.interpretable is esperado["interpretable"]
    for clave in ("activo_total", "patrimonio_total", "utilidad_neta", "ingresos_netos"):
        assert getattr(dp, clave) - Decimal(esperado[clave]) == 0, (anio, clave, getattr(dp, clave), esperado[clave])
    for clave in ("margen_neto", "rotacion_activos", "multiplicador_capital", "roe"):
        fraccion = Fraction(esperado[clave])
        exacto = Decimal(fraccion.numerator) / Decimal(fraccion.denominator)
        assert abs(getattr(dp, clave) - exacto) < TOLERANCIA_FACTOR, (anio, clave, getattr(dp, clave), esperado[clave])
    for clave in ("roe_dupont_pct", "roe_directo_pct"):
        assert abs(getattr(dp, clave) - Decimal(esperado["roe_pct"])) <= TOLERANCIA_PP, (anio, clave, getattr(dp, clave))
    assert all(c.correcto for c in dp.controles), [(c.nombre, c.detalle) for c in dp.controles if not c.correcto]


@pytest.mark.parametrize("anio", ANIOS)
def test_estado_de_los_reportes(bd, anio):
    with session_scope() as s:
        p = _periodo(s, anio)
        bs, inc = compute_balance_sheet(s, p.id), compute_income_statement(s, p.id)
        conciliacion = conciliar_resultado(bs, inc)
        dp = compute_dupont(s, p)
    assert conciliacion.estado == CONCILIADO and conciliacion.diferencia == 0
    esperado = CASO["esperado"][anio]["estado"]
    assert resumen(banderas_balance(bs, conciliacion)) == esperado
    assert resumen(banderas_resultados(inc, conciliacion)) == esperado
    assert resumen(banderas_dupont(dp)) == esperado
