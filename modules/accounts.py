"""Catalogo de cuentas financieras (seccion 5): alta, edicion, desactivacion.

Una cuenta con importes capturados no puede cambiar su clasificacion
(categoria, subcategoria ni efecto): alteraria los estados de ejercicios
anteriores (hallazgo C-03). Para reclasificar se crea una cuenta nueva y
se desactiva la anterior.
"""
from __future__ import annotations

import streamlit as st
from sqlalchemy.orm import Session

from components.transacciones import ejecutar_escritura
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


def _clasificacion_bloqueada(cuenta) -> None:
    sub = f" / {NOMBRES_SUBCATEGORIA[cuenta.subcategoria]}" if cuenta.subcategoria else ""
    efecto = ""
    if cuenta.efecto:
        efecto = " · efecto: " + ("Ingreso (suma)" if cuenta.efecto == Efecto.INGRESO else "Gasto (resta)")
    st.text_input(
        "Clasificación (bloqueada)",
        value=f"{NOMBRES_CATEGORIA[cuenta.categoria_principal]}{sub}{efecto}",
        disabled=True,
        key=f"edit_clasif_bloqueada_{cuenta.id}",
    )
    st.caption(
        "Esta cuenta tiene importes capturados: cambiar su clasificación alteraría los estados de ejercicios "
        "anteriores. Para reclasificar, cree una cuenta nueva con la clasificación correcta y desactive esta."
    )


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
                creada, _ = ejecutar_escritura(
                    session,
                    lambda: create_account(
                        session,
                        codigo=codigo.strip(),
                        nombre=nombre.strip(),
                        categoria_principal=categoria,
                        subcategoria=subcategoria,
                        naturaleza_saldo=naturaleza,
                        efecto=efecto,
                        orden_presentacion=int(orden),
                    ),
                    descripcion=f"crear la cuenta {codigo.strip()}",
                )
                if creada:
                    st.success(f"Cuenta {codigo} creada.")
                    st.rerun()

    with tab_lista:
        mostrar_inactivas = st.checkbox("Mostrar cuentas inactivas", value=False)
        cuentas = list_accounts(session)
        if not mostrar_inactivas:
            cuentas = [c for c in cuentas if c.estado == EstadoCuenta.ACTIVA]

        for cuenta in cuentas:
            etiqueta_sub = f" / {NOMBRES_SUBCATEGORIA[cuenta.subcategoria]}" if cuenta.subcategoria else ""
            estado_txt = "🟢 Activa" if cuenta.estado == EstadoCuenta.ACTIVA else "⚪ Inactiva"
            with st.expander(f"{cuenta.codigo} — {cuenta.nombre} ({NOMBRES_CATEGORIA[cuenta.categoria_principal]}{etiqueta_sub}) · {estado_txt}"):
                tiene_mov = account_has_movements(session, cuenta.id)
                nombre_edit = st.text_input("Nombre", value=cuenta.nombre, key=f"edit_nombre_{cuenta.id}")
                if tiene_mov:
                    _clasificacion_bloqueada(cuenta)
                    clasificacion = {}
                else:
                    categoria_edit, subcategoria_edit, efecto_edit = _clasificacion_inputs(
                        f"edit_{cuenta.id}", cuenta.categoria_principal, cuenta.subcategoria, cuenta.efecto
                    )
                    clasificacion = dict(
                        categoria_principal=categoria_edit, subcategoria=subcategoria_edit, efecto=efecto_edit
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
                        if not nombre_edit.strip():
                            st.error("El nombre de la cuenta es obligatorio.")
                        else:
                            actualizada, _ = ejecutar_escritura(
                                session,
                                lambda: update_account(
                                    session,
                                    cuenta.id,
                                    nombre=nombre_edit.strip(),
                                    naturaleza_saldo=naturaleza_edit,
                                    orden_presentacion=int(orden_edit),
                                    **clasificacion,
                                ),
                                descripcion=f"actualizar la cuenta {cuenta.codigo}",
                            )
                            if actualizada:
                                st.success("Cuenta actualizada.")
                                st.rerun()
                with col2:
                    if cuenta.estado == EstadoCuenta.ACTIVA:
                        ayuda = " (tiene movimientos históricos; no se elimina, solo se desactiva)" if tiene_mov else ""
                        if st.button(f"Desactivar{ayuda}", key=f"deact_{cuenta.id}"):
                            desactivada, _ = ejecutar_escritura(
                                session, lambda: deactivate_account(session, cuenta.id),
                                descripcion=f"desactivar la cuenta {cuenta.codigo}",
                            )
                            if desactivada:
                                st.success("Cuenta desactivada.")
                                st.rerun()
