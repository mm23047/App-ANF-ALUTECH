"""Avisos de calidad de los estados en pantalla: completitud (M-04), signos
(A-05) y conciliacion resultado-patrimonio (M-07)."""
from __future__ import annotations

import streamlit as st

from calculations.controls import CONCILIADO, DIFERENCIA, Conciliacion
from components.money import format_money


def mostrar_completitud(resultado, nombre_estado: str) -> None:
    if resultado.completo:
        st.caption(f"{nombre_estado}: todas las categorías obligatorias tienen datos capturados.")
    else:
        st.warning(
            f"{nombre_estado.upper()} INCOMPLETO: no hay datos de {', '.join(resultado.categorias_faltantes)}. "
            "Esas categorías aparecen en 0 porque no se capturaron, no porque valgan cero; los totales no son definitivos."
        )
    if resultado.cuentas_sin_dato:
        with st.expander(f"Cuentas activas sin dato ({len(resultado.cuentas_sin_dato)})"):
            st.caption("Informativo: una cuenta sin dato no se suma como cero ni es obligatoria por sí sola.")
            st.write(", ".join(f"{c.codigo} — {c.nombre}" for c in resultado.cuentas_sin_dato))


def mostrar_avisos_signo(resultado) -> None:
    if resultado.advertencias_signo:
        st.warning(
            "Importes con signo distinto a la convención (se muestran tal como se capturaron, sin invertirlos):\n"
            + "\n".join(f"- {a}" for a in resultado.advertencias_signo)
        )


def mostrar_conciliacion(conciliacion: Conciliacion, moneda: str) -> None:
    st.markdown("### Conciliación: resultado del ejercicio frente a utilidad neta")
    if conciliacion.estado == CONCILIADO:
        st.success(conciliacion.mensaje)
    elif conciliacion.estado == DIFERENCIA:
        st.error(conciliacion.mensaje)
    else:
        st.info(conciliacion.mensaje)
    st.caption(
        f"Resultado del ejercicio (patrimonio): {format_money(conciliacion.resultado_patrimonio, moneda)} · "
        f"Utilidad neta (Estado de Resultados): {format_money(conciliacion.utilidad_neta, moneda)} · "
        f"Diferencia: {format_money(conciliacion.diferencia, moneda)}"
    )
