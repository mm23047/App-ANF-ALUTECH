# Matriz de adaptación — Trabajo ANF ↔ módulos de la aplicación

Relación entre cada requerimiento del «Trabajo de investigación ANF» (y de la consigna de adaptación) y el lugar donde la
aplicación lo resuelve. «Prueba» remite a `tests/test_alutech.py` salvo que se indique otro archivo. El resultado de cada
comparación está en `INFORME_VALIDACION_FINANCIERA.md`.

## 1. Requerimientos del trabajo ANF

| Requerimiento (sección del trabajo) | Datos que usa | Cálculo | Pantalla | Exportación | Prueba | Resultado frente al trabajo |
|---|---|---|---|---|---|---|
| Estados financieros 2021–2025 (5.1, 6.2) | `fuentes/alutech/estados_financieros_2021_2025.json` → BD | `calculations/balance_sheet.py`, `income_statement.py` | Reportes › Balance General / Estado de Resultados; Informe integral (estados originales) | PDF y Excel por ejercicio (existentes) e informe integral | `test_cada_importe_registrado_es_el_del_documento`, `test_balance_cuadra_y_totales_coinciden_con_los_impresos` | Totales iguales a los impresos (61/61) |
| Análisis horizontal: rubros y totales (6.3, 6.4, Tablas 3–5) | Totales y rubros | `calculations/comparativo.py` (`variacion`, `horizontal_conceptos`) | Reportes › Análisis Horizontal 2021–2025 (nivel «rubros») | Excel / PDF de la página e informe integral | `test_variacion_controla_base_cero_y_negativa` | Coincide salvo cifras de 2022–2023 del trabajo que no corresponden a los documentos (OBS‑01 a 06) |
| Análisis horizontal por grupo y por cuenta (6.2: comparabilidad entre presentaciones) | Grupos de análisis | `horizontal_grupos`, `horizontal_cuentas` | Misma página (niveles «grupos» y «cuentas») | Ídem | Prueba de páginas | — (ampliación para la trazabilidad) |
| Capital de trabajo, razón corriente, prueba ácida (5.6 a–c, 6.5, 8.1, Tablas 6–7) | Totales, inventarios | `calculations/indicadores.py` (`ctn`, `razon_corriente`, `prueba_acida`) | Indicadores › Liquidez y Capital de trabajo; Dashboard | Ídem | `test_indicador_calculado_a_mano` | 8.1: coincide; Tablas 6–7: diferencias por OBS‑01 a 05 |
| Razón de efectivo (5.6 d) | Efectivo | `razon_efectivo` | Indicadores › Liquidez | Ídem | — | El trabajo no presenta valores (sin referencia) |
| Razón de tesorería (9.1) | Efectivo + inversiones corrientes | `razon_tesoreria` | Indicadores › Liquidez; Capital de trabajo | Ídem | `test_indicador_calculado_a_mano` | Coincide |
| Fondo de maniobra CP y LP, capitales permanentes (9.2) | Totales | `ctn`, `fondo_maniobra_lp`, `capitales_permanentes` | Indicadores › Liquidez | Ídem | Ídem | Coincide |
| Rotación de inventarios, PPI/EPI (8.2 A, 9.3) | Costo de ventas, inventarios | `rotacion_inventarios`, `ppi` | Indicadores › Actividad | Ídem | Ídem | Coincide |
| Rotación de CxC, PPC (8.2 B, 9.3) | Ingresos, CxC comerciales (línea presentada / comerciales y otras) | `rotacion_cxc`, `ppc`, `rotacion_cxc_total`, `ppc_total` | Indicadores › Actividad | Ídem | Ídem | 9.3 coincide; 8.2 B 2023 difiere por base (OBS‑07) |
| PPP, ciclo operativo, CCE (5.6 i–k, 8.2 C, 9.3) | CxP comerciales, costo de ventas | `ppp`, `ciclo_operativo`, `cce` | Indicadores › Actividad (gráfico del ciclo) | Ídem | Ídem | Coincide (3 por redondeo) |
| Rotación de activos (8.2 D) | Ingresos, activo total | `rotacion_activos` | Indicadores › Actividad | Ídem | Prueba de comparación | Coincide |
| Endeudamiento, PC/pasivo, deuda‑capital (8.3 A, D) | Totales | `endeudamiento`, `pc_sobre_pasivo`, `deuda_capital` | Indicadores › Endeudamiento; Dashboard | Ídem | Ídem | Coincide (1 por redondeo) |
| Razón de cargos de interés fijo (8.3 B) | Utilidad de operación, gastos financieros netos | `cobertura_intereses` (+ `cobertura_intereses_bruta` complementaria) | Indicadores › Endeudamiento | Ídem | `test_indicador_calculado_a_mano` | Coincide |
| Cobertura de pagos fijos (8.3 C) | No disponibles | `cobertura_pagos_fijos` («no calculable») | Indicadores › Endeudamiento | Ídem | `test_indicadores_de_mercado_no_calculables` | Sin valor en el trabajo |
| Márgenes, ROA, ROE (8.4 A–C, E–F) | Utilidades, activo, patrimonio | `margen_*`, `roa`, `roe` | Indicadores › Rentabilidad; Dashboard | Ídem | Ídem | Coincide |
| EPS, P/E, M/L (8.4 D, 8.5) | No disponibles | `eps`, `per`, `ml` («no calculable») | Indicadores › Razones de mercado | Ídem | Ídem | No aplica (ambos no calculables) |
| EBITDA (6.7) | Utilidad de operación + D&A (ER 2024–2025; flujo de efectivo 2021–2023) | `ebitda` | Indicadores › Rentabilidad | Ídem | Ídem | Coincide (2025) |
| Análisis vertical del ER y del BG (7.1, 7.2) | Líneas con signo; bases ingresos y activo total | `vertical_comparativo` | Reportes › Análisis Vertical comparativo 2021–2025 (además de los verticales por ejercicio existentes) | Ídem | Prueba de comparación | Coincide (115 de 115) |
| DuPont total (9.5, 9.6) | Utilidad, ingresos, activo, patrimonio al cierre | `margen_neto`, `rotacion_activos`, `roa_dupont`, `maf`, `roe_dupont` | Indicadores › DuPont (saldos al cierre) | Ídem | Ídem | Coincide |
| DuPont de la controladora (9.6) | Utilidad atribuible (ECP 2021–2023; supuesto 2024–2025) y patrimonio sin no controladoras | `*_controladora` | Indicadores › DuPont | Ídem | `test_indicador_calculado_a_mano` | Coincide |
| WACC (9.4) | Balance por cuenta; Ke = ROE; tasas e ISR **supuestos** del trabajo (`fuentes/anf/supuestos_wacc.json`) | `calculations/wacc.py` | Reportes › WACC (resumen, supuestos y detalle por año) | Ídem | `test_wacc_2021_a_mano`, `test_wacc_sin_tasa_supuesta_no_se_calcula` | Coincide con supuestos no verificables (OBS‑13); 2023 por redondeo (3.88 vs 3.87, OBS‑11) |
| Origen y aplicación de fondos (9.7) | Balances de dos ejercicios por grupo | `calculations/fuentes_usos.py` | Reportes › Origen y aplicación de fondos (cualquier par consecutivo) | Ídem | `test_fuentes_y_usos_cuadran_y_reproducen_los_totales_del_trabajo` | 2023 vs 2022 coincide (209,290,574). 2025 vs 2024: 3 diferencias por la clasificación de «Otras cuentas por cobrar a LP» que el trabajo trata como relacionadas (OBS‑12); total de la aplicación 408,447,177 |
| Comparación Alutech vs Ternium (10) | Ternium: fuente externa | — | Validación (fuera de alcance) | — | — | Solo se verifican las cifras de Alutech |
| Comparación con el trabajo (consigna, fase 6) | Referencias del trabajo | `calculations/comparacion_anf.py` + observaciones | Validación › Comparación con el trabajo ANF | Excel / PDF; `INFORME_VALIDACION_FINANCIERA.md` (script) | `test_comparacion_completa_con_el_trabajo`, `test_clasificacion_de_la_comparacion` | 672 coinciden, 6 por redondeo, 43 diferencias con causa y categoría documentadas, 15 no aplica |

## 2. Requerimientos de datos y trazabilidad (consigna, fases 3 y 4)

| Requerimiento | Implementación | Prueba |
|---|---|---|
| Catálogo con denominaciones originales | 106 cuentas `CB…`/`CN…` (`fuentes/alutech/…json`, `MAPEO_FINANCIERO_ALUTECH.md`) | `test_todas_las_cuentas_tienen_un_grupo_valido` |
| Mapeo configurable (nombre original, normalizado, categoría, grupo, indicadores) | `account.grupo_analisis` (migración v4), `calculations/rubros.py`, `indicadores_de_grupo`; editable en Catálogo de cuentas | `test_migracion_v3_a_v4_conserva_todo` |
| Fuente de cada importe | Tabla `fuente_importe` (documento, página, estado, denominación y cifra impresas, valor registrado) | `test_control_de_fuente_detecta_un_importe_editado` |
| Controles de carga (totales) | Tabla `dato_complementario` (61 totales impresos) y `calculations/controles_carga.py`; página Datos originales › Trazabilidad | `test_carga_crea_todo_y_cuadra_los_61_totales_impresos` |
| Carga reproducible, sin duplicar ni sobrescribir | `scripts/cargar_alutech.py` (respaldo previo, todo o nada, idempotente, `--simular`) | `test_la_carga_es_idempotente`, `test_la_carga_no_sobrescribe_…`, `test_la_simulacion_no_modifica_la_bd`, `test_un_signo_impreso_incoherente_detiene_la_carga` |
| Respaldo y migración segura | Migración v4 con copia previa verificada; copia `pre_carga_alutech` antes de escribir | `test_migracion_v3_a_v4_conserva_todo`, `tests/test_fase1_migracion.py` |
| Datos originales separados de resultados calculados y de referencias | BD (originales) / `calculations/` (calculados, no se almacenan) / `fuentes/anf/` (referencias) | `test_los_valores_del_trabajo_no_entran_en_los_calculos` |
| Fórmulas centralizadas | `calculations/indicadores.py`, `comparativo.py`, `wacc.py`, `fuentes_usos.py`; reportes vía `reports/secciones.py` | Mismas secciones en pantalla, Excel y PDF |

## 3. Funcionalidades existentes (consigna, fase 2)

Verificadas en el código y con la suite de pruebas después de la adaptación.

| Funcionalidad | Módulo | Estado tras la adaptación |
|---|---|---|
| Administración de la empresa | `modules/company.py` | Conservada (datos sin cambios) |
| Catálogo de cuentas | `modules/accounts.py` | Conservado; ahora permite asignar el grupo de análisis |
| Gestión de ejercicios (crear, cerrar, reabrir, eliminar vacíos) | `components/navigation.py`, `modules/data_edit.py` | Conservada; el cierre también protege las tablas nuevas |
| Captura de Balance y Resultados | `modules/data_entry.py` | Conservada |
| Saldos iniciales | `modules/data_entry.py` | Conservada |
| Importación de Excel | `modules/excel_import.py` | Conservada (plantilla con el catálogo vigente) |
| Edición de información | `modules/data_edit.py` | Conservada; una edición de un importe cargado se detecta en el control de trazabilidad |
| Historial de modificaciones | `modules/history.py` | Conservado; registra también las cuentas, importes, fuentes y totales de la carga |
| Dashboard | `modules/dashboard.py` | Conservado y ampliado (capital de trabajo, liquidez, rentabilidad 2021–2025) |
| Reportes de Balance y Resultados | `reports/balance_report.py`, `income_report.py` | Conservados |
| Análisis vertical del BG y del ER (por ejercicio) | `reports/vertical_report.py` | Conservados; se agrega el vertical comparativo |
| Análisis DuPont (saldos promedio) | `reports/dupont_report.py` | Conservado; el DuPont al cierre del trabajo se agrega en Indicadores |
| Exportación PDF y Excel | `reports/pdf_export.py`, `excel_export.py` | Conservadas; nuevas exportaciones en `reports/exportar_secciones.py` |
| Copias de seguridad y restauración | `modules/backup.py`, `database/backup_utils.py` | Conservadas |
| Análisis horizontal | — | **No existía** en la aplicación: se implementó |
| Indicadores de liquidez, actividad, endeudamiento y rentabilidad | — | **No existían** (solo DuPont): se implementaron |
| WACC, origen y aplicación de fondos, comparación con el trabajo, trazabilidad | — | **No existían**: se implementaron |
