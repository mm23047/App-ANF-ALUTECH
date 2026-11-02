"""Texto de usuario dentro de elementos Markdown de Streamlit (hallazgo B-04).

st.markdown, st.caption, st.subheader, st.info, etc. interpretan Markdown
(y extensiones de Streamlit: :color[...], :emoji:, $LaTeX$). Un dato
escrito por el usuario (nombre de la empresa, moneda) debe mostrarse
literalmente: se antepone una barra invertida a todo signo de puntuacion
ASCII, que CommonMark muestra como el caracter tal cual. Asi `<b>x</b>`
se ve como texto y `&amp;` no se convierte en `&`.

El HTML nunca se habilita con datos dinamicos: el unico
unsafe_allow_html del proyecto es el CSS constante de app.py.
"""
from __future__ import annotations

import string

_ESCAPES = {ord(c): "\\" + c for c in string.punctuation}


def md(valor: object) -> str:
    """Devuelve `valor` como texto literal para un elemento Markdown."""
    texto = "" if valor is None else str(valor)
    # Un salto de linea en un dato de una sola linea romperia el formato.
    texto = " ".join(texto.splitlines())
    return texto.translate(_ESCAPES)
