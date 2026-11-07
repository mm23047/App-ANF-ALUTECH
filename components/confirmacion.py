"""Confirmacion explicita de operaciones masivas (hallazgo M-10, fase 4.2).

Flujo en dos pasos:
1. La pantalla valida los cambios y llama a `proponer`: no escribe nada.
   Guarda en st.session_state la operacion pendiente (alcance, importes
   exactos a escribir y valores actuales de esas cuentas) con un token nuevo.
2. `mostrar` presenta el alcance con "Confirmar y guardar" y "Cancelar".
   Al confirmar, la operacion se retira de session_state ANTES de devolverse
   (un solo uso); el llamador comprueba con `vigente` que los datos no
   cambiaron y la ejecuta en una sola transaccion (ejecutar_escritura).

Protecciones:
- Recarga del navegador: Streamlit crea una sesion nueva y la operacion
  pendiente se pierde; nada se escribe sin una confirmacion nueva.
- Navegacion: app.py llama a `descartar_al_navegar` al cambiar de pagina;
  cambiar de ejercicio cambia el contexto y `mostrar` la descarta.
- Repeticion (doble clic, reenvio): el token se consume al confirmar; un
  segundo clic ya no encuentra la operacion.
- Cancelar descarta la operacion sin tocar la base de datos.
- Restauracion o sustitucion de la base desde otra pestana o proceso
  (hallazgo O-1, fase 7): la operacion guarda `EstadoBase` (identidad del
  archivo SQLite y ultimo registro del historial) al prepararse; al
  confirmar, `misma_base` lo compara con la base real, dentro de la misma
  transaccion de escritura. No depende de st.session_state, que es propio
  de cada pestana.
"""
from __future__ import annotations

import os
import uuid
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Hashable

import pandas as pd
import streamlit as st
from sqlalchemy import select
from sqlalchemy.orm import Session

from components.money import format_money
from database.models import ChangeHistory

_PENDIENTES = "_operaciones_pendientes"
_PAGINA = "_pagina_operaciones_pendientes"

ETIQUETA_CONFIRMAR = "Confirmar y guardar"
ETIQUETA_CANCELAR = "Cancelar"


@dataclass
class Cambio:
    account_id: int
    cuenta: str  # "codigo — nombre", solo para mostrar
    previo: Decimal | None
    nuevo: Decimal


@dataclass(frozen=True)
class EstadoBase:
    """Identifica la base de datos sobre la que se preparo una operacion.

    - archivo: (volumen, id de archivo, creacion) del .db. Una restauracion
      reemplaza el archivo (os.replace) y cambia el id; las escrituras
      normales de SQLite (modo journal DELETE) no lo cambian.
    - ancla: ultimo registro del historial de cambios. El historial solo
      crece: las escrituras normales lo conservan, y si otra base sustituye
      el contenido (aunque sea en el mismo archivo) ese registro falta o
      difiere.
    """

    archivo: tuple
    ancla: tuple | None


_COLUMNAS_ANCLA = (ChangeHistory.id, ChangeHistory.tabla_afectada, ChangeHistory.registro_id, ChangeHistory.campo,
                   ChangeHistory.fecha, ChangeHistory.lote_id)


def _identidad_archivo(session: Session) -> tuple:
    estado = os.stat(session.get_bind().url.database)
    # st_ctime es la creacion solo en Windows; en Linux es el ultimo cambio del inodo y varia con cada escritura.
    creacion = getattr(estado, "st_birthtime_ns", estado.st_ctime_ns if os.name == "nt" else None)
    return (estado.st_dev, estado.st_ino, creacion)


def estado_base(session: Session) -> EstadoBase:
    fila = session.execute(select(*_COLUMNAS_ANCLA).order_by(ChangeHistory.id.desc()).limit(1)).first()
    return EstadoBase(_identidad_archivo(session), tuple(fila) if fila else None)


def misma_base(base: EstadoBase | None, session: Session) -> bool:
    """True si la base actual es la misma sobre la que se preparo `base`."""
    if base is None or _identidad_archivo(session) != base.archivo:
        return False
    if base.ancla is None:
        return True
    fila = session.execute(select(*_COLUMNAS_ANCLA).where(ChangeHistory.id == base.ancla[0])).first()
    return fila is not None and tuple(fila) == base.ancla


MENSAJE_BASE_CAMBIADA = (
    "la base de datos cambió después de preparar la confirmación (por ejemplo, se restauró una copia de "
    "seguridad desde otra pestaña). Revise los datos y vuelva a pulsar Guardar para preparar una confirmación nueva."
)


class BaseCambiada(ValueError):
    """La operacion confirmada se preparo sobre otra base de datos."""

    def __init__(self) -> None:
        super().__init__(MENSAJE_BASE_CAMBIADA)


def comprobar_base(op: OperacionPendiente, session: Session) -> None:
    """Lanza BaseCambiada si la base no es la de la propuesta. Se llama dentro
    de la transaccion de escritura: ejecutar_escritura revierte y lo informa."""
    if not misma_base(op.base, session):
        raise BaseCambiada()


@dataclass
class OperacionPendiente:
    pantalla: str
    contexto: Hashable
    token: str
    resumen: str
    cambios: list[Cambio]
    avisos: list[str] = field(default_factory=list)
    extra: Any = None
    base: EstadoBase | None = None


def _pendientes() -> dict[str, OperacionPendiente]:
    return st.session_state.setdefault(_PENDIENTES, {})


def resumen_cambios(cambios: list[Cambio], anio: int, estado: str) -> str:
    nuevos = sum(1 for c in cambios if c.previo is None)
    return (
        f"Se modificarán {len(cambios)} valor(es) de {estado} en el ejercicio {anio}: "
        f"{nuevos} nuevo(s) y {len(cambios) - nuevos} modificado(s)."
    )


def proponer(pantalla: str, contexto: Hashable, *, resumen: str, cambios: list[Cambio],
             avisos: list[str] | None = None, extra: Any = None, base: EstadoBase | None = None) -> OperacionPendiente:
    """Registra la operacion para confirmarla; reemplaza a la anterior de la pantalla.
    `base` (estado_base) identifica la base sobre la que se prepara."""
    op = OperacionPendiente(pantalla, contexto, uuid.uuid4().hex, resumen, list(cambios), list(avisos or []), extra,
                            base)
    _pendientes()[pantalla] = op
    return op


def pendiente(pantalla: str) -> OperacionPendiente | None:
    return _pendientes().get(pantalla)


def descartar(pantalla: str) -> None:
    _pendientes().pop(pantalla, None)


def descartar_al_navegar(pagina: str) -> None:
    """Elimina todas las operaciones pendientes si cambio la pagina."""
    if st.session_state.get(_PAGINA) != pagina:
        _pendientes().clear()
        st.session_state[_PAGINA] = pagina


def vigente(op: OperacionPendiente, valores_actuales: dict[int, Decimal]) -> bool:
    """True si las cuentas afectadas conservan el valor mostrado en la confirmacion."""
    return all(valores_actuales.get(c.account_id) == c.previo for c in op.cambios)


def tabla_alcance(cambios: list[Cambio]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Cuenta": c.cuenta,
                "Valor actual": "Sin dato" if c.previo is None else format_money(c.previo),
                "Valor nuevo": format_money(c.nuevo),
            }
            for c in cambios
        ]
    )


def mostrar(pantalla: str, contexto: Hashable) -> OperacionPendiente | None:
    """Muestra la operacion pendiente de la pantalla. Devuelve la operacion
    (ya retirada) solo en la ejecucion en que se pulsa "Confirmar y guardar"."""
    op = pendiente(pantalla)
    if op is None:
        return None
    if op.contexto != contexto:
        descartar(pantalla)
        return None
    marco = st.empty()
    with marco.container(border=True):
        st.warning(f"Revise antes de guardar. {op.resumen} Nada se guarda hasta que confirme.")
        st.dataframe(tabla_alcance(op.cambios), hide_index=True, width="stretch")
        for aviso in op.avisos:
            st.caption(aviso)
        col_confirmar, col_cancelar = st.columns(2)
        with col_confirmar:
            confirmar = st.button(ETIQUETA_CONFIRMAR, type="primary", key=f"confirmar_{op.token}")
        with col_cancelar:
            cancelar = st.button(ETIQUETA_CANCELAR, key=f"cancelar_{op.token}")
    if cancelar:
        descartar(pantalla)
        marco.empty()
        st.info("Operación cancelada. No se modificó ningún registro.")
        return None
    if confirmar:
        descartar(pantalla)  # un solo uso, antes de escribir
        marco.empty()
        return op
    return None
