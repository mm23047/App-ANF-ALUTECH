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
