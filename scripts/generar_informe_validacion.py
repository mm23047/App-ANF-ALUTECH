"""Genera INFORME_VALIDACION_FINANCIERA.md a partir de la base de datos.

Las tablas del informe (comparacion por ejercicio, por indicador, detalle y
discrepancias) se calculan en el momento con calculations/comparacion_anf.py
sobre los datos originales cargados; no se escriben a mano. Solo lee la BD.

Uso:  python scripts/generar_informe_validacion.py [--bd RUTA.db] [--salida ARCHIVO.md]
"""
from __future__ import annotations

import argparse
import datetime
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

PROYECTO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROYECTO))

from calculations import indicadores as ind  # noqa: E402
from calculations.comparacion_anf import (  # noqa: E402
    COINCIDE,
    DIFERENCIA,
    ESTADOS,
    NO_APLICA,
    NO_VERIFICABLE,
    REDONDEO,
    cargar_observaciones,
    comparar,
    fuera_de_alcance,
)
from calculations.rubros import datos_todos  # noqa: E402
from database import connection  # noqa: E402


def _num(valor: Decimal | None, decimales: int) -> str:
    if valor is None:
        return "No calculable"
    return f"{valor:,.{decimales}f}"


def _app(valor: Decimal | None, decimales: int) -> str:
    """Resultado de la aplicacion con dos decimales mas que el trabajo (salvo importes)."""
    return _num(valor, decimales + 2 if decimales else 0)


ANALISIS = """## 9. Análisis de las discrepancias

### 9.1 Posibles errores del trabajo

1. **Activo y pasivo corriente de 2023 en las Tablas 3, 4 y 6** (OBS-01, OBS-02, OBS-05). El trabajo usa 541,094,544 y
   342,120,685; el estado combinado 2023 presenta 429,794,544 y 333,120,685 (la suma de las partidas transcritas coincide
   con esos totales). Estas cifras no aparecen en ningún documento de la carpeta; en magnitud coinciden con las del informe
   PCR de junio 2025 (541.1 M y 342.1 M en dic‑23), que corresponde a otro perímetro (activo total 818.1 M). El propio
   trabajo usa las cifras correctas en el análisis vertical (7.2), en la tabla de liquidez (8.1) y en el fondo de maniobra
   (9.2), por lo que presenta **dos valores distintos** del CTN 2023 (198,973,859 y 96,673,859), de la razón corriente
   (1.58 y 1.29) y de la prueba ácida (1.17 y 0.87). La conclusión de 6.5 sobre 2022–2023 («CTN −8.20 %») subestima el
   deterioro: con los datos originales el CTN cae 55.39 %.
2. **Pasivo corriente de 2022** (OBS-03, OBS-04): 231,914,180 en lugar de 231,944,180 (dígitos intercambiados). Arrastra
   el CTN 2022 (216,758,221 en lugar de 216,728,221) y sus variaciones en las Tablas 3, 6 y 7.
3. **Utilidad operativa 2022 en la Tabla 5** (OBS-06): 31,200,000* frente a 31,200,977 (cifra que el mismo trabajo usa en
   8.3 B y 8.4).
4. **Base de las cuentas por cobrar en 8.2 B** (OBS-07): mezcla la cartera comercial (2021–2022) con la cartera comercial
   y otras (2023). La aplicación calcula ambas variantes y reproduce el valor del trabajo con la base homogénea.
5. **WACC 2023** (OBS-11): el cuadro dice 3.88 % y el texto 3.87 %; el cálculo da 3.8745 % (3.87 %).
6. **Clasificación de «Otras cuentas por cobrar a LP» 2024 en 9.7** (OBS-12): el trabajo la trata como cuenta por cobrar a
   partes relacionadas; ni el estado de 2024 ni el informe PCR (que a dic‑24 muestra 0.0 de relacionadas no corrientes)
   respaldan esa equivalencia. Con la clasificación documentada, el total de fuentes y usos 2025 vs 2024 es 408,447,177.
7. Erratas sin efecto en los resultados: en 9.5 el divisor de la rotación aparece como 553,995,185 (el resultado 0.9459
   usa el correcto 553,955,185) y la verificación directa escribe «68,602.739».

### 9.2 Posibles errores de extracción

La extracción de la aplicación se verificó con **61 totales y subtotales impresos** (activo y pasivo corriente y no
corriente, totales, patrimonio, utilidad bruta, operativa, antes de impuestos y neta): todos coinciden con la suma de
las partidas transcritas (control en «Datos originales › Trazabilidad» y en la carga). El PDF de 2024 está escaneado (sin
texto): se transcribió visualmente y se validó con todos sus subtotales impresos. No se detectaron errores de extracción
en la aplicación. Observaciones de los documentos originales que no afectan los totales:

- 2024: capital social 119,391,833 frente a 119,389,833 en 2022, 2023 y 2025 (diferencia de 2,000; los totales impresos
  de 2024 cuadran con 119,391,833).
- 2021: el estado de cambios en el patrimonio cierra en 145,321,189 y participaciones no controladoras 3,263,360; el
  balance presenta 145,321,190 y 3,263,361 (diferencia de redondeo de 1 USD en el documento).
- 2023: el estado de resultados atribuye 13,330,680 a la controladora; el estado de cambios en el patrimonio, 12,309,102
  a la controladora y 1,021,578 a las no controladoras. La aplicación usa el estado de cambios en el patrimonio (fuente
  disponible para 2021–2023), igual que el trabajo.

### 9.3 Diferencias de clasificación entre ejercicios

- 2021–2023 son **estados combinados** (certificación de Espinoza Auditores; auditados por PwC Honduras) y 2024–2025
  **estados consolidados** internos firmados por la administración. La denominación y la agrupación de las cuentas
  cambian entre 2023 y 2024; la aplicación conserva cada denominación y las compara mediante grupos de análisis
  (`MAPEO_FINANCIERO_ALUTECH.md`).
- 2024–2025 presentan «Deudores comerciales y otras cuentas por cobrar» y «Acreedores comerciales y otras cuentas por
  pagar» en una sola línea: los períodos de cobro y de pago no son homogéneos con 2021–2023.
- 2021–2023 presentan el gasto financiero **neto**; 2024–2025 separan ingresos y gastos financieros. «Otros ingresos» se
  presenta dentro de la utilidad de operación en 2021–2023 y después del resultado financiero en 2024–2025.
- 2024 «Otras cuentas por cobrar a LP» (118,684,551) se mantiene como «otras cuentas por cobrar no corrientes»; no se
  agrupa con «Cuentas por cobrar Empresas Relacionadas a LP» de 2025 porque ningún documento lo respalda (revisión final
  del 2026-11-02; antes se había adoptado la equivalencia del trabajo). Solo cambia el análisis por grupos y el origen y
  aplicación de fondos; ningún indicador.
- Los estados 2024–2025 no presentan plusvalía ni participaciones no controladoras por separado.

### 9.4 Recomendaciones de corrección para el trabajo

1. Sustituir en las Tablas 3, 4, 6 y 7 el activo corriente 2023 por 429,794,544 y el pasivo corriente 2023 por
   333,120,685, y el pasivo corriente 2022 por 231,944,180; recalcular el CTN (216,728,221 en 2022 y 96,673,859 en 2023),
   sus variaciones, la razón corriente (1.29) y la prueba ácida (0.87) de 2023, y revisar la interpretación de 6.5.
2. Presentar la utilidad operativa 2022 exacta (31,200,977) en la Tabla 5.
3. Usar una base homogénea de cuentas por cobrar en 8.2 B (o declarar la ruptura de serie en 2023 y en 2024).
4. Unificar el WACC 2023 (3.87 %) entre el cuadro y el texto.
4 bis. En 9.7, presentar «Otras cuentas por cobrar a LP» 2024 por separado de las cuentas por cobrar a relacionadas a LP de
   2025, o documentar la evidencia de que son la misma partida.
5. Documentar que las tasas de interés y la tasa de ISR del WACC provienen de notas del informe auditado que no forman
   parte de los documentos analizados (y que para 2024–2025 no se citan fuentes), y que Ke = ROE es una aproximación.
"""


def _tabla(encabezados: list[str], filas: list[list[str]]) -> str:
    lineas = ["| " + " | ".join(encabezados) + " |", "|" + "|".join("---" for _ in encabezados) + "|"]
    lineas += ["| " + " | ".join(str(c).replace("|", "/") for c in f) + " |" for f in filas]
    return "\n".join(lineas)


def generar(db_path: Path | None = None) -> str:
    connection.init_db(db_path) if db_path else connection.init_db()
    try:
        with connection.render_scope() as s:
            lista = [d for d in datos_todos(s) if d.tiene_datos]
            comparaciones = comparar(lista)
    finally:
        connection.dispose_engine()
    total = Counter(c.estado for c in comparaciones)
    anios = sorted({c.anio for c in comparaciones})
    partes = [
        "# Informe de validación financiera — Alutech 2021–2025",
        "",
        f"Generado automáticamente el {datetime.date.today().isoformat()} con `scripts/generar_informe_validacion.py` a partir "
        "de la base de datos de la aplicación. Compara los resultados que **calcula la aplicación** con los datos originales "
        "de los estados financieros (carpeta `documentos/`) contra los **resultados de referencia** publicados en el "
        "«Trabajo de investigación ANF». Los valores del trabajo nunca se usan como datos ni como resultados calculados.",
        "",
        "## 1. Método y criterios",
        "",
        "Para cada valor numérico del trabajo (registrado en `fuentes/anf/resultados_referencia.json` con su sección, tabla, "
        "unidad y precisión): (1) se toman los datos originales de la BD; (2) se aplica la fórmula implementada "
        "(`calculations/`); (3) se obtiene el resultado calculado; (4) se recupera el valor de referencia; (5) se comparan; "
        "(6) se calcula la diferencia absoluta y (7) la porcentual; (8) se clasifica; (9) se documenta la causa "
        "(`fuentes/anf/observaciones_validacion.json`).",
        "",
        "| Estado | Criterio |",
        "|---|---|",
        "| Coincide | El valor calculado, redondeado (mitad hacia arriba) a la precisión con que el trabajo presenta el dato, es igual al de referencia. |",
        "| Coincidencia por redondeo | No es igual tras redondear, pero la diferencia no supera **una unidad del último decimal presentado** (0.01 en porcentajes y razones con 2 decimales, 0.1 días con 1 decimal, 1 USD en importes enteros). Justificación: el trabajo opera con cifras intermedias ya redondeadas (sumas de días o de aportes al WACC redondeados). |",
        "| Diferencia | La diferencia supera esa tolerancia. Se investiga la causa en el orden de la consigna (extracción, clasificación, conjunto de cuentas, fórmula, base, redondeo, error aritmético, clasificación entre ejercicios). |",
        "| No verificable | La aplicación no puede calcular el valor con los datos disponibles. |",
        "| No aplica | El trabajo declara el indicador no calculable y la aplicación llega a la misma conclusión. |",
        "",
        "Ningún dato original ni ninguna fórmula se modificó para provocar una coincidencia.",
        "",
        "## 2. Resumen",
        "",
        _tabla(["Estado", "Valores comparados"], [[e, str(total[e])] for e in ESTADOS] + [["**Total**", f"**{len(comparaciones)}**"]]),
        "",
        "## 3. Comparación por ejercicio",
        "",
        _tabla(["Ejercicio"] + list(ESTADOS) + ["Total"],
               [[str(a)] + [str(sum(1 for c in comparaciones if c.anio == a and c.estado == e)) for e in ESTADOS]
                + [str(sum(1 for c in comparaciones if c.anio == a))] for a in anios]),
        "",
        "## 4. Comparación por sección del trabajo",
        "",
    ]
    por_seccion = defaultdict(Counter)
    for c in comparaciones:
        por_seccion[(c.referencia.seccion, c.referencia.tabla)][c.estado] += 1
    partes.append(_tabla(["Sección", "Tabla / apartado"] + list(ESTADOS),
                         [[s, t] + [str(cnt[e]) for e in ESTADOS] for (s, t), cnt in por_seccion.items()]))
    partes += ["", "## 5. Comparación por indicador (resultado de la aplicación vs. trabajo ANF)", ""]
    por_indicador = defaultdict(list)
    for c in comparaciones:
        por_indicador[(c.referencia.id, c.referencia.seccion, c.referencia.concepto, c.referencia.unidad, c.referencia.decimales)].append(c)
    filas = []
    for (rid, seccion, concepto, unidad, decimales), lista_c in por_indicador.items():
        for c in lista_c:
            anf = "No calculable" if c.valor_anf is None else _num(c.valor_anf, decimales)
            dif = "" if c.diferencia is None else _num(c.diferencia, decimales)
            filas.append([rid, seccion, concepto, str(c.anio), _app(c.valor_app, decimales), anf, dif, unidad, c.estado])
    partes.append(_tabla(["Ref.", "Secc.", "Indicador / concepto", "Año", "Resultado aplicación", "Resultado trabajo ANF",
                          "Diferencia", "Unidad", "Estado"], filas))
    partes += ["", "## 6. Resultados con diferencias, coincidencias por redondeo y no verificables", ""]
    discrepantes = [c for c in comparaciones if c.estado in (DIFERENCIA, REDONDEO, NO_VERIFICABLE)]
    partes.append(_tabla(["Ref.", "Año", "Concepto", "Aplicación", "Trabajo ANF", "Diferencia", "Dif. %", "Estado", "Categoría de la causa"],
                         [[c.referencia.id, str(c.anio), c.referencia.concepto, _app(c.valor_app, c.referencia.decimales),
                           _num(c.valor_anf, c.referencia.decimales), _num(c.diferencia, c.referencia.decimales),
                           "" if c.diferencia_pct is None else f"{c.diferencia_pct:,.2f}%", c.estado, c.categoria]
                          for c in discrepantes]))
    partes += ["", "Resumen de las discrepancias y de las coincidencias condicionadas a supuestos, por categoría de causa:", ""]
    categorias = Counter((c.categoria or "(sin causa)", c.estado) for c in comparaciones if c.categoria or c.estado in (DIFERENCIA, REDONDEO))
    partes.append(_tabla(["Categoría de la causa", "Estado", "Valores"], [[k[0], k[1], str(v)] for k, v in sorted(categorias.items())]))
    partes += ["", "## 7. Causas identificadas", ""]
    for obs in cargar_observaciones():
        afectados = sorted({f"{c.referencia.id} ({c.anio})" for c in discrepantes
                            if c.referencia.id in obs["referencias"] and (not obs.get("anios") or c.anio in obs["anios"])})
        partes.append(f"**{obs['id']} — {obs.get('categoria', '')}: {obs['tipo']}.** {obs['causa']}")
        partes.append("")
        partes.append(f"Valores afectados: {', '.join(afectados) if afectados else 'ninguno en esta ejecución'}.")
        partes.append("")
    partes += ["## 8. Fórmulas utilizadas por la aplicación", ""]
    partes.append(_tabla(["Indicador", "Fórmula", "Cuentas / rubros", "Unidad", "Sección del trabajo"],
                         [[i.nombre, i.formula, i.insumos, i.unidad, i.seccion_anf] for i in ind.INDICADORES]))
    partes += ["", ANALISIS, "## 10. Fuera del alcance de la comparación", ""]
    partes += [f"- {t}" for t in fuera_de_alcance()]
    partes += ["", f"Coinciden {total[COINCIDE]} valores, {total[REDONDEO]} coinciden por redondeo, {total[DIFERENCIA]} "
               f"presentan diferencias con causa documentada, {total[NO_VERIFICABLE]} no son verificables y {total[NO_APLICA]} "
               "no aplican (no calculables en ambos)."]
    return "\n".join(partes) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--bd", type=Path, default=None)
    parser.add_argument("--salida", type=Path, default=PROYECTO / "INFORME_VALIDACION_FINANCIERA.md")
    args = parser.parse_args(argv)
    args.salida.write_text(generar(args.bd), encoding="utf-8")
    print(f"Escrito: {args.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
