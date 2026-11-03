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

from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy.orm import Session

from calculations.balance_sheet import BalanceSheetResult, compute_balance_sheet
from calculations.income_statement import IncomeStatementResult, compute_income_statement
from database.enums import CategoriaPrincipal as Cat
from database.enums import EfectoCuenta as Efecto
from database.enums import TipoEstadoFinanciero
from database.models import Account, DatoComplementario, FiscalPeriod
from database.repositories import list_datos_complementarios, list_entries, list_fiscal_periods

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


@dataclass(frozen=True)
class Rubro:
    codigo: str
    nombre: str
    grupos: tuple[str, ...]
    nota: str = ""


_RUBROS = [
    Rubro("EFECTIVO", "Efectivo y equivalentes de efectivo", ("EFECTIVO",)),
    Rubro("INVERSIONES_CP", "Inversiones y depósitos a plazo (corrientes)", ("INVERSIONES_CP",)),
    Rubro("TESORERIA", "Tesorería y valores negociables (efectivo + inversiones corrientes)", ("EFECTIVO", "INVERSIONES_CP")),
    Rubro("CXC_COMERCIALES_PRESENTADA", "Cuentas por cobrar comerciales (línea presentada)",
          ("CXC_COMERCIALES", "DEUDORES_COMERCIALES_OTRAS"),
          "2021–2023: solo cuentas por cobrar comerciales; 2024–2025 el estado presenta una sola línea "
          "'Deudores comerciales y otras cuentas por cobrar'. La base no es homogénea entre ambos períodos."),
    Rubro("CXC_COMERCIALES_Y_OTRAS", "Cuentas por cobrar comerciales y otras (corrientes)",
          ("CXC_COMERCIALES", "OTRAS_CXC_CP", "DEUDORES_COMERCIALES_OTRAS"),
          "Base homogénea 2021–2025: comerciales + otras cuentas por cobrar corrientes."),
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
          "Criterio del trabajo ANF (Tabla 5): excluye el deterioro de cuentas por cobrar y los otros ingresos."),
    Rubro("OTROS_INGRESOS_GASTOS", "Otros ingresos o gastos (neto)", ("OTROS_INGRESOS_OPERATIVOS", "OTROS_NO_OPERATIVOS"),
          "2021–2023 se presentan dentro de la utilidad de operación; 2024–2025, después del resultado financiero."),
]
RUBROS: dict[str, Rubro] = {r.codigo: r for r in _RUBROS}


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

    def rubro(self, codigo: str) -> Decimal:
        return sum((self.g(g) for g in RUBROS[codigo].grupos), CERO)

    def rubro_tiene(self, codigo: str) -> bool:
        return any(self.tiene(g) for g in RUBROS[codigo].grupos)

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
        for clave, origen in (("utilidad_controladora_ecp", "Estado de cambios en el patrimonio"),
                              ("utilidad_controladora_er", "Estado de resultados")):
            dato = self.complementarios.get(clave)
            if dato is not None:
                return dato.valor, f"{origen} ({dato.documento}, pág. {dato.pagina})"
        if not self.inc.tiene_datos:
            return None, "Sin Estado de Resultados"
        if self.g("NO_CONTROLADORAS") == CERO:
            return self.inc.utilidad_neta, (
                "Supuesto: los estados no presentan participaciones no controladoras ni atribución de la utilidad; "
                "se iguala a la utilidad neta del ejercicio")
        return None, "Hay participaciones no controladoras y el documento no informa la utilidad atribuible"

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
            if not codigo or codigo not in GRUPOS:
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
