"""Carga reproducible de los estados financieros originales de Alutech 2021-2025.

Lee fuentes/alutech/estados_financieros_2021_2025.json (datos transcritos de
la carpeta documentos/, con documento, pagina y denominacion original de cada
importe) y los incorpora a la base de datos de la aplicacion:

  1. Lleva la BD a la version de esquema vigente (migracion con copia previa).
  2. Crea una copia de seguridad verificada en data/backups/ antes de escribir.
  3. En UNA transaccion: crea las cuentas que falten (con su grupo de
     analisis), los ejercicios que falten, los importes, la fuente de cada
     importe y los totales impresos.
  4. Antes de confirmar, compara cada total impreso con el calculado por la
     aplicacion. Si algo no coincide, o si un importe ya existe con otro valor,
     revierte todo: la BD queda exactamente como estaba.

Es idempotente: ejecutarlo de nuevo no duplica nada ni modifica lo ya cargado.
Nunca sobrescribe ni borra datos existentes (los 19 importes en cero del
catalogo estandar de 2021 se conservan intactos).

Convencion de signos al registrar (calculations/validation.py):
  Balance: la cifra impresa con su signo (parentesis = negativo).
  Resultados: en positivo; la cifra impresa debe tener el signo que
  corresponde a la cuenta (ingresos positivos, costos y gastos entre
  parentesis). Un signo incoherente detiene la carga: no se invierte nada.

Uso (con la aplicacion cerrada):
    python scripts/cargar_alutech.py              # carga en data/financiera.db
    python scripts/cargar_alutech.py --simular    # ensaya sobre una copia temporal (no modifica la BD)
    python scripts/cargar_alutech.py --bd RUTA.db
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

PROYECTO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROYECTO))

from calculations.controles_carga import controles_totales  # noqa: E402
from calculations.rubros import GRUPOS, datos_ejercicio, signo_resultado  # noqa: E402
from database import connection  # noqa: E402
from database.backup_utils import crear_respaldo, marca_tiempo  # noqa: E402
from database.enums import CategoriaPrincipal, EfectoCuenta, NaturalezaSaldo, Subcategoria, TipoEstadoFinanciero  # noqa: E402
from database.repositories import (  # noqa: E402
    create_account,
    get_account_by_codigo,
    get_entries_map,
    get_fiscal_period,
    get_or_create_fiscal_period,
    lote,
    registrar_dato_complementario,
    registrar_fuente,
    update_account,
    upsert_entry,
)

ARCHIVO_DATOS = PROYECTO / "fuentes" / "alutech" / "estados_financieros_2021_2025.json"
ESTADO = {
    "BALANCE": "Estado de situación financiera",
    "RESULTADOS": "Estado de resultados",
}


class CargaError(RuntimeError):
    """La carga no se aplico; la BD queda como estaba."""


@dataclass
class InformeCarga:
    respaldo: Path | None = None
    cuentas_creadas: int = 0
    cuentas_existentes: int = 0
    ejercicios_creados: list[int] = field(default_factory=list)
    importes_creados: int = 0
    importes_existentes: int = 0
    fuentes_creadas: int = 0
    datos_creados: int = 0
    controles: list = field(default_factory=list)
    simulado: bool = False

    @property
    def controles_ok(self) -> bool:
        return all(c.estado == "OK" for c in self.controles)


def importe_impreso(texto: str) -> Decimal:
    """Cifra tal como aparece impresa: "(1,234)" o "-1,234" -> -1234; "-" -> 0."""
    limpio = texto.replace(",", "").replace("$", "").strip()
    if limpio in ("-", "—", ""):
        return Decimal("0")
    if limpio.startswith("(") and limpio.endswith(")"):
        return -Decimal(limpio[1:-1])
    return Decimal(limpio)


def valor_a_registrar(cuenta, impreso: str, tipo: str) -> Decimal:
    valor = importe_impreso(impreso)
    if tipo == "BALANCE" or valor == 0:
        return valor
    esperado = signo_resultado(cuenta)
    if (valor > 0) != (esperado > 0):
        raise CargaError(
            f"{cuenta.codigo} — {cuenta.nombre}: la cifra impresa {impreso} tiene un signo incoherente con la cuenta "
            f"({'aumenta' if esperado > 0 else 'disminuye'} la utilidad). No se invierte el signo: revise la transcripción."
        )
    return abs(valor)


def _cuentas(session, datos: dict, informe: InformeCarga) -> dict:
    cuentas = {}
    for c in datos["cuentas"]:
        if c["grupo"] not in GRUPOS:
            raise CargaError(f"Cuenta {c['codigo']}: grupo de análisis desconocido {c['grupo']!r}.")
        clasificacion = dict(
            categoria_principal=CategoriaPrincipal(c["categoria"]),
            subcategoria=Subcategoria(c["subcategoria"]) if c.get("subcategoria") else None,
            efecto=EfectoCuenta(c["efecto"]) if c.get("efecto") else None,
            naturaleza_saldo=NaturalezaSaldo(c["naturaleza"]),
        )
        existente = get_account_by_codigo(session, c["codigo"])
        if existente is None:
            cuentas[c["codigo"]] = create_account(session, codigo=c["codigo"], nombre=c["nombre"],
                                                  orden_presentacion=c["orden"], grupo_analisis=c["grupo"], **clasificacion)
            informe.cuentas_creadas += 1
            continue
        distintos = [k for k, v in clasificacion.items() if getattr(existente, k) != v]
        if distintos:
            raise CargaError(f"La cuenta {c['codigo']} ya existe con otra clasificación ({', '.join(distintos)}); no se modifica.")
        if existente.grupo_analisis is None:
            update_account(session, existente.id, grupo_analisis=c["grupo"])
        informe.cuentas_existentes += 1
        cuentas[c["codigo"]] = existente
    return cuentas


def cargar(ruta_datos: Path = ARCHIVO_DATOS, db_path: Path | None = None, *, simular: bool = False,
           respaldar: bool = True) -> InformeCarga:
    datos = json.loads(Path(ruta_datos).read_text(encoding="utf-8"))
    db_path = Path(db_path) if db_path else connection.DB_PATH
    if simular:
        # La simulacion trabaja sobre una copia temporal: la BD indicada no se
        # migra ni se modifica de ninguna forma.
        temporal = Path(tempfile.mkdtemp(prefix="simulacion_alutech_"))
        try:
            copia = temporal / "financiera.db"
            if db_path.exists():
                crear_respaldo(db_path, copia)
            informe = cargar(ruta_datos, copia, respaldar=False)
            informe.simulado = True
            return informe
        finally:
            connection.dispose_engine()
            shutil.rmtree(temporal, ignore_errors=True)

    informe = InformeCarga()
    if respaldar and db_path.exists():
        informe.respaldo = crear_respaldo(db_path, db_path.parent / "backups" / f"{db_path.stem}_pre_carga_alutech_{marca_tiempo()}.db")
    connection.init_db(db_path)

    session = connection.get_session()
    try:
        with lote(session):
            cuentas = _cuentas(session, datos, informe)
            conflictos = []
            for anio_texto, ejercicio in datos["ejercicios"].items():
                documento = datos["documentos"][ejercicio["documento"]]
                archivo = documento["archivo"]
                periodo, creado = get_or_create_fiscal_period(session, int(anio_texto))
                if creado:
                    informe.ejercicios_creados.append(periodo.anio)
                if periodo.cerrado:
                    raise CargaError(f"El ejercicio {periodo.anio} está cerrado: no se carga nada.")
                for tipo_texto in ("BALANCE", "RESULTADOS"):
                    tipo = TipoEstadoFinanciero(tipo_texto)
                    vigentes = get_entries_map(session, periodo.id, tipo)
                    for codigo, nombre_original, impreso, pagina in ejercicio[tipo_texto]:
                        cuenta = cuentas[codigo]
                        valor = valor_a_registrar(cuenta, impreso, tipo_texto)
                        actual = vigentes.get(cuenta.id)
                        if actual is None:
                            upsert_entry(session, fiscal_period_id=periodo.id, account_id=cuenta.id, valor=valor, tipo=tipo)
                            informe.importes_creados += 1
                        elif actual != valor:
                            conflictos.append(f"{periodo.anio} {codigo}: vigente {actual}, documento {valor}")
                            continue
                        else:
                            informe.importes_existentes += 1
                        if registrar_fuente(session, fiscal_period_id=periodo.id, account_id=cuenta.id, tipo=tipo,
                                            documento=archivo, pagina=pagina, estado_financiero=ESTADO[tipo_texto],
                                            nombre_original=nombre_original, importe_documento=impreso, valor_registrado=valor):
                            informe.fuentes_creadas += 1
                for clave, nombre_original, impreso, pagina in ejercicio["totales_declarados"]:
                    estado = ESTADO["RESULTADOS" if clave.startswith("utilidad") else "BALANCE"]
                    if registrar_dato_complementario(session, fiscal_period_id=periodo.id, clave=clave, tipo="TOTAL_DECLARADO",
                                                     valor=importe_impreso(impreso), documento=archivo, pagina=pagina,
                                                     estado_financiero=estado, nombre_original=nombre_original,
                                                     importe_documento=impreso):
                        informe.datos_creados += 1
                for clave, nombre_original, impreso, pagina, estado in ejercicio["datos_complementarios"]:
                    if registrar_dato_complementario(session, fiscal_period_id=periodo.id, clave=clave, tipo="COMPLEMENTARIO",
                                                     valor=importe_impreso(impreso), documento=archivo, pagina=pagina,
                                                     estado_financiero=estado, nombre_original=nombre_original,
                                                     importe_documento=impreso):
                        informe.datos_creados += 1
            if conflictos:
                raise CargaError("Importes existentes con otro valor (no se sobrescriben): " + "; ".join(conflictos))
            session.flush()
            for anio_texto in datos["ejercicios"]:
                d = datos_ejercicio(session, get_fiscal_period(session, int(anio_texto)))
                informe.controles.extend(controles_totales(d, session))
            if not informe.controles_ok:
                malos = [f"{c.anio} {c.concepto}: impreso {c.declarado}, calculado {c.calculado}" for c in informe.controles
                         if c.estado != "OK"]
                raise CargaError("Los totales calculados no coinciden con los impresos: " + "; ".join(malos))
        session.commit()
    except BaseException:
        session.rollback()
        raise
    finally:
        session.close()
        connection.dispose_engine()
    return informe


def _imprimir(informe: InformeCarga) -> None:
    print("SIMULACIÓN (no se guardó nada)" if informe.simulado else "Carga confirmada")
    if informe.respaldo:
        print(f"Copia previa verificada: {informe.respaldo}")
    print(f"Cuentas creadas: {informe.cuentas_creadas} · existentes: {informe.cuentas_existentes}")
    print(f"Ejercicios creados: {informe.ejercicios_creados or 'ninguno'}")
    print(f"Importes creados: {informe.importes_creados} · ya cargados: {informe.importes_existentes}")
    print(f"Fuentes registradas: {informe.fuentes_creadas} · totales y datos complementarios: {informe.datos_creados}")
    print(f"Controles de totales: {sum(c.estado == 'OK' for c in informe.controles)}/{len(informe.controles)} OK")
    for c in informe.controles:
        print(f"  {c.anio} {c.estado:10s} {c.concepto:42s} impreso {c.declarado:>18,.2f} calculado {c.calculado:>18,.2f}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--bd", type=Path, default=None, help="Ruta de la base de datos (por defecto data/financiera.db)")
    parser.add_argument("--datos", type=Path, default=ARCHIVO_DATOS, help="Archivo JSON de datos originales")
    parser.add_argument("--simular", action="store_true", help="Ensaya la carga sobre una copia temporal de la BD (no la modifica)")
    args = parser.parse_args(argv)
    try:
        informe = cargar(args.datos, args.bd, simular=args.simular)
    except CargaError as exc:
        print(f"NO SE CARGÓ NADA: {exc}", file=sys.stderr)
        return 1
    _imprimir(informe)
    return 0


if __name__ == "__main__":
    sys.exit(main())
