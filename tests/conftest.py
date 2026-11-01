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


@pytest.fixture()
def db_session(tmp_path):
    db_path = tmp_path / "test_financiera.db"
    init_db(db_path=db_path)
    with session_scope() as setup_session:
        seed_default_accounts(setup_session)

    with session_scope() as session:
        yield session

    connection.dispose_engine()
