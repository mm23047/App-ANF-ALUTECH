"""Funciones de acceso a datos. Todas reciben una Session abierta
(ver database.connection.session_scope) y no hacen commit por si mismas,
salvo que se indique lo contrario -- el llamador controla la transaccion.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

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


def _to_decimal(valor) -> Decimal:
    return valor if isinstance(valor, Decimal) else Decimal(str(valor))


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
    period = get_fiscal_period(session, anio)
    if period is not None:
        return period, False
    period = FiscalPeriod(anio=anio, estado=EstadoEjercicio.ABIERTO)
    session.add(period)
    session.flush()
    log_change(session, "fiscal_period", period.id, "creacion", None, str(anio), "CREAR")
    return period, True


def get_previous_period(session: Session, anio: int) -> FiscalPeriod | None:
    """Ejercicio fiscal mas reciente estrictamente anterior a `anio`.

    Soporta huecos: si no existe anio-1 pero existe anio-3, se devuelve ese.
    """
    return session.execute(
        select(FiscalPeriod)
        .where(FiscalPeriod.anio < anio)
        .order_by(FiscalPeriod.anio.desc())
    ).scalars().first()


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
    log_change(session, "account", account.id, "creacion", None, f"{codigo} - {nombre}", "CREAR")
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
            log_change(session, "account", account.id, campo, str(anterior), str(nuevo_valor), "EDITAR")
            setattr(account, campo, nuevo_valor)
    return account


def deactivate_account(session: Session, account_id: int) -> Account:
    account = get_account(session, account_id)
    if account is None:
        raise ValueError(f"Cuenta {account_id} no encontrada.")
    if account.estado != EstadoCuenta.INACTIVA:
        log_change(session, "account", account.id, "estado", account.estado.value, EstadoCuenta.INACTIVA.value, "DESACTIVAR")
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


def upsert_entry(
    session: Session,
    *,
    fiscal_period_id: int,
    account_id: int,
    valor,
    tipo: TipoEstadoFinanciero,
) -> None:
    model = ENTRY_MODEL[tipo]
    valor = _to_decimal(valor)
    existente = session.execute(
        select(model).where(
            model.fiscal_period_id == fiscal_period_id, model.account_id == account_id
        )
    ).scalars().first()

    tabla = "balance_entry" if tipo == TipoEstadoFinanciero.BALANCE else "income_entry"
    if existente is None:
        session.add(model(fiscal_period_id=fiscal_period_id, account_id=account_id, valor=valor))
        log_change(session, tabla, account_id, "valor", None, str(valor), "CREAR")
    elif existente.valor != valor:
        log_change(session, tabla, existente.id, "valor", str(existente.valor), str(valor), "EDITAR")
        existente.valor = valor


def delete_entry(session: Session, *, fiscal_period_id: int, account_id: int, tipo: TipoEstadoFinanciero) -> None:
    model = ENTRY_MODEL[tipo]
    existente = session.execute(
        select(model).where(
            model.fiscal_period_id == fiscal_period_id, model.account_id == account_id
        )
    ).scalars().first()
    if existente is not None:
        tabla = "balance_entry" if tipo == TipoEstadoFinanciero.BALANCE else "income_entry"
        log_change(session, tabla, existente.id, "valor", str(existente.valor), None, "ELIMINAR")
        session.delete(existente)


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


def upsert_initial_balance(session: Session, *, fiscal_period_id: int, account_id: int, valor) -> None:
    valor = _to_decimal(valor)
    existente = session.execute(
        select(InitialBalance).where(
            InitialBalance.fiscal_period_id == fiscal_period_id,
            InitialBalance.account_id == account_id,
        )
    ).scalars().first()
    if existente is None:
        session.add(InitialBalance(fiscal_period_id=fiscal_period_id, account_id=account_id, valor=valor))
        log_change(session, "initial_balance", account_id, "valor", None, str(valor), "CREAR")
    elif existente.valor != valor:
        log_change(session, "initial_balance", existente.id, "valor", str(existente.valor), str(valor), "EDITAR")
        existente.valor = valor


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
    if status is None:
        session.add(StatementStatus(fiscal_period_id=fiscal_period_id, tipo=tipo, estado=estado))
        log_change(session, "statement_status", fiscal_period_id, f"estado_{tipo.value}", None, estado.value, "CREAR")
    elif status.estado != estado:
        log_change(session, "statement_status", fiscal_period_id, f"estado_{tipo.value}", status.estado.value, estado.value, "EDITAR")
        status.estado = estado


# ---------------------------------------------------------------------------
# Change history (secciones 8 y 17)
# ---------------------------------------------------------------------------

def log_change(
    session: Session,
    tabla_afectada: str,
    registro_id: int,
    campo: str,
    valor_anterior: str | None,
    valor_nuevo: str | None,
    operacion: str,
) -> None:
    session.add(
        ChangeHistory(
            tabla_afectada=tabla_afectada,
            registro_id=registro_id,
            campo=campo,
            valor_anterior=valor_anterior,
            valor_nuevo=valor_nuevo,
            operacion=operacion,
        )
    )


def list_history(
    session: Session, tabla_afectada: str | None = None, registro_id: int | None = None
) -> list[ChangeHistory]:
    stmt = select(ChangeHistory)
    if tabla_afectada is not None:
        stmt = stmt.where(ChangeHistory.tabla_afectada == tabla_afectada)
    if registro_id is not None:
        stmt = stmt.where(ChangeHistory.registro_id == registro_id)
    stmt = stmt.order_by(ChangeHistory.fecha.desc())
    return list(session.execute(stmt).scalars())
