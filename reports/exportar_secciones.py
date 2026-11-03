"""Exportacion a Excel y PDF de las secciones del analisis 2021-2025.

Las cifras salen de reports/secciones.py (calculos centrales); aqui solo se
les da formato. En el Excel cada importe se escribe como numero con el
formato de su unidad (sin redondear el valor); en el PDF y en pantalla se
redondea al presentar. Todas las celdas se escriben con
components.celdas_excel.escribir: un texto nunca se convierte en formula
(hallazgo B-10).
"""
from __future__ import annotations

import datetime
import io
from decimal import Decimal
from xml.sax.saxutils import escape

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from components.celdas_excel import escribir
from reports.secciones import DIAS, PCT, TEXTO, USD, VECES, Seccion, formatear, tipo_celda

AZUL = "0B2447"
GRIS = "F2F2F2"
FORMATOS = {USD: "#,##0.00", PCT: '0.00"%"', VECES: "0.00", DIAS: "#,##0.00"}
FUENTE_DATOS = ("Fuente de los datos: estados financieros originales de Alutech, S. A. de C. V. y subsidiarias - División "
                "Acero (carpeta documentos/). Resultados calculados por la aplicación. Los valores del trabajo ANF solo se "
                "muestran como referencia de comparación.")


# ------------------------------------------------------------------ Excel
def _nombre_hoja(titulo: str, usados: set[str]) -> str:
    base = "".join(ch for ch in titulo if ch not in '[]:*?/\\')[:28] or "Hoja"
    nombre, n = base, 2
    while nombre in usados:
        nombre = f"{base[:25]} {n}"
        n += 1
    usados.add(nombre)
    return nombre


def _escribir_seccion(ws, fila: int, seccion: Seccion) -> int:
    escribir(ws, fila, 1, seccion.titulo).font = Font(bold=True, size=12, color=AZUL)
    fila += 1
    for col, columna in enumerate(seccion.columnas, start=1):
        celda = escribir(ws, fila, col, columna.nombre)
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor=AZUL)
        celda.alignment = Alignment(wrap_text=True, vertical="top")
    fila += 1
    for i, valores in enumerate(seccion.filas):
        for col, valor in enumerate(valores, start=1):
            tipo = tipo_celda(seccion, valores, col - 1)
            if isinstance(valor, Decimal):
                celda = escribir(ws, fila, col, float(valor))
                celda.number_format = FORMATOS.get(tipo, "#,##0.00")
            else:
                celda = escribir(ws, fila, col, "" if valor is None else str(valor))
                celda.alignment = Alignment(wrap_text=True, vertical="top")
            if i in seccion.filas_destacadas:
                celda.font = Font(bold=True)
                celda.fill = PatternFill("solid", fgColor=GRIS)
        fila += 1
    for nota in seccion.notas:
        escribir(ws, fila, 1, nota).font = Font(italic=True, size=9, color="555555")
        fila += 1
    return fila + 1


def _anchos(ws) -> None:
    for columna in ws.columns:
        letra = get_column_letter(columna[0].column)
        largo = max((len(str(c.value)) for c in columna[2:] if c.value is not None and not isinstance(c.value, float)), default=10)
        ws.column_dimensions[letra].width = min(max(12, largo + 2), 60)
    ws.page_setup.orientation = ws.ORIENTATION_LANDSCAPE
    ws.page_setup.paperSize = ws.PAPERSIZE_LETTER
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True


def secciones_a_excel(company, titulo: str, hojas: list[tuple[str, list[Seccion]]]) -> bytes:
    """hojas: [(nombre de hoja, [secciones])]."""
    wb = Workbook()
    wb.remove(wb.active)
    usados: set[str] = set()
    for nombre, secciones in hojas:
        ws = wb.create_sheet(_nombre_hoja(nombre, usados))
        escribir(ws, 1, 1, company.nombre_legal).font = Font(bold=True, size=14, color=AZUL)
        escribir(ws, 2, 1, titulo).font = Font(bold=True, size=12)
        escribir(ws, 3, 1, f"Moneda: {company.moneda} · Generado el {datetime.date.today().isoformat()}").font = Font(italic=True, size=9)
        escribir(ws, 4, 1, FUENTE_DATOS).font = Font(italic=True, size=9, color="555555")
        fila = 6
        for seccion in secciones:
            fila = _escribir_seccion(ws, fila, seccion)
        _anchos(ws)
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


# -------------------------------------------------------------------- PDF
_styles = getSampleStyleSheet()
_titulo = ParagraphStyle("TituloInforme", parent=_styles["Title"], textColor=colors.HexColor("#0B2447"), fontSize=15)
_sub = ParagraphStyle("SubInforme", parent=_styles["Normal"], fontSize=9, textColor=colors.grey)
_seccion = ParagraphStyle("SeccionInforme", parent=_styles["Heading2"], textColor=colors.HexColor("#0B2447"), fontSize=11)
_celda = ParagraphStyle("CeldaInforme", parent=_styles["Normal"], fontSize=6.5, leading=8)
_celda_num = ParagraphStyle("CeldaNum", parent=_celda, alignment=2)
_encabezado = ParagraphStyle("CeldaEncabezado", parent=_celda, textColor=colors.white, fontName="Helvetica-Bold")
_nota = ParagraphStyle("NotaInforme", parent=_styles["Normal"], fontSize=7, leading=9, textColor=colors.HexColor("#555555"))


def _pie(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(doc.pagesize[0] - 1.5 * cm, 1 * cm, f"Página {doc.page}")
    canvas.drawString(1.5 * cm, 1 * cm, f"Generado el {datetime.date.today().isoformat()}")
    canvas.restoreState()


def _tabla_pdf(seccion: Seccion, ancho: float) -> Table:
    pesos = []
    for i, columna in enumerate(seccion.columnas):
        textos = [str(f[i]) for f in seccion.filas if isinstance(f[i], str)]
        largo = max([len(columna.nombre)] + [len(t) for t in textos]) if columna.tipo == TEXTO else 14
        pesos.append(min(max(largo, 6), 45))
    total = sum(pesos)
    anchos = [ancho * p / total for p in pesos]
    datos = [[Paragraph(escape(c.nombre), _encabezado) for c in seccion.columnas]]
    for valores in seccion.filas:
        fila = []
        for i, valor in enumerate(valores):
            tipo = tipo_celda(seccion, valores, i)
            texto = formatear(valor, tipo) if not isinstance(valor, str) or tipo == TEXTO else valor
            fila.append(Paragraph(escape(texto), _celda_num if isinstance(valor, Decimal) else _celda))
        datos.append(fila)
    tabla = Table(datos, colWidths=anchos, repeatRows=1)
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B2447")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]
    for i in seccion.filas_destacadas:
        estilo.append(("BACKGROUND", (0, i + 1), (-1, i + 1), colors.HexColor("#F2F2F2")))
    tabla.setStyle(TableStyle(estilo))
    return tabla


def secciones_a_pdf(company, titulo: str, secciones: list[Seccion], *, salto_por_seccion: bool = False) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    ancho = landscape(letter)[0] - 3 * cm
    story = [Paragraph(escape(company.nombre_legal), _titulo), Paragraph(escape(titulo), _sub),
             Paragraph(f"Moneda: {escape(company.moneda)}", _sub), Paragraph(escape(FUENTE_DATOS), _nota), Spacer(1, 0.3 * cm)]
    for n, seccion in enumerate(secciones):
        if salto_por_seccion and n:
            story.append(PageBreak())
        story.append(Paragraph(escape(seccion.titulo), _seccion))
        if seccion.filas:
            story.append(_tabla_pdf(seccion, ancho))
        else:
            story.append(Paragraph("Sin datos.", _nota))
        for nota in seccion.notas:
            story.append(Paragraph(escape(nota), _nota))
        story.append(Spacer(1, 0.3 * cm))
    doc.build(story, onFirstPage=_pie, onLaterPages=_pie)
    return buffer.getvalue()
