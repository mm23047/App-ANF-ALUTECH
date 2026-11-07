"""Conexion a SQLite y utilidades de sesion.

La base de datos vive en data/financiera.db, fuera del control de
versiones (ver .gitignore), y persiste entre ejecuciones de la app.
"""
from __future__ import annotations

import os
import shutil
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from database.migrations import migrar
from database.models import Base

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "financiera.db"
# Base de partida que se publica con el codigo (caso Alutech). Nunca se usa directamente: cada equipo trabaja en su copia.
BASE_INICIAL = DATA_DIR / "inicial" / "financiera.db"


def preparar_base_inicial() -> bool:
    """Primera ejecucion de un clon nuevo: copia la base inicial a data/financiera.db para no crear una base vacia. Nunca
    sobrescribe una base existente ni actua si DB_PATH se redirigio. ANF_BASE_VACIA=1 permite empezar con otra empresa."""
    destino = DATA_DIR / "financiera.db"
    if (DB_PATH != destino or destino.exists() or not BASE_INICIAL.is_file()
            or os.environ.get("ANF_BASE_VACIA") == "1"):
        return False
    temporal = destino.with_suffix(".copiando")
    shutil.copyfile(BASE_INICIAL, temporal)
    os.replace(temporal, destino)  # atomico: una copia interrumpida nunca queda como base
    return True


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
    """Lleva la BD a la version de esquema actual (con copia previa si hay
    que migrar datos existentes; ver database/migrations.py) y crea el
    engine y la session factory."""
    global _engine, _SessionFactory
    _ensure_data_dir()
    migrar(Path(db_path) if db_path else DB_PATH)
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
def render_scope():
    """Sesion para renderizar una pagina de Streamlit (hallazgo M-06).

    Nunca confirma implicitamente: al terminar siempre hace rollback, de
    modo que leer o mostrar una pagina no guarda nada. Las acciones de
    escritura confirman de forma explicita (components.transacciones).
    """
    session = get_session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@contextmanager
def session_scope():
    """Context manager: commit en exito, rollback en excepcion. Para scripts
    y pruebas; las paginas usan render_scope."""
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
