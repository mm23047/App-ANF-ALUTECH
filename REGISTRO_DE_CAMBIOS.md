# Registro de cambios — Adaptación a Alutech 2021–2025

Fecha: 2026-11-02. Rama: `correcciones-auditoria` (cambios sin confirmar en git). La aplicación se adaptó de forma
incremental: no se reemplazó la arquitectura (Python 3.12, Streamlit 1.66, SQLAlchemy, SQLite), no se agregaron
dependencias y no se eliminó ninguna funcionalidad.

## 1. Base de datos (migración v4)

| Archivo | Cambio |
|---|---|
| `database/models.py` | `Account.grupo_analisis` (grupo de análisis, configurable); modelos `FuenteImporte` (documento, página, estado, denominación y cifra impresas, valor registrado) y `DatoComplementario` (totales impresos y datos de otros estados). |
| `database/migrations.py` | Versión 4: agrega la columna y las dos tablas con sus disparadores de ejercicio cerrado. Idempotente, en la misma transacción que los pasos anteriores y con copia previa verificada; no modifica ninguna fila existente. |
| `database/repositories.py` | `create_account(..., grupo_analisis)`; `list_fuentes`, `get_fuente`, `registrar_fuente`, `list_datos_complementarios`, `registrar_dato_complementario` (nunca sobrescriben un dato distinto; registran en el historial). |

## 2. Datos originales y referencias (nuevos)

| Archivo | Contenido |
|---|---|
| `fuentes/alutech/estados_financieros_2021_2025.json` | Datos originales transcritos de `documentos/`: 106 cuentas con su clasificación y grupo, 247 importes con documento, página y denominación original, 61 totales impresos y 13 datos complementarios. Sin resultados del trabajo ANF. |
| `fuentes/anf/resultados_referencia.json` | 736 valores de referencia del trabajo ANF (sección, tabla, métrica, unidad, precisión). Solo los lee el comparador. |
| `fuentes/anf/supuestos_wacc.json` | Tasas de interés e ISR que usa el trabajo en el WACC (no verificables con los documentos). |
| `fuentes/anf/observaciones_validacion.json` | Causas investigadas de las diferencias con el trabajo (OBS‑01 a OBS‑11). |
| `scripts/cargar_alutech.py` | Carga reproducible: respaldo previo, una transacción, idempotente, no sobrescribe, valida los 61 totales antes de confirmar; `--simular` ensaya sobre una copia temporal. |
| `scripts/generar_informe_validacion.py` | Genera `INFORME_VALIDACION_FINANCIERA.md` desde la BD (solo lectura). |

## 3. Cálculos (nuevos, centralizados)

| Archivo | Contenido |
|---|---|
| `calculations/rubros.py` | 73 grupos de análisis (clase y tipo de pasivo para el WACC), 16 rubros y `DatosEjercicio` (agregación por grupo; los totales salen de los cálculos existentes de Balance y Resultados). |
| `calculations/indicadores.py` | 39 indicadores (liquidez, actividad, endeudamiento, rentabilidad, mercado, DuPont al cierre y de la controladora) con fórmula, insumos, unidad, sección del trabajo e interpretación. |
| `calculations/comparativo.py` | Registro único de conceptos, análisis horizontal (rubros, grupos, cuentas; bases cero o negativas sin porcentaje) y vertical comparativo. |
| `calculations/wacc.py` | WACC por el método del trabajo; una fuente de deuda sin tasa deja el WACC como no calculable. |
| `calculations/fuentes_usos.py` | Estado de origen y aplicación de fondos por grupo entre dos ejercicios. |
| `calculations/controles_carga.py` | Totales impresos vs calculados y vigencia de cada importe frente a su fuente. |
| `calculations/comparacion_anf.py` | Comparación con el trabajo: métrica por referencia, clasificación con tolerancia de una unidad del último decimal presentado y causa documentada. |

## 4. Interfaz, reportes y exportaciones

| Archivo | Cambio |
|---|---|
| `components/navigation.py`, `app.py` | 8 páginas nuevas: Datos originales › Trazabilidad y controles; Reportes › Análisis Horizontal 2021–2025, Análisis Vertical comparativo, Indicadores financieros, WACC, Origen y aplicación de fondos, Informe integral; Validación › Comparación con el trabajo ANF. |
| `reports/secciones.py` | Tablas de cada reporte a partir de los cálculos (una sola fuente para pantalla, Excel y PDF). |
| `reports/exportar_secciones.py` | Excel (valores numéricos sin redondear con formato por unidad; textos nunca como fórmula, B‑10) y PDF horizontal con encabezado repetido. |
| `reports/informe_integral.py`, `reports/analisis_alutech.py`, `modules/trazabilidad.py`, `components/secciones_ui.py` | Páginas y descargas. |
| `modules/dashboard.py` | Sección nueva: activo y pasivo corriente, CTN, razón corriente, prueba ácida, costo de ventas, margen neto, endeudamiento, ROE y gráficos 2021–2025. Lo existente no cambia. |
| `modules/accounts.py` | Selector del grupo de análisis al crear o editar una cuenta (permitido aunque la cuenta tenga importes: no altera los estados). |

## 5. Pruebas

| Archivo | Cambio |
|---|---|
| `tests/test_alutech.py` (nuevo) | 50 pruebas: carga (totales, idempotencia, no sobrescritura, simulación, signos, ceros de 2021), cálculos verificados a mano con las cifras de los documentos, WACC, fuentes y usos, horizontal, clasificación y resultado completo de la comparación, exportaciones, migración v3→v4 y las 24 páginas con los datos de Alutech. |
| `tests/test_fase1_migracion.py` | El esquema vigente tiene 19 disparadores (13 + 6 de la v4). |
| `tests/test_fase4.py` | `scripts` es un paquete local. |
| `tests/test_fase5_integracion.py` | La aplicación tiene 24 páginas (16 + 8). |
| `tests/test_fase4.py` | La comprobación de los 19 importes en cero de 2021 en la BD real se limita a las cuentas del catálogo estándar (2021 ya tiene también los importes de Alutech). |

Resultado de la suite completa tras la adaptación (ejecutada el 2026-11-02): **512 aprobadas y 2 fallidas de 514**.
Las 2 fallidas son F01 y F03 de `test_auditoria.py`, que fallan por diseño desde las fases anteriores (esperan que se
invierta el signo de un importe, lo que la convención aprobada prohíbe). Las pruebas no modificaron `data/financiera.db`
(su SHA-256 se verifica antes y después).

## 6. Datos incorporados a `data/financiera.db`

- Migración a la versión 4 con copia previa `data/backups/financiera_pre_migracion_v3_20261102_214805_965908.db` y copia
  previa a la carga `data/backups/financiera_pre_carga_alutech_20261102_214805_952056.db`.
- 106 cuentas, ejercicios 2022–2025 (2021 ya existía), 247 importes, 247 fuentes y 74 totales/datos complementarios;
  61 de 61 totales impresos coinciden. Historial: 678 registros nuevos en un solo lote.
- No se modificó ningún dato previo: los 19 importes en cero de 2021, los datos de la empresa y el estado de los estados
  financieros 2021 quedan como estaban.

## 7. Decisiones técnicas

1. **Dos familias de cuentas** (combinados 2021–2023 y consolidados 2024–2025) relacionadas por grupos de análisis, en
   lugar de forzar una sola cuenta por concepto: conserva la denominación original y evita confundir cambios de
   presentación con variaciones reales.
2. **Saldos al cierre** en todos los indicadores nuevos (criterio del trabajo; no hay balance 2020). El reporte DuPont
   existente (saldos promedio) se conserva sin cambios.
3. **Convención de signos** sin excepciones: «Otros Ingresos (Gastos)» se registra en dos cuentas según su efecto en cada
   año.
4. **Utilidad de la controladora 2021–2023** desde el estado de cambios en el patrimonio (único estado que la informa en
   los tres años); en 2023 difiere del estado de resultados y se documenta.
5. **Supuestos del WACC** en un archivo separado y marcado como no verificable; el costo del patrimonio se calcula (ROE).
6. **Tolerancia de comparación**: una unidad del último decimal que presenta el trabajo; toda diferencia mayor queda como
   «Diferencia» con su causa investigada. Ningún dato ni fórmula se ajustó para provocar coincidencias.

## 8. Revisión final (2026-11-02)

**Respaldo previo:** `data/backups/financiera_pre_revision_final_20261102_220519_194293.db` (verificado: integridad y
conteo de filas). Registros afectados, identificados antes de modificar: la fila de `company` (3 campos) y la cuenta
`CN1202` (solo el campo `grupo_analisis`). Ningún importe, fuente, total impreso ni ejercicio se modificó.

| Punto | Cambio | Dónde |
|---|---|---|
| 19 importes en cero de 2021 | Solo diagnóstico, **sin modificar** (ver §9) | — |
| Datos de la empresa | Nombre legal «Alutech, S. A. de C. V. y subsidiarias – División Acero», nombre comercial «Alutech – División Acero», país «Honduras». Actividad, moneda y año inicial sin cambios. Con historial (3 registros EDITAR). | BD (`company`) |
| Equivalencia de CxC a LP | `CN1202` «Otras cuentas por cobrar a LP» (2024) pasa de `CXC_RELACIONADAS_LP` a `OTRAS_CXC_LP`: ni el estado de 2024 ni el informe PCR (dic‑24: relacionadas no corrientes 0.0) la identifican como partes relacionadas. Denominación e importe sin cambios. Efecto: horizontal por grupos y origen y aplicación de fondos 2024–2025 (total 2025 vs 2024: 408,447,177); ningún indicador ni el vertical. | BD (historial), `fuentes/alutech/…json`, `MAPEO_FINANCIERO_ALUTECH.md` |
| Diferencias con el trabajo | Cada causa clasificada en: error del trabajo académico, error de extracción, error de clasificación, diferencia de fórmula, diferencia de redondeo o supuesto no verificable. Nuevas OBS‑12 (clasificación de CxC LP en 9.7) y OBS‑13 (WACC: coincidencias condicionadas a tasas e ISR no verificables). Comparación: 672 / 6 / 43 / 0 / 15. | `fuentes/anf/observaciones_validacion.json`, `calculations/comparacion_anf.py`, `reports/secciones.py`, `scripts/generar_informe_validacion.py`, `INFORME_VALIDACION_FINANCIERA.md` |
| F01 y F03 | Actualizadas para exigir la convención aprobada (sin inversión silenciosa, aviso, bandera SIGNO ATÍPICO) y que la captura correcta dé 700 y 400. El código no cambia: su comportamiento es el aprobado. | `tests/test_auditoria.py` |
| Pruebas | Nueva: los indicadores se recalculan al cambiar el mapeo. Actualizadas: conteos de la comparación, total de fuentes y usos 2025, datos de la empresa en la BD real (la corrección de la fase 4 sigue en el historial) y encabezados de Excel/PDF. | `tests/test_alutech.py`, `tests/test_fase4.py` |

**Suite completa tras la revisión: 515 aprobadas de 515.**

**Validación de integridad (copia de la BD real):** 5 ejercicios; 247/247 importes iguales al documento y a su fuente
registrada; 61/61 totales impresos conciliados; 24/24 páginas sin excepciones (Dashboard con 2021–2025 y el nuevo
nombre); en las 11 hojas del Excel y en el PDF del informe integral aparece el nuevo nombre; los 38 valores del capital de
trabajo son iguales en Excel y PDF; ciclo de copia de seguridad y restauración verificado.

## 9. Importes en cero de 2021: diagnóstico y corrección autorizada

**19 importes en cero de 2021 (diagnóstico).** Son las 19 cuentas de balance del catálogo estándar de la plantilla
(1001–1104, 2001–2102, 3001–3005), creadas en un solo guardado manual del formulario «Ingreso de datos › Balance General»
el 2026-11-01 a las 15:45:04, un minuto después de crear la empresa y el ejercicio 2021 (historial 34–52); luego el
Balance 2021 se marcó REVISADO. No provienen de ningún documento, no son saldos iniciales (la tabla de saldos iniciales
está vacía) ni datos históricos: son registros de prueba sin utilidad financiera. Suman 0, por lo que no alteran ningún
total, indicador ni comparación. Solo uno tiene efecto: «3004 Resultado del ejercicio» = 0 hace que el control de
conciliación compare 0 con la utilidad neta de 2021 (68,602,739) y marque el Balance y los Resultados de 2021 como
«SIN CONCILIAR» (y el control del DuPont por promedios). En los estados de 2021 el resultado del año está dentro de
«Utilidades acumuladas» (CB3106), sin línea separada, igual que en 2022 y 2023, que quedan «sin datos para conciliar»
(no es bandera). Las otras 18 solo agregan líneas en cero a los reportes de 2021.

La cuenta 3004 no debe excluirse de la validación (la regla de conciliación es correcta para cualquier ejercicio que sí
presente el resultado por separado, como 2024 y 2025). Corrección menos destructiva propuesta: borrar **solo** el
importe 0 de «3004 Resultado del ejercicio» de 2021 con «Modificación de datos › Borrar importe» (queda en el historial y
en el respaldo); alternativa: borrar los 19. No se ejecuta sin autorización expresa, conforme a la decisión del
2026-11-01 de conservarlos.

**Ejecutado con autorización del usuario (2026-11-02):** se borró únicamente el importe 0.00 de «3004 Resultado del
ejercicio» de 2021 (balance_entry id 18) con `delete_entry` dentro de un lote, el mismo mecanismo que «Modificación de
datos › Borrar importe». Verificaciones: respaldo previo íntegro (`financiera_pre_revision_final_20261102_220519_194293.db`);
el registro era de 2021 y valía exactamente 0.00; el historial registra la operación (ELIMINAR, 0.00 → vacío, con lote);
la cuenta 3004 sigue ACTIVA en el catálogo y disponible para cualquier ejercicio; los otros 18 ceros, las 106 cuentas,
las 247 fuentes, los 74 totales y datos complementarios, los 5 ejercicios y la empresa no cambiaron. La conciliación de
2021 ya no compara 0 con 68,602,739 (incluida en «Utilidades acumuladas»): queda sin datos para conciliar, como 2022 y
2023, y los reportes de Balance y Resultados 2021 son DEFINITIVOS. La comparación con el trabajo no cambia (672 / 6 / 43
/ 0 / 15). Se actualizó `tests/test_fase4.py` (la BD real tiene ahora 18 ceros y el borrado en el historial). Suite:
**515 aprobadas de 515**.

## 10. Fase 2: corrección del análisis horizontal en el trabajo académico (2026-11-03)

**Autorización:** exclusivamente el análisis horizontal (hallazgos D‑01 a D‑08 y D‑19 de `AUDITORIA_DOCUMENTAL_TRABAJO_ANF_FASE2.md`). Sin commit. Base: HEAD `4506ed8`.

**Archivo modificado:** `Trabajo de investigación ANF.md`, SHA-256 `bcfeb15d9278dc55f974e572735e138eb23080d16bb22dd52cbf2c31ae78ece4` → `5d5e316425292d83e65a436a8a167239dfb1e0daf669442bd20828b23156b80c`. No se modificó el PDF, que ahora **no refleja** estas correcciones.

**Respaldo:** `C:\Users\estua\Documents\ANF\respaldos_appfinanciera\fase2_horizontal_20261103_165827\` (MD y PDF originales, con hashes verificados).

| Ubicación (línea original) | Concepto | Antes | Después |
|---|---|---|---|
| Tabla 3 (L498) | Activo corriente 2023 | 541,094,544 | 429,794,544 |
| Tabla 3 (L498) | Var. AC 2022–2023 | +92,422,143 / +20.60 % | −18,877,857 / −4.21 % |
| Tabla 3 (L499) | Pasivo corriente 2022 | 231,914,180 | 231,944,180 |
| Tabla 3 (L499) | Var. PC 2021–2022 | +25,940,950 / +12.59 % | +25,970,950 / +12.61 % |
| Tabla 3 (L499) | Pasivo corriente 2023 | 342,120,685 | 333,120,685 |
| Tabla 3 (L499) | Var. PC 2022–2023 | +110,206,505 / +47.52 % | +101,176,505 / +43.62 % |
| Tabla 4 (L511) | Var. AC 2023–2024 | −108,322,866 / −20.02 % | +2,977,134 / +0.69 % |
| Tabla 4 (L512) | Var. PC 2023–2024 | +20,845,530 / +6.09 % | +29,845,530 / +8.96 % |
| Tabla 5 (L527) | Utilidad operativa 2022 | 31,200,000\* | 31,200,977 (variaciones sin cambio: −69.88 % y +43.23 %) |
| Tablas 6 y 7 | CTN 2022 | +216,758,221 | +216,728,221 |
| Tablas 6 y 7 | Var. CTN 2022 | +38,849,904 / +21.84 % | +38,819,904 / +21.82 % |
| Tablas 6 y 7 | CTN 2023 | +198,973,859 | +96,673,859 |
| Tablas 6 y 7 | Var. CTN 2023 | −17,784,362 / −8.20 % | −120,054,362 / −55.39 % |
| Tablas 6 y 7 | Var. CTN 2024 | −129,168,396 / −64.92 % | −26,868,396 / −27.79 % |
| Tabla 6 | RC 2023 / PA 2023 | 1.58x / 1.17x | 1.29x / 0.87x |

Las mismas cifras de AC y PC se corrigieron en cada aparición de las Tablas 4, 6 y 7.

**Texto y presentación:** 6.5 puntos 1, 2 y 3 (incluido el título del punto 3, porque el activo corriente subió en 2024); 6.6 («comparaciones interanuales»); 6.8; título de 6.4 y su entrada del índice (L83; el ancla no cambia); errata «2021-20252» (L489 y L517). Notas nuevas: fuente y cambio de estados combinados a consolidados (6.2); base de cuentas por cobrar (Tablas 3 y 4); definiciones y derivaciones (Tabla 5).

**Verificación:** 93 cifras impresas halladas en los documentos originales (2024 por lectura de la imagen); 240 celdas de las Tablas 3 a 7 recalculadas sin discrepancias; 31 importes, 16 porcentajes y las razones del texto de 6.5–6.8 respaldados; sin cifras erróneas residuales en el documento. Fuera de la sección 6 solo cambió la L83; las secciones 1–5 (salvo esa línea), 6.1, 6.3 y de la 7 al final son idénticas. Desde la sección 7, las líneas del Markdown aumentan en 14 respecto de las citadas en los informes de auditoría.

**Sin modificar por estar fuera de la autorización:** `fuentes/anf/resultados_referencia.json`, `fuentes/anf/observaciones_validacion.json` e `INFORME_VALIDACION_FINANCIERA.md`, que siguen reflejando la versión anterior del trabajo; la aplicación, la base de datos y el resto del documento.

## 11. Fase 2: actualización del PDF del trabajo académico (2026-11-03)

**Autorización:** actualizar `Trabajo de investigación ANF.pdf` para que coincida con el Markdown corregido. Sin commit. Siguen pendientes, para una fase independiente, `fuentes/anf/resultados_referencia.json`, `fuentes/anf/observaciones_validacion.json`, `INFORME_VALIDACION_FINANCIERA.md` y las pruebas de la aplicación.

**Procedimiento de exportación identificado:** el proyecto no tiene ninguno. El PDF original indica como productor «Skia/PDF m159 Google Docs Renderer», es decir, se exportó desde Google Docs, y el Markdown tiene el formato de una exportación de ese documento. No hay scripts del trabajo en el repositorio. No se pudo consultar Google Drive (el conector requiere volver a iniciar sesión), por lo que no se confirmó si el documento fuente sigue disponible, y **ese documento, si existe, no tiene estas correcciones**.

**Procedimiento aplicado:** reconstrucción parcial del PDF original con PyMuPDF, instalado solo en el directorio temporal de la sesión, no en el proyecto. Las páginas 1, 3–20 y 29–83 originales se conservaron. Las páginas 21–28 se recompusieron línea por línea y fila por fila desde el propio PDF, con el mismo tamaño de página, márgenes, Arial y tablas. Solo se reescribieron las 45 celdas y los párrafos que cambiaron en el Markdown y se añadieron sus notas. En la página 2 se sustituyó la línea 6.4 del índice.

| Dato | Antes | Después |
|---|---|---|
| SHA-256 del PDF | `e0776984035f86911afe…` | `14be92f6df2d1e1a406560b8dcea6feb5a2926dd7401e093f1537224160a2b1f` |
| Páginas | 83 | 84 (las notas nuevas añaden una página; la sección 7 empieza en la 30) |
| Tamaño | 8,233,187 bytes | 8,812,834 bytes |
| Markdown | `5d5e316425292d83…` | Sin cambios |

**Respaldo:** `C:\Users\estua\Documents\ANF\respaldos_appfinanciera\fase2_pdf_20261103_171131\`.

**Verificación:** 74 de las 75 páginas no reconstruidas son idénticas en texto e imagen (la restante es la página 2, modificada a propósito); 240 de 240 celdas de las Tablas 3 a 7 y 17 de 17 párrafos coinciden con el Markdown; sin cifras antiguas en todo el PDF; 52 de 52 enlaces del índice y los 56 marcadores llevan a la página correcta (2 marcadores sin título ya existían en el original); revisión visual de las páginas 2 y 21–29.

**Limitaciones:**
- La línea 6.4 del índice se imprime a 10.1 pt en lugar de 11 pt para caber en una línea.
- **Los números de página impresos en el índice se conservan iguales al Markdown** y, desde 6.5, ya no coinciden con la paginación real: la diferencia es de +1 en la mayoría de las entradas y de +3 o +4 desde 9.3, porque el índice ya estaba desfasado (D‑37). Los enlaces y marcadores sí llevan a la página correcta.
- Las referencias a páginas del PDF en los informes de auditoría aumentan en 1 desde la sección 7.

## 12. Análisis vertical y DuPont alineados con el trabajo ANF (2026-11-05)

**Autorización:** fase 2 de la auditoría metodológica, decisiones D-1 a D-6. Sin commit. Sin cambios en la base de datos, en `fuentes/` ni en el trabajo académico.

**Respaldo:** `C:\Users\estua\Documents\ANF\respaldo_fase2_vertical_dupont_20261105\`, con manifiesto SHA-256.

| Archivo | Cambio |
|---|---|
| `calculations/dupont.py` | Única fuente del modelo, con saldos al cierre: `factores_dupont`, `factores_total` y `factores_controladora`. Se eliminan los promedios y los saldos iniciales. El resultado incluye RSA, comprobación directa y enfoque de la controladora |
| `calculations/indicadores.py` | `_maf`, `_roa_dupont`, `_roe_dupont` y los de la controladora delegan en `calculations/dupont.py`. Rotación, margen, ROA y ROE directos no cambian |
| `calculations/banderas.py` | Se elimina APROXIMADO. «Sin datos para conciliar» ya no se presenta como SIN CONCILIAR |
| `calculations/vertical_analysis.py` | Los costos, gastos e impuestos del Estado de Resultados tienen porcentaje negativo. El importe y `efecto` no cambian |
| `reports/dupont_report.py`, `reports/pdf_export.py`, `reports/excel_export.py` | Enfoque total y de la controladora por separado, con las filas comunes de `calculations/dupont.py`. Excel: la fórmula de control del vertical incluye el signo |
| `reports/vertical_report.py`, `reports/secciones.py`, `modules/dashboard.py` | Textos, notas y estados coherentes con lo anterior. El Informe integral lee los factores de la fuente única |
| `modules/data_entry.py` | La página Saldos iniciales se conserva y deja de depender del cálculo DuPont |
| `tests/` | Pruebas y `caso_controlado.json` actualizados al criterio del trabajo, sin eliminar casos. Nuevos: `test_fase8_vertical_dupont.py` y `humo_vertical_dupont.py` |
| `README.md`, `MATRIZ_ADAPTACION.md` | Referencias a saldos promedio y al carácter aproximado de 2021 |

## 13. Auditoría integral conforme a la rúbrica (2026-11-05)

**Informe:** `INFORME_AUDITORIA_RUBRICA_ANF.md`; matriz completa en `MATRIZ_CONCORDANCIA_ANF.md`. Sin commit. Sin cambios en la base de datos, en el trabajo académico ni en `fuentes/alutech/`.

**Respaldo:** `C:\Users\estua\Documents\ANF\respaldos_appfinanciera\rubrica_integral_20261105\`, con manifiesto SHA-256.

| Archivo | Cambio |
|---|---|
| `calculations/comparativo.py`, `reports/secciones.py`, `reports/analisis_alutech.py`, `components/navigation.py`, `app.py` | Reportes de análisis horizontal del Balance y de Resultados en el menú: Tablas 3 a 7 y comparación de dos ejercicios. El grupo de otros no operativos conserva su signo |
| `reports/vertical_report.py`, `reports/dupont_report.py` | Comparativos de los ejercicios (7.1, 7.2, 9.5 y 9.6), sin cambiar el cálculo |
| `calculations/indicadores.py`, `reports/indicadores_financieros.py` | Cobertura de pagos fijos según 8.3 C; base financiera, EPS y descargas por apartado |
| `reports/exportar_secciones.py` | PDF con anchos medidos, sin cifras partidas; Excel con anchos y formatos con signo |
| `calculations/validation.py`, `calculations/vertical_analysis.py`, `reports/balance_report.py`, `reports/pdf_export.py`, `reports/excel_export.py`, `components/tables.py` | Los importes 0.00 de cuentas sin mapear no se presentan si el grupo ya tiene cuentas mapeadas; siguen en la base y en Modificación de datos |
| `components/secciones_ui.py`, `.streamlit/config.toml` | Cifras a la derecha, etiquetas completas, exportación al pulsar el botón y barra mínima |
| `fuentes/anf/resultados_referencia.json`, `fuentes/anf/observaciones_validacion.json` | 37 referencias al día con la versión vigente y 5 nuevas de 8.3 C; 6 observaciones obsoletas pasan a una sección histórica. Validación: 714, 6, 6 y 15 |
| `tests/` | Nuevos: `test_fase9_rubrica.py`, `concordancia_documento.py` y `humo_horizontal.py`. Ajustadas 7 pruebas en 5 archivos, ninguna eliminada. Suite: 656 de 656 |

## 14. Unificación metodológica con el documento ANF (2026-11-05)

**Informe:** `INFORME_UNIFICACION_METODOLOGICA_ANF.md`. Sin commit. Sin cambios en la base de datos, en el trabajo académico ni en `fuentes/alutech/`.

**Respaldo:** `C:\Users\estua\Documents\ANF\respaldos_appfinanciera\unificacion_metodologica_20261105\`, con manifiesto SHA-256.

| Archivo | Cambio |
|---|---|
| `calculations/indicadores.py` | Ciclo operativo y CCE con operandos a 2 decimales, como escribe 9.3, con una regla general. Interpretaciones con la misma cifra que las tablas |
| `components/money.py`, `reports/secciones.py` | Redondeo único, mitad hacia arriba y una sola vez |
| `reports/secciones.py`, `reports/indicadores_financieros.py` | Tabla de las dos bases de cuentas por cobrar, en pantalla, PDF y Excel |
| `calculations/comparacion_anf.py`, `fuentes/anf/*.json` | Estado «Resultado derivado» para 8.3 C y observaciones OBS-07, 08, 09 y 14. Validación: 711, 4, 5, 6 y 15. Ningún valor de referencia cambió |
| `tests/` | Nuevo `test_fase10_metodologia.py`; expectativas ajustadas, ninguna prueba eliminada. Suite: 695 de 695 |

## 15. Correcciones del análisis horizontal (2026-11-05)

**Informe:** `INFORME_IMPLEMENTACION_ANALISIS_HORIZONTAL.md`. Autorizadas R-1, R-3, R-4, R-5, R-11 a R-14 y las decisiones D-1 a D-4. Sin commit. Sin cambios en la base de datos, en `documentos/` ni en `fuentes/`. R-15 quedó revisada y sin insertar; R-2, R-6, R-7, R-8, R-9, R-10 y R-16 esperan autorización.

**Respaldo:** `C:\Users\estua\Documents\ANF\respaldos_appfinanciera\horizontal_20261105\`.

| Archivo | Cambio |
|---|---|
| `calculations/comparativo.py`, `calculations/rubros.py` | Un grupo sin cuentas queda sin dato; estados de comparabilidad deducidos de los datos, sin excepciones por año; observación del capital social |
| `reports/secciones.py`, `reports/analisis_alutech.py` | Marcas † y notas por fila; cambio de signo en las Tablas 6 y 7; descargas con el nivel elegido |
| `calculations/indicadores.py`, `reports/indicadores_financieros.py` | «Alternativa analítica» en lugar de «homogénea» (solo texto) |
| `Trabajo de investigación ANF.md`, `.pdf` | 6.3, notas de las Tablas 4 a 7, Tabla 5 (continuación); PDF: páginas 21 a 29 recompuestas e índice corregido; 84 páginas |
| `tests/` | Nuevos `test_fase11_horizontal.py` y `humo_exportes_nivel.py`; `concordancia_documento.py` ignora la llamada †. Ninguna prueba eliminada. Suite: 740 de 740 |
