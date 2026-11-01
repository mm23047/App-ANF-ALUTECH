"""Fixtures compartidas. Cada prueba recibe su propia base de datos
SQLite temporal (aislada de data/financiera.db) con el catálogo
estándar sembrado, usando datos sintéticos definidos en cada prueba."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from database import connection
from database.connection import init_db, session_scope
from database.seed import seed_default_accounts


@pytest.fixture()
def db_session(tmp_path):
    db_path = tmp_path / "test_financiera.db"
    init_db(db_path=db_path)
    with session_scope() as setup_session:
        seed_default_accounts(setup_session)

    with session_scope() as session:
        yield session

    connection.dispose_engine()
