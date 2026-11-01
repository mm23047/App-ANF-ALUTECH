"""Fixtures compartidas. Cada prueba recibe su propia base de datos
SQLite temporal (aislada de data/financiera.db) con el catálogo
estándar sembrado, usando datos sintéticos definidos en cada prueba."""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from database import connection
from database.connection import init_db, session_scope
from database.seed import seed_default_accounts

REAL_DB = connection.DATA_DIR / "financiera.db"


def _sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


@pytest.fixture(scope="session", autouse=True)
def _proteger_bd_real():
    """Falla la sesión de pruebas si data/financiera.db cambia."""
    antes = _sha256(REAL_DB)
    yield
    connection.dispose_engine()
    assert _sha256(REAL_DB) == antes, "Las pruebas modificaron data/financiera.db"


@pytest.fixture(autouse=True)
def _redirigir_db_path(tmp_path, monkeypatch):
    """Si algún código abre la BD por defecto (init_db() sin ruta), usa un
    archivo temporal en lugar de data/financiera.db."""
    monkeypatch.setattr(connection, "DB_PATH", tmp_path / "db_por_defecto.db")


ESQUEMA_V0 = Path(__file__).resolve().parent / "fixtures" / "esquema_v0.sql"
FECHA = "2026-11-01 15:45:04.751750"


def construir_bd_v0(ruta: Path, importes_balance: list | None = None) -> Path:
    """BD con el esquema original (version 0) y datos sinteticos. Los
    importes se insertan tal cual (float -> REAL, int -> INTEGER), como los
    guardaba la aplicacion antes de la migracion a centavos.

    Por defecto reproduce la BD real: 2021 con 19 cuentas de balance en 0."""
    import sqlite3

    from database.seed import DEFAULT_ACCOUNTS

    con = sqlite3.connect(ruta)
    con.executescript(ESQUEMA_V0.read_text(encoding="utf-8"))
    con.execute("INSERT INTO company VALUES (1, 'Empresa v0', 'EV0', 'Pruebas', 'SV', 'USD', 2021)")
    con.execute("INSERT INTO fiscal_period VALUES (1, 2021, 'ABIERTO', ?)", (FECHA,))
    con.execute("INSERT INTO fiscal_period VALUES (2, 2022, 'ABIERTO', ?)", (FECHA,))
    for i, (codigo, nombre, cat, sub, nat, efecto, orden) in enumerate(DEFAULT_ACCOUNTS, start=1):
        con.execute(
            "INSERT INTO account VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVA', ?)",
            (i, codigo, nombre, cat.value, sub.value if sub else None, efecto.value if efecto else None, nat.value, orden),
        )
        con.execute(
            "INSERT INTO change_history VALUES (?, 'account', ?, 'creacion', NULL, ?, 'CREAR', ?)",
            (i, i, f"{codigo} - {nombre}", FECHA),
        )
    if importes_balance is None:
        importes_balance = [0] * 19  # cuentas 1..19 (balance) en 0, como en la BD real
    for account_id, valor in enumerate(importes_balance, start=1):
        con.execute("INSERT INTO balance_entry VALUES (?, 1, ?, ?, ?, ?)", (account_id, account_id, valor, FECHA, FECHA))
        con.execute(
            "INSERT INTO change_history (tabla_afectada, registro_id, campo, valor_anterior, valor_nuevo, operacion, fecha) "
            "VALUES ('balance_entry', ?, 'valor', NULL, ?, 'CREAR', ?)",
            (account_id, str(valor), FECHA),
        )
    con.execute("INSERT INTO income_entry VALUES (1, 2, 20, 1234.56, ?, ?)", (FECHA, FECHA))
    con.execute("INSERT INTO income_entry VALUES (2, 2, 21, 600, ?, ?)", (FECHA, FECHA))
    con.execute("INSERT INTO initial_balance VALUES (1, 2, 1, 99999999.99)")
    con.execute("INSERT INTO statement_status VALUES (1, 1, 'BALANCE', 'REVISADO', ?)", (FECHA,))
    con.commit()
    con.close()
    return ruta


@pytest.fixture()
def db_session(tmp_path):
    db_path = tmp_path / "test_financiera.db"
    init_db(db_path=db_path)
    with session_scope() as setup_session:
        seed_default_accounts(setup_session)

    with session_scope() as session:
        yield session

    connection.dispose_engine()
