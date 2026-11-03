"""Modelos SQLAlchemy 2.0 (declarative, typed) para la aplicacion financiera.

Principio de diseno (ver seccion 12 de la especificacion): los subtotales
derivados (utilidad bruta, totales de activo, ROE, etc.) NUNCA se
almacenan aqui. Esta capa solo persiste datos capturados por el usuario;
calculations/ los deriva en tiempo de lectura.
"""
from __future__ import annotations

import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Enum as SAEnum,
    ForeignKey,
    String,
    TypeDecorator,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from database.enums import (
    CategoriaPrincipal,
    EfectoCuenta,
    EstadoCuenta,
    EstadoEjercicio,
    EstadoRegistro,
    NaturalezaSaldo,
    Subcategoria,
    TipoEstadoFinanciero,
)

class Centavos(TypeDecorator):
    """Importe monetario guardado como entero de centavos (hallazgo M-02).

    En Python siempre es Decimal con dos decimales; en SQLite es INTEGER,
    por lo que no hay coma flotante binaria. Nunca redondea: un Decimal
    con mas de dos decimales, NaN, infinito o fuera de NUMERIC(18,2) se
    rechaza (la validacion para el usuario esta en components.money).
    """

    impl = BigInteger
    cache_ok = True
    MAXIMO = Decimal("9999999999999999.99")

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if not isinstance(value, Decimal):
            raise TypeError(f"Los importes deben ser Decimal, no {type(value).__name__}.")
        if not value.is_finite():
            raise ValueError("Importe no finito (NaN o infinito).")
        if abs(value) > self.MAXIMO:
            raise ValueError(f"Importe fuera de rango: {value}.")
        centavos = value.scaleb(2)
        if centavos != centavos.to_integral_value():
            raise ValueError(f"El importe {value} tiene mas de dos decimales.")
        return int(centavos)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if not isinstance(value, int):
            raise ValueError(f"Valor monetario almacenado no entero: {value!r}.")
        return Decimal(value).scaleb(-2)


MONEY = Centavos()


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


def _enum_col(enum_cls, length: int = 30):
    """Columna de enum que SI se reconstruye como el Enum de Python al
    leer (a diferencia de un String simple, que devolveria texto plano
    y rompe cualquier uso de .value en un objeto recien consultado)."""
    return SAEnum(
        enum_cls,
        native_enum=False,
        length=length,
        values_callable=lambda cls: [member.value for member in cls],
    )


class Base(DeclarativeBase):
    pass


class Company(Base):
    """Fila unica: datos generales de la empresa (seccion 4)."""

    __tablename__ = "company"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_legal: Mapped[str] = mapped_column(String(200))
    nombre_comercial: Mapped[str] = mapped_column(String(200))
    actividad_economica: Mapped[str] = mapped_column(String(200))
    pais: Mapped[str] = mapped_column(String(100))
    moneda: Mapped[str] = mapped_column(String(10))
    anio_inicial_analisis: Mapped[int] = mapped_column()


class FiscalPeriod(Base):
    """Ejercicio fiscal (ej. 2021, 2022, ...)."""

    __tablename__ = "fiscal_period"
    __table_args__ = (UniqueConstraint("anio", name="uq_fiscal_period_anio"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    anio: Mapped[int] = mapped_column()
    estado: Mapped[EstadoEjercicio] = mapped_column(
        _enum_col(EstadoEjercicio, 20), default=EstadoEjercicio.ABIERTO
    )
    fecha_creacion: Mapped[datetime.datetime] = mapped_column(
        default=_utcnow
    )
    fecha_cierre: Mapped[datetime.datetime | None] = mapped_column(nullable=True)

    @property
    def cerrado(self) -> bool:
        return self.estado == EstadoEjercicio.CERRADO

    balance_entries: Mapped[list["BalanceEntry"]] = relationship(
        back_populates="fiscal_period", cascade="all, delete-orphan"
    )
    income_entries: Mapped[list["IncomeEntry"]] = relationship(
        back_populates="fiscal_period", cascade="all, delete-orphan"
    )
    initial_balances: Mapped[list["InitialBalance"]] = relationship(
        back_populates="fiscal_period", cascade="all, delete-orphan"
    )
    statement_statuses: Mapped[list["StatementStatus"]] = relationship(
        back_populates="fiscal_period", cascade="all, delete-orphan"
    )


class Account(Base):
    """Catalogo de cuentas financieras personalizable (seccion 5)."""

    __tablename__ = "account"
    __table_args__ = (UniqueConstraint("codigo", name="uq_account_codigo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(30))
    nombre: Mapped[str] = mapped_column(String(200))
    categoria_principal: Mapped[CategoriaPrincipal] = mapped_column(_enum_col(CategoriaPrincipal))
    subcategoria: Mapped[Subcategoria | None] = mapped_column(_enum_col(Subcategoria), nullable=True)
    efecto: Mapped[EfectoCuenta | None] = mapped_column(_enum_col(EfectoCuenta, 10), nullable=True)
    naturaleza_saldo: Mapped[NaturalezaSaldo] = mapped_column(_enum_col(NaturalezaSaldo, 10))
    estado: Mapped[EstadoCuenta] = mapped_column(
        _enum_col(EstadoCuenta, 10), default=EstadoCuenta.ACTIVA
    )
    orden_presentacion: Mapped[int] = mapped_column(default=0)
    # Grupo de analisis normalizado (calculations/rubros.py). Permite comparar
    # cuentas cuya denominacion cambia entre ejercicios sin depender del texto
    # del nombre. No altera los estados: solo los analisis por grupo/rubro.
    grupo_analisis: Mapped[str | None] = mapped_column(String(40), nullable=True)

    balance_entries: Mapped[list["BalanceEntry"]] = relationship(
        back_populates="account"
    )
    income_entries: Mapped[list["IncomeEntry"]] = relationship(
        back_populates="account"
    )

    @property
    def activa(self) -> bool:
        return self.estado == EstadoCuenta.ACTIVA


class BalanceEntry(Base):
    """Importe capturado de una cuenta de Balance General en un ejercicio."""

    __tablename__ = "balance_entry"
    __table_args__ = (
        UniqueConstraint("fiscal_period_id", "account_id", name="uq_balance_period_account"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    fiscal_period_id: Mapped[int] = mapped_column(
        ForeignKey("fiscal_period.id", ondelete="CASCADE")
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="RESTRICT")
    )
    valor: Mapped[Decimal] = mapped_column(MONEY)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=_utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow
    )

    fiscal_period: Mapped[FiscalPeriod] = relationship(back_populates="balance_entries")
    account: Mapped[Account] = relationship(back_populates="balance_entries")


class IncomeEntry(Base):
    """Importe capturado de una cuenta de Estado de Resultados en un ejercicio."""

    __tablename__ = "income_entry"
    __table_args__ = (
        UniqueConstraint("fiscal_period_id", "account_id", name="uq_income_period_account"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    fiscal_period_id: Mapped[int] = mapped_column(
        ForeignKey("fiscal_period.id", ondelete="CASCADE")
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="RESTRICT")
    )
    valor: Mapped[Decimal] = mapped_column(MONEY)
    created_at: Mapped[datetime.datetime] = mapped_column(
        default=_utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow
    )

    fiscal_period: Mapped[FiscalPeriod] = relationship(back_populates="income_entries")
    account: Mapped[Account] = relationship(back_populates="income_entries")


class InitialBalance(Base):
    """Saldos iniciales manuales (solo primer ejercicio registrado o huecos).

    Ver calculations/dupont.py: solo se consulta esta tabla cuando NO existe
    un ejercicio fiscal anterior encadenable en el sistema.
    """

    __tablename__ = "initial_balance"
    __table_args__ = (
        UniqueConstraint("fiscal_period_id", "account_id", name="uq_initial_period_account"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    fiscal_period_id: Mapped[int] = mapped_column(
        ForeignKey("fiscal_period.id", ondelete="CASCADE")
    )
    account_id: Mapped[int] = mapped_column(
        ForeignKey("account.id", ondelete="RESTRICT")
    )
    valor: Mapped[Decimal] = mapped_column(MONEY)

    fiscal_period: Mapped[FiscalPeriod] = relationship(back_populates="initial_balances")
    account: Mapped[Account] = relationship()


class StatementStatus(Base):
    """Estado (BORRADOR/REVISADO) de un estado financiero completo por
    ejercicio (seccion 6.3). No es por cuenta individual."""

    __tablename__ = "statement_status"
    __table_args__ = (
        UniqueConstraint("fiscal_period_id", "tipo", name="uq_statement_period_tipo"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    fiscal_period_id: Mapped[int] = mapped_column(
        ForeignKey("fiscal_period.id", ondelete="CASCADE")
    )
    tipo: Mapped[TipoEstadoFinanciero] = mapped_column(_enum_col(TipoEstadoFinanciero, 20))
    estado: Mapped[EstadoRegistro] = mapped_column(
        _enum_col(EstadoRegistro, 10), default=EstadoRegistro.BORRADOR
    )
    fecha_actualizacion: Mapped[datetime.datetime] = mapped_column(
        default=_utcnow, onupdate=_utcnow
    )

    fiscal_period: Mapped[FiscalPeriod] = relationship(back_populates="statement_statuses")


class FuenteImporte(Base):
    """Trazabilidad de un importe cargado desde un documento original:
    documento, pagina, estado financiero y denominacion tal como aparece
    impresa. `importe_documento` es la cifra impresa (texto, con sus
    parentesis) y `valor_registrado` el importe que se guardo segun la
    convencion de signos; si el importe vigente difiere de este, el control
    de trazabilidad lo senala (nunca se corrige automaticamente)."""

    __tablename__ = "fuente_importe"
    __table_args__ = (
        UniqueConstraint("fiscal_period_id", "account_id", "tipo", name="uq_fuente_importe"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    fiscal_period_id: Mapped[int] = mapped_column(ForeignKey("fiscal_period.id", ondelete="CASCADE"))
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id", ondelete="RESTRICT"))
    tipo: Mapped[TipoEstadoFinanciero] = mapped_column(_enum_col(TipoEstadoFinanciero, 20))
    documento: Mapped[str] = mapped_column(String(300))
    pagina: Mapped[int | None] = mapped_column(nullable=True)
    estado_financiero: Mapped[str] = mapped_column(String(200))
    nombre_original: Mapped[str] = mapped_column(String(300))
    importe_documento: Mapped[str] = mapped_column(String(40))
    valor_registrado: Mapped[Decimal] = mapped_column(MONEY)
    fecha_carga: Mapped[datetime.datetime] = mapped_column(default=_utcnow)

    account: Mapped[Account] = relationship()


class DatoComplementario(Base):
    """Dato original de un documento que no es el importe de una cuenta:
    totales y subtotales impresos (para controlar la carga) y datos de otros
    estados (utilidad atribuible a la controladora, depreciacion del flujo de
    efectivo). `tipo` es TOTAL_DECLARADO o COMPLEMENTARIO."""

    __tablename__ = "dato_complementario"
    __table_args__ = (
        UniqueConstraint("fiscal_period_id", "clave", name="uq_dato_complementario"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    fiscal_period_id: Mapped[int] = mapped_column(ForeignKey("fiscal_period.id", ondelete="CASCADE"))
    clave: Mapped[str] = mapped_column(String(60))
    tipo: Mapped[str] = mapped_column(String(20))
    valor: Mapped[Decimal] = mapped_column(MONEY)
    documento: Mapped[str] = mapped_column(String(300))
    pagina: Mapped[int | None] = mapped_column(nullable=True)
    estado_financiero: Mapped[str] = mapped_column(String(200))
    nombre_original: Mapped[str] = mapped_column(String(300))
    importe_documento: Mapped[str] = mapped_column(String(40))
    fecha_carga: Mapped[datetime.datetime] = mapped_column(default=_utcnow)


class ChangeHistory(Base):
    """Historial de modificaciones (secciones 8 y 17): quien/que/cuando.

    registro_id es siempre el id real de la fila de `tabla_afectada`.
    fiscal_period_id y account_id no tienen clave foranea a proposito: el
    historial debe sobrevivir a la eliminacion de un ejercicio vacio. Las
    filas anteriores a la migracion v1 tienen estas columnas en NULL.
    lote_id agrupa los cambios de una misma accion (un guardado, una
    importacion).
    """

    __tablename__ = "change_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    tabla_afectada: Mapped[str] = mapped_column(String(50))
    registro_id: Mapped[int] = mapped_column()
    campo: Mapped[str] = mapped_column(String(100))
    valor_anterior: Mapped[str | None] = mapped_column(String(200), nullable=True)
    valor_nuevo: Mapped[str | None] = mapped_column(String(200), nullable=True)
    operacion: Mapped[str] = mapped_column(String(20))
    fecha: Mapped[datetime.datetime] = mapped_column(default=_utcnow)
    fiscal_period_id: Mapped[int | None] = mapped_column(nullable=True)
    account_id: Mapped[int | None] = mapped_column(nullable=True)
    lote_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
