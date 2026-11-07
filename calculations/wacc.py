"""Costo promedio ponderado de capital (trabajo ANF, seccion 9.4).

Metodo del trabajo, reproducido sin cambios:
  - Base de ponderacion V = pasivo total + patrimonio total (todas las
    fuentes del Balance, incluidos los pasivos operativos sin costo).
  - Pasivos operativos (proveedores, partes relacionadas, impuestos,
    provisiones...): costo 0 %.
  - Deuda financiera (prestamos, arrendamientos, titulos valores,
    documentos y otros pasivos financieros): tasa supuesta × (1 − t).
  - Patrimonio: Ke = ROE al cierre (utilidad neta / patrimonio total).
  WACC = Σ (importe / V) × costo neto.

Que es dato y que es supuesto:
  - Importes, pesos, clasificacion operativo/financiero y Ke: se obtienen
    de los estados financieros originales (grupos de analisis).
  - Tasas de interes y tasa de ISR: supuestos del trabajo ANF
    (fuentes/anf/supuestos_wacc.json), NO verificables con los documentos
    disponibles. Una fuente de deuda sin tasa deja el WACC como no
    calculable (no se inventa una tasa).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal
from functools import lru_cache
from pathlib import Path

from calculations.rubros import FINANCIERO, OPERATIVO, DatosEjercicio, grupo_de_cuenta

CERO = Decimal("0")
CIEN = Decimal("100")
SUPUESTOS = Path(__file__).resolve().parent.parent / "fuentes" / "anf" / "supuestos_wacc.json"


@lru_cache(maxsize=1)
def cargar_supuestos(ruta: str = str(SUPUESTOS)) -> dict:
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


@dataclass
class LineaWACC:
    tipo: str  # OPERATIVO, FINANCIERO o PATRIMONIO
    codigo: str
    nombre: str
    grupo: str | None
    importe: Decimal
    costo_pct: Decimal | None  # antes de impuestos
    costo_neto_pct: Decimal | None
    proporcion_pct: Decimal
    aporte_pct: Decimal | None
    cita: str = ""


@dataclass
class ResultadoWACC:
    anio: int
    disponible: bool
    motivo: str | None = None
    lineas: list[LineaWACC] = field(default_factory=list)
    tasa_isr_pct: Decimal | None = None
    ke_pct: Decimal | None = None
    total_financiamiento: Decimal = CERO
    pct_pasivos_operativos: Decimal | None = None
    pct_deuda_financiera: Decimal | None = None
    pct_patrimonio: Decimal | None = None
    kd_neto_promedio_pct: Decimal | None = None
    aporte_deuda_pct: Decimal | None = None
    aporte_patrimonio_pct: Decimal | None = None
    wacc_pct: Decimal | None = None
    roa_pct: Decimal | None = None
    spread_pct: Decimal | None = None
    advertencias: list[str] = field(default_factory=list)

    @property
    def diagnostico(self) -> str:
        if self.spread_pct is None:
            return "No disponible"
        return "Rentabilidad suficiente" if self.spread_pct > CERO else "Insuficiente"


def calcular_wacc(d: DatosEjercicio, supuestos: dict | None = None) -> ResultadoWACC:
    supuestos = supuestos if supuestos is not None else cargar_supuestos()
    resultado = ResultadoWACC(anio=d.anio, disponible=False)
    if not (d.bs.tiene_datos and d.inc.tiene_datos):
        resultado.motivo = "Se requieren el Balance General y el Estado de Resultados del ejercicio."
        return resultado
    if d.utilidad_neta is None or d.pasivo_total is None or d.patrimonio_total is None:
        resultado.motivo = "Falta un dato registrado: se requieren el pasivo, el patrimonio y un Estado de Resultados completo."
        return resultado
    datos_anio = supuestos.get("ejercicios", {}).get(str(d.anio))
    if datos_anio is None:
        resultado.motivo = f"No hay supuestos de tasas para {d.anio} en {SUPUESTOS.name}."
        return resultado
    v = d.bs.total_pasivo + d.bs.total_patrimonio
    if v <= CERO or d.bs.total_patrimonio <= CERO:
        resultado.motivo = "El financiamiento total o el patrimonio es cero o negativo."
        return resultado

    t = Decimal(datos_anio["tasa_isr"]) / CIEN
    tasas = datos_anio.get("tasas", {})
    citas = datos_anio.get("citas", {})
    ke = d.inc.utilidad_neta / d.bs.total_patrimonio
    resultado.tasa_isr_pct = t * CIEN
    resultado.ke_pct = ke * CIEN
    resultado.total_financiamiento = v

    operativos = financieros = costo_deuda = CERO
    faltan_tasas = []
    sin_clasificar = []
    for grupo in (d.bs.pasivo_corriente, d.bs.pasivo_no_corriente):
        for linea in grupo.lineas:
            cuenta = linea.cuenta
            info = grupo_de_cuenta(cuenta)
            proporcion = linea.valor / v
            if info is None and linea.valor != CERO:
                # Sin grupo no se sabe si tiene costo: no se le asigna 0 % ni una tasa.
                sin_clasificar.append(f"{cuenta.codigo} — {cuenta.nombre}")
                resultado.lineas.append(LineaWACC("SIN CLASIFICAR", cuenta.codigo, cuenta.nombre, None, linea.valor,
                                                  None, None, proporcion * CIEN, None))
                continue
            if info is not None and info.tipo_pasivo == FINANCIERO:
                tasa = tasas.get(info.codigo)
                if tasa is None:
                    faltan_tasas.append(f"{cuenta.codigo} — {cuenta.nombre}")
                    resultado.lineas.append(LineaWACC(FINANCIERO, cuenta.codigo, cuenta.nombre, info.codigo, linea.valor,
                                                      None, None, proporcion * CIEN, None))
                    financieros += linea.valor
                    continue
                kd = Decimal(tasa) / CIEN
                neto = kd * (1 - t)
                financieros += linea.valor
                costo_deuda += linea.valor * neto
                resultado.lineas.append(LineaWACC(FINANCIERO, cuenta.codigo, cuenta.nombre, info.codigo, linea.valor,
                                                  kd * CIEN, neto * CIEN, proporcion * CIEN, proporcion * neto * CIEN,
                                                  citas.get(info.codigo, "")))
            else:
                operativos += linea.valor
                resultado.lineas.append(LineaWACC(OPERATIVO, cuenta.codigo, cuenta.nombre, cuenta.grupo_analisis, linea.valor,
                                                  CERO, CERO, proporcion * CIEN, CERO))
    for grupo in d.bs.patrimonio_grupos:
        for linea in grupo.lineas:
            proporcion = linea.valor / v
            resultado.lineas.append(LineaWACC("PATRIMONIO", linea.cuenta.codigo, linea.cuenta.nombre, linea.cuenta.grupo_analisis,
                                              linea.valor, ke * CIEN, ke * CIEN, proporcion * CIEN, proporcion * ke * CIEN))

    resultado.pct_pasivos_operativos = operativos / v * CIEN
    resultado.pct_deuda_financiera = financieros / v * CIEN
    resultado.pct_patrimonio = d.bs.total_patrimonio / v * CIEN
    resultado.roa_pct = d.inc.utilidad_neta / v * CIEN
    resultado.aporte_patrimonio_pct = d.bs.total_patrimonio / v * ke * CIEN
    if sin_clasificar:
        resultado.motivo = ("Pasivo sin grupo de análisis: " + "; ".join(sin_clasificar) + ". No se sabe si tiene costo financiero: "
                            "asigne el grupo. El WACC no se calcula.")
        return resultado
    if faltan_tasas:
        resultado.motivo = ("Falta la tasa supuesta de: " + "; ".join(faltan_tasas) +
                            ". No se inventa una tasa: el WACC no se calcula.")
        return resultado
    resultado.kd_neto_promedio_pct = costo_deuda / financieros * CIEN if financieros else None
    resultado.aporte_deuda_pct = costo_deuda / v * CIEN
    resultado.wacc_pct = resultado.aporte_deuda_pct + resultado.aporte_patrimonio_pct
    if resultado.kd_neto_promedio_pct is not None:
        resultado.spread_pct = resultado.roa_pct - resultado.kd_neto_promedio_pct
    resultado.disponible = True
    if d.g("NO_CONTROLADORAS") != CERO:
        resultado.advertencias.append("Ke usa la utilidad neta y el patrimonio totales (incluye participaciones no controladoras).")
    return resultado

