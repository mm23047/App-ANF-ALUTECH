"""Versionado del esquema con PRAGMA user_version (hallazgo M-09).

Versiones:
  0  Esquema original (create_all, importes NUMERIC(18,2) guardados como REAL).
  1  change_history: columnas fiscal_period_id, account_id y lote_id (A-08).
     Tabla schema_migration con el registro de migraciones aplicadas.
  2  Importes como entero de centavos (M-02). Cada fila se convierte con
     Decimal y se verifica; cualquier valor ambiguo detiene la migracion.
  3  Cierre de ejercicios (M-05): fiscal_period.fecha_cierre y disparadores
     que impiden modificar los importes de un ejercicio CERRADO.
  4  Trazabilidad de datos originales (adaptación Alutech): account.grupo_analisis
     y tablas fuente_importe y dato_complementario, protegidas por el cierre.
     No modifica ninguna fila existente.

Cada paso es idempotente (comprueba la forma actual antes de cambiarla) y
todos se ejecutan en una sola transaccion. Antes de migrar una BD con datos se
crea una copia verificada en <carpeta de la BD>/backups/.

Uso por linea de comandos (verificacion manual):
    python -m database.migrations RUTA.db
"""
from __future__ import annotations

import datetime
import sqlite3
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

VERSION_ACTUAL = 4

IMPORTE_MAXIMO = Decimal("9999999999999999.99")
DIGITOS_FLOAT_SEGUROS = 15


class MigracionError(RuntimeError):
    """La migracion no se aplico; la BD queda como estaba."""


class EsquemaIncompatible(MigracionError):
    """La BD fue creada por una version mas reciente de la aplicacion."""


# DDL de la version 2 (igual al que genera create_all con los modelos).
_DDL_MONETARIAS = {
    "balance_entry": """CREATE TABLE balance_entry (
	id INTEGER NOT NULL,
	fiscal_period_id INTEGER NOT NULL,
	account_id INTEGER NOT NULL,
	valor BIGINT NOT NULL,
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_balance_period_account UNIQUE (fiscal_period_id, account_id),
	FOREIGN KEY(fiscal_period_id) REFERENCES fiscal_period (id) ON DELETE CASCADE,
	FOREIGN KEY(account_id) REFERENCES account (id) ON DELETE RESTRICT
)""",
    "income_entry": """CREATE TABLE income_entry (
	id INTEGER NOT NULL,
	fiscal_period_id INTEGER NOT NULL,
	account_id INTEGER NOT NULL,
	valor BIGINT NOT NULL,
	created_at DATETIME NOT NULL,
	updated_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_income_period_account UNIQUE (fiscal_period_id, account_id),
	FOREIGN KEY(fiscal_period_id) REFERENCES fiscal_period (id) ON DELETE CASCADE,
	FOREIGN KEY(account_id) REFERENCES account (id) ON DELETE RESTRICT
)""",
    "initial_balance": """CREATE TABLE initial_balance (
	id INTEGER NOT NULL,
	fiscal_period_id INTEGER NOT NULL,
	account_id INTEGER NOT NULL,
	valor BIGINT NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_initial_period_account UNIQUE (fiscal_period_id, account_id),
	FOREIGN KEY(fiscal_period_id) REFERENCES fiscal_period (id) ON DELETE CASCADE,
	FOREIGN KEY(account_id) REFERENCES account (id) ON DELETE RESTRICT
)""",
}

_TABLAS_PROTEGIDAS_POR_CIERRE = ("balance_entry", "income_entry", "initial_balance", "statement_status")


def _conectar(ruta: Path) -> sqlite3.Connection:
    con = sqlite3.connect(ruta, isolation_level=None)  # transacciones explicitas
    return con


def version_esquema(ruta: Path) -> int:
    con = sqlite3.connect(f"{Path(ruta).resolve().as_uri()}?mode=ro", uri=True)
    try:
        return con.execute("PRAGMA user_version").fetchone()[0]
    finally:
        con.close()


def _columnas(con: sqlite3.Connection, tabla: str) -> dict[str, str]:
    return {r[1]: r[2] for r in con.execute(f'PRAGMA table_info("{tabla}")')}


def _tabla_existe(con: sqlite3.Connection, tabla: str) -> bool:
    return con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (tabla,)).fetchone() is not None


def _tiene_datos(con: sqlite3.Connection) -> bool:
    for tabla in ("company", "fiscal_period", "account", "change_history"):
        if _tabla_existe(con, tabla) and con.execute(f'SELECT 1 FROM "{tabla}" LIMIT 1').fetchone():
            return True
    return False


def valor_a_centavos(valor, *, contexto: str = "") -> int:
    """Convierte un importe almacenado (REAL, INTEGER o TEXT de la version 0)
    a centavos sin redondear. Lanza MigracionError si el valor es ambiguo:
    NULL, no numerico, mas de dos decimales, demasiados digitos para un REAL
    o fuera de NUMERIC(18,2)."""
    prefijo = f"{contexto}: " if contexto else ""
    if valor is None or isinstance(valor, bool):
        raise MigracionError(f"{prefijo}importe nulo o no numérico ({valor!r}).")
    if isinstance(valor, int):
        decimal = Decimal(valor)
    elif isinstance(valor, float):
        decimal = Decimal(repr(valor))
    elif isinstance(valor, str):
        try:
            decimal = Decimal(valor.strip())
        except InvalidOperation:
            raise MigracionError(f"{prefijo}importe de texto no numérico ({valor!r}).") from None
    else:
        raise MigracionError(f"{prefijo}tipo de importe no soportado ({type(valor).__name__}: {valor!r}).")
    if not decimal.is_finite():
        raise MigracionError(f"{prefijo}importe no finito ({valor!r}).")
    if abs(decimal) > IMPORTE_MAXIMO:
        raise MigracionError(f"{prefijo}importe fuera de rango ({decimal}).")
    centavos = decimal.scaleb(2)
    if centavos != centavos.to_integral_value():
        raise MigracionError(
            f"{prefijo}el importe {decimal} tiene más de dos decimales; convertirlo exigiría redondear."
        )
    if isinstance(valor, float) and len(str(abs(int(centavos)))) > DIGITOS_FLOAT_SEGUROS:
        raise MigracionError(
            f"{prefijo}el importe REAL {valor!r} tiene más de {DIGITOS_FLOAT_SEGUROS} dígitos significativos; "
            "no se puede asegurar que conserve los centavos originales."
        )
    return int(centavos)


def _decimal_original(valor) -> Decimal:
    """Valor de la version 0 tal como lo leeria una persona (repr de un REAL)."""
    return Decimal(repr(valor)) if isinstance(valor, float) else Decimal(str(valor))


# --------------------------------------------------------------------------- pasos

def _paso_1_historial(con: sqlite3.Connection) -> str:
    con.execute(
        """CREATE TABLE IF NOT EXISTS schema_migration (
            version INTEGER NOT NULL PRIMARY KEY,
            descripcion VARCHAR(200) NOT NULL,
            aplicada_en DATETIME NOT NULL
        )"""
    )
    columnas = _columnas(con, "change_history")
    agregadas = []
    for nombre, tipo in (("fiscal_period_id", "INTEGER"), ("account_id", "INTEGER"), ("lote_id", "VARCHAR(36)")):
        if nombre not in columnas:
            con.execute(f"ALTER TABLE change_history ADD COLUMN {nombre} {tipo}")
            agregadas.append(nombre)
    return f"change_history: columnas agregadas {agregadas}" if agregadas else "change_history ya tenía las columnas"


def _paso_2_centavos(con: sqlite3.Connection) -> str:
    resumen = []
    for tabla, ddl in _DDL_MONETARIAS.items():
        columnas = _columnas(con, tabla)
        if columnas.get("valor", "").upper() == "BIGINT":
            no_enteros = con.execute(f"SELECT COUNT(*) FROM {tabla} WHERE typeof(valor) <> 'integer'").fetchone()[0]
            if no_enteros:
                raise MigracionError(f"{tabla}: {no_enteros} importes no son enteros en una tabla de centavos.")
            resumen.append(f"{tabla}: ya en centavos")
            continue

        nombres = list(columnas)
        lista = ", ".join(nombres)
        indice_valor = nombres.index("valor")
        originales = con.execute(f"SELECT {lista} FROM {tabla} ORDER BY id").fetchall()
        convertidas = []
        for fila in originales:
            centavos = valor_a_centavos(fila[indice_valor], contexto=f"{tabla} id={fila[0]}")
            convertidas.append(fila[:indice_valor] + (centavos,) + fila[indice_valor + 1:])

        respaldo = f"{tabla}__v1"
        con.execute(f"ALTER TABLE {tabla} RENAME TO {respaldo}")
        con.execute(ddl)
        marcadores = ", ".join("?" for _ in nombres)
        con.executemany(f"INSERT INTO {tabla} ({lista}) VALUES ({marcadores})", convertidas)

        # Verificacion fila por fila contra la tabla original.
        nuevas = con.execute(f"SELECT {lista} FROM {tabla} ORDER BY id").fetchall()
        if len(nuevas) != len(originales):
            raise MigracionError(f"{tabla}: {len(originales)} filas antes y {len(nuevas)} después.")
        for antes, despues in zip(originales, nuevas):
            iguales = all(a == d for i, (a, d) in enumerate(zip(antes, despues)) if i != indice_valor)
            centavos = despues[indice_valor]
            if not iguales or not isinstance(centavos, int):
                raise MigracionError(f"{tabla} id={antes[0]}: la fila migrada no coincide con la original.")
            original = antes[indice_valor]
            migrado = Decimal(centavos).scaleb(-2)
            if migrado != _decimal_original(original) or (isinstance(original, float) and float(migrado) != original):
                raise MigracionError(f"{tabla} id={antes[0]}: importe {original!r} distinto tras migrar ({migrado}).")
        con.execute(f"DROP TABLE {respaldo}")
        resumen.append(f"{tabla}: {len(nuevas)} filas convertidas a centavos y verificadas")
    return "; ".join(resumen)


def _paso_3_cierre(con: sqlite3.Connection) -> str:
    resumen = []
    if "fecha_cierre" not in _columnas(con, "fiscal_period"):
        con.execute("ALTER TABLE fiscal_period ADD COLUMN fecha_cierre DATETIME")
        resumen.append("fiscal_period.fecha_cierre agregada")
    for tabla in _TABLAS_PROTEGIDAS_POR_CIERRE:
        cerrado_new = f"(SELECT estado FROM fiscal_period WHERE id = NEW.fiscal_period_id) = 'CERRADO'"
        cerrado_old = f"(SELECT estado FROM fiscal_period WHERE id = OLD.fiscal_period_id) = 'CERRADO'"
        for evento, condicion in (
            ("INSERT", cerrado_new),
            ("UPDATE", f"{cerrado_new} OR {cerrado_old}"),
            ("DELETE", cerrado_old),
        ):
            con.execute(
                f"""CREATE TRIGGER IF NOT EXISTS trg_{tabla}_cerrado_{evento.lower()}
                BEFORE {evento} ON {tabla} WHEN {condicion}
                BEGIN SELECT RAISE(ABORT, 'EJERCICIO_CERRADO'); END"""
            )
    con.execute(
        """CREATE TRIGGER IF NOT EXISTS trg_fiscal_period_cerrado_delete
        BEFORE DELETE ON fiscal_period WHEN OLD.estado = 'CERRADO'
        BEGIN SELECT RAISE(ABORT, 'EJERCICIO_CERRADO'); END"""
    )
    resumen.append("disparadores de ejercicio cerrado verificados")
    return "; ".join(resumen)


# DDL de la version 4 (igual al que genera create_all con los modelos).
_DDL_TRAZABILIDAD = {
    "fuente_importe": """CREATE TABLE IF NOT EXISTS fuente_importe (
	id INTEGER NOT NULL,
	fiscal_period_id INTEGER NOT NULL,
	account_id INTEGER NOT NULL,
	tipo VARCHAR(20) NOT NULL,
	documento VARCHAR(300) NOT NULL,
	pagina INTEGER,
	estado_financiero VARCHAR(200) NOT NULL,
	nombre_original VARCHAR(300) NOT NULL,
	importe_documento VARCHAR(40) NOT NULL,
	valor_registrado BIGINT NOT NULL,
	fecha_carga DATETIME NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_fuente_importe UNIQUE (fiscal_period_id, account_id, tipo),
	FOREIGN KEY(fiscal_period_id) REFERENCES fiscal_period (id) ON DELETE CASCADE,
	FOREIGN KEY(account_id) REFERENCES account (id) ON DELETE RESTRICT
)""",
    "dato_complementario": """CREATE TABLE IF NOT EXISTS dato_complementario (
	id INTEGER NOT NULL,
	fiscal_period_id INTEGER NOT NULL,
	clave VARCHAR(60) NOT NULL,
	tipo VARCHAR(20) NOT NULL,
	valor BIGINT NOT NULL,
	documento VARCHAR(300) NOT NULL,
	pagina INTEGER,
	estado_financiero VARCHAR(200) NOT NULL,
	nombre_original VARCHAR(300) NOT NULL,
	importe_documento VARCHAR(40) NOT NULL,
	fecha_carga DATETIME NOT NULL,
	PRIMARY KEY (id),
	CONSTRAINT uq_dato_complementario UNIQUE (fiscal_period_id, clave),
	FOREIGN KEY(fiscal_period_id) REFERENCES fiscal_period (id) ON DELETE CASCADE
)""",
}


def _disparadores_cierre(con: sqlite3.Connection, tabla: str) -> None:
    cerrado_new = "(SELECT estado FROM fiscal_period WHERE id = NEW.fiscal_period_id) = 'CERRADO'"
    cerrado_old = "(SELECT estado FROM fiscal_period WHERE id = OLD.fiscal_period_id) = 'CERRADO'"
    for evento, condicion in (
        ("INSERT", cerrado_new),
        ("UPDATE", f"{cerrado_new} OR {cerrado_old}"),
        ("DELETE", cerrado_old),
    ):
        con.execute(
            f"""CREATE TRIGGER IF NOT EXISTS trg_{tabla}_cerrado_{evento.lower()}
            BEFORE {evento} ON {tabla} WHEN {condicion}
            BEGIN SELECT RAISE(ABORT, 'EJERCICIO_CERRADO'); END"""
        )


def _paso_4_trazabilidad(con: sqlite3.Connection) -> str:
    resumen = []
    if "grupo_analisis" not in _columnas(con, "account"):
        con.execute("ALTER TABLE account ADD COLUMN grupo_analisis VARCHAR(40)")
        resumen.append("account.grupo_analisis agregada")
    for tabla, ddl in _DDL_TRAZABILIDAD.items():
        existia = _tabla_existe(con, tabla)
        con.execute(ddl)
        _disparadores_cierre(con, tabla)
        resumen.append(f"{tabla} {'ya existía' if existia else 'creada'}")
    return "; ".join(resumen)


PASOS = (
    (1, "Historial: ejercicio, cuenta y lote", _paso_1_historial),
    (2, "Importes en centavos enteros", _paso_2_centavos),
    (3, "Cierre de ejercicios", _paso_3_cierre),
    (4, "Trazabilidad de datos originales", _paso_4_trazabilidad),
)


def _crear_esquema_nuevo(ruta: Path) -> None:
    from sqlalchemy import create_engine

    from database.models import Base

    engine = create_engine(f"sqlite:///{ruta}", future=True)
    try:
        Base.metadata.create_all(engine)
    finally:
        engine.dispose()


def migrar(ruta: Path, *, respaldar: bool = True) -> list[str]:
    """Lleva la BD de `ruta` a VERSION_ACTUAL. Devuelve el registro de lo
    aplicado (vacio si ya estaba al dia). Una BD inexistente o vacia se crea
    directamente en la version actual."""
    from database.backup_utils import crear_respaldo, marca_tiempo

    ruta = Path(ruta)
    con = _conectar(ruta)
    try:
        version = con.execute("PRAGMA user_version").fetchone()[0]
        if version > VERSION_ACTUAL:
            raise EsquemaIncompatible(
                f"La base de datos usa el esquema {version}, más reciente que el de esta aplicación ({VERSION_ACTUAL})."
            )
        if version == VERSION_ACTUAL:
            return []
        nueva = not _tabla_existe(con, "company")
        con_datos = _tiene_datos(con)
    finally:
        con.close()

    registro = []
    if nueva:
        _crear_esquema_nuevo(ruta)
        registro.append("Esquema creado con los modelos actuales")
    elif respaldar and con_datos:
        destino = ruta.parent / "backups" / f"{ruta.stem}_pre_migracion_v{version}_{marca_tiempo()}.db"
        crear_respaldo(ruta, destino)
        registro.append(f"Copia previa verificada: {destino}")

    # Todos los pasos en UNA transaccion: si cualquiera se detiene (p. ej. por
    # un importe ambiguo), la BD queda exactamente como estaba.
    con = _conectar(ruta)
    try:
        con.execute("BEGIN IMMEDIATE")
        try:
            aplicada_en = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None).isoformat(sep=" ")
            for numero, descripcion, paso in PASOS:
                if numero <= version:
                    continue
                detalle = paso(con)
                violaciones = con.execute("PRAGMA foreign_key_check").fetchall()
                if violaciones:
                    raise MigracionError(f"Violaciones de clave foránea tras el paso {numero}: {violaciones[:5]}")
                con.execute(
                    "INSERT OR REPLACE INTO schema_migration (version, descripcion, aplicada_en) VALUES (?, ?, ?)",
                    (numero, descripcion, aplicada_en),
                )
                con.execute(f"PRAGMA user_version = {numero}")
                registro.append(f"v{numero} {descripcion}: {detalle}")
            con.execute("COMMIT")
        except BaseException:
            con.execute("ROLLBACK")
            raise
        integridad = con.execute("PRAGMA integrity_check").fetchall()
        if integridad != [("ok",)]:
            raise MigracionError(f"integrity_check tras migrar: {integridad[:3]}")
    finally:
        con.close()
    return registro


# --------------------------------------------------------------------------- verificacion

_TABLAS_MONETARIAS = tuple(_DDL_MONETARIAS)
_COLUMNAS_NUEVAS = {
    "change_history": {"fiscal_period_id", "account_id", "lote_id"},
    "fiscal_period": {"fecha_cierre"},
    "account": {"grupo_analisis"},
}


def comparar_bd(antes: Path, despues: Path) -> tuple[list[str], list[tuple]]:
    """Compara una BD antes y despues de migrar. Devuelve (diferencias,
    importes), donde importes es [(tabla, id, valor_antes, valor_despues)].
    Ninguna fila puede desaparecer ni cambiar; los importes se comparan
    como Decimal y las columnas agregadas por la migracion deben ser NULL
    en las filas existentes."""
    a = sqlite3.connect(f"{Path(antes).resolve().as_uri()}?mode=ro", uri=True)
    d = sqlite3.connect(f"{Path(despues).resolve().as_uri()}?mode=ro", uri=True)
    diferencias: list[str] = []
    importes: list[tuple] = []
    try:
        tablas = [r[0] for r in a.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        for tabla in tablas:
            cols_a = list(_columnas(a, tabla))
            cols_d = _columnas(d, tabla)
            if not cols_d:
                diferencias.append(f"{tabla}: la tabla desapareció")
                continue
            faltantes = [c for c in cols_a if c not in cols_d]
            if faltantes:
                diferencias.append(f"{tabla}: desaparecieron columnas {faltantes}")
                continue
            nuevas = [c for c in cols_d if c not in cols_a]
            inesperadas = set(nuevas) - _COLUMNAS_NUEVAS.get(tabla, set())
            if inesperadas:
                diferencias.append(f"{tabla}: columnas inesperadas {sorted(inesperadas)}")
            filas_a = a.execute(f'SELECT {", ".join(cols_a)} FROM "{tabla}" ORDER BY id').fetchall()
            filas_d = d.execute(f'SELECT {", ".join(cols_a + nuevas)} FROM "{tabla}" ORDER BY id').fetchall()
            if len(filas_a) != len(filas_d):
                diferencias.append(f"{tabla}: {len(filas_a)} filas antes y {len(filas_d)} después")
                continue
            for fa, fd in zip(filas_a, filas_d):
                for i, col in enumerate(cols_a):
                    va, vd = fa[i], fd[i]
                    if tabla in _TABLAS_MONETARIAS and col == "valor":
                        dec_a = _decimal_original(va)
                        dec_d = Decimal(vd).scaleb(-2) if isinstance(vd, int) and cols_d["valor"].upper() == "BIGINT" else Decimal(str(vd))
                        importes.append((tabla, fa[0], va, dec_d))
                        if dec_a != dec_d:
                            diferencias.append(f"{tabla} id={fa[0]}: importe {va!r} -> {dec_d}")
                    elif va != vd:
                        diferencias.append(f"{tabla} id={fa[0]} {col}: {va!r} -> {vd!r}")
                for j, col in enumerate(nuevas):
                    if fd[len(cols_a) + j] is not None:
                        diferencias.append(f"{tabla} id={fa[0]}: columna nueva {col} con valor {fd[len(cols_a) + j]!r}")
    finally:
        a.close()
        d.close()
    return diferencias, importes


def _main(argv: list[str]) -> int:
    from database.backup_utils import sha256_archivo

    if len(argv) != 1:
        print(__doc__)
        return 2
    ruta = Path(argv[0])
    print(f"BD: {ruta}")
    print(f"SHA-256 antes:   {sha256_archivo(ruta)}")
    print(f"Versión antes:   {version_esquema(ruta)}")
    registro = migrar(ruta)
    for linea in registro:
        print(f"  - {linea}")
    print(f"Versión después: {version_esquema(ruta)}")
    print(f"SHA-256 después: {sha256_archivo(ruta)}")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
