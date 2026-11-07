"""Analisis horizontal y vertical comparativo de varios ejercicios.

CONCEPTOS es el registro unico de los importes que se comparan entre
ejercicios (totales del Balance y del Estado de Resultados, rubros y
lineas con signo). Lo usan el analisis horizontal, el vertical comparativo,
el dashboard y la comparacion con el trabajo ANF.

Analisis horizontal (trabajo ANF, seccion 6.3):
  Variacion absoluta = Vt − Vt−1
  Variacion relativa = (Vt − Vt−1) / Vt−1 × 100
Si el valor anterior es cero la variacion relativa no existe; si es
negativo, el cociente cambia de signo y no es interpretable: en ambos casos
se devuelve None con la causa, nunca un porcentaje enganoso.

Una partida sin cuentas en un ejercicio no vale cero: queda sin dato. Solo un
importe registrado en cero es un saldo cero. Cuando los grupos de una familia
de presentacion (calculations/rubros.py) se reorganizan entre dos ejercicios,
la comparacion se marca como no confirmada: los grupos afectados no calculan
variacion y las sumas que cubren toda la familia la calculan como agrupacion
analitica, con su advertencia. La regla se deduce de los datos de cada par de
ejercicios; no depende de ningun anio.

Analisis vertical comparativo (seccion 7): Estado de Resultados sobre los
ingresos ordinarios, con signo (costos y gastos negativos, como en el
trabajo); Balance General sobre el activo total.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Callable

from calculations.rubros import CLASE_BALANCE, FAMILIA_DE_GRUPO, GRUPOS, RUBROS, DatosEjercicio, FamiliaPresentacion, signo_resultado

CERO = Decimal("0")
CIEN = Decimal("100")

CUENTA, SUBTOTAL, TOTAL = "cuenta", "subtotal", "total"


@dataclass(frozen=True)
class Concepto:
    clave: str
    etiqueta: str
    obtener: Callable[[DatosEjercicio], Decimal | None]
    tipo: str = CUENTA
    nota: str = ""


def _bs(fn):
    return lambda d: fn(d) if d.bs.tiene_datos else None


def _er(fn):
    return lambda d: fn(d) if d.inc.tiene_datos else None


def _rubro(codigo: str):
    return lambda d: d.rubro_registrado(codigo)


def _con_signo(*grupos: str):
    """Linea que un estado puede no presentar: sin cuentas es «no aplicable» y vale 0.00 %, como en la tabla 7.1 del trabajo."""
    return _er(lambda d: d.rubro_con_signo(*grupos))


def _con_signo_requerida(*grupos: str):
    """Linea que todo estado de resultados presenta: sin cuentas es un dato faltante, no un cero."""
    return _er(lambda d: d.rubro_con_signo(*grupos) if any(d.tiene(g) for g in grupos) else None)


_LISTA = [
    # Balance General
    Concepto("activo_corriente", "Total activo corriente", _bs(lambda d: d.activo_corriente), SUBTOTAL),
    Concepto("activo_no_corriente", "Total activo no corriente", _bs(lambda d: d.activo_no_corriente), SUBTOTAL),
    Concepto("total_activo", "Total activo", _bs(lambda d: d.activo_total), TOTAL),
    Concepto("pasivo_corriente", "Total pasivo corriente", _bs(lambda d: d.pasivo_corriente), SUBTOTAL),
    Concepto("pasivo_no_corriente", "Total pasivo no corriente", _bs(lambda d: d.pasivo_no_corriente), SUBTOTAL),
    Concepto("total_pasivo", "Total pasivo", _bs(lambda d: d.pasivo_total), TOTAL),
    Concepto("total_patrimonio", "Total patrimonio", _bs(lambda d: d.patrimonio_total), TOTAL),
    Concepto("patrimonio_controladora", "Patrimonio atribuible a la controladora", _bs(lambda d: d.patrimonio_controladora if d.patrimonio_total is not None else None), SUBTOTAL),
    Concepto("total_pasivo_patrimonio", "Total pasivo y patrimonio", _bs(lambda d: d.bs.total_pasivo_patrimonio if d.pasivo_total is not None and d.patrimonio_total is not None else None), TOTAL),
    # Estado de resultados (importes positivos, como se capturan)
    Concepto("ingresos", "Ingresos ordinarios", _er(lambda d: d.ingresos), SUBTOTAL),
    Concepto("costo_ventas", "Costo de ventas", _er(lambda d: d.costo_ventas)),
    Concepto("utilidad_bruta", "Utilidad bruta", _er(lambda d: d.utilidad_bruta), TOTAL),
    Concepto("gastos_operativos_anf", RUBROS["GASTOS_OPERATIVOS_ANF"].nombre, _er(lambda d: d.rubro_registrado("GASTOS_OPERATIVOS_ANF")),
             nota=RUBROS["GASTOS_OPERATIVOS_ANF"].nota),
    Concepto("utilidad_operativa", "Utilidad de operación", _er(lambda d: d.utilidad_operativa), TOTAL),
    Concepto("ingresos_financieros", "Ingresos financieros", _er(lambda d: d.inc.ingresos_financieros.subtotal)),
    Concepto("gastos_financieros", "Gastos financieros (como se presentan)", _er(lambda d: d.inc.gastos_financieros.subtotal)),
    Concepto("gastos_financieros_netos", "Gastos financieros netos", _er(lambda d: d.gastos_financieros_netos_registrados),
             nota="Gastos financieros − ingresos financieros. 2021–2023 el estado ya presenta el neto."),
    Concepto("utilidad_antes_impuestos", "Utilidad antes de impuestos", _er(lambda d: d.utilidad_antes_impuestos), TOTAL),
    Concepto("impuesto_renta", "Impuesto sobre la renta", _er(lambda d: d._registrado(d.inc.impuesto_renta))),
    Concepto("utilidad_neta", "Utilidad neta del ejercicio", _er(lambda d: d.utilidad_neta), TOTAL),
    Concepto("utilidad_controladora", "Utilidad atribuible a la controladora", _er(lambda d: d.utilidad_controladora()[0])),
    Concepto("depreciacion_amortizacion_total", "Depreciación y amortización", lambda d: d.depreciacion_amortizacion()[0]),
    # Lineas con signo para el vertical del Estado de Resultados (seccion 7.1)
    Concepto("s_ingresos", "Ingresos ordinarios", _er(lambda d: d.ingresos), SUBTOTAL),
    Concepto("s_costo_ventas", "Costo de ventas", _con_signo_requerida("COSTO_VENTAS")),
    Concepto("s_utilidad_bruta", "Ganancia bruta", _er(lambda d: d.utilidad_bruta), TOTAL),
    Concepto("s_gastos_administracion", "Gastos de administración", _con_signo_requerida("GASTOS_ADMINISTRACION")),
    Concepto("s_gastos_venta", "Gastos de venta y despacho o distribución", _con_signo_requerida("GASTOS_VENTA")),
    Concepto("s_deterioro_cxc", "Deterioro de cuentas por cobrar", _con_signo("DETERIORO_CXC")),
    Concepto("s_gastos_personal", "Gastos de personal", _con_signo("GASTOS_PERSONAL")),
    Concepto("s_depreciacion_amortizacion", "Depreciación y amortización (en el estado de resultados)",
             _con_signo("DEPRECIACION_AMORTIZACION")),
    Concepto("s_otros_ingresos_gastos", "Otros ingresos o gastos", _con_signo("OTROS_INGRESOS_OPERATIVOS", "OTROS_NO_OPERATIVOS"),
             nota=RUBROS["OTROS_INGRESOS_GASTOS"].nota),
    Concepto("s_utilidad_operativa", "Resultado operativo", _er(lambda d: d.utilidad_operativa), TOTAL),
    Concepto("s_ingresos_financieros", "Ingresos financieros", _con_signo("INGRESOS_FINANCIEROS")),
    Concepto("s_gastos_financieros", "Gastos financieros", _con_signo_requerida("GASTOS_FINANCIEROS", "GASTOS_FINANCIEROS_NETOS"),
             nota="2021–2023: gasto financiero neto (así se presenta); 2024–2025: gasto financiero bruto."),
    Concepto("s_utilidad_antes_impuestos", "Resultado antes de impuestos", _er(lambda d: d.utilidad_antes_impuestos), TOTAL),
    Concepto("s_impuesto_renta", "Impuesto sobre la renta", _con_signo_requerida("IMPUESTO_RENTA")),
    Concepto("s_utilidad_neta", "Ganancia o resultado neto", _er(lambda d: d.utilidad_neta), TOTAL),
]
CONCEPTOS: dict[str, Concepto] = {c.clave: c for c in _LISTA}
for _r in RUBROS.values():
    CONCEPTOS[f"rubro:{_r.codigo}"] = Concepto(f"rubro:{_r.codigo}", _r.nombre, _rubro(_r.codigo), nota=_r.nota)
for _g in GRUPOS.values():
    CONCEPTOS[f"grupo:{_g.codigo}"] = Concepto(
        f"grupo:{_g.codigo}", _g.nombre, (lambda codigo: lambda d: d.g(codigo) if d.tiene(codigo) else None)(_g.codigo))
# Este grupo reune cuentas de ingreso y de gasto: sumar sus importes capturados (positivos)
# presentaria un gasto como un aumento del ingreso. Se compara el neto con su signo.
CONCEPTOS["grupo:OTROS_NO_OPERATIVOS"] = Concepto(
    "grupo:OTROS_NO_OPERATIVOS", GRUPOS["OTROS_NO_OPERATIVOS"].nombre,
    lambda d: d.rubro_con_signo("OTROS_NO_OPERATIVOS") if d.tiene("OTROS_NO_OPERATIVOS") else None)

# Seleccion del trabajo ANF (Tablas 3 a 5): rubros clave y totales.
CLAVES_HORIZONTAL_ANF = (
    "rubro:EFECTIVO", "rubro:CXC_COMERCIALES_PRESENTADA", "rubro:CXC_COMERCIALES_Y_OTRAS", "rubro:INVENTARIOS",
    "activo_corriente", "pasivo_corriente", "total_activo", "total_pasivo", "total_patrimonio",
    "ingresos", "costo_ventas", "utilidad_bruta", "gastos_operativos_anf", "utilidad_operativa",
    "gastos_financieros_netos", "utilidad_neta",
)
# Filas de las Tablas 3, 4 y 5 del trabajo, en su orden. La Tabla 3 usa la linea de cuentas por
# cobrar comerciales; la Tabla 4, comerciales y otras (nota de la Tabla 4).
CLAVES_TABLA_3 = ("rubro:EFECTIVO", "rubro:CXC_COMERCIALES_PRESENTADA", "rubro:INVENTARIOS", "activo_corriente",
                  "pasivo_corriente", "total_activo", "total_pasivo", "total_patrimonio")
CLAVES_TABLA_4 = ("rubro:EFECTIVO", "rubro:CXC_COMERCIALES_Y_OTRAS", "rubro:INVENTARIOS", "activo_corriente",
                  "pasivo_corriente", "total_activo", "total_pasivo", "total_patrimonio")
CLAVES_TABLA_5 = ("ingresos", "costo_ventas", "utilidad_bruta", "gastos_operativos_anf", "utilidad_operativa",
                  "gastos_financieros_netos", "utilidad_neta")
CLAVES_RUBROS_BG = ("rubro:EFECTIVO", "rubro:CXC_COMERCIALES_PRESENTADA", "rubro:CXC_COMERCIALES_Y_OTRAS", "rubro:INVENTARIOS",
                    "activo_corriente", "activo_no_corriente", "total_activo", "pasivo_corriente", "pasivo_no_corriente",
                    "total_pasivo", "total_patrimonio")
CLAVES_RUBROS_ER = ("ingresos", "costo_ventas", "utilidad_bruta", "gastos_operativos_anf", "utilidad_operativa",
                    "gastos_financieros_netos", "utilidad_antes_impuestos", "impuesto_renta", "utilidad_neta")
CLAVES_VERTICAL_ER = (
    "s_ingresos", "s_costo_ventas", "s_utilidad_bruta", "s_gastos_administracion", "s_gastos_venta", "s_deterioro_cxc",
    "s_gastos_personal", "s_depreciacion_amortizacion", "s_otros_ingresos_gastos", "s_utilidad_operativa",
    "s_ingresos_financieros", "s_gastos_financieros", "s_utilidad_antes_impuestos", "s_impuesto_renta", "s_utilidad_neta",
)
CLAVES_VERTICAL_BG = (
    "activo_corriente", "rubro:INVENTARIOS", "activo_no_corriente", "total_activo", "pasivo_corriente",
    "pasivo_no_corriente", "total_pasivo", "total_patrimonio",
)
# Denominaciones de las tablas 7.1 y 7.2 del trabajo, donde difieren de la etiqueta general.
ETIQUETAS_VERTICAL = {
    "activo_corriente": "Activos corrientes", "activo_no_corriente": "Activos no corrientes", "total_activo": "Total activos",
    "pasivo_corriente": "Pasivos corrientes", "pasivo_no_corriente": "Pasivos no corrientes", "total_pasivo": "Total pasivos",
    "total_patrimonio": "Patrimonio", "s_depreciacion_amortizacion": "Depreciación y amortización",
    "s_impuesto_renta": "Impuestos sobre la renta",
}


def valor(concepto: str, d: DatosEjercicio) -> Decimal | None:
    return CONCEPTOS[concepto].obtener(d)


# ------------------------------------------------------------- horizontal
def variacion(actual: Decimal | None, anterior: Decimal | None) -> tuple[Decimal | None, Decimal | None, str]:
    """(variacion absoluta, variacion relativa %, nota). La relativa es None
    si la base es cero o negativa (no se inventa un porcentaje)."""
    if actual is None or anterior is None:
        return None, None, "Sin dato en uno de los ejercicios."
    absoluta = actual - anterior
    if anterior == CERO:
        return absoluta, None, "Base cero: la variación relativa no se puede calcular."
    if anterior < CERO:
        return absoluta, None, "Base negativa: la variación relativa no es interpretable; use la variación absoluta."
    return absoluta, absoluta / anterior * CIEN, ""


# ------------------------------------------------- comparabilidad entre presentaciones
ADVERTENCIA_ANALITICA = "Agrupación analítica; comparabilidad no confirmada."
AGRUPADA, NO_COMPARABLE, ANALITICA, INFORMATIVA = "agrupada", "no_comparable", "analitica", "informativa"
COMPOSICION_DISTINTA = "composicion_distinta"  # se calcula, pero la partida no contiene lo mismo en ambos ejercicios
# Por que una celda no tiene valor. Cada causa se muestra con su propio texto.
SIN_DATO, NO_CALCULABLE, SIN_COMPARAR = "Sin dato", "No calculable", "No comparable"
SIN_VARIACION_CALCULADA = (AGRUPADA, NO_COMPARABLE)  # estados en los que no se calcula la variacion
UMBRAL_CAPITAL_SOCIAL = Decimal("0.01")  # % bajo el cual un cambio del capital social se senala para confirmarlo


@dataclass(frozen=True)
class Comparabilidad:
    estado: str
    nota: str


def _grupos_presentes(familia: FamiliaPresentacion, d: DatosEjercicio) -> set[str]:
    return {g for g in familia.grupos if d.tiene(g)}


def _cuentas_del_grupo(codigo: str, d: DatosEjercicio) -> set[int]:
    return {cuenta.id for cuenta, _ in d.lineas_por_grupo.get(codigo, [])}


def presentacion_cambia(familia: FamiliaPresentacion, anterior: DatosEjercicio, actual: DatosEjercicio) -> bool:
    """La familia se reorganiza si una linea deja de presentarse y otra empieza a presentarse, o si
    una o varias cambian mientras otra sigue con el mismo nombre pero con cuentas distintas."""
    antes, despues = _grupos_presentes(familia, anterior), _grupos_presentes(familia, actual)
    salen, entran = antes - despues, despues - antes
    if not salen and not entran:
        return False
    if salen and entran:
        return True
    return any(_cuentas_del_grupo(g, anterior).isdisjoint(_cuentas_del_grupo(g, actual)) for g in antes & despues)


def _nombres(grupos: set[str], familia: FamiliaPresentacion) -> str:
    return ", ".join(f"«{GRUPOS[g].nombre}»" for g in familia.grupos if g in grupos)


def comparabilidad_grupo(codigo: str, anterior: DatosEjercicio, actual: DatosEjercicio) -> Comparabilidad | None:
    """Estado de un grupo de analisis entre dos ejercicios (None: nada que advertir)."""
    familia = FAMILIA_DE_GRUPO.get(codigo)
    if familia is None or not presentacion_cambia(familia, anterior, actual):
        return None
    en_anterior, en_actual = anterior.tiene(codigo), actual.tiene(codigo)
    if en_anterior and not en_actual:
        destino = _nombres(_grupos_presentes(familia, actual), familia)
        relacion = f"; puede estar comprendida en {destino}" if destino else ""
        return Comparabilidad(AGRUPADA, f"En {actual.anio} no se presenta por separado{relacion}. {ADVERTENCIA_ANALITICA}")
    if en_actual and not en_anterior:
        origen = _nombres(_grupos_presentes(familia, anterior), familia)
        relacion = f"; puede corresponder a {origen}" if origen else ""
        return Comparabilidad(AGRUPADA, f"En {anterior.anio} no se presenta con esta denominación{relacion}. {ADVERTENCIA_ANALITICA}")
    if en_anterior and _cuentas_del_grupo(codigo, anterior).isdisjoint(_cuentas_del_grupo(codigo, actual)):
        return Comparabilidad(NO_COMPARABLE, f"La presentación de esta partida cambia entre {anterior.anio} y {actual.anio}: "
                                             f"la variación no se calcula. {ADVERTENCIA_ANALITICA}")
    return None


def comparabilidad_agregado(grupos: tuple[str, ...], anterior: DatosEjercicio, actual: DatosEjercicio) -> Comparabilidad | None:
    """Estado de una suma de grupos. Si cubre todas las lineas de la familia que se reorganiza, la variacion se
    calcula como agrupacion analitica; si cubre solo una parte, compara contenidos distintos y no se calcula."""
    resultado = None
    for familia in {FAMILIA_DE_GRUPO[g] for g in grupos if g in FAMILIA_DE_GRUPO}:
        if not presentacion_cambia(familia, anterior, actual):
            continue
        if not (_grupos_presentes(familia, anterior) | _grupos_presentes(familia, actual)) <= set(grupos):
            return Comparabilidad(NO_COMPARABLE, f"La línea no contiene lo mismo en {anterior.anio} y en {actual.anio}: "
                                                 f"la variación no se calcula. {ADVERTENCIA_ANALITICA}")
        resultado = Comparabilidad(ANALITICA, ADVERTENCIA_ANALITICA)
    return resultado


def comparabilidad_cuenta(cuenta, anterior: DatosEjercicio, actual: DatosEjercicio) -> Comparabilidad | None:
    """Una cuenta presente en un solo ejercicio de una familia reorganizada: aparece o desaparece, y se advierte
    que puede tratarse de la misma partida con otra denominacion."""
    familia = FAMILIA_DE_GRUPO.get(cuenta.grupo_analisis or "")
    if familia is None or not presentacion_cambia(familia, anterior, actual):
        return None
    en_anterior = cuenta.id in _cuentas_del_grupo(cuenta.grupo_analisis, anterior)
    en_actual = cuenta.id in _cuentas_del_grupo(cuenta.grupo_analisis, actual)
    if en_anterior == en_actual:
        return None
    otro = actual if en_anterior else anterior
    return Comparabilidad(INFORMATIVA, f"Puede corresponder a otra denominación en {otro.anio}: "
                                       f"{_nombres(_grupos_presentes(familia, otro), familia)}. {ADVERTENCIA_ANALITICA}")


def comparabilidad_utilidad_operativa(anterior: DatosEjercicio, actual: DatosEjercicio) -> Comparabilidad | None:
    """La utilidad operativa no contiene lo mismo si los otros ingresos estan dentro de ella en un ejercicio
    y despues de ella en el otro. La variacion se calcula y se advierte."""
    familia = FAMILIA_DE_GRUPO["OTROS_INGRESOS_OPERATIVOS"]
    if not presentacion_cambia(familia, anterior, actual):
        return None
    dentro, fuera = (anterior, actual) if anterior.tiene("OTROS_INGRESOS_OPERATIVOS") else (actual, anterior)
    incluye = "los otros ingresos netos"
    if dentro.tiene("DETERIORO_CXC") and not fuera.tiene("DETERIORO_CXC"):
        incluye += " y el deterioro de cuentas por cobrar"
    return Comparabilidad(COMPOSICION_DISTINTA, f"La utilidad operativa de {dentro.anio} incluye {incluye}; en {fuera.anio}, los otros "
                                                "ingresos (gastos) se presentan después del resultado de operación. "
                                                "La variación no es plenamente comparable.")


def causa_sin_variacion(actual: Decimal | None, anterior: Decimal | None, estado: Comparabilidad | None = None) -> str:
    """Texto de una celda de variacion sin valor: la comparacion no es valida, falta un saldo o la base no lo permite."""
    if estado and estado.estado in SIN_VARIACION_CALCULADA:
        return SIN_COMPARAR
    if actual is None or anterior is None:
        return SIN_DATO
    return NO_CALCULABLE


_GRUPOS_DE_CONCEPTO = {"gastos_operativos_anf": RUBROS["GASTOS_OPERATIVOS_ANF"].grupos,
                       "gastos_financieros_netos": ("GASTOS_FINANCIEROS", "GASTOS_FINANCIEROS_NETOS", "INGRESOS_FINANCIEROS")}


def _grupos_de_concepto(clave: str) -> tuple[str, ...]:
    return RUBROS[clave[6:]].grupos if clave.startswith("rubro:") else _GRUPOS_DE_CONCEPTO.get(clave, ())


@dataclass
class FilaHorizontal:
    clave: str
    etiqueta: str
    tipo: str
    valores: dict[int, Decimal | None]
    var_abs: dict[int, Decimal | None] = field(default_factory=dict)
    var_pct: dict[int, Decimal | None] = field(default_factory=dict)
    notas: dict[int, str] = field(default_factory=dict)
    nota: str = ""
    comparabilidad: dict[int, Comparabilidad] = field(default_factory=dict)
    observaciones: dict[int, str] = field(default_factory=dict)
    causas: dict[int, str] = field(default_factory=dict)  # por que falta una variacion (R-6)


def _fila(clave: str, etiqueta: str, tipo: str, lista: list[DatosEjercicio], obtener, nota: str = "", comparar=None) -> FilaHorizontal:
    fila = FilaHorizontal(clave, etiqueta, tipo, {d.anio: obtener(d) for d in lista}, nota=nota)
    for anterior, actual in zip(lista, lista[1:]):
        if actual.anio != anterior.anio + 1:
            fila.notas[actual.anio] = f"Ejercicio anterior inmediato ({actual.anio - 1}) no registrado."
            fila.causas[actual.anio] = SIN_DATO
            continue
        absoluta, relativa, nota_var = variacion(fila.valores[actual.anio], fila.valores[anterior.anio])
        estado = comparar(anterior, actual) if comparar else None
        if estado:
            fila.comparabilidad[actual.anio] = estado
            if estado.estado in SIN_VARIACION_CALCULADA:
                absoluta, relativa = None, None
            nota_var = estado.nota
        fila.causas[actual.anio] = causa_sin_variacion(fila.valores[actual.anio], fila.valores[anterior.anio], estado)
        fila.var_abs[actual.anio] = absoluta
        fila.var_pct[actual.anio] = relativa
        if nota_var:
            fila.notas[actual.anio] = nota_var
    return fila


def _observar_capital_social(fila: FilaHorizontal) -> FilaHorizontal:
    """Un cambio minimo del capital social no se ajusta: se conserva el importe del estado y se pide confirmarlo."""
    for anio, relativa in fila.var_pct.items():
        if relativa and abs(relativa) < UMBRAL_CAPITAL_SOCIAL:
            texto = (f"El capital social difiere en USD {abs(fila.var_abs[anio]):,.0f} respecto de {anio - 1}. Se conserva el importe "
                     "del estado financiero original; la diferencia requiere confirmación documental.")
            fila.observaciones[anio] = texto
            fila.notas[anio] = texto
    return fila


def _fila_grupo(g, tipo: str, lista: list[DatosEjercicio]) -> FilaHorizontal:
    fila = _fila(f"grupo:{g.codigo}", g.nombre, tipo, lista, CONCEPTOS[f"grupo:{g.codigo}"].obtener,
                 comparar=lambda anterior, actual: comparabilidad_grupo(g.codigo, anterior, actual))
    return _observar_capital_social(fila) if g.codigo == "CAPITAL_SOCIAL" else fila


def _fila_concepto(clave: str, lista: list[DatosEjercicio]) -> FilaHorizontal:
    grupos = _grupos_de_concepto(clave)
    comparar = (lambda anterior, actual: comparabilidad_agregado(grupos, anterior, actual)) if grupos else None
    if clave == "utilidad_operativa":
        comparar = comparabilidad_utilidad_operativa
    c = CONCEPTOS[clave]
    return _fila(clave, c.etiqueta, c.tipo, lista, c.obtener, c.nota, comparar=comparar)


def horizontal_conceptos(lista: list[DatosEjercicio], claves=CLAVES_HORIZONTAL_ANF) -> list[FilaHorizontal]:
    lista = [d for d in lista if d.tiene_datos]
    return [_fila_concepto(c, lista) for c in claves]


def horizontal_grupos(lista: list[DatosEjercicio], estado: str | None = None) -> list[FilaHorizontal]:
    """Todos los grupos de analisis con datos en algun ejercicio, por clase,
    con los subtotales del Balance y los resultados del Estado de Resultados.
    estado: "BG" o "ER" para limitar a uno de los dos estados."""
    lista = [d for d in lista if d.tiene_datos]
    presentes = {g for d in lista for g in d.grupos}
    filas = []
    if estado != "ER":
        filas += _grupos_balance(lista, presentes)
    if estado != "BG":
        filas += _grupos_resultados(lista, presentes)
    return filas


def _grupos_balance(lista: list[DatosEjercicio], presentes: set[str]) -> list[FilaHorizontal]:
    filas = []
    subtotales = {"AC": "activo_corriente", "ANC": "activo_no_corriente", "PC": "pasivo_corriente",
                  "PNC": "pasivo_no_corriente", "PAT": "total_patrimonio"}
    for clase in CLASE_BALANCE:
        for g in GRUPOS.values():
            if g.clase == clase and g.codigo in presentes:
                filas.append(_fila_grupo(g, CUENTA, lista))
        c = subtotales[clase]
        filas.append(_fila(c, CONCEPTOS[c].etiqueta, SUBTOTAL, lista, CONCEPTOS[c].obtener))
        if clase == "ANC":
            filas.append(_fila("total_activo", "Total activo", TOTAL, lista, CONCEPTOS["total_activo"].obtener))
        if clase == "PNC":
            filas.append(_fila("total_pasivo", "Total pasivo", TOTAL, lista, CONCEPTOS["total_pasivo"].obtener))
    return filas


def _grupos_resultados(lista: list[DatosEjercicio], presentes: set[str]) -> list[FilaHorizontal]:
    filas = []
    for g in GRUPOS.values():
        if g.clase == "ER" and g.codigo in presentes:
            filas.append(_fila_grupo(g, CUENTA, lista))
    for c in ("utilidad_bruta", "utilidad_operativa", "utilidad_antes_impuestos", "utilidad_neta"):
        filas.append(_fila_concepto(c, lista))
    return filas


def horizontal_cuentas(lista: list[DatosEjercicio]) -> list[FilaHorizontal]:
    """Cada cuenta con su denominacion propia. Una cuenta que no existe en un
    ejercicio queda 'sin dato' (no se iguala a cero): asi se ve el cambio de
    presentacion entre familias de estados."""
    lista = [d for d in lista if d.tiene_datos]
    cuentas = {}
    for d in lista:
        for grupo in (d.bs.activo_corriente, d.bs.activo_no_corriente, d.bs.pasivo_corriente, d.bs.pasivo_no_corriente,
                      *d.bs.patrimonio_grupos):
            for linea in grupo.lineas:
                cuentas.setdefault(linea.cuenta.id, (linea.cuenta, "BALANCE"))
        for grupo in (d.inc.ingresos_netos, d.inc.costo_ventas, d.inc.gastos_administracion, d.inc.gastos_ventas,
                      d.inc.otros_ingresos_operativos, d.inc.otros_gastos_operativos, d.inc.ingresos_financieros,
                      d.inc.gastos_financieros, d.inc.otros_ingresos_no_operativos, d.inc.otros_gastos_no_operativos,
                      d.inc.impuesto_renta):
            for linea in grupo.lineas:
                cuentas.setdefault(linea.cuenta.id, (linea.cuenta, "RESULTADOS"))

    def importe(cuenta_id):
        def obtener(d):
            for lineas in d.lineas_por_grupo.values():
                for cuenta, v in lineas:
                    if cuenta.id == cuenta_id:
                        return v
            for cuenta, v, _ in d.sin_grupo:
                if cuenta.id == cuenta_id:
                    return v
            return None
        return obtener

    def fila_cuenta(c):
        fila = _fila(c.codigo, f"{c.codigo} — {c.nombre}", CUENTA, lista, importe(c.id),
                     comparar=lambda anterior, actual: comparabilidad_cuenta(c, anterior, actual))
        return _observar_capital_social(fila) if c.grupo_analisis == "CAPITAL_SOCIAL" else fila

    ordenadas = sorted(cuentas.values(), key=lambda t: (t[1], t[0].orden_presentacion, t[0].codigo))
    return [fila_cuenta(c) for c, _ in ordenadas]


# ------------------------------------------------- comparacion de dos ejercicios
AUMENTO, DISMINUCION, SIN_VARIACION, APARECE, DESAPARECE = "Aumento", "Disminución", "Sin variación", "Aparece", "Desaparece"
PRESENTACION_AGRUPADA = "Presentación agrupada"


@dataclass
class FilaDosEjercicios:
    clave: str
    etiqueta: str
    tipo: str
    actual: Decimal | None
    anterior: Decimal | None
    var_abs: Decimal | None
    var_pct: Decimal | None
    tendencia: str
    nota: str = ""
    causa: str = ""  # por que falta una variacion (R-6)


def tendencia(actual: Decimal | None, anterior: Decimal | None) -> str:
    """Sentido del cambio del saldo. Una cuenta sin dato en un ejercicio aparece o desaparece: no se iguala a cero."""
    if actual is None and anterior is None:
        return ""
    if anterior is None:
        return APARECE
    if actual is None:
        return DESAPARECE
    if actual > anterior:
        return AUMENTO
    return DISMINUCION if actual < anterior else SIN_VARIACION


def _clase_cuenta(cuenta) -> str | None:
    """Clase del Balance segun la clasificacion contable de la cuenta (None si es de resultados)."""
    categoria = cuenta.categoria_principal.value
    subcategoria = cuenta.subcategoria.value if cuenta.subcategoria else ""
    if categoria == "ACTIVO":
        return "AC" if subcategoria == "CORRIENTE" else "ANC"
    if categoria == "PASIVO":
        return "PC" if subcategoria == "CORRIENTE" else "PNC"
    return "PAT" if categoria == "PATRIMONIO" else None


def _cuentas_de_estado(lista: list[DatosEjercicio], estado: str) -> list[FilaHorizontal]:
    """Cuentas con importe en algun ejercicio, con los subtotales del estado en su lugar."""
    lista = [d for d in lista if d.tiene_datos]
    clases = {}
    for d in lista:
        for lineas in d.lineas_por_grupo.values():
            clases.update({cuenta.codigo: _clase_cuenta(cuenta) for cuenta, _ in lineas})
        clases.update({cuenta.codigo: _clase_cuenta(cuenta) for cuenta, _, _ in d.sin_grupo})
    cuentas = [f for f in horizontal_cuentas(lista) if any(v is not None for v in f.valores.values())]
    filas = []
    if estado == "ER":
        filas = [f for f in cuentas if clases.get(f.clave) is None]
        return filas + [_fila_concepto(c, lista) for c in ("utilidad_bruta", "utilidad_operativa", "utilidad_antes_impuestos", "utilidad_neta")]
    subtotales = {"AC": ("activo_corriente",), "ANC": ("activo_no_corriente", "total_activo"), "PC": ("pasivo_corriente",),
                  "PNC": ("pasivo_no_corriente", "total_pasivo"), "PAT": ("total_patrimonio", "total_pasivo_patrimonio")}
    for clase in CLASE_BALANCE:
        filas += [f for f in cuentas if clases.get(f.clave) == clase]
        filas += [_fila(c, CONCEPTOS[c].etiqueta, CONCEPTOS[c].tipo, lista, CONCEPTOS[c].obtener) for c in subtotales[clase]]
    return filas


def horizontal_de_estado(lista: list[DatosEjercicio], estado: str, nivel: str) -> list[FilaHorizontal]:
    """Filas del analisis horizontal de un estado ("BG" o "ER") a nivel "rubros", "grupos" o "cuentas"."""
    if nivel == "rubros":
        return horizontal_conceptos(lista, CLAVES_RUBROS_BG if estado == "BG" else CLAVES_RUBROS_ER)
    if nivel == "grupos":
        return horizontal_grupos(lista, estado)
    return _cuentas_de_estado(lista, estado)


def _nota_dos_ejercicios(actual, anterior, nota: str, anio_anterior: int, anio_actual: int) -> str:
    if anterior is None and actual is not None:
        return f"No se presenta en {anio_anterior}: sin base de comparación."
    if actual is None and anterior is not None:
        return f"No se presenta en {anio_actual}: sin dato para comparar."
    if anterior and actual and (anterior > CERO) != (actual > CERO):
        if anterior < CERO:
            return "Cambia de signo con base negativa: la variación relativa no se calcula; use la variación absoluta."
        return "Cambia de signo: el porcentaje debe leerse junto con la variación absoluta y el cambio de signo (trabajo, 6.3)."
    return nota


def dos_ejercicios(filas: list[FilaHorizontal], anio_actual: int, anio_anterior: int) -> list[FilaDosEjercicios]:
    """Saldo actual, saldo anterior, variaciones y sentido del cambio entre dos ejercicios. Se omiten las
    filas sin importe en ambos, que no tienen nada que comparar."""
    resultado = []
    for fila in filas:
        actual, anterior = fila.valores.get(anio_actual), fila.valores.get(anio_anterior)
        if not actual and not anterior:
            continue
        absoluta, relativa, nota = variacion(actual, anterior)
        sentido = tendencia(actual, anterior)
        nota = _nota_dos_ejercicios(actual, anterior, nota, anio_anterior, anio_actual)
        estado = fila.comparabilidad.get(anio_actual) if anio_actual == anio_anterior + 1 else None
        if estado:
            if estado.estado in SIN_VARIACION_CALCULADA:
                absoluta, relativa = None, None
                sentido = PRESENTACION_AGRUPADA if estado.estado == AGRUPADA else SIN_COMPARAR
                nota = ""
            nota = " ".join(t for t in (estado.nota, fila.nota, nota) if t)
        observacion = fila.observaciones.get(anio_actual)
        if observacion:
            nota = " ".join(t for t in (nota, observacion) if t)
        resultado.append(FilaDosEjercicios(fila.clave, fila.etiqueta, fila.tipo, actual, anterior, absoluta, relativa, sentido, nota,
                                           causa_sin_variacion(actual, anterior, estado)))
    return resultado


# --------------------------------------------------------- vertical comparativo
@dataclass
class FilaVerticalComparativa:
    clave: str
    etiqueta: str
    tipo: str
    valores: dict[int, Decimal | None]
    porcentajes: dict[int, Decimal | None]
    nota: str = ""


def porcentaje(valor_: Decimal | None, base: Decimal | None) -> Decimal | None:
    if valor_ is None or base is None or base == CERO:
        return None
    return valor_ / base * CIEN


def _sin_clasificar_con_signo(d: DatosEjercicio, categorias: tuple[str, ...]) -> Decimal:
    return sum((signo_resultado(c) * v for c, v, _ in d.sin_grupo if c.categoria_principal.value in categorias), CERO)


# Partidas sin grupo: entran en las utilidades por su categoria, asi que se muestran para que las lineas sumen el total.
_FILAS_SIN_CLASIFICAR = {
    "s_utilidad_operativa": Concepto("s_sin_clasificar_operativas", "Partidas operativas sin grupo de análisis",
                                     lambda d: _sin_clasificar_con_signo(d, ("COSTOS", "GASTOS_OPERATIVOS"))),
    "s_utilidad_antes_impuestos": Concepto("s_sin_clasificar_financieras", "Partidas financieras y otras sin grupo de análisis",
                                           lambda d: _sin_clasificar_con_signo(d, ("INGRESOS_FINANCIEROS", "GASTOS_FINANCIEROS", "OTROS_INGRESOS_GASTOS"))),
    "s_utilidad_neta": Concepto("s_sin_clasificar_impuestos", "Impuestos sin grupo de análisis",
                                lambda d: _sin_clasificar_con_signo(d, ("IMPUESTOS",))),
}


def vertical_comparativo(lista: list[DatosEjercicio], estado: str) -> list[FilaVerticalComparativa]:
    """estado: "ER" (base ingresos ordinarios) o "BG" (base activo total)."""
    claves, base = (CLAVES_VERTICAL_ER, "ingresos") if estado == "ER" else (CLAVES_VERTICAL_BG, "total_activo")
    lista = [d for d in lista if (d.inc.tiene_datos if estado == "ER" else d.bs.tiene_datos)]
    filas = []
    for clave in claves:
        previa = _FILAS_SIN_CLASIFICAR.get(clave) if estado == "ER" else None
        if previa is not None and any(previa.obtener(d) != CERO for d in lista):
            valores = {d.anio: previa.obtener(d) for d in lista}
            filas.append(FilaVerticalComparativa(previa.clave, previa.etiqueta, previa.tipo, valores,
                                                 {d.anio: porcentaje(valores[d.anio], CONCEPTOS[base].obtener(d)) for d in lista}))
        concepto = CONCEPTOS[clave]
        valores = {d.anio: concepto.obtener(d) for d in lista}
        filas.append(FilaVerticalComparativa(
            clave, ETIQUETAS_VERTICAL.get(clave, concepto.etiqueta), concepto.tipo, valores,
            {d.anio: porcentaje(valores[d.anio], CONCEPTOS[base].obtener(d)) for d in lista}, concepto.nota))
    return filas

