# Auditoría e implementación conforme a la rúbrica y al documento ANF

**Alutech, S. A. de C. V., y subsidiarias – División Acero · 2021–2025**
Fecha: 2026-11-05. Rama: `correcciones-auditoria`. Sin commit. Anexo: [MATRIZ_CONCORDANCIA_ANF.md](MATRIZ_CONCORDANCIA_ANF.md), con los 837 valores.

> **Nota de actualización (2026-11-05).** Este informe describe el estado anterior a la unificación metodológica y se conserva como registro. Lo vigente está en `INFORME_UNIFICACION_METODOLOGICA_ANF.md`; `AUDITORIA_FINAL_REFERENCIAS_ANF.md` corrige varias de sus afirmaciones. En especial: las cifras del ciclo operativo de 9.3 sí salen del procedimiento escrito del documento; ya no son 9 sino 5 las celdas que difieren, y las referencias de Validación ahora separan los resultados derivados.

## 1. Resumen ejecutivo

| Medida | Inicial | Final |
|---|---:|---:|
| Cumplimiento estimado de la rúbrica | **62.75 %** | **97.00 %** |
| Valores de las tablas del documento que la aplicación reproduce | 828 de 837 | 828 de 837 |
| Página de Validación: diferencias mostradas | 43 | 6 |
| Pruebas aprobadas | 599 de 599 | 656 de 656 |

**Los cálculos ya eran correctos: las deficiencias estaban en el acceso y la presentación.** El análisis horizontal, que vale 15 %, no aparecía en el menú; los comparativos 7.1 y 7.2 tampoco. En los PDF las cifras se partían dígito a dígito y el Balance 2021 mostraba 18 cuentas ajenas a los estados originales. Todo esto quedó corregido.

**Los 9 valores que no coinciden tienen causa en el documento, no en la aplicación:** un recálculo independiente desde los estados originales obtiene los mismos resultados que la aplicación. Se dejaron documentados y no se forzaron.

**Tu decisión:** elegir la base de cuentas por cobrar de 2023 (D-1, sección 8) y decidir el commit.

## 2. Estado inicial del repositorio

| Elemento | Valor |
|---|---|
| Rama y commit | `correcciones-auditoria`, `4506ed8ff24906d44a3e7c22cba8e111094759db` |
| `git status` | 30 archivos modificados y 3 sin seguimiento, todos anteriores a esta tarea, guardados en el respaldo con su diff |
| Fuentes | `documentos/` (PDF originales), `fuentes/alutech/*.json` (transcripción con documento y página) |
| Respaldo | `C:\Users\estua\Documents\ANF\respaldos_appfinanciera\rubrica_integral_20261105\`: 118 archivos, base de datos incluida, con manifiesto SHA-256 verificado |

## 3. Estado inicial de las pruebas

599 aprobadas, 0 fallidas, 0 omitidas, en una copia aislada.

## 4. Matriz de cumplimiento de los 15 requisitos

Puntuación: CUMPLE = 100 % del peso, CUMPLE PARCIALMENTE = 50 %, NO CUMPLE = 0 %.

| # | Requisito | Peso | Inicial | Final | Evidencia |
|---:|---|---:|---|---|---|
| 1 | Ingreso de datos | 2.5 | CUMPLE | CUMPLE | Formularios por ejercicio, validación de importes y signos, confirmación antes de guardar y restricciones únicas por ejercicio y cuenta. Se conservó |
| 2 | Modificación de datos | 2.5 | CUMPLE | CUMPLE | Tabla editable, vista previa, historial y bloqueo por cierre. Prueba nueva: modificar 2025 no altera los otros ejercicios |
| 3 | Balance General | 2.5 | PARCIAL | CUMPLE | Totales iguales a los originales y ecuación contable correcta. Se omiten en el reporte las 18 cuentas ajenas de 2021 |
| 4 | Estado de Resultados | 2.5 | CUMPLE | CUMPLE | Subtotales y signos iguales a las fuentes. Se conservó |
| 5 | Vertical del Balance | 7.5 | PARCIAL | CUMPLE | Tabla 7.2 ahora en el menú, con 40 de 40 valores y las mismas denominaciones |
| 6 | Vertical de Resultados | 7.5 | PARCIAL | CUMPLE | Tabla 7.1 ahora en el menú, con 75 de 75 valores y signos negativos |
| 7 | Horizontal del Balance | 7.5 | PARCIAL | CUMPLE | Reporte nuevo: Tablas 3, 4, 6 y 7 y comparación de dos ejercicios |
| 8 | Horizontal de Resultados | 7.5 | PARCIAL | CUMPLE | Reporte nuevo: Tabla 5 y comparación de dos ejercicios |
| 9 | Ratios de liquidez | 6 | CUMPLE | CUMPLE | Tablas 8.1, 6 y 9.1 reproducidas. Se agrega su base financiera |
| 10 | Ratios de actividad | 6 | PARCIAL | **PARCIAL** | Saldos al cierre, como dice 8.2. Queda pendiente D-1: el documento usa dos bases para 2023 |
| 11 | Ratios de deuda | 6 | PARCIAL | CUMPLE | 8.3 A, B y D reproducidas. 8.3 C ahora sigue el criterio del documento |
| 12 | Ratios de rendimiento | 6 | CUMPLE | CUMPLE | 8.4 completa, con EPS «No calculable», como en el documento |
| 13 | Análisis DuPont | 6 | CUMPLE | CUMPLE | No se reimplementó. Se agregan a su página las tablas de 9.5 y 9.6 de los cinco años |
| 14 | Interfaz de usuario | 15 | PARCIAL | CUMPLE | Menú completo, cifras alineadas y selección de período. Sin excepciones ni desborde en Edge a 1400 y 480 px |
| 15 | Diseño de reportes | 15 | PARCIAL | CUMPLE | Los 11 reportes con PDF y Excel, cifras sin cortes y Excel sin `###` |
| | **Total** | **100** | **62.75** | **97.00** | |

Rúbrica 4.11: el documento no define un indicador de autonomía patrimonial. **NO APLICA**; su equivalente es la fila «Patrimonio» de 7.2.

Los requisitos 14 y 15 incluyen criterio estético: el 100 % es técnico y queda sujeto a tu revisión.

## 5. Porcentaje estimado de cumplimiento inicial

**62.75 %**: 2.5 + 2.5 + 1.25 + 2.5 + (3.75 × 4) + 6 + 3 + 3 + 6 + 6 + 7.5 + 7.5.

## 6. Matriz de concordancia

Cada valor se comparó en tres vías: documento (leído del Markdown), recálculo exacto desde los estados originales y aplicación. La aplicación y el recálculo coinciden en los 837 valores, con diferencia menor que 0.000001.

| Sección | Valores | Coinciden | No coinciden |
|---|---:|---:|---:|
| 6.4 Tablas 3, 4 y 5 (horizontal) | 175 | 175 | 0 |
| 6.5 y 6.6 Tablas 6 y 7 (capital de trabajo) | 65 | 65 | 0 |
| 7.1 Vertical de Resultados | 75 | 75 | 0 |
| 7.2 Vertical del Balance | 40 | 40 | 0 |
| 8.1 Liquidez | 15 | 15 | 0 |
| 8.2 A y D Inventarios y activos | 35 | 35 | 0 |
| 8.2 B Cuentas por cobrar | 20 | 16 | 4 |
| 8.2 C Ciclo operativo (texto) | 2 | 1 | 1 |
| 8.3 A, B y D Endeudamiento | 45 | 45 | 0 |
| 8.4 Rentabilidad | 130 | 130 | 0 |
| 9.1 y 9.2 Tesorería y fondo de maniobra | 45 | 45 | 0 |
| 9.3 Ciclo de conversión | 75 | 71 | 4 |
| 9.5 y 9.6 DuPont total | 65 | 65 | 0 |
| 9.6 DuPont controladora | 50 | 50 | 0 |
| **Total** | **837** | **828** | **9** |

Los controles DuPont que indicaste coinciden en los cinco años: margen, rotación, RSA, MAF y RSP. La tabla de 4 decimales se obtiene en la página por ejercicio.

Las tablas 3 a 7, 7.1 y 7.2 también se compararon como texto en pantalla, celda por celda, con la misma precisión y signos que el documento. La única adaptación es que en la app no se muestra el sufijo «x» de la Tabla 6.

La página de Validación, que abarca también WACC, 9.7 y textos, compara ahora 741 valores: 714 coinciden, 6 por redondeo, 6 difieren y 15 no aplican.

## 7. Diferencias numéricas y metodológicas

| Valor | Documento | Aplicación | Causa |
|---|---:|---:|---|
| CxC 2023 (8.2 B) | 96,097,483 | 41,272,525 | D-1, base distinta |
| Rotación CxC 2023 (8.2 B) | 4.98 | 11.60 | D-1 |
| PPC 2023 (8.2 B) | 73.3 | 31.47 | D-1 |
| PPC 2025 (8.2 B) | 58.3 | 58.25 | D-2, doble redondeo |
| Ciclo operativo 2022 (9.3, dos filas) | 149.28 | 149.29 | D-3, suma de redondeados |
| Ciclo operativo 2023 (9.3, dos filas) | 169.72 | 169.73 | D-3 |
| Ciclo operativo 2025 (8.2 C) | 135.2 | 135.14 | D-3 |

No hay diferencias de signo, denominador, período ni cuenta en los demás valores.

## 8. Inconsistencias dentro del documento

El documento no se modificó. «Verificado hoy» significa que se comprobó en esta tarea; «auditoría anterior» indica que viene del 2026-11-03 y que el archivo no ha cambiado desde entonces (mismo hash).

| ID | Inconsistencia | Publicado | Sustentado | ¿Corregible en la aplicación? | Origen |
|---|---|---|---|---|---|
| **D-1** | 8.2 B usa comerciales en 2021–2022 y comerciales + otras en 2023; 9.3 usa solo comerciales en 2023 | 96,097,483 · 4.98 · 73.3 | Ambas aritméticas son correctas; solo la serie de 9.3 mantiene una regla única entre años de igual presentación | Solo con una excepción por año, que prohibiste. **Decisión académica.** La aplicación sigue 9.3 y muestra 4.98 y 73.28 en la variante homogénea | Verificado hoy |
| **D-2** | PPC 2025 difiere entre 8.2 B y 9.3 | 58.3 | 58.25 (exacto 58.2482), igual que 9.3 | No se reproduce un error | Verificado hoy |
| **D-3** | El ciclo operativo suma cifras ya redondeadas | 149.28, 169.72, 135.2 | 149.29, 169.73, 135.14 | No: exigiría redondeo intermedio | Verificado hoy |
| D-4 | 9.7 trata «Otras CxC a LP» 2024 (118,684,551) como relacionadas | Variación 143,444,117; total 289,762,626 | Variación 262,128,668; total 408,447,177 | Sin respaldo documental; queda documentado. Fuera de la rúbrica | Auditoría anterior |
| D-5 | 8.3 A trunca PC / pasivo 2021 | 50.40 % | 50.41 % (50.4053) | No se reproduce | Verificado hoy |
| D-6 | WACC 2023 suma aportes redondeados | 3.88 % | 3.87 % | Fuera de la rúbrica | Auditoría anterior |
| D-7 | 5.6 define rotaciones con promedios; 8.2 establece saldos al cierre | — | La aplicación sigue 8.2, el criterio de cálculo | Ya aplicado | Verificado hoy |
| D-8 | 8.2 dice que no hay desglose de cuentas por pagar y que no es viable el PPP; 9.3 lo usa y lo calcula | — | La aplicación calcula el PPP de 9.3 | Ya aplicado | Verificado hoy |
| D-9 | Figuras DuPont del PDF con importes intermedios erróneos; sus razones finales sí coinciden | 2022: costo 388,240,555 y activos circulantes 333,168,323 | 410,331,156 y 448,672,401 | No: son imágenes del documento. La auditoría anterior contó 29 de 65 importes erróneos | Figuras de 2022 y 2023 vistas hoy |
| D-10 | La tabla 7.1 ubica «Otros ingresos o gastos» antes del resultado operativo, pero en 2024–2025 se suma después | — | La aplicación conserva el orden y lo aclara en una nota | Ya aplicado | Verificado hoy |
| D-11 | 7.1 marca 6.24 %\* y 9.34 %\* sin nota al pie | — | Valores correctos | Nada que corregir | Verificado hoy |
| D-12 | 8.3 B rotula «Gastos financieros» importes netos; 8.4 C cita el bruto de 2025 (51,914,906) | — | La aplicación usa neto y lo rotula así; muestra el bruto como variante | Ya aplicado | Verificado hoy |
| D-13 | Utilidad de la controladora 2023: el estado de resultados dice 13,330,680 y el de cambios en el patrimonio, 12,309,102 | 12,309,102 | La aplicación usa la misma fuente que el documento | Ya aplicado | Verificado hoy |
| D-14 | 9.5 y 9.6 mezclan formatos numéricos (13,09 % y 0.95 veces) | — | Solo presentación | No afecta | Verificado hoy |
| D-15 | Los números de página del índice están desfasados | — | Solo presentación | No afecta | Auditoría anterior |

**Markdown frente a PDF:** las 2,291 cifras de las tablas de las secciones 6 a 9 del Markdown aparecen en el PDF. Es una búsqueda por cadena de texto, no una comparación celda por celda. El PDF tiene 85 páginas.

## 9. Deficiencias encontradas en el software

| # | Deficiencia | Peso afectado |
|---:|---|---|
| 1 | Análisis horizontal fuera del menú; solo se abría con `ANF_MENU_COMPLETO=1` | 15 % |
| 2 | Sin reportes separados por estado, sin saldo actual y anterior por par, y sin aumento o disminución | 15 % |
| 3 | Comparativos 7.1 y 7.2 fuera del menú | 15 % |
| 4 | PDF: cifras partidas y columna «Unidad» escrita letra por letra | 15 % |
| 5 | Excel de secciones: columnas más angostas que los importes, con riesgo de `###` | 15 % |
| 6 | 18 cuentas del catálogo estándar en 0.00 en el Balance y el vertical de 2021 | 2.5 % y 7.5 % |
| 7 | Validación comparaba contra una versión antigua del documento: 37 referencias obsoletas | Confiabilidad |
| 8 | 8.3 C «No calculable», cuando el documento dice que iguala a la cobertura de intereses | 6 % |
| 9 | Ratios sin sus bases, sin archivo propio por apartado y sin EPS en Rentabilidad | 12 % |
| 10 | Grupo «Otros no operativos» sumaba ingresos y gastos sin signo: un gasto de 2025 se veía como aumento | Horizontal |
| 11 | Cifras alineadas a la izquierda en pantalla y etiquetas cortadas | 15 % |
| 12 | Cada exportación se regeneraba al redibujar la página | Interfaz |

## 10. Correcciones implementadas

1. **Reportes nuevos de análisis horizontal**, uno por estado, en el menú. Traen las tablas del documento y la comparación de dos ejercicios por rubros, grupos o cuentas, con aumentos, disminuciones, cuentas que aparecen o desaparecen y cambios de signo. No se inventan porcentajes con base cero, negativa o inexistente.
2. **Pestaña comparativa en cada análisis vertical** y tablas de cinco años en DuPont, con sus descargas.
3. **Ratios:** base financiera por apartado, PDF y Excel propios, cobertura de pagos fijos y EPS.
4. **PDF:** el ancho se calcula con la medida real de cada cifra, el tamaño de letra se ajusta y los totales van en negrita.
5. **Excel:** los anchos incluyen las cifras y los formatos llevan signo cuando son variaciones.
6. **Cuentas en 0.00 sin mapear:** se omiten solo en los reportes, con una nota. Siguen en la base y en Modificación de datos.
7. **Referencias:** 37 valores actualizados, cada uno comprobado contra la tabla vigente del documento, y 5 agregados de 8.3 C. Seis observaciones obsoletas pasan a una sección histórica.
8. **Interfaz:** cifras a la derecha, etiquetas completas, botón «Deploy» oculto y exportaciones generadas al pulsar el botón.

Ningún resultado se escribió a mano y no hay excepciones por año en los cálculos.

## 11. Archivos modificados y motivo

| Archivo | Motivo |
|---|---|
| `calculations/comparativo.py` | Filas de las tablas, comparación de dos ejercicios, sentido del cambio y signo de «Otros no operativos» |
| `calculations/indicadores.py` | Cobertura de pagos fijos según 8.3 C |
| `calculations/validation.py`, `calculations/vertical_analysis.py` | Omisión de las cuentas ajenas en reportes |
| `reports/secciones.py` | Tablas 3 a 7, base financiera y formatos con signo |
| `reports/analisis_alutech.py` | Páginas de análisis horizontal |
| `reports/vertical_report.py`, `reports/dupont_report.py` | Comparativos de los ejercicios |
| `reports/indicadores_financieros.py` | Bases, descargas por apartado, EPS y pagos fijos |
| `reports/exportar_secciones.py` | Diseño del PDF y anchos y formatos del Excel |
| `reports/balance_report.py`, `reports/pdf_export.py`, `reports/excel_export.py` | Omisión con nota de las cuentas ajenas |
| `components/navigation.py`, `app.py` | Menú y rutas |
| `components/tables.py`, `components/secciones_ui.py` | Alineación, etiquetas y descarga diferida |
| `.streamlit/config.toml` | Oculta el botón «Deploy» |
| `fuentes/anf/resultados_referencia.json`, `fuentes/anf/observaciones_validacion.json` | Copia de referencia del documento, puesta al día. **No son estados financieros ni el documento académico** |
| `README.md`, `REGISTRO_DE_CAMBIOS.md` | Documentación |
| **Nuevos:** `tests/test_fase9_rubrica.py`, `tests/concordancia_documento.py`, `tests/humo_horizontal.py`, este informe y `MATRIZ_CONCORDANCIA_ANF.md` | Pruebas y entregables |

Pruebas ajustadas por un cambio legítimo: `test_alutech.py`, `test_fase8_vertical_dupont.py`, `test_fase1_paginas.py`, `test_fase5_integracion.py` y `test_fase4.py`.

## 12. Funcionalidades que ya cumplían y se conservaron

Captura, edición, historial y cierre de ejercicios; cálculo de estados y de indicadores; modelo DuPont (`calculations/dupont.py` sin cambios); WACC; origen y aplicación; importación Excel; copias de seguridad; catálogo; y la opción oculta del horizontal anterior.

## 13. Pruebas funcionales

- **Automatizadas:** captura, edición, validaciones, confirmaciones, duplicados y ejercicios cerrados, con las pruebas existentes. Modificar un ejercicio no altera los demás, con una prueba nueva.
- **En navegador:** Edge sobre una copia aislada; se abrieron 10 opciones del menú sin excepciones.
- **No hecho:** no se guardó ningún dato desde el navegador; esos flujos solo se comprobaron con pruebas automatizadas.

## 14. Pruebas matemáticas

837 valores recalculados con fracciones exactas desde los estados originales, sin usar `calculations/`. Sin diferencias con la aplicación.

## 15. Pruebas de concordancia

`tests/test_fase9_rubrica.py` lee los valores del propio documento y exige exactamente las 9 discrepancias documentadas: una nueva, o la desaparición de una, hace fallar la prueba.

Para comprobar que detectan errores, se introdujeron 12 fallos en copias, uno a la vez, y **los 12 se detectaron**. Una variante del signo se detectó antes de llegar a estas pruebas, porque la carga de datos falló:

| Tipo | Fallos introducidos |
|---|---|
| Fórmula y denominador | PPI sobre ingresos, base de 360 días, ROE sobre activo, cobertura con gastos brutos, MAF sobre pasivo |
| Cuenta | Prueba ácida sin restar inventarios, CxC con otras cuentas |
| Signo | Costo de ventas positivo (dos variantes) |
| Período | Variación sobre el saldo actual |
| Redondeo | Variación relativa a un decimal |
| Exportación | Excel con importes redondeados |

## 16. Pruebas de interfaz

- **AppTest:** todas las páginas, el menú y la selección de período y de nivel.
- **Edge real, verificación manual asistida por código:** capturas revisadas a 1400 px y 480 px, sin desborde de página. En móvil, las tablas anchas se desplazan dentro de su recuadro.
- **No medido:** los tiempos de carga, porque la medición resultó poco fiable.

## 17. Pruebas PDF y Excel

| Comprobación | Método | Resultado |
|---|---|---|
| Generación de los 11 reportes | Código | PDF y Excel válidos, con empresa y título |
| Cifras de PDF y Excel iguales a pantalla | Código, reportes horizontales y comparativos | Coinciden |
| Ninguna cifra partida en el PDF | Medida de anchos, automatizada | Sin cortes |
| Aspecto del PDF | Primera página convertida a imagen, 6 reportes vistos | Correcto |
| Excel sin `###` ni errores | **Microsoft Excel real**, solo lectura, 12 libros y 2,043 celdas numéricas | 0 y 0 |
| Descarga con los botones | Edge real, Horizontal del Balance | PDF de 8 páginas y Excel de 6 hojas |

**Sin verificar a mano:** no se revisaron todas las páginas de cada PDF ni la impresión en papel. Tampoco se pulsó en el navegador la descarga de los demás reportes.

## 18. Número de pruebas

| Concepto | Cantidad |
|---|---:|
| Iniciales | 599 |
| Finales | **656: 656 aprobadas, 0 fallidas, 0 omitidas** |
| Nuevas | 57: 53 en `test_fase9_rubrica.py` y 4 por las páginas nuevas |
| Modificadas | 7 pruebas, en 5 archivos |
| Eliminadas | **0**, comprobado comparando las listas de pruebas |

## 19. Porcentaje estimado de cumplimiento final

**97.00 %.** Los 3 puntos restantes corresponden al requisito 10, que queda parcial por D-1 y depende de una decisión académica.

## 20. Incidencias pendientes y limitaciones

1. **D-1, base de cuentas por cobrar de 2023:** requiere tu decisión. Las opciones son mantener 9.3 (la actual) o unificar 8.2 B en el documento.
2. **Figuras DuPont del PDF (D-9) y demás correcciones del documento:** no se tocaron.
3. **18 cuentas en 0.00 de 2021:** siguen en la base. Se omiten de los reportes; borrarlas requiere tu autorización.
4. **Base negativa:** el documento dice que el porcentaje «debe interpretarse con cautela»; la aplicación no lo calcula y lo explica. No afecta a ninguna tabla del documento. Cambiarlo es sencillo si lo prefieres.
5. **Cambio de estados combinados a consolidados:** las variaciones 2023–2024 mezclan cambios reales y de presentación. Los reportes lo advierten.
6. **EPS, P/E y mercado/libro:** no calculables por falta de datos. La cobertura de pagos fijos no mide la cobertura real.
7. **Reinicio:** si tienes la aplicación abierta, reiníciala para que aplique el cambio de `.streamlit/config.toml`.

## 21. Base de datos y hashes

| Archivo | SHA-256 inicial | Final |
|---|---|---|
| `data/financiera.db` | `39ee373979fe9a72740c29e534ecdfe3e8c2ef0e145f7164c8b1a0675ebcba77` | **Sin cambios** |
| `Trabajo de investigación ANF.md` | `5d5e316425292d83e65a436a8a167239dfb1e0daf669442bd20828b23156b80c` | **Sin cambios** |
| `Trabajo de investigación ANF.pdf` | `f6b0bc64738fad2b3e014b68d1aba06387a38c32ae05bcbea4de7f435509d957` | **Sin cambios** |
| `fuentes/alutech/estados_financieros_2021_2025.json` | `c96af696ca71a3700c5a01a7833399a878b729cb80d5d1d014cb2feee8310321` | **Sin cambios** |
| `fuentes/anf/supuestos_wacc.json` | `835a561e0120d5b041e0629a1e74e9e01f76dc2aeef3aa0224cd8bffa0d0234a` | **Sin cambios** |
| `fuentes/anf/resultados_referencia.json` | `7f4b7e85d10cd69c5302d0bc0af4928043e6076a49d39988d07783a44eb148c5` | **Cambió:** `6491d32f…`. Lo decidí dentro del alcance de corregir diferencias, sin autorización expresa; ver sección 11. Para revertirlo, usa el respaldo |
| `fuentes/anf/observaciones_validacion.json` | `f007266f95187e3c33a01bf3d46ac096d336efe69b5fc6d313092e49731d52d1` | **Cambió:** `f22baa51…` |

Los 9 archivos de `documentos/` tienen los mismos hashes al inicio y al final. No hubo migración ni reconstrucción de la base. Todas las pruebas se ejecutaron en copias.

## 22. Estado de Git

**No se realizó ningún commit.** Rama `correcciones-auditoria`, HEAD sigue en `4506ed8`. Tampoco hubo push ni despliegue.

## 23. Recomendaciones para la revisión manual

1. Abre la aplicación y recorre **Generación de reportes**, en especial los dos análisis horizontales y la pestaña «Comparar dos ejercicios», nivel *Cuentas*, 2024 vs 2023.
2. Compara con el documento en mano la Tabla 5 y las tablas 7.1 y 7.2.
3. Descarga y abre un PDF y un Excel de cada tipo de reporte, y prueba imprimir uno.
4. Revisa el Balance 2021 y comprueba en **Modificación de datos** que las 18 cuentas siguen allí.
5. Prueba en el navegador un ingreso y una modificación sobre una copia de la base, no sobre la original.
6. Decide D-1 y, después, el commit.

## Conclusión

| Pregunta | Respuesta |
|---|---|
| ¿Cumple la rúbrica? | **Sí en 14 de 15 requisitos.** Ratios de actividad queda parcial por D-1: 97 % estimado |
| ¿Reproduce los resultados del documento? | **Sí en 828 de 837 valores (98.9 %).** Los otros 9 no se sustentan con la fórmula aplicada a los datos originales, o contradicen otra sección del documento |
| ¿Presenta diferencias pendientes? | **Sí:** las 9 anteriores, todas documentales y explicadas; en la Validación quedan además las de 9.7 (D-4) |
| ¿Está lista para revisión y aprobación final? | **Sí, para revisión manual.** La aprobación depende de esa revisión y de tu decisión sobre D-1 |
