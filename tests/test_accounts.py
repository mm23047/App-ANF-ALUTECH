"""Casos 1-4 de la sección 16: cuentas, ejercicios y persistencia."""
import pytest

from database import connection
from database.connection import init_db, session_scope
from database.enums import CategoriaPrincipal as Cat
from database.enums import EstadoCuenta
from database.enums import NaturalezaSaldo as Nat
from database.enums import Subcategoria as Sub
from database.repositories import (
    account_has_movements,
    create_account,
    deactivate_account,
    get_account_by_codigo,
    get_fiscal_period,
    get_or_create_fiscal_period,
    list_fiscal_periods,
    save_company,
    upsert_entry,
    update_account,
)
from database.enums import TipoEstadoFinanciero as Tipo


def test_registro_de_cuentas(db_session):
    cuenta = create_account(
        db_session,
        codigo="9999",
        nombre="Cuenta de prueba",
        categoria_principal=Cat.ACTIVO,
        subcategoria=Sub.CORRIENTE,
        naturaleza_saldo=Nat.DEUDORA,
    )
    db_session.commit()
    assert cuenta.id is not None
    assert get_account_by_codigo(db_session, "9999") is not None


def test_no_permite_codigo_duplicado(db_session):
    create_account(
        db_session, codigo="9998", nombre="A", categoria_principal=Cat.ACTIVO,
        subcategoria=Sub.CORRIENTE, naturaleza_saldo=Nat.DEUDORA,
    )
    db_session.commit()
    with pytest.raises(ValueError):
        create_account(
            db_session, codigo="9998", nombre="B", categoria_principal=Cat.ACTIVO,
            subcategoria=Sub.CORRIENTE, naturaleza_saldo=Nat.DEUDORA,
        )


def test_modificacion_de_cuentas(db_session):
    cuenta = create_account(
        db_session, codigo="9997", nombre="Original", categoria_principal=Cat.ACTIVO,
        subcategoria=Sub.CORRIENTE, naturaleza_saldo=Nat.DEUDORA,
    )
    db_session.commit()

    update_account(db_session, cuenta.id, nombre="Editada", orden_presentacion=5)
    db_session.commit()
    assert cuenta.nombre == "Editada"
    assert cuenta.orden_presentacion == 5


def test_desactivar_cuenta_no_la_elimina(db_session):
    cuenta = create_account(
        db_session, codigo="9996", nombre="Para desactivar", categoria_principal=Cat.ACTIVO,
        subcategoria=Sub.CORRIENTE, naturaleza_saldo=Nat.DEUDORA,
    )
    db_session.commit()

    deactivate_account(db_session, cuenta.id)
    db_session.commit()

    recuperada = get_account_by_codigo(db_session, "9996")
    assert recuperada is not None
    assert recuperada.estado == EstadoCuenta.INACTIVA


def test_cuenta_con_movimientos_se_detecta(db_session):
    cuenta = get_account_by_codigo(db_session, "1001")
    periodo, _ = get_or_create_fiscal_period(db_session, 2021)
    db_session.commit()
    assert account_has_movements(db_session, cuenta.id) is False

    upsert_entry(db_session, fiscal_period_id=periodo.id, account_id=cuenta.id, valor="100.00", tipo=Tipo.BALANCE)
    db_session.commit()
    assert account_has_movements(db_session, cuenta.id) is True


def test_categoria_se_recupera_como_enum_tras_consulta_fresca(db_session):
    """Regresion: las columnas de enum deben reconstruirse como el Enum de
    Python (no como str plano) incluso cuando se consultan desde una
    identidad distinta a la que las creo (sesion nueva sobre el mismo
    engine), para que .value no falle (ver bug detectado al generar las
    plantillas de Excel)."""
    db_session.commit()

    nueva_sesion = connection.get_session()
    try:
        cuenta = get_account_by_codigo(nueva_sesion, "1001")
        assert isinstance(cuenta.categoria_principal, Cat)
        assert cuenta.categoria_principal.value == "ACTIVO"
        assert isinstance(cuenta.subcategoria, Sub)
    finally:
        nueva_sesion.close()


def test_registro_de_ejercicios(db_session):
    periodo_a, creado_a = get_or_create_fiscal_period(db_session, 2021)
    db_session.commit()
    assert creado_a is True

    periodo_b, creado_b = get_or_create_fiscal_period(db_session, 2021)
    assert creado_b is False
    assert periodo_a.id == periodo_b.id

    get_or_create_fiscal_period(db_session, 2022)
    db_session.commit()
    anios = [p.anio for p in list_fiscal_periods(db_session)]
    assert anios == [2021, 2022]


def test_persistencia_en_sqlite(tmp_path):
    db_path = tmp_path / "persistencia.db"
    init_db(db_path=db_path)
    with session_scope() as s:
        save_company(
            s, nombre_legal="Persistente SA", nombre_comercial="Persistente", actividad_economica="Pruebas",
            pais="GT", moneda="GTQ", anio_inicial_analisis=2021,
        )
        create_account(
            s, codigo="7777", nombre="Cuenta persistente", categoria_principal=Cat.ACTIVO,
            subcategoria=Sub.CORRIENTE, naturaleza_saldo=Nat.DEUDORA,
        )

    connection.dispose_engine()

    # Reabrir la misma base de datos como si la aplicación se hubiera cerrado y reabierto.
    init_db(db_path=db_path)
    with session_scope() as s:
        from database.repositories import get_company

        assert get_company(s).nombre_legal == "Persistente SA"
        assert get_account_by_codigo(s, "7777") is not None

    connection.dispose_engine()
