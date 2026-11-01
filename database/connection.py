"""Conexion a SQLite y utilidades de sesion.

La base de datos vive en data/financiera.db, fuera del control de
versiones (ver .gitignore), y persiste entre ejecuciones de la app.
"""
from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from database.models import Base

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "financiera.db"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_engine(db_path: Path | str | None = None):
    _ensure_data_dir()
    path = Path(db_path) if db_path else DB_PATH
    engine = create_engine(f"sqlite:///{path}", future=True)

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


_engine = None
_SessionFactory: sessionmaker | None = None


def init_db(db_path: Path | str | None = None) -> None:
    """Crea el engine, las tablas (si no existen) y la session factory."""
    global _engine, _SessionFactory
    _engine = get_engine(db_path)
    Base.metadata.create_all(_engine)
    _SessionFactory = sessionmaker(bind=_engine, expire_on_commit=False)


def dispose_engine() -> None:
    """Libera todas las conexiones del engine actual (necesario antes de
    sobrescribir el archivo .db al restaurar una copia de seguridad)."""
    global _engine, _SessionFactory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionFactory = None


def get_session() -> Session:
    if _SessionFactory is None:
        init_db()
    return _SessionFactory()


@contextmanager
def session_scope():
    """Context manager: commit en exito, rollback en excepcion."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
