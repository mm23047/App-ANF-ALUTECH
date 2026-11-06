"""Comparacion de los resultados calculados con el trabajo de investigacion ANF.

Tres elementos que nunca se mezclan:
  - Datos originales: importes de los estados financieros (base de datos).
  - Resultados calculados: los que obtiene la aplicacion (calculations/).
  - Resultados de referencia: los publicados en el trabajo ANF
    (fuentes/anf/resultados_referencia.json). Solo se usan aqui, para comparar.

Criterio de clasificacion (para cada valor de referencia):
  - Coincide: el valor calculado, redondeado a la precision con que el
    trabajo presenta el dato (ROUND_HALF_UP), es igual al de referencia.
  - Coincidencia por redondeo: no es igual tras redondear, pero la diferencia
    no supera una unidad del ultimo decimal presentado (p. ej. 0.01 en un
    porcentaje con 2 decimales, 1 USD en un importe entero). Ocurre cuando el
    trabajo suma o multiplica componentes ya redondeados.
  - Diferencia: la diferencia supera esa tolerancia. Requiere revision; la
    causa investigada se documenta en fuentes/anf/observaciones_validacion.json.
  - No verificable: la aplicacion no puede calcular el valor con los datos
    disponibles.
  - Resultado derivado: el trabajo no publica la cifra de forma independiente,
    sino una equivalencia con otro indicador (p. ej. 8.3 C). Coincide por
    construccion, asi que no se cuenta como coincidencia con una cifra publicada.
  - No aplica: el trabajo declara el indicador no calculable y la aplicacion
    llega a la misma conclusion.
No se ajusta ningun dato ni formula para provocar una coincidencia.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from functools import lru_cache
from pathlib import Path

from calculations.comparativo import CONCEPTOS, porcentaje, variacion
from calculations.fuentes_usos import calcular_fuentes_usos
from calculations.indicadores import POR_CLAVE, calcular
from calculations.rubros import DatosEjercicio
from calculations.wacc import calcular_wacc

CERO = Decimal("0")
CIEN = Decimal("100")
DIR_ANF = Path(__file__).resolve().parent.parent / "fuentes" / "anf"
REFERENCIAS = DIR_ANF / "resultados_referencia.json"
OBSERVACIONES = DIR_ANF / "observaciones_validacion.json"

COINCIDE = "Coincide"
REDONDEO = "Coincidencia por redondeo"
DIFERENCIA = "Diferencia"
NO_VERIFICABLE = "No verificable"
NO_APLICA = "No aplica"
DERIVADO = "Resultado derivado"
ESTADOS = (COINCIDE, REDONDEO, DERIVADO, DIFERENCIA, NO_VERIFICABLE, NO_APLICA)


@dataclass(frozen=True)
class Referencia:
    id: str
    seccion: str
    tabla: str
    concepto: str
    metrica: str
    unidad: str
    decimales: int
    valores: dict
    escala: Decimal = Decimal("1")


@dataclass
class Comparacion:
    referencia: Referencia
    anio: int
    valor_app: Decimal | None  # en la escala del trabajo, sin redondear
    valor_anf: Decimal | None  # None si el trabajo dice "No calculable"
    estado: str
    criterio: str
    causa: str = ""
    tipo_causa: str = ""
    categoria: str = ""  # error del trabajo, extraccion, clasificacion, formula, redondeo o supuesto

    @property
    def diferencia(self) -> Decimal | None:
        if self.valor_app is None or self.valor_anf is None:
            return None
        return self.valor_app - self.valor_anf

    @property
    def diferencia_pct(self) -> Decimal | None:
        if self.diferencia is None or self.valor_anf in (None, CERO):
            return None
        return self.diferencia / abs(self.valor_anf) * CIEN


@lru_cache(maxsize=4)
def cargar_referencias(ruta: str = str(REFERENCIAS)) -> tuple[Referencia, ...]:
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)
    referencias = []
    for fila in datos["referencias"]:
        id_, seccion, tabla, concepto, metrica, unidad, decimales, valores, *resto = fila
        escala = Decimal(str(resto[0])) if resto else Decimal("1")
        referencias.append(Referencia(id_, seccion, tabla, concepto, metrica, unidad, decimales, valores, escala))
    return tuple(referencias)


@lru_cache(maxsize=4)
def cargar_observaciones(ruta: str = str(OBSERVACIONES)) -> tuple[dict, ...]:
    if not Path(ruta).exists():
        return ()
    with open(ruta, encoding="utf-8") as f:
        return tuple(json.load(f)["observaciones"])


@lru_cache(maxsize=4)
def referencias_derivadas(ruta: str = str(REFERENCIAS)) -> frozenset[str]:
    """Referencias sin cifra publicada independiente: su valor sale de una equivalencia que enuncia el trabajo."""
    with open(ruta, encoding="utf-8") as f:
        return frozenset(json.load(f).get("referencias_derivadas", []))


def fuera_de_alcance(ruta: str = str(REFERENCIAS)) -> list[str]:
    with open(ruta, encoding="utf-8") as f:
        return json.load(f).get("fuera_de_alcance", [])


class Contexto:
    """Valores calculados por metrica y ejercicio (con cache por ejecucion)."""

    def __init__(self, lista: list[DatosEjercicio]):
        self.por_anio = {d.anio: d for d in lista if d.tiene_datos}
        self._wacc = {}
        self._fyu = {}

    def wacc(self, anio: int):
        if anio not in self._wacc:
            self._wacc[anio] = calcular_wacc(self.por_anio[anio])
        return self._wacc[anio]

    def fuentes_usos(self, anio: int):
        if anio not in self._fyu:
            anterior = self.por_anio.get(anio - 1)
            self._fyu[anio] = calcular_fuentes_usos(anterior, self.por_anio[anio]) if anterior else None
        return self._fyu[anio]

    def valor(self, metrica: str, anio: int) -> Decimal | None:
        d = self.por_anio.get(anio)
        if d is None:
            return None
        tipo, _, resto = metrica.partition(":")
        if tipo == "ind":
            return calcular(d, resto).valor
        if tipo in ("var_abs", "var_pct"):
            if anio - 1 not in self.por_anio:
                return None
            absoluta, relativa, _ = variacion(self.valor(resto, anio), self.valor(resto, anio - 1))
            return absoluta if tipo == "var_abs" else relativa
        if tipo == "var_acum_pct":
            primero = min(self.por_anio)
            _, relativa, _ = variacion(self.valor(resto, anio), self.valor(resto, primero))
            return relativa
        if tipo == "vert_er":
            return porcentaje(self.valor(resto, anio), CONCEPTOS["ingresos"].obtener(d))
        if tipo == "vert_bg":
            return porcentaje(self.valor(resto, anio), CONCEPTOS["total_activo"].obtener(d))
        if tipo == "wacc":
            resultado = self.wacc(anio)
            return getattr(resultado, resto)
        if tipo == "fyu" or tipo == "fyu_neto":
            fyu = self.fuentes_usos(anio)
            if fyu is None:
                return None
            claves = resto.split("+")
            lineas = [l for l in fyu.lineas if l.clave in claves]
            return sum((l.variacion for l in lineas), CERO) if lineas else CERO
        if metrica == "fyu_total":
            fyu = self.fuentes_usos(anio)
            return fyu.total_fuentes if fyu is not None and fyu.cuadra else None
        concepto = CONCEPTOS.get(metrica)
        if concepto is None:
            raise KeyError(f"Métrica desconocida: {metrica}")
        return concepto.obtener(d)


def _redondear(valor: Decimal, decimales: int) -> Decimal:
    return valor.quantize(Decimal(1).scaleb(-decimales), rounding=ROUND_HALF_UP)


def clasificar(valor_app: Decimal | None, valor_anf: Decimal | None, decimales: int) -> tuple[str, str]:
    """(estado, criterio aplicado)."""
    if valor_anf is None:
        if valor_app is None:
            return NO_APLICA, "El trabajo y la aplicación coinciden en que no es calculable con la información disponible."
        return DIFERENCIA, "El trabajo lo declara no calculable, pero la aplicación obtiene un valor."
    if valor_app is None:
        return NO_VERIFICABLE, "La aplicación no puede calcular el valor con los datos disponibles."
    unidad = Decimal(1).scaleb(-decimales)
    if _redondear(valor_app, decimales) == valor_anf:
        return COINCIDE, f"Igual al redondear a {decimales} decimal(es), la precisión presentada en el trabajo."
    if abs(valor_app - valor_anf) <= unidad:
        return REDONDEO, (f"Diferencia ≤ {unidad} (una unidad del último decimal presentado): atribuible a que el "
                          "trabajo opera con cifras intermedias ya redondeadas.")
    return DIFERENCIA, f"Diferencia mayor que {unidad} (tolerancia de una unidad del último decimal presentado)."


CATEGORIAS_CAUSA = ("Error en el trabajo académico", "Error de extracción", "Error de clasificación",
                    "Diferencia de fórmula", "Diferencia de redondeo", "Supuesto no verificable", "Resultado derivado")


def _observacion(ref: Referencia, anio: int, estado: str) -> tuple[str, str, str]:
    """(causa, tipo, categoria). Una coincidencia solo lleva causa si la
    observacion lo indica (p. ej. depende de un supuesto no verificable)."""
    if estado == NO_APLICA:
        return "", "", ""
    for obs in cargar_observaciones():
        if estado == COINCIDE and not obs.get("tambien_coincidencias"):
            continue
        if ref.id in obs["referencias"] and (not obs.get("anios") or anio in obs["anios"]):
            return obs["causa"], obs.get("tipo", ""), obs.get("categoria", "")
    return "", "", ""


def comparar(lista: list[DatosEjercicio]) -> list[Comparacion]:
    contexto = Contexto(lista)
    resultados = []
    for ref in cargar_referencias():
        for anio_texto, texto in ref.valores.items():
            anio = int(anio_texto)
            valor_anf = None if texto == "NC" else Decimal(texto)
            app = contexto.valor(ref.metrica, anio) if anio in contexto.por_anio else None
            valor_app = app / ref.escala if app is not None else None
            estado, criterio = clasificar(valor_app, valor_anf, ref.decimales)
            if estado == COINCIDE and ref.id in referencias_derivadas():
                estado, criterio = DERIVADO, "Sin cifra publicada independiente: el trabajo enuncia una equivalencia con otro indicador."
            causa, tipo, categoria = _observacion(ref, anio, estado)
            resultados.append(Comparacion(ref, anio, valor_app, valor_anf, estado, criterio, causa, tipo, categoria))
    return resultados


def resumen(comparaciones: list[Comparacion]) -> dict[str, int]:
    conteo = {estado: 0 for estado in ESTADOS}
    for c in comparaciones:
        conteo[c.estado] += 1
    return conteo


def metricas_desconocidas() -> list[str]:
    """Metricas de las referencias que la aplicacion no sabe calcular (control)."""
    faltan = []
    for ref in cargar_referencias():
        base = ref.metrica
        for prefijo in ("var_abs:", "var_pct:", "var_acum_pct:", "vert_er:", "vert_bg:"):
            if base.startswith(prefijo):
                base = base[len(prefijo):]
        tipo, _, resto = base.partition(":")
        if tipo == "ind" and resto not in POR_CLAVE:
            faltan.append(ref.metrica)
        elif tipo not in ("ind", "wacc", "fyu", "fyu_neto") and base != "fyu_total" and base not in CONCEPTOS:
            faltan.append(ref.metrica)
    return faltan
