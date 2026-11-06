"""Fase 1.1: versionado del esquema y migracion a centavos (M-09, M-02, A-08, M-05)."""
import shutil
import sqlite3
from decimal import Decimal

import pytest

from conftest import construir_bd_v0
from database import connection
from database.backup_utils import contar_filas, sha256_archivo, verificar_integridad
from database.connection import init_db, session_scope
from database.enums import TipoEstadoFinanciero as Tipo
from database.migrations import VERSION_ACTUAL, EsquemaIncompatible, MigracionError, comparar_bd, migrar, version_esquema
from database.models import BalanceEntry, ChangeHistory
from database.repositories import get_entries_map, get_initial_balances_map


def _esquema(ruta):
    con = sqlite3.connect(ruta)
    try:
        tablas = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        columnas = {t: [tuple(r[1:]) for r in con.execute(f'PRAGMA table_info("{t}")')] for t in tablas}
        disparadores = sorted(r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='trigger'"))
        return columnas, disparadores
    finally:
        con.close()


def test_bd_v0_migra_sin_perder_filas_ni_importes(tmp_path):
    importes = [1234.56, -98765.43, 0, 0.1, 123456789012.34, 99999999.99] + [0] * 13
    bd = construir_bd_v0(tmp_path / "v0.db", importes)
    antes = tmp_path / "v0_antes.db"
    shutil.copy2(bd, antes)

    registro = migrar(bd)

    assert version_esquema(bd) == VERSION_ACTUAL
    assert any("Copia previa verificada" in linea for linea in registro)
    diferencias, comparados = comparar_bd(antes, bd)
    assert diferencias == []
    assert len(comparados) == 19 + 2 + 1  # balance + resultados + saldo inicial
    verificar_integridad(bd)

    con = sqlite3.connect(bd)
    tipos = con.execute("SELECT DISTINCT typeof(valor) FROM balance_entry UNION SELECT typeof(valor) FROM income_entry").fetchall()
    centavos = dict(con.execute("SELECT id, valor FROM balance_entry WHERE id <= 6").fetchall())
    con.close()
    assert tipos == [("integer",)]
    assert centavos == {1: 123456, 2: -9876543, 3: 0, 4: 10, 5: 12345678901234, 6: 9999999999}

    init_db(db_path=bd)
    with session_scope() as s:
        balance = get_entries_map(s, 1, Tipo.BALANCE)
        resultados = get_entries_map(s, 2, Tipo.RESULTADOS)
        iniciales = get_initial_balances_map(s, 2)
    connection.dispose_engine()
    assert balance[1] == Decimal("1234.56") and balance[2] == Decimal("-98765.43")
    assert balance[5] == Decimal("123456789012.34")
    assert resultados == {20: Decimal("1234.56"), 21: Decimal("600.00")}
    assert iniciales == {1: Decimal("99999999.99")}


def test_los_19_ceros_se_conservan_intactos(tmp_path):
    bd = construir_bd_v0(tmp_path / "ceros.db")  # 19 cuentas en 0, como la BD real
    antes = tmp_path / "antes.db"
    shutil.copy2(bd, antes)
    migrar(bd)
    diferencias, comparados = comparar_bd(antes, bd)
    assert diferencias == []
    con = sqlite3.connect(bd)
    filas = con.execute("SELECT id, account_id, valor FROM balance_entry ORDER BY id").fetchall()
    con.close()
    assert filas == [(i, i, 0) for i in range(1, 20)]


def test_respaldo_previo_a_la_migracion_es_integro(tmp_path):
    bd = construir_bd_v0(tmp_path / "financiera.db")
    conteos = contar_filas(bd)
    migrar(bd)
    respaldos = list((tmp_path / "backups").glob("financiera_pre_migracion_v0_*.db"))
    assert len(respaldos) == 1
    verificar_integridad(respaldos[0])
    assert version_esquema(respaldos[0]) == 0
    assert contar_filas(respaldos[0]) == conteos


def test_migracion_es_idempotente(tmp_path):
    bd = construir_bd_v0(tmp_path / "v0.db")
    migrar(bd)
    hash_migrada = sha256_archivo(bd)
    assert migrar(bd) == []
    init_db(db_path=bd)
    connection.dispose_engine()
    assert sha256_archivo(bd) == hash_migrada
    assert len(list((tmp_path / "backups").glob("*.db"))) == 1


def test_bd_migrada_tiene_el_mismo_esquema_que_una_nueva(tmp_path):
    bd = construir_bd_v0(tmp_path / "v0.db")
    migrar(bd)
    nueva = tmp_path / "nueva.db"
    init_db(db_path=nueva)
    connection.dispose_engine()
    assert version_esquema(nueva) == VERSION_ACTUAL
    columnas_migrada, triggers_migrada = _esquema(bd)
    columnas_nueva, triggers_nueva = _esquema(nueva)
    assert columnas_migrada == columnas_nueva
    # 13 de la v3 + 6 de la v4 (cierre de fuente_importe y dato_complementario).
    assert triggers_migrada == triggers_nueva and len(triggers_nueva) == 19


@pytest.mark.parametrize("valor_ambiguo", [0.30000000000000004, 2.675, 12345678901234.56, "abc"])
def test_importe_ambiguo_detiene_la_migracion_sin_cambiar_la_bd(tmp_path, valor_ambiguo):
    bd = construir_bd_v0(tmp_path / "ambigua.db", [100.5, valor_ambiguo])
    hash_original = sha256_archivo(bd)
    with pytest.raises(MigracionError, match="balance_entry id=2"):
        migrar(bd)
    assert sha256_archivo(bd) == hash_original
    assert version_esquema(bd) == 0


def test_historial_heredado_no_se_reescribe(tmp_path):
    bd = construir_bd_v0(tmp_path / "v0.db")
    migrar(bd)
    init_db(db_path=bd)
    with session_scope() as s:
        heredados = s.query(ChangeHistory).filter_by(tabla_afectada="balance_entry").all()
        assert len(heredados) == 19
        assert all(h.fiscal_period_id is None and h.account_id is None and h.lote_id is None for h in heredados)
        assert [h.registro_id for h in heredados] == list(range(1, 20))
    connection.dispose_engine()


def test_esquema_mas_reciente_es_rechazado(tmp_path):
    bd = tmp_path / "futura.db"
    init_db(db_path=bd)
    connection.dispose_engine()
    con = sqlite3.connect(bd)
    con.execute(f"PRAGMA user_version = {VERSION_ACTUAL + 1}")
    con.close()
    with pytest.raises(EsquemaIncompatible):
        migrar(bd)


def test_centavos_rechaza_mas_de_dos_decimales_en_la_bd(db_session):
    """El tipo Centavos nunca redondea, aunque se salte parse_importe."""
    from sqlalchemy.exc import StatementError

    from database.repositories import get_account_by_codigo, get_or_create_fiscal_period

    periodo, _ = get_or_create_fiscal_period(db_session, 2021)
    db_session.add(BalanceEntry(fiscal_period_id=periodo.id, account_id=get_account_by_codigo(db_session, "1001").id,
                                valor=Decimal("1.234")))
    with pytest.raises(StatementError, match="mas de dos decimales"):
        db_session.flush()
    db_session.rollback()
