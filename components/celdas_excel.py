"""Escritura de celdas XLSX con openpyxl (hallazgo B-10).

openpyxl guarda como formula cualquier cadena asignada a una celda que
empiece con "=". Un nombre de empresa o de cuenta como
'=HYPERLINK("http://...","x")' se exportaria como formula activa.

Por eso la escritura se separa en dos caminos:
- texto() / escribir(): todo str se guarda como cadena literal
  (data_type "s"). Si empieza con un signo que una hoja de calculo
  interpreta como formula (= + - @, tabulador o retorno de carro) se
  marca ademas con quotePrefix: Excel lo sigue tratando como texto
  aunque el usuario edite la celda. El texto no se modifica.
- formula(): unico camino para las formulas de control que genera la
  aplicacion.

Los caracteres de control que XLSX no admite (U+0000-U+0008, U+000B,
U+000C, U+000E-U+001F) se eliminan; el resto, incluidos los saltos de
linea, se conserva.
"""
from __future__ import annotations

from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE, Cell
from openpyxl.worksheet.worksheet import Worksheet

PREFIJOS_FORMULA = ("=", "+", "-", "@", "\t", "\r")


def texto(ws: Worksheet, fila: int, columna: int, valor: str) -> Cell:
    """Escribe `valor` como cadena literal, nunca como formula."""
    limpio = ILLEGAL_CHARACTERS_RE.sub("", str(valor))
    celda = ws.cell(fila, columna)
    celda.value = limpio
    celda.data_type = "s"  # openpyxl habria puesto "f" si empieza con "="
    if limpio.startswith(PREFIJOS_FORMULA):
        celda.quotePrefix = True
    return celda


def escribir(ws: Worksheet, fila: int, columna: int, valor) -> Cell:
    """Escribe un dato: un str como texto literal; un numero o None tal cual."""
    if isinstance(valor, str):
        return texto(ws, fila, columna, valor)
    return ws.cell(fila, columna, valor)


def formula(ws: Worksheet, fila: int, columna: int, expresion: str) -> Cell:
    """Escribe una formula generada por la aplicacion (nunca un dato del usuario)."""
    if not expresion.startswith("="):
        raise ValueError(f"No es una fórmula: {expresion!r}")
    return ws.cell(fila, columna, expresion)


def agregar_fila(ws: Worksheet, valores) -> int:
    """Equivalente a ws.append() con escribir() en cada celda. Devuelve la fila."""
    fila = ws.max_row + 1 if ws.max_row > 1 or ws.cell(1, 1).value is not None else 1
    for columna, valor in enumerate(valores, start=1):
        escribir(ws, fila, columna, valor)
    return fila
