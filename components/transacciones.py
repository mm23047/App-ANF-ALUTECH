"""Escrituras explicitas desde la interfaz (hallazgos M-06 y A-07).

Las paginas se renderizan con database.connection.render_scope, que nunca
confirma. Cada accion del usuario que escribe pasa por ejecutar_escritura:
agrupa sus cambios en un lote del historial, confirma, y ante un error
revierte TODO, deja la traza completa en el log y muestra al usuario un
mensaje comprensible.
"""
from __future__ import annotations

import logging
from typing import Callable, TypeVar

import streamlit as st
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

from database.repositories import lote

T = TypeVar("T")
log = logging.getLogger(__name__)


def mensaje_error(exc: Exception) -> str:
    if isinstance(exc, IntegrityError):
        texto = str(exc.orig)
        if "EJERCICIO_CERRADO" in texto:
            return "el ejercicio está cerrado y no admite cambios."
        if "UNIQUE" in texto:
            return "ya existe un registro con esos mismos datos."
        if "FOREIGN KEY" in texto:
            return "el registro hace referencia a una cuenta o ejercicio inexistente, o tiene datos que dependen de él."
        if "NOT NULL" in texto:
            return "falta un valor obligatorio."
        return "la base de datos rechazó la operación por una regla de integridad."
    if isinstance(exc, OperationalError):
        if "locked" in str(exc.orig).lower():
            return "la base de datos está ocupada por otra operación. Espere un momento e intente de nuevo."
        return f"error de acceso a la base de datos ({exc.orig})."
    if isinstance(exc, SQLAlchemyError):
        return "error de la base de datos. El detalle técnico quedó en el registro de la aplicación."
    return str(exc)


def ejecutar_escritura(session: Session, accion: Callable[[], T], *, descripcion: str) -> tuple[bool, T | None]:
    """Ejecuta `accion` y confirma la transaccion.

    Devuelve (True, resultado) si se guardo, o (False, None) si se revirtio.
    Solo captura errores de validacion (ValueError) y de base de datos
    (SQLAlchemyError); cualquier otro error se propaga sin ocultarse.
    """
    try:
        with lote(session):
            resultado = accion()
        session.commit()
        return True, resultado
    except (ValueError, SQLAlchemyError) as exc:
        session.rollback()
        log.exception("No se pudo %s", descripcion)
        st.error(f"No se pudo {descripcion}: {mensaje_error(exc)} No se guardó ningún cambio de esta operación.")
        return False, None
