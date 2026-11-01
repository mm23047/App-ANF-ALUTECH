"""Catalogo de cuentas estandar inicial (plantilla editable).

No son datos financieros reales de ninguna empresa -- es un punto de
partida profesional tipico que el usuario puede editar, desactivar o
ampliar desde el modulo de Catalogo de Cuentas (seccion 5). Solo se
inserta si el catalogo esta vacio.
"""
from __future__ import annotations

from sqlalchemy.orm import Session

from database.enums import CategoriaPrincipal as Cat
from database.enums import EfectoCuenta as Efecto
from database.enums import NaturalezaSaldo as Nat
from database.enums import Subcategoria as Sub
from database.repositories import create_account, list_accounts

# (codigo, nombre, categoria, subcategoria, naturaleza, efecto, orden)
DEFAULT_ACCOUNTS: list[tuple[str, str, Cat, Sub | None, Nat, Efecto | None, int]] = [
    # ACTIVO CORRIENTE
    ("1001", "Efectivo y equivalentes", Cat.ACTIVO, Sub.CORRIENTE, Nat.DEUDORA, None, 10),
    ("1002", "Cuentas por cobrar", Cat.ACTIVO, Sub.CORRIENTE, Nat.DEUDORA, None, 20),
    ("1003", "Inventarios", Cat.ACTIVO, Sub.CORRIENTE, Nat.DEUDORA, None, 30),
    ("1004", "Otros activos corrientes", Cat.ACTIVO, Sub.CORRIENTE, Nat.DEUDORA, None, 40),
    # ACTIVO NO CORRIENTE
    ("1101", "Propiedad, planta y equipo", Cat.ACTIVO, Sub.NO_CORRIENTE, Nat.DEUDORA, None, 110),
    ("1102", "Depreciacion acumulada", Cat.ACTIVO, Sub.NO_CORRIENTE, Nat.ACREEDORA, None, 120),
    ("1103", "Activos intangibles", Cat.ACTIVO, Sub.NO_CORRIENTE, Nat.DEUDORA, None, 130),
    ("1104", "Otros activos no corrientes", Cat.ACTIVO, Sub.NO_CORRIENTE, Nat.DEUDORA, None, 140),
    # PASIVO CORRIENTE
    ("2001", "Cuentas por pagar", Cat.PASIVO, Sub.CORRIENTE, Nat.ACREEDORA, None, 210),
    ("2002", "Prestamos a corto plazo", Cat.PASIVO, Sub.CORRIENTE, Nat.ACREEDORA, None, 220),
    ("2003", "Impuestos por pagar", Cat.PASIVO, Sub.CORRIENTE, Nat.ACREEDORA, None, 230),
    ("2004", "Otros pasivos corrientes", Cat.PASIVO, Sub.CORRIENTE, Nat.ACREEDORA, None, 240),
    # PASIVO NO CORRIENTE
    ("2101", "Prestamos a largo plazo", Cat.PASIVO, Sub.NO_CORRIENTE, Nat.ACREEDORA, None, 310),
    ("2102", "Otros pasivos no corrientes", Cat.PASIVO, Sub.NO_CORRIENTE, Nat.ACREEDORA, None, 320),
    # PATRIMONIO
    ("3001", "Capital social", Cat.PATRIMONIO, Sub.CAPITAL_SOCIAL, Nat.ACREEDORA, None, 410),
    ("3002", "Reservas", Cat.PATRIMONIO, Sub.RESERVAS, Nat.ACREEDORA, None, 420),
    ("3003", "Resultados acumulados", Cat.PATRIMONIO, Sub.RESULTADOS_ACUMULADOS, Nat.ACREEDORA, None, 430),
    ("3004", "Resultado del ejercicio", Cat.PATRIMONIO, Sub.RESULTADO_EJERCICIO, Nat.ACREEDORA, None, 440),
    ("3005", "Otras cuentas patrimoniales", Cat.PATRIMONIO, Sub.OTRAS_PATRIMONIALES, Nat.ACREEDORA, None, 450),
    # ESTADO DE RESULTADOS
    ("4001", "Ingresos netos", Cat.INGRESOS, None, Nat.ACREEDORA, None, 510),
    ("5001", "Costo de ventas", Cat.COSTOS, None, Nat.DEUDORA, None, 520),
    ("6001", "Gastos de administracion", Cat.GASTOS_OPERATIVOS, Sub.ADMINISTRACION, Nat.DEUDORA, None, 530),
    ("6002", "Gastos de ventas", Cat.GASTOS_OPERATIVOS, Sub.VENTAS, Nat.DEUDORA, None, 540),
    ("6003", "Otros ingresos operativos", Cat.GASTOS_OPERATIVOS, Sub.OTROS_OPERATIVOS, Nat.ACREEDORA, Efecto.INGRESO, 550),
    ("6004", "Otros gastos operativos", Cat.GASTOS_OPERATIVOS, Sub.OTROS_OPERATIVOS, Nat.DEUDORA, Efecto.GASTO, 560),
    ("7001", "Ingresos financieros", Cat.INGRESOS_FINANCIEROS, None, Nat.ACREEDORA, None, 570),
    ("7002", "Gastos financieros", Cat.GASTOS_FINANCIEROS, None, Nat.DEUDORA, None, 580),
    ("7003", "Otros ingresos no operativos", Cat.OTROS_INGRESOS_GASTOS, None, Nat.ACREEDORA, Efecto.INGRESO, 590),
    ("7004", "Otros gastos no operativos", Cat.OTROS_INGRESOS_GASTOS, None, Nat.DEUDORA, Efecto.GASTO, 600),
    ("8001", "Impuesto sobre la renta", Cat.IMPUESTOS, None, Nat.DEUDORA, None, 610),
]


def seed_default_accounts(session: Session) -> int:
    """Inserta el catalogo estandar solo si no hay cuentas registradas.

    Devuelve el numero de cuentas insertadas (0 si ya existia catalogo).
    """
    if list_accounts(session):
        return 0
    for codigo, nombre, categoria, subcategoria, naturaleza, efecto, orden in DEFAULT_ACCOUNTS:
        create_account(
            session,
            codigo=codigo,
            nombre=nombre,
            categoria_principal=categoria,
            subcategoria=subcategoria,
            naturaleza_saldo=naturaleza,
            efecto=efecto,
            orden_presentacion=orden,
        )
    return len(DEFAULT_ACCOUNTS)
