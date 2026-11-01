"""Funciones de acceso a datos. Todas reciben una Session abierta
(ver database.connection.session_scope) y no hacen commit por si mismas,
salvo que se indique lo contrario -- el llamador controla la transaccion.
"""
from __future__ import annotations

import datetime
import uuid
from contextlib import contextmanager
from decimal import Decimal
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from components.money import parse_anio, parse_importe

from database.enums import (
    CategoriaPrincipal,
    EfectoCuenta,
    EstadoCuenta,
    EstadoEjercicio,
    EstadoRegistro,
    NaturalezaSaldo,
    Subcategoria,
    TipoEstadoFinanciero,
    requiere_subcategoria,
    subcategorias_validas,
)
from database.models import (
    Account,
    BalanceEntry,
    ChangeHistory,
    Company,
    FiscalPeriod,
    IncomeEntry,
    InitialBalance,
    StatementStatus,
)

TipoEstado = Literal["BALANCE", "RESULTADOS"]

ENTRY_MODEL = {
    TipoEstadoFinanciero.BALANCE: BalanceEntry,
    TipoEstadoFinanciero.RESULTADOS: IncomeEntry,
}

TABLA_ENTRADA = {
    TipoEstadoFinanciero.BALANCE: "balance_entry",
    TipoEstadoFinanciero.RESULTADOS: "income_entry",
}

# Campos que determinan como participa una cuenta en los estados financieros
# (hallazgo C-03). No se pueden cambiar si la cuenta tiene importes.
CAMPOS_CLASIFICACION = ("categoria_principal", "subcategoria", "efecto")


class EjercicioCerradoError(ValueError):
    """Se intento modificar un ejercicio CERRADO."""


class CatalogoProtegidoError(ValueError):
    """Se intento reclasificar una cuenta que ya tiene importes."""


def _verificar_ejercicio_abierto(session: Session, fiscal_period_id: int) -> FiscalPeriod:
    period = session.get(FiscalPeriod, fiscal_period_id)
    if period is None:
        raise ValueError(f"El ejercicio fiscal {fiscal_period_id} no existe.")
    if period.estado == EstadoEjercicio.CERRADO:
        raise EjercicioCerradoError(
            f"El ejercicio {period.anio} está cerrado y no admite cambios. Reábralo primero si necesita modificarlo."
        )
    return period


# ---------------------------------------------------------------------------
# Company (seccion 4)
# ---------------------------------------------------------------------------

def get_company(session: Session) -> Company | None:
    return session.execute(select(Company)).scalars().first()


def save_company(
    session: Session,
    *,
    nombre_legal: str,
    nombre_comercial: str,
    actividad_economica: str,
    pais: str,
    moneda: str,
    anio_inicial_analisis: int,
) -> Company:
    company = get_company(session)
    nuevos = dict(
        nombre_legal=nombre_legal,
        nombre_comercial=nombre_comercial,
        actividad_economica=actividad_economica,
        pais=pais,
        moneda=moneda,
        anio_inicial_analisis=anio_inicial_analisis,
    )
    if company is None:
        company = Company(**nuevos)
        session.add(company)
        session.flush()
        log_change(session, "company", company.id, "creacion", None, nombre_legal, "CREAR")
        return company

    for campo, nuevo_valor in nuevos.items():
        anterior = getattr(company, campo)
        if anterior != nuevo_valor:
            log_change(session, "company", company.id, campo, str(anterior), str(nuevo_valor), "EDITAR")
            setattr(company, campo, nuevo_valor)
    return company


# ---------------------------------------------------------------------------
# Fiscal periods (seccion 3)
# ---------------------------------------------------------------------------

def list_fiscal_periods(session: Session) -> list[FiscalPeriod]:
    return list(
        session.execute(select(FiscalPeriod).order_by(FiscalPeriod.anio)).scalars()
    )


def get_fiscal_period(session: Session, anio: int) -> FiscalPeriod | None:
    return session.execute(
        select(FiscalPeriod).where(FiscalPeriod.anio == anio)
    ).scalars().first()


def get_or_create_fiscal_period(session: Session, anio: int) -> tuple[FiscalPeriod, bool]:
    anio = parse_anio(anio)
    period = get_fiscal_period(session, anio)
    if period is not None:
        return period, False
    period = FiscalPeriod(anio=anio, estado=EstadoEjercicio.ABIERTO)
    session.add(period)
    session.flush()
    log_change(session, "fiscal_period", period.id, "creacion", None, str(anio), "CREAR", fiscal_period_id=period.id)
    return period, True


def period_has_entries(session: Session, fiscal_period_id: int) -> bool:
    for model in (BalanceEntry, IncomeEntry, InitialBalance):
        if session.execute(select(model.id).where(model.fiscal_period_id == fiscal_period_id)).first() is not None:
            return True
    return False


def close_fiscal_period(session: Session, fiscal_period_id: int) -> FiscalPeriod:
    """Cierra un ejercicio: desde ese momento no admite captura, edicion,
    importacion ni borrado de importes (tambien lo impiden disparadores en
    la BD; ver database/migrations.py)."""
    period = _verificar_ejercicio_abierto(session, fiscal_period_id)
    period.estado = EstadoEjercicio.CERRADO
    period.fecha_cierre = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    log_change(session, "fiscal_period", period.id, "estado", EstadoEjercicio.ABIERTO.value, EstadoEjercicio.CERRADO.value,
               "CERRAR", fiscal_period_id=period.id)
    session.flush()
    return period


def reopen_fiscal_period(session: Session, fiscal_period_id: int) -> FiscalPeriod:
    period = session.get(FiscalPeriod, fiscal_period_id)
    if period is None:
        raise ValueError(f"El ejercicio fiscal {fiscal_period_id} no existe.")
    if period.estado != EstadoEjercicio.CERRADO:
        raise ValueError(f"El ejercicio {period.anio} no está cerrado.")
    period.estado = EstadoEjercicio.ABIERTO
    period.fecha_cierre = None
    log_change(session, "fiscal_period", period.id, "estado", EstadoEjercicio.CERRADO.value, EstadoEjercicio.ABIERTO.value,
               "REABRIR", fiscal_period_id=period.id)
    session.flush()
    return period


def delete_fiscal_period(session: Session, fiscal_period_id: int) -> int:
    """Elimina un ejercicio abierto que no tiene importes (balance,
    resultados ni saldos iniciales). Devuelve el año eliminado."""
    period = _verificar_ejercicio_abierto(session, fiscal_period_id)
    if period_has_entries(session, fiscal_period_id):
        raise ValueError(
            f"El ejercicio {period.anio} tiene importes capturados y no se puede eliminar. "
            "Solo se eliminan ejercicios vacíos."
        )
    anio = period.anio
    for status in list(period.statement_statuses):
        log_change(session, "statement_status", status.id, f"estado_{status.tipo.value}", status.estado.value, None,
                   "ELIMINAR", fiscal_period_id=period.id)
    log_change(session, "fiscal_period", period.id, "creacion", str(anio), None, "ELIMINAR", fiscal_period_id=period.id)
    session.delete(period)
    session.flush()
    return anio


# ---------------------------------------------------------------------------
# Accounts (seccion 5)
# ---------------------------------------------------------------------------

def list_accounts(
    session: Session,
    categoria: CategoriaPrincipal | None = None,
    solo_activas: bool = False,
) -> list[Account]:
    stmt = select(Account)
    if categoria is not None:
        stmt = stmt.where(Account.categoria_principal == categoria)
    if solo_activas:
        stmt = stmt.where(Account.estado == EstadoCuenta.ACTIVA)
    stmt = stmt.order_by(Account.orden_presentacion, Account.codigo)
    return list(session.execute(stmt).scalars())


def get_account(session: Session, account_id: int) -> Account | None:
    return session.get(Account, account_id)


def get_account_by_codigo(session: Session, codigo: str) -> Account | None:
    return session.execute(
        select(Account).where(Account.codigo == codigo)
    ).scalars().first()


def validar_clasificacion(
    categoria: CategoriaPrincipal,
    subcategoria: Subcategoria | None,
    efecto: EfectoCuenta | None,
) -> None:
    if requiere_subcategoria(categoria):
        if subcategoria is None:
            raise ValueError(f"La categoria {categoria} requiere una subcategoria.")
        if subcategoria not in subcategorias_validas(categoria):
            raise ValueError(
                f"Subcategoria {subcategoria} no es valida para la categoria {categoria}."
            )
    elif subcategoria is not None:
        raise ValueError(f"La categoria {categoria} no admite subcategoria.")

    requiere_efecto = (
        subcategoria == Subcategoria.OTROS_OPERATIVOS
        or categoria == CategoriaPrincipal.OTROS_INGRESOS_GASTOS
    )
    if requiere_efecto and efecto is None:
        raise ValueError(
            "Esta clasificacion requiere indicar efecto (INGRESO o GASTO) para saber "
            "si suma o resta en el subtotal correspondiente."
        )
    if not requiere_efecto and efecto is not None:
        raise ValueError(
            "El campo 'efecto' solo aplica a 'Otros operativos' (gastos operativos) "
            "y a 'Otros ingresos y gastos' no operativos."
        )


def create_account(
    session: Session,
    *,
    codigo: str,
    nombre: str,
    categoria_principal: CategoriaPrincipal,
    subcategoria: Subcategoria | None,
    naturaleza_saldo: NaturalezaSaldo,
    efecto: EfectoCuenta | None = None,
    orden_presentacion: int = 0,
) -> Account:
    if get_account_by_codigo(session, codigo) is not None:
        raise ValueError(f"Ya existe una cuenta con el codigo {codigo}.")
    validar_clasificacion(categoria_principal, subcategoria, efecto)

    account = Account(
        codigo=codigo,
        nombre=nombre,
        categoria_principal=categoria_principal,
        subcategoria=subcategoria,
        efecto=efecto,
        naturaleza_saldo=naturaleza_saldo,
        estado=EstadoCuenta.ACTIVA,
        orden_presentacion=orden_presentacion,
    )
    session.add(account)
    session.flush()
    log_change(session, "account", account.id, "creacion", None, f"{codigo} - {nombre}", "CREAR", account_id=account.id)
    return account


def account_has_movements(session: Session, account_id: int) -> bool:
    for model in (BalanceEntry, IncomeEntry, InitialBalance):
        existe = session.execute(
            select(model.id).where(model.account_id == account_id)
        ).first()
        if existe is not None:
            return True
    return False


def update_account(session: Session, account_id: int, **cambios) -> Account:
    account = get_account(session, account_id)
    if account is None:
        raise ValueError(f"Cuenta {account_id} no encontrada.")

    reclasificados = [c for c in CAMPOS_CLASIFICACION if c in cambios and cambios[c] != getattr(account, c)]
    if reclasificados and account_has_movements(session, account_id):
        raise CatalogoProtegidoError(
            f"La cuenta {account.codigo} — {account.nombre} tiene importes capturados: no se puede cambiar "
            f"{', '.join(reclasificados)} porque alteraría los estados de ejercicios anteriores. Para reclasificar, "
            "cree una cuenta nueva con la clasificación correcta y desactive esta."
        )

    categoria = cambios.get("categoria_principal", account.categoria_principal)
    subcategoria = cambios.get("subcategoria", account.subcategoria)
    efecto = cambios.get("efecto", account.efecto)
    validar_clasificacion(categoria, subcategoria, efecto)

    nuevo_codigo = cambios.get("codigo")
    if nuevo_codigo and nuevo_codigo != account.codigo:
        existente = get_account_by_codigo(session, nuevo_codigo)
        if existente is not None and existente.id != account_id:
            raise ValueError(f"Ya existe una cuenta con el codigo {nuevo_codigo}.")

    for campo, nuevo_valor in cambios.items():
        anterior = getattr(account, campo)
        if anterior != nuevo_valor:
            log_change(session, "account", account.id, campo, _texto(anterior), _texto(nuevo_valor), "EDITAR",
                       account_id=account.id)
            setattr(account, campo, nuevo_valor)
    return account


def deactivate_account(session: Session, account_id: int) -> Account:
    account = get_account(session, account_id)
    if account is None:
        raise ValueError(f"Cuenta {account_id} no encontrada.")
    if account.estado != EstadoCuenta.INACTIVA:
        log_change(session, "account", account.id, "estado", account.estado.value, EstadoCuenta.INACTIVA.value, "DESACTIVAR",
                   account_id=account.id)
        account.estado = EstadoCuenta.INACTIVA
    return account


# ---------------------------------------------------------------------------
# Balance / Income entries (seccion 6)
# ---------------------------------------------------------------------------

def get_entries_map(
    session: Session, fiscal_period_id: int, tipo: TipoEstadoFinanciero
) -> dict[int, Decimal]:
    model = ENTRY_MODEL[tipo]
    rows = session.execute(
        select(model.account_id, model.valor).where(model.fiscal_period_id == fiscal_period_id)
    ).all()
    return {account_id: valor for account_id, valor in rows}


def list_entries(
    session: Session, fiscal_period_id: int, tipo: TipoEstadoFinanciero
) -> list[tuple[Account, Decimal]]:
    model = ENTRY_MODEL[tipo]
    rows = session.execute(
        select(Account, model.valor)
        .join(model, model.account_id == Account.id)
        .where(model.fiscal_period_id == fiscal_period_id)
        .order_by(Account.orden_presentacion, Account.codigo)
    ).all()
    return [(account, valor) for account, valor in rows]


def _upsert_importe(session: Session, model, tabla: str, *, fiscal_period_id: int, account_id: int, valor) -> str | None:
    """Crea o actualiza un importe. El valor se valida con parse_importe
    (sin redondeo). Devuelve "CREAR", "EDITAR" o None si no cambio."""
    valor = parse_importe(valor)
    _verificar_ejercicio_abierto(session, fiscal_period_id)
    existente = session.execute(
        select(model).where(model.fiscal_period_id == fiscal_period_id, model.account_id == account_id)
    ).scalars().first()
    if existente is None:
        entrada = model(fiscal_period_id=fiscal_period_id, account_id=account_id, valor=valor)
        session.add(entrada)
        session.flush()
        log_change(session, tabla, entrada.id, "valor", None, str(valor), "CREAR",
                   fiscal_period_id=fiscal_period_id, account_id=account_id)
        return "CREAR"
    if existente.valor != valor:
        log_change(session, tabla, existente.id, "valor", str(existente.valor), str(valor), "EDITAR",
                   fiscal_period_id=fiscal_period_id, account_id=account_id)
        existente.valor = valor
        return "EDITAR"
    return None


def _delete_importe(session: Session, model, tabla: str, *, fiscal_period_id: int, account_id: int) -> bool:
    _verificar_ejercicio_abierto(session, fiscal_period_id)
    existente = session.execute(
        select(model).where(model.fiscal_period_id == fiscal_period_id, model.account_id == account_id)
    ).scalars().first()
    if existente is None:
        return False
    log_change(session, tabla, existente.id, "valor", str(existente.valor), None, "ELIMINAR",
               fiscal_period_id=fiscal_period_id, account_id=account_id)
    session.delete(existente)
    session.flush()
    return True


def upsert_entry(
    session: Session,
    *,
    fiscal_period_id: int,
    account_id: int,
    valor,
    tipo: TipoEstadoFinanciero,
) -> str | None:
    return _upsert_importe(session, ENTRY_MODEL[tipo], TABLA_ENTRADA[tipo],
                           fiscal_period_id=fiscal_period_id, account_id=account_id, valor=valor)


def delete_entry(session: Session, *, fiscal_period_id: int, account_id: int, tipo: TipoEstadoFinanciero) -> bool:
    """Borra un importe (queda como "sin dato"), con registro en el historial."""
    return _delete_importe(session, ENTRY_MODEL[tipo], TABLA_ENTRADA[tipo],
                           fiscal_period_id=fiscal_period_id, account_id=account_id)


# ---------------------------------------------------------------------------
# Initial balances (seccion 9.5 / DuPont)
# ---------------------------------------------------------------------------

def get_initial_balances_map(session: Session, fiscal_period_id: int) -> dict[int, Decimal]:
    rows = session.execute(
        select(InitialBalance.account_id, InitialBalance.valor).where(
            InitialBalance.fiscal_period_id == fiscal_period_id
        )
    ).all()
    return {account_id: valor for account_id, valor in rows}


def upsert_initial_balance(session: Session, *, fiscal_period_id: int, account_id: int, valor) -> str | None:
    return _upsert_importe(session, InitialBalance, "initial_balance",
                           fiscal_period_id=fiscal_period_id, account_id=account_id, valor=valor)


def delete_initial_balance(session: Session, *, fiscal_period_id: int, account_id: int) -> bool:
    return _delete_importe(session, InitialBalance, "initial_balance",
                           fiscal_period_id=fiscal_period_id, account_id=account_id)


# ---------------------------------------------------------------------------
# Statement status (borrador / revisado) - seccion 6.3
# ---------------------------------------------------------------------------

def get_statement_status(
    session: Session, fiscal_period_id: int, tipo: TipoEstadoFinanciero
) -> EstadoRegistro:
    status = session.execute(
        select(StatementStatus).where(
            StatementStatus.fiscal_period_id == fiscal_period_id,
            StatementStatus.tipo == tipo,
        )
    ).scalars().first()
    return status.estado if status is not None else EstadoRegistro.BORRADOR


def set_statement_status(
    session: Session, fiscal_period_id: int, tipo: TipoEstadoFinanciero, estado: EstadoRegistro
) -> None:
    status = session.execute(
        select(StatementStatus).where(
            StatementStatus.fiscal_period_id == fiscal_period_id,
            StatementStatus.tipo == tipo,
        )
    ).scalars().first()
    _verificar_ejercicio_abierto(session, fiscal_period_id)
    if status is None:
        status = StatementStatus(fiscal_period_id=fiscal_period_id, tipo=tipo, estado=estado)
        session.add(status)
        session.flush()
        log_change(session, "statement_status", status.id, f"estado_{tipo.value}", None, estado.value, "CREAR",
                   fiscal_period_id=fiscal_period_id)
    elif status.estado != estado:
        log_change(session, "statement_status", status.id, f"estado_{tipo.value}", status.estado.value, estado.value,
                   "EDITAR", fiscal_period_id=fiscal_period_id)
        status.estado = estado


# ---------------------------------------------------------------------------
# Change history (secciones 8 y 17)
# ---------------------------------------------------------------------------

def _texto(valor) -> str | None:
    if valor is None:
        return None
    return valor.value if hasattr(valor, "value") else str(valor)


@contextmanager
def lote(session: Session):
    """Agrupa con un mismo lote_id los cambios del historial hechos dentro
    del bloque (un guardado, una importacion). Devuelve el lote_id."""
    anterior = session.info.get("lote_id")
    session.info["lote_id"] = uuid.uuid4().hex
    try:
        yield session.info["lote_id"]
    finally:
        if anterior is None:
            session.info.pop("lote_id", None)
        else:
            session.info["lote_id"] = anterior


def log_change(
    session: Session,
    tabla_afectada: str,
    registro_id: int,
    campo: str,
    valor_anterior: str | None,
    valor_nuevo: str | None,
    operacion: str,
    *,
    fiscal_period_id: int | None = None,
    account_id: int | None = None,
) -> None:
    """registro_id debe ser siempre el id de la fila de `tabla_afectada`."""
    session.add(
        ChangeHistory(
            tabla_afectada=tabla_afectada,
            registro_id=registro_id,
            campo=campo,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
            operacion=operacion,
            fiscal_period_id=fiscal_period_id,
            account_id=account_id,
            lote_id=session.info.get("lote_id"),
        )
    )


def list_history(
    session: Session,
    tabla_afectada: str | None = None,
    registro_id: int | None = None,
    *,
    fiscal_period_id: int | None = None,
    account_id: int | None = None,
) -> list[ChangeHistory]:
    stmt = select(ChangeHistory)
    if tabla_afectada is not None:
        stmt = stmt.where(ChangeHistory.tabla_afectada == tabla_afectada)
    if registro_id is not None:
        stmt = stmt.where(ChangeHistory.registro_id == registro_id)
    if fiscal_period_id is not None:
        stmt = stmt.where(ChangeHistory.fiscal_period_id == fiscal_period_id)
    if account_id is not None:
        stmt = stmt.where(ChangeHistory.account_id == account_id)
    stmt = stmt.order_by(ChangeHistory.fecha.desc(), ChangeHistory.id.desc())
    return list(session.execute(stmt).scalars())
