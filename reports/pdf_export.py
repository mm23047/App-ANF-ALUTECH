"""Exportacion de reportes a PDF (seccion 11) usando ReportLab.

Todos los documentos incluyen: nombre de la empresa, periodo fiscal,
titulo del reporte, estado del reporte (DEFINITIVO o sus banderas),
cuentas financieras, importes, porcentajes e indicadores cuando
corresponda, fecha de generacion y numeracion de paginas.

Los textos de longitud variable (nombres de cuenta, advertencias) se
escriben como parrafos para que se ajusten a la celda en lugar de
cortarse, y las tablas repiten su encabezado si cruzan de pagina.
"""
from __future__ import annotations

import datetime
import io
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from calculations.banderas import Bandera, banderas_balance, banderas_dupont, banderas_resultados, resumen
from calculations.vertical_analysis import ETIQUETA_EFECTO
from components.money import format_money, format_percent, format_ratio

AZUL_OSCURO = colors.HexColor("#0B2447")
GRIS_CLARO = colors.HexColor("#F2F2F2")
ROJO = colors.HexColor("#C00000")
VERDE = colors.HexColor("#2E7D32")

_styles = getSampleStyleSheet()
_titulo_style = ParagraphStyle("TituloReporte", parent=_styles["Title"], textColor=AZUL_OSCURO, fontSize=16)
_sub_style = ParagraphStyle("Subtitulo", parent=_styles["Normal"], fontSize=10, textColor=colors.grey)
_seccion_style = ParagraphStyle("Seccion", parent=_styles["Heading2"], textColor=AZUL_OSCURO, fontSize=12)
_celda_style = ParagraphStyle("Celda", parent=_styles["Normal"], fontSize=9, leading=11)
_celda_negrita = ParagraphStyle("CeldaNegrita", parent=_celda_style, fontName="Helvetica-Bold")
_alerta_style = ParagraphStyle("Alerta", parent=_styles["Normal"], fontSize=9, leading=11, textColor=ROJO)
_estado_style = ParagraphStyle("Estado", parent=_styles["Normal"], fontSize=11, fontName="Helvetica-Bold")

ESTILO_TABLA = [
    ("BACKGROUND", (0, 0), (-1, 0), AZUL_OSCURO),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
]


def _texto(texto: str, estilo=_celda_style) -> Paragraph:
    return Paragraph(escape(str(texto)), estilo)


def _pie_pagina(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawRightString(doc.pagesize[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.drawString(2 * cm, 1.2 * cm, f"Generado el {datetime.date.today().isoformat()}")
    canvas.restoreState()


def _encabezado(company, periodo_anio: int, titulo: str) -> list:
    return [
        Paragraph(escape(company.nombre_legal), _titulo_style),
        Paragraph(escape(titulo), _sub_style),
        Paragraph(f"Ejercicio fiscal: {periodo_anio} · Moneda: {escape(company.moneda)}", _sub_style),
        Spacer(1, 0.3 * cm),
    ]


def _banderas(banderas: list[Bandera]) -> list:
    estado = resumen(banderas)
    color = "#2E7D32" if not banderas else "#C00000"
    story = [Paragraph(f'Estado del reporte: <font color="{color}">{escape(estado)}</font>', _estado_style)]
    for bandera in banderas:
        story.append(Paragraph(f"<b>{escape(bandera.codigo)}:</b> {escape(bandera.texto)}", _alerta_style))
    story.append(Spacer(1, 0.4 * cm))
    return story


def _documento(buffer):
    return SimpleDocTemplate(buffer, pagesize=letter, topMargin=2 * cm, bottomMargin=2 * cm)


def _tabla_grupo(grupo, moneda: str) -> list:
    if not grupo.lineas:
        return [Paragraph(escape(grupo.nombre), _seccion_style), _texto("Sin datos capturados."), Spacer(1, 0.3 * cm)]
    filas = [["Código", "Cuenta", "Importe"]]
    for linea in grupo.lineas:
        filas.append([linea.cuenta.codigo, _texto(linea.cuenta.nombre), format_money(linea.valor, moneda)])
    filas.append(["", _texto(f"Subtotal {grupo.nombre}", _celda_negrita), format_money(grupo.subtotal, moneda)])

    tabla = Table(filas, colWidths=[2.5 * cm, 9 * cm, 4 * cm], repeatRows=1)
    tabla.setStyle(TableStyle(ESTILO_TABLA + [
        ("BACKGROUND", (0, -1), (-1, -1), GRIS_CLARO),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
    ]))
    return [Paragraph(escape(grupo.nombre), _seccion_style), tabla, Spacer(1, 0.3 * cm)]


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


def export_balance_pdf(company, period, bs, banderas: list[Bandera] | None = None) -> bytes:
    buffer = io.BytesIO()
    doc = _documento(buffer)
    story = _encabezado(company, period.anio, "Balance General")
    story += _banderas(banderas if banderas is not None else banderas_balance(bs))

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
                f"ADVERTENCIA: la ecuación contable NO cuadra. Diferencia: {escape(format_money(bs.diferencia, company.moneda))}.",
                _alerta_style,
            )
        )

    doc.build(story, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    return buffer.getvalue()


def export_income_pdf(company, period, inc, banderas: list[Bandera] | None = None) -> bytes:
    buffer = io.BytesIO()
    doc = _documento(buffer)
    story = _encabezado(company, period.anio, "Estado de Resultados")
    story += _banderas(banderas if banderas is not None else banderas_resultados(inc))
    story.append(Paragraph("Los costos, gastos e impuestos se capturan en positivo y se restan.", _sub_style))

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


def export_vertical_pdf(company, period, titulo: str, lineas, base, nombre_base: str,
                        banderas: list[Bandera] | None = None) -> bytes:
    """Analisis vertical con cuentas, subtotales, totales y utilidades (M-03)."""
    buffer = io.BytesIO()
    doc = _documento(buffer)
    story = _encabezado(company, period.anio, titulo)
    story += _banderas(banderas or [])
    story.append(Paragraph(f"Base (100%): {escape(nombre_base)} = {escape(format_money(base, company.moneda))}", _seccion_style))
    if any(l.efecto for l in lineas):
        story.append(Paragraph("Los costos, gastos e impuestos tienen porcentaje positivo y restan "
                               "(columna Efecto).", _sub_style))
    story.append(Spacer(1, 0.3 * cm))

    filas = [["Código", "Concepto", "Importe", "%", "Efecto"]]
    estilos = list(ESTILO_TABLA) + [("ALIGN", (2, 0), (3, -1), "RIGHT")]
    for i, linea in enumerate(lineas, start=1):
        destacado = linea.tipo != "cuenta"
        filas.append([
            linea.codigo,
            _texto(linea.etiqueta, _celda_negrita if destacado else _celda_style),
            format_money(linea.valor, company.moneda) if linea.valor is not None else "Sin datos",
            format_percent(linea.porcentaje),
            ETIQUETA_EFECTO.get(linea.efecto, ""),
        ])
        if linea.tipo == "total":
            estilos += [("BACKGROUND", (0, i), (-1, i), GRIS_CLARO), ("FONTNAME", (0, i), (-1, i), "Helvetica-Bold")]
        elif destacado:
            estilos.append(("FONTNAME", (0, i), (-1, i), "Helvetica-Bold"))
    tabla = Table(filas, colWidths=[1.8 * cm, 7.2 * cm, 3.6 * cm, 2 * cm, 2 * cm], repeatRows=1)
    tabla.setStyle(TableStyle(estilos))
    story.append(tabla)

    doc.build(story, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    return buffer.getvalue()


def export_dupont_pdf(company, period, resultado) -> bytes:
    from calculations.dupont import generar_interpretacion

    buffer = io.BytesIO()
    doc = _documento(buffer)
    story = _encabezado(company, period.anio, "Análisis de Rentabilidad — Modelo DuPont")
    story += _banderas(banderas_dupont(resultado))

    def roe(valor):
        return format_percent(valor) if resultado.interpretable else "NO INTERPRETABLE"

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
        ["Margen neto", format_percent(resultado.margen_neto * 100 if resultado.margen_neto is not None else None, 4)],
        ["Rotación de activos", format_ratio(resultado.rotacion_activos, 4)],
        ["Multiplicador del capital", format_ratio(resultado.multiplicador_capital, 4)],
        ["ROE (DuPont)", roe(resultado.roe_dupont_pct)],
        ["ROE directo", roe(resultado.roe_directo_pct)],
    ]
    tabla = Table(filas, colWidths=[9 * cm, 6.5 * cm], repeatRows=1)
    tabla.setStyle(TableStyle(ESTILO_TABLA + [("ALIGN", (1, 0), (1, -1), "RIGHT")]))
    story.append(tabla)
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(f"Fuente de saldos iniciales: {escape(resultado.fuente_saldos_iniciales or '')}.", _sub_style))
    story.append(Paragraph("Criterio: ROE calculado con el patrimonio total del Balance.", _sub_style))
    story.append(Spacer(1, 0.3 * cm))

    if resultado.controles:
        story.append(Paragraph("Controles de los datos", _seccion_style))
        controles = [["Control", "Resultado", "Detalle"]] + [
            [_texto(c.nombre), "Correcto" if c.correcto else "Revisar", _texto(c.detalle)] for c in resultado.controles
        ]
        tabla_controles = Table(controles, colWidths=[5.5 * cm, 2 * cm, 8 * cm], repeatRows=1)
        estilos = list(ESTILO_TABLA)
        for i, c in enumerate(resultado.controles, start=1):
            estilos.append(("TEXTCOLOR", (1, i), (1, i), VERDE if c.correcto else ROJO))
        tabla_controles.setStyle(TableStyle(estilos))
        story.append(tabla_controles)
        story.append(Spacer(1, 0.3 * cm))

    story.append(Paragraph("Interpretación financiera automática", _seccion_style))
    story.append(Paragraph(escape(generar_interpretacion(resultado)), _styles["Normal"]))

    doc.build(story, onFirstPage=_pie_pagina, onLaterPages=_pie_pagina)
    return buffer.getvalue()
