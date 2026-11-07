"""Modificacion de datos (seccion 8): consultar y modificar registros ya
capturados en un unico tablero por ejercicio, con historial de cambios.

La clasificacion de cuentas (categoria/subcategoria/estado) se edita en
el modulo Catalogo de cuentas -- aqui solo se modifican los IMPORTES
capturados, para no duplicar la logica de validacion de clasificacion.
Guardar la tabla pide confirmar el alcance antes de escribir
(components/confirmacion.py, M-10).
Tambien se administra el ejercicio: cierre, reapertura y eliminacion de
ejercicios vacios (hallazgo M-05).
"""
from __future__ import annotations

from decimal import Decimal

import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session

from calculations.balance_sheet import compute_balance_sheet
from calculations.rubros import datos_ejercicio
from calculations.validation import CONVENCION_SIGNOS, aviso_signo
from components import confirmacion
from components.confirmacion import Cambio
from components.money import ImporteInvalido, es_vacio, format_money, parse_importe_con_aviso
from components.navigation import select_fiscal_period
from components.transacciones import ejecutar_escritura
from components.texto import md
from database.enums import TipoEstadoFinanciero as Tipo
from database.models import Account, Company, FiscalPeriod
from database.repositories import (
    actualizar_atribucion,
    close_fiscal_period,
    delete_entry,
    delete_fiscal_period,
    list_entries,
    list_history,
    par_atribucion,
    period_has_entries,
    registrar_atribucion_documentada,
    reopen_fiscal_period,
    upsert_entry,
)
from modules.history import historial_dataframe


def _valores_tabla(editado: pd.DataFrame) -> tuple:
    """Huella de la tabla editada: si cambia, la propuesta pendiente ya no
    corresponde a lo que el usuario tiene en pantalla."""
    return tuple((int(f["account_id"]), None if es_vacio(f["Valor"]) else float(f["Valor"])) for _, f in editado.iterrows())


def _guardar_edicion(
    session: Session,
    period: FiscalPeriod,
    tipo: Tipo,
    editado: pd.DataFrame,
    originales: dict[int, Decimal],
    cuentas: dict[int, Account],
    confirmar_signos: bool,
    pantalla: str,
) -> None:
    """Valida la tabla y prepara la confirmacion; no escribe nada."""
    confirmacion.descartar(pantalla)
    errores: list[str] = []
    avisos: list[str] = []
    avisos_signo: list[str] = []
    cambios: list[Cambio] = []
    for _, fila in editado.iterrows():
        account_id = int(fila["account_id"])
        cuenta = cuentas[account_id]
        valor = fila["Valor"]
        if es_vacio(valor):
            errores.append(
                f"{cuenta.codigo} — {cuenta.nombre}: la celda está vacía. Para eliminar un importe use 'Borrar importe'."
            )
            continue
        if float(valor) == float(originales[account_id]):
            continue
        try:
            importe, aviso = parse_importe_con_aviso(float(valor), redondear=True)
        except ImporteInvalido as exc:
            errores.append(f"{cuenta.codigo} — {cuenta.nombre}: {exc}")
            continue
        if aviso:
            avisos.append(f"{cuenta.codigo} — {cuenta.nombre}: {aviso}")
        if importe != originales[account_id]:
            cambios.append(Cambio(account_id, f"{cuenta.codigo} — {cuenta.nombre}", originales[account_id], importe))
            signo = aviso_signo(cuenta, importe)
            if signo:
                avisos_signo.append(signo)

    if errores:
        st.error("No se guardó ningún cambio. Corrija:\n" + "\n".join(f"- {md(e)}" for e in errores))
        return
    if not cambios:
        st.info("No se detectaron cambios.")
        return
    if avisos_signo and not confirmar_signos:
        st.warning(
            "No se guardó ningún cambio. Estos importes tienen un signo distinto a la convención:\n"
            + "\n".join(f"- {md(a)}" for a in avisos_signo)
            + "\n\nCorríjalos, o marque la casilla de confirmación y guarde de nuevo."
        )
        return
    estado = "Balance General" if tipo == Tipo.BALANCE else "Estado de Resultados"
    confirmacion.proponer(
        pantalla, (period.id, tipo), resumen=confirmacion.resumen_cambios(cambios, period.anio, estado),
        cambios=cambios, avisos=avisos, extra=_valores_tabla(editado), base=confirmacion.estado_base(session),
    )


def _aplicar_edicion(
    session: Session, period: FiscalPeriod, tipo: Tipo, op: confirmacion.OperacionPendiente, originales: dict[int, Decimal]
) -> None:
    """Escribe los importes confirmados en una sola transaccion, si la base es
    la misma sobre la que se preparo (O-1) y los importes no cambiaron."""
    if not confirmacion.misma_base(op.base, session):
        st.error(f"No se guardó ningún dato: {confirmacion.MENSAJE_BASE_CAMBIADA}")
        return
    if not confirmacion.vigente(op, originales):
        st.error(
            "No se guardó ningún cambio: los importes del ejercicio cambiaron después de la vista previa. "
            "Revise la tabla y guarde de nuevo."
        )
        return
    def escribir():
        # Se repite dentro de la transaccion: si la base cambio, no se escribe nada.
        confirmacion.comprobar_base(op, session)
        return [
            upsert_entry(session, fiscal_period_id=period.id, account_id=c.account_id, valor=c.nuevo, tipo=tipo)
            for c in op.cambios
        ]

    guardado, _ = ejecutar_escritura(session, escribir, descripcion=f"guardar los cambios del ejercicio {period.anio}")
    if guardado:
        st.success(f"Ejercicio {period.anio}: {len(op.cambios)} valor(es) actualizado(s).")
        for aviso in op.avisos:
            st.warning(aviso)
        if not op.avisos:
            st.rerun()


def _borrar_importe(
    session: Session, period: FiscalPeriod, tipo: Tipo, cuentas: dict[int, Account], originales: dict[int, Decimal],
    moneda: str, key: str,
) -> None:
    with st.expander("Borrar un importe capturado"):
        st.caption("El importe borrado queda como 'sin dato' (no como cero) y la eliminación se registra en el historial.")
        account_id = st.selectbox(
            "Cuenta",
            list(originales),
            format_func=lambda i: f"{cuentas[i].codigo} — {cuentas[i].nombre} ({format_money(originales[i], moneda)})",
            key=f"{key}_borrar_cuenta",
        )
        confirmar = st.checkbox(
            f"Confirmo que deseo borrar este importe del ejercicio {period.anio}", key=f"{key}_borrar_confirmar"
        )
        if st.button("Borrar importe", key=f"{key}_borrar", disabled=not confirmar):
            borrado, _ = ejecutar_escritura(
                session,
                lambda: delete_entry(session, fiscal_period_id=period.id, account_id=account_id, tipo=tipo),
                descripcion=f"borrar el importe de {cuentas[account_id].codigo} en {period.anio}",
            )
            if borrado:
                st.success("Importe borrado.")
                st.rerun()


def _tabla_editable(session: Session, period_id: int, tipo: Tipo, moneda: str, key: str) -> None:
    period = session.get(FiscalPeriod, period_id)
    entradas = list_entries(session, period_id, tipo)
    if not entradas:
        st.info("No hay cuentas con valores capturados todavía para este ejercicio.")
        return

    originales = {cuenta.id: valor for cuenta, valor in entradas}
    cuentas = {cuenta.id: cuenta for cuenta, _ in entradas}
    df = pd.DataFrame(
        [
            {
                "account_id": cuenta.id,
                "Código": cuenta.codigo,
                "Nombre": cuenta.nombre,
                "Categoría": cuenta.categoria_principal.value,
                "Subcategoría": cuenta.subcategoria.value if cuenta.subcategoria else "",
                "Valor": float(valor),
            }
            for cuenta, valor in entradas
        ]
    )

    editado = st.data_editor(
        df,
        hide_index=True,
        width="stretch",
        disabled=True if period.cerrado else ["account_id", "Código", "Nombre", "Categoría", "Subcategoría"],
        # account_id identifica la cuenta al guardar: sigue en los datos, pero no se muestra (O-5).
        column_config={"account_id": None, "Valor": st.column_config.NumberColumn(format="%.2f", step=0.01)},
        key=key,
    )
    if period.cerrado:
        confirmacion.descartar(key)
        st.caption(f"El ejercicio {period.anio} está cerrado: solo lectura.")
        return

    st.caption(CONVENCION_SIGNOS)
    confirmar_signos = st.checkbox("Confirmo los importes con signo distinto a la convención", key=f"{key}_confirmar_signos")
    col_guardar, col_cancelar = st.columns(2)
    with col_guardar:
        if st.button("Guardar cambios", key=f"{key}_guardar"):
            _guardar_edicion(session, period, tipo, editado, originales, cuentas, confirmar_signos, key)
    with col_cancelar:
        if st.button("Cancelar modificaciones", key=f"{key}_cancelar"):
            confirmacion.descartar(key)
            st.rerun()
    pendiente = confirmacion.pendiente(key)
    if pendiente is not None and pendiente.extra != _valores_tabla(editado):
        # La tabla se edito despues de pulsar "Guardar cambios": la propuesta ya no vale.
        confirmacion.descartar(key)
        st.info("La tabla cambió después de pulsar 'Guardar cambios'. Pulse de nuevo para revisar el alcance.")
    op = confirmacion.mostrar(key, (period.id, tipo))
    if op is not None:
        _aplicar_edicion(session, period, tipo, op, originales)
    _borrar_importe(session, period, tipo, cuentas, originales, moneda, key)


def _administrar_ejercicio(session: Session, period: FiscalPeriod) -> None:
    if period.cerrado:
        cierre = f" el {period.fecha_cierre:%Y-%m-%d %H:%M} (UTC)" if period.fecha_cierre else ""
        st.info(f"El ejercicio {period.anio} está CERRADO{cierre}. No admite captura, edición, importación ni borrado.")
        confirmar = st.checkbox(f"Confirmo que deseo reabrir el ejercicio {period.anio}", key=f"reabrir_conf_{period.id}")
        if st.button("Reabrir ejercicio", disabled=not confirmar, key=f"reabrir_{period.id}"):
            reabierto, _ = ejecutar_escritura(
                session, lambda: reopen_fiscal_period(session, period.id), descripcion=f"reabrir el ejercicio {period.anio}"
            )
            if reabierto:
                st.rerun()
        return

    st.write(f"El ejercicio {period.anio} está ABIERTO.")
    st.caption("Cerrar un ejercicio impide modificar, importar o borrar sus importes hasta reabrirlo.")
    confirmar = st.checkbox(f"Confirmo que deseo cerrar el ejercicio {period.anio}", key=f"cerrar_conf_{period.id}")
    if st.button("Cerrar ejercicio", disabled=not confirmar, key=f"cerrar_{period.id}"):
        cerrado, _ = ejecutar_escritura(
            session, lambda: close_fiscal_period(session, period.id), descripcion=f"cerrar el ejercicio {period.anio}"
        )
        if cerrado:
            st.rerun()

    st.divider()
    if period_has_entries(session, period.id):
        st.caption("Este ejercicio tiene importes capturados: no se puede eliminar. Solo se eliminan ejercicios vacíos.")
        return
    confirmar_eliminar = st.checkbox(
        f"Confirmo que deseo eliminar el ejercicio vacío {period.anio}", key=f"eliminar_conf_{period.id}"
    )
    if st.button("Eliminar ejercicio", disabled=not confirmar_eliminar, key=f"eliminar_{period.id}"):
        eliminado, anio = ejecutar_escritura(
            session, lambda: delete_fiscal_period(session, period.id), descripcion=f"eliminar el ejercicio {period.anio}"
        )
        if eliminado:
            st.success(f"Ejercicio {anio} eliminado.")
            st.rerun()


def _registrar_atribucion(session: Session, period: FiscalPeriod, datos, moneda: str) -> None:
    """Ejercicio sin atribucion registrada: una atribucion documentada que concilie sustituye al supuesto."""
    utilidad, fuente = datos.utilidad_controladora()
    if utilidad is None:
        return
    with st.expander("Registrar una atribución documentada de la utilidad neta"):
        st.caption(md(f"{fuente}."))
        uc = st.number_input("Utilidad atribuible a la controladora", value=float(datos.utilidad_neta), step=0.01, format="%.2f",
                             key=f"atribucion_doc_uc_{period.id}")
        nci = st.number_input("Participación no controladora", value=0.0, step=0.01, format="%.2f", key=f"atribucion_doc_nci_{period.id}")
        documento = st.text_input("Documento de origen", key=f"atribucion_doc_documento_{period.id}")
        pagina = st.number_input("Página", min_value=1, value=1, step=1, key=f"atribucion_doc_pagina_{period.id}")
        confirmar = st.checkbox(f"Confirmo la atribución documentada del ejercicio {period.anio}", key=f"atribucion_doc_conf_{period.id}")
        if st.button("Registrar atribución", disabled=not confirmar, key=f"atribucion_doc_guardar_{period.id}"):
            guardado, _ = ejecutar_escritura(
                session,
                lambda: registrar_atribucion_documentada(
                    session, fiscal_period_id=period.id, utilidad_neta=datos.utilidad_neta,
                    utilidad_controladora=parse_importe_con_aviso(uc, redondear=True)[0],
                    participacion=parse_importe_con_aviso(nci, redondear=True)[0], documento=documento, pagina=int(pagina)),
                descripcion=f"registrar la atribución del ejercicio {period.anio}",
            )
            if guardado:
                st.success("Atribución registrada.")
                st.rerun()


def _editar_atribucion(session: Session, period: FiscalPeriod, moneda: str) -> None:
    """Utilidad atribuible y participacion no controladora del documento: al cambiar una, la otra se ajusta para que
    ambas sumen la utilidad neta vigente."""
    if period.cerrado:
        return
    datos = datos_ejercicio(session, period)
    par = par_atribucion(datos.complementarios)
    if datos.utilidad_neta is None:
        return
    if par is None:
        _registrar_atribucion(session, period, datos, moneda)
        return
    if par[1] is None:
        return
    dato, participacion, origen = par
    utilidad, fuente = datos.utilidad_controladora()
    with st.expander("Atribución de la utilidad neta (controladora y no controladoras)"):
        st.caption(md(f"Utilidad neta vigente: {format_money(datos.utilidad_neta, moneda)}. Atribuible a la controladora: "
                      f"{format_money(utilidad, moneda)}. {fuente}. Registrado: atribuible {format_money(dato.valor, moneda)}; "
                      f"no controladoras {format_money(participacion.valor, moneda)}."))
        que = st.radio("Dato a modificar", ["Participación no controladora", "Utilidad atribuible a la controladora"], horizontal=True,
                       key=f"atribucion_dato_{period.id}")
        inicial = participacion.valor if que.startswith("Participación") else dato.valor
        importe = st.number_input(que, value=float(inicial), step=0.01, format="%.2f", key=f"atribucion_valor_{period.id}_{que}")
        confirmar = st.checkbox(f"Confirmo que deseo modificar la atribución del ejercicio {period.anio}", key=f"atribucion_conf_{period.id}")
        if st.button("Guardar atribución", disabled=not confirmar, key=f"atribucion_guardar_{period.id}"):
            campo = {"participacion" if que.startswith("Participación") else "utilidad_controladora": parse_importe_con_aviso(importe, redondear=True)[0]}
            guardado, _ = ejecutar_escritura(
                session, lambda: actualizar_atribucion(session, fiscal_period_id=period.id, utilidad_neta=datos.utilidad_neta, **campo),
                descripcion=f"modificar la atribución del ejercicio {period.anio}",
            )
            if guardado:
                st.success("Atribución actualizada.")
                st.rerun()


def render(session: Session, company: Company) -> None:
    st.header("Modificación de datos")
    period = select_fiscal_period(session, key="periodo_edicion", allow_create=False)
    if period is None:
        return

    bs = compute_balance_sheet(session, period.id)
    if bs.tiene_datos:
        estado_eq = "✅ La ecuación contable cuadra." if bs.cuadra else f"⚠️ Diferencia de {md(format_money(bs.diferencia, company.moneda))} entre Activo y Pasivo+Patrimonio."
        st.caption(
            f"Activo: {md(format_money(bs.total_activo, company.moneda))} · "
            f"Pasivo+Patrimonio: {md(format_money(bs.total_pasivo_patrimonio, company.moneda))} · {estado_eq}"
        )

    tab_balance, tab_resultados, tab_historial, tab_ejercicio = st.tabs(
        ["Balance General", "Estado de Resultados", "Historial de este ejercicio", "Ejercicio"]
    )

    with tab_balance:
        _tabla_editable(session, period.id, Tipo.BALANCE, company.moneda, key=f"editor_balance_{period.id}")
    with tab_resultados:
        _tabla_editable(session, period.id, Tipo.RESULTADOS, company.moneda, key=f"editor_resultados_{period.id}")
    with tab_historial:
        registros = list_history(session, fiscal_period_id=period.id)
        if not registros:
            st.info(
                f"Sin modificaciones registradas para el ejercicio {period.anio}. Los cambios anteriores a la "
                "actualización del historial no identifican el ejercicio; consúltelos en 'Historial de cambios'."
            )
        else:
            st.dataframe(historial_dataframe(session, registros), width="stretch")
    with tab_ejercicio:
        _administrar_ejercicio(session, period)
        _editar_atribucion(session, period, company.moneda)
