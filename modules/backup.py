"""Copias de seguridad de la base de datos SQLite (secciones 3 y 12).

La restauracion no se ejecuta inmediatamente: se guarda la ruta del
origen en session_state y se solicita un st.rerun(). app.py revisa esa
bandera ANTES de abrir ninguna sesion de base de datos en la siguiente
ejecucion, para poder liberar el engine actual y sobrescribir el
archivo .db de forma segura.
"""
from __future__ import annotations

import datetime
import shutil

import streamlit as st

from database.connection import DATA_DIR, DB_PATH

BACKUPS_DIR = DATA_DIR / "backups"


def _listar_backups() -> list:
    if not BACKUPS_DIR.exists():
        return []
    return sorted(BACKUPS_DIR.glob("financiera_*.db"), reverse=True)


def render() -> None:
    st.header("Copias de seguridad")

    if not DB_PATH.exists():
        st.info("Todavía no existe una base de datos para respaldar.")
        return

    tamano_kb = DB_PATH.stat().st_size / 1024
    modificado = datetime.datetime.fromtimestamp(DB_PATH.stat().st_mtime)
    st.caption(f"Base de datos actual: {DB_PATH.name} · {tamano_kb:,.1f} KB · última modificación: {modificado:%Y-%m-%d %H:%M:%S}")

    if st.button("Crear copia de seguridad ahora", type="primary"):
        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        marca = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        destino = BACKUPS_DIR / f"financiera_{marca}.db"
        shutil.copy2(DB_PATH, destino)
        st.success(f"Copia de seguridad creada: {destino.name}")
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
                    st.session_state["confirmar_restauracion"] = str(backup)

    st.markdown("### Restaurar desde un archivo subido")
    subido = st.file_uploader("Archivo .db de respaldo", type=["db"])
    if subido is not None and st.button("Preparar restauración desde archivo subido"):
        BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
        temporal = BACKUPS_DIR / "_restaurar_subido.db"
        temporal.write_bytes(subido.getvalue())
        st.session_state["confirmar_restauracion"] = str(temporal)

    pendiente = st.session_state.get("confirmar_restauracion")
    if pendiente:
        st.warning(
            f"¿Confirmas restaurar la base de datos desde '{pendiente}'? "
            "Esto SOBRESCRIBIRÁ todos los datos actuales. Esta acción no se puede deshacer."
        )
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("Sí, restaurar y sobrescribir", type="primary"):
                st.session_state.pop("confirmar_restauracion")
                st.session_state["pending_restore"] = pendiente
                st.rerun()
        with col_no:
            if st.button("Cancelar restauración"):
                st.session_state.pop("confirmar_restauracion")
                st.rerun()
