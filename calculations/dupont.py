"""Modelo DuPont con saldos al cierre (trabajo ANF, secciones 8.4, 9.5 y 9.6).

Unica fuente de calculo del modelo. La usan el reporte DuPont (pantalla, PDF y
Excel), el Dashboard, el Informe integral y los indicadores que alimentan la
comparacion con el trabajo:

  Margen neto          = Ganancia neta / Ventas
  Rotacion de activos  = Ventas / Activos totales al cierre
  RSA (ROA)            = Margen neto x Rotacion de activos
  MAF                  = Activos totales al cierre / Patrimonio total al cierre
  RSP (ROE)            = RSA x MAF
  Comprobacion directa = Ganancia neta / Patrimonio total al cierre

No se usan saldos promedio ni el balance del ejercicio anterior: todos los
ejercicios, incluido el primero, se calculan solo con sus propios saldos.

Hay dos enfoques que nunca se mezclan. El total usa la ganancia neta del año y
el patrimonio total. El de la controladora usa la ganancia y el patrimonio
atribuibles a sus propietarios. Ambos usan los activos totales de la empresa.

Si el patrimonio al cierre es negativo, el ROE no es interpretable: los factores
quedan solo como referencia y no se genera interpretacion. Si es cero, no se
puede calcular.

Todos los calculos usan Decimal sin redondeo intermedio; los porcentajes *_pct
se cuantizan a 2 decimales solo como valor final de presentacion.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from sqlalchemy.orm import Session

from calculations.controls import CONCILIADO, SIN_DATOS, conciliar_resultado
from calculations.rubros import DatosEjercicio, datos_ejercicio
from components.money import format_money, format_percent, format_ratio, q2
from database.models import FiscalPeriod

CERO = Decimal("0.00")
CIEN = Decimal("100")
TOLERANCIA_PCT = Decimal("0.01")
NO_INTERPRETABLE = "NO INTERPRETABLE"
BASE_SALDOS = ("Saldos al cierre del ejercicio, como en las secciones 8.4, 9.5 y 9.6 del trabajo; no se usan saldos "
               "promedio ni el balance del ejercicio anterior.")
# Tipos de valor de las filas de presentacion
IMPORTE, PORCENTAJE, VECES = "importe", "porcentaje", "veces"


@dataclass(frozen=True)
class FactoresDuPont:
    """Factores sin redondear, en fraccion (no x100). None: no calculable."""
    margen_neto: Decimal | None
    rotacion_activos: Decimal | None
    rsa: Decimal | None
    maf: Decimal | None
    rsp: Decimal | None
    rsa_directo: Decimal | None
    roe_directo: Decimal | None
    patrimonio_positivo: bool

    @property
    def maf_interpretable(self) -> Decimal | None:
        return self.maf if self.patrimonio_positivo else None

    @property
    def rsp_interpretable(self) -> Decimal | None:
        return self.rsp if self.patrimonio_positivo else None


def factores_dupont(
    utilidad: Decimal | None, ingresos: Decimal | None, activo: Decimal | None, patrimonio: Decimal | None
) -> FactoresDuPont:
    """Unica definicion de las formulas. Un dato None o un denominador invalido
    deja en None solo los factores que dependen de el."""
    margen = utilidad / ingresos if utilidad is not None and ingresos is not None and ingresos != CERO else None
    activo_valido = activo is not None and activo > CERO
    rotacion = ingresos / activo if ingresos is not None and activo_valido else None
    rsa = margen * rotacion if margen is not None and rotacion is not None else None
    con_patrimonio = activo is not None and patrimonio is not None and patrimonio != CERO
    maf = activo / patrimonio if con_patrimonio else None
    return FactoresDuPont(
        margen_neto=margen,
        rotacion_activos=rotacion,
        rsa=rsa,
        maf=maf,
        rsp=rsa * maf if rsa is not None and maf is not None else None,
        rsa_directo=utilidad / activo if utilidad is not None and activo_valido else None,
        roe_directo=utilidad / patrimonio if utilidad is not None and con_patrimonio else None,
        patrimonio_positivo=patrimonio is not None and patrimonio > CERO,
    )


def factores_total(d: DatosEjercicio) -> FactoresDuPont:
    """Enfoque total: ganancia neta del año y patrimonio total."""
    return factores_dupont(
        d.inc.utilidad_neta if d.inc.tiene_datos else None,
        d.inc.ingresos_netos.subtotal if d.inc.tiene_datos else None,
        d.bs.total_activo if d.bs.tiene_datos else None,
        d.bs.total_patrimonio if d.bs.tiene_datos else None,
    )


def factores_controladora(d: DatosEjercicio) -> tuple[FactoresDuPont, str]:
    """Enfoque de la controladora: (factores, fuente de la utilidad atribuible)."""
    utilidad, fuente = d.utilidad_controladora()
    factores = factores_dupont(
        utilidad,
        d.inc.ingresos_netos.subtotal if d.inc.tiene_datos else None,
        d.bs.total_activo if d.bs.tiene_datos else None,
        d.patrimonio_controladora if d.bs.tiene_datos else None,
    )
    return factores, fuente


@dataclass
class Control:
    nombre: str
    correcto: bool
    detalle: str
    sin_datos: bool = False  # no se pudo comprobar: no es una diferencia

    @property
    def resultado(self) -> str:
        if self.sin_datos:
            return "Sin datos para conciliar"
        return "Correcto" if self.correcto else "Revisar"


@dataclass
class EnfoqueControladora:
    utilidad: Decimal | None
    patrimonio: Decimal | None
    factores: FactoresDuPont
    fuente: str

    @property
    def disponible(self) -> bool:
        return self.factores.rsp_interpretable is not None


@dataclass
class DuPontResult:
    disponible: bool
    motivo_no_disponible: str | None
    utilidad_neta: Decimal | None
    ingresos_netos: Decimal | None
    activo_total: Decimal | None
    patrimonio_total: Decimal | None
    margen_neto: Decimal | None  # fraccion (no x100), sin redondear
    rotacion_activos: Decimal | None  # veces, sin redondear
    rsa: Decimal | None  # fraccion, sin redondear
    multiplicador_capital: Decimal | None  # MAF, veces, sin redondear
    rsa_directo: Decimal | None  # comprobacion: ganancia neta / activos, fraccion
    roe_dupont_pct: Decimal | None  # presentacion: 2 decimales
    roe_directo_pct: Decimal | None  # presentacion: 2 decimales
    coincide_redondeo: bool | None  # identidad algebraica; no es un control (B-02)
    interpretable: bool = True
    roe: Decimal | None = None  # RSP en fraccion, sin redondear
    roe_directo: Decimal | None = None  # comprobacion en fraccion, sin redondear
    controladora: EnfoqueControladora | None = None
    advertencias: list[str] = field(default_factory=list)
    controles: list[Control] = field(default_factory=list)


def compute_dupont(session: Session, fiscal_period: FiscalPeriod) -> DuPontResult:
    d = datos_ejercicio(session, fiscal_period)
    bs, inc = d.bs, d.inc

    def vacio(motivo: str, **datos) -> DuPontResult:
        base = dict(
            utilidad_neta=None, ingresos_netos=None, activo_total=None, patrimonio_total=None, margen_neto=None,
            rotacion_activos=None, rsa=None, multiplicador_capital=None, rsa_directo=None, roe_dupont_pct=None,
            roe_directo_pct=None, coincide_redondeo=None,
        )
        base.update(datos)
        return DuPontResult(disponible=False, motivo_no_disponible=motivo, **base)

    if not bs.tiene_datos:
        return vacio("No hay datos de Balance General capturados para este ejercicio.")
    if not inc.tiene_datos:
        return vacio("No hay datos de Estado de Resultados capturados para este ejercicio.")

    utilidad_neta = inc.utilidad_neta
    ingresos_netos = inc.ingresos_netos.subtotal
    conciliacion = conciliar_resultado(bs, inc)

    advertencias = []
    if not bs.completo:
        advertencias.append(f"Balance General INCOMPLETO (sin datos de {', '.join(bs.categorias_faltantes)}).")
    if not inc.completo:
        advertencias.append(f"Estado de Resultados INCOMPLETO (sin datos de {', '.join(inc.categorias_faltantes)}).")
    if not bs.cuadra:
        advertencias.append(f"El Balance General no cuadra (diferencia {format_money(bs.diferencia)}).")
    if bs.advertencias_signo or inc.advertencias_signo:
        advertencias.append("Hay importes con signo distinto a la convención; revíselos en los reportes del Balance y de Resultados.")

    controles = [
        Control("Balance del ejercicio cuadra", bs.cuadra, f"Diferencia: {format_money(bs.diferencia)}"),
        Control("Balance del ejercicio completo", bs.completo,
                "Completo" if bs.completo else f"Sin datos de {', '.join(bs.categorias_faltantes)}"),
        Control("Estado de Resultados completo", inc.completo,
                "Completo" if inc.completo else f"Sin datos de {', '.join(inc.categorias_faltantes)}"),
        Control("Resultado del ejercicio conciliado con la utilidad neta", conciliacion.estado == CONCILIADO,
                conciliacion.mensaje, sin_datos=conciliacion.estado == SIN_DATOS),
        Control("Signos según la convención", not (bs.advertencias_signo or inc.advertencias_signo),
                f"{len(bs.advertencias_signo) + len(inc.advertencias_signo)} importe(s) con signo atípico"),
    ]
    comunes = dict(
        utilidad_neta=utilidad_neta, ingresos_netos=ingresos_netos, activo_total=bs.total_activo,
        patrimonio_total=bs.total_patrimonio, advertencias=advertencias, controles=controles,
    )

    if ingresos_netos == CERO:
        return vacio("Los ingresos netos son cero; no se puede calcular el margen neto ni la rotacion de activos.", **comunes)
    if bs.total_activo <= CERO:
        return vacio("El activo total al cierre es cero o negativo; no se puede calcular la rotacion de activos.", **comunes)
    if bs.total_patrimonio == CERO:
        return vacio("El patrimonio total al cierre es cero; no se puede calcular el multiplicador del capital ni el ROE.", **comunes)

    total = factores_total(d)
    f_controladora, fuente_controladora = factores_controladora(d)
    utilidad_controladora = d.utilidad_controladora()[0]
    factores = dict(
        margen_neto=total.margen_neto, rotacion_activos=total.rotacion_activos, rsa=total.rsa,
        multiplicador_capital=total.maf, rsa_directo=total.rsa_directo,
        roe_dupont_pct=q2(total.rsp * CIEN), roe_directo_pct=q2(total.roe_directo * CIEN),
        coincide_redondeo=abs(q2(total.rsp * CIEN) - q2(total.roe_directo * CIEN)) <= TOLERANCIA_PCT,
        roe=total.rsp, roe_directo=total.roe_directo,
        controladora=EnfoqueControladora(utilidad_controladora, d.patrimonio_controladora, f_controladora, fuente_controladora),
    )

    positivo = total.patrimonio_positivo
    controles.append(Control("Patrimonio total al cierre positivo", positivo,
                             "Positivo" if positivo else f"No positivo: {format_money(bs.total_patrimonio)}"))
    if not positivo:
        motivo = (
            f"ROE {NO_INTERPRETABLE}: el patrimonio total al cierre ({format_money(bs.total_patrimonio)}) es cero o "
            "negativo. Con patrimonio negativo el cociente puede dar un ROE positivo aunque haya pérdidas, y el "
            "multiplicador pierde su significado. Los factores se muestran solo como referencia."
        )
        resultado = vacio(motivo, **comunes, **factores)
        resultado.interpretable = False
        return resultado

    return DuPontResult(disponible=True, motivo_no_disponible=None, **comunes, **factores)


# ------------------------------------------------------------- presentacion
@dataclass(frozen=True)
class FilaDuPont:
    """Fila comun de pantalla, PDF y Excel. `valor` None: no disponible; texto:
    se muestra tal cual (NO INTERPRETABLE)."""
    etiqueta: str
    valor: Decimal | str | None
    tipo: str
    decimales: int = 4


def formatear_fila(fila: FilaDuPont, moneda: str = "") -> str:
    """Texto de la fila en pantalla y PDF."""
    if isinstance(fila.valor, str):
        return fila.valor
    if fila.tipo == IMPORTE:
        return format_money(fila.valor, moneda)
    if fila.tipo == PORCENTAJE:
        return format_percent(fila.valor, fila.decimales)
    return format_ratio(fila.valor, fila.decimales)


def _pct(fraccion: Decimal | None) -> Decimal | None:
    return fraccion * CIEN if fraccion is not None else None


def filas_enfoque_total(r: DuPontResult) -> list[FilaDuPont]:
    def roe(valor: Decimal | None) -> Decimal | str | None:
        return valor if r.interpretable else NO_INTERPRETABLE

    return [
        FilaDuPont("Ganancia neta del año", r.utilidad_neta, IMPORTE),
        FilaDuPont("Ventas (ingresos ordinarios)", r.ingresos_netos, IMPORTE),
        FilaDuPont("Activos totales al cierre", r.activo_total, IMPORTE),
        FilaDuPont("Patrimonio total al cierre", r.patrimonio_total, IMPORTE),
        FilaDuPont("Margen neto", _pct(r.margen_neto), PORCENTAJE),
        FilaDuPont("Rotación de activos", r.rotacion_activos, VECES),
        FilaDuPont("RSA / ROA", _pct(r.rsa), PORCENTAJE),
        FilaDuPont("Multiplicador del capital (MAF)", r.multiplicador_capital, VECES),
        FilaDuPont("RSP / ROE DuPont", roe(r.roe_dupont_pct), PORCENTAJE, 2),
        FilaDuPont("ROA directo (comprobación)", _pct(r.rsa_directo), PORCENTAJE),
        FilaDuPont("ROE directo (comprobación)", roe(r.roe_directo_pct), PORCENTAJE, 2),
    ]


def filas_enfoque_controladora(r: DuPontResult) -> list[FilaDuPont]:
    c = r.controladora
    if c is None:
        return []
    f = c.factores
    rsp = _pct(f.rsp_interpretable) if f.patrimonio_positivo else NO_INTERPRETABLE
    directo = _pct(f.roe_directo) if f.patrimonio_positivo else NO_INTERPRETABLE
    return [
        FilaDuPont("Ganancia atribuible a la controladora", c.utilidad, IMPORTE),
        FilaDuPont("Patrimonio atribuible a la controladora", c.patrimonio, IMPORTE),
        FilaDuPont("Margen neto (controladora)", _pct(f.margen_neto), PORCENTAJE),
        FilaDuPont("Rotación de activos", f.rotacion_activos, VECES),
        FilaDuPont("RSA (controladora)", _pct(f.rsa), PORCENTAJE),
        FilaDuPont("MAF (controladora)", f.maf, VECES),
        FilaDuPont("RSP / ROE (controladora)", rsp, PORCENTAJE, 2),
        FilaDuPont("ROE directo de la controladora (comprobación)", directo, PORCENTAJE, 2),
    ]


def generar_interpretacion(resultado: DuPontResult) -> str:
    """Interpretacion basada exclusivamente en los valores calculados. No se
    interpretan los factores si el ROE no es interpretable."""
    if not resultado.disponible:
        return f"No es posible generar una interpretacion: {resultado.motivo_no_disponible}"

    margen_pct = resultado.margen_neto * CIEN
    partes = [
        f"El margen neto fue de {margen_pct:.4f}%: de cada 100 unidades monetarias de ventas, "
        f"{margen_pct:.2f} se convirtieron en ganancia neta.",
        f"La rotacion de activos fue de {resultado.rotacion_activos:.4f} veces: los activos totales al cierre "
        f"generaron {resultado.rotacion_activos:.2f} veces su valor en ventas durante el ejercicio.",
        f"El margen neto por la rotacion da un RSA de {resultado.rsa * CIEN:.2f}%.",
        f"El multiplicador del capital (MAF) fue de {resultado.multiplicador_capital:.4f} veces: los activos totales "
        f"equivalen a {resultado.multiplicador_capital:.2f} veces el patrimonio total al cierre (a mayor "
        "multiplicador, mayor proporcion de los activos financiada con pasivos en lugar de patrimonio).",
        f"El RSA por el MAF da un RSP / ROE de {resultado.roe_dupont_pct:.2f}%, igual a la ganancia neta del año "
        "entre el patrimonio total al cierre.",
    ]
    if any("INCOMPLETO" in a for a in resultado.advertencias):
        partes.append("Advertencia: al menos un estado financiero del ejercicio está incompleto.")
    return " ".join(partes)


def interpretacion_controladora(resultado: DuPontResult) -> str | None:
    """Lectura del enfoque de la controladora, separada de la del enfoque total."""
    c = resultado.controladora
    if not resultado.disponible or c is None or not c.disponible:
        return None
    return (
        f"Con la ganancia y el patrimonio atribuibles a los propietarios de la controladora, el RSA fue de "
        f"{c.factores.rsa * CIEN:.2f}% y el RSP / ROE de {c.factores.rsp * CIEN:.2f}%. Estas cifras no se suman ni "
        "se comparan como si fueran del enfoque total: usan bases diferentes."
    )
