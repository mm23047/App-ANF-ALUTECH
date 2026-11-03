"""Controles de los datos originales cargados (trazabilidad).

1. Totales declarados: cada total o subtotal impreso en el documento
   (dato_complementario tipo TOTAL_DECLARADO) se compara con el que la
   aplicacion calcula a partir de las cuentas. Una diferencia indica un
   error de transcripcion o de clasificacion.
2. Vigencia de las fuentes: el importe vigente de cada cuenta se compara con
   el valor registrado al cargarlo desde el documento. Si alguien lo edito o
   lo borro despues, el control lo senala (nunca lo corrige).
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy.orm import Session

from calculations.rubros import DatosEjercicio
from database.models import FiscalPeriod
from database.repositories import get_entries_map, list_datos_complementarios, list_fuentes

CERO = Decimal("0")

TOTALES = {
    "total_activo_corriente": ("Total activo corriente", lambda d: d.bs.activo_corriente.subtotal),
    "total_activo_no_corriente": ("Total activo no corriente", lambda d: d.bs.activo_no_corriente.subtotal),
    "total_activo": ("Total activo", lambda d: d.bs.total_activo),
    "total_pasivo_corriente": ("Total pasivo corriente", lambda d: d.bs.pasivo_corriente.subtotal),
    "total_pasivo_no_corriente": ("Total pasivo no corriente", lambda d: d.bs.pasivo_no_corriente.subtotal),
    "total_pasivo": ("Total pasivo", lambda d: d.bs.total_pasivo),
    "patrimonio_controladora": ("Patrimonio atribuible a la controladora", lambda d: d.patrimonio_controladora),
    "total_patrimonio": ("Total patrimonio", lambda d: d.bs.total_patrimonio),
    "total_pasivo_patrimonio": ("Total pasivo y patrimonio", lambda d: d.bs.total_pasivo_patrimonio),
    "utilidad_bruta": ("Utilidad bruta", lambda d: d.inc.utilidad_bruta),
    "utilidad_operativa": ("Utilidad de operación", lambda d: d.inc.utilidad_operativa),
    "utilidad_antes_impuestos": ("Utilidad antes de impuestos", lambda d: d.inc.utilidad_antes_impuestos),
    "utilidad_neta": ("Utilidad neta", lambda d: d.inc.utilidad_neta),
}

OK, DIFERENCIA, MODIFICADO, ELIMINADO = "OK", "DIFERENCIA", "MODIFICADO", "ELIMINADO"


@dataclass
class ControlTotal:
    anio: int
    clave: str
    concepto: str
    nombre_original: str
    declarado: Decimal
    calculado: Decimal | None
    documento: str
    pagina: int | None

    @property
    def diferencia(self) -> Decimal | None:
        return None if self.calculado is None else self.calculado - self.declarado

    @property
    def estado(self) -> str:
        return OK if self.diferencia == CERO else DIFERENCIA


@dataclass
class ControlFuente:
    anio: int
    tipo: str
    codigo: str
    cuenta: str
    nombre_original: str
    importe_documento: str
    valor_registrado: Decimal
    valor_vigente: Decimal | None
    documento: str
    pagina: int | None
    estado_financiero: str

    @property
    def estado(self) -> str:
        if self.valor_vigente is None:
            return ELIMINADO
        return OK if self.valor_vigente == self.valor_registrado else MODIFICADO


def controles_totales(d: DatosEjercicio, session: Session) -> list[ControlTotal]:
    controles = []
    for dato in list_datos_complementarios(session, d.periodo.id):
        if dato.tipo != "TOTAL_DECLARADO":
            continue
        concepto, obtener = TOTALES.get(dato.clave, (dato.clave, lambda _d: None))
        controles.append(ControlTotal(d.anio, dato.clave, concepto, dato.nombre_original, dato.valor, obtener(d),
                                      dato.documento, dato.pagina))
    return controles


def controles_fuentes(session: Session, periodo: FiscalPeriod) -> list[ControlFuente]:
    vigentes = {tipo: get_entries_map(session, periodo.id, tipo) for tipo in {f.tipo for f in list_fuentes(session, periodo.id)}}
    return [
        ControlFuente(periodo.anio, f.tipo.value, f.account.codigo, f.account.nombre, f.nombre_original, f.importe_documento,
                      f.valor_registrado, vigentes[f.tipo].get(f.account_id), f.documento, f.pagina, f.estado_financiero)
        for f in list_fuentes(session, periodo.id)
    ]
