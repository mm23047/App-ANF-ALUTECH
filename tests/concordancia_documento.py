"""Referencias independientes para las pruebas de concordancia.

Lee los valores publicados directamente de las tablas de «Trabajo de investigación
ANF.md» y recalcula cada uno con fracciones exactas a partir de
fuentes/alutech/estados_financieros_2021_2025.json. No importa ningun modulo de
calculations/ ni de reports/: si una formula de la aplicacion cambia, estas
referencias no cambian con ella.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DOCUMENTO = RAIZ / "Trabajo de investigación ANF.md"
ANIOS = range(2021, 2026)


def lineas_documento() -> list[str]:
    return DOCUMENTO.read_text(encoding="utf-8").splitlines()


def tabla(lineas: list[str], marcador: str, desde: int = 0) -> list[list[str]]:
    """Primera tabla Markdown despues del primer renglon que contiene `marcador`."""
    i = next(n for n, linea in enumerate(lineas) if n >= desde and marcador in linea)
    while not lineas[i].startswith("|"):
        i += 1
    filas = []
    while i < len(lineas) and lineas[i].startswith("|"):
        celdas = [c.strip() for c in lineas[i].strip().strip("|").split("|")]
        if not all(re.fullmatch(r":?-+:?", c) for c in celdas):
            filas.append(celdas)
        i += 1
    return filas


def limpiar_celda(celda: str) -> str:
    """Texto de la celda sin marcas de Markdown, sin la llamada de nota † y con guion simple."""
    return celda.replace("*", "").replace("\\", "").replace("†", "").replace("−", "-").strip()


def numero(celda: str, europeo: bool = False) -> tuple[Decimal, int] | None:
    """(valor, decimales publicados) o None si la celda no es numerica."""
    t = limpiar_celda(celda).replace("$", "").replace("+", "").replace("%", "")
    t = re.sub(r"(veces|días|x)\s*$", "", t).strip()
    if europeo:  # las tablas 9.5 y 9.6 usan punto de miles y coma decimal en parte de sus celdas
        t = t.replace(".", "").replace(",", ".") if ("," in t or t.count(".") > 1) else t
    else:
        t = t.replace(",", "")
    if not re.fullmatch(r"-?\d+(\.\d+)?", t):
        return None
    return Decimal(t), len(t.split(".")[1]) if "." in t else 0


def redondear(valor: Decimal, decimales: int) -> Decimal:
    return valor.quantize(Decimal(1).scaleb(-decimales), rounding=ROUND_HALF_UP)


# ------------------------------------------------- recalculo independiente
_FUENTE = json.loads((RAIZ / "fuentes/alutech/estados_financieros_2021_2025.json").read_text(encoding="utf-8"))
_CUENTAS = {c["codigo"]: c for c in _FUENTE["cuentas"]}


def _importe(texto: str) -> Fraction:
    texto = texto.strip()
    if texto in ("-", "—", ""):
        return Fraction(0)
    negativo = texto.startswith("(")
    valor = Fraction(texto.strip("()").replace(",", ""))
    return -valor if negativo else valor


def _a_2_decimales(valor: Fraction) -> Fraction:
    """Redondeo a 2 decimales, mitad hacia arriba, con aritmetica entera."""
    return Fraction(int(abs(valor) * 100 + Fraction(1, 2)), 100) * (1 if valor >= 0 else -1)


def _co(d) -> Fraction:
    """Desarrollo escrito de 9.3: suma los operandos ya redondeados a 2 decimales."""
    return _a_2_decimales(365 * d.inv / d.cv) + _a_2_decimales(365 * d.cxc / d.ing)


class Ejercicio:
    """Importes de un ejercicio tal como se imprimen: los gastos llegan con signo negativo."""

    def __init__(self, anio: int):
        datos = _FUENTE["ejercicios"][str(anio)]
        self.bal, self.res, self.clase = {}, {}, {}
        for codigo, _, valor, *_ in datos["BALANCE"]:
            c = _CUENTAS[codigo]
            self.bal[c["grupo"]] = self.bal.get(c["grupo"], Fraction(0)) + _importe(valor)
            clave = c["categoria"] if c["categoria"] == "PATRIMONIO" else f'{c["categoria"]}/{c["subcategoria"]}'
            self.clase[clave] = self.clase.get(clave, Fraction(0)) + _importe(valor)
        for codigo, _, valor, *_ in datos["RESULTADOS"]:
            grupo = _CUENTAS[codigo]["grupo"]
            self.res[grupo] = self.res.get(grupo, Fraction(0)) + _importe(valor)
        self.comp = {r[0]: r[2] for r in datos["datos_complementarios"]}

    def b(self, *grupos):
        return sum((self.bal.get(g, Fraction(0)) for g in grupos), Fraction(0))

    def r(self, *grupos):
        return sum((self.res.get(g, Fraction(0)) for g in grupos), Fraction(0))

    ac = property(lambda s: s.clase["ACTIVO/CORRIENTE"])
    anc = property(lambda s: s.clase["ACTIVO/NO_CORRIENTE"])
    ta = property(lambda s: s.ac + s.anc)
    pc = property(lambda s: s.clase["PASIVO/CORRIENTE"])
    pnc = property(lambda s: s.clase["PASIVO/NO_CORRIENTE"])
    tp = property(lambda s: s.pc + s.pnc)
    pat = property(lambda s: s.clase["PATRIMONIO"])
    ing = property(lambda s: s.r("INGRESOS_ORDINARIOS"))
    cv = property(lambda s: -s.r("COSTO_VENTAS"))
    ub = property(lambda s: s.ing - s.cv)
    gop = property(lambda s: -s.r("GASTOS_ADMINISTRACION", "GASTOS_VENTA", "GASTOS_PERSONAL", "DEPRECIACION_AMORTIZACION"))
    uo = property(lambda s: s.ub - s.gop + s.r("DETERIORO_CXC", "OTROS_INGRESOS_OPERATIVOS"))
    gf = property(lambda s: -s.r("GASTOS_FINANCIEROS", "GASTOS_FINANCIEROS_NETOS"))
    gfn = property(lambda s: s.gf - s.r("INGRESOS_FINANCIEROS"))
    un = property(lambda s: sum(s.res.values(), Fraction(0)))
    uai = property(lambda s: s.un - s.r("IMPUESTO_RENTA"))
    inv = property(lambda s: s.b("INVENTARIOS"))
    efe = property(lambda s: s.b("EFECTIVO"))
    cxc = property(lambda s: s.b("CXC_COMERCIALES", "DEUDORES_COMERCIALES_OTRAS"))
    cxct = property(lambda s: s.b("CXC_COMERCIALES", "OTRAS_CXC_CP", "DEUDORES_COMERCIALES_OTRAS"))
    cxp = property(lambda s: s.b("CXP_COMERCIALES", "ACREEDORES_COMERCIALES_OTRAS"))
    tes = property(lambda s: s.b("EFECTIVO", "INVERSIONES_CP"))
    patc = property(lambda s: s.pat - s.b("NO_CONTROLADORAS"))

    @property
    def uc(self):
        for clave in ("utilidad_controladora_ecp", "utilidad_controladora_er"):
            if clave in self.comp:
                return _importe(self.comp[clave])
        return self.un  # sin no controladoras: 2024 y 2025 no informan la atribucion


EJERCICIOS = {a: Ejercicio(a) for a in ANIOS}

# metrica -> (clave en la aplicacion, recalculo independiente)
METRICAS = {
    "efe": ("rubro:EFECTIVO", lambda d: d.efe), "cxc": ("rubro:CXC_COMERCIALES_PRESENTADA", lambda d: d.cxc),
    "cxct": ("rubro:CXC_COMERCIALES_Y_OTRAS", lambda d: d.cxct), "inv": ("rubro:INVENTARIOS", lambda d: d.inv),
    "ac": ("activo_corriente", lambda d: d.ac), "anc": ("activo_no_corriente", lambda d: d.anc),
    "pc": ("pasivo_corriente", lambda d: d.pc), "pnc": ("pasivo_no_corriente", lambda d: d.pnc),
    "ta": ("total_activo", lambda d: d.ta), "tp": ("total_pasivo", lambda d: d.tp), "pat": ("total_patrimonio", lambda d: d.pat),
    "ing": ("ingresos", lambda d: d.ing), "cv": ("costo_ventas", lambda d: d.cv), "ub": ("utilidad_bruta", lambda d: d.ub),
    "gop": ("gastos_operativos_anf", lambda d: d.gop), "uo": ("utilidad_operativa", lambda d: d.uo),
    "gfn": ("gastos_financieros_netos", lambda d: d.gfn), "un": ("utilidad_neta", lambda d: d.un),
    "ctn": ("ind:ctn", lambda d: d.ac - d.pc), "rc": ("ind:razon_corriente", lambda d: d.ac / d.pc),
    "pa": ("ind:prueba_acida", lambda d: (d.ac - d.inv) / d.pc), "tes": ("rubro:TESORERIA", lambda d: d.tes),
    "rte": ("ind:razon_tesoreria", lambda d: d.tes / d.pc * 100), "cper": ("ind:capitales_permanentes", lambda d: d.pat + d.pnc),
    "fmlp": ("ind:fondo_maniobra_lp", lambda d: d.pat + d.pnc - d.anc), "rinv": ("ind:rotacion_inventarios", lambda d: d.cv / d.inv),
    "ppi": ("ind:ppi", lambda d: 365 * d.inv / d.cv), "rcxc": ("ind:rotacion_cxc", lambda d: d.ing / d.cxc),
    "ppc": ("ind:ppc", lambda d: 365 * d.cxc / d.ing), "rcxct": ("ind:rotacion_cxc_total", lambda d: d.ing / d.cxct),
    "ppct": ("ind:ppc_total", lambda d: 365 * d.cxct / d.ing), "cxp": ("rubro:CXP_COMERCIALES_PRESENTADA", lambda d: d.cxp),
    "ppp": ("ind:ppp", lambda d: 365 * d.cxp / d.cv), "co": ("ind:ciclo_operativo", _co),
    "cce": ("ind:cce", lambda d: _co(d) - _a_2_decimales(365 * d.cxp / d.cv)),
    "rat": ("ind:rotacion_activos", lambda d: d.ing / d.ta), "end": ("ind:endeudamiento", lambda d: d.tp / d.ta * 100),
    "cob": ("ind:cobertura_intereses", lambda d: d.uo / d.gfn), "cpf": ("ind:cobertura_pagos_fijos", lambda d: d.uo / d.gfn),
    "dc": ("ind:deuda_capital", lambda d: d.tp / d.pat), "mb": ("ind:margen_bruto", lambda d: d.ub / d.ing * 100),
    "mo": ("ind:margen_operativo", lambda d: d.uo / d.ing * 100), "mn": ("ind:margen_neto", lambda d: d.un / d.ing * 100),
    "roa": ("ind:roa", lambda d: d.un / d.ta * 100), "roe": ("ind:roe", lambda d: d.un / d.pat * 100),
    "maf": ("ind:maf", lambda d: d.ta / d.pat), "road": ("ind:roa_dupont", lambda d: d.un / d.ta * 100),
    "roed": ("ind:roe_dupont", lambda d: d.un / d.pat * 100), "uc": ("utilidad_controladora", lambda d: d.uc),
    "patc": ("patrimonio_controladora", lambda d: d.patc), "mnc": ("ind:margen_neto_controladora", lambda d: d.uc / d.ing * 100),
    "rac": ("ind:roa_controladora", lambda d: d.uc / d.ta * 100), "mafc": ("ind:maf_controladora", lambda d: d.ta / d.patc),
    "roec": ("ind:roe_controladora", lambda d: d.uc / d.patc * 100),
}
_ER = {"v_ing": ("s_ingresos", lambda d: d.ing), "v_cv": ("s_costo_ventas", lambda d: -d.cv), "v_ub": ("s_utilidad_bruta", lambda d: d.ub),
       "v_adm": ("s_gastos_administracion", lambda d: d.r("GASTOS_ADMINISTRACION")), "v_ven": ("s_gastos_venta", lambda d: d.r("GASTOS_VENTA")),
       "v_det": ("s_deterioro_cxc", lambda d: d.r("DETERIORO_CXC")), "v_per": ("s_gastos_personal", lambda d: d.r("GASTOS_PERSONAL")),
       "v_dep": ("s_depreciacion_amortizacion", lambda d: d.r("DEPRECIACION_AMORTIZACION")),
       "v_otr": ("s_otros_ingresos_gastos", lambda d: d.r("OTROS_INGRESOS_OPERATIVOS", "OTROS_NO_OPERATIVOS")),
       "v_uo": ("s_utilidad_operativa", lambda d: d.uo), "v_if": ("s_ingresos_financieros", lambda d: d.r("INGRESOS_FINANCIEROS")),
       "v_gf": ("s_gastos_financieros", lambda d: -d.gf), "v_uai": ("s_utilidad_antes_impuestos", lambda d: d.uai),
       "v_isr": ("s_impuesto_renta", lambda d: d.r("IMPUESTO_RENTA")), "v_un": ("s_utilidad_neta", lambda d: d.un)}
for _k, (_clave, _fn) in _ER.items():
    METRICAS[_k] = (f"vert_er:{_clave}", (lambda fn: lambda d: fn(d) / d.ing * 100)(_fn))
_BG = {"b_ac": ("activo_corriente", "ac"), "b_inv": ("rubro:INVENTARIOS", "inv"), "b_anc": ("activo_no_corriente", "anc"),
       "b_ta": ("total_activo", "ta"), "b_pc": ("pasivo_corriente", "pc"), "b_pnc": ("pasivo_no_corriente", "pnc"),
       "b_tp": ("total_pasivo", "tp"), "b_pat": ("total_patrimonio", "pat")}
for _k, (_clave, _attr) in _BG.items():
    METRICAS[_k] = (f"vert_bg:{_clave}", (lambda a: lambda d: getattr(d, a) / d.ta * 100)(_attr))


def independiente(metrica: str, anio: int, variacion: str | None = None) -> Decimal:
    fn = METRICAS[metrica][1]
    actual = Fraction(fn(EJERCICIOS[anio]))
    if variacion:
        anterior = Fraction(fn(EJERCICIOS[anio - 1]))
        actual = actual - anterior if variacion == "abs" else (actual - anterior) / anterior * 100
    return Decimal(actual.numerator) / Decimal(actual.denominator)


@dataclass(frozen=True)
class Valor:
    seccion: str
    tabla: str
    partida: str
    anio: int
    publicado: Decimal
    decimales: int
    metrica: str
    variacion: str | None = None

    @property
    def clave_app(self) -> str:
        base = METRICAS[self.metrica][0]
        return {"abs": f"var_abs:{base}", "pct": f"var_pct:{base}"}.get(self.variacion, base)

    @property
    def id(self) -> tuple[str, str, int]:
        return self.seccion, self.partida, self.anio


def valores_publicados() -> list[Valor]:
    lineas = lineas_documento()
    salida: list[Valor] = []

    def reg(sec, tab, partida, anio, celda, metrica, variacion=None, europeo=False):
        n = numero(celda, europeo)
        if n is not None:
            salida.append(Valor(sec, tab, partida, anio, n[0], n[1], metrica, variacion))

    def fila_tabla_34(texto: str, cxc: str) -> str:
        t = limpiar_celda(texto).lower()
        for prefijo, metrica in (("efectivo", "efe"), ("cuentas por cobrar", cxc), ("inventarios", "inv"), ("total activo corriente", "ac"),
                                 ("total pasivo corriente", "pc"), ("total activo", "ta"), ("total pasivo", "tp"), ("total patrimonio", "pat")):
            if t.startswith(prefijo):
                return metrica
        raise KeyError(texto)

    for marca, inicio, cxc, nombre in (("Tabla 3\\.", 2021, "cxc", "Tabla 3"), ("Tabla 4\\.", 2023, "cxct", "Tabla 4")):
        for f in tabla(lineas, marca)[1:]:
            m, n = fila_tabla_34(f[0], cxc), limpiar_celda(f[0])
            reg("6.4", nombre, n, inicio, f[1], m)
            for k, anio in ((2, inicio + 1), (5, inicio + 2)):
                reg("6.4", nombre, n, anio, f[k], m)
                reg("6.4", nombre, f"{n} (var. abs.)", anio, f[k + 1], m, "abs")
                reg("6.4", nombre, f"{n} (var. %)", anio, f[k + 2], m, "pct")
    for f, m in zip(tabla(lineas, "Tabla 5\\.")[1:], ("ing", "cv", "ub", "gop", "uo", "gfn", "un")):
        for j, anio in enumerate(ANIOS):
            reg("6.4", "Tabla 5", f[0], anio, f[1 + j], m)
        for j, anio in enumerate(range(2022, 2026)):
            reg("6.4", "Tabla 5", f"{f[0]} (var. %)", anio, f[6 + j], m, "pct")
    for f in tabla(lineas, "Tabla 6\\.")[1:]:
        anio = int(limpiar_celda(f[0]))
        for j, (nombre, m, v) in enumerate((("AC", "ac", None), ("PC", "pc", None), ("CTN", "ctn", None), ("CTN var. abs.", "ctn", "abs"),
                                            ("CTN var. %", "ctn", "pct"), ("Razón corriente", "rc", None), ("Prueba ácida", "pa", None))):
            reg("6.5", "Tabla 6", nombre, anio, f[1 + j], m, v)
    for f in tabla(lineas, "Tabla 7\\.")[1:]:
        a, b = (int(x) for x in re.findall(r"\d{4}", f[0]))
        for j, (nombre, m, anio, v) in enumerate((("AC inicial", "ac", a, None), ("AC final", "ac", b, None), ("PC inicial", "pc", a, None),
                                                  ("PC final", "pc", b, None), ("CTN inicial", "ctn", a, None), ("CTN final", "ctn", b, None),
                                                  ("CTN var. abs.", "ctn", b, "abs"), ("CTN var. %", "ctn", b, "pct"))):
            reg("6.6", "Tabla 7", f"{nombre} ({a} vs {b})", anio, f[1 + j], m, v)

    def por_filas(sec, tab, marca, metricas, desde=0):
        for f, m in zip(tabla(lineas, marca, desde)[1:], metricas):
            for j, anio in enumerate(ANIOS):
                reg(sec, tab, limpiar_celda(f[0]), anio, f[1 + j], m)

    def por_anio(sec, tab, marca, columnas, desde=0):
        for f in tabla(lineas, marca, desde)[1:]:
            anio = int(re.search(r"\d{4}", f[0]).group())
            for j, par in enumerate(columnas):
                if par:
                    reg(sec, tab, par[0], anio, f[1 + j], par[1])

    por_filas("7.1", "Vertical ER", "Partida (% de ingresos)", ("v_ing", "v_cv", "v_ub", "v_adm", "v_ven", "v_det", "v_per", "v_dep", "v_otr",
                                                                 "v_uo", "v_if", "v_gf", "v_uai", "v_isr", "v_un"))
    por_filas("7.2", "Vertical BG", "Partida (% de activos totales)", ("b_ac", "b_inv", "b_anc", "b_ta", "b_pc", "b_pnc", "b_tp", "b_pat"))
    por_filas("8.1", "Liquidez", "Tabla de resultados de liquidez", ("rc", "pa", "ctn"))
    por_anio("8.2 A", "Inventarios", "Rotación y Período Promedio de Inventario", (("Costo de ventas", "cv"), ("Inventarios", "inv"), ("Rotación", "rinv"), ("PPI", "ppi")))
    por_anio("8.2 B", "CxC", "Rotación de Cuentas por Cobrar y Período Promedio de Cobro", (("Ingresos", "ing"), ("CxC", "cxc"), ("Rotación CxC", "rcxc"), ("PPC", "ppc")))
    por_anio("8.2 D", "Activos", "Rotación de Activos Totales (2021", (("Ingresos", "ing"), ("Total activo", "ta"), ("Rotación activos", "rat")))
    por_anio("8.3 A", "Endeudamiento", "Índice de Endeudamiento (2021", (("Total pasivo", "tp"), ("Total activo", "ta"), ("Índice", "end")))
    por_anio("8.3 B", "Cobertura", "Cobertura de Intereses (2021", (("Utilidad de operación", "uo"), ("Gastos financieros", "gfn"), ("Cobertura", "cob")))
    por_anio("8.3 D", "Deuda-capital", "Razón Deuda-Capital Patrimonial (2021", (("Total pasivo", "tp"), ("Total patrimonio", "pat"), ("Razón", "dc")))
    por_filas("8.4", "Base financiera", "Base financiera utilizada", ("ing", "ub", "uo", "un", "ta", "pat"))
    i84 = next(n for n, l in enumerate(lineas) if l.startswith("#### **8.4"))
    for letra, marca, num, den, m in (("A", "A. Margen de utilidad bruta", "ub", "ing", "mb"), ("B", "B. Margen de utilidad operativa", "uo", "ing", "mo"),
                                      ("C", "C. Margen de utilidad neta", "un", "ing", "mn"), ("E", "E. Rendimiento sobre los activos", "un", "ta", "roa"),
                                      ("F", "F. Retorno sobre el patrimonio", "un", "pat", "roe")):
        i = next(n for n, l in enumerate(lineas) if n > i84 and marca in l)
        por_anio(f"8.4 {letra}", "Rentabilidad", "Tabla de cálculo", ((num, num), (den, den), None, (m, m)), i)
    por_filas("8.4", "Síntesis", "Síntesis comparativa de los indicadores de rentabilidad", ("mb", "mo", "mn", "roa", "roe"))
    i91 = next(n for n, l in enumerate(lineas) if l.startswith("#### **9.1"))
    por_anio("9.1", "Tesorería", "| Año | Tesorería activa", (("Tesorería", "tes"), ("PC", "pc"), None, ("Razón de tesorería", "rte")), i91)
    por_anio("9.2.1", "Fondo CP", "| Año | Activo corriente | Pasivo corriente | Sustitución", (("AC", "ac"), ("PC", "pc"), None, ("Fondo CP", "ctn")), i91)
    por_anio("9.2.2", "Fondo LP", "| Año | Capitales permanentes", (("Capitales permanentes", "cper"), ("ANC", "anc"), None, ("Fondo LP", "fmlp")), i91)
    por_anio("9.3", "EPI", "| Año | Inventarios | Costo de ventas", (("Inventarios", "inv"), ("Costo de ventas", "cv"), None, ("EPI", "ppi")), i91)
    por_anio("9.3", "PPC", "| Año | Cuentas por cobrar comerciales | Ingresos", (("CxC", "cxc"), ("Ingresos", "ing"), None, ("PPC", "ppc")), i91)
    por_anio("9.3", "PPP", "| Año | Cuentas por pagar comerciales", (("CxP", "cxp"), ("Costo de ventas", "cv"), None, ("PPP", "ppp")), i91)
    por_anio("9.3", "CO", "| Año | EPI (días) | PPC (días)", (("EPI", "ppi"), ("PPC", "ppc"), None, ("Ciclo operativo", "co")), i91)
    por_anio("9.3", "CCE", "| Año | CO (días) | PPP (días)", (("CO", "co"), ("PPP", "ppp"), None, ("CCE", "cce")), i91)

    def dupont(sec, tab, marca, metricas):
        filas = tabla(lineas, marca)
        inicio = next(k for k, f in enumerate(filas) if "2021" in f[1])
        for f, m in zip(filas[inicio + 1:], metricas):
            for j, anio in enumerate(ANIOS):
                reg(sec, tab, limpiar_celda(f[0]), anio, f[1 + j], m, europeo=True)

    dupont("9.5", "DuPont RSA", "SISTEMA DUPONT (RSA", ("ing", "un", "ta", "mn", "rat", "road", "roa"))
    dupont("9.6", "DuPont RSP", "SISTEMA DUPONT MODIFICADO", ("road", "ta", "pat", "maf", "roed", "roe"))
    dupont("9.6 C", "DuPont controladora", "ENFOQUE CONTROLADORA", ("ing", "uc", "ta", "patc", "mnc", "rat", "rac", "mafc", "roec", "roec"))
    for anio, texto in ((2024, "187.0"), (2025, "135.2")):
        reg("8.2 C", "Ciclo operativo (texto)", "Ciclo operativo", anio, texto, "co")
    return salida
