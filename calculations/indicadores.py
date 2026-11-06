"""Indicadores financieros del trabajo ANF (secciones 5.6, 6.5, 8 y 9).

Unica definicion de cada indicador: nombre, formula, insumos, unidad,
interpretacion y funcion de calculo. El dashboard, los reportes, las
exportaciones y la comparacion con el trabajo ANF usan estas funciones;
ninguno repite una formula.

Criterios (los del trabajo, seccion 8.2 y 8.4):
  - Saldos al cierre de cada ejercicio, no promedios (no se dispone del
    balance de 2020 con detalle para promediar 2021).
  - Las rotaciones de cuentas por cobrar usan los ingresos ordinarios como
    aproximacion de las ventas a credito; el periodo de pago usa el costo de
    ventas como aproximacion de las compras (los estados no informan
    ventas a credito ni compras).
  - ROA y ROE con la utilidad neta total y el activo y patrimonio totales
    al cierre. El enfoque de la controladora usa la utilidad y el
    patrimonio atribuibles a los propietarios de la controladora.
Los valores se calculan con Decimal sin redondeo intermedio; el redondeo
solo se aplica al presentar. Unica excepcion, porque el trabajo la escribe asi
(9.3): el ciclo operativo suma EPI y PPC ya redondeados a 2 decimales y el CCE
resta de ese resultado el PPP a 2 decimales. La regla es la misma en todos los
ejercicios y solo depende de los importes.

Cuentas por cobrar: el indicador principal usa la linea comercial presentada,
la formula explicita de 9.3 en todos los ejercicios. La cartera comercial y
otras es un indicador distinto, tambien para todos los ejercicios; 8.2 B
publica su valor solo en 2023 (ver reports/secciones.py, bases_cxc).
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Callable

from calculations.dupont import factores_controladora, factores_total
from calculations.rubros import RUBROS, DatosEjercicio
from components.money import format_money, format_percent, redondear

CERO = Decimal("0")
CIEN = Decimal("100")
DIAS = Decimal("365")
DECIMALES_CICLO = 2  # precision de los operandos que 9.3 suma y resta

USD, VECES, PCT, DIAS_U = "USD", "veces", "%", "días"

# Categorias de presentacion
LIQUIDEZ = "Liquidez y capital de trabajo"
ACTIVIDAD = "Actividad (ciclo de efectivo)"
ENDEUDAMIENTO = "Endeudamiento y cobertura"
RENTABILIDAD = "Rentabilidad"
DUPONT = "DuPont (saldos al cierre)"
MERCADO = "Razones de mercado"
CATEGORIAS = (LIQUIDEZ, ACTIVIDAD, ENDEUDAMIENTO, RENTABILIDAD, DUPONT, MERCADO)

Resultado = tuple[Decimal | None, str | None, str | None]  # (valor, motivo si no calculable, nota)


@dataclass(frozen=True)
class Indicador:
    clave: str
    nombre: str
    categoria: str
    formula: str
    insumos: str
    unidad: str
    calcular: Callable[[DatosEjercicio], Resultado]
    usa: tuple[str, ...] = ()  # "rubro:X", "clase:AC", "grupo:X" (mapeo de cuentas a indicadores)
    seccion_anf: str = ""
    interpretar: Callable[[Decimal], str] | None = None


@dataclass
class ResultadoIndicador:
    indicador: Indicador
    anio: int
    valor: Decimal | None
    motivo: str | None = None
    nota: str | None = None

    @property
    def calculado(self) -> bool:
        return self.valor is not None


def _div(numerador: Decimal | None, denominador: Decimal | None, que: str) -> Resultado:
    if numerador is None or denominador is None:
        return None, f"Falta un dato para calcular {que}.", None
    if denominador == CERO:
        return None, f"El denominador de {que} es cero.", None
    return numerador / denominador, None, None


def _pct(r: Resultado) -> Resultado:
    valor, motivo, nota = r
    return (valor * CIEN if valor is not None else None), motivo, nota


def _dias(r: Resultado) -> Resultado:
    valor, motivo, nota = r
    return (valor * DIAS if valor is not None else None), motivo, nota


def _requiere_bs(d: DatosEjercicio) -> str | None:
    return None if d.bs.tiene_datos else "No hay Balance General capturado."


def _requiere_er(d: DatosEjercicio) -> str | None:
    return None if d.inc.tiene_datos else "No hay Estado de Resultados capturado."


def _con(*requisitos):
    """Decorador: devuelve 'no calculable' si falta algun estado requerido."""
    def envoltura(fn):
        def calcular(d: DatosEjercicio) -> Resultado:
            for req in requisitos:
                motivo = req(d)
                if motivo:
                    return None, motivo, None
            return fn(d)
        return calcular
    return envoltura


BS, ER = _requiere_bs, _requiere_er


# ---------------------------------------------------------------- calculos
@_con(BS)
def _ctn(d):
    return d.bs.activo_corriente.subtotal - d.bs.pasivo_corriente.subtotal, None, None


@_con(BS)
def _razon_corriente(d):
    return _div(d.bs.activo_corriente.subtotal, d.bs.pasivo_corriente.subtotal, "la razón corriente")


@_con(BS)
def _prueba_acida(d):
    return _div(d.bs.activo_corriente.subtotal - d.rubro("INVENTARIOS"), d.bs.pasivo_corriente.subtotal, "la prueba ácida")


@_con(BS)
def _razon_efectivo(d):
    return _div(d.rubro("EFECTIVO"), d.bs.pasivo_corriente.subtotal, "la razón de efectivo")


@_con(BS)
def _razon_tesoreria(d):
    return _pct(_div(d.rubro("TESORERIA"), d.bs.pasivo_corriente.subtotal, "la razón de tesorería"))


@_con(BS)
def _capitales_permanentes(d):
    return d.capitales_permanentes, None, None


@_con(BS)
def _fondo_maniobra_lp(d):
    return d.capitales_permanentes - d.bs.activo_no_corriente.subtotal, None, None


@_con(BS, ER)
def _rotacion_inventarios(d):
    return _div(d.inc.costo_ventas.subtotal, d.rubro("INVENTARIOS"), "la rotación de inventarios")


@_con(BS, ER)
def _ppi(d):
    return _dias(_div(d.rubro("INVENTARIOS"), d.inc.costo_ventas.subtotal, "el período promedio de inventario"))


@_con(BS, ER)
def _rotacion_cxc(d):
    valor, motivo, _ = _div(d.inc.ingresos_netos.subtotal, d.rubro("CXC_COMERCIALES_PRESENTADA"), "la rotación de cuentas por cobrar")
    return valor, motivo, RUBROS["CXC_COMERCIALES_PRESENTADA"].nota


@_con(BS, ER)
def _ppc(d):
    valor, motivo, _ = _dias(_div(d.rubro("CXC_COMERCIALES_PRESENTADA"), d.inc.ingresos_netos.subtotal, "el período promedio de cobro"))
    return valor, motivo, RUBROS["CXC_COMERCIALES_PRESENTADA"].nota


@_con(BS, ER)
def _rotacion_cxc_total(d):
    return _div(d.inc.ingresos_netos.subtotal, d.rubro("CXC_COMERCIALES_Y_OTRAS"), "la rotación de cuentas por cobrar totales")


@_con(BS, ER)
def _ppc_total(d):
    return _dias(_div(d.rubro("CXC_COMERCIALES_Y_OTRAS"), d.inc.ingresos_netos.subtotal, "el período de cobro (cartera total)"))


@_con(BS, ER)
def _ppp(d):
    valor, motivo, _ = _dias(_div(d.rubro("CXP_COMERCIALES_PRESENTADA"), d.inc.costo_ventas.subtotal, "el período promedio de pago"))
    return valor, motivo, RUBROS["CXP_COMERCIALES_PRESENTADA"].nota


def _ciclo_operativo(d):
    """CO = EPI + PPC con los operandos a 2 decimales: el desarrollo escrito de 9.3 (p. ej. 125.48 + 23.80 = 149.28)."""
    ppi, m1, _ = _ppi(d)
    ppc, m2, _ = _ppc(d)
    if ppi is None or ppc is None:
        return None, m1 or m2, None
    return redondear(ppi, DECIMALES_CICLO) + redondear(ppc, DECIMALES_CICLO), None, None


def _cce(d):
    """CCE = CO − PPP, con el CO anterior y el PPP a 2 decimales (9.3, p. ej. 169.72 − 191.12 = −21.40)."""
    co, m1, _ = _ciclo_operativo(d)
    ppp, m2, _ = _ppp(d)
    if co is None or ppp is None:
        return None, m1 or m2, None
    return co - redondear(ppp, DECIMALES_CICLO), None, None


@_con(BS, ER)
def _rotacion_activos(d):
    return _div(d.inc.ingresos_netos.subtotal, d.bs.total_activo, "la rotación de activos totales")


@_con(BS)
def _endeudamiento(d):
    return _pct(_div(d.bs.total_pasivo, d.bs.total_activo, "el índice de endeudamiento"))


@_con(BS)
def _pc_sobre_pasivo(d):
    return _pct(_div(d.bs.pasivo_corriente.subtotal, d.bs.total_pasivo, "la proporción de pasivo corriente"))


@_con(BS)
def _deuda_capital(d):
    return _div(d.bs.total_pasivo, d.bs.total_patrimonio, "la razón deuda-capital")


@_con(ER)
def _cobertura_intereses(d):
    valor, motivo, _ = _div(d.inc.utilidad_operativa, d.gastos_financieros_netos, "la razón de cargos de interés fijo")
    nota = None
    if d.inc.ingresos_financieros.subtotal != CERO:
        nota = "Gastos financieros netos de ingresos financieros (criterio del trabajo, Tabla 5)."
    return valor, motivo, nota


@_con(ER)
def _cobertura_intereses_bruta(d):
    if not d.tiene("GASTOS_FINANCIEROS"):
        return None, "El estado de resultados presenta solo el gasto financiero neto; no se puede separar el bruto.", None
    return _div(d.inc.utilidad_operativa, d.g("GASTOS_FINANCIEROS"), "la cobertura con gastos financieros brutos")


def _cobertura_pagos_fijos(d):
    """Criterio del trabajo (8.3 C): sin desglose de cuotas de arrendamiento ni de amortizacion del principal, ambos
    terminos valen cero en la formula y el indice iguala a la razon de cargos de interes fijo."""
    valor, motivo, _ = _cobertura_intereses(d)
    return valor, motivo, ("Los estados no desglosan las cuotas de arrendamiento ni la amortización obligatoria del principal: el índice "
                           "iguala a la razón de cargos de interés fijo (trabajo, 8.3 C). No mide la cobertura con esos pagos.")


@_con(ER)
def _margen_bruto(d):
    return _pct(_div(d.inc.utilidad_bruta, d.inc.ingresos_netos.subtotal, "el margen bruto"))


@_con(ER)
def _margen_operativo(d):
    return _pct(_div(d.inc.utilidad_operativa, d.inc.ingresos_netos.subtotal, "el margen operativo"))


@_con(ER)
def _margen_neto(d):
    return _pct(_div(d.inc.utilidad_neta, d.inc.ingresos_netos.subtotal, "el margen neto"))


@_con(BS, ER)
def _roa(d):
    return _pct(_div(d.inc.utilidad_neta, d.bs.total_activo, "el ROA"))


@_con(BS, ER)
def _roe(d):
    if d.bs.total_patrimonio <= CERO:
        return None, "El patrimonio es cero o negativo: el ROE no es interpretable.", None
    return _pct(_div(d.inc.utilidad_neta, d.bs.total_patrimonio, "el ROE"))


@_con(ER)
def _ebitda(d):
    da, fuente = d.depreciacion_amortizacion()
    if da is None:
        return None, fuente, None
    return d.inc.utilidad_operativa + da, None, f"Depreciación y amortización: {fuente}."


def _no_calculable(motivo: str):
    def calcular(d):
        return None, motivo, None
    return calcular


_MOTIVO_ACCIONES = ("Los documentos no informan el número (promedio ponderado) de acciones comunes; dividir entre el "
                    "capital social en dólares no sería correcto.")
_MOTIVO_PRECIO = ("No se dispone de un precio de mercado verificable de acciones comunes (CIALUTECH1 son certificados "
                  "de inversión, títulos de deuda) ni del número de acciones.")


# DuPont: las formulas estan solo en calculations/dupont.py. Estas funciones las
# exponen como indicadores (fuente de la comparacion con el trabajo ANF).
@_con(BS)
def _maf(d):
    maf = factores_total(d).maf_interpretable
    if maf is None:
        return None, "El patrimonio es cero o negativo.", None
    return maf, None, None


def _motivo_rsa(d, margen):
    if margen is None:
        return _margen_neto(d)[1]
    return _rotacion_activos(d)[1] or "El activo total es cero o negativo."


def _roa_dupont(d):
    f = factores_total(d)
    if f.rsa is None:
        return None, _motivo_rsa(d, f.margen_neto), None
    return f.rsa * CIEN, None, None


def _roe_dupont(d):
    roa, motivo, _ = _roa_dupont(d)
    maf, motivo_maf, _ = _maf(d)
    if roa is None or maf is None:
        return None, motivo or motivo_maf, None
    return factores_total(d).rsp * CIEN, None, None


@_con(BS, ER)
def _margen_neto_controladora(d):
    f, fuente = factores_controladora(d)
    nota = f"Utilidad atribuible: {fuente}."
    if f.margen_neto is None:
        que = "Falta un dato para calcular" if d.utilidad_controladora()[0] is None else "El denominador es cero en"
        return None, f"{que} el margen neto de la controladora.", nota
    return f.margen_neto * CIEN, None, nota


def _roa_controladora(d):
    margen, motivo, nota = _margen_neto_controladora(d)
    f = factores_controladora(d)[0]
    if margen is None or f.rsa is None:
        return None, motivo or _motivo_rsa(d, margen), nota
    return f.rsa * CIEN, None, nota


@_con(BS)
def _maf_controladora(d):
    maf = factores_controladora(d)[0].maf_interpretable
    if maf is None:
        return None, "El patrimonio de la controladora es cero o negativo.", None
    return maf, None, None


def _roe_controladora(d):
    roa, motivo, nota = _roa_controladora(d)
    maf, motivo_maf, _ = _maf_controladora(d)
    if roa is None or maf is None:
        return None, motivo or motivo_maf, nota
    return factores_controladora(d)[0].rsp * CIEN, None, nota


# ---------------------------------------------------------- interpretaciones
def _n(valor: Decimal) -> str:
    """Cifra de las interpretaciones: mismo redondeo y misma precision que las tablas."""
    return f"{redondear(valor, 2):,.2f}"


def _i_ctn(v):
    if v > 0:
        return "Positivo: el activo corriente supera al pasivo corriente; por sí solo no garantiza efectivo suficiente."
    if v < 0:
        return "Negativo: el pasivo corriente supera al activo corriente; presiona la liquidez, aunque no prueba insolvencia."
    return "Cero: no hay excedente contable de activos corrientes."


def _i_cobertura(nombre_activo: str, nombre_pasivo: str = "pasivo corriente"):
    def texto(v):
        return f"Por cada $1.00 de {nombre_pasivo} hay ${_n(v)} de {nombre_activo}; {'supera' if v > 1 else 'no alcanza'} la unidad."
    return texto


def _i_dias(que):
    return lambda v: f"{que} de aproximadamente {_n(v)} días."


def _i_veces(que):
    return lambda v: f"{que} {_n(v)} veces en el ejercicio."


def _i_pct(que):
    return lambda v: f"{que} {_n(v)}%."


INDICADORES: list[Indicador] = [
    # Liquidez y capital de trabajo
    Indicador("ctn", "Capital de trabajo neto (fondo de maniobra a corto plazo)", LIQUIDEZ, "Activo corriente − Pasivo corriente",
              "Total activo corriente; total pasivo corriente", USD, _ctn, ("clase:AC", "clase:PC"), "5.6 a, 6.5, 8.1 C, 9.2.1", _i_ctn),
    Indicador("razon_corriente", "Razón corriente (circulante)", LIQUIDEZ, "Activo corriente / Pasivo corriente",
              "Total activo corriente; total pasivo corriente", VECES, _razon_corriente, ("clase:AC", "clase:PC"), "5.6 b, 6.5, 8.1 A",
              _i_cobertura("activo corriente")),
    Indicador("prueba_acida", "Prueba ácida", LIQUIDEZ, "(Activo corriente − Inventarios) / Pasivo corriente",
              "Total activo corriente; inventarios; total pasivo corriente", VECES, _prueba_acida,
              ("clase:AC", "clase:PC", "rubro:INVENTARIOS"), "5.6 c, 6.5, 8.1 B", _i_cobertura("activo corriente sin inventarios")),
    Indicador("razon_efectivo", "Razón de efectivo", LIQUIDEZ, "Efectivo y equivalentes / Pasivo corriente",
              "Efectivo y equivalentes; total pasivo corriente", VECES, _razon_efectivo, ("rubro:EFECTIVO", "clase:PC"),
              "5.6 d (definida; el trabajo no presenta resultados)", _i_cobertura("efectivo")),
    Indicador("razon_tesoreria", "Razón de tesorería", LIQUIDEZ, "(Efectivo + inversiones y depósitos corrientes) / Pasivo corriente × 100",
              "Efectivo; certificados de depósito, bonos e inversiones corrientes; total pasivo corriente", PCT, _razon_tesoreria,
              ("rubro:TESORERIA", "clase:PC"), "9.1", lambda v: f"Por cada $100 de pasivo corriente hay ${_n(v)} de tesorería."),
    Indicador("capitales_permanentes", "Capitales permanentes", LIQUIDEZ, "Patrimonio + Pasivo no corriente",
              "Total patrimonio; total pasivo no corriente", USD, _capitales_permanentes, ("clase:PAT", "clase:PNC"), "9.2.2"),
    Indicador("fondo_maniobra_lp", "Fondo de maniobra a largo plazo", LIQUIDEZ, "Capitales permanentes − Activo no corriente",
              "Total patrimonio; total pasivo no corriente; total activo no corriente", USD, _fondo_maniobra_lp,
              ("clase:PAT", "clase:PNC", "clase:ANC"), "9.2.2", _i_ctn),
    # Actividad
    Indicador("rotacion_inventarios", "Rotación de inventarios", ACTIVIDAD, "Costo de ventas / Inventarios (saldo al cierre)",
              "Costo de ventas; inventarios", VECES, _rotacion_inventarios, ("rubro:INVENTARIOS", "grupo:COSTO_VENTAS"), "8.2 A",
              _i_veces("El inventario se renovó")),
    Indicador("ppi", "Período promedio (edad promedio) de inventario", ACTIVIDAD, "Inventarios / Costo de ventas × 365",
              "Inventarios; costo de ventas", DIAS_U, _ppi, ("rubro:INVENTARIOS", "grupo:COSTO_VENTAS"), "8.2 A, 9.3",
              _i_dias("Permanencia del inventario")),
    Indicador("rotacion_cxc", "Rotación de cuentas por cobrar comerciales", ACTIVIDAD,
              "Ingresos ordinarios / Cuentas por cobrar comerciales (línea presentada)",
              "Ingresos ordinarios (aproximación de las ventas a crédito); cuentas por cobrar comerciales", VECES, _rotacion_cxc,
              ("rubro:CXC_COMERCIALES_PRESENTADA", "grupo:INGRESOS_ORDINARIOS"), "8.2 B", _i_veces("La cartera rotó")),
    Indicador("ppc", "Período promedio de cobro", ACTIVIDAD, "Cuentas por cobrar comerciales / Ingresos ordinarios × 365",
              "Cuentas por cobrar comerciales (línea presentada); ingresos ordinarios", DIAS_U, _ppc,
              ("rubro:CXC_COMERCIALES_PRESENTADA", "grupo:INGRESOS_ORDINARIOS"), "8.2 B, 9.3", _i_dias("Plazo de cobro")),
    Indicador("rotacion_cxc_total", "Rotación de cuentas por cobrar comerciales y otras", ACTIVIDAD,
              "Ingresos ordinarios / (Cuentas por cobrar comerciales + otras cuentas por cobrar corrientes)",
              "Ingresos ordinarios; cuentas por cobrar comerciales y otras", VECES, _rotacion_cxc_total,
              ("rubro:CXC_COMERCIALES_Y_OTRAS", "grupo:INGRESOS_ORDINARIOS"), "8.2 B (variante homogénea)", _i_veces("La cartera total rotó")),
    Indicador("ppc_total", "Período de cobro (cartera comercial y otras)", ACTIVIDAD,
              "(Cuentas por cobrar comerciales + otras) / Ingresos ordinarios × 365",
              "Cuentas por cobrar comerciales y otras; ingresos ordinarios", DIAS_U, _ppc_total,
              ("rubro:CXC_COMERCIALES_Y_OTRAS", "grupo:INGRESOS_ORDINARIOS"), "8.2 B (variante homogénea)", _i_dias("Plazo de cobro")),
    Indicador("ppp", "Período promedio de pago", ACTIVIDAD, "Cuentas por pagar comerciales / Costo de ventas × 365",
              "Cuentas por pagar comerciales (línea presentada); costo de ventas (aproximación de las compras)", DIAS_U, _ppp,
              ("rubro:CXP_COMERCIALES_PRESENTADA", "grupo:COSTO_VENTAS"), "9.3", _i_dias("Plazo de pago a proveedores")),
    Indicador("ciclo_operativo", "Ciclo operativo", ACTIVIDAD, "PPI + PPC, ambos a 2 decimales", "Período promedio de inventario; período promedio de cobro",
              DIAS_U, _ciclo_operativo, ("rubro:INVENTARIOS", "rubro:CXC_COMERCIALES_PRESENTADA"), "8.2 C, 9.3", _i_dias("Ciclo operativo")),
    Indicador("cce", "Ciclo de conversión del efectivo", ACTIVIDAD, "Ciclo operativo − PPP, con PPP a 2 decimales", "Ciclo operativo; período promedio de pago",
              DIAS_U, _cce, ("rubro:INVENTARIOS", "rubro:CXC_COMERCIALES_PRESENTADA", "rubro:CXP_COMERCIALES_PRESENTADA"), "5.6 k, 9.3",
              lambda v: f"Ciclo de {_n(v)} días; {'negativo: los proveedores financian el ciclo operativo' if v < 0 else 'días que la empresa financia con recursos propios o deuda'}."),
    Indicador("rotacion_activos", "Rotación de activos totales", ACTIVIDAD, "Ingresos ordinarios / Activo total",
              "Ingresos ordinarios; total activo", VECES, _rotacion_activos, ("clase:AC", "clase:ANC", "grupo:INGRESOS_ORDINARIOS"),
              "8.2 D, 9.5", lambda v: f"Se generaron ${_n(v)} de ingresos por cada $1.00 de activos."),
    # Endeudamiento
    Indicador("endeudamiento", "Índice de endeudamiento", ENDEUDAMIENTO, "Pasivo total / Activo total × 100",
              "Total pasivo; total activo", PCT, _endeudamiento, ("clase:PC", "clase:PNC", "clase:AC", "clase:ANC"), "8.3 A",
              _i_pct("Proporción de los activos financiada con pasivos:")),
    Indicador("pc_sobre_pasivo", "Pasivo corriente sobre pasivo total", ENDEUDAMIENTO, "Pasivo corriente / Pasivo total × 100",
              "Total pasivo corriente; total pasivo", PCT, _pc_sobre_pasivo, ("clase:PC", "clase:PNC"), "8.3 A (texto)",
              _i_pct("Parte del pasivo exigible a corto plazo:")),
    Indicador("deuda_capital", "Razón deuda-capital patrimonial", ENDEUDAMIENTO, "Pasivo total / Patrimonio total",
              "Total pasivo; total patrimonio", VECES, _deuda_capital, ("clase:PC", "clase:PNC", "clase:PAT"), "8.3 D",
              lambda v: f"${_n(v)} de pasivo por cada $1.00 de patrimonio."),
    Indicador("cobertura_intereses", "Razón de cargos de interés fijo", ENDEUDAMIENTO,
              "Utilidad de operación / Gastos financieros netos", "Utilidad de operación; gastos financieros − ingresos financieros",
              VECES, _cobertura_intereses, ("grupo:GASTOS_FINANCIEROS", "grupo:GASTOS_FINANCIEROS_NETOS", "grupo:INGRESOS_FINANCIEROS"),
              "8.3 B", lambda v: f"La utilidad de operación cubre {_n(v)} veces los gastos financieros netos."),
    Indicador("cobertura_intereses_bruta", "Cobertura con gastos financieros brutos", ENDEUDAMIENTO,
              "Utilidad de operación / Gastos financieros (brutos)", "Utilidad de operación; gastos financieros", VECES,
              _cobertura_intereses_bruta, ("grupo:GASTOS_FINANCIEROS",), "Complementario (no figura en el trabajo)",
              lambda v: f"La utilidad de operación cubre {_n(v)} veces los gastos financieros brutos."),
    Indicador("cobertura_pagos_fijos", "Índice de cobertura de pagos fijos", ENDEUDAMIENTO,
              "(UAII + arrendamientos) / (intereses + arrendamientos + principal / (1 − t)); sin desglose = UAII / intereses",
              "Utilidad de operación; gastos financieros netos (arrendamientos y principal no informados)",
              VECES, _cobertura_pagos_fijos, ("grupo:GASTOS_FINANCIEROS", "grupo:GASTOS_FINANCIEROS_NETOS", "grupo:INGRESOS_FINANCIEROS"),
              "8.3 C", lambda v: f"Iguala a la razón de cargos de interés fijo: {_n(v)} veces, por falta de desglose."),
    # Rentabilidad
    Indicador("margen_bruto", "Margen de utilidad bruta", RENTABILIDAD, "Utilidad bruta / Ingresos ordinarios × 100",
              "Utilidad bruta; ingresos ordinarios", PCT, _margen_bruto, ("grupo:INGRESOS_ORDINARIOS", "grupo:COSTO_VENTAS"), "8.4 A",
              lambda v: f"De cada $100 de ingresos quedaron ${_n(v)} tras el costo de ventas."),
    Indicador("margen_operativo", "Margen de utilidad operativa", RENTABILIDAD, "Utilidad de operación / Ingresos ordinarios × 100",
              "Utilidad de operación; ingresos ordinarios", PCT, _margen_operativo, ("grupo:INGRESOS_ORDINARIOS",), "8.4 B",
              lambda v: f"De cada $100 de ingresos quedaron ${_n(v)} de resultado de operación."),
    Indicador("margen_neto", "Margen de utilidad neta", RENTABILIDAD, "Utilidad neta / Ingresos ordinarios × 100",
              "Utilidad neta del ejercicio; ingresos ordinarios", PCT, _margen_neto, ("grupo:INGRESOS_ORDINARIOS",), "8.4 C, 9.5",
              lambda v: f"De cada $100 de ingresos quedaron ${_n(v)} de utilidad neta."),
    Indicador("roa", "Rendimiento sobre los activos totales (ROA)", RENTABILIDAD, "Utilidad neta / Activo total al cierre × 100",
              "Utilidad neta; total activo", PCT, _roa, ("clase:AC", "clase:ANC"), "8.4 E",
              lambda v: f"${_n(v)} de utilidad neta por cada $100 de activos."),
    Indicador("roe", "Retorno sobre el patrimonio (ROE)", RENTABILIDAD, "Utilidad neta / Patrimonio total al cierre × 100",
              "Utilidad neta; total patrimonio (incluye participaciones no controladoras)", PCT, _roe, ("clase:PAT",), "8.4 F",
              lambda v: f"${_n(v)} de utilidad neta por cada $100 de patrimonio contable."),
    Indicador("ebitda", "EBITDA", RENTABILIDAD, "Utilidad de operación + Depreciación y amortización",
              "Utilidad de operación; depreciación y amortización (estado de resultados o flujo de efectivo)", USD, _ebitda,
              ("grupo:DEPRECIACION_AMORTIZACION",), "6.7 (texto, 2025)"),
    Indicador("eps", "Ganancia por acción (EPS)", MERCADO, "Utilidad atribuible a accionistas comunes / Promedio ponderado de acciones",
              "Número de acciones (no disponible)", USD, _no_calculable(_MOTIVO_ACCIONES), (), "8.4 D"),
    Indicador("per", "Relación precio/ganancias (P/E)", MERCADO, "Precio de mercado por acción / EPS",
              "Precio por acción y EPS (no disponibles)", VECES, _no_calculable(_MOTIVO_PRECIO), (), "8.5 A"),
    Indicador("ml", "Razón mercado/libro (M/L)", MERCADO, "Precio de mercado por acción / Valor contable por acción",
              "Precio y número de acciones (no disponibles)", VECES, _no_calculable(_MOTIVO_PRECIO), (), "8.5 B"),
    # DuPont al cierre (enfoque del trabajo, 9.5 y 9.6)
    Indicador("maf", "Multiplicador del apalancamiento financiero (MAF)", DUPONT, "Activo total / Patrimonio total",
              "Total activo; total patrimonio", VECES, _maf, ("clase:PAT",), "9.6",
              lambda v: f"Los activos equivalen a {_n(v)} veces el patrimonio."),
    Indicador("roa_dupont", "RSA (ROA) por DuPont", DUPONT, "Margen de utilidad neta × Rotación de activos totales",
              "Margen neto; rotación de activos", PCT, _roa_dupont, (), "9.5"),
    Indicador("roe_dupont", "RSP (ROE) por DuPont modificado", DUPONT, "RSA × MAF", "RSA; MAF", PCT, _roe_dupont, (), "9.6"),
    Indicador("margen_neto_controladora", "Margen neto (controladora)", DUPONT,
              "Utilidad atribuible a la controladora / Ingresos ordinarios × 100",
              "Utilidad atribuible a los propietarios de la controladora; ingresos ordinarios", PCT, _margen_neto_controladora,
              ("grupo:NO_CONTROLADORAS",), "9.6 (controladora)"),
    Indicador("roa_controladora", "RSA (controladora)", DUPONT, "Margen neto (controladora) × Rotación de activos",
              "Margen neto de la controladora; rotación de activos", PCT, _roa_controladora, (), "9.6 (controladora)"),
    Indicador("maf_controladora", "MAF (controladora)", DUPONT, "Activo total / Patrimonio atribuible a la controladora",
              "Total activo; total patrimonio − participaciones no controladoras", VECES, _maf_controladora,
              ("grupo:NO_CONTROLADORAS",), "9.6 (controladora)"),
    Indicador("roe_controladora", "RSP (ROE) de la controladora", DUPONT, "RSA (controladora) × MAF (controladora)",
              "RSA y MAF de la controladora", PCT, _roe_controladora, (), "9.6 (controladora)"),
]
POR_CLAVE: dict[str, Indicador] = {i.clave: i for i in INDICADORES}


def calcular(datos: DatosEjercicio, clave: str) -> ResultadoIndicador:
    indicador = POR_CLAVE[clave]
    valor, motivo, nota = indicador.calcular(datos)
    return ResultadoIndicador(indicador, datos.anio, valor, motivo if valor is None else None, nota)


def calcular_todos(lista: list[DatosEjercicio], categoria: str | None = None) -> list[tuple[Indicador, dict[int, ResultadoIndicador]]]:
    """[(indicador, {anio: resultado})] para los ejercicios con datos."""
    seleccion = [i for i in INDICADORES if categoria is None or i.categoria == categoria]
    con_datos = [d for d in lista if d.tiene_datos]
    return [(i, {d.anio: calcular(d, i.clave) for d in con_datos}) for i in seleccion]


def formatear(unidad: str, valor: Decimal | None) -> str:
    if valor is None:
        return "No calculable"
    if unidad == USD:
        return format_money(valor, "USD")
    if unidad == PCT:
        return format_percent(valor)
    if unidad == DIAS_U:
        return f"{redondear(valor, 2):,.2f} días"
    return f"{redondear(valor, 2):,.2f} veces"


def interpretacion(resultado: ResultadoIndicador) -> str:
    if resultado.valor is None:
        return resultado.motivo or "No calculable."
    if resultado.indicador.interpretar is None:
        return ""
    return resultado.indicador.interpretar(resultado.valor)


def indicadores_de_grupo(codigo_grupo: str, clase: str) -> list[Indicador]:
    """Indicadores en los que participa un grupo de analisis (directamente,
    por un rubro que lo contiene o por el total de su clase)."""
    rubros = {r.codigo for r in RUBROS.values() if codigo_grupo in r.grupos}
    resultado = []
    for ind in INDICADORES:
        for uso in ind.usa:
            tipo, _, codigo = uso.partition(":")
            if (tipo == "grupo" and codigo == codigo_grupo) or (tipo == "rubro" and codigo in rubros) or (tipo == "clase" and codigo == clase):
                resultado.append(ind)
                break
    return resultado
