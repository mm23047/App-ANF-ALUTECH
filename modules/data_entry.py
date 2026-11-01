"""Ingreso de datos: Balance General, Estado de Resultados y Saldos
iniciales (secciones 6.1, 6.2, 6.3, 9.5).

Un campo vacio significa "sin dato" y no se guarda; un cero escrito se
guarda como importe cero (hallazgo A-03). Solo se guardan los importes
nuevos o modificados, en una transaccion explicita.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Callable

import streamlit as st
from sqlalchemy.orm import Session

from calculations.income_statement import compute_income_statement
from calculations.validation import CONVENCION_SIGNOS, aviso_signo
from components.money import ImporteInvalido, format_money, parse_importe, parse_importe_con_aviso
from components.navigation import select_fiscal_period
from components.transacciones import ejecutar_escritura
from database.enums import CategoriaPrincipal as Cat
from database.enums import EstadoRegistro
from database.enums import Subcategoria as Sub
from database.enums import TipoEstadoFinanciero as Tipo
from database.models import Account, Company, FiscalPeriod
from database.repositories import (
    delete_initial_balance,
    get_entries_map,
    get_initial_balances_map,
    get_statement_status,
    list_accounts,
    set_statement_status,
    upsert_entry,
    upsert_initial_balance,
)

GRUPOS_BALANCE = [
    ("Activo corriente", Cat.ACTIVO, Sub.CORRIENTE),
    ("Activo no corriente", Cat.ACTIVO, Sub.NO_CORRIENTE),
    ("Pasivo corriente", Cat.PASIVO, Sub.CORRIENTE),
    ("Pasivo no corriente", Cat.PASIVO, Sub.NO_CORRIENTE),
    ("Capital social", Cat.PATRIMONIO, Sub.CAPITAL_SOCIAL),
    ("Reservas", Cat.PATRIMONIO, Sub.RESERVAS),
    ("Resultados acumulados", Cat.PATRIMONIO, Sub.RESULTADOS_ACUMULADOS),
    ("Resultado del ejercicio", Cat.PATRIMONIO, Sub.RESULTADO_EJERCICIO),
    ("Otras cuentas patrimoniales", Cat.PATRIMONIO, Sub.OTRAS_PATRIMONIALES),
]

GRUPOS_RESULTADOS = [
    ("Ingresos netos", Cat.INGRESOS, None),
    ("Costo de ventas", Cat.COSTOS, None),
    ("Gastos de administración", Cat.GASTOS_OPERATIVOS, Sub.ADMINISTRACION),
    ("Gastos de ventas", Cat.GASTOS_OPERATIVOS, Sub.VENTAS),
    ("Otros ingresos/gastos operativos", Cat.GASTOS_OPERATIVOS, Sub.OTROS_OPERATIVOS),
    ("Ingresos financieros", Cat.INGRESOS_FINANCIEROS, None),
    ("Gastos financieros", Cat.GASTOS_FINANCIEROS, None),
    ("Otros ingresos y gastos no operativos", Cat.OTROS_INGRESOS_GASTOS, None),
    ("Impuesto sobre la renta", Cat.IMPUESTOS, None),
]

AYUDA_CAPTURA = (
    "Deje vacío el campo de una cuenta sin dato: no se guardará nada para ella. Un 0 escrito explícitamente "
    "se guarda como importe igual a cero. Vaciar un campo que ya tenía importe no lo borra; para borrarlo "
    "use 'Borrar importe' en Modificación de datos (los saldos iniciales, al pie de su página)."
)


def _to_decimal(valor_float: float) -> Decimal:
    """Convierte el float de st.number_input sin redondeo binario: se toma su
    representacion decimal y se redondea a centavos con ROUND_HALF_UP
    (2.675 -> 2.68). Hallazgo B-08."""
    return parse_importe(valor_float, redondear=True)


def _aviso_ejercicio_cerrado(period: FiscalPeriod) -> bool:
    if period.cerrado:
        st.info(
            f"El ejercicio {period.anio} está cerrado: sus importes no se pueden capturar ni modificar. "
            "Puede reabrirlo en 'Modificación de datos › Ejercicio'."
        )
    return period.cerrado


def _guardar_capturados(
    session: Session,
    period: FiscalPeriod,
    capturados: dict[int, tuple[Account, float | None]],
    valores_actuales: dict[int, Decimal],
    guardar: Callable[[int, Decimal], str | None],
    confirmar_signos: bool = False,
) -> None:
    """Guarda solo los importes informados que son nuevos o distintos del
    actual. Si algun valor es invalido no se guarda nada. Un importe con
    signo distinto a la convencion solo se guarda si el usuario lo confirma;
    nunca se invierte (hallazgo A-05)."""
    errores: list[str] = []
    avisos_signo: list[str] = []
    avisos: list[str] = []
    vaciados: list[str] = []
    cambios: list[tuple[int, Decimal]] = []
    for account_id, (cuenta, valor) in capturados.items():
        previo = valores_actuales.get(account_id)
        if valor is None:
            if previo is not None:
                vaciados.append(f"{cuenta.codigo} — {cuenta.nombre}")
            continue
        if previo is not None and valor == float(previo):
            continue  # sin cambios: el widget muestra el importe guardado
        try:
            importe, aviso = parse_importe_con_aviso(valor, redondear=True)
        except ImporteInvalido as exc:
            errores.append(f"{cuenta.codigo} — {cuenta.nombre}: {exc}")
            continue
        if aviso:
            avisos.append(f"{cuenta.codigo} — {cuenta.nombre}: {aviso}")
        if importe != previo:
            cambios.append((account_id, importe))
            signo = aviso_signo(cuenta, importe)
            if signo:
                avisos_signo.append(signo)

    if errores:
        st.error("No se guardó ningún dato. Corrija estos importes:\n" + "\n".join(f"- {e}" for e in errores))
        return
    if vaciados:
        st.warning(
            "Estos campos se vaciaron, pero conservan su importe guardado (vaciar no borra): "
            + "; ".join(vaciados) + ". Para borrarlos use 'Borrar importe'."
        )
    if not cambios:
        st.info("No hay importes nuevos ni modificados para guardar.")
        return
    if avisos_signo and not confirmar_signos:
        st.warning(
            "No se guardó ningún dato. Estos importes tienen un signo distinto a la convención:\n"
            + "\n".join(f"- {a}" for a in avisos_signo)
            + "\n\nCorríjalos, o marque 'Confirmo los importes con signo distinto a la convención' y guarde de nuevo."
        )
        return

    guardado, operaciones = ejecutar_escritura(
        session,
        lambda: [guardar(account_id, importe) for account_id, importe in cambios],
        descripcion=f"guardar los importes del ejercicio {period.anio}",
    )
    if guardado:
        st.success(
            f"Ejercicio {period.anio}: {operaciones.count('CREAR')} importe(s) nuevo(s) y "
            f"{operaciones.count('EDITAR')} modificado(s)."
        )
        for aviso in avisos:
            st.warning(aviso)
        if not avisos and not vaciados:
            st.rerun()


def _estado_selector(session: Session, period: FiscalPeriod, tipo: Tipo, key: str) -> None:
    actual = get_statement_status(session, period.id, tipo)
    opciones = [EstadoRegistro.BORRADOR, EstadoRegistro.REVISADO]
    etiquetas = {EstadoRegistro.BORRADOR: "Borrador", EstadoRegistro.REVISADO: "Revisado"}
    seleccion = st.radio(
        "Estado de este estado financiero",
        opciones,
        index=opciones.index(actual),
        format_func=lambda e: etiquetas[e],
        horizontal=True,
        disabled=period.cerrado,
        key=f"{key}_{period.id}",
    )
    if seleccion != actual and not period.cerrado:
        cambiado, _ = ejecutar_escritura(
            session,
            lambda: set_statement_status(session, period.id, tipo, seleccion),
            descripcion=f"cambiar el estado del ejercicio {period.anio}",
        )
        if cambiado:
            st.toast(f"Estado cambiado a {etiquetas[seleccion]}.")


def _campo_importe(cuenta: Account, previo: Decimal | None, moneda: str, key: str) -> float | None:
    """Campo vacio (None) si la cuenta no tiene importe guardado."""
    return st.number_input(
        f"{cuenta.codigo} — {cuenta.nombre} ({moneda})",
        value=None if previo is None else float(previo),
        step=0.01,
        format="%.2f",
        placeholder="Sin dato",
        key=key,
    )


def _render_grupos(session: Session, period: FiscalPeriod, tipo: Tipo, grupos, moneda: str, form_key: str) -> None:
    if _aviso_ejercicio_cerrado(period):
        return
    valores_actuales = get_entries_map(session, period.id, tipo)
    cuentas_todas = list_accounts(session, solo_activas=True)
    st.caption(AYUDA_CAPTURA)
    st.caption(CONVENCION_SIGNOS)

    with st.form(form_key):
        capturados: dict[int, tuple[Account, float | None]] = {}
        for titulo, categoria, subcategoria in grupos:
            cuentas_grupo = [
                c for c in cuentas_todas
                if c.categoria_principal == categoria and (subcategoria is None or c.subcategoria == subcategoria)
            ]
            if not cuentas_grupo:
                continue
            st.subheader(titulo)
            for cuenta in cuentas_grupo:
                # La clave incluye el ejercicio para no arrastrar valores
                # escritos en otro ejercicio al cambiar el selector.
                valor = _campo_importe(cuenta, valores_actuales.get(cuenta.id), moneda, f"{form_key}_{period.id}_{cuenta.id}")
                capturados[cuenta.id] = (cuenta, valor)
        confirmar_signos = st.checkbox(
            "Confirmo los importes con signo distinto a la convención", key=f"{form_key}_{period.id}_confirmar_signos"
        )
        guardado = st.form_submit_button("Guardar")

    if guardado:
        _guardar_capturados(
            session,
            period,
            capturados,
            valores_actuales,
            lambda account_id, importe: upsert_entry(
                session, fiscal_period_id=period.id, account_id=account_id, valor=importe, tipo=tipo
            ),
            confirmar_signos,
        )


def render_balance(session: Session, company: Company) -> None:
    st.header("Ingreso de datos — Balance General")
    period = select_fiscal_period(session)
    if period is None:
        return
    st.caption(f"Período seleccionado: ejercicio {period.anio} · Moneda: {company.moneda}")

    inc = compute_income_statement(session, period.id)
    if inc.tiene_datos:
        st.info(
            f"Utilidad neta calculada en el Estado de Resultados {period.anio}: "
            f"{format_money(inc.utilidad_neta, company.moneda)}. Puedes usar este valor en "
            "'Resultado del ejercicio' dentro de Patrimonio (el campo permanece editable: la Ecuación "
            "Contable del reporte de Balance te avisará si no cuadra)."
        )

    _estado_selector(session, period, Tipo.BALANCE, key="estado_balance")
    _render_grupos(session, period, Tipo.BALANCE, GRUPOS_BALANCE, company.moneda, form_key="form_balance")


def render_income(session: Session, company: Company) -> None:
    st.header("Ingreso de datos — Estado de Resultados")
    period = select_fiscal_period(session)
    if period is None:
        return
    st.caption(f"Período seleccionado: ejercicio {period.anio} · Moneda: {company.moneda}")

    _estado_selector(session, period, Tipo.RESULTADOS, key="estado_resultados")
    _render_grupos(session, period, Tipo.RESULTADOS, GRUPOS_RESULTADOS, company.moneda, form_key="form_resultados")


def render_initial_balances(session: Session, company: Company) -> None:
    st.header("Ingreso de datos — Saldos iniciales")
    st.caption(
        "Estos saldos solo se usan para calcular los promedios del modelo DuPont (sección 9.5) cuando el "
        "Balance del ejercicio inmediatamente anterior no existe o no es utilizable (incompleto, con activo "
        "total menor o igual a cero o descuadrado). Capture al menos una cuenta de Activo y una de Patrimonio: "
        "unos saldos parciales no se usan y el DuPont se marca como aproximado."
    )
    period = select_fiscal_period(session, key="periodo_saldos_iniciales", allow_create=False)
    if period is None:
        return

    from calculations.dupont import evaluar_balance_anterior

    bs_anterior, causa = evaluar_balance_anterior(session, period)
    if bs_anterior is not None:
        st.warning(
            f"El saldo inicial de {period.anio} se toma automáticamente del Balance final de {period.anio - 1}; "
            "los valores capturados aquí no se usarán."
        )
    else:
        st.info(f"Se usarán los saldos capturados aquí (si están completos) porque {causa}.")

    if _aviso_ejercicio_cerrado(period):
        return
    valores_actuales = get_initial_balances_map(session, period.id)
    cuentas = [
        c for c in list_accounts(session, solo_activas=True)
        if c.categoria_principal in (Cat.ACTIVO, Cat.PATRIMONIO)
    ]
    st.caption(AYUDA_CAPTURA)
    st.caption(CONVENCION_SIGNOS)

    with st.form("form_saldos_iniciales"):
        capturados: dict[int, tuple[Account, float | None]] = {}
        for titulo, categoria in (("Activo", Cat.ACTIVO), ("Patrimonio", Cat.PATRIMONIO)):
            st.subheader(titulo)
            for cuenta in [c for c in cuentas if c.categoria_principal == categoria]:
                valor = _campo_importe(
                    cuenta, valores_actuales.get(cuenta.id), company.moneda, f"saldo_inicial_{period.id}_{cuenta.id}"
                )
                capturados[cuenta.id] = (cuenta, valor)
        confirmar_signos = st.checkbox(
            "Confirmo los importes con signo distinto a la convención", key=f"saldo_inicial_{period.id}_confirmar_signos"
        )
        guardado = st.form_submit_button("Guardar saldos iniciales")

    if guardado:
        _guardar_capturados(
            session,
            period,
            capturados,
            valores_actuales,
            lambda account_id, importe: upsert_initial_balance(
                session, fiscal_period_id=period.id, account_id=account_id, valor=importe
            ),
            confirmar_signos,
        )

    if valores_actuales:
        cuentas_por_id = {c.id: c for c in list_accounts(session)}
        with st.expander("Borrar un saldo inicial capturado"):
            account_id = st.selectbox(
                "Cuenta",
                list(valores_actuales),
                format_func=lambda i: f"{cuentas_por_id[i].codigo} — {cuentas_por_id[i].nombre} "
                f"({format_money(valores_actuales[i], company.moneda)})",
                key=f"borrar_saldo_inicial_cuenta_{period.id}",
            )
            confirmar = st.checkbox(
                "Confirmo que deseo borrar este saldo inicial (quedará como 'sin dato')",
                key=f"borrar_saldo_inicial_confirmar_{period.id}",
            )
            if st.button("Borrar importe", key=f"borrar_saldo_inicial_{period.id}", disabled=not confirmar):
                borrado, _ = ejecutar_escritura(
                    session,
                    lambda: delete_initial_balance(session, fiscal_period_id=period.id, account_id=account_id),
                    descripcion=f"borrar el saldo inicial de {cuentas_por_id[account_id].codigo}",
                )
                if borrado:
                    st.success("Saldo inicial borrado.")
                    st.rerun()
