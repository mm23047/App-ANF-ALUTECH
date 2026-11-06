"""Secciones de los reportes del analisis 2021-2025 (adaptacion Alutech).

Cada funcion arma una tabla (Seccion) a partir de los calculos centrales
(calculations/): la pantalla, el Excel y el PDF presentan exactamente las
mismas cifras porque leen la misma Seccion; ningun formato recalcula nada.

Las celdas numericas guardan el Decimal sin redondear y la unidad de su
columna (o de su fila); el redondeo solo ocurre al presentar.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.orm import Session

from calculations import indicadores as ind
from calculations.comparacion_anf import Comparacion
from calculations.comparativo import (
    CLAVES_TABLA_3,
    CLAVES_TABLA_4,
    CLAVES_TABLA_5,
    CONCEPTOS,
    dos_ejercicios,
    horizontal_conceptos,
    horizontal_cuentas,
    horizontal_de_estado,
    horizontal_grupos,
    variacion,
    vertical_comparativo,
)
from calculations.controles_carga import controles_fuentes, controles_totales
from calculations.dupont import factores_controladora, factores_total
from calculations.fuentes_usos import ResultadoFuentesUsos
from calculations.rubros import GRUPOS, NOMBRE_CLASE, DatosEjercicio
from calculations.wacc import ResultadoWACC, cargar_supuestos
from components.money import format_money, format_percent, redondear

TEXTO, USD, PCT, VECES, DIAS, POR_FILA = "texto", "USD", "%", "veces", "días", "por_fila"
VAR_USD, VAR_PCT = "var_usd", "var_pct"  # variaciones: con signo explicito, como las Tablas 3 a 7 del trabajo


@dataclass
class Columna:
    nombre: str
    tipo: str = TEXTO


@dataclass
class Seccion:
    titulo: str
    columnas: list[Columna]
    filas: list[list] = field(default_factory=list)
    notas: list[str] = field(default_factory=list)
    columna_unidad: int | None = None  # indice de la columna con la unidad de cada fila (tipo POR_FILA)
    filas_destacadas: set[int] = field(default_factory=set)


def es_entero(valor: Decimal) -> bool:
    return valor == valor.to_integral_value()


def formatear(valor, tipo: str) -> str:
    if valor is None:
        return "—"
    if isinstance(valor, str):
        return valor
    if tipo == USD:  # sin centavos cuando no los hay, como las tablas del trabajo
        return f"{valor:,.0f}" if es_entero(valor) else format_money(valor)
    if tipo == VAR_USD:
        return f"{valor:+,.0f}" if es_entero(valor) else f"{valor:+,.2f}"
    if tipo == VAR_PCT:
        redondeado = valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return f"{redondeado:+.2f}%"
    if tipo == PCT:
        return format_percent(valor)
    if tipo == DIAS:
        return f"{redondear(valor, 2):,.2f}"
    if tipo == VECES:
        return f"{redondear(valor, 2):,.2f}"
    if isinstance(valor, Decimal):
        return f"{redondear(valor, 2):,.2f}"
    return str(valor)


def tipo_celda(seccion: Seccion, fila: list, indice: int) -> str:
    tipo = seccion.columnas[indice].tipo
    if tipo == POR_FILA and seccion.columna_unidad is not None:
        return {ind.USD: USD, ind.PCT: PCT, ind.VECES: VECES, ind.DIAS_U: DIAS}.get(fila[seccion.columna_unidad], VECES)
    return tipo


def _anios(lista: list[DatosEjercicio]) -> list[int]:
    return [d.anio for d in lista if d.tiene_datos]


# ---------------------------------------------------------------- estados
def estados_originales(lista: list[DatosEjercicio], estado: str) -> Seccion:
    """Cuentas con su denominacion y su importe original por ejercicio."""
    anios = _anios(lista)
    nombre = "Estado de situación financiera" if estado == "BALANCE" else "Estado de resultados"
    seccion = Seccion(
        f"{nombre} — datos originales por ejercicio",
        [Columna("Código"), Columna("Cuenta (denominación del catálogo)"), Columna("Grupo de análisis")]
        + [Columna(str(a), USD) for a in anios],
        notas=["Importes tal como se registraron desde los documentos originales (convención de signos de la aplicación: "
               "costos, gastos e impuestos en positivo). «—» indica que la cuenta no se presenta en ese ejercicio. "
               "La fuente de cada importe está en «Datos originales › Trazabilidad»."],
    )
    for fila in horizontal_cuentas(lista):
        cuenta = _cuenta_de(lista, fila.clave)
        if cuenta is None:
            continue
        es_balance = cuenta.categoria_principal.value in ("ACTIVO", "PASIVO", "PATRIMONIO")
        if es_balance != (estado == "BALANCE"):
            continue
        grupo = GRUPOS.get(cuenta.grupo_analisis or "")
        seccion.filas.append([cuenta.codigo, cuenta.nombre, grupo.nombre if grupo else "(sin grupo)"]
                             + [fila.valores.get(a) for a in anios])
    claves = (("activo_corriente", "activo_no_corriente", "total_activo", "pasivo_corriente", "pasivo_no_corriente",
               "total_pasivo", "total_patrimonio", "total_pasivo_patrimonio") if estado == "BALANCE" else
              ("ingresos", "utilidad_bruta", "utilidad_operativa", "utilidad_antes_impuestos", "utilidad_neta"))
    for clave in claves:
        seccion.filas_destacadas.add(len(seccion.filas))
        seccion.filas.append(["", CONCEPTOS[clave].etiqueta.upper(), "Total calculado"]
                             + [CONCEPTOS[clave].obtener(d) for d in lista if d.tiene_datos])
    return seccion


def _cuenta_de(lista, codigo):
    for d in lista:
        for lineas in d.lineas_por_grupo.values():
            for cuenta, _ in lineas:
                if cuenta.codigo == codigo:
                    return cuenta
        for cuenta, _, _ in d.sin_grupo:
            if cuenta.codigo == codigo:
                return cuenta
    return None


def _rango(anios: list[int]) -> str:
    return f"{anios[0]}–{anios[-1]}" if anios else ""


# ------------------------------------------------------------- horizontal
def horizontal(lista: list[DatosEjercicio], nivel: str = "rubros") -> Seccion:
    anios = _anios(lista)
    filas = {"rubros": horizontal_conceptos, "grupos": horizontal_grupos, "cuentas": horizontal_cuentas}[nivel](lista)
    pares = list(zip(anios, anios[1:]))
    seccion = Seccion(
        {"rubros": "Análisis horizontal — rubros y totales (criterio de las Tablas 3 a 5 del trabajo)",
         "grupos": "Análisis horizontal — por grupo de análisis (cuentas comparables entre ejercicios)",
         "cuentas": "Análisis horizontal — por cuenta (denominación original)"}[nivel],
        [Columna("Concepto")] + [Columna(str(a), USD) for a in anios]
        + [c for a, b in pares for c in (Columna(f"Var. abs. {a}–{b}", USD), Columna(f"Var. % {a}–{b}", PCT))],
        notas=["Variación absoluta = Vt − Vt−1; variación relativa = (Vt − Vt−1) / Vt−1 × 100. Si la base es cero o "
               "negativa no se calcula el porcentaje («—») y se indica la causa."],
    )
    for fila in filas:
        if fila.tipo != "cuenta":
            seccion.filas_destacadas.add(len(seccion.filas))
        seccion.filas.append([fila.etiqueta] + [fila.valores.get(a) for a in anios]
                             + [v for _, b in pares for v in (fila.var_abs.get(b), fila.var_pct.get(b))])
        for anio, nota in fila.notas.items():
            if nota and not nota.startswith("Sin dato"):
                seccion.notas.append(f"{fila.etiqueta} ({anio}): {nota}")
        if fila.nota:
            seccion.notas.append(f"{fila.etiqueta}: {fila.nota}")
    seccion.notas = list(dict.fromkeys(seccion.notas))
    return seccion


_NOTA_FORMULAS = ("Variación absoluta = Vt − Vt−1; variación relativa = (Vt − Vt−1) / Vt−1 × 100. Si la base es cero o negativa "
                  "no se calcula el porcentaje («—»).")
_NOTA_2023_2024 = ("2021–2023: estados combinados; 2024–2025: estados consolidados. El cambio modifica la presentación de varias "
                   "partidas: las variaciones 2023–2024 deben interpretarse con cautela (trabajo, 6.2).")


def _tabla_trabajo(lista: list[DatosEjercicio], anios: list[int], claves, titulo: str, notas: list[str]) -> Seccion:
    """Tabla con la estructura de las Tablas 3 y 4 del trabajo: cada ejercicio seguido de sus variaciones."""
    filas = horizontal_conceptos(lista, claves)
    columnas = [Columna("Cuenta financiera")]
    for n, anio in enumerate(anios):
        columnas.append(Columna(str(anio), USD))
        if n:
            periodo = f"{str(anios[n - 1])[-2:]}–{str(anio)[-2:]}"
            columnas += [Columna(f"Var. abs. {periodo}", VAR_USD), Columna(f"Var. rel. {periodo}", VAR_PCT)]
    seccion = Seccion(titulo, columnas, notas=notas)
    for fila in filas:
        if fila.tipo != "cuenta":
            seccion.filas_destacadas.add(len(seccion.filas))
        celdas = [fila.etiqueta]
        for n, anio in enumerate(anios):
            celdas.append(fila.valores.get(anio))
            if n:
                celdas += [fila.var_abs.get(anio), fila.var_pct.get(anio)]
        seccion.filas.append(celdas)
    return seccion


def horizontal_balance_tablas(lista: list[DatosEjercicio]) -> list[Seccion]:
    """Tablas 3 y 4 del trabajo. La primera usa la linea de cuentas por cobrar comerciales y la segunda, comerciales
    y otras; por eso el importe del ejercicio comun difiere entre ambas (nota de la Tabla 4)."""
    anios = [d.anio for d in lista if d.bs.tiene_datos]
    if not anios:
        return []
    secciones = [_tabla_trabajo(
        lista, anios[:3], CLAVES_TABLA_3,
        f"Tabla 3. Análisis horizontal del estado de situación financiera ({anios[0]}–{anios[:3][-1]}) [USD]",
        [_NOTA_FORMULAS, "Cuentas por cobrar: únicamente la línea «Cuentas por cobrar comerciales» en los estados combinados."])]
    if len(anios) > 3:
        secciones.append(_tabla_trabajo(
            lista, anios[2:], CLAVES_TABLA_4,
            f"Tabla 4. Análisis horizontal del estado de situación financiera ({anios[2]}–{anios[-1]}) [USD]",
            [_NOTA_FORMULAS, "Cuentas por cobrar: comerciales y otras cuentas por cobrar, porque los estados consolidados presentan "
                             "ambas en una sola línea. Por esa razón el importe del primer ejercicio difiere del de la Tabla 3.",
             _NOTA_2023_2024]))
    return secciones


def horizontal_resultados_tabla(lista: list[DatosEjercicio]) -> Seccion:
    """Tabla 5 del trabajo, con la variacion absoluta ademas de la relativa."""
    filas = horizontal_conceptos(lista, CLAVES_TABLA_5)
    anios = [d.anio for d in lista if d.inc.tiene_datos]
    pares = list(zip(anios, anios[1:]))
    seccion = Seccion(
        f"Tabla 5. Análisis horizontal del estado de resultados ({anios[0]}–{anios[-1]}) [USD]" if anios else "Tabla 5",
        [Columna("Rubro del estado de resultados")] + [Columna(str(a), USD) for a in anios]
        + [Columna(f"Var. abs. {str(a)[-2:]}–{str(b)[-2:]}", VAR_USD) for a, b in pares]
        + [Columna(f"Var. rel. {str(a)[-2:]}–{str(b)[-2:]}", VAR_PCT) for a, b in pares],
        notas=[_NOTA_FORMULAS,
               "Costos y gastos en positivo, como en el trabajo: un aumento significa mayor costo o gasto.",
               "Gastos operativos: administración, venta o distribución y, en 2024–2025, personal y depreciación y amortización. "
               "No incluyen el deterioro de cuentas por cobrar ni los otros ingresos netos de 2021–2023, que sí forman parte de la "
               "utilidad operativa.",
               "Utilidad operativa: los estados de 2022 y 2023 no imprimen este subtotal; se obtiene de sus partidas impresas.",
               "Gastos financieros netos: en 2021–2023 los estados presentan directamente el neto; en 2024–2025, gastos financieros "
               "menos ingresos financieros.", _NOTA_2023_2024],
    )
    for fila in filas:
        if fila.tipo != "cuenta":
            seccion.filas_destacadas.add(len(seccion.filas))
        seccion.filas.append([fila.etiqueta] + [fila.valores.get(a) for a in anios] + [fila.var_abs.get(b) for _, b in pares]
                             + [fila.var_pct.get(b) for _, b in pares])
    return seccion


def horizontal_dos_ejercicios(lista: list[DatosEjercicio], anio: int, anterior: int, estado: str, nivel: str) -> Seccion:
    """Saldo actual, saldo anterior, variaciones y sentido del cambio de un estado entre dos ejercicios."""
    nombre = "Balance General" if estado == "BG" else "Estado de Resultados"
    detalle = {"rubros": "rubros y totales", "grupos": "grupos de análisis", "cuentas": "cuentas"}[nivel]
    seccion = Seccion(
        f"{nombre}: {anio} vs {anterior} — {detalle} [USD]",
        [Columna("Partida"), Columna(f"Saldo actual ({anio})", USD), Columna(f"Saldo anterior ({anterior})", USD),
         Columna("Variación absoluta", VAR_USD), Columna("Variación relativa", VAR_PCT), Columna("Sentido"), Columna("Observación")],
        notas=[_NOTA_FORMULAS] + ([_NOTA_2023_2024] if {anio, anterior} == {2023, 2024} else []),
    )
    if estado == "ER":
        seccion.notas.append("Costos y gastos en positivo, como en el trabajo: un aumento significa mayor costo o gasto.")
    for fila in dos_ejercicios(horizontal_de_estado(lista, estado, nivel), anio, anterior):
        if fila.tipo != "cuenta":
            seccion.filas_destacadas.add(len(seccion.filas))
        seccion.filas.append([fila.etiqueta, fila.actual, fila.anterior, fila.var_abs, fila.var_pct, fila.tendencia, fila.nota])
    return seccion


def base_financiera(lista: list[DatosEjercicio], claves, titulo: str = "Base financiera utilizada") -> Seccion:
    """Importes de los que parten los indicadores (saldos al cierre), como la base de la seccion 8.4 del trabajo."""
    anios = _anios(lista)
    seccion = Seccion(titulo, [Columna("Concepto")] + [Columna(str(a), USD) for a in anios])
    for clave in claves:
        seccion.filas.append([CONCEPTOS[clave].etiqueta] + [CONCEPTOS[clave].obtener(d) for d in lista if d.tiene_datos])
    return seccion


def vertical(lista: list[DatosEjercicio], estado: str) -> Seccion:
    filas = vertical_comparativo(lista, estado)
    anios = sorted({a for f in filas for a in f.valores})
    if estado == "ER":
        titulo = f"Análisis vertical del estado de resultados {_rango(anios)} (% de los ingresos ordinarios)"
        nota = ("Base: ingresos ordinarios de cada ejercicio. Costos y gastos con signo negativo, como en el trabajo "
                "(sección 7.1).")
    else:
        titulo = f"Análisis vertical del balance general {_rango(anios)} (% del activo total)"
        nota = "Base: activo total de cada ejercicio (sección 7.2)."
    seccion = Seccion(titulo, [Columna("Partida")] + [Columna(str(a), PCT) for a in anios] + [Columna(f"Importe {a}", USD) for a in anios],
                      notas=[nota])
    for f in filas:
        if f.tipo != "cuenta":
            seccion.filas_destacadas.add(len(seccion.filas))
        seccion.filas.append([f.etiqueta] + [f.porcentajes.get(a) for a in anios] + [f.valores.get(a) for a in anios])
        if f.nota:
            seccion.notas.append(f"{f.etiqueta}: {f.nota}")
    return seccion


# ------------------------------------------------------------ indicadores
def indicadores(lista: list[DatosEjercicio], categoria: str) -> Seccion:
    anios = _anios(lista)
    seccion = Seccion(
        f"Indicadores — {categoria}",
        [Columna("Indicador"), Columna("Fórmula"), Columna("Cuentas utilizadas"), Columna("Unidad")]
        + [Columna(str(a), POR_FILA) for a in anios] + [Columna(f"Interpretación ({anios[-1] if anios else ''})"),
                                                         Columna("Sección del trabajo")],
        columna_unidad=3,
    )
    for indicador, resultados in ind.calcular_todos(lista, categoria):
        ultimo = resultados.get(anios[-1]) if anios else None
        seccion.filas.append(
            [indicador.nombre, indicador.formula, indicador.insumos, indicador.unidad]
            + [resultados[a].valor if a in resultados else None for a in anios]
            + [ind.interpretacion(ultimo) if ultimo else "", indicador.seccion_anf]
        )
        motivos = {r.motivo for r in resultados.values() if r.motivo}
        notas = {r.nota for r in resultados.values() if r.nota}
        for m in motivos:
            seccion.notas.append(f"{indicador.nombre}: no calculable — {m}")
        for n in notas:
            seccion.notas.append(f"{indicador.nombre}: {n}")
    seccion.notas = list(dict.fromkeys(seccion.notas))
    return seccion


def bases_cxc(lista: list[DatosEjercicio]) -> Seccion:
    """Las dos carteras, en todos los ejercicios y sin mezclarlas: no son el mismo indicador."""
    anios = _anios(lista)
    seccion = Seccion(
        "Cuentas por cobrar: dos bases que no son equivalentes",
        [Columna("Concepto")] + [Columna(str(a), POR_FILA) for a in anios] + [Columna("Unidad")],
        columna_unidad=len(anios) + 1,
        notas=["Línea comercial presentada: fórmula explícita de la sección 9.3 y base del PPC, del ciclo operativo y del CCE de "
               "esta aplicación. Desde que los estados presentan una sola línea, esa línea ya incluye otras cuentas por cobrar.",
               "Comerciales y otras: la misma regla en todos los ejercicios. La sección 8.2 B publica este valor solo en el "
               "primer ejercicio en que une ambas líneas; en los anteriores usa la línea comercial, por lo que su serie no sigue "
               "una regla única.",
               "Las dos bases no deben compararse como si fueran el mismo indicador."],
    )
    for titulo, rubro, rotacion, ppc in (
            ("Línea comercial presentada (9.3)", "rubro:CXC_COMERCIALES_PRESENTADA", "rotacion_cxc", "ppc"),
            ("Comerciales y otras", "rubro:CXC_COMERCIALES_Y_OTRAS", "rotacion_cxc_total", "ppc_total")):
        for etiqueta, obtener, unidad in ((f"{titulo}: saldo al cierre", CONCEPTOS[rubro].obtener, ind.USD),
                                          (f"{titulo}: rotación", (lambda c: lambda d: ind.calcular(d, c).valor)(rotacion), ind.VECES),
                                          (f"{titulo}: período de cobro", (lambda c: lambda d: ind.calcular(d, c).valor)(ppc), ind.DIAS_U)):
            seccion.filas.append([etiqueta] + [obtener(d) for d in lista if d.tiene_datos] + [unidad])
    return seccion


def capital_trabajo(lista: list[DatosEjercicio]) -> Seccion:
    """Evolucion del capital de trabajo (estructura de la Tabla 6 del trabajo)."""
    anios = _anios(lista)
    por = {d.anio: d for d in lista if d.tiene_datos}
    seccion = Seccion(
        "Tabla 6. Capital de trabajo neto y razones de liquidez",
        [Columna("Ejercicio"), Columna("Activo corriente", USD), Columna("Pasivo corriente", USD), Columna("CTN", VAR_USD),
         Columna("Var. absoluta CTN", VAR_USD), Columna("Var. relativa CTN", VAR_PCT), Columna("Razón corriente", VECES),
         Columna("Prueba ácida", VECES), Columna("Razón de tesorería", PCT)],
        notas=["CTN = Activo corriente − Pasivo corriente; RC = AC / PC; PA = (AC − Inventarios) / PC; "
               "Tesorería = (Efectivo + inversiones corrientes) / PC × 100."],
    )
    for anio in anios:
        d = por[anio]
        ctn = ind.calcular(d, "ctn").valor
        anterior = por.get(anio - 1)
        absoluta, relativa, nota = variacion(ctn, ind.calcular(anterior, "ctn").valor) if anterior else ("Base", "Base", "")
        seccion.filas.append([str(anio), d.bs.activo_corriente.subtotal, d.bs.pasivo_corriente.subtotal, ctn, absoluta, relativa,
                              ind.calcular(d, "razon_corriente").valor, ind.calcular(d, "prueba_acida").valor,
                              ind.calcular(d, "razon_tesoreria").valor])
        if nota and anterior:
            seccion.notas.append(f"{anio}: {nota}")
    return seccion


def capital_trabajo_interanual(lista: list[DatosEjercicio]) -> Seccion:
    """Resumen de variaciones por periodo (estructura de la Tabla 7 del trabajo)."""
    con_balance = [d for d in lista if d.bs.tiene_datos]
    seccion = Seccion(
        "Tabla 7. Resumen de variaciones del capital de trabajo neto [USD]",
        [Columna("Período comparativo"), Columna("Activo corriente inicial", USD), Columna("Activo corriente final", USD),
         Columna("Pasivo corriente inicial", USD), Columna("Pasivo corriente final", USD), Columna("CTN inicial", VAR_USD),
         Columna("CTN final", VAR_USD), Columna("Variación absoluta CTN", VAR_USD), Columna("Variación relativa CTN", VAR_PCT)],
    )
    for a, b in zip(con_balance, con_balance[1:]):
        if b.anio != a.anio + 1:
            continue
        inicial, final = ind.calcular(a, "ctn").valor, ind.calcular(b, "ctn").valor
        absoluta, relativa, nota = variacion(final, inicial)
        seccion.filas.append([f"{a.anio} vs {b.anio}", a.bs.activo_corriente.subtotal, b.bs.activo_corriente.subtotal,
                              a.bs.pasivo_corriente.subtotal, b.bs.pasivo_corriente.subtotal, inicial, final, absoluta, relativa])
        if nota:
            seccion.notas.append(f"{a.anio} vs {b.anio}: {nota}")
    return seccion


def _x100(fraccion):
    return fraccion * 100 if fraccion is not None else None


def dupont(lista: list[DatosEjercicio]) -> list[Seccion]:
    anios = _anios(lista)
    por = {d.anio: d for d in lista if d.tiene_datos}
    total = Seccion(
        "Sistema DuPont con saldos al cierre — enfoque total (secciones 9.5 y 9.6)",
        [Columna("Concepto")] + [Columna(str(a), POR_FILA) for a in anios] + [Columna("Unidad")],
        columna_unidad=len(anios) + 1,
        notas=["RSA = Margen neto × Rotación de activos; RSP = RSA × MAF; MAF = Activo total / Patrimonio total. "
               "Saldos al cierre (criterio del trabajo), igual que el reporte «Rentabilidad mediante fórmula DuPont»."],
    )
    filas_total = [("Ingresos ordinarios", lambda d: d.inc.ingresos_netos.subtotal, ind.USD),
                   ("Utilidad neta del ejercicio", lambda d: d.inc.utilidad_neta, ind.USD),
                   ("Activo total", lambda d: d.bs.total_activo, ind.USD),
                   ("Patrimonio total", lambda d: d.bs.total_patrimonio, ind.USD)]
    for clave, obtener in (("margen_neto", lambda d: _x100(factores_total(d).margen_neto)),
                           ("rotacion_activos", lambda d: factores_total(d).rotacion_activos),
                           ("roa_dupont", lambda d: _x100(factores_total(d).rsa)),
                           ("maf", lambda d: factores_total(d).maf_interpretable),
                           ("roe_dupont", lambda d: _x100(factores_total(d).rsp_interpretable))):
        i = ind.POR_CLAVE[clave]
        filas_total.append((i.nombre, obtener, i.unidad))
    # Comprobacion con las formulas directas de la seccion 8.4 (indicadores ROA y ROE).
    for clave in ("roa", "roe"):
        i = ind.POR_CLAVE[clave]
        filas_total.append((f"{i.nombre} — verificación directa", (lambda c: lambda d: ind.calcular(d, c).valor)(clave), i.unidad))
    for etiqueta, obtener, unidad in filas_total:
        total.filas.append([etiqueta] + [obtener(por[a]) for a in anios] + [unidad])

    ctrl = Seccion(
        "Sistema DuPont — enfoque de la controladora",
        [Columna("Concepto")] + [Columna(str(a), POR_FILA) for a in anios] + [Columna("Unidad")],
        columna_unidad=len(anios) + 1,
    )
    filas_ctrl = [("Utilidad atribuible a la controladora", lambda d: d.utilidad_controladora()[0], ind.USD),
                  ("Patrimonio atribuible a la controladora", lambda d: d.patrimonio_controladora, ind.USD)]
    for clave, obtener in (("margen_neto_controladora", lambda d: _x100(factores_controladora(d)[0].margen_neto)),
                           ("rotacion_activos", lambda d: factores_controladora(d)[0].rotacion_activos),
                           ("roa_controladora", lambda d: _x100(factores_controladora(d)[0].rsa)),
                           ("maf_controladora", lambda d: factores_controladora(d)[0].maf_interpretable),
                           ("roe_controladora", lambda d: _x100(factores_controladora(d)[0].rsp_interpretable))):
        i = ind.POR_CLAVE[clave]
        filas_ctrl.append((i.nombre, obtener, i.unidad))
    for etiqueta, obtener, unidad in filas_ctrl:
        ctrl.filas.append([etiqueta] + [obtener(por[a]) for a in anios] + [unidad])
    for a in anios:
        ctrl.notas.append(f"{a}: utilidad atribuible — {por[a].utilidad_controladora()[1]}.")
    return [total, ctrl]


# ------------------------------------------------------------------- WACC
def wacc_resumen(resultados: list[ResultadoWACC]) -> Seccion:
    anios = [r.anio for r in resultados]
    seccion = Seccion(
        "WACC — comparativo (método del trabajo, sección 9.4)",
        [Columna("Componente")] + [Columna(str(a), POR_FILA) for a in anios] + [Columna("Unidad")],
        columna_unidad=len(anios) + 1,
        notas=[
            "Ponderación sobre pasivo total + patrimonio. Pasivos operativos con costo 0 %; deuda financiera a la tasa "
            "supuesta × (1 − t); patrimonio a Ke = ROE al cierre (no es el rendimiento exigido por los socios).",
            "Las tasas de interés y la tasa de ISR son SUPUESTOS del trabajo ANF (fuentes/anf/supuestos_wacc.json): no "
            "pueden verificarse con los documentos disponibles. Los importes, pesos y Ke sí provienen de los estados "
            "financieros originales.",
        ],
    )
    filas = [
        ("Total financiamiento (pasivo + patrimonio)", "total_financiamiento", ind.USD),
        ("Pasivos operativos sin costo (% del total)", "pct_pasivos_operativos", ind.PCT),
        ("Deuda financiera con costo (% del total)", "pct_deuda_financiera", ind.PCT),
        ("Patrimonio (% del total)", "pct_patrimonio", ind.PCT),
        ("Costo del patrimonio (Ke = ROE)", "ke_pct", ind.PCT),
        ("Tasa de ISR (supuesto)", "tasa_isr_pct", ind.PCT),
        ("Costo neto promedio de la deuda financiera", "kd_neto_promedio_pct", ind.PCT),
        ("Aporte de la deuda al WACC", "aporte_deuda_pct", ind.PCT),
        ("Aporte del patrimonio al WACC", "aporte_patrimonio_pct", ind.PCT),
        ("WACC", "wacc_pct", ind.PCT),
        ("ROA (utilidad neta / financiamiento total)", "roa_pct", ind.PCT),
        ("Spread (ROA − costo neto de la deuda)", "spread_pct", ind.PCT),
    ]
    for etiqueta, attr, unidad in filas:
        if attr == "wacc_pct":
            seccion.filas_destacadas.add(len(seccion.filas))
        seccion.filas.append([etiqueta] + [getattr(r, attr) for r in resultados] + [unidad])
    seccion.filas.append(["Diagnóstico"] + [r.diagnostico for r in resultados] + [""])
    for r in resultados:
        if r.motivo:
            seccion.notas.append(f"{r.anio}: {r.motivo}")
        for a in r.advertencias:
            seccion.notas.append(f"{r.anio}: {a}")
    return seccion


def wacc_detalle(resultado: ResultadoWACC) -> Seccion:
    seccion = Seccion(
        f"WACC {resultado.anio} — detalle por fuente de financiamiento",
        [Columna("Tipo"), Columna("Código"), Columna("Cuenta"), Columna("Importe", USD), Columna("Costo", PCT),
         Columna("Costo neto", PCT), Columna("Proporción", PCT), Columna("Aporte al WACC", PCT), Columna("Cita del trabajo (no verificada)")],
    )
    for l in resultado.lineas:
        seccion.filas.append([l.tipo.capitalize(), l.codigo, l.nombre, l.importe, l.costo_pct, l.costo_neto_pct, l.proporcion_pct,
                              l.aporte_pct, l.cita])
    seccion.filas_destacadas.add(len(seccion.filas))
    seccion.filas.append(["TOTAL", "", "", resultado.total_financiamiento, None, None,
                          sum((l.proporcion_pct for l in resultado.lineas), Decimal(0)), resultado.wacc_pct, ""])
    if resultado.motivo:
        seccion.notas.append(resultado.motivo)
    return seccion


def supuestos_wacc() -> Seccion:
    datos = cargar_supuestos()
    anios = sorted(datos["ejercicios"])
    grupos = sorted({g for a in anios for g in datos["ejercicios"][a]["tasas"]}, key=lambda g: list(GRUPOS).index(g))
    seccion = Seccion("Supuestos del WACC tomados del trabajo ANF (no verificables con los documentos)",
                      [Columna("Fuente de deuda (grupo de análisis)")] + [Columna(a, PCT) for a in anios],
                      notas=[datos["descripcion"], datos["metodo_costo_patrimonio"]])
    seccion.filas.append(["Tasa de ISR"] + [Decimal(datos["ejercicios"][a]["tasa_isr"]) for a in anios])
    for g in grupos:
        seccion.filas.append([GRUPOS[g].nombre] + [Decimal(datos["ejercicios"][a]["tasas"][g])
                                                    if g in datos["ejercicios"][a]["tasas"] else None for a in anios])
    return seccion


# -------------------------------------------------------- fuentes y usos
def fuentes_usos(resultado: ResultadoFuentesUsos) -> Seccion:
    seccion = Seccion(
        f"Estado de origen y aplicación de fondos {resultado.anio_actual} vs {resultado.anio_anterior}",
        [Columna("Partida (grupo de análisis)"), Columna("Grupo"), Columna(str(resultado.anio_actual), USD),
         Columna(str(resultado.anio_anterior), USD), Columna("Variación", USD), Columna("Fuente", USD), Columna("Uso", USD),
         Columna("Cuentas incluidas")],
        notas=["Activo: disminución = fuente; aumento = uso. Pasivo y patrimonio: aumento = fuente; disminución = uso. "
               "No es un estado de flujos de efectivo."] + resultado.advertencias,
    )
    for l in resultado.lineas:
        seccion.filas.append([l.concepto, l.grupo_estado, l.actual, l.anterior, l.variacion, l.fuente or None, l.uso or None,
                              "; ".join(l.cuentas)])
    seccion.filas_destacadas.add(len(seccion.filas))
    seccion.filas.append(["TOTALES (sumas iguales)" if resultado.cuadra else "TOTALES (NO CUADRAN)", "", None, None, None,
                          resultado.total_fuentes, resultado.total_usos, ""])
    return seccion


# ------------------------------------------------------------ comparacion
def comparacion(comparaciones: list[Comparacion], *, solo_estados: tuple[str, ...] | None = None,
                titulo: str = "Comparación con el trabajo de investigación ANF") -> Seccion:
    seccion = Seccion(
        titulo,
        [Columna("Ref."), Columna("Sección"), Columna("Tabla"), Columna("Indicador / concepto"), Columna("Año"),
         Columna("Resultado aplicación", POR_FILA), Columna("Resultado trabajo ANF", POR_FILA), Columna("Diferencia", POR_FILA),
         Columna("Diferencia %", PCT), Columna("Estado"), Columna("Unidad"), Columna("Categoría de la causa"),
         Columna("Causa documentada")],
        columna_unidad=10,
        notas=["Coincide: igual al redondear a la precisión del trabajo. Coincidencia por redondeo: diferencia ≤ una unidad "
               "del último decimal presentado. Diferencia: mayor que esa tolerancia (causa investigada). No verificable: "
               "faltan datos. No aplica: ambos lo declaran no calculable.",
               "Importes en millones cuando el trabajo los presenta así (EBITDA, CTN y escala de la sección 10)."],
    )
    for c in comparaciones:
        if solo_estados and c.estado not in solo_estados:
            continue
        unidad = {"USD": ind.USD, "%": ind.PCT, "veces": ind.VECES, "días": ind.DIAS_U}.get(c.referencia.unidad, ind.VECES)
        anf = "No calculable" if c.valor_anf is None else c.valor_anf
        seccion.filas.append([c.referencia.id, c.referencia.seccion, c.referencia.tabla, c.referencia.concepto, str(c.anio),
                              c.valor_app if c.valor_app is not None else "No calculable", anf, c.diferencia, c.diferencia_pct,
                              c.estado, unidad, c.categoria, c.causa])
    return seccion


# ------------------------------------------------------------ trazabilidad
def trazabilidad(session: Session, lista: list[DatosEjercicio]) -> list[Seccion]:
    controles = Seccion(
        "Controles de carga: totales impresos en los documentos vs. totales calculados",
        [Columna("Año"), Columna("Concepto"), Columna("Denominación impresa"), Columna("Impreso", USD), Columna("Calculado", USD),
         Columna("Diferencia", USD), Columna("Estado"), Columna("Documento"), Columna("Pág.")],
    )
    fuentes = Seccion(
        "Fuente de cada importe original",
        [Columna("Año"), Columna("Estado"), Columna("Código"), Columna("Cuenta"), Columna("Denominación original"),
         Columna("Cifra impresa"), Columna("Valor registrado", USD), Columna("Valor vigente", USD), Columna("Control"),
         Columna("Documento"), Columna("Pág.")],
        notas=["Control MODIFICADO o ELIMINADO: el importe vigente ya no es el que se cargó desde el documento "
               "(se editó después). La aplicación no lo corrige: revise el historial de cambios."],
    )
    complementarios = Seccion(
        "Datos complementarios originales (no son cuentas del catálogo)",
        [Columna("Año"), Columna("Clave"), Columna("Denominación original"), Columna("Importe", USD), Columna("Estado financiero"),
         Columna("Documento"), Columna("Pág.")],
    )
    for d in lista:
        for c in controles_totales(d, session):
            controles.filas.append([str(c.anio), c.concepto, c.nombre_original, c.declarado, c.calculado, c.diferencia, c.estado,
                                    c.documento, c.pagina])
        for f in controles_fuentes(session, d.periodo):
            fuentes.filas.append([str(f.anio), "Balance" if f.tipo == "BALANCE" else "Resultados", f.codigo, f.cuenta,
                                  f.nombre_original, f.importe_documento, f.valor_registrado, f.valor_vigente, f.estado,
                                  f.documento, f.pagina])
        for dato in d.complementarios.values():
            if dato.tipo == "COMPLEMENTARIO":
                complementarios.filas.append([str(d.anio), dato.clave, dato.nombre_original, dato.valor, dato.estado_financiero,
                                              dato.documento, dato.pagina])
        for cuenta, valor, tipo in d.sin_grupo:
            fuentes.notas.append(f"{d.anio}: la cuenta {cuenta.codigo} — {cuenta.nombre} ({valor}) no tiene grupo de análisis; "
                                 "no participa en los indicadores por rubro.")
    return [controles, fuentes, complementarios]


def mapeo_cuentas(session: Session) -> Seccion:
    """Correspondencia cuenta original -> grupo normalizado -> clase -> indicadores."""
    from database.repositories import list_accounts

    seccion = Seccion(
        "Mapeo de cuentas: denominación, grupo normalizado, clasificación e indicadores",
        [Columna("Código"), Columna("Cuenta"), Columna("Categoría"), Columna("Subcategoría"), Columna("Grupo de análisis"),
         Columna("Clase"), Columna("Tipo de pasivo (WACC)"), Columna("Indicadores en los que participa")],
    )
    for cuenta in list_accounts(session):
        grupo = GRUPOS.get(cuenta.grupo_analisis or "")
        indicadores_ = ind.indicadores_de_grupo(grupo.codigo, grupo.clase) if grupo else []
        seccion.filas.append([
            cuenta.codigo, cuenta.nombre, cuenta.categoria_principal.value,
            cuenta.subcategoria.value if cuenta.subcategoria else "",
            f"{grupo.codigo} — {grupo.nombre}" if grupo else "(sin grupo)", NOMBRE_CLASE.get(grupo.clase, "") if grupo else "",
            (grupo.tipo_pasivo or "") if grupo else "", ", ".join(i.nombre for i in indicadores_),
        ])
    return seccion
