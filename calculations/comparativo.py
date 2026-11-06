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

Analisis vertical comparativo (seccion 7): Estado de Resultados sobre los
ingresos ordinarios, con signo (costos y gastos negativos, como en el
trabajo); Balance General sobre el activo total.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Callable

from calculations.rubros import CLASE_BALANCE, GRUPOS, RUBROS, DatosEjercicio

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
    return lambda d: d.rubro(codigo) if d.bs.tiene_datos or d.inc.tiene_datos else None


def _con_signo(*grupos: str):
    return _er(lambda d: d.rubro_con_signo(*grupos))


_LISTA = [
    # Balance General
    Concepto("activo_corriente", "Total activo corriente", _bs(lambda d: d.bs.activo_corriente.subtotal), SUBTOTAL),
    Concepto("activo_no_corriente", "Total activo no corriente", _bs(lambda d: d.bs.activo_no_corriente.subtotal), SUBTOTAL),
    Concepto("total_activo", "Total activo", _bs(lambda d: d.bs.total_activo), TOTAL),
    Concepto("pasivo_corriente", "Total pasivo corriente", _bs(lambda d: d.bs.pasivo_corriente.subtotal), SUBTOTAL),
    Concepto("pasivo_no_corriente", "Total pasivo no corriente", _bs(lambda d: d.bs.pasivo_no_corriente.subtotal), SUBTOTAL),
    Concepto("total_pasivo", "Total pasivo", _bs(lambda d: d.bs.total_pasivo), TOTAL),
    Concepto("total_patrimonio", "Total patrimonio", _bs(lambda d: d.bs.total_patrimonio), TOTAL),
    Concepto("patrimonio_controladora", "Patrimonio atribuible a la controladora", _bs(lambda d: d.patrimonio_controladora), SUBTOTAL),
    Concepto("total_pasivo_patrimonio", "Total pasivo y patrimonio", _bs(lambda d: d.bs.total_pasivo_patrimonio), TOTAL),
    # Estado de resultados (importes positivos, como se capturan)
    Concepto("ingresos", "Ingresos ordinarios", _er(lambda d: d.inc.ingresos_netos.subtotal), SUBTOTAL),
    Concepto("costo_ventas", "Costo de ventas", _er(lambda d: d.inc.costo_ventas.subtotal)),
    Concepto("utilidad_bruta", "Utilidad bruta", _er(lambda d: d.inc.utilidad_bruta), TOTAL),
    Concepto("gastos_operativos_anf", RUBROS["GASTOS_OPERATIVOS_ANF"].nombre, _er(lambda d: d.rubro("GASTOS_OPERATIVOS_ANF")),
             nota=RUBROS["GASTOS_OPERATIVOS_ANF"].nota),
    Concepto("utilidad_operativa", "Utilidad de operación", _er(lambda d: d.inc.utilidad_operativa), TOTAL),
    Concepto("ingresos_financieros", "Ingresos financieros", _er(lambda d: d.inc.ingresos_financieros.subtotal)),
    Concepto("gastos_financieros", "Gastos financieros (como se presentan)", _er(lambda d: d.inc.gastos_financieros.subtotal)),
    Concepto("gastos_financieros_netos", "Gastos financieros netos", _er(lambda d: d.gastos_financieros_netos),
             nota="Gastos financieros − ingresos financieros. 2021–2023 el estado ya presenta el neto."),
    Concepto("utilidad_antes_impuestos", "Utilidad antes de impuestos", _er(lambda d: d.inc.utilidad_antes_impuestos), TOTAL),
    Concepto("impuesto_renta", "Impuesto sobre la renta", _er(lambda d: d.inc.impuesto_renta.subtotal)),
    Concepto("utilidad_neta", "Utilidad neta del ejercicio", _er(lambda d: d.inc.utilidad_neta), TOTAL),
    Concepto("utilidad_controladora", "Utilidad atribuible a la controladora", _er(lambda d: d.utilidad_controladora()[0])),
    Concepto("depreciacion_amortizacion_total", "Depreciación y amortización", lambda d: d.depreciacion_amortizacion()[0]),
    # Lineas con signo para el vertical del Estado de Resultados (seccion 7.1)
    Concepto("s_ingresos", "Ingresos ordinarios", _er(lambda d: d.inc.ingresos_netos.subtotal), SUBTOTAL),
    Concepto("s_costo_ventas", "Costo de ventas", _con_signo("COSTO_VENTAS")),
    Concepto("s_utilidad_bruta", "Ganancia bruta", _er(lambda d: d.inc.utilidad_bruta), TOTAL),
    Concepto("s_gastos_administracion", "Gastos de administración", _con_signo("GASTOS_ADMINISTRACION")),
    Concepto("s_gastos_venta", "Gastos de venta y despacho o distribución", _con_signo("GASTOS_VENTA")),
    Concepto("s_deterioro_cxc", "Deterioro de cuentas por cobrar", _con_signo("DETERIORO_CXC")),
    Concepto("s_gastos_personal", "Gastos de personal", _con_signo("GASTOS_PERSONAL")),
    Concepto("s_depreciacion_amortizacion", "Depreciación y amortización (en el estado de resultados)",
             _con_signo("DEPRECIACION_AMORTIZACION")),
    Concepto("s_otros_ingresos_gastos", "Otros ingresos o gastos", _con_signo("OTROS_INGRESOS_OPERATIVOS", "OTROS_NO_OPERATIVOS"),
             nota=RUBROS["OTROS_INGRESOS_GASTOS"].nota),
    Concepto("s_utilidad_operativa", "Resultado operativo", _er(lambda d: d.inc.utilidad_operativa), TOTAL),
    Concepto("s_ingresos_financieros", "Ingresos financieros", _con_signo("INGRESOS_FINANCIEROS")),
    Concepto("s_gastos_financieros", "Gastos financieros", _con_signo("GASTOS_FINANCIEROS", "GASTOS_FINANCIEROS_NETOS"),
             nota="2021–2023: gasto financiero neto (así se presenta); 2024–2025: gasto financiero bruto."),
    Concepto("s_utilidad_antes_impuestos", "Resultado antes de impuestos", _er(lambda d: d.inc.utilidad_antes_impuestos), TOTAL),
    Concepto("s_impuesto_renta", "Impuesto sobre la renta", _con_signo("IMPUESTO_RENTA")),
    Concepto("s_utilidad_neta", "Ganancia o resultado neto", _er(lambda d: d.inc.utilidad_neta), TOTAL),
]
CONCEPTOS: dict[str, Concepto] = {c.clave: c for c in _LISTA}
for _r in RUBROS.values():
    CONCEPTOS[f"rubro:{_r.codigo}"] = Concepto(f"rubro:{_r.codigo}", _r.nombre, _rubro(_r.codigo), nota=_r.nota)
for _g in GRUPOS.values():
    CONCEPTOS[f"grupo:{_g.codigo}"] = Concepto(
        f"grupo:{_g.codigo}", _g.nombre, (lambda codigo: lambda d: d.g(codigo) if d.tiene_datos else None)(_g.codigo))
# Este grupo reune cuentas de ingreso y de gasto: sumar sus importes capturados (positivos)
# presentaria un gasto como un aumento del ingreso. Se compara el neto con su signo.
CONCEPTOS["grupo:OTROS_NO_OPERATIVOS"] = Concepto(
    "grupo:OTROS_NO_OPERATIVOS", GRUPOS["OTROS_NO_OPERATIVOS"].nombre, _con_signo("OTROS_NO_OPERATIVOS"))

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


def _fila(clave: str, etiqueta: str, tipo: str, lista: list[DatosEjercicio], obtener, nota: str = "") -> FilaHorizontal:
    fila = FilaHorizontal(clave, etiqueta, tipo, {d.anio: obtener(d) for d in lista}, nota=nota)
    for anterior, actual in zip(lista, lista[1:]):
        if actual.anio != anterior.anio + 1:
            fila.notas[actual.anio] = f"Ejercicio anterior inmediato ({actual.anio - 1}) no registrado."
            continue
        absoluta, relativa, nota_var = variacion(fila.valores[actual.anio], fila.valores[anterior.anio])
        fila.var_abs[actual.anio] = absoluta
        fila.var_pct[actual.anio] = relativa
        if nota_var:
            fila.notas[actual.anio] = nota_var
    return fila


def horizontal_conceptos(lista: list[DatosEjercicio], claves=CLAVES_HORIZONTAL_ANF) -> list[FilaHorizontal]:
    lista = [d for d in lista if d.tiene_datos]
    return [_fila(c, CONCEPTOS[c].etiqueta, CONCEPTOS[c].tipo, lista, CONCEPTOS[c].obtener, CONCEPTOS[c].nota) for c in claves]


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
                filas.append(_fila(f"grupo:{g.codigo}", g.nombre, CUENTA, lista, CONCEPTOS[f"grupo:{g.codigo}"].obtener))
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
            filas.append(_fila(f"grupo:{g.codigo}", g.nombre, CUENTA, lista, CONCEPTOS[f"grupo:{g.codigo}"].obtener))
    for c in ("utilidad_bruta", "utilidad_operativa", "utilidad_antes_impuestos", "utilidad_neta"):
        filas.append(_fila(c, CONCEPTOS[c].etiqueta, TOTAL, lista, CONCEPTOS[c].obtener))
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

    ordenadas = sorted(cuentas.values(), key=lambda t: (t[1], t[0].orden_presentacion, t[0].codigo))
    return [_fila(c.codigo, f"{c.codigo} — {c.nombre}", CUENTA, lista, importe(c.id)) for c, _ in ordenadas]


# ------------------------------------------------- comparacion de dos ejercicios
AUMENTO, DISMINUCION, SIN_VARIACION, APARECE, DESAPARECE = "Aumento", "Disminución", "Sin variación", "Aparece", "Desaparece"


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
        return filas + [_fila(c, CONCEPTOS[c].etiqueta, TOTAL, lista, CONCEPTOS[c].obtener)
                        for c in ("utilidad_bruta", "utilidad_operativa", "utilidad_antes_impuestos", "utilidad_neta")]
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
        return "Cambia de signo: interpretar el porcentaje con cautela (trabajo, 6.3)."
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
        resultado.append(FilaDosEjercicios(fila.clave, fila.etiqueta, fila.tipo, actual, anterior, absoluta, relativa,
                                           tendencia(actual, anterior),
                                           _nota_dos_ejercicios(actual, anterior, nota, anio_anterior, anio_actual)))
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


def vertical_comparativo(lista: list[DatosEjercicio], estado: str) -> list[FilaVerticalComparativa]:
    """estado: "ER" (base ingresos ordinarios) o "BG" (base activo total)."""
    claves, base = (CLAVES_VERTICAL_ER, "ingresos") if estado == "ER" else (CLAVES_VERTICAL_BG, "total_activo")
    lista = [d for d in lista if (d.inc.tiene_datos if estado == "ER" else d.bs.tiene_datos)]
    filas = []
    for clave in claves:
        concepto = CONCEPTOS[clave]
        valores = {d.anio: concepto.obtener(d) for d in lista}
        filas.append(FilaVerticalComparativa(
            clave, ETIQUETAS_VERTICAL.get(clave, concepto.etiqueta), concepto.tipo, valores,
            {d.anio: porcentaje(valores[d.anio], CONCEPTOS[base].obtener(d)) for d in lista}, concepto.nota))
    return filas

