"""Grupos de analisis, rubros comparables y datos agregados por ejercicio.

Las cuentas conservan su denominacion original y su clasificacion contable
(categoria/subcategoria), que determinan los estados financieros. Ademas,
cada cuenta puede pertenecer a un *grupo de analisis* (account.grupo_analisis,
configurable desde el Catalogo de cuentas): una linea normalizada que permite
comparar cuentas cuya denominacion cambia entre ejercicios (p. ej. "Efectivo"
en los estados combinados 2021-2023 y "Efectivo y Equivalentes de Efectivo"
en los consolidados 2024-2025) sin depender de coincidencias de texto.

Un *rubro* es una suma de grupos que usan los indicadores y el analisis
horizontal. Unica fuente de estas definiciones: los indicadores, el
dashboard, los reportes y las exportaciones leen los importes por medio de
DatosEjercicio, nunca recalculan los subtotales por su cuenta.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy.orm import Session

from calculations.balance_sheet import BalanceSheetResult, compute_balance_sheet
from calculations.income_statement import IncomeStatementResult, compute_income_statement
from database.enums import CategoriaPrincipal as Cat
from database.enums import EfectoCuenta as Efecto
from database.enums import NaturalezaSaldo as Nat
from database.enums import Subcategoria as Sub
from database.enums import TipoEstadoFinanciero
from database.models import Account, DatoComplementario, FiscalPeriod
from database.repositories import list_datos_complementarios, list_entries, list_fiscal_periods, par_atribucion

CERO = Decimal("0")

# Clases de grupo
AC, ANC, PC, PNC, PAT, ER = "AC", "ANC", "PC", "PNC", "PAT", "ER"
NOMBRE_CLASE = {
    AC: "Activo corriente", ANC: "Activo no corriente", PC: "Pasivo corriente",
    PNC: "Pasivo no corriente", PAT: "Patrimonio", ER: "Estado de resultados",
}
# Tipo de pasivo para la estructura de capital (WACC): con costo explicito o no.
FINANCIERO = "FINANCIERO"
OPERATIVO = "OPERATIVO"


@dataclass(frozen=True)
class GrupoAnalisis:
    codigo: str
    nombre: str
    clase: str
    tipo_pasivo: str | None = None


_GRUPOS = [
    # Activo corriente
    GrupoAnalisis("EFECTIVO", "Efectivo y equivalentes de efectivo", AC),
    GrupoAnalisis("INVERSIONES_CP", "Inversiones y depósitos a plazo (corrientes)", AC),
    GrupoAnalisis("CXC_COMERCIALES", "Cuentas por cobrar comerciales (neto)", AC),
    GrupoAnalisis("OTRAS_CXC_CP", "Otras cuentas por cobrar (corrientes)", AC),
    GrupoAnalisis("DEUDORES_COMERCIALES_OTRAS", "Deudores comerciales y otras cuentas por cobrar (neto)", AC),
    GrupoAnalisis("CXC_RELACIONADAS_CP", "Cuentas por cobrar a partes relacionadas (corrientes)", AC),
    GrupoAnalisis("INVENTARIOS", "Inventarios", AC),
    GrupoAnalisis("PAGOS_ANTICIPADOS", "Gastos y pagos por anticipado", AC),
    GrupoAnalisis("IMPUESTOS_ACTIVO_CP", "Anticipos de ISR e impuestos corrientes (activo)", AC),
    # Activo no corriente
    GrupoAnalisis("DEPOSITOS_PLAZO_LP", "Certificados de depósito a plazo (no corrientes)", ANC),
    GrupoAnalisis("INVERSIONES_ACCIONES", "Inversiones en acciones", ANC),
    GrupoAnalisis("INVERSIONES_LP", "Inversiones (no corrientes)", ANC),
    GrupoAnalisis("CXC_LP", "Cuentas por cobrar a largo plazo", ANC),
    GrupoAnalisis("CXC_RELACIONADAS_LP", "Cuentas por cobrar a partes relacionadas (no corrientes)", ANC),
    GrupoAnalisis("OTRAS_CXC_LP", "Otras cuentas por cobrar (no corrientes)", ANC),
    GrupoAnalisis("PROPIEDADES_INVERSION", "Propiedades de inversión", ANC),
    GrupoAnalisis("PPE", "Propiedades, planta y equipo (neto)", ANC),
    GrupoAnalisis("DERECHO_USO", "Activos por derecho de uso (neto)", ANC),
    GrupoAnalisis("INTANGIBLES", "Activos intangibles", ANC),
    GrupoAnalisis("PLUSVALIA", "Plusvalía mercantil", ANC),
    GrupoAnalisis("OTROS_ACTIVOS_NC", "Otros activos (no corrientes)", ANC),
    GrupoAnalisis("OTROS_ACTIVOS_FINANCIEROS_NC", "Otros activos financieros (no corrientes)", ANC),
    GrupoAnalisis("IMPUESTO_DIFERIDO_ACTIVO", "Impuesto sobre la renta diferido (activo)", ANC),
    # Pasivo corriente
    GrupoAnalisis("PRESTAMOS_CP", "Préstamos bancarios (corrientes)", PC, FINANCIERO),
    GrupoAnalisis("ARRENDAMIENTOS_CP", "Pasivos por arrendamientos (corrientes)", PC, FINANCIERO),
    GrupoAnalisis("BONOS_CP", "Bonos corporativos (corrientes)", PC, FINANCIERO),
    GrupoAnalisis("CERTIFICADOS_INVERSION_CP", "Certificados de inversión (corrientes)", PC, FINANCIERO),
    GrupoAnalisis("TITULARIZACION_CP", "Obligaciones por derechos titularizados (corrientes)", PC, FINANCIERO),
    GrupoAnalisis("TITULOS_VALORES_CP", "Obligaciones por emisión de títulos valores (corrientes)", PC, FINANCIERO),
    GrupoAnalisis("DOCUMENTOS_POR_PAGAR_CP", "Documentos por pagar (corrientes)", PC, FINANCIERO),
    GrupoAnalisis("OTROS_PASIVOS_FINANCIEROS_CP", "Otros pasivos financieros (corrientes)", PC, FINANCIERO),
    GrupoAnalisis("CXP_COMERCIALES", "Cuentas por pagar comerciales", PC, OPERATIVO),
    GrupoAnalisis("OTRAS_CXP_CP", "Otras cuentas por pagar (corrientes)", PC, OPERATIVO),
    GrupoAnalisis("ACREEDORES_COMERCIALES_OTRAS", "Acreedores comerciales y otras cuentas por pagar", PC, OPERATIVO),
    GrupoAnalisis("CXP_RELACIONADAS_CP", "Cuentas por pagar a partes relacionadas", PC, OPERATIVO),
    GrupoAnalisis("IMPUESTOS_PASIVO_CP", "Impuesto sobre la renta e impuestos por pagar (corrientes)", PC, OPERATIVO),
    # Pasivo no corriente
    GrupoAnalisis("PRESTAMOS_LP", "Préstamos y otras obligaciones financieras (no corrientes)", PNC, FINANCIERO),
    GrupoAnalisis("ARRENDAMIENTOS_LP", "Pasivos por arrendamientos (no corrientes)", PNC, FINANCIERO),
    GrupoAnalisis("BONOS_LP", "Bonos corporativos (no corrientes)", PNC, FINANCIERO),
    GrupoAnalisis("CERTIFICADOS_INVERSION_LP", "Certificados de inversión (no corrientes)", PNC, FINANCIERO),
    GrupoAnalisis("TITULARIZACION_LP", "Obligaciones por derechos titularizados (no corrientes)", PNC, FINANCIERO),
    GrupoAnalisis("TITULOS_VALORES_LP", "Obligaciones por emisión de títulos valores (no corrientes)", PNC, FINANCIERO),
    GrupoAnalisis("DOCUMENTOS_POR_PAGAR_LP", "Documentos por pagar (no corrientes)", PNC, FINANCIERO),
    GrupoAnalisis("OTROS_PASIVOS_FINANCIEROS_LP", "Otros pasivos financieros (no corrientes)", PNC, FINANCIERO),
    GrupoAnalisis("OTRAS_CXP_LP", "Otras cuentas por pagar (no corrientes)", PNC, OPERATIVO),
    GrupoAnalisis("PRIMA_VENTA_ACCIONES", "Pasivo por prima en venta de acciones de subsidiaria", PNC, OPERATIVO),
    GrupoAnalisis("BENEFICIOS_POST_EMPLEO", "Pasivos por beneficios post empleo", PNC, OPERATIVO),
    GrupoAnalisis("PROVISIONES_LP", "Provisiones (no corrientes)", PNC, OPERATIVO),
    GrupoAnalisis("IMPUESTOS_PASIVO_LP", "Impuesto sobre la renta por pagar (no corriente)", PNC, OPERATIVO),
    GrupoAnalisis("IMPUESTO_DIFERIDO_PASIVO", "Impuesto sobre la renta diferido (pasivo)", PNC, OPERATIVO),
    # Patrimonio
    GrupoAnalisis("CAPITAL_SOCIAL", "Capital social", PAT),
    GrupoAnalisis("PRIMA_ACCIONES", "Prima / superávit por acciones", PAT),
    GrupoAnalisis("APORTACIONES_CAPITAL", "Aportaciones de capital / capital adicional", PAT),
    GrupoAnalisis("RESERVA_LEGAL", "Reserva legal", PAT),
    GrupoAnalisis("OTRAS_RESERVAS", "Otras reservas de capital (incluye otros resultados integrales)", PAT),
    GrupoAnalisis("RESERVAS_CAPITAL", "Reservas de capital", PAT),
    GrupoAnalisis("EFECTO_CONVERSION", "Efecto de conversión de entidades extranjeras", PAT),
    GrupoAnalisis("RESULTADOS_ACUMULADOS", "Resultados (utilidades) acumulados", PAT),
    GrupoAnalisis("RESULTADO_PERIODO", "Resultado del período", PAT),
    GrupoAnalisis("NO_CONTROLADORAS", "Participaciones no controladoras", PAT),
    # Estado de resultados
    GrupoAnalisis("INGRESOS_ORDINARIOS", "Ingresos de actividades ordinarias", ER),
    GrupoAnalisis("COSTO_VENTAS", "Costo de ventas", ER),
    GrupoAnalisis("GASTOS_ADMINISTRACION", "Gastos de administración", ER),
    GrupoAnalisis("GASTOS_VENTA", "Gastos de venta y despacho / distribución", ER),
    GrupoAnalisis("DETERIORO_CXC", "Deterioro de cuentas por cobrar", ER),
    GrupoAnalisis("GASTOS_PERSONAL", "Gastos de personal", ER),
    GrupoAnalisis("DEPRECIACION_AMORTIZACION", "Depreciación y amortización", ER),
    GrupoAnalisis("OTROS_INGRESOS_OPERATIVOS", "Otros ingresos operativos (neto)", ER),
    GrupoAnalisis("INGRESOS_FINANCIEROS", "Ingresos financieros", ER),
    GrupoAnalisis("GASTOS_FINANCIEROS", "Gastos financieros", ER),
    GrupoAnalisis("GASTOS_FINANCIEROS_NETOS", "Gastos financieros (neto, presentado así)", ER),
    GrupoAnalisis("OTROS_NO_OPERATIVOS", "Otros ingresos (gastos) no operativos", ER),
    GrupoAnalisis("IMPUESTO_RENTA", "Impuesto sobre la renta", ER),
]
GRUPOS: dict[str, GrupoAnalisis] = {g.codigo: g for g in _GRUPOS}
CLASE_BALANCE = (AC, ANC, PC, PNC, PAT)
# Categoria contable que admite cada grupo del Estado de Resultados.
_CATEGORIA_DE_GRUPO = {
    "INGRESOS_ORDINARIOS": Cat.INGRESOS, "COSTO_VENTAS": Cat.COSTOS, "GASTOS_ADMINISTRACION": Cat.GASTOS_OPERATIVOS,
    "GASTOS_VENTA": Cat.GASTOS_OPERATIVOS, "DETERIORO_CXC": Cat.GASTOS_OPERATIVOS, "GASTOS_PERSONAL": Cat.GASTOS_OPERATIVOS,
    "DEPRECIACION_AMORTIZACION": Cat.GASTOS_OPERATIVOS, "OTROS_INGRESOS_OPERATIVOS": Cat.GASTOS_OPERATIVOS,
    "INGRESOS_FINANCIEROS": Cat.INGRESOS_FINANCIEROS, "GASTOS_FINANCIEROS": Cat.GASTOS_FINANCIEROS,
    "GASTOS_FINANCIEROS_NETOS": Cat.GASTOS_FINANCIEROS, "OTROS_NO_OPERATIVOS": Cat.OTROS_INGRESOS_GASTOS, "IMPUESTO_RENTA": Cat.IMPUESTOS,
}


def clase_contable(categoria, subcategoria) -> str:
    """Clase que corresponde a una clasificacion contable (AC, ANC, PC, PNC, PAT o ER)."""
    if categoria == Cat.ACTIVO:
        return AC if subcategoria == Sub.CORRIENTE else ANC
    if categoria == Cat.PASIVO:
        return PC if subcategoria == Sub.CORRIENTE else PNC
    return PAT if categoria == Cat.PATRIMONIO else ER


def grupo_incongruente(categoria, subcategoria, codigo: str | None) -> str | None:
    """Motivo por el que un grupo no corresponde a la clasificacion de la cuenta (None si corresponde o si no hay grupo).
    Ejemplo: una cuenta de activo corriente en un grupo de deuda sumaria su importe a un rubro de otra naturaleza."""
    if not codigo:
        return None
    grupo = GRUPOS.get(codigo)
    if grupo is None:
        return f"El grupo «{codigo}» no existe."
    clase = clase_contable(categoria, subcategoria)
    if grupo.clase != clase:
        return f"El grupo «{grupo.nombre}» es de {NOMBRE_CLASE[grupo.clase]} y la cuenta es de {NOMBRE_CLASE[clase]}."
    if clase == ER and _CATEGORIA_DE_GRUPO[codigo] != categoria:
        return f"El grupo «{grupo.nombre}» no corresponde a la categoría de la cuenta."
    return None


# Naturaleza de una cuenta de activo corriente sin grupo. El catalogo no tiene un campo para ello: solo se reconoce una
# denominacion completa de estas listas cerradas; cualquier otra queda como desconocida y nunca se supone. Salen de la
# seccion 5.2 del trabajo, de las interpretaciones aprobadas y del catalogo real. Se comparan nombres completos ya
# normalizados (ver _nombre_normalizado), nunca prefijos ni palabras sueltas.
INVENTARIO, NO_INVENTARIO = "INVENTARIO", "NO_INVENTARIO"
_NOMBRES_INVENTARIO = frozenset({
    # 5.2, literal
    "inventarios", "inventario", "materias primas", "materia prima", "productos en proceso", "producto en proceso",
    "inventarios de materias primas", "inventario de materias primas", "inventarios de productos en proceso", "inventario de productos en proceso",
    # Sinonimo que usa el propio trabajo (8.2 A y 9.3)
    "existencias",
    # Interpretacion academica aprobada: bienes destinados a la venta y mercancia en camino
    "productos terminados", "producto terminado", "mercaderias", "mercaderia", "inventario en transito", "inventarios en transito",
    "inventarios de productos terminados", "inventario de productos terminados", "inventarios de mercaderias", "inventario de mercaderias",
    # Catalogo real
    "inventarios - neto", "inventario (materiales, suministros, etc.)",
})
_CXC_COMERCIALES = ("CXC_COMERCIALES", "DEUDORES_COMERCIALES_OTRAS")
# Nombre -> grupos con los que es coherente. El grupo no decide el reconocimiento: solo sirve para detectar contradicciones.
_NOMBRES_NO_INVENTARIO: dict[str, tuple[str, ...]] = {
    "efectivo": ("EFECTIVO",), "efectivo en caja": ("EFECTIVO",), "efectivo y equivalentes": ("EFECTIVO",),
    "efectivo y equivalentes de efectivo": ("EFECTIVO",), "caja general": ("EFECTIVO",), "bancos": ("EFECTIVO",), "caja y bancos": ("EFECTIVO",),
    "depositos bancarios a la vista": ("EFECTIVO",),
    "inversiones": ("INVERSIONES_CP",), "inversiones (corriente)": ("INVERSIONES_CP",), "inversiones en bonos": ("INVERSIONES_CP",),
    "inversiones financieras de corto plazo": ("INVERSIONES_CP",), "certificados de depositos a plazo fijo (corriente)": ("INVERSIONES_CP",),
    "cuentas por cobrar": (*_CXC_COMERCIALES, "OTRAS_CXC_CP", "CXC_RELACIONADAS_CP"),
    "cuentas por cobrar comerciales": _CXC_COMERCIALES, "cuentas por cobrar comerciales - neto": _CXC_COMERCIALES,
    "cuentas comerciales por cobrar": _CXC_COMERCIALES, "deudores comerciales": _CXC_COMERCIALES,
    "deudores comerciales y otras cuentas por cobrar (netos)": ("DEUDORES_COMERCIALES_OTRAS",),
    "cuentas por cobrar relacionadas": ("CXC_RELACIONADAS_CP",), "cuentas por cobrar a relacionadas": ("CXC_RELACIONADAS_CP",),
    "cuentas por cobrar a partes relacionadas": ("CXC_RELACIONADAS_CP",), "cuentas por cobrar a partes relacionadas (corriente)": ("CXC_RELACIONADAS_CP",),
    "cuentas por cobrar empresas relacionadas (corriente)": ("CXC_RELACIONADAS_CP",),
    "gastos pagados por anticipado": ("PAGOS_ANTICIPADOS",), "pagos por anticipado": ("PAGOS_ANTICIPADOS",), "pagos anticipados": ("PAGOS_ANTICIPADOS",),
    "impuestos corrientes (activo)": ("IMPUESTOS_ACTIVO_CP",), "anticipos al impuesto sobre la renta": ("IMPUESTOS_ACTIVO_CP",),
    # Decision 4 del usuario y matriz final de cierre: solo estos nombres exactos, nunca sus compuestos
    "caja": ("EFECTIVO",), "banco": ("EFECTIVO",), "caja chica": ("EFECTIVO",),
    "documentos por cobrar": (*_CXC_COMERCIALES, "OTRAS_CXC_CP"), "clientes": _CXC_COMERCIALES,
    "otras cuentas por cobrar": ("OTRAS_CXC_CP", "DEUDORES_COMERCIALES_OTRAS"),
}
# Activos fijos: ningun grupo de activo corriente es coherente con estos nombres.
_NOMBRE_ACTIVO_FIJO = re.compile(r"\b(terrenos?|edificios?|edificaciones|maquinaria|vehiculos?|mobiliario|herramientas|depreciacion)\b")


def _nombre_normalizado(nombre: str) -> str:
    """Sin diferencias de mayusculas, tildes ni espacios. No quita palabras ni signos: los nombres se comparan completos."""
    sin_tildes = "".join(c for c in unicodedata.normalize("NFD", nombre.casefold()) if unicodedata.category(c) != "Mn")
    return " ".join(sin_tildes.split())


def _saldo_incompatible(cuenta: Account, valor: Decimal | None) -> str | None:
    """Motivo por el que el saldo no permite reconocer la cuenta por su nombre (None si es deudor; sin importe solo se examina su naturaleza)."""
    if cuenta.naturaleza_saldo != Nat.DEUDORA:
        return "saldo acreedor"
    if valor is None or valor > CERO:
        return None
    return "saldo negativo" if valor < CERO else "saldo cero"


def naturaleza_activo_corriente(cuenta: Account, valor: Decimal | None = None) -> str | None:
    """INVENTARIO o NO_INVENTARIO si la cuenta no tiene grupo, su denominacion completa esta en una lista cerrada y su saldo
    es deudor; None en cualquier otro caso. Un grupo asignado siempre tiene prioridad sobre el nombre, y uno que no le
    corresponde es una clasificacion contradictoria: tampoco se reconoce. Sin valor solo se examina la naturaleza del saldo."""
    if (cuenta.grupo_analisis or clase_contable(cuenta.categoria_principal, cuenta.subcategoria) != AC
            or _saldo_incompatible(cuenta, valor)):
        return None
    nombre = _nombre_normalizado(cuenta.nombre)
    if nombre in _NOMBRES_INVENTARIO:
        return INVENTARIO
    return NO_INVENTARIO if nombre in _NOMBRES_NO_INVENTARIO else None


def contradiccion_nombre_grupo(cuenta: Account) -> tuple[str, bool] | None:
    """(texto, bloquea) si el nombre de una cuenta de activo corriente contradice su grupo valido. Nunca cambia el grupo.
    Bloquea si la contradiccion afecta a lo unico que decide la prueba acida: si la cuenta es inventario o, en un activo
    fijo, si cabe en el activo corriente. Entre dos grupos que no son inventario el resultado no cambia: solo se avisa."""
    codigo = cuenta.grupo_analisis
    if not codigo or codigo not in GRUPOS or GRUPOS[codigo].clase != AC or clase_contable(cuenta.categoria_principal, cuenta.subcategoria) != AC:
        return None
    nombre, grupo = _nombre_normalizado(cuenta.nombre), GRUPOS[codigo].nombre
    if _NOMBRE_ACTIVO_FIJO.search(nombre):
        return f"el nombre indica un activo fijo y su grupo es «{grupo}», de activo corriente", True
    if nombre in _NOMBRES_INVENTARIO and codigo != "INVENTARIOS":
        return f"el nombre indica inventario y su grupo es «{grupo}»", True
    if nombre in _NOMBRES_NO_INVENTARIO:
        if codigo == "INVENTARIOS":
            return f"el nombre indica que no es inventario y su grupo es «{grupo}»", True
        if codigo not in _NOMBRES_NO_INVENTARIO[nombre]:
            return f"el nombre no corresponde a su grupo «{grupo}»", False
    return None


# Tipos de aviso de reconocimiento de la prueba acida
AVISO_INVENTARIO, AVISO_NO_INVENTARIO, AVISO_AMBIGUA, AVISO_CONTRADICCION, AVISO_SALDO = "INVENTARIO", "NO_INVENTARIO", "AMBIGUA", "CONTRADICCION", "SALDO"


@dataclass(frozen=True)
class AvisoReconocimiento:
    """Por que una cuenta de activo corriente se reconocio, se excluyo o no pudo clasificarse."""

    tipo: str
    cuenta: Account
    detalle: str = ""
    bloquea: bool = False


def grupo_de_cuenta(cuenta: Account) -> GrupoAnalisis | None:
    """Grupo de la cuenta si esta asignado y corresponde a su clasificacion; si no, la cuenta queda sin clasificar."""
    codigo = cuenta.grupo_analisis
    if not codigo or grupo_incongruente(cuenta.categoria_principal, cuenta.subcategoria, codigo):
        return None
    return GRUPOS[codigo]


@dataclass(frozen=True)
class Rubro:
    codigo: str
    nombre: str
    grupos: tuple[str, ...]
    nota: str = ""
    # Combinaciones de grupos que hacen disponible el rubro; basta una. Sin ellas, basta cualquier grupo.
    requiere: tuple[tuple[str, ...], ...] = ()


_RUBROS = [
    Rubro("EFECTIVO", "Efectivo y equivalentes de efectivo", ("EFECTIVO",)),
    Rubro("INVERSIONES_CP", "Inversiones y depósitos a plazo (corrientes)", ("INVERSIONES_CP",)),
    Rubro("TESORERIA", "Tesorería y valores negociables (efectivo + inversiones corrientes)", ("EFECTIVO", "INVERSIONES_CP"),
          requiere=(("EFECTIVO",),)),
    Rubro("CXC_COMERCIALES_PRESENTADA", "Cuentas por cobrar comerciales (línea presentada)",
          ("CXC_COMERCIALES", "DEUDORES_COMERCIALES_OTRAS"),
          "2021–2023: solo cuentas por cobrar comerciales; 2024–2025 el estado presenta una sola línea "
          "'Deudores comerciales y otras cuentas por cobrar'. La base no es homogénea entre ambos períodos."),
    Rubro("CXC_COMERCIALES_Y_OTRAS", "Cuentas por cobrar comerciales y otras (corrientes)",
          ("CXC_COMERCIALES", "OTRAS_CXC_CP", "DEUDORES_COMERCIALES_OTRAS"),
          "Alternativa analítica: comerciales + otras cuentas por cobrar corrientes. Su comparabilidad depende de confirmar "
          "que la línea unificada de 2024–2025 contiene exactamente esas cuentas, sin conceptos adicionales.",
          requiere=(("DEUDORES_COMERCIALES_OTRAS",), ("CXC_COMERCIALES", "OTRAS_CXC_CP"))),
    Rubro("CXC_RELACIONADAS_CP", "Cuentas por cobrar a partes relacionadas (corrientes)", ("CXC_RELACIONADAS_CP",)),
    Rubro("CXC_RELACIONADAS_LP", "Cuentas por cobrar a partes relacionadas (no corrientes)", ("CXC_RELACIONADAS_LP",)),
    Rubro("INVENTARIOS", "Inventarios", ("INVENTARIOS",)),
    Rubro("CXP_COMERCIALES_PRESENTADA", "Cuentas por pagar comerciales (línea presentada)",
          ("CXP_COMERCIALES", "ACREEDORES_COMERCIALES_OTRAS"),
          "2021–2023: cuentas por pagar comerciales; 2024–2025 'Acreedores comerciales y otras cuentas por "
          "pagar' (incluye otras cuentas por pagar)."),
    Rubro("DEUDA_FINANCIERA", "Deuda financiera con costo (préstamos, arrendamientos y títulos valores)",
          tuple(g.codigo for g in _GRUPOS if g.tipo_pasivo == FINANCIERO)),
    Rubro("PASIVOS_OPERATIVOS", "Pasivos operativos sin costo explícito",
          tuple(g.codigo for g in _GRUPOS if g.tipo_pasivo == OPERATIVO)),
    Rubro("INVERSIONES_NC", "Inversiones y depósitos (no corrientes)", ("DEPOSITOS_PLAZO_LP", "INVERSIONES_ACCIONES", "INVERSIONES_LP")),
    Rubro("INTANGIBLES_Y_PLUSVALIA", "Activos intangibles y plusvalía", ("INTANGIBLES", "PLUSVALIA"),
          "Los estados 2024–2025 no presentan plusvalía por separado."),
    Rubro("PPE", "Propiedades, planta y equipo (neto)", ("PPE",)),
    # Estado de resultados
    Rubro("GASTOS_OPERATIVOS_ANF", "Gastos operativos (administración, venta, personal y depreciación)",
          ("GASTOS_ADMINISTRACION", "GASTOS_VENTA", "GASTOS_PERSONAL", "DEPRECIACION_AMORTIZACION"),
          "Criterio del trabajo ANF (sección 6.4): excluye el deterioro de cuentas por cobrar y los otros ingresos.",
          requiere=(("GASTOS_ADMINISTRACION", "GASTOS_VENTA"),)),
    Rubro("OTROS_INGRESOS_GASTOS", "Otros ingresos o gastos (neto)", ("OTROS_INGRESOS_OPERATIVOS", "OTROS_NO_OPERATIVOS"),
          "2021–2023 se presentan dentro de la utilidad de operación; 2024–2025, después del resultado financiero."),
]
RUBROS: dict[str, Rubro] = {r.codigo: r for r in _RUBROS}


@dataclass(frozen=True)
class FamiliaPresentacion:
    """Grupos que, por su denominacion, pueden presentar el mismo contenido de otra forma entre
    ejercicios. Es un parametro metodologico: la relacion no esta demostrada, porque la composicion
    de las lineas no siempre se puede comprobar con los documentos."""

    codigo: str
    grupos: tuple[str, ...]


_FAMILIAS = [
    FamiliaPresentacion("CXC_CORRIENTES", ("CXC_COMERCIALES", "OTRAS_CXC_CP", "DEUDORES_COMERCIALES_OTRAS")),
    FamiliaPresentacion("CXC_LARGO_PLAZO", ("CXC_RELACIONADAS_LP", "OTRAS_CXC_LP", "CXC_LP")),
    FamiliaPresentacion("INVERSIONES_NO_CORRIENTES", ("DEPOSITOS_PLAZO_LP", "INVERSIONES_ACCIONES", "INVERSIONES_LP")),
    FamiliaPresentacion("INTANGIBLES", ("INTANGIBLES", "PLUSVALIA")),
    FamiliaPresentacion("OTROS_ACTIVOS_NC", ("OTROS_ACTIVOS_NC", "OTROS_ACTIVOS_FINANCIEROS_NC")),
    FamiliaPresentacion("TITULOS_CORRIENTES", ("BONOS_CP", "CERTIFICADOS_INVERSION_CP", "TITULARIZACION_CP", "TITULOS_VALORES_CP")),
    FamiliaPresentacion("TITULOS_NO_CORRIENTES", ("BONOS_LP", "CERTIFICADOS_INVERSION_LP", "TITULARIZACION_LP", "TITULOS_VALORES_LP")),
    FamiliaPresentacion("CXP_CORRIENTES", ("CXP_COMERCIALES", "OTRAS_CXP_CP", "ACREEDORES_COMERCIALES_OTRAS")),
    FamiliaPresentacion("RESERVAS", ("OTRAS_RESERVAS", "RESERVAS_CAPITAL", "EFECTO_CONVERSION")),
    FamiliaPresentacion("RESULTADOS_PATRIMONIO", ("RESULTADOS_ACUMULADOS", "RESULTADO_PERIODO")),
    FamiliaPresentacion("GASTOS_OPERACION", ("GASTOS_ADMINISTRACION", "GASTOS_VENTA", "GASTOS_PERSONAL", "DEPRECIACION_AMORTIZACION")),
    FamiliaPresentacion("RESULTADO_FINANCIERO", ("GASTOS_FINANCIEROS", "GASTOS_FINANCIEROS_NETOS", "INGRESOS_FINANCIEROS")),
    FamiliaPresentacion("OTROS_INGRESOS", ("OTROS_INGRESOS_OPERATIVOS", "OTROS_NO_OPERATIVOS")),
]
FAMILIA_DE_GRUPO: dict[str, FamiliaPresentacion] = {g: f for f in _FAMILIAS for g in f.grupos}


BASE_DOCUMENTO = "Dato del documento"
BASE_INGRESADA = "Dato ingresado"
BASE_SIMULACION = "Supuesto de simulación"
BASE_SUPUESTO_IGUALDAD = "Supuesto: igual a la utilidad neta"
BASE_NO_DISPONIBLE = "No disponible"


def dato_modificado(dato: DatoComplementario) -> bool:
    """True si el importe vigente de un dato complementario ya no es la cifra impresa en el documento."""
    impreso = dato.importe_documento.strip("()$ ").replace(",", "")
    return impreso not in ("-", "—", "") and Decimal(impreso) != abs(dato.valor)


def es_grupo_valido(codigo: str | None) -> bool:
    return codigo is None or codigo in GRUPOS


def signo_resultado(cuenta: Account) -> int:
    """+1 si la cuenta aumenta la utilidad, -1 si la disminuye (convencion:
    los importes de resultados se capturan en positivo)."""
    if cuenta.categoria_principal in (Cat.INGRESOS, Cat.INGRESOS_FINANCIEROS):
        return 1
    if cuenta.efecto == Efecto.INGRESO:
        return 1
    return -1


@dataclass
class DatosEjercicio:
    """Datos de un ejercicio agregados por grupo de analisis. Los totales
    salen de calculations/balance_sheet y income_statement (no se suman de
    nuevo aqui)."""

    periodo: FiscalPeriod
    bs: BalanceSheetResult
    inc: IncomeStatementResult
    grupos: dict[str, Decimal] = field(default_factory=dict)
    grupos_con_signo: dict[str, Decimal] = field(default_factory=dict)
    lineas_por_grupo: dict[str, list[tuple[Account, Decimal]]] = field(default_factory=dict)
    sin_grupo: list[tuple[Account, Decimal, TipoEstadoFinanciero]] = field(default_factory=list)
    complementarios: dict[str, DatoComplementario] = field(default_factory=dict)

    @property
    def anio(self) -> int:
        return self.periodo.anio

    @property
    def tiene_datos(self) -> bool:
        return self.bs.tiene_datos or self.inc.tiene_datos

    def g(self, codigo: str) -> Decimal:
        return self.grupos.get(codigo, CERO)

    def tiene(self, codigo: str) -> bool:
        return codigo in self.grupos

    def inventario_identificado(self) -> list[tuple[Account, Decimal]]:
        """Cuentas sin grupo reconocidas como inventario por su denominacion."""
        return [(c, v) for c, v, _ in self.sin_grupo if naturaleza_activo_corriente(c, v) == INVENTARIO]

    def avisos_reconocimiento(self) -> list[AvisoReconocimiento]:
        """Trazabilidad de las cuentas de activo corriente con importe: las que no tienen grupo valido y las que lo tienen
        pero su nombre lo contradice. Un aviso que bloquea deja la prueba acida en «No calculable»."""
        avisos = []
        for cuenta, valor, _ in self.sin_grupo:
            if clase_contable(cuenta.categoria_principal, cuenta.subcategoria) != AC:
                continue
            naturaleza = naturaleza_activo_corriente(cuenta, valor)
            nombre = _nombre_normalizado(cuenta.nombre)
            incongruencia = grupo_incongruente(cuenta.categoria_principal, cuenta.subcategoria, cuenta.grupo_analisis)
            if naturaleza == INVENTARIO:
                avisos.append(AvisoReconocimiento(AVISO_INVENTARIO, cuenta))
            elif naturaleza == NO_INVENTARIO:
                avisos.append(AvisoReconocimiento(AVISO_NO_INVENTARIO, cuenta))
            elif incongruencia:
                avisos.append(AvisoReconocimiento(AVISO_CONTRADICCION, cuenta, incongruencia, True))
            elif nombre in _NOMBRES_INVENTARIO or nombre in _NOMBRES_NO_INVENTARIO:
                avisos.append(AvisoReconocimiento(AVISO_SALDO, cuenta, _saldo_incompatible(cuenta, valor) or "", True))
            else:
                avisos.append(AvisoReconocimiento(AVISO_AMBIGUA, cuenta, bloquea=True))
        for lineas in self.lineas_por_grupo.values():
            for cuenta, valor in lineas:
                contradiccion = contradiccion_nombre_grupo(cuenta) if valor != CERO else None
                if contradiccion:
                    avisos.append(AvisoReconocimiento(AVISO_CONTRADICCION, cuenta, contradiccion[0], contradiccion[1]))
        return avisos

    def rubro(self, codigo: str) -> Decimal:
        total = sum((self.g(g) for g in RUBROS[codigo].grupos), CERO)
        if "INVENTARIOS" in RUBROS[codigo].grupos:
            total += sum((v for _, v in self.inventario_identificado()), CERO)
        return total

    def rubro_tiene(self, codigo: str) -> bool:
        return any(self.tiene(g) for g in RUBROS[codigo].grupos)

    def rubro_registrado(self, codigo: str) -> Decimal | None:
        """Importe del rubro, o None si sus cuentas no estan registradas en el ejercicio. Un importe capturado
        en cero es un saldo cero, no un dato faltante."""
        rubro = RUBROS[codigo]
        disponible = (any(all(self.tiene(g) for g in combinacion) for combinacion in rubro.requiere)
                      if rubro.requiere else self.rubro_tiene(codigo))
        # Con cuentas de esa clase sin grupo, el importe puede estar registrado pero sin clasificar: no es un dato
        # faltante. El rubro lleva lo clasificado y los indicadores que lo usan se marcan como provisionales.
        identificado = "INVENTARIOS" in rubro.grupos and bool(self.inventario_identificado())
        return self.rubro(codigo) if disponible or identificado or self.cuentas_sin_clasificar(*rubro.grupos) else None

    def cuentas_sin_clasificar(self, *grupos: str) -> list[Account]:
        """Cuentas con importe y sin grupo valido que, por su clasificacion contable, podrian pertenecer a esos grupos."""
        clases = {GRUPOS[g].clase for g in grupos}
        categorias = {_CATEGORIA_DE_GRUPO[g] for g in grupos if g in _CATEGORIA_DE_GRUPO}
        resultado = []
        for cuenta, valor, _ in self.sin_grupo:
            clase = clase_contable(cuenta.categoria_principal, cuenta.subcategoria)
            naturaleza = naturaleza_activo_corriente(cuenta, valor)
            if naturaleza == INVENTARIO or (naturaleza == NO_INVENTARIO and set(grupos) == {"INVENTARIOS"}):
                continue  # su naturaleza ya responde si pertenece o no a estos grupos
            if clase in clases and (clase != ER or cuenta.categoria_principal in categorias):
                resultado.append(cuenta)
        return resultado

    # ---------------------------------------- importes de los estados, o None si no estan registrados
    @staticmethod
    def _registrado(grupo) -> Decimal | None:
        return grupo.subtotal if grupo.lineas else None

    @property
    def activo_corriente(self) -> Decimal | None:
        return self._registrado(self.bs.activo_corriente)

    @property
    def activo_no_corriente(self) -> Decimal | None:
        return self._registrado(self.bs.activo_no_corriente)

    @property
    def pasivo_corriente(self) -> Decimal | None:
        return self._registrado(self.bs.pasivo_corriente)

    @property
    def pasivo_no_corriente(self) -> Decimal | None:
        return self._registrado(self.bs.pasivo_no_corriente)

    @property
    def activo_total(self) -> Decimal | None:
        return self.bs.total_activo if self.bs.activo_corriente.lineas or self.bs.activo_no_corriente.lineas else None

    @property
    def pasivo_total(self) -> Decimal | None:
        return self.bs.total_pasivo if self.bs.pasivo_corriente.lineas or self.bs.pasivo_no_corriente.lineas else None

    @property
    def patrimonio_total(self) -> Decimal | None:
        return self.bs.total_patrimonio if any(g.lineas for g in self.bs.patrimonio_grupos) else None

    @property
    def ingresos(self) -> Decimal | None:
        return self._registrado(self.inc.ingresos_netos)

    @property
    def costo_ventas(self) -> Decimal | None:
        return self._registrado(self.inc.costo_ventas)

    @property
    def utilidad_bruta(self) -> Decimal | None:
        return self.inc.utilidad_bruta if self.inc.ingresos_netos.lineas and self.inc.costo_ventas.lineas else None

    @property
    def utilidad_operativa(self) -> Decimal | None:
        inc = self.inc
        gastos = (inc.gastos_administracion, inc.gastos_ventas, inc.otros_ingresos_operativos, inc.otros_gastos_operativos)
        return inc.utilidad_operativa if self.utilidad_bruta is not None and any(g.lineas for g in gastos) else None

    @property
    def utilidad_antes_impuestos(self) -> Decimal | None:
        return self.inc.utilidad_antes_impuestos if self.utilidad_operativa is not None else None

    @property
    def utilidad_neta(self) -> Decimal | None:
        return self.inc.utilidad_neta if self.utilidad_operativa is not None and self.inc.impuesto_renta.lineas else None

    @property
    def gastos_financieros_netos_registrados(self) -> Decimal | None:
        return self.gastos_financieros_netos if self.inc.gastos_financieros.lineas or self.inc.ingresos_financieros.lineas else None

    def rubro_con_signo(self, *grupos: str) -> Decimal:
        return sum((self.grupos_con_signo.get(g, CERO) for g in grupos), CERO)

    def complementario(self, clave: str) -> Decimal | None:
        dato = self.complementarios.get(clave)
        return dato.valor if dato is not None else None

    # ------------------------------------------------------------ montos
    @property
    def patrimonio_controladora(self) -> Decimal:
        return self.bs.total_patrimonio - self.g("NO_CONTROLADORAS")

    @property
    def capitales_permanentes(self) -> Decimal:
        return self.bs.total_patrimonio + self.bs.pasivo_no_corriente.subtotal

    @property
    def gastos_financieros_netos(self) -> Decimal:
        return self.inc.gastos_financieros.subtotal - self.inc.ingresos_financieros.subtotal

    def utilidad_controladora(self) -> tuple[Decimal | None, str]:
        """(utilidad atribuible a los propietarios de la controladora, fuente)."""
        return self.atribucion()[:2]

    def base_atribucion(self) -> str:
        return self.atribucion()[2]

    def _nota_otra_atribucion(self, dato) -> str:
        """Otra atribucion impresa de la utilidad neta que no coincide con la usada: queda a la vista, sin elegirla."""
        otro = self.complementarios.get("utilidad_controladora_er")
        if otro is None or otro is dato or otro.valor == dato.valor:
            return ""
        return (f"; difiere de la atribución de {otro.valor:,.0f} del Estado de resultados ({otro.documento}, pág. {otro.pagina}): "
                "pendiente editorial y académica")

    def atribucion(self) -> tuple[Decimal | None, str, str]:
        """(utilidad atribuible, fuente, base). Base: de donde sale la cifra; un supuesto nunca se presenta como dato.

        La cifra registrada se usa mientras concilie con la utilidad neta vigente. Si la utilidad neta cambia, el cambio se
        atribuye a la controladora como supuesto de simulacion. Sin participacion registrada, o si las cifras del documento
        no concilian, no se elige ningun valor. Solo se iguala a la utilidad neta, como supuesto, en los ejercicios sin
        atribucion registrada y sin no controladoras, como hace el trabajo en 2024 y 2025."""
        par = par_atribucion(self.complementarios)
        if par is not None:
            dato, participacion, origen = par
            fuente = f"{origen} ({dato.documento}, pág. {dato.pagina})"
            base = BASE_INGRESADA if dato_modificado(dato) else BASE_DOCUMENTO
            if base == BASE_INGRESADA:
                fuente += f"; dato modificado por el usuario, cifra impresa {dato.importe_documento}"
            fuente += self._nota_otra_atribucion(dato)
            if not self.inc.tiene_datos:
                return dato.valor, fuente, base
            neta = self.utilidad_neta
            if neta is None:
                return None, "El Estado de Resultados está incompleto: no hay utilidad neta que atribuir", BASE_NO_DISPONIBLE
            impresa = self.complementarios.get("utilidad_neta")
            sin_cambios = impresa is not None and impresa.valor == neta
            if participacion is None:
                if impresa is not None and not sin_cambios:
                    return None, (f"La utilidad neta cambió y no hay participación no controladora registrada para actualizar la cifra de "
                                  f"{fuente}"), BASE_NO_DISPONIBLE
                return dato.valor, fuente, base
            if dato.valor + participacion.valor == neta:
                return dato.valor, fuente, base
            if sin_cambios:
                return None, (f"No concilia: atribuible {dato.valor} + no controladora {participacion.valor} difiere de la utilidad "
                              f"neta {neta} ({fuente}). No se elige una cifra: requiere una decisión"), BASE_NO_DISPONIBLE
            return neta - participacion.valor, (
                f"Derivada por supuesto de simulación: el cambio de la utilidad neta se atribuye íntegramente a la controladora y la "
                f"participación no controladora queda fija en {participacion.valor:,.2f} ({origen}, {participacion.documento}, "
                f"pág. {participacion.pagina}). No es una distribución contable comprobada: se requiere información actualizada de atribución"
            ), BASE_SIMULACION
        if not self.inc.tiene_datos:
            return None, "Sin Estado de Resultados", BASE_NO_DISPONIBLE
        if self.g("NO_CONTROLADORAS") == CERO:
            impresa = self.complementarios.get("utilidad_neta")
            origen_neta = f" ({impresa.documento}, pág. {impresa.pagina})" if impresa is not None else ""
            return self.inc.utilidad_neta, (
                f"Supuesto: utilidad atribuible igual a utilidad neta total (criterio de 9.6 del trabajo). Utilidad neta "
                f"{self.inc.utilidad_neta:,.2f}{origen_neta}. Los documentos no informan la atribución: no es un dato comprobado y se "
                "sustituye al registrar una atribución documentada"), BASE_SUPUESTO_IGUALDAD
        return None, "Hay participaciones no controladoras y el documento no informa la utilidad atribuible", BASE_NO_DISPONIBLE

    def depreciacion_amortizacion(self) -> tuple[Decimal | None, str]:
        if self.tiene("DEPRECIACION_AMORTIZACION"):
            return self.g("DEPRECIACION_AMORTIZACION"), "Estado de resultados"
        combinado = self.complementarios.get("depreciacion_amortizacion_fe")
        if combinado is not None:
            return combinado.valor, f"Estado de flujos de efectivo ({combinado.documento}, pág. {combinado.pagina})"
        dep = self.complementarios.get("depreciaciones_fe")
        amo = self.complementarios.get("amortizaciones_fe")
        if dep is not None and amo is not None:
            return dep.valor + amo.valor, f"Estado de flujos de efectivo, depreciaciones + amortizaciones ({dep.documento}, pág. {dep.pagina})"
        return None, "No se informa la depreciación y amortización"


def datos_ejercicio(session: Session, periodo: FiscalPeriod) -> DatosEjercicio:
    datos = DatosEjercicio(
        periodo=periodo,
        bs=compute_balance_sheet(session, periodo.id),
        inc=compute_income_statement(session, periodo.id),
    )
    for tipo in (TipoEstadoFinanciero.BALANCE, TipoEstadoFinanciero.RESULTADOS):
        for cuenta, valor in list_entries(session, periodo.id, tipo):
            codigo = cuenta.grupo_analisis
            if grupo_de_cuenta(cuenta) is None:
                if valor != CERO:
                    datos.sin_grupo.append((cuenta, valor, tipo))
                continue
            datos.grupos[codigo] = datos.grupos.get(codigo, CERO) + valor
            datos.lineas_por_grupo.setdefault(codigo, []).append((cuenta, valor))
            if tipo == TipoEstadoFinanciero.RESULTADOS:
                datos.grupos_con_signo[codigo] = datos.grupos_con_signo.get(codigo, CERO) + signo_resultado(cuenta) * valor
    datos.complementarios = {d.clave: d for d in list_datos_complementarios(session, periodo.id)}
    return datos


def datos_todos(session: Session) -> list[DatosEjercicio]:
    """Datos agregados de todos los ejercicios, en orden cronologico."""
    return [datos_ejercicio(session, p) for p in list_fiscal_periods(session)]
