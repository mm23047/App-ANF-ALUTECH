"""Exportacion de reportes a Excel (seccion 11) usando OpenPyXL.

Todos los libros incluyen nombre de la empresa, periodo fiscal, titulo
del reporte y fecha de generacion en el encabezado, ademas de formulas
de suma nativas de Excel para los subtotales (en vez de solo escribir
el resultado ya calculado), para que el archivo siga siendo auditable.
"""
from __future__ import annotations

import datetime
import io

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

AZUL_OSCURO = "0B2447"
BLANCO = "FFFFFF"
GRIS_CLARO = "F2F2F2"


def _encabezado(ws, company, periodo_anio: int, titulo: str, fila_inicio: int = 1) -> int:
    ws.cell(fila_inicio, 1, company.nombre_legal).font = Font(bold=True, size=14, color=AZUL_OSCURO)
    ws.cell(fila_inicio + 1, 1, titulo).font = Font(bold=True, size=12)
    ws.cell(fila_inicio + 2, 1, f"Ejercicio fiscal: {periodo_anio}  ·  Moneda: {company.moneda}")
    ws.cell(fila_inicio + 3, 1, f"Generado el {datetime.date.today().isoformat()}").font = Font(italic=True, size=9, color="808080")
    return fila_inicio + 5


def _escribir_grupo(ws, fila: int, grupo, encabezados=("Código", "Cuenta", "Importe")) -> tuple[int, int]:
    """Escribe un grupo con formula SUMA para el subtotal. Devuelve (fila_siguiente, fila_subtotal)."""
    if not grupo.lineas:
        return fila, fila
    ws.cell(fila, 1, grupo.nombre).font = Font(bold=True, color=AZUL_OSCURO)
    fila += 1
    fila_encabezado = fila
    for col, titulo in enumerate(encabezados, start=1):
        celda = ws.cell(fila, col, titulo)
        celda.font = Font(bold=True, color=BLANCO)
        celda.fill = PatternFill("solid", fgColor=AZUL_OSCURO)
    fila += 1
    fila_datos_inicio = fila
    for linea in grupo.lineas:
        ws.cell(fila, 1, linea.cuenta.codigo)
        ws.cell(fila, 2, linea.cuenta.nombre)
        ws.cell(fila, 3, float(linea.valor)).number_format = "#,##0.00"
        fila += 1
    fila_datos_fin = fila - 1
    fila_subtotal = fila
    ws.cell(fila, 2, f"Subtotal {grupo.nombre}").font = Font(bold=True)
    celda_subtotal = ws.cell(fila, 3, f"=SUM(C{fila_datos_inicio}:C{fila_datos_fin})" if fila_datos_fin >= fila_datos_inicio else 0)
    celda_subtotal.font = Font(bold=True)
    celda_subtotal.fill = PatternFill("solid", fgColor=GRIS_CLARO)
    celda_subtotal.number_format = "#,##0.00"
    fila += 2
    return fila, fila_subtotal


def _autoajustar_columnas(ws, ancho_col_b: int = 35) -> None:
    ws.column_dimensions["A"].width = 14
    ws.column_dimensions["B"].width = ancho_col_b
    ws.column_dimensions["C"].width = 18


def export_balance_excel(company, period, bs) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Balance General"
    fila = _encabezado(ws, company, period.anio, "Balance General")

    ws.cell(fila, 1, "ACTIVO").font = Font(bold=True, size=11)
    fila += 1
    fila, fila_ac = _escribir_grupo(ws, fila, bs.activo_corriente)
    fila, fila_anc = _escribir_grupo(ws, fila, bs.activo_no_corriente)
    fila_total_activo = fila
    ws.cell(fila, 2, "TOTAL ACTIVO").font = Font(bold=True)
    referencias = [f"C{f}" for f in (fila_ac, fila_anc) if f]
    ws.cell(fila, 3, f"={'+'.join(referencias)}" if referencias else 0).font = Font(bold=True)
    ws.cell(fila, 3).number_format = "#,##0.00"
    fila += 2

    ws.cell(fila, 1, "PASIVO").font = Font(bold=True, size=11)
    fila += 1
    fila, fila_pc = _escribir_grupo(ws, fila, bs.pasivo_corriente)
    fila, fila_pnc = _escribir_grupo(ws, fila, bs.pasivo_no_corriente)
    fila_total_pasivo = fila
    ws.cell(fila, 2, "TOTAL PASIVO").font = Font(bold=True)
    referencias = [f"C{f}" for f in (fila_pc, fila_pnc) if f]
    ws.cell(fila, 3, f"={'+'.join(referencias)}" if referencias else 0).font = Font(bold=True)
    ws.cell(fila, 3).number_format = "#,##0.00"
    fila += 2

    ws.cell(fila, 1, "PATRIMONIO").font = Font(bold=True, size=11)
    fila += 1
    filas_patrimonio = []
    for grupo in bs.patrimonio_grupos:
        fila, fila_sub = _escribir_grupo(ws, fila, grupo)
        if fila_sub:
            filas_patrimonio.append(fila_sub)
    fila_total_patrimonio = fila
    ws.cell(fila, 2, "TOTAL PATRIMONIO").font = Font(bold=True)
    referencias = [f"C{f}" for f in filas_patrimonio]
    ws.cell(fila, 3, f"={'+'.join(referencias)}" if referencias else 0).font = Font(bold=True)
    ws.cell(fila, 3).number_format = "#,##0.00"
    fila += 2

    ws.cell(fila, 2, "TOTAL PASIVO + PATRIMONIO").font = Font(bold=True)
    ws.cell(fila, 3, f"=C{fila_total_pasivo}+C{fila_total_patrimonio}").font = Font(bold=True)
    ws.cell(fila, 3).number_format = "#,##0.00"
    fila += 2

    ws.cell(fila, 1, "Validación: Activo = Pasivo + Patrimonio").font = Font(italic=True)
    ws.cell(fila + 1, 1, f"=C{fila_total_activo}-C{fila-1}").number_format = "#,##0.00"
    ws.cell(fila + 1, 2, "Diferencia (debe ser 0)").font = Font(italic=True)

    _autoajustar_columnas(ws)
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def export_income_excel(company, period, inc) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Estado de Resultados"
    fila = _encabezado(ws, company, period.anio, "Estado de Resultados")

    fila, f_ing = _escribir_grupo(ws, fila, inc.ingresos_netos)
    fila, f_costo = _escribir_grupo(ws, fila, inc.costo_ventas)
    ws.cell(fila, 2, "UTILIDAD BRUTA").font = Font(bold=True)
    ws.cell(fila, 3, f"=C{f_ing}-C{f_costo}" if f_ing and f_costo else float(inc.utilidad_bruta)).number_format = "#,##0.00"
    fila_bruta = fila
    fila += 2

    fila, f_admin = _escribir_grupo(ws, fila, inc.gastos_administracion)
    fila, f_ventas = _escribir_grupo(ws, fila, inc.gastos_ventas)
    fila, f_oio = _escribir_grupo(ws, fila, inc.otros_ingresos_operativos)
    fila, f_ogo = _escribir_grupo(ws, fila, inc.otros_gastos_operativos)
    ws.cell(fila, 2, "UTILIDAD OPERATIVA").font = Font(bold=True)
    partes = [f"C{fila_bruta}"]
    partes += [f"-C{f_admin}"] if f_admin else []
    partes += [f"-C{f_ventas}"] if f_ventas else []
    partes += [f"+C{f_oio}"] if f_oio else []
    partes += [f"-C{f_ogo}"] if f_ogo else []
    ws.cell(fila, 3, "=" + "".join(partes)).number_format = "#,##0.00"
    fila_operativa = fila
    fila += 2

    fila, f_ingfin = _escribir_grupo(ws, fila, inc.ingresos_financieros)
    fila, f_gasfin = _escribir_grupo(ws, fila, inc.gastos_financieros)
    fila, f_oino = _escribir_grupo(ws, fila, inc.otros_ingresos_no_operativos)
    fila, f_ogno = _escribir_grupo(ws, fila, inc.otros_gastos_no_operativos)
    ws.cell(fila, 2, "UTILIDAD ANTES DE IMPUESTOS").font = Font(bold=True)
    partes = [f"C{fila_operativa}"]
    partes += [f"+C{f_ingfin}"] if f_ingfin else []
    partes += [f"-C{f_gasfin}"] if f_gasfin else []
    partes += [f"+C{f_oino}"] if f_oino else []
    partes += [f"-C{f_ogno}"] if f_ogno else []
    ws.cell(fila, 3, "=" + "".join(partes)).number_format = "#,##0.00"
    fila_antes_imp = fila
    fila += 2

    fila, f_isr = _escribir_grupo(ws, fila, inc.impuesto_renta)
    ws.cell(fila, 2, "UTILIDAD NETA").font = Font(bold=True)
    ws.cell(fila, 3, f"=C{fila_antes_imp}-C{f_isr}" if f_isr else float(inc.utilidad_antes_impuestos)).number_format = "#,##0.00"

    _autoajustar_columnas(ws)
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def export_vertical_excel(company, period, titulo: str, df, base, nombre_base: str) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Análisis Vertical"
    fila = _encabezado(ws, company, period.anio, titulo)
    ws.cell(fila, 1, f"Base (100%): {nombre_base} = {float(base):,.2f}").font = Font(italic=True)
    fila += 2

    encabezados = ["Código", "Cuenta", "Valor", "Participación %"]
    for col, titulo_col in enumerate(encabezados, start=1):
        celda = ws.cell(fila, col, titulo_col)
        celda.font = Font(bold=True, color=BLANCO)
        celda.fill = PatternFill("solid", fgColor=AZUL_OSCURO)
    fila += 1
    for _, row in df.iterrows():
        ws.cell(fila, 1, row["Código"])
        ws.cell(fila, 2, row["Cuenta"])
        ws.cell(fila, 3, float(row["Valor"])).number_format = "#,##0.00"
        pct = row["Participación %"]
        celda_pct = ws.cell(fila, 4, float(pct) if pct is not None else "No disponible")
        if pct is not None:
            celda_pct.number_format = "0.00"
        fila += 1

    _autoajustar_columnas(ws)
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def export_dupont_excel(company, period, resultado) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Análisis DuPont"
    fila = _encabezado(ws, company, period.anio, "Análisis de Rentabilidad — Modelo DuPont")

    filas_datos = [
        ("Utilidad neta", float(resultado.utilidad_neta)),
        ("Ingresos netos", float(resultado.ingresos_netos)),
        ("Activo total inicial", float(resultado.activo_inicial)),
        ("Activo total final", float(resultado.activo_final)),
        ("Activo total promedio", float(resultado.activo_promedio)),
        ("Patrimonio inicial", float(resultado.patrimonio_inicial)),
        ("Patrimonio final", float(resultado.patrimonio_final)),
        ("Patrimonio promedio", float(resultado.patrimonio_promedio)),
        ("Margen neto (%)", float(resultado.margen_neto * 100)),
        ("Rotación de activos (veces)", float(resultado.rotacion_activos)),
        ("Multiplicador del capital (veces)", float(resultado.multiplicador_capital)),
        ("ROE DuPont (%)", float(resultado.roe_dupont_pct)),
        ("ROE directo (%)", float(resultado.roe_directo_pct)),
    ]
    for etiqueta, valor in filas_datos:
        ws.cell(fila, 1, etiqueta)
        celda = ws.cell(fila, 2, valor)
        celda.number_format = "#,##0.00"
        fila += 1

    fila += 1
    ws.cell(fila, 1, "Fuente de saldos iniciales:").font = Font(italic=True)
    ws.cell(fila, 2, resultado.fuente_saldos_iniciales or "")

    _autoajustar_columnas(ws, ancho_col_b=30)
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
