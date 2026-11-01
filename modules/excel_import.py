"""Importacion de estados financieros desde Excel (seccion 7).

Plantillas descargables para Balance General y Estado de Resultados.
El tipo de estado (Balance/Resultados) de cada fila se determina por la
clasificacion real de la cuenta en el catalogo (no por lo que diga la
columna Categoria del archivo, que es solo informativa) -- asi se evita
que una importacion de valores reclasifique silenciosamente una cuenta.
"""
from __future__ import annotations

import io
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

import pandas as pd
import streamlit as st
from openpyxl import Workbook
from sqlalchemy.orm import Session

from database.enums import BALANCE_CATEGORIAS, RESULTADOS_CATEGORIAS
from database.enums import EstadoCuenta, TipoEstadoFinanciero
from database.models import Account, Company
from database.repositories import (
    get_account_by_codigo,
    get_entries_map,
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
    estado: str  # OK, CUENTA_DESCONOCIDA, VALOR_NO_NUMERICO, PERIODO_INVALIDO, DUPLICADA
    mensaje: str
    valor_existente: Decimal | None = None


def _validar_dataframe(session: Session, df: pd.DataFrame) -> list[FilaImportacion]:
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

        cuenta = get_account_by_codigo(session, codigo)
        if cuenta is None:
            filas.append(FilaImportacion(numero_fila, codigo, nombre_archivo, None, None, None, "CUENTA_DESCONOCIDA", f"No existe ninguna cuenta con código '{codigo}' en el catálogo."))
            continue
        if cuenta.estado == EstadoCuenta.INACTIVA:
            filas.append(FilaImportacion(numero_fila, codigo, nombre_archivo, None, None, cuenta, "CUENTA_INACTIVA", f"La cuenta {codigo} está desactivada."))
            continue

        try:
            periodo = int(periodo_raw)
        except (TypeError, ValueError):
            filas.append(FilaImportacion(numero_fila, codigo, nombre_archivo, None, None, cuenta, "PERIODO_INVALIDO", f"El período '{periodo_raw}' no es un año válido."))
            continue

        try:
            valor = Decimal(str(valor_raw).strip())
        except (InvalidOperation, ValueError):
            filas.append(FilaImportacion(numero_fila, codigo, nombre_archivo, periodo, None, cuenta, "VALOR_NO_NUMERICO", f"El valor '{valor_raw}' no es numérico."))
            continue

        clave = (codigo, periodo)
        if clave in vistos:
            filas.append(FilaImportacion(numero_fila, codigo, nombre_archivo, periodo, valor, cuenta, "DUPLICADA", f"La cuenta {codigo} aparece más de una vez para el período {periodo} en este archivo."))
            continue
        vistos.add(clave)

        filas.append(FilaImportacion(numero_fila, codigo, nombre_archivo, periodo, valor, cuenta, "OK", "Listo para importar."))

    return filas


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

    cache_entries: dict[tuple[int, TipoEstadoFinanciero], dict[int, Decimal]] = {}
    for fila in filas:
        if fila.estado != "OK" or fila.cuenta is None or fila.periodo is None:
            continue
        tipo = TipoEstadoFinanciero.BALANCE if fila.cuenta.categoria_principal in BALANCE_CATEGORIAS else TipoEstadoFinanciero.RESULTADOS
        periodo_existente = get_or_create_fiscal_period(session, fila.periodo)[0]
        clave_cache = (periodo_existente.id, tipo)
        if clave_cache not in cache_entries:
            cache_entries[clave_cache] = get_entries_map(session, periodo_existente.id, tipo)
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
                "Valor nuevo": f.valor,
                "Valor existente": f.valor_existente,
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
    st.caption(f"{total} filas leídas · {ok} listas para importar · {errores} con observaciones.")

    col_confirmar, col_cancelar = st.columns(2)
    with col_confirmar:
        confirmar = st.button("Confirmar importación", type="primary", disabled=(ok == 0))
    with col_cancelar:
        if st.button("Cancelar"):
            st.info("Importación cancelada. No se guardó ningún dato.")
            return

    if confirmar:
        importadas = 0
        for fila in filas:
            if fila.estado != "OK" or fila.cuenta is None or fila.periodo is None or fila.valor is None:
                continue
            tipo = TipoEstadoFinanciero.BALANCE if fila.cuenta.categoria_principal in BALANCE_CATEGORIAS else TipoEstadoFinanciero.RESULTADOS
            periodo_obj, _ = get_or_create_fiscal_period(session, fila.periodo)
            upsert_entry(session, fiscal_period_id=periodo_obj.id, account_id=fila.cuenta.id, valor=fila.valor, tipo=tipo)
            importadas += 1
        session.commit()
        st.success(f"Importación completada: {importadas} registros importados, {errores} filas con observaciones no importadas.")
