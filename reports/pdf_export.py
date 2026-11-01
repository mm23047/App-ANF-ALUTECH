"""Exportacion de reportes a PDF (seccion 11) usando ReportLab.

Todos los documentos incluyen: nombre de la empresa, periodo fiscal,
titulo del reporte, cuentas financieras, importes, porcentajes e
indicadores cuando corresponda, fecha de generacion y numeracion de
paginas.
"""
from __future__ import annotations

import datetime
import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from components.money import format_money, format_percent, format_ratio

AZUL_OSCURO = colors.HexColor("#0B2447")
GRIS_CLARO = colors.HexColor("#F2F2F2")

_styles = getSampleStyleSheet()
_titulo_style = ParagraphStyle("TituloReporte", parent=_styles["Title"], textColor=AZUL_OSCURO, fontSize=16)
_sub_style = ParagraphStyle("Subtitulo", parent=_styles["Normal"], fontSize=10, textColor=colors.grey)
_seccion_style = ParagraphStyle("Seccion", parent=_styles["Heading2"], textColor=AZUL_OSCURO, fontSize=12)


def _pie_pagina(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(doc.pagesize[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.drawString(2 * cm, 1.2 * cm, f"Generado el {datetime.date.today().isoformat()}")
    canvas.restoreState()


def _encabezado(company, periodo_anio: int, titulo: str) -> list:
    return [
        Paragraph(company.nombre_legal, _titulo_style),
        Paragraph(titulo, _sub_style),
        Paragraph(f"Ejercicio fiscal: {periodo_anio} · Moneda: {company.moneda}", _sub_style),
        Spacer(1, 0.5 * cm),
    ]


def _tabla_grupo(grupo, moneda: str) -> list:
    if not grupo.lineas:
        return []
    filas = [["Código", "Cuenta", "Importe"]]
    for linea in grupo.lineas:
        filas.append([linea.cuenta.codigo, linea.cuenta.nombre, format_money(linea.valor, moneda)])
    filas.append(["", f"Subtotal {grupo.nombre}", format_money(grupo.subtotal, moneda)])

    tabla = Table(filas, colWidths=[2.5 * cm, 9 * cm, 4 * cm])
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), AZUL_OSCURO),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BACKGROUND", (0, -1), (-1, -1), GRIS_CLARO),
                ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (2, 0), (2, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    return [Paragraph(grupo.nombre, _seccion_style), tabla, Spacer(1, 0.3 * cm)]


def _tabla_total(etiqueta: str, valor, moneda: str) -> list:
    tabla = Table([[etiqueta, format_money(valor, moneda)]], colWidths=[11.5 * cm, 4 * cm])
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), AZUL_OSCURO),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return [tabla, Spacer(1, 0.4 * cm)]


def export_balance_pdf(company, period, bs) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=2 * cm, bottomMargin=2 * cm)
    story = _encabezado(company, period.anio, "Balance General")

    story.append(Paragraph("Activo", _seccion_style))
    story += _tabla_grupo(bs.activo_corriente, company.moneda)
    story += _tabla_grupo(bs.activo_no_corriente, company.moneda)
    story += _tabla_total("Total Activo", bs.total_activo, company.moneda)

    story.append(Paragraph("Pasivo", _seccion_style))
    story += _tabla_grupo(bs.pasivo_corriente, company.moneda)
    story += _tabla_grupo(bs.pasivo_no_corriente, company.moneda)
    story += _tabla_total("Total Pasivo", bs.total_pasivo, company.moneda)

    story.append(Paragraph("Patrimonio", _seccion_style))
    for grupo in bs.patrimonio_grupos:
        story += _tabla_grupo(grupo, company.moneda)
    story += _tabla_total("Total Patrimonio", bs.total_patrimonio, company.moneda)
    story += _tabla_total("Total Pasivo + Patrimonio", bs.total_pasivo_patrimonio, company.moneda)

    if bs.cuadra:
        story.append(Paragraph("La ecuación contable cuadra (Activo = Pasivo + Patrimonio).", _sub_style))
    else:
        story.append(
            Paragraph(
                f"ADVERTENCIA: la ecuación contable NO cuadra. Diferencia: {format_money(bs.diferencia, company.moneda)}.",
                _sub_style,
            )
        )

    doc.build(story, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    return buffer.getvalue()


def export_income_pdf(company, period, inc) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=2 * cm, bottomMargin=2 * cm)
    story = _encabezado(company, period.anio, "Estado de Resultados")

    story += _tabla_grupo(inc.ingresos_netos, company.moneda)
    story += _tabla_grupo(inc.costo_ventas, company.moneda)
    story += _tabla_total("Utilidad bruta", inc.utilidad_bruta, company.moneda)

    story += _tabla_grupo(inc.gastos_administracion, company.moneda)
    story += _tabla_grupo(inc.gastos_ventas, company.moneda)
    story += _tabla_grupo(inc.otros_ingresos_operativos, company.moneda)
    story += _tabla_grupo(inc.otros_gastos_operativos, company.moneda)
    story += _tabla_total("Utilidad operativa", inc.utilidad_operativa, company.moneda)

    story += _tabla_grupo(inc.ingresos_financieros, company.moneda)
    story += _tabla_grupo(inc.gastos_financieros, company.moneda)
    story += _tabla_total("Resultado financiero", inc.resultado_financiero, company.moneda)
    story += _tabla_grupo(inc.otros_ingresos_no_operativos, company.moneda)
    story += _tabla_grupo(inc.otros_gastos_no_operativos, company.moneda)
    story += _tabla_total("Otros resultados", inc.otros_resultados, company.moneda)
    story += _tabla_total("Utilidad antes de impuestos", inc.utilidad_antes_impuestos, company.moneda)

    story += _tabla_grupo(inc.impuesto_renta, company.moneda)
    story += _tabla_total("Utilidad neta", inc.utilidad_neta, company.moneda)

    doc.build(story, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    return buffer.getvalue()


def export_dupont_pdf(company, period, resultado) -> bytes:
    from calculations.dupont import generar_interpretacion

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=2 * cm, bottomMargin=2 * cm)
    story = _encabezado(company, period.anio, "Análisis de Rentabilidad — Modelo DuPont")

    filas = [
        ["Componente", "Valor"],
        ["Utilidad neta", format_money(resultado.utilidad_neta, company.moneda)],
        ["Ingresos netos", format_money(resultado.ingresos_netos, company.moneda)],
        ["Activo total inicial", format_money(resultado.activo_inicial, company.moneda)],
        ["Activo total final", format_money(resultado.activo_final, company.moneda)],
        ["Activo total promedio", format_money(resultado.activo_promedio, company.moneda)],
        ["Patrimonio inicial", format_money(resultado.patrimonio_inicial, company.moneda)],
        ["Patrimonio final", format_money(resultado.patrimonio_final, company.moneda)],
        ["Patrimonio promedio", format_money(resultado.patrimonio_promedio, company.moneda)],
        # 4 decimales: el producto de los factores reproduce el ROE mostrado (B-01).
        ["Margen neto", format_percent(resultado.margen_neto * 100, 4)],
        ["Rotación de activos", format_ratio(resultado.rotacion_activos, 4)],
        ["Multiplicador del capital", format_ratio(resultado.multiplicador_capital, 4)],
        ["ROE (DuPont)", format_percent(resultado.roe_dupont_pct)],
        ["ROE directo", format_percent(resultado.roe_directo_pct)],
    ]
    tabla = Table(filas, colWidths=[9 * cm, 6.5 * cm])
    tabla.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), AZUL_OSCURO),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
            ]
        )
    )
    story.append(tabla)
    story.append(Spacer(1, 0.5 * cm))

    if resultado.saldos_aproximados:
        story.append(Paragraph(f"Advertencia: {resultado.fuente_saldos_iniciales}.", _sub_style))
    else:
        story.append(Paragraph(f"Fuente de saldos iniciales: {resultado.fuente_saldos_iniciales}.", _sub_style))
    story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Interpretación financiera automática", _seccion_style))
    story.append(Paragraph(generar_interpretacion(resultado), _styles["Normal"]))

    doc.build(story, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    return buffer.getvalue()
