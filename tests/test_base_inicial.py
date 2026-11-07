"""Base inicial que se publica con el codigo: un clon nuevo abre con los datos de Alutech, sin tocar nunca una base existente.
Las pruebas redirigen DATA_DIR y BASE_INICIAL a carpetas temporales; solo la ultima lee la base publicada."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pytest

from database import connection


@pytest.fixture()
def carpeta(tmp_path, monkeypatch):
    datos = tmp_path / "data"
    (datos / "inicial").mkdir(parents=True)
    (datos / "inicial" / "financiera.db").write_bytes(b"base inicial")
    monkeypatch.setattr(connection, "DATA_DIR", datos)
    monkeypatch.setattr(connection, "DB_PATH", datos / "financiera.db")
    monkeypatch.setattr(connection, "BASE_INICIAL", datos / "inicial" / "financiera.db")
    monkeypatch.delenv("ANF_BASE_VACIA", raising=False)
    return datos


def test_clon_nuevo_copia_la_base_inicial(carpeta):
    assert connection.preparar_base_inicial() is True
    assert (carpeta / "financiera.db").read_bytes() == b"base inicial"
    assert not list(carpeta.glob("*.copiando"))


def test_nunca_sobrescribe_una_base_existente(carpeta):
    (carpeta / "financiera.db").write_bytes(b"datos del usuario")
    assert connection.preparar_base_inicial() is False
    assert (carpeta / "financiera.db").read_bytes() == b"datos del usuario"


def test_la_base_inicial_no_cambia_al_usar_la_copia(carpeta):
    connection.preparar_base_inicial()
    (carpeta / "financiera.db").write_bytes(b"modificada")
    assert (carpeta / "inicial" / "financiera.db").read_bytes() == b"base inicial"


def test_ruta_redirigida_no_recibe_la_base_inicial(carpeta, tmp_path, monkeypatch):
    monkeypatch.setattr(connection, "DB_PATH", tmp_path / "otra.db")
    assert connection.preparar_base_inicial() is False
    assert not (carpeta / "financiera.db").exists()


def test_variable_permite_empezar_con_otra_empresa(carpeta, monkeypatch):
    monkeypatch.setenv("ANF_BASE_VACIA", "1")
    assert connection.preparar_base_inicial() is False
    assert not (carpeta / "financiera.db").exists()


def test_sin_base_inicial_no_falla(carpeta):
    (carpeta / "inicial" / "financiera.db").unlink()
    assert connection.preparar_base_inicial() is False


def test_la_base_publicada_es_valida_y_no_trae_datos_de_prueba():
    publicada = Path(connection.__file__).resolve().parent.parent / "data" / "inicial" / "financiera.db"
    con = sqlite3.connect(f"file:{publicada}?mode=ro", uri=True)
    try:
        assert con.execute("pragma integrity_check").fetchone()[0] == "ok"
        assert con.execute("select nombre_legal from company").fetchone()[0].startswith("Alutech")
        assert con.execute("select count(*) from fiscal_period").fetchone()[0] == 5
        assert con.execute("select max(version) from schema_migration").fetchone()[0] == 4
        assert con.execute("select count(*) from account where codigo like 'Z%' or codigo like 'Q%'").fetchone()[0] == 0
    finally:
        con.close()
