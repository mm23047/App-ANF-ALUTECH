"""Copias de seguridad y restauracion seguras (hallazgos C-01 y M-09 b).

- Las copias se crean con sqlite3.Connection.backup y se verifican con
  PRAGMA integrity_check y conteo de filas.
- Un archivo solo se restaura si es una SQLite integra con el esquema de
  esta aplicacion (tablas, columnas, version y una empresa).
- Antes de reemplazar la BD actual se guarda una copia byte a byte
  (mismo SHA-256). El reemplazo es atomico (os.replace); si algo falla
  despues, se revierte a esa copia.

Estas funciones no usan Streamlit: los mensajes de sus excepciones son
aptos para mostrarse al usuario.
"""
from __future__ import annotations

import datetime
import hashlib
import os
import shutil
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path

ENCABEZADO_SQLITE = b"SQLite format 3\x00"

# Columnas presentes desde la version 0 del esquema. Las versiones nuevas
# solo agregan columnas, asi que toda BD valida de esta aplicacion las tiene.
COLUMNAS_REQUERIDAS: dict[str, set[str]] = {
    "company": {"id", "nombre_legal", "nombre_comercial", "actividad_economica", "pais", "moneda", "anio_inicial_analisis"},
    "fiscal_period": {"id", "anio", "estado", "fecha_creacion"},
    "account": {"id", "codigo", "nombre", "categoria_principal", "subcategoria", "efecto", "naturaleza_saldo", "estado", "orden_presentacion"},
    "balance_entry": {"id", "fiscal_period_id", "account_id", "valor", "created_at", "updated_at"},
    "income_entry": {"id", "fiscal_period_id", "account_id", "valor", "created_at", "updated_at"},
    "initial_balance": {"id", "fiscal_period_id", "account_id", "valor"},
    "statement_status": {"id", "fiscal_period_id", "tipo", "estado", "fecha_actualizacion"},
    "change_history": {"id", "tabla_afectada", "registro_id", "campo", "valor_anterior", "valor_nuevo", "operacion", "fecha"},
}

TABLAS_CONTEO = ("account", "fiscal_period", "balance_entry", "income_entry", "initial_balance", "statement_status", "change_history")


class RespaldoInvalido(ValueError):
    """El archivo no es una copia valida de la BD de esta aplicacion."""


class RestauracionError(RuntimeError):
    """La restauracion no se completo. El mensaje indica el estado de la BD actual."""


@dataclass
class InfoBD:
    ruta: Path
    sha256: str
    version_esquema: int
    empresa: str
    ejercicios: list[tuple[int, str]]
    registros: dict[str, int] = field(default_factory=dict)


@dataclass
class ResultadoRestauracion:
    info: InfoBD
    respaldo_previo: Path | None


def sha256_archivo(ruta: Path) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def _conectar_lectura(ruta: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"{Path(ruta).resolve().as_uri()}?mode=ro", uri=True)


def marca_tiempo() -> str:
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")


def contar_filas(ruta: Path) -> dict[str, int]:
    con = _conectar_lectura(ruta)
    try:
        tablas = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        return {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in sorted(tablas)}
    finally:
        con.close()


def verificar_integridad(ruta: Path) -> None:
    con = _conectar_lectura(ruta)
    try:
        resultado = con.execute("PRAGMA integrity_check").fetchall()
    finally:
        con.close()
    if resultado != [("ok",)]:
        raise RespaldoInvalido(f"El archivo está dañado (integrity_check: {resultado[:3]}).")


def crear_respaldo(origen: Path, destino: Path) -> Path:
    """Copia `origen` en `destino` con la API de respaldo de SQLite y la
    verifica (integridad y mismo numero de filas por tabla)."""
    origen, destino = Path(origen), Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    if destino.exists():
        raise FileExistsError(f"Ya existe el archivo de respaldo {destino}.")
    src = _conectar_lectura(origen)
    dst = sqlite3.connect(destino)
    try:
        src.backup(dst)
    finally:
        dst.close()
        src.close()
    try:
        verificar_integridad(destino)
        if contar_filas(origen) != contar_filas(destino):
            raise RespaldoInvalido("La copia no tiene el mismo número de filas que el original.")
    except (RespaldoInvalido, sqlite3.Error):
        destino.unlink(missing_ok=True)
        raise
    return destino


def inspeccionar_bd(ruta: Path) -> InfoBD:
    """Valida que `ruta` sea una BD de esta aplicacion y resume su contenido.
    No modifica el archivo (se abre en solo lectura)."""
    from database.migrations import VERSION_ACTUAL

    ruta = Path(ruta)
    if not ruta.is_file():
        raise RespaldoInvalido(f"No existe el archivo {ruta.name}.")
    with open(ruta, "rb") as f:
        if f.read(16) != ENCABEZADO_SQLITE:
            raise RespaldoInvalido("El archivo no es una base de datos SQLite.")
    try:
        verificar_integridad(ruta)
        con = _conectar_lectura(ruta)
        try:
            version = con.execute("PRAGMA user_version").fetchone()[0]
            if version > VERSION_ACTUAL:
                raise RespaldoInvalido(
                    f"La copia usa la versión de esquema {version}, más reciente que la de esta aplicación ({VERSION_ACTUAL})."
                )
            for tabla, requeridas in COLUMNAS_REQUERIDAS.items():
                columnas = {r[1] for r in con.execute(f'PRAGMA table_info("{tabla}")')}
                if not columnas:
                    raise RespaldoInvalido(f"El archivo no pertenece a esta aplicación: falta la tabla '{tabla}'.")
                faltantes = requeridas - columnas
                if faltantes:
                    raise RespaldoInvalido(
                        f"El archivo no es compatible: a la tabla '{tabla}' le faltan las columnas {sorted(faltantes)}."
                    )
            empresas = con.execute("SELECT nombre_legal FROM company").fetchall()
            if len(empresas) != 1:
                raise RespaldoInvalido(f"La copia debe contener exactamente una empresa y contiene {len(empresas)}.")
            ejercicios = [(a, e) for a, e in con.execute("SELECT anio, estado FROM fiscal_period ORDER BY anio")]
            registros = {t: con.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in TABLAS_CONTEO}
        finally:
            con.close()
    except sqlite3.DatabaseError as exc:
        raise RespaldoInvalido(f"No se pudo leer el archivo como base de datos: {exc}.") from exc
    return InfoBD(ruta, sha256_archivo(ruta), version, empresas[0][0], ejercicios, registros)


def _reemplazar(origen: Path, destino: Path, intentos: int = 5) -> None:
    """os.replace con reintentos: en Windows falla mientras otra conexion
    (otra pestana o proceso) mantiene abierto el archivo."""
    for intento in range(intentos):
        try:
            os.replace(origen, destino)
            return
        except PermissionError:
            if intento == intentos - 1:
                raise
            time.sleep(0.3)


def restaurar(origen: Path, destino: Path, *, dir_respaldos: Path) -> ResultadoRestauracion:
    """Restaura `origen` sobre `destino`. El llamador debe haber liberado
    todas las conexiones a `destino` (database.connection.dispose_engine).

    Garantia: si se lanza una excepcion, `destino` conserva exactamente el
    mismo contenido (SHA-256) que antes de llamar a esta funcion.
    """
    from database.migrations import MigracionError, migrar

    origen, destino, dir_respaldos = Path(origen), Path(destino), Path(dir_respaldos)
    info = inspeccionar_bd(origen)  # RespaldoInvalido si no es valido

    for sufijo in ("-journal", "-wal"):
        if Path(f"{destino}{sufijo}").exists():
            raise RestauracionError(
                f"Existe el archivo {destino.name}{sufijo}: la base de datos actual tiene una transacción pendiente. "
                "Cierre la aplicación y vuelva a intentarlo. La base de datos actual no se modificó."
            )

    temporal = destino.with_name(f"{destino.name}.restaurando")
    temporal.unlink(missing_ok=True)
    respaldo_previo = None
    sha_original = sha256_archivo(destino) if destino.exists() else None
    reemplazada = False
    try:
        crear_respaldo(origen, temporal)
        migrar(temporal, respaldar=False)
        con = sqlite3.connect(temporal)
        try:
            con.execute("PRAGMA journal_mode=DELETE")
        finally:
            con.close()
        inspeccionar_bd(temporal)

        if sha_original is not None:
            respaldo_previo = dir_respaldos / f"{destino.stem}_pre_restauracion_{marca_tiempo()}.db"
            dir_respaldos.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destino, respaldo_previo)
            if sha256_archivo(respaldo_previo) != sha_original:
                raise RestauracionError("No se pudo verificar la copia previa de la base de datos actual.")

        _reemplazar(temporal, destino)
        reemplazada = True
    except PermissionError as exc:
        raise RestauracionError(
            "La base de datos actual está en uso (otra pestaña o proceso de la aplicación). Cierre las demás "
            "pestañas y vuelva a intentarlo. La base de datos actual no se modificó."
        ) from exc
    except (OSError, sqlite3.Error, MigracionError) as exc:
        raise RestauracionError(f"No se pudo preparar la restauración ({exc}). La base de datos actual no se modificó.") from exc
    finally:
        if not reemplazada:
            # Hallazgo O-2: la restauracion no ocurrio; se limpian los archivos de esta operacion.
            temporal.unlink(missing_ok=True)
            _descartar_copia_previa(respaldo_previo, destino, sha_original)

    try:
        inspeccionar_bd(destino)
    except RespaldoInvalido as exc:
        # La copia previa se conserva: es la referencia de la recuperacion.
        if respaldo_previo is not None:
            reversion = destino.with_name(f"{destino.name}.revertir")
            try:
                shutil.copy2(respaldo_previo, reversion)
                _reemplazar(reversion, destino)
            except OSError as exc_reversion:
                reversion.unlink(missing_ok=True)
                raise RestauracionError(
                    f"La restauración falló y no se pudo restablecer la base anterior ({exc_reversion}). "
                    f"Copia previa conservada: {respaldo_previo}."
                ) from exc
            if sha256_archivo(destino) != sha_original:
                raise RestauracionError(
                    f"La restauración falló y la reversión no coincide con el original. Copia previa: {respaldo_previo}."
                ) from exc
        raise RestauracionError(f"La restauración falló ({exc}); se restableció la base de datos anterior.") from exc
    return ResultadoRestauracion(info, respaldo_previo)


def _descartar_copia_previa(copia: Path | None, destino: Path, sha_original: str | None) -> None:
    """Elimina la copia previa creada por una restauracion que no llego a
    reemplazar la base (hallazgo O-2), solo si la base actual sigue
    demostrablemente intacta (mismo SHA-256 que antes). Ante cualquier duda
    (la base cambio o no se puede leer) la copia se conserva."""
    if copia is None or not copia.exists():
        return
    try:
        intacta = sha_original is not None and destino.exists() and sha256_archivo(destino) == sha_original
    except OSError:
        intacta = False
    if not intacta:
        return
    try:
        copia.unlink()
    except OSError:
        pass  # no se pudo borrar: se conserva, no es un error de la restauracion
