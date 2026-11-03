"""Copias de seguridad de la base de datos SQLite (secciones 3 y 12).

Las copias se crean con la API de respaldo de SQLite y se verifican
(database/backup_utils.py). Antes de restaurar se valida el archivo y se
muestra su contenido; la restauracion no se ejecuta inmediatamente: se
guarda la ruta en session_state y app.py la aplica en la siguiente
ejecucion, ANTES de abrir ninguna sesion, con copia previa automatica de
la BD actual y reversion si algo falla (hallazgo C-01).
"""
from __future__ import annotations

import datetime
import logging
import sqlite3

import streamlit as st

from database import connection
from database.backup_utils import InfoBD, RespaldoInvalido, crear_respaldo, inspeccionar_bd, marca_tiempo

log = logging.getLogger(__name__)


def _dir_respaldos():
    return connection.DB_PATH.parent / "backups"


def _listar_backups() -> list:
    if not _dir_respaldos().exists():
        return []
    return sorted(_dir_respaldos().glob("financiera_*.db"), reverse=True)


def _resumen(info: InfoBD) -> str:
    ejercicios = ", ".join(f"{a}{' (cerrado)' if e == 'CERRADO' else ''}" for a, e in info.ejercicios) or "ninguno"
    r = info.registros
    return (
        f"Empresa: {info.empresa} · Ejercicios: {ejercicios} · Importes: {r['balance_entry']} de balance, "
        f"{r['income_entry']} de resultados, {r['initial_balance']} saldos iniciales · Cuentas: {r['account']} · "
        f"Versión de esquema: {info.version_esquema}"
    )


def _preparar(ruta) -> None:
    try:
        info = inspeccionar_bd(ruta)
    except RespaldoInvalido as exc:
        st.session_state.pop("confirmar_restauracion", None)
        st.error(f"El archivo no se puede restaurar: {exc}")
        return
    st.session_state["confirmar_restauracion"] = str(ruta)
    st.session_state["confirmar_restauracion_resumen"] = _resumen(info)


def render() -> None:
    st.header("Copias de seguridad")
    db_path = connection.DB_PATH

    if not db_path.exists():
        st.info("Todavía no existe una base de datos para respaldar.")
        return

    tamano_kb = db_path.stat().st_size / 1024
    modificado = datetime.datetime.fromtimestamp(db_path.stat().st_mtime)
    st.caption(f"Base de datos actual: {db_path.name} · {tamano_kb:,.1f} KB · última modificación: {modificado:%Y-%m-%d %H:%M:%S}")

    if st.button("Crear copia de seguridad ahora", type="primary"):
        destino = _dir_respaldos() / f"financiera_{marca_tiempo()}.db"
        try:
            crear_respaldo(db_path, destino)
        except (RespaldoInvalido, OSError, sqlite3.Error) as exc:
            log.exception("No se pudo crear la copia de seguridad")
            st.error(f"No se pudo crear la copia de seguridad: {exc}")
        else:
            st.success(f"Copia de seguridad creada y verificada: {destino.name}")
            st.rerun()

    st.markdown("### Copias existentes")
    backups = _listar_backups()
    if not backups:
        st.info("No hay copias de seguridad todavía.")
    else:
        for backup in backups:
            col1, col2, col3 = st.columns([3, 1, 1])
            marca = datetime.datetime.fromtimestamp(backup.stat().st_mtime)
            col1.write(f"{backup.name} · {marca:%Y-%m-%d %H:%M:%S} · {backup.stat().st_size / 1024:,.1f} KB")
            with col2:
                st.download_button("Descargar", data=backup.read_bytes(), file_name=backup.name, key=f"dl_{backup.name}")
            with col3:
                if st.button("Restaurar", key=f"restore_{backup.name}"):
                    _preparar(backup)

    st.markdown("### Restaurar desde un archivo subido")
    subido = st.file_uploader("Archivo .db de respaldo", type=["db"])
    if subido is not None and st.button("Preparar restauración desde archivo subido"):
        _dir_respaldos().mkdir(parents=True, exist_ok=True)
        temporal = _dir_respaldos() / "_restaurar_subido.db"
        temporal.write_bytes(subido.getvalue())
        _preparar(temporal)

    pendiente = st.session_state.get("confirmar_restauracion")
    if pendiente:
        st.warning(
            f"¿Confirmas restaurar la base de datos desde '{pendiente}'?\n\n"
            f"Contenido de la copia: {st.session_state.get('confirmar_restauracion_resumen', '')}\n\n"
            "Se reemplazarán todos los datos actuales. Antes se guardará automáticamente una copia de la base "
            "actual en data/backups/ (financiera_pre_restauracion_...)."
        )
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("Sí, restaurar y sobrescribir", type="primary"):
                st.session_state.pop("confirmar_restauracion")
                st.session_state.pop("confirmar_restauracion_resumen", None)
                st.session_state["pending_restore"] = pendiente
                st.rerun()
        with col_no:
            if st.button("Cancelar restauración"):
                st.session_state.pop("confirmar_restauracion")
                st.session_state.pop("confirmar_restauracion_resumen", None)
                st.rerun()
