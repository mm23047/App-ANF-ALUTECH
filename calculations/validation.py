"""Convencion de signos y completitud de los estados (hallazgos A-05 y M-04).

Convencion de captura (se valida, nunca se invierte un signo):
  - Ingresos, costos, gastos e impuestos: positivos. Los calculos restan
    los costos y gastos; el `efecto` de "otros" decide si suma o resta.
  - Activos, pasivos y patrimonio: positivos segun su naturaleza.
  - Cuentas correctoras (naturaleza contraria a la de su categoria, p. ej.
    depreciacion acumulada ACREEDORA dentro del ACTIVO): negativas.
  - Resultados acumulados, resultado del ejercicio y otras cuentas
    patrimoniales pueden ser negativos (perdidas, ORI).
  - Un ISR negativo (beneficio fiscal) se admite con confirmacion.
Un cero siempre es valido.
"""
from __future__ import annotations

from decimal import Decimal

from database.enums import RESULTADOS_CATEGORIAS
from database.enums import CategoriaPrincipal as Cat
from database.enums import NaturalezaSaldo as Nat
from database.enums import Subcategoria as Sub

CONVENCION_SIGNOS = (
    "Convención de signos: capture ingresos, costos, gastos e impuestos en positivo (los cálculos restan "
    "costos y gastos). Activos, pasivos y patrimonio en positivo. Las cuentas correctoras del activo "
    "(p. ej. depreciación acumulada) en negativo. Los resultados acumulados o del ejercicio pueden ser "
    "negativos si hay pérdidas. Un importe con signo distinto requiere confirmación; nunca se invierte."
)

# Naturaleza propia de cada categoria del Balance; una cuenta con la
# naturaleza contraria es correctora y se captura en negativo.
NATURALEZA_CATEGORIA = {Cat.ACTIVO: Nat.DEUDORA, Cat.PASIVO: Nat.ACREEDORA, Cat.PATRIMONIO: Nat.ACREEDORA}
# Subcategorias de patrimonio que admiten cualquier signo.
PATRIMONIO_CON_SIGNO_LIBRE = {Sub.RESULTADOS_ACUMULADOS, Sub.RESULTADO_EJERCICIO, Sub.OTRAS_PATRIMONIALES}

# Categorias que deben tener al menos una cuenta capturada (un 0 explicito
# cuenta como capturado) para que el estado se considere completo. Las demas
# (ingresos/gastos financieros, otros no operativos) son opcionales: no todas
# las empresas las tienen.
OBLIGATORIAS_BALANCE = (Cat.ACTIVO, Cat.PASIVO, Cat.PATRIMONIO)
OBLIGATORIAS_RESULTADOS = (Cat.INGRESOS, Cat.COSTOS, Cat.GASTOS_OPERATIVOS, Cat.IMPUESTOS)

NOMBRE_CATEGORIA = {
    Cat.ACTIVO: "Activo", Cat.PASIVO: "Pasivo", Cat.PATRIMONIO: "Patrimonio", Cat.INGRESOS: "Ingresos",
    Cat.COSTOS: "Costo de ventas", Cat.GASTOS_OPERATIVOS: "Gastos operativos",
    Cat.INGRESOS_FINANCIEROS: "Ingresos financieros", Cat.GASTOS_FINANCIEROS: "Gastos financieros",
    Cat.OTROS_INGRESOS_GASTOS: "Otros ingresos y gastos", Cat.IMPUESTOS: "Impuesto sobre la renta",
}


def es_correctora(cuenta) -> bool:
    natural = NATURALEZA_CATEGORIA.get(cuenta.categoria_principal)
    return natural is not None and cuenta.naturaleza_saldo != natural


def aviso_signo(cuenta, valor: Decimal) -> str | None:
    """Mensaje si `valor` no sigue la convencion para `cuenta`; None si la sigue."""
    if valor == 0:
        return None
    nombre = f"{cuenta.codigo} — {cuenta.nombre}"
    if cuenta.categoria_principal in RESULTADOS_CATEGORIAS:
        if valor > 0:
            return None
        if cuenta.categoria_principal == Cat.IMPUESTOS:
            return (f"{nombre}: ISR negativo ({valor}). Si corresponde a un beneficio fiscal, confírmelo y "
                    "explíquelo en las notas; aumentará la utilidad neta.")
        return (f"{nombre}: importe negativo ({valor}). Esta cuenta se captura en positivo; el cálculo ya la "
                "suma o resta según su categoría. Un negativo invierte su efecto.")
    if es_correctora(cuenta):
        if valor < 0:
            return None
        return (f"{nombre}: cuenta correctora capturada en positivo ({valor}). Debe ser negativa: en positivo "
                "aumenta el total en lugar de disminuirlo.")
    if valor > 0 or (cuenta.categoria_principal == Cat.PATRIMONIO and cuenta.subcategoria in PATRIMONIO_CON_SIGNO_LIBRE):
        return None
    return f"{nombre}: importe negativo ({valor}) en una cuenta que normalmente es positiva."


def categorias_faltantes(entries, obligatorias) -> list[str]:
    capturadas = {cuenta.categoria_principal for cuenta, _ in entries}
    return [NOMBRE_CATEGORIA[c] for c in obligatorias if c not in capturadas]


def cuentas_sin_dato(cuentas_activas, entries, categorias) -> list:
    """Cuentas activas de esas categorias sin importe capturado (informativo:
    no todas las cuentas del catalogo deben tener movimientos)."""
    capturadas = {cuenta.id for cuenta, _ in entries}
    return [c for c in cuentas_activas if c.categoria_principal in categorias and c.id not in capturadas]


def lineas_reportables(grupo) -> list:
    """Lineas de un grupo que se presentan en los reportes. Si el grupo ya tiene cuentas mapeadas a un grupo de
    analisis, se omiten sus importes 0.00 de cuentas sin mapear: son del catalogo estandar, no figuran en los estados
    originales y no aportan a ningun total. Siguen guardados y visibles en Modificacion de datos. Un cero en un
    catalogo sin mapear es un dato capturado y se presenta."""
    mapeada = lambda linea: getattr(linea.cuenta, "grupo_analisis", None)
    if not any(mapeada(l) for l in grupo.lineas):
        return list(grupo.lineas)
    return [l for l in grupo.lineas if l.valor != 0 or mapeada(l)]


def nota_cuentas_omitidas(grupos) -> str | None:
    omitidas = sum(len(g.lineas) - len(lineas_reportables(g)) for g in grupos)
    if not omitidas:
        return None
    return (f"No se muestran {omitidas} cuenta(s) del catálogo estándar con importe 0.00 y sin grupo de análisis: no figuran en "
            "los estados originales ni alteran los totales. Siguen guardadas y se consultan en «Modificación de datos».")
