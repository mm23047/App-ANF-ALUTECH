"""Exportacion de reportes a Excel (seccion 11) usando OpenPyXL.

Todos los libros incluyen nombre de la empresa, periodo fiscal, titulo
del reporte, fecha de generacion y el estado del reporte (DEFINITIVO o
sus banderas: INCOMPLETO, DESCUADRADO, APROXIMADO, NO INTERPRETABLE...).

Columnas de los estados (hallazgos A-06 y B-03):
  C  Importe: SIEMPRE el valor calculado por Python (calculations/). Se lee
     correctamente aunque el visor no recalcule formulas.
  D  Control: formula nativa de Excel que recalcula el subtotal o total a
     partir de los importes de la columna C. Nunca hace referencia a su
     propia celda (no hay referencias circulares).
  E  Diferencia (C - D): debe ser 0.
Un grupo sin cuentas capturadas se muestra como "Sin datos" y se excluye
de las formulas.
"""
from __future__ import annotations

import datetime
import io
from decimal import Decimal

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

from calculations.banderas import Bandera, banderas_balance, banderas_dupont, banderas_resultados, resumen
from calculations.vertical_analysis import ETIQUETA_EFECTO
from components.money import q2

AZUL_OSCURO = "0B2447"
BLANCO = "FFFFFF"
GRIS_CLARO = "F2F2F2"
ROJO = "C00000"
VERDE = "2E7D32"
FORMATO_IMPORTE = "#,##0.00"
SIN_DATOS = "Sin datos"


def _encabezado(ws, company, periodo_anio: int, titulo: str, fila_inicio: int = 1) -> int:
    ws.cell(fila_inicio, 1, company.nombre_legal).font = Font(bold=True, size=14, color=AZUL_OSCURO)
    ws.cell(fila_inicio + 1, 1, titulo).font = Font(bold=True, size=12)
    ws.cell(fila_inicio + 2, 1, f"Ejercicio fiscal: {periodo_anio}  ·  Moneda: {company.moneda}")
    ws.cell(fila_inicio + 3, 1, f"Generado el {datetime.date.today().isoformat()}").font = Font(italic=True, size=9, color="808080")
    return fila_inicio + 5


def _escribir_banderas(ws, fila: int, banderas: list[Bandera]) -> int:
    estado = resumen(banderas)
    ws.cell(fila, 1, f"Estado del reporte: {estado}").font = Font(bold=True, color=VERDE if not banderas else ROJO)
    fila += 1
    for bandera in banderas:
        ws.cell(fila, 1, f"{bandera.codigo}: {bandera.texto}").font = Font(color=ROJO)
        fila += 1
    return fila + 1


def _importe(ws, fila: int, columna: int, valor: Decimal | None, negrita: bool = False):
    celda = ws.cell(fila, columna, float(q2(valor)) if valor is not None else SIN_DATOS)
    celda.number_format = FORMATO_IMPORTE
    celda.font = Font(bold=negrita)
    return celda


def _encabezado_tabla(ws, fila: int, titulos=("Código", "Cuenta", "Importe", "Control (fórmula)", "Diferencia")) -> int:
    for col, titulo in enumerate(titulos, start=1):
        celda = ws.cell(fila, col, titulo)
        celda.font = Font(bold=True, color=BLANCO)
        celda.fill = PatternFill("solid", fgColor=AZUL_OSCURO)
    return fila + 1


def _control(ws, fila: int, formula: str) -> None:
    """Formula de control en D y diferencia en E. Ambas leen la columna C."""
    ws.cell(fila, 4, formula).number_format = FORMATO_IMPORTE
    ws.cell(fila, 5, f"=C{fila}-D{fila}").number_format = FORMATO_IMPORTE


def _escribir_grupo(ws, fila: int, grupo) -> tuple[int, int | None]:
    """Escribe un grupo y su subtotal. Devuelve (fila_siguiente, fila_subtotal);
    fila_subtotal es None si el grupo no tiene cuentas (no entra en formulas)."""
    ws.cell(fila, 1, grupo.nombre).font = Font(bold=True, color=AZUL_OSCURO)
    fila += 1
    if not grupo.lineas:
        ws.cell(fila, 2, SIN_DATOS).font = Font(italic=True, color="808080")
        return fila + 2, None
    inicio = fila
    for linea in grupo.lineas:
        ws.cell(fila, 1, linea.cuenta.codigo)
        ws.cell(fila, 2, linea.cuenta.nombre)
        _importe(ws, fila, 3, linea.valor)
        fila += 1
    ws.cell(fila, 2, f"Subtotal {grupo.nombre}").font = Font(bold=True)
    _importe(ws, fila, 3, grupo.subtotal, negrita=True).fill = PatternFill("solid", fgColor=GRIS_CLARO)
    _control(ws, fila, f"=SUM(C{inicio}:C{fila - 1})")
    return fila + 2, fila


def _formula(terminos: list[tuple[str, int | None]]) -> str:
    """"=C10-C14+C20" con los terminos (signo, fila) cuya fila existe; "=0" si ninguno."""
    partes = [f"{signo}C{fila}" for signo, fila in terminos if fila is not None]
    if not partes:
        return "=0"
    texto = "".join(partes)
    return "=" + (texto[1:] if texto.startswith("+") else texto)


def _total(ws, fila: int, etiqueta: str, valor: Decimal, terminos: list[tuple[str, int | None]]) -> int:
    ws.cell(fila, 2, etiqueta).font = Font(bold=True)
    _importe(ws, fila, 3, valor, negrita=True)
    _control(ws, fila, _formula(terminos))
    return fila


def _autoajustar_columnas(ws, ancho_col_b: int = 40) -> None:
    for columna, ancho in (("A", 14), ("B", ancho_col_b), ("C", 18), ("D", 18), ("E", 14)):
        ws.column_dimensions[columna].width = ancho


def _guardar(wb) -> bytes:
    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()


def export_balance_excel(company, period, bs, banderas: list[Bandera] | None = None) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Balance General"
    fila = _encabezado(ws, company, period.anio, "Balance General")
    fila = _escribir_banderas(ws, fila, banderas if banderas is not None else banderas_balance(bs))
    fila = _encabezado_tabla(ws, fila)

    ws.cell(fila, 1, "ACTIVO").font = Font(bold=True, size=11)
    fila, f_ac = _escribir_grupo(ws, fila + 1, bs.activo_corriente)
    fila, f_anc = _escribir_grupo(ws, fila, bs.activo_no_corriente)
    f_ta = _total(ws, fila, "TOTAL ACTIVO", bs.total_activo, [("+", f_ac), ("+", f_anc)])
    fila += 2

    ws.cell(fila, 1, "PASIVO").font = Font(bold=True, size=11)
    fila, f_pc = _escribir_grupo(ws, fila + 1, bs.pasivo_corriente)
    fila, f_pnc = _escribir_grupo(ws, fila, bs.pasivo_no_corriente)
    f_tp = _total(ws, fila, "TOTAL PASIVO", bs.total_pasivo, [("+", f_pc), ("+", f_pnc)])
    fila += 2

    ws.cell(fila, 1, "PATRIMONIO").font = Font(bold=True, size=11)
    fila += 1
    filas_patrimonio = []
    for grupo in bs.patrimonio_grupos:
        fila, f_sub = _escribir_grupo(ws, fila, grupo)
        filas_patrimonio.append(("+", f_sub))
    f_tpat = _total(ws, fila, "TOTAL PATRIMONIO", bs.total_patrimonio, filas_patrimonio)
    fila += 2

    f_tpp = _total(ws, fila, "TOTAL PASIVO + PATRIMONIO", bs.total_pasivo_patrimonio, [("+", f_tp), ("+", f_tpat)])
    fila += 2
    _total(ws, fila, "Diferencia: Activo − (Pasivo + Patrimonio) (debe ser 0)", bs.diferencia, [("+", f_ta), ("-", f_tpp)])

    _autoajustar_columnas(ws)
    return _guardar(wb)


def export_income_excel(company, period, inc, banderas: list[Bandera] | None = None) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Estado de Resultados"
    fila = _encabezado(ws, company, period.anio, "Estado de Resultados")
    fila = _escribir_banderas(ws, fila, banderas if banderas is not None else banderas_resultados(inc))
    ws.cell(fila - 1, 1, "Costos, gastos e impuestos se capturan en positivo y se restan.").font = Font(italic=True, size=9)
    fila = _encabezado_tabla(ws, fila)

    fila, f_ing = _escribir_grupo(ws, fila, inc.ingresos_netos)
    fila, f_costo = _escribir_grupo(ws, fila, inc.costo_ventas)
    f_ub = _total(ws, fila, "UTILIDAD BRUTA", inc.utilidad_bruta, [("+", f_ing), ("-", f_costo)])
    fila += 2

    fila, f_admin = _escribir_grupo(ws, fila, inc.gastos_administracion)
    fila, f_ventas = _escribir_grupo(ws, fila, inc.gastos_ventas)
    fila, f_oio = _escribir_grupo(ws, fila, inc.otros_ingresos_operativos)
    fila, f_ogo = _escribir_grupo(ws, fila, inc.otros_gastos_operativos)
    f_uo = _total(ws, fila, "UTILIDAD OPERATIVA", inc.utilidad_operativa,
                  [("+", f_ub), ("-", f_admin), ("-", f_ventas), ("+", f_oio), ("-", f_ogo)])
    fila += 2

    fila, f_ingfin = _escribir_grupo(ws, fila, inc.ingresos_financieros)
    fila, f_gasfin = _escribir_grupo(ws, fila, inc.gastos_financieros)
    f_rf = _total(ws, fila, "RESULTADO FINANCIERO", inc.resultado_financiero, [("+", f_ingfin), ("-", f_gasfin)])
    fila += 2
    fila, f_oino = _escribir_grupo(ws, fila, inc.otros_ingresos_no_operativos)
    fila, f_ogno = _escribir_grupo(ws, fila, inc.otros_gastos_no_operativos)
    f_or = _total(ws, fila, "OTROS RESULTADOS NO OPERATIVOS", inc.otros_resultados, [("+", f_oino), ("-", f_ogno)])
    fila += 2
    f_uai = _total(ws, fila, "UTILIDAD ANTES DE IMPUESTOS", inc.utilidad_antes_impuestos, [("+", f_uo), ("+", f_rf), ("+", f_or)])
    fila += 2

    fila, f_isr = _escribir_grupo(ws, fila, inc.impuesto_renta)
    _total(ws, fila, "UTILIDAD NETA", inc.utilidad_neta, [("+", f_uai), ("-", f_isr)])

    _autoajustar_columnas(ws)
    return _guardar(wb)


def export_vertical_excel(company, period, titulo: str, df, base, nombre_base: str, lineas=None,
                          banderas: list[Bandera] | None = None) -> bytes:
    """Analisis vertical. Con `lineas` (calculations.vertical_analysis) se
    exporta la presentacion completa con subtotales y utilidades; sin ellas,
    las filas de `df` (compatibilidad). La base siempre es numerica (B-03)."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Análisis Vertical"
    fila = _encabezado(ws, company, period.anio, titulo)
    fila = _escribir_banderas(ws, fila, banderas or [])
    ws.cell(fila, 1, "Base (100%)").font = Font(bold=True)
    ws.cell(fila, 2, nombre_base)
    _importe(ws, fila, 3, base, negrita=True)
    fila_base = fila
    fila += 2

    fila = _encabezado_tabla(ws, fila, ("Código", "Concepto", "Importe", "Participación %", "Efecto", "Control % (fórmula)"))
    if lineas is not None:
        filas = [(l.codigo, l.etiqueta, l.valor, l.porcentaje, l.efecto, l.tipo != "cuenta") for l in lineas]
    else:
        filas = [
            (r["Código"], r["Cuenta"], Decimal(str(r["Valor"])),
             None if r["Participación %"] is None or r["Participación %"] != r["Participación %"] else Decimal(str(r["Participación %"])),
             "", False)
            for _, r in df.iterrows()
        ]
    for codigo, etiqueta, valor, porcentaje, efecto, negrita in filas:
        ws.cell(fila, 1, codigo)
        ws.cell(fila, 2, etiqueta).font = Font(bold=negrita)
        _importe(ws, fila, 3, valor, negrita)
        celda_pct = ws.cell(fila, 4, float(porcentaje) if porcentaje is not None else "No disponible")
        celda_pct.number_format = "0.00"
        ws.cell(fila, 5, ETIQUETA_EFECTO.get(efecto, ""))
        if valor is not None and base != 0:
            ws.cell(fila, 6, f"=C{fila}/$C${fila_base}*100").number_format = "0.00"
        fila += 1

    _autoajustar_columnas(ws)
    ws.column_dimensions["F"].width = 18
    return _guardar(wb)


def export_dupont_excel(company, period, resultado) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Análisis DuPont"
    fila = _encabezado(ws, company, period.anio, "Análisis de Rentabilidad — Modelo DuPont")
    fila = _escribir_banderas(ws, fila, banderas_dupont(resultado))

    def roe(valor):
        return valor if resultado.interpretable else "NO INTERPRETABLE"

    filas_datos = [
        ("Utilidad neta", resultado.utilidad_neta, FORMATO_IMPORTE),
        ("Ingresos netos", resultado.ingresos_netos, FORMATO_IMPORTE),
        ("Activo total inicial", resultado.activo_inicial, FORMATO_IMPORTE),
        ("Activo total final", resultado.activo_final, FORMATO_IMPORTE),
        ("Activo total promedio", resultado.activo_promedio, FORMATO_IMPORTE),
        ("Patrimonio inicial", resultado.patrimonio_inicial, FORMATO_IMPORTE),
        ("Patrimonio final", resultado.patrimonio_final, FORMATO_IMPORTE),
        ("Patrimonio promedio", resultado.patrimonio_promedio, FORMATO_IMPORTE),
        ("Margen neto (%)", resultado.margen_neto * 100 if resultado.margen_neto is not None else None, "0.0000"),
        ("Rotación de activos (veces)", resultado.rotacion_activos, "0.0000"),
        ("Multiplicador del capital (veces)", resultado.multiplicador_capital, "0.0000"),
        ("ROE DuPont (%)", roe(resultado.roe_dupont_pct), "0.00"),
        ("ROE directo (%)", roe(resultado.roe_directo_pct), "0.00"),
    ]
    for etiqueta, valor, formato in filas_datos:
        ws.cell(fila, 1, etiqueta)
        celda = ws.cell(fila, 2, float(valor) if isinstance(valor, Decimal) else (valor if valor is not None else "No disponible"))
        celda.number_format = formato
        fila += 1

    fila += 1
    ws.cell(fila, 1, "Fuente de saldos iniciales:").font = Font(italic=True)
    ws.cell(fila, 2, resultado.fuente_saldos_iniciales or "")
    fila += 2
    fila = _encabezado_tabla(ws, fila, ("Control", "Resultado", "Detalle"))
    for control in resultado.controles:
        ws.cell(fila, 1, control.nombre)
        ws.cell(fila, 2, "Correcto" if control.correcto else "Revisar").font = Font(color=VERDE if control.correcto else ROJO)
        ws.cell(fila, 3, control.detalle)
        fila += 1

    ws.column_dimensions["A"].width = 52
    ws.column_dimensions["B"].width = 22
    ws.column_dimensions["C"].width = 60
    return _guardar(wb)
