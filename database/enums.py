"""Enumeraciones del catalogo de cuentas y clasificaciones de reporte.

Estas enumeraciones son la unica fuente de verdad para como una cuenta
participa en los calculos de calculations/. No se debe inferir el signo
de una cuenta a partir de su "naturaleza del saldo": ese campo es
informativo/de validacion unicamente (ver plan de resolucion de
ambiguedades, seccion "Otros ingresos/gastos operativos").
"""
from __future__ import annotations

import enum


class CategoriaPrincipal(str, enum.Enum):
    # Balance General
    ACTIVO = "ACTIVO"
    PASIVO = "PASIVO"
    PATRIMONIO = "PATRIMONIO"
    # Estado de Resultados
    INGRESOS = "INGRESOS"
    COSTOS = "COSTOS"
    GASTOS_OPERATIVOS = "GASTOS_OPERATIVOS"
    INGRESOS_FINANCIEROS = "INGRESOS_FINANCIEROS"
    GASTOS_FINANCIEROS = "GASTOS_FINANCIEROS"
    OTROS_INGRESOS_GASTOS = "OTROS_INGRESOS_GASTOS"
    IMPUESTOS = "IMPUESTOS"


BALANCE_CATEGORIAS = {
    CategoriaPrincipal.ACTIVO,
    CategoriaPrincipal.PASIVO,
    CategoriaPrincipal.PATRIMONIO,
}

RESULTADOS_CATEGORIAS = {
    CategoriaPrincipal.INGRESOS,
    CategoriaPrincipal.COSTOS,
    CategoriaPrincipal.GASTOS_OPERATIVOS,
    CategoriaPrincipal.INGRESOS_FINANCIEROS,
    CategoriaPrincipal.GASTOS_FINANCIEROS,
    CategoriaPrincipal.OTROS_INGRESOS_GASTOS,
    CategoriaPrincipal.IMPUESTOS,
}


class Subcategoria(str, enum.Enum):
    # ACTIVO / PASIVO
    CORRIENTE = "CORRIENTE"
    NO_CORRIENTE = "NO_CORRIENTE"
    # PATRIMONIO
    CAPITAL_SOCIAL = "CAPITAL_SOCIAL"
    RESERVAS = "RESERVAS"
    RESULTADOS_ACUMULADOS = "RESULTADOS_ACUMULADOS"
    RESULTADO_EJERCICIO = "RESULTADO_EJERCICIO"
    OTRAS_PATRIMONIALES = "OTRAS_PATRIMONIALES"
    # GASTOS_OPERATIVOS
    ADMINISTRACION = "ADMINISTRACION"
    VENTAS = "VENTAS"
    OTROS_OPERATIVOS = "OTROS_OPERATIVOS"


SUBCATEGORIAS_POR_CATEGORIA = {
    CategoriaPrincipal.ACTIVO: {Subcategoria.CORRIENTE, Subcategoria.NO_CORRIENTE},
    CategoriaPrincipal.PASIVO: {Subcategoria.CORRIENTE, Subcategoria.NO_CORRIENTE},
    CategoriaPrincipal.PATRIMONIO: {
        Subcategoria.CAPITAL_SOCIAL,
        Subcategoria.RESERVAS,
        Subcategoria.RESULTADOS_ACUMULADOS,
        Subcategoria.RESULTADO_EJERCICIO,
        Subcategoria.OTRAS_PATRIMONIALES,
    },
    CategoriaPrincipal.GASTOS_OPERATIVOS: {
        Subcategoria.ADMINISTRACION,
        Subcategoria.VENTAS,
        Subcategoria.OTROS_OPERATIVOS,
    },
    # Las demas categorias de resultados no requieren subcategoria.
}


class EfectoCuenta(str, enum.Enum):
    """Solo relevante para Subcategoria.OTROS_OPERATIVOS: determina si la
    cuenta suma (INGRESO) o resta (GASTO) en la Utilidad Operativa."""

    INGRESO = "INGRESO"
    GASTO = "GASTO"


class NaturalezaSaldo(str, enum.Enum):
    DEUDORA = "DEUDORA"
    ACREEDORA = "ACREEDORA"


class EstadoCuenta(str, enum.Enum):
    ACTIVA = "ACTIVA"
    INACTIVA = "INACTIVA"


class EstadoRegistro(str, enum.Enum):
    """Estado de captura de un balance_entry / income_entry."""

    BORRADOR = "BORRADOR"
    REVISADO = "REVISADO"


class EstadoEjercicio(str, enum.Enum):
    ABIERTO = "ABIERTO"
    CERRADO = "CERRADO"


class TipoEstadoFinanciero(str, enum.Enum):
    BALANCE = "BALANCE"
    RESULTADOS = "RESULTADOS"


def requiere_subcategoria(categoria: CategoriaPrincipal) -> bool:
    return categoria in SUBCATEGORIAS_POR_CATEGORIA


def subcategorias_validas(categoria: CategoriaPrincipal) -> set[Subcategoria]:
    return SUBCATEGORIAS_POR_CATEGORIA.get(categoria, set())
