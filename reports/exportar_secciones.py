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
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from components.celdas_excel import escribir
from reports.secciones import DIAS, PCT, TEXTO, USD, VAR_PCT, VAR_USD, VECES, Seccion, es_entero, formatear, tipo_celda

AZUL = "0B2447"
GRIS = "F2F2F2"
FORMATOS = {USD: "#,##0.00", PCT: '0.00"%"', VECES: "0.00", DIAS: "#,##0.00", VAR_USD: "+#,##0.00;-#,##0.00;0.00",
            VAR_PCT: '+0.00"%";-0.00"%";0.00"%"'}
FORMATOS_ENTEROS = {USD: "#,##0", VAR_USD: "+#,##0;-#,##0;0"}  # sin centavos cuando no los hay, como en pantalla y en el PDF
FUENTE_DATOS = ("Fuente de los datos: estados financieros originales de Alutech, S. A. de C. V. y subsidiarias - División "
                "Acero (carpeta documentos/). Resultados calculados por la aplicación.")


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
                celda.number_format = (FORMATOS_ENTEROS.get(tipo) if es_entero(valor) else None) or FORMATOS.get(tipo, "#,##0.00")
            else:
                # Mismo texto que en pantalla. En una columna de cifras, a la derecha como las cifras.
                celda = escribir(ws, fila, col, formatear(valor, tipo) if valor is None else str(valor))
                derecha = "right" if seccion.columnas[col - 1].tipo != TEXTO else None
                celda.alignment = Alignment(horizontal=derecha, wrap_text=True, vertical="top")
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
        # Las cifras tambien cuentan: una columna mas angosta que el importe se ve como ##### en Excel.
        largo = max((len(f"{c.value:+,.2f}") if isinstance(c.value, float) else len(str(c.value))
                     for c in columna[2:] if c.value is not None), default=10)
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
_titulo_reporte = ParagraphStyle("TituloDelReporte", parent=_styles["Normal"], fontSize=11, leading=14, alignment=1,
                                 fontName="Helvetica-Bold", textColor=colors.HexColor("#0B2447"))
_sub = ParagraphStyle("SubInforme", parent=_styles["Normal"], fontSize=9, textColor=colors.grey)
_seccion = ParagraphStyle("SeccionInforme", parent=_styles["Heading2"], textColor=colors.HexColor("#0B2447"), fontSize=11)
TAMANOS_CELDA = (7.5, 7, 6.5, 6, 5.5, 5)  # se usa el mayor con el que las cifras caben sin partirse
RELLENO = 3  # puntos a cada lado de la celda
_nota = ParagraphStyle("NotaInforme", parent=_styles["Normal"], fontSize=7, leading=9, textColor=colors.HexColor("#555555"))


def _pie(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(doc.pagesize[0] - 1.5 * cm, 1 * cm, f"Página {doc.page}")
    canvas.drawString(1.5 * cm, 1 * cm, f"Generado el {datetime.date.today().isoformat()}")
    canvas.restoreState()


def _texto_celda(seccion: Seccion, valores: list, i: int) -> str:
    tipo = tipo_celda(seccion, valores, i)
    return formatear(valor, tipo) if not isinstance(valor := valores[i], str) or tipo == TEXTO else valor


def _ancho_palabra(texto: str, tamano: float) -> float:
    return max((stringWidth(p, "Helvetica-Bold", tamano) for p in texto.split()), default=0)


def _anchos_columnas(seccion: Seccion, ancho: float, tamano: float) -> tuple[list[float], bool]:
    """(anchos, caben). Una cifra nunca se parte: su columna mide al menos lo que su cifra mas larga. Las columnas
    de texto se ajustan en varias lineas sin cortar palabras y reparten el espacio que queda."""
    minimos, deseados = [], []
    for i, columna in enumerate(seccion.columnas):
        textos = [_texto_celda(seccion, f, i) for f in seccion.filas]
        encabezado = _ancho_palabra(columna.nombre, tamano)
        if columna.tipo == TEXTO:
            minimo = max([encabezado] + [_ancho_palabra(t, tamano) for t in textos]) + 2 * RELLENO + 1
            deseado = max([stringWidth(columna.nombre, "Helvetica-Bold", tamano)]
                          + [stringWidth(t, "Helvetica-Bold", tamano) for t in textos]) + 2 * RELLENO + 1
        else:
            minimo = deseado = max([encabezado] + [stringWidth(t, "Helvetica-Bold", tamano) for t in textos]) + 2 * RELLENO + 1
        minimos.append(minimo)
        deseados.append(max(minimo, min(deseado, ancho * 0.3)))
    holgura = ancho - sum(minimos)
    if holgura < 0:
        return [m * ancho / sum(minimos) for m in minimos], False
    falta = sum(d - m for d, m in zip(deseados, minimos))
    fraccion = min(1, holgura / falta) if falta else 0
    anchos = [m + (d - m) * fraccion for d, m in zip(deseados, minimos)]
    sobrante = ancho - sum(anchos)
    con_texto = [i for i, c in enumerate(seccion.columnas) if c.tipo == TEXTO] or list(range(len(anchos)))
    for i in con_texto:
        anchos[i] += sobrante / len(con_texto)
    return anchos, True


def _tabla_pdf(seccion: Seccion, ancho: float) -> Table:
    for tamano in TAMANOS_CELDA:
        anchos, caben = _anchos_columnas(seccion, ancho, tamano)
        if caben:
            break
    interlineado = tamano + 1.5
    celda = ParagraphStyle(f"Celda{tamano}", parent=_styles["Normal"], fontSize=tamano, leading=interlineado)
    negrita = ParagraphStyle(f"CeldaNegrita{tamano}", parent=celda, fontName="Helvetica-Bold")
    derecha, derecha_negrita = (ParagraphStyle(f"{e.name}Der", parent=e, alignment=2) for e in (celda, negrita))
    blanco = ParagraphStyle(f"Encabezado{tamano}", parent=negrita, textColor=colors.white)
    blanco_derecha = ParagraphStyle(f"EncabezadoDer{tamano}", parent=blanco, alignment=2)
    datos = [[Paragraph(escape(c.nombre), blanco if c.tipo == TEXTO else blanco_derecha) for c in seccion.columnas]]
    for n, valores in enumerate(seccion.filas):
        destacada = n in seccion.filas_destacadas
        fila = []
        for i, _ in enumerate(valores):
            numerica = seccion.columnas[i].tipo != TEXTO
            estilo_celda = (derecha_negrita if destacada else derecha) if numerica else (negrita if destacada else celda)
            fila.append(Paragraph(escape(_texto_celda(seccion, valores, i)), estilo_celda))
        datos.append(fila)
    tabla = Table(datos, colWidths=anchos, repeatRows=1)
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B2447")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), RELLENO),
        ("RIGHTPADDING", (0, 0), (-1, -1), RELLENO),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
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
    story = [Paragraph(escape(company.nombre_legal), _titulo), Paragraph(escape(titulo), _titulo_reporte), Spacer(1, 0.2 * cm),
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
