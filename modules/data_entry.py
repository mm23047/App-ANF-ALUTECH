"""Ingreso de datos: Balance General, Estado de Resultados y Saldos
iniciales (secciones 6.1, 6.2, 6.3, 9.5)."""
from __future__ import annotations

from decimal import Decimal

import streamlit as st
from sqlalchemy.orm import Session

from calculations.income_statement import compute_income_statement
from components.money import format_money
from components.navigation import select_fiscal_period
from database.enums import CategoriaPrincipal as Cat
from database.enums import EstadoCuenta
from database.enums import EstadoRegistro
from database.enums import Subcategoria as Sub
from database.enums import TipoEstadoFinanciero as Tipo
from database.models import Company, FiscalPeriod
from database.repositories import (
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


def _to_decimal(valor_float: float) -> Decimal:
    return Decimal(str(round(valor_float, 2)))


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
        key=key,
    )
    if seleccion != actual:
        set_statement_status(session, period.id, tipo, seleccion)
        session.commit()
        st.toast(f"Estado cambiado a {etiquetas[seleccion]}.")


def _render_grupos(session: Session, period: FiscalPeriod, tipo: Tipo, grupos, moneda: str, form_key: str) -> None:
    valores_actuales = get_entries_map(session, period.id, tipo)
    cuentas_todas = list_accounts(session, solo_activas=True)

    with st.form(form_key):
        nuevos_valores: dict[int, float] = {}
        for titulo, categoria, subcategoria in grupos:
            cuentas_grupo = [
                c for c in cuentas_todas
                if c.categoria_principal == categoria and (subcategoria is None or c.subcategoria == subcategoria)
            ]
            if not cuentas_grupo:
                continue
            st.subheader(titulo)
            for cuenta in cuentas_grupo:
                valor_previo = valores_actuales.get(cuenta.id, Decimal("0.00"))
                nuevos_valores[cuenta.id] = st.number_input(
                    f"{cuenta.codigo} — {cuenta.nombre} ({moneda})",
                    value=float(valor_previo),
                    step=0.01,
                    format="%.2f",
                    key=f"{form_key}_{cuenta.id}",
                )
        guardado = st.form_submit_button("Guardar")

    if guardado:
        for account_id, valor in nuevos_valores.items():
            upsert_entry(session, fiscal_period_id=period.id, account_id=account_id, valor=_to_decimal(valor), tipo=tipo)
        session.commit()
        st.success("Datos guardados correctamente.")
        st.rerun()


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
        "Estos saldos solo se usan para calcular los promedios del modelo DuPont (sección 9.5) cuando "
        "no existe un ejercicio fiscal anterior registrado en el sistema. Si ya existe un ejercicio "
        "anterior con Balance capturado, su saldo final se usa automáticamente y esta pantalla no es necesaria."
    )
    period = select_fiscal_period(session, key="periodo_saldos_iniciales", allow_create=False)
    if period is None:
        return

    from database.repositories import get_previous_period

    anterior = get_previous_period(session, period.anio)
    if anterior is not None:
        st.warning(
            f"Ya existe el ejercicio {anterior.anio} registrado antes de {period.anio}. El saldo inicial "
            f"de {period.anio} se tomará automáticamente del Balance final de {anterior.anio}; los valores "
            "capturados aquí no se usarán salvo que ese ejercicio anterior no tenga datos de Balance."
        )

    valores_actuales = get_initial_balances_map(session, period.id)
    cuentas = [
        c for c in list_accounts(session, solo_activas=True)
        if c.categoria_principal in (Cat.ACTIVO, Cat.PATRIMONIO)
    ]

    with st.form("form_saldos_iniciales"):
        nuevos_valores: dict[int, float] = {}
        for titulo, categoria in (("Activo", Cat.ACTIVO), ("Patrimonio", Cat.PATRIMONIO)):
            st.subheader(titulo)
            for cuenta in [c for c in cuentas if c.categoria_principal == categoria]:
                valor_previo = valores_actuales.get(cuenta.id, Decimal("0.00"))
                nuevos_valores[cuenta.id] = st.number_input(
                    f"{cuenta.codigo} — {cuenta.nombre} ({company.moneda})",
                    value=float(valor_previo),
                    step=0.01,
                    format="%.2f",
                    key=f"saldo_inicial_{cuenta.id}",
                )
        guardado = st.form_submit_button("Guardar saldos iniciales")

    if guardado:
        for account_id, valor in nuevos_valores.items():
            upsert_initial_balance(session, fiscal_period_id=period.id, account_id=account_id, valor=_to_decimal(valor))
        session.commit()
        st.success("Saldos iniciales guardados.")
        st.rerun()
