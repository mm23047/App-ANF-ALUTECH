"""Estado de origen y aplicacion de fondos (trabajo ANF, seccion 9.7).

Se construye con las variaciones de los saldos del Balance General entre
dos ejercicios; NO es un estado de flujos de efectivo (no separa partidas
que no implican efectivo ni reclasificaciones):
  Activo:     disminucion = fuente (origen); aumento = uso (aplicacion).
  Pasivo y patrimonio: aumento = fuente; disminucion = uso.
Las sumas de fuentes y usos son iguales cuando ambos balances cuadran.

Nivel de comparacion: grupo de analisis (account.grupo_analisis), para que
una cuenta que cambia de denominacion entre ejercicios se compare consigo
misma. Una cuenta sin grupo se compara por su codigo.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from calculations.rubros import CLASE_BALANCE, GRUPOS, DatosEjercicio, grupo_de_cuenta

CERO = Decimal("0")


@dataclass
class LineaFuentesUsos:
    clave: str
    concepto: str
    clase: str  # AC, ANC, PC, PNC, PAT
    anterior: Decimal
    actual: Decimal
    cuentas: list[str] = field(default_factory=list)

    @property
    def variacion(self) -> Decimal:
        return self.actual - self.anterior

    @property
    def es_activo(self) -> bool:
        return self.clase in ("AC", "ANC")

    @property
    def fuente(self) -> Decimal:
        v = self.variacion
        return -v if (self.es_activo and v < 0) else (v if (not self.es_activo and v > 0) else CERO)

    @property
    def uso(self) -> Decimal:
        v = self.variacion
        return v if (self.es_activo and v > 0) else (-v if (not self.es_activo and v < 0) else CERO)

    @property
    def grupo_estado(self) -> str:
        return "Activo" if self.es_activo else ("Pasivo" if self.clase in ("PC", "PNC") else "Patrimonio")


@dataclass
class ResultadoFuentesUsos:
    anio_anterior: int
    anio_actual: int
    lineas: list[LineaFuentesUsos]
    total_fuentes: Decimal
    total_usos: Decimal
    advertencias: list[str] = field(default_factory=list)

    @property
    def cuadra(self) -> bool:
        return self.total_fuentes == self.total_usos


_CLASE_DE = {("ACTIVO", "CORRIENTE"): "AC", ("ACTIVO", "NO_CORRIENTE"): "ANC", ("PASIVO", "CORRIENTE"): "PC",
             ("PASIVO", "NO_CORRIENTE"): "PNC"}


def _clase_cuenta(cuenta) -> str:
    sub = cuenta.subcategoria.value if cuenta.subcategoria is not None else ""
    return _CLASE_DE.get((cuenta.categoria_principal.value, sub), "PAT")


def _saldos(d: DatosEjercicio) -> dict[str, tuple[str, str, Decimal, list[str]]]:
    """clave -> (concepto, clase, saldo, cuentas) del Balance del ejercicio."""
    saldos: dict[str, tuple[str, str, Decimal, list[str]]] = {}
    grupos = [d.bs.activo_corriente, d.bs.activo_no_corriente, d.bs.pasivo_corriente, d.bs.pasivo_no_corriente,
              *d.bs.patrimonio_grupos]
    for grupo in grupos:
        for linea in grupo.lineas:
            cuenta = linea.cuenta
            info = grupo_de_cuenta(cuenta)
            if info is not None:
                clave, concepto, clase = info.codigo, info.nombre, info.clase
            else:
                clave, concepto, clase = f"cuenta:{cuenta.codigo}", f"{cuenta.codigo} — {cuenta.nombre}", _clase_cuenta(cuenta)
            previo = saldos.get(clave)
            cuentas = (previo[3] if previo else []) + [f"{cuenta.codigo} {cuenta.nombre}"]
            saldos[clave] = (concepto, clase, (previo[2] if previo else CERO) + linea.valor, cuentas)
    return saldos


def calcular_fuentes_usos(anterior: DatosEjercicio, actual: DatosEjercicio) -> ResultadoFuentesUsos:
    s_ant, s_act = _saldos(anterior), _saldos(actual)
    orden = {g: i for i, g in enumerate(GRUPOS)}
    claves = sorted(set(s_ant) | set(s_act),
                    key=lambda c: (CLASE_BALANCE.index((s_act.get(c) or s_ant.get(c))[1]), orden.get(c, 999), c))
    lineas = []
    for clave in claves:
        concepto, clase, _, cuentas_act = s_act.get(clave) or (*s_ant[clave][:2], CERO, [])
        cuentas_ant = s_ant[clave][3] if clave in s_ant else []
        lineas.append(LineaFuentesUsos(
            clave, concepto, clase,
            s_ant[clave][2] if clave in s_ant else CERO,
            s_act[clave][2] if clave in s_act else CERO,
            sorted(set(cuentas_ant) | set(cuentas_act)),
        ))
    total_fuentes = sum((l.fuente for l in lineas), CERO)
    total_usos = sum((l.uso for l in lineas), CERO)
    advertencias = []
    for d in (anterior, actual):
        if not d.bs.cuadra:
            advertencias.append(f"El Balance de {d.anio} no cuadra: las sumas de fuentes y usos pueden diferir.")
    if total_fuentes != total_usos and not advertencias:
        advertencias.append("Las sumas de fuentes y usos difieren aunque ambos balances cuadran: revise la clasificación.")
    return ResultadoFuentesUsos(anterior.anio, actual.anio, lineas, total_fuentes, total_usos, advertencias)

