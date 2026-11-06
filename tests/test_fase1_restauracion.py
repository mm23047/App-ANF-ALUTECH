"""Fase 1.7: copias y restauracion seguras (C-01, M-09 b)."""
import sqlite3
import sys

import pytest

from conftest import construir_bd_v0
from database import backup_utils, connection
from database.backup_utils import (
    RespaldoInvalido,
    RestauracionError,
    contar_filas,
    crear_respaldo,
    inspeccionar_bd,
    restaurar,
    sha256_archivo,
)
from database.connection import init_db, session_scope
from database.migrations import VERSION_ACTUAL, version_esquema
from database.repositories import get_company, save_company
from database.seed import seed_default_accounts


def _bd_app(ruta, empresa):
    init_db(db_path=ruta)
    with session_scope() as s:
        seed_default_accounts(s)
        save_company(s, nombre_legal=empresa, nombre_comercial="x", actividad_economica="x", pais="SV", moneda="USD",
                     anio_inicial_analisis=2021)
    connection.dispose_engine()
    return ruta


@pytest.fixture()
def actual(tmp_path):
    return _bd_app(tmp_path / "financiera.db", "Empresa actual")


def test_crear_respaldo_con_api_sqlite_verificado(tmp_path, actual):
    copia = crear_respaldo(actual, tmp_path / "backups" / "financiera_copia.db")
    assert contar_filas(copia) == contar_filas(actual)
    assert inspeccionar_bd(copia).empresa == "Empresa actual"
    with pytest.raises(FileExistsError):
        crear_respaldo(actual, copia)


def test_inspeccion_resume_el_contenido(actual):
    info = inspeccionar_bd(actual)
    assert info.empresa == "Empresa actual"
    assert info.version_esquema == VERSION_ACTUAL
    assert info.registros["account"] == 30
    assert info.ejercicios == []


@pytest.mark.parametrize("caso", ["corrupto", "vacio", "ajena", "sin_empresa", "dos_empresas", "version_futura", "cabecera_ok_contenido_basura"])
def test_archivos_invalidos_son_rechazados(tmp_path, caso):
    ruta = tmp_path / f"{caso}.db"
    if caso == "corrupto":
        ruta.write_bytes(b"esto no es una base sqlite" * 100)
    elif caso == "vacio":
        ruta.write_bytes(b"")
    elif caso == "ajena":
        con = sqlite3.connect(ruta); con.execute("create table x(a)"); con.commit(); con.close()
    elif caso == "cabecera_ok_contenido_basura":
        ruta.write_bytes(backup_utils.ENCABEZADO_SQLITE + b"\xff" * 4000)
    else:
        _bd_app(ruta, "Otra")
        con = sqlite3.connect(ruta)
        if caso == "sin_empresa":
            con.execute("DELETE FROM company")
        elif caso == "dos_empresas":
            con.execute("INSERT INTO company VALUES (2, 'b', 'b', 'b', 'b', 'USD', 2021)")
        else:
            con.execute(f"PRAGMA user_version = {VERSION_ACTUAL + 1}")
        con.commit(); con.close()
    with pytest.raises(RespaldoInvalido):
        inspeccionar_bd(ruta)


def test_restaurar_copia_valida_crea_copia_previa_identica(tmp_path, actual):
    origen = _bd_app(tmp_path / "otra.db", "Empresa restaurada")
    hash_actual = sha256_archivo(actual)
    resultado = restaurar(origen, actual, dir_respaldos=tmp_path / "backups")
    assert resultado.info.empresa == "Empresa restaurada"
    assert resultado.respaldo_previo.name.startswith("financiera_pre_restauracion_")
    assert sha256_archivo(resultado.respaldo_previo) == hash_actual
    init_db(db_path=actual)
    with session_scope() as s:
        assert get_company(s).nombre_legal == "Empresa restaurada"
    connection.dispose_engine()
    assert not (tmp_path / "financiera.db.restaurando").exists()


def test_restaurar_copia_v0_la_migra(tmp_path, actual):
    origen = construir_bd_v0(tmp_path / "copia_v0.db", [1234.56] + [0] * 18)
    restaurar(origen, actual, dir_respaldos=tmp_path / "backups")
    assert version_esquema(actual) == VERSION_ACTUAL
    assert version_esquema(origen) == 0  # el archivo de origen no se modifica


@pytest.mark.parametrize("contenido", [b"basura" * 500, b""])
def test_restaurar_invalido_deja_la_bd_intacta(tmp_path, actual, contenido):
    origen = tmp_path / "malo.db"
    origen.write_bytes(contenido)
    hash_actual = sha256_archivo(actual)
    with pytest.raises(RespaldoInvalido):
        restaurar(origen, actual, dir_respaldos=tmp_path / "backups")
    assert sha256_archivo(actual) == hash_actual
    assert not (tmp_path / "backups").exists()  # ni siquiera se crea la copia previa


def test_fallo_del_reemplazo_deja_la_bd_intacta(tmp_path, actual, monkeypatch):
    origen = _bd_app(tmp_path / "otra.db", "Otra")
    hash_actual = sha256_archivo(actual)

    def reemplazo_bloqueado(*_):
        raise PermissionError("archivo en uso")

    monkeypatch.setattr(backup_utils.os, "replace", reemplazo_bloqueado)
    monkeypatch.setattr(backup_utils.time, "sleep", lambda _: None)
    with pytest.raises(RestauracionError, match="en uso"):
        restaurar(origen, actual, dir_respaldos=tmp_path / "backups")
    assert sha256_archivo(actual) == hash_actual
    assert not (tmp_path / "financiera.db.restaurando").exists()


@pytest.mark.skipif(sys.platform != "win32", reason="bloqueo de archivos propio de Windows")
def test_bloqueo_real_de_windows_deja_la_bd_intacta(tmp_path, actual, monkeypatch):
    """Otra conexion abierta (otra pestaña) impide reemplazar el archivo."""
    origen = _bd_app(tmp_path / "otra.db", "Otra")
    hash_actual = sha256_archivo(actual)
    monkeypatch.setattr(backup_utils.time, "sleep", lambda _: None)
    otra_pestana = sqlite3.connect(actual)
    otra_pestana.execute("SELECT COUNT(*) FROM company").fetchone()
    try:
        with pytest.raises(RestauracionError, match="en uso"):
            restaurar(origen, actual, dir_respaldos=tmp_path / "backups")
    finally:
        otra_pestana.close()
    assert sha256_archivo(actual) == hash_actual


def test_diario_pendiente_impide_restaurar(tmp_path, actual):
    origen = _bd_app(tmp_path / "otra.db", "Otra")
    (tmp_path / "financiera.db-journal").write_bytes(b"x")
    hash_actual = sha256_archivo(actual)
    with pytest.raises(RestauracionError, match="transacción pendiente"):
        restaurar(origen, actual, dir_respaldos=tmp_path / "backups")
    assert sha256_archivo(actual) == hash_actual


def test_fallo_despues_de_reemplazar_revierte_al_original(tmp_path, actual, monkeypatch):
    origen = _bd_app(tmp_path / "otra.db", "Otra")
    hash_actual = sha256_archivo(actual)
    inspeccion_real = backup_utils.inspeccionar_bd

    def inspeccion_que_falla_en_destino(ruta):
        if ruta == actual and sha256_archivo(actual) != hash_actual:
            raise RespaldoInvalido("verificación posterior simulada")
        return inspeccion_real(ruta)

    monkeypatch.setattr(backup_utils, "inspeccionar_bd", inspeccion_que_falla_en_destino)
    with pytest.raises(RestauracionError, match="se restableció"):
        restaurar(origen, actual, dir_respaldos=tmp_path / "backups")
    assert sha256_archivo(actual) == hash_actual
