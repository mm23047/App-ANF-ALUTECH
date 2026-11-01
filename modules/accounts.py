"""Catalogo de cuentas financieras (seccion 5): alta, edicion, desactivacion."""
from __future__ import annotations

import streamlit as st
from sqlalchemy.orm import Session

from database.enums import CategoriaPrincipal as Cat
from database.enums import EfectoCuenta as Efecto
from database.enums import EstadoCuenta
from database.enums import NaturalezaSaldo as Nat
from database.enums import Subcategoria as Sub
from database.enums import subcategorias_validas
from database.repositories import (
    account_has_movements,
    create_account,
    deactivate_account,
    list_accounts,
    update_account,
)

NOMBRES_CATEGORIA = {
    Cat.ACTIVO: "Activo",
    Cat.PASIVO: "Pasivo",
    Cat.PATRIMONIO: "Patrimonio",
    Cat.INGRESOS: "Ingresos",
    Cat.COSTOS: "Costos",
    Cat.GASTOS_OPERATIVOS: "Gastos operativos",
    Cat.INGRESOS_FINANCIEROS: "Ingresos financieros",
    Cat.GASTOS_FINANCIEROS: "Gastos financieros",
    Cat.OTROS_INGRESOS_GASTOS: "Otros ingresos y gastos (no operativos)",
    Cat.IMPUESTOS: "Impuestos",
}

NOMBRES_SUBCATEGORIA = {
    Sub.CORRIENTE: "Corriente",
    Sub.NO_CORRIENTE: "No corriente",
    Sub.CAPITAL_SOCIAL: "Capital social",
    Sub.RESERVAS: "Reservas",
    Sub.RESULTADOS_ACUMULADOS: "Resultados acumulados",
    Sub.RESULTADO_EJERCICIO: "Resultado del ejercicio",
    Sub.OTRAS_PATRIMONIALES: "Otras cuentas patrimoniales",
    Sub.ADMINISTRACION: "Administración",
    Sub.VENTAS: "Ventas",
    Sub.OTROS_OPERATIVOS: "Otros operativos",
}


def _requiere_efecto(categoria: Cat, subcategoria: Sub | None) -> bool:
    return subcategoria == Sub.OTROS_OPERATIVOS or categoria == Cat.OTROS_INGRESOS_GASTOS


def _clasificacion_inputs(prefijo: str, categoria_default=Cat.ACTIVO, sub_default=None, efecto_default=None):
    categoria = st.selectbox(
        "Categoría principal",
        list(Cat),
        index=list(Cat).index(categoria_default),
        format_func=lambda c: NOMBRES_CATEGORIA[c],
        key=f"{prefijo}_categoria",
    )
    subs_validas = sorted(subcategorias_validas(categoria), key=lambda s: s.value)
    subcategoria = None
    if subs_validas:
        idx = subs_validas.index(sub_default) if sub_default in subs_validas else 0
        subcategoria = st.selectbox(
            "Subcategoría",
            subs_validas,
            index=idx,
            format_func=lambda s: NOMBRES_SUBCATEGORIA[s],
            key=f"{prefijo}_subcategoria",
        )
    efecto = None
    if _requiere_efecto(categoria, subcategoria):
        opciones_efecto = list(Efecto)
        idx = opciones_efecto.index(efecto_default) if efecto_default in opciones_efecto else 0
        efecto = st.selectbox(
            "Efecto (¿suma o resta en el subtotal?)",
            opciones_efecto,
            index=idx,
            format_func=lambda e: "Ingreso (suma)" if e == Efecto.INGRESO else "Gasto (resta)",
            key=f"{prefijo}_efecto",
        )
    return categoria, subcategoria, efecto


def render(session: Session) -> None:
    st.header("Catálogo de cuentas")

    tab_lista, tab_nueva = st.tabs(["Cuentas registradas", "Agregar cuenta"])

    with tab_nueva:
        st.subheader("Nueva cuenta")
        codigo = st.text_input("Código de cuenta", key="nueva_codigo")
        nombre = st.text_input("Nombre de cuenta", key="nueva_nombre")
        categoria, subcategoria, efecto = _clasificacion_inputs("nueva")
        naturaleza = st.selectbox(
            "Naturaleza del saldo",
            list(Nat),
            format_func=lambda n: "Deudora" if n == Nat.DEUDORA else "Acreedora",
            key="nueva_naturaleza",
        )
        orden = st.number_input("Orden de presentación", min_value=0, value=0, step=10, key="nueva_orden")

        if st.button("Crear cuenta"):
            if not codigo.strip() or not nombre.strip():
                st.error("El código y el nombre de la cuenta son obligatorios.")
            else:
                try:
                    create_account(
                        session,
                        codigo=codigo.strip(),
                        nombre=nombre.strip(),
                        categoria_principal=categoria,
                        subcategoria=subcategoria,
                        naturaleza_saldo=naturaleza,
                        efecto=efecto,
                        orden_presentacion=int(orden),
                    )
                    session.commit()
                    st.success(f"Cuenta {codigo} creada.")
                    st.rerun()
                except ValueError as exc:
                    session.rollback()
                    st.error(str(exc))

    with tab_lista:
        mostrar_inactivas = st.checkbox("Mostrar cuentas inactivas", value=False)
        cuentas = list_accounts(session)
        if not mostrar_inactivas:
            cuentas = [c for c in cuentas if c.estado == EstadoCuenta.ACTIVA]

        for cuenta in cuentas:
            etiqueta_sub = f" / {NOMBRES_SUBCATEGORIA[cuenta.subcategoria]}" if cuenta.subcategoria else ""
            estado_txt = "🟢 Activa" if cuenta.estado == EstadoCuenta.ACTIVA else "⚪ Inactiva"
            with st.expander(f"{cuenta.codigo} — {cuenta.nombre} ({NOMBRES_CATEGORIA[cuenta.categoria_principal]}{etiqueta_sub}) · {estado_txt}"):
                nombre_edit = st.text_input("Nombre", value=cuenta.nombre, key=f"edit_nombre_{cuenta.id}")
                categoria_edit, subcategoria_edit, efecto_edit = _clasificacion_inputs(
                    f"edit_{cuenta.id}", cuenta.categoria_principal, cuenta.subcategoria, cuenta.efecto
                )
                naturaleza_edit = st.selectbox(
                    "Naturaleza del saldo",
                    list(Nat),
                    index=list(Nat).index(cuenta.naturaleza_saldo),
                    format_func=lambda n: "Deudora" if n == Nat.DEUDORA else "Acreedora",
                    key=f"edit_nat_{cuenta.id}",
                )
                orden_edit = st.number_input(
                    "Orden de presentación", min_value=0, value=cuenta.orden_presentacion, step=10, key=f"edit_orden_{cuenta.id}"
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Guardar cambios", key=f"save_{cuenta.id}"):
                        try:
                            update_account(
                                session,
                                cuenta.id,
                                nombre=nombre_edit.strip(),
                                categoria_principal=categoria_edit,
                                subcategoria=subcategoria_edit,
                                efecto=efecto_edit,
                                naturaleza_saldo=naturaleza_edit,
                                orden_presentacion=int(orden_edit),
                            )
                            session.commit()
                            st.success("Cuenta actualizada.")
                            st.rerun()
                        except ValueError as exc:
                            session.rollback()
                            st.error(str(exc))
                with col2:
                    if cuenta.estado == EstadoCuenta.ACTIVA:
                        tiene_mov = account_has_movements(session, cuenta.id)
                        ayuda = " (tiene movimientos históricos; no se elimina, solo se desactiva)" if tiene_mov else ""
                        if st.button(f"Desactivar{ayuda}", key=f"deact_{cuenta.id}"):
                            deactivate_account(session, cuenta.id)
                            session.commit()
                            st.success("Cuenta desactivada.")
                            st.rerun()
