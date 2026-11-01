"""Importacion de estados financieros desde Excel (seccion 7).

Plantillas descargables para Balance General y Estado de Resultados.
El tipo de estado (Balance/Resultados) de cada fila se determina por la
clasificacion real de la cuenta en el catalogo (no por lo que diga la
columna Categoria del archivo, que es solo informativa) -- asi se evita
que una importacion de valores reclasifique silenciosamente una cuenta.

La vista previa solo lee la base de datos: no crea ejercicios ni escribe
en el historial (hallazgo C-02). Los ejercicios faltantes se indican como
"se creará" y solo se crean al confirmar. La importacion confirmada es
una sola transaccion: si una fila falla, no se guarda ninguna.
"""
from __future__ import annotations

import io
from dataclasses import dataclass
from decimal import Decimal

import pandas as pd
import streamlit as st
from openpyxl import Workbook
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from components.money import (
    AnioFueraDeRango,
    AnioInvalido,
    ImporteInvalido,
    ImporteNoNumerico,
    ImporteVacio,
    es_ruido_float,
    parse_anio,
    parse_importe_con_aviso,
)
from calculations.validation import CONVENCION_SIGNOS, aviso_signo
from components.transacciones import ejecutar_escritura, mensaje_error
from database.enums import BALANCE_CATEGORIAS, RESULTADOS_CATEGORIAS
from database.enums import EstadoCuenta, TipoEstadoFinanciero
from database.models import Account, Company
from database.repositories import (
    get_account_by_codigo,
    get_entries_map,
    get_fiscal_period,
    get_or_create_fiscal_period,
    list_accounts,
    upsert_entry,
)

COLUMNAS = ["Código de cuenta", "Nombre de cuenta", "Categoría", "Subcategoría", "Período", "Valor monetario"]


def _generar_plantilla(session: Session, categorias: set) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Plantilla"
    ws.append(COLUMNAS)
    cuentas = [
        c for c in list_accounts(session, solo_activas=True) if c.categoria_principal in categorias
    ]
    for c in cuentas:
        ws.append([
            c.codigo,
            c.nombre,
            c.categoria_principal.value,
            c.subcategoria.value if c.subcategoria else "",
            "",
            "",
        ])
    convencion = wb.create_sheet("Convención de signos")
    convencion.append(["Convención de signos (se valida al importar; nunca se invierte un signo)"])
    for linea in (
        "Ingresos, costos, gastos e impuestos: en positivo. Los cálculos restan costos y gastos.",
        "Activos, pasivos y patrimonio: en positivo.",
        "Cuentas correctoras del activo (p. ej. depreciación acumulada): en negativo.",
        "Resultados acumulados y resultado del ejercicio: negativos si hay pérdidas.",
        "ISR negativo (beneficio fiscal): se admite, pero requiere confirmación.",
        "Celda vacía = sin dato (no se importa). Un 0 escrito se importa como cero.",
        "Solo se lee la primera hoja ('Plantilla').",
    ):
        convencion.append([linea])
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


@dataclass
class FilaImportacion:
    numero_fila: int
    codigo: str
    nombre_archivo: str
    periodo: int | None
    valor: Decimal | None
    cuenta: Account | None
    # OK, CUENTA_DESCONOCIDA, CUENTA_INACTIVA, PERIODO_INVALIDO, PERIODO_FUERA_DE_RANGO,
    # VALOR_VACIO, VALOR_NO_NUMERICO, VALOR_INVALIDO, DUPLICADA, EJERCICIO_CERRADO,
    # OMITIDA_SIN_AUTORIZACION, SIGNO_SIN_CONFIRMAR
    estado: str
    mensaje: str
    valor_existente: Decimal | None = None
    crea_ejercicio: bool = False
    aviso_signo: str | None = None


def _tipo_de(cuenta: Account) -> TipoEstadoFinanciero:
    return TipoEstadoFinanciero.BALANCE if cuenta.categoria_principal in BALANCE_CATEGORIAS else TipoEstadoFinanciero.RESULTADOS


def _validar_dataframe(session: Session, df: pd.DataFrame) -> list[FilaImportacion]:
    """Valida cada fila. Solo lee la base de datos."""
    filas: list[FilaImportacion] = []
    vistos: set[tuple[str, int]] = set()

    for idx, row in df.iterrows():
        numero_fila = idx + 2  # +1 por encabezado, +1 por index 0-based
        codigo = str(row.get("Código de cuenta", "")).strip()
        nombre_archivo = str(row.get("Nombre de cuenta", "")).strip()
        periodo_raw = row.get("Período")
        valor_raw = row.get("Valor monetario")

        if not codigo or codigo.lower() == "nan":
            continue  # fila vacia, se ignora silenciosamente

        def fila(estado, mensaje, periodo=None, valor=None, cuenta=None):
            return FilaImportacion(numero_fila, codigo, nombre_archivo, periodo, valor, cuenta, estado, mensaje)

        cuenta = get_account_by_codigo(session, codigo)
        if cuenta is None:
            filas.append(fila("CUENTA_DESCONOCIDA", f"No existe ninguna cuenta con código '{codigo}' en el catálogo."))
            continue
        if cuenta.estado == EstadoCuenta.INACTIVA:
            filas.append(fila("CUENTA_INACTIVA", f"La cuenta {codigo} está desactivada.", cuenta=cuenta))
            continue

        try:
            periodo = parse_anio(periodo_raw)
        except AnioFueraDeRango as exc:
            filas.append(fila("PERIODO_FUERA_DE_RANGO", str(exc), cuenta=cuenta))
            continue
        except AnioInvalido as exc:
            filas.append(fila("PERIODO_INVALIDO", str(exc), cuenta=cuenta))
            continue

        try:
            # Solo se redondea el ruido binario de Excel (0.30000000000000004);
            # un tercer decimal real (2.675) se rechaza.
            valor, aviso = parse_importe_con_aviso(valor_raw, redondear=es_ruido_float(valor_raw))
        except ImporteVacio:
            filas.append(fila("VALOR_VACIO", "La celda 'Valor monetario' está vacía (sin dato); no se importará.", periodo, cuenta=cuenta))
            continue
        except ImporteNoNumerico as exc:
            filas.append(fila("VALOR_NO_NUMERICO", str(exc), periodo, cuenta=cuenta))
            continue
        except ImporteInvalido as exc:
            filas.append(fila("VALOR_INVALIDO", str(exc), periodo, cuenta=cuenta))
            continue

        clave = (codigo, periodo)
        if clave in vistos:
            filas.append(fila("DUPLICADA", f"La cuenta {codigo} aparece más de una vez para el período {periodo} en este archivo.", periodo, valor, cuenta))
            continue
        vistos.add(clave)

        periodo_existente = get_fiscal_period(session, periodo)
        if periodo_existente is not None and periodo_existente.cerrado:
            filas.append(fila("EJERCICIO_CERRADO", f"El ejercicio {periodo} está cerrado; reábralo para importar.", periodo, valor, cuenta))
            continue

        signo = aviso_signo(cuenta, valor)
        nueva = fila("OK", "Listo para importar." + (f" {aviso}" if aviso else "") + (f" {signo}" if signo else ""),
                     periodo, valor, cuenta)
        nueva.crea_ejercicio = periodo_existente is None
        nueva.aviso_signo = signo
        filas.append(nueva)

    return filas


def _importar(session: Session, filas: list[FilaImportacion]) -> dict[str, int]:
    """Crea los ejercicios faltantes e importa las filas OK. Se ejecuta dentro
    de una sola transaccion (ejecutar_escritura): cualquier error revierte todo."""
    resultado = {"CREAR": 0, "EDITAR": 0, "SIN_CAMBIOS": 0, "EJERCICIOS": 0}
    for fila in filas:
        if fila.estado != "OK":
            continue
        try:
            periodo, creado = get_or_create_fiscal_period(session, fila.periodo)
            resultado["EJERCICIOS"] += int(creado)
            operacion = upsert_entry(
                session, fiscal_period_id=periodo.id, account_id=fila.cuenta.id, valor=fila.valor, tipo=_tipo_de(fila.cuenta)
            )
        except ValueError as exc:
            raise ValueError(f"fila {fila.numero_fila} ({fila.codigo}): {exc}") from exc
        except SQLAlchemyError as exc:
            raise ValueError(f"fila {fila.numero_fila} ({fila.codigo}): {mensaje_error(exc)}") from exc
        resultado[operacion or "SIN_CAMBIOS"] += 1
    return resultado


def render(session: Session, company: Company) -> None:
    st.header("Importación desde Excel")

    st.subheader("1. Plantillas descargables")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Descargar plantilla — Balance General",
            data=_generar_plantilla(session, BALANCE_CATEGORIAS),
            file_name="plantilla_balance_general.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    with col2:
        st.download_button(
            "Descargar plantilla — Estado de Resultados",
            data=_generar_plantilla(session, RESULTADOS_CATEGORIAS),
            file_name="plantilla_estado_resultados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    st.caption(
        "Deje vacía la celda 'Valor monetario' de las cuentas sin dato: no se importarán (vacío no es cero). "
        "Use punto decimal, sin separador de miles y como máximo dos decimales. "
        "La hoja 'Convención de signos' de la plantilla explica los signos esperados."
    )

    st.subheader("2. Subir archivo")
    archivo = st.file_uploader("Archivo XLSX (Balance General o Estado de Resultados)", type=["xlsx"])
    if archivo is None:
        return

    try:
        df = pd.read_excel(archivo, sheet_name=0)
    except Exception as exc:  # noqa: BLE001 - mostrar cualquier error de lectura al usuario
        st.error(f"No se pudo leer el archivo: {exc}")
        return

    faltantes = [c for c in COLUMNAS if c not in df.columns]
    if faltantes:
        st.error(f"El archivo no tiene la estructura esperada. Faltan columnas: {', '.join(faltantes)}")
        return

    filas = _validar_dataframe(session, df)
    if not filas:
        st.warning("El archivo no contiene filas con datos.")
        return

    permitir_sobrescribir = st.checkbox(
        "Permitir sobrescribir valores ya existentes en la base de datos", value=False
    )
    confirmar_signos = False
    if any(f.estado == "OK" and f.aviso_signo for f in filas):
        st.warning(CONVENCION_SIGNOS)
        confirmar_signos = st.checkbox(
            "Importar también las filas con signo distinto a la convención (confirmo que son correctas)", value=False
        )
    for fila in filas:
        if fila.estado == "OK" and fila.aviso_signo and not confirmar_signos:
            fila.estado = "SIGNO_SIN_CONFIRMAR"

    # Vista previa: solo consultas de lectura.
    cache_entries: dict[tuple[int, TipoEstadoFinanciero], dict[int, Decimal]] = {}
    for fila in filas:
        if fila.estado != "OK" or fila.crea_ejercicio:
            continue
        periodo_existente = get_fiscal_period(session, fila.periodo)
        clave_cache = (periodo_existente.id, _tipo_de(fila.cuenta))
        if clave_cache not in cache_entries:
            cache_entries[clave_cache] = get_entries_map(session, periodo_existente.id, clave_cache[1])
        existente = cache_entries[clave_cache].get(fila.cuenta.id)
        fila.valor_existente = existente
        if existente is not None and existente != fila.valor and not permitir_sobrescribir:
            fila.estado = "OMITIDA_SIN_AUTORIZACION"
            fila.mensaje = f"Ya existe un valor ({existente}) para este período; marca la casilla para sobrescribir."

    st.subheader("3. Vista previa")
    vista = pd.DataFrame(
        [
            {
                "Fila": f.numero_fila,
                "Código": f.codigo,
                "Cuenta en catálogo": f.cuenta.nombre if f.cuenta else "—",
                "Período": f.periodo,
                "Ejercicio": ("Se creará" if f.crea_ejercicio else "Existe") if f.estado == "OK" else "",
                "Valor nuevo": f"{f.valor:.2f}" if f.valor is not None else "",
                "Valor existente": f"{f.valor_existente:.2f}" if f.valor_existente is not None else "",
                "Estado": f.estado,
                "Detalle": f.mensaje,
            }
            for f in filas
        ]
    )
    st.dataframe(vista, width="stretch")

    total = len(filas)
    ok = sum(1 for f in filas if f.estado == "OK")
    errores = total - ok
    st.caption(f"{total} filas leídas · {ok} listas para importar · {errores} con observaciones (no se importarán).")
    a_crear = sorted({f.periodo for f in filas if f.estado == "OK" and f.crea_ejercicio})
    if a_crear:
        st.info(f"Al confirmar se crearán los ejercicios: {', '.join(str(a) for a in a_crear)}.")

    col_confirmar, col_cancelar = st.columns(2)
    with col_confirmar:
        confirmar = st.button("Confirmar importación", type="primary", disabled=(ok == 0))
    with col_cancelar:
        if st.button("Cancelar"):
            st.info("Importación cancelada. No se guardó ningún dato.")
            return

    if confirmar and ok:
        importado, resultado = ejecutar_escritura(session, lambda: _importar(session, filas), descripcion="importar el archivo")
        if importado:
            st.success(
                f"Importación completada: {resultado['CREAR']} importes nuevos, {resultado['EDITAR']} sobrescritos, "
                f"{resultado['SIN_CAMBIOS']} sin cambios, {resultado['EJERCICIOS']} ejercicio(s) creado(s). "
                f"{errores} fila(s) con observaciones no se importaron."
            )
