# Auditoría forense de errores — Aplicación financiera y Trabajo ANF
## Alutech, S. A. de C. V. y subsidiarias – División Acero, 2021–2025

Fecha: 2026-11-03 · Rama `correcciones-auditoria` (HEAD `92115b6` más cambios sin confirmar) · Auditoría **de solo lectura**: no se modificó, movió ni restauró ningún archivo, dato ni registro de git. El único archivo creado en el proyecto es este informe.

---

## 1. Resumen ejecutivo

1. **Datos de la aplicación: sin errores.** Los 247 importes de SQLite coinciden con la cifra impresa en el documento original y en la página registrada (cadena documento → `fuente_importe` → `balance_entry`/`income_entry`). Las agregaciones por SQL directo coinciden con los cálculos de la app. Los valores de pantalla (195 de indicadores) y del Excel del informe integral (7,326 celdas numéricas) coinciden con los cálculos.
2. **Código de la aplicación: sin errores de fórmula ni de implementación.** Recalculé de forma independiente 1,188 resultados y coinciden 1,183. Las 5 excepciones son el ROE del reporte DuPont por promedios, redondeado a 2 decimales para presentarlo. La suite de pruebas pasa 525/525 en una copia aislada.
3. **Integridad del proyecto: hallazgo crítico vigente.** `calculations/` sigue movida a `.venv/calculations/`. La app solo funciona por accidente con el intérprete del `.venv`, y 7 módulos sin seguimiento en git están dentro de una carpeta excluida por `.gitignore` (§2).
4. **Documento académico: 4 cifras base no figuran en los estados auditados.** Son el AC 2023 (541,094,544), el PC 2023 (342,120,685), el PC 2022 (231,914,180) y la UO 2022 (31,200,000). **Nuevo hallazgo de origen:** las tres primeras coinciden en millones con el *resumen de estados financieros no auditados* del informe de calificación PCR (`SV-CIALUTECH-202506.pdf`, p. 8: 541.1, 342.1 y 231.9). La UO 2022 coincide con el 31.2 de esa misma página. El AC y el PC 2023 del trabajo son híbridos: millones de PCR con los dígitos inferiores de la cifra auditada (diferencias exactas de 111,300,000 y 9,000,000).
5. **Errores de clasificación:** el trabajo trata como «relacionadas» la cuenta 2024 «Otras cuentas por cobrar a LP» (118,684,551), y ninguna fuente disponible lo respalda. La app la clasifica conforme al documento. Además, el trabajo cambia en 2023 la base de cuentas por cobrar en 8.2 B.
6. **Diferencias metodológicas con efecto en las conclusiones:**
   - el ciclo de conversión del efectivo mezcla bases de CxC y CxP entre 2021–2023 y 2024–2025, tanto en el trabajo como en el indicador principal de la app; con bases homogéneas, el CCE 2023 es **+8.56 días**, no −21.40;
   - el WACC usa el ROE como costo del patrimonio (Ke < Kd en 2022, 2024 y 2025) e incluye pasivos operativos sin costo en la ponderación;
   - el reporte DuPont antiguo de la app usa saldos promedio.
7. **No verificable:** las tasas de interés y el ISR del WACC, la contraparte de la cuenta CN1202 de 2024 y cuál de las dos cifras de utilidad de la controladora de 2023 es la correcta.

## 2. Estado de integridad del proyecto

| Elemento | Estado verificado (2026-11-03 11:21) |
|---|---|
| `calculations/` | **No existe** en la raíz del proyecto. |
| `.venv/calculations/` | **Existe**, con 14 módulos íntegros: `balance_sheet`, `banderas`, `comparacion_anf`, `comparativo`, `controles_carga`, `controls`, `dupont`, `fuentes_usos`, `income_statement`, `indicadores`, `rubros`, `validation`, `vertical_analysis`, `wacc`. Fechas originales (última: 2026-11-02 22:06); carpeta movida el 2026-11-03 a las 10:50:17. Los 7 con seguimiento son idénticos a HEAD salvo los fines de línea (CRLF). |
| `data/financiera.db` | Existe; SHA-256 `48bb729f…af4dd269`, igual antes y después de ambas auditorías. Esquema v4. 5 respaldos en `data/backups/`. |
| Módulos de captura y modificación | `modules/data_entry.py`, `data_edit.py`, `excel_import.py` y `accounts.py`: presentes. |
| Módulos de reportes | `reports/*.py` (11 archivos): presentes. |
| Documentos de control | `INFORME_VALIDACION_FINANCIERA.md`, `MAPEO_FINANCIERO_ALUTECH.md`, `MATRIZ_ADAPTACION.md`, `REGISTRO_DE_CAMBIOS.md`, `INVESTIGACION_DOCUMENTAL_ANF.md` y `AUDITORIA_CONCORDANCIA_APP_VS_TRABAJO_ANF.md`: presentes, sin seguimiento en git. |
| `git status` | 16 modificados (` M`), **7 eliminados** (` D calculations/{balance_sheet, banderas, controls, dupont, income_statement, validation, vertical_analysis}.py`) y 17 sin seguimiento (`??`): documentos de control, `fuentes/`, `scripts/`, `reports/secciones.py`, etc. Sin stash. |
| Archivos `.py` fuera de lugar | Ninguno fuera de las carpetas esperadas, salvo `.venv/calculations/*.py`. |

**Consecuencias, comprobadas sin escribir archivos (`python -B`):**

- Con `.venv\Scripts\python.exe`, `import calculations` resuelve a `.venv\calculations` como *paquete de espacio de nombres*, porque en Windows la raíz del venv está en `sys.path`. La app y sus reportes importan y funcionan, pero **por accidente**.
- Con cualquier otro intérprete (p. ej., el Python global) falla: `ModuleNotFoundError: No module named 'calculations'`.
- `.gitignore` excluye `.venv/`. Los 7 módulos **sin seguimiento** (`comparacion_anf`, `comparativo`, `controles_carga`, `fuentes_usos`, `indicadores`, `rubros`, `wacc`) solo existen en esa carpeta: se perderían si se recrea el venv.
- `git commit -a` registraría el borrado de los 7 módulos con seguimiento.
- Treinta y tres archivos del proyecto (módulos, reportes, scripts y pruebas) importan `calculations`.

**Corrección al informe anterior:** `AUDITORIA_CONCORDANCIA_APP_VS_TRABAJO_ANF.md` (§3 y O‑1) afirmó que la aplicación «no puede iniciarse». No es exacto: arranca con el intérprete del venv por el mecanismo descrito, pero su funcionamiento depende de ese accidente. Ese informe no se modificó.

## 3. Archivos y documentos examinados

| Tipo | Archivo | Uso |
|---|---|---|
| Original | `documentos/Certificacin_EFC_Alutech_Divisin_Acero_2021VF_Mod010925.pdf` (y 2022, 2023) | Estados **combinados** auditados (PwC), certificados por Espinoza Auditores. Balance págs. 6–9, resultados págs. 9–10, cambios en el patrimonio págs. 11–12 y flujos de efectivo págs. 12–13. |
| Original | `documentos/12_EEFF_diciembre_2024.pdf` | Estados **consolidados** 2024 (escaneados): lectura visual de las págs. 1–2. |
| Original | `documentos/12_EEFF_diciembre_2025.pdf` | Estados consolidados 2025 (págs. 1–2). |
| Complementario | `documentos/SV-CIALUTECH-202506.pdf` | Informe de calificación PCR (jun‑2025): tramos de CIALUTECH1 (p. 7), resumen de estados **no auditados** (p. 8) e indicadores (p. 9). |
| Base de datos | `data/financiera.db` | Tablas `account`, `balance_entry`, `income_entry`, `fuente_importe`, `dato_complementario` y `fiscal_period`, en modo de solo lectura (`mode=ro`). |
| Código | `.venv/calculations/*.py`, `reports/secciones.py`, `reports/exportar_secciones.py`, `reports/informe_integral.py` y `fuentes/anf/supuestos_wacc.json` | Fórmulas, agregación y presentación. |
| Académico | `Trabajo de investigación ANF.md` (línea `MD Lnnn`) y `.pdf` (página física `PDF p. n`, de 83) | Valores del trabajo. |
| Control | `fuentes/alutech/estados_financieros_2021_2025.json`, `REGISTRO_DE_CAMBIOS.md` y `MAPEO_FINANCIERO_ALUTECH.md` | Antecedentes; no se tomaron como prueba. |

## 4. Metodología

1. **Integridad:** listado de carpetas, `git status`, resolución de importaciones con `python -B` (sin escribir caché) y comprobación de que ningún archivo del proyecto cambió durante la auditoría.
2. **Documento → SQLite:** para cada registro de `fuente_importe`, la cifra impresa (`importe_documento`) se buscó en el texto del PDF en la página registrada (para 2024, en mi transcripción visual de la imagen). Además, se comparó `valor_registrado` con el importe vigente de `balance_entry`/`income_entry` (en centavos).
3. **SQLite → cálculo:** totales y utilidades agregados con **SQL directo** por categoría contable, sin código de la app, y comparados con `compute_balance_sheet`, `compute_income_statement` y `DatosEjercicio`.
4. **Cálculo → presentación:** los valores de `reports/secciones.py` (que alimentan pantalla, Excel y PDF) se compararon con `indicadores.calcular`. Se generó en una carpeta temporal el Excel del informe integral (`secciones_a_excel`) y se releyó con `openpyxl`, celda por celda.
5. **Fórmulas:** inspección del código y recálculo independiente de cada indicador (scripts propios en Python con `Decimal`), aplicando las fórmulas del trabajo.
6. **Pruebas:** suite completa (`pytest -B -p no:cacheprovider`) en una **copia** del árbol con `calculations/` en su lugar y una copia de la base: 525 aprobadas de 525. No se ejecutó en el árbol real porque escribiría cachés.
7. **Trabajo académico:** 1,440 valores leídos de sus líneas del Markdown, contrastados con el PDF y con los originales (detalle en `AUDITORIA_CONCORDANCIA_APP_VS_TRABAJO_ANF.md`, §6).

## 5. Verificación de cifras originales

| Control | Resultado |
|---|---|
| Registros de trazabilidad (`fuente_importe`) | 247 |
| Cifra impresa hallada en el PDF y en la página registrada | **247 / 247** |
| `valor_registrado` = importe vigente en SQLite | **247 / 247** (0 modificados después de la carga) |
| Importes en SQLite sin fuente | 18: los ceros de 2021 de las cuentas del catálogo estándar (1001–1104, 2001–2102, 3001–3003, 3005), sin documento de origen y sin efecto en los totales. |
| Totales impresos = totales de la app | 61 / 61 |
| SQL directo = cálculo de la app (17 partidas × 5 años) | Sin diferencias |
| Presentación = cálculo | 195 / 195 valores de indicadores; capital de trabajo, RC y PA iguales; 7,326 / 7,326 celdas del Excel iguales, sin fórmulas en las celdas (B‑10 respetado). |

**Partidas clave por ejercicio.** «Original» es la cifra impresa; si el documento no la imprime, la suma de sus líneas impresas, o se indica. La columna «Trabajo ANF» muestra todos los valores distintos que el trabajo usa para la partida.

| Año | Partida | Original (documento, pág.) | SQLite | Aplicación | Trabajo ANF | Diferencia trabajo − original |
|---|---|---:|---:|---:|---:|---:|
| 2021 | Total activos corrientes | 383,881,547 — Cert. EFC 2021, p. 8 (impreso) | 383,881,547 | 383,881,547 | 383,881,547 | 0 |
| 2021 | Total activos no corrientes | 170,073,638 — Cert. EFC 2021, p. 8 (impreso) | 170,073,638 | 170,073,638 | (no presenta el importe) | — |
| 2021 | Total activos | 553,955,185 — Cert. EFC 2021, p. 8 (impreso) | 553,955,185 | 553,955,185 | 553,955,185 | 0 |
| 2021 | Total pasivos corrientes | 205,973,230 — Cert. EFC 2021, p. 9 (impreso) | 205,973,230 | 205,973,230 | 205,973,230 | 0 |
| 2021 | Total pasivos no corrientes | 202,660,765 — Cert. EFC 2021, p. 9 (impreso) | 202,660,765 | 202,660,765 | (no presenta el importe) | — |
| 2021 | Total pasivos | 408,633,995 — Cert. EFC 2021, p. 9 (impreso) | 408,633,995 | 408,633,995 | 408,633,995 | 0 |
| 2021 | Total patrimonio | 145,321,190 — Cert. EFC 2021, p. 9 (impreso) | 145,321,190 | 145,321,190 | 145,321,190 | 0 |
| 2021 | Ingresos ordinarios | 523,965,227 — Cert. EFC 2021, p. 10 | 523,965,227 | 523,965,227 | 523,965,227 | 0 |
| 2021 | Costo de ventas | 367,252,613 — Cert. EFC 2021, p. 10 | 367,252,613 | 367,252,613 | 367,252,613 | 0 |
| 2021 | Utilidad bruta | 156,712,614 — Cert. EFC 2021, p. 10 (impreso) | 156,712,614 | 156,712,614 | 156,712,614 | 0 |
| 2021 | Gastos de operación (adm.+ventas+personal+dep.; criterio Tabla 5) | 53,179,448 — Cert. EFC 2021, p. 10 (suma de líneas) | — | 53,179,448 | 53,179,448 | 0 |
| 2021 | Utilidad de operación | 103,578,903 — Cert. EFC 2021, p. 10 (impreso) | 103,578,903 | 103,578,903 | 103,578,903 | 0 |
| 2021 | Ingresos financieros | 0 — Cert. EFC 2021: no presentado | 0 | 0 | (no presenta el importe) | — |
| 2021 | Gastos financieros (como se presentan) | 21,777,725 — Cert. EFC 2021, p. 10 | 21,777,725 | 21,777,725 | (no presenta el importe) | — |
| 2021 | Utilidad antes de impuestos | 81,801,178 — Cert. EFC 2021, p. 10 (impreso) | 81,801,178 | 81,801,178 | (no presenta el importe) | — |
| 2021 | Impuesto sobre la renta | 13,198,439 — Cert. EFC 2021, p. 10 | 13,198,439 | 13,198,439 | (no presenta el importe) | — |
| 2021 | Utilidad neta | 68,602,739 — Cert. EFC 2021, p. 10 (impreso) | 68,602,739 | 68,602,739 | 68,602,739 | 0 |
| 2022 | Total activos corrientes | 448,672,401 — Cert. EFC 2022, p. 8 (impreso) | 448,672,401 | 448,672,401 | 448,672,401 | 0 |
| 2022 | Total activos no corrientes | 223,352,692 — Cert. EFC 2022, p. 8 (impreso) | 223,352,692 | 223,352,692 | (no presenta el importe) | — |
| 2022 | Total activos | 672,025,093 — Cert. EFC 2022, p. 8 (impreso) | 672,025,093 | 672,025,093 | 672,025,093 | 0 |
| 2022 | Total pasivos corrientes | 231,944,180 — Cert. EFC 2022, p. 9 (impreso) | 231,944,180 | 231,944,180 | 231,914,180 / 231,944,180 | -30,000 |
| 2022 | Total pasivos no corrientes | 226,204,149 — Cert. EFC 2022, p. 9 (impreso) | 226,204,149 | 226,204,149 | (no presenta el importe) | — |
| 2022 | Total pasivos | 458,148,329 — Cert. EFC 2022, p. 9 (impreso) | 458,148,329 | 458,148,329 | 458,148,329 | 0 |
| 2022 | Total patrimonio | 213,876,764 — Cert. EFC 2022, p. 9 (impreso) | 213,876,764 | 213,876,764 | 213,876,764 | 0 |
| 2022 | Ingresos ordinarios | 499,653,494 — Cert. EFC 2022, p. 10 | 499,653,494 | 499,653,494 | 499,653,494 | 0 |
| 2022 | Costo de ventas | 410,331,156 — Cert. EFC 2022, p. 10 | 410,331,156 | 410,331,156 | 410,331,156 | 0 |
| 2022 | Utilidad bruta | 89,322,338 — Cert. EFC 2022, p. 10 (impreso) | 89,322,338 | 89,322,338 | 89,322,338 | 0 |
| 2022 | Gastos de operación (adm.+ventas+personal+dep.; criterio Tabla 5) | 58,057,208 — Cert. EFC 2022, p. 10 (suma de líneas) | — | 58,057,208 | 58,057,208 | 0 |
| 2022 | Utilidad de operación | 31,200,977 — Cert. EFC 2022: no impresa; derivada de partidas impresas | 31,200,977 | 31,200,977 | 31,200,000 / 31,200,977 | -977 |
| 2022 | Ingresos financieros | 0 — Cert. EFC 2022: no presentado | 0 | 0 | (no presenta el importe) | — |
| 2022 | Gastos financieros (como se presentan) | 17,181,342 — Cert. EFC 2022, p. 10 | 17,181,342 | 17,181,342 | (no presenta el importe) | — |
| 2022 | Utilidad antes de impuestos | 14,019,635 — Cert. EFC 2022, p. 10 (impreso) | 14,019,635 | 14,019,635 | (no presenta el importe) | — |
| 2022 | Impuesto sobre la renta | 3,960,325 — Cert. EFC 2022, p. 10 | 3,960,325 | 3,960,325 | (no presenta el importe) | — |
| 2022 | Utilidad neta | 10,059,310 — Cert. EFC 2022, p. 10 (impreso) | 10,059,310 | 10,059,310 | 10,059,310 | 0 |
| 2023 | Total activos corrientes | 429,794,544 — Cert. EFC 2023, p. 7 (impreso) | 429,794,544 | 429,794,544 | 429,794,544 / 541,094,544 | +111,300,000 |
| 2023 | Total activos no corrientes | 379,306,402 — Cert. EFC 2023, p. 7 (impreso) | 379,306,402 | 379,306,402 | (no presenta el importe) | — |
| 2023 | Total activos | 809,100,946 — Cert. EFC 2023, p. 7 (impreso) | 809,100,946 | 809,100,946 | 809,100,946 | 0 |
| 2023 | Total pasivos corrientes | 333,120,685 — Cert. EFC 2023, p. 7 (impreso) | 333,120,685 | 333,120,685 | 333,120,685 / 342,120,685 | +9,000,000 |
| 2023 | Total pasivos no corrientes | 248,306,867 — Cert. EFC 2023, p. 8 (impreso) | 248,306,867 | 248,306,867 | (no presenta el importe) | — |
| 2023 | Total pasivos | 581,427,552 — Cert. EFC 2023, p. 8 (impreso) | 581,427,552 | 581,427,552 | 581,427,552 | 0 |
| 2023 | Total patrimonio | 227,673,394 — Cert. EFC 2023, p. 8 (impreso) | 227,673,394 | 227,673,394 | 227,673,394 | 0 |
| 2023 | Ingresos ordinarios | 478,623,072 — Cert. EFC 2023, p. 9 | 478,623,072 | 478,623,072 | 478,623,072 | 0 |
| 2023 | Costo de ventas | 373,545,631 — Cert. EFC 2023, p. 9 | 373,545,631 | 373,545,631 | 373,545,631 | 0 |
| 2023 | Utilidad bruta | 105,077,441 — Cert. EFC 2023, p. 9 (impreso) | 105,077,441 | 105,077,441 | 105,077,441 | 0 |
| 2023 | Gastos de operación (adm.+ventas+personal+dep.; criterio Tabla 5) | 63,602,388 — Cert. EFC 2023, p. 9 (suma de líneas) | — | 63,602,388 | 63,602,388 | 0 |
| 2023 | Utilidad de operación | 44,689,021 — Cert. EFC 2023: no impresa; derivada de partidas impresas | 44,689,021 | 44,689,021 | 44,689,021 | 0 |
| 2023 | Ingresos financieros | 0 — Cert. EFC 2023: no presentado | 0 | 0 | (no presenta el importe) | — |
| 2023 | Gastos financieros (como se presentan) | 22,016,927 — Cert. EFC 2023, p. 9 | 22,016,927 | 22,016,927 | (no presenta el importe) | — |
| 2023 | Utilidad antes de impuestos | 22,672,094 — Cert. EFC 2023, p. 9 (impreso) | 22,672,094 | 22,672,094 | (no presenta el importe) | — |
| 2023 | Impuesto sobre la renta | 9,341,414 — Cert. EFC 2023, p. 9 | 9,341,414 | 9,341,414 | (no presenta el importe) | — |
| 2023 | Utilidad neta | 13,330,680 — Cert. EFC 2023, p. 9 (impreso) | 13,330,680 | 13,330,680 | 13,330,680 | 0 |
| 2024 | Total activos corrientes | 432,771,678 — EEFF dic-2024, p. 1 (impreso) | 432,771,678 | 432,771,678 | 432,771,678 | 0 |
| 2024 | Total activos no corrientes | 394,404,696 — EEFF dic-2024, p. 1 (impreso) | 394,404,696 | 394,404,696 | (no presenta el importe) | — |
| 2024 | Total activos | 827,176,374 — EEFF dic-2024, p. 1 (impreso) | 827,176,374 | 827,176,374 | 827,176,374 | 0 |
| 2024 | Total pasivos corrientes | 362,966,215 — EEFF dic-2024, p. 1 (impreso) | 362,966,215 | 362,966,215 | 362,966,215 | 0 |
| 2024 | Total pasivos no corrientes | 238,148,371 — EEFF dic-2024, p. 1 (impreso) | 238,148,371 | 238,148,371 | (no presenta el importe) | — |
| 2024 | Total pasivos | 601,114,586 — EEFF dic-2024, p. 1 (impreso) | 601,114,586 | 601,114,586 | 601,114,586 | 0 |
| 2024 | Total patrimonio | 226,061,788 — EEFF dic-2024, p. 1 (impreso) | 226,061,788 | 226,061,788 | 226,061,788 | 0 |
| 2024 | Ingresos ordinarios | 479,006,719 — EEFF dic-2024, p. 2 | 479,006,719 | 479,006,719 | 479,006,719 | 0 |
| 2024 | Costo de ventas | 377,459,424 — EEFF dic-2024, p. 2 | 377,459,424 | 377,459,424 | 377,459,424 | 0 |
| 2024 | Utilidad bruta | 101,547,295 — EEFF dic-2024, p. 2 (impreso) | 101,547,295 | 101,547,295 | 101,547,295 | 0 |
| 2024 | Gastos de operación (adm.+ventas+personal+dep.; criterio Tabla 5) | 66,353,377 — EEFF dic-2024, p. 2 (suma de líneas) | — | 66,353,377 | 66,353,377 | 0 |
| 2024 | Utilidad de operación | 35,193,918 — EEFF dic-2024, p. 2 (impreso) | 35,193,918 | 35,193,918 | 35,193,918 | 0 |
| 2024 | Ingresos financieros | 15,024,973 — EEFF dic-2024, p. 2 | 15,024,973 | 15,024,973 | (no presenta el importe) | — |
| 2024 | Gastos financieros (como se presentan) | 43,089,283 — EEFF dic-2024, p. 2 | 43,089,283 | 43,089,283 | (no presenta el importe) | — |
| 2024 | Utilidad antes de impuestos | 7,185,178 — EEFF dic-2024, p. 2 (impreso) | 7,185,178 | 7,185,178 | (no presenta el importe) | — |
| 2024 | Impuesto sobre la renta | 4,124,197 — EEFF dic-2024, p. 2 | 4,124,197 | 4,124,197 | (no presenta el importe) | — |
| 2024 | Utilidad neta | 3,060,981 — EEFF dic-2024, p. 2 (impreso) | 3,060,981 | 3,060,981 | 3,060,981 | 0 |
| 2025 | Total activos corrientes | 247,705,981 — EEFF dic-2025, p. 1 (impreso) | 247,705,981 | 247,705,981 | 247,705,981 | 0 |
| 2025 | Total activos no corrientes | 534,343,580 — EEFF dic-2025, p. 1 (impreso) | 534,343,580 | 534,343,580 | (no presenta el importe) | — |
| 2025 | Total activos | 782,049,561 — EEFF dic-2025, p. 1 (impreso) | 782,049,561 | 782,049,561 | 782,049,561 | 0 |
| 2025 | Total pasivos corrientes | 371,274,007 — EEFF dic-2025, p. 1 (impreso) | 371,274,007 | 371,274,007 | 371,274,007 | 0 |
| 2025 | Total pasivos no corrientes | 179,615,356 — EEFF dic-2025, p. 1 (impreso) | 179,615,356 | 179,615,356 | (no presenta el importe) | — |
| 2025 | Total pasivos | 550,889,363 — EEFF dic-2025, p. 1 (impreso) | 550,889,363 | 550,889,363 | 550,889,363 | 0 |
| 2025 | Total patrimonio | 231,160,198 — EEFF dic-2025, p. 1 (impreso) | 231,160,198 | 231,160,198 | 231,160,198 | 0 |
| 2025 | Ingresos ordinarios | 439,704,567 — EEFF dic-2025, p. 2 | 439,704,567 | 439,704,567 | 439,704,567 | 0 |
| 2025 | Costo de ventas | 331,430,173 — EEFF dic-2025, p. 2 | 331,430,173 | 331,430,173 | 331,430,173 | 0 |
| 2025 | Utilidad bruta | 108,274,394 — EEFF dic-2025, p. 2 (impreso) | 108,274,394 | 108,274,394 | 108,274,394 | 0 |
| 2025 | Gastos de operación (adm.+ventas+personal+dep.; criterio Tabla 5) | 53,608,750 — EEFF dic-2025, p. 2 (suma de líneas) | — | 53,608,750 | 53,608,750 | 0 |
| 2025 | Utilidad de operación | 54,665,644 — EEFF dic-2025, p. 2 (impreso) | 54,665,644 | 54,665,644 | 54,665,644 | 0 |
| 2025 | Ingresos financieros | 14,515,895 — EEFF dic-2025, p. 2 | 14,515,895 | 14,515,895 | (no presenta el importe) | — |
| 2025 | Gastos financieros (como se presentan) | 51,914,906 — EEFF dic-2025, p. 2 | 51,914,906 | 51,914,906 | 51,914,906 | 0 |
| 2025 | Utilidad antes de impuestos | 16,455,062 — EEFF dic-2025, p. 2 (impreso) | 16,455,062 | 16,455,062 | (no presenta el importe) | — |
| 2025 | Impuesto sobre la renta | 4,556,075 — EEFF dic-2025, p. 2 | 4,556,075 | 4,556,075 | (no presenta el importe) | — |
| 2025 | Utilidad neta | 11,898,987 — EEFF dic-2025, p. 2 (impreso) | 11,898,987 | 11,898,987 | 11,898,987 | 0 |

Notas:

- Utilidad de operación 2022 y 2023: los estados combinados no la imprimen. Derivación de 2022 (Cert. EFC 2022, p. 10): 89,322,338 − 18,344,656 − 39,712,552 − 397,016 + 332,863 = 31,200,977. Se concilia con la «Ganancia antes de ISR» impresa: 31,200,977 − 17,181,342 = 14,019,635.
- Gastos financieros 2021–2023: el documento solo presenta el neto («Gastos financieros (neto)»); los ingresos financieros no se presentan por separado (0 en la app).

## 6. Errores de transcripción

**Ninguno en la aplicación.** Todas las cifras de SQLite coinciden con los documentos (§5).

En el **documento académico** hay cuatro cifras base que no corresponden a los estados auditados (§9, F‑02 a F‑05). No son errores de transcripción de la app: la app nunca las registró.

## 7. Errores de clasificación

| Cuenta | Documento y página | Clasificación en la app (`account.grupo_analisis`) | Evaluación |
|---|---|---|---|
| Efectivo / Efectivo y equivalentes (CB1101, CN1101) | Cert. 2021 p. 8 … EEFF 2025 p. 1 | `EFECTIVO` | Correcta. |
| CDs a plazo e inversiones en bonos corrientes (CB1102–CB1103); «Inversiones» corrientes (CN1102) | ídem | `INVERSIONES_CP` (entran en la tesorería) | Correcta; el trabajo hace lo mismo en 9.1. |
| CxC comerciales (CB1104) / Deudores comerciales y otras CxC (CN1103) | ídem | `CXC_COMERCIALES` / `DEUDORES_COMERCIALES_OTRAS` | Correcta según la presentación. **Bases no homogéneas**: 2024–2025 incluye «otras» (ver F‑13). |
| Otras CxC corrientes (CB1106) | 2021–2023 | `OTRAS_CXC_CP` | Correcta. |
| CxC a partes relacionadas CP (CB1105, CN1104) | 2021–2025 | `CXC_RELACIONADAS_CP` | Correcta (así se denominan). |
| CxC a partes relacionadas LP (CB1202 2023: 110,380,709; CN1203 2025: 262,128,668) | Cert. 2023 p. 7; EEFF 2025 p. 1 | `CXC_RELACIONADAS_LP` | Correcta. |
| **«Otras cuentas por cobrar a LP» 2024 (CN1202: 118,684,551)** | EEFF 2024 p. 1 | `OTRAS_CXC_LP` | **Correcta según la denominación impresa.** El resumen PCR (p. 8) también la presenta a dic‑24 como «Cuentas por cobrar de LP» (119.7 = 0.98 + 118.68), con «Cuentas por cobrar a partes relacionadas» LP en **0.0**. La **contraparte económica no es verificable**. El trabajo la trata como relacionada (F‑07): sin respaldo. |
| Inventarios | todas | `INVENTARIOS` | Correcta. |
| Préstamos CP/LP, arrendamientos, bonos, certificados de inversión, titularizaciones, documentos por pagar, «Obligaciones emisión de títulos valores» y «Otros pasivos financieros» | todas | Grupos `*_CP`/`*_LP` de tipo FINANCIERO | Correcta como deuda. Que los «Otros pasivos financieros» devenguen interés es un **supuesto no verificable**. |
| CxP comerciales (CB2108) / Acreedores comerciales y otras CxP (CN2105) | todas | `CXP_COMERCIALES` / `ACREEDORES_COMERCIALES_OTRAS` | Correcta según la presentación; **bases no homogéneas** (F‑13). |
| Provisiones (CN2205) | EEFF 2024–2025 p. 1, bajo «Pasivos no circulantes» | `PROVISIONES_LP` (operativo) | Correcta. |
| Pasivo por prima en venta de acciones de subsidiaria (CB2208) | Cert. 2022–2023 | `PRIMA_VENTA_ACCIONES` (operativo, costo 0) | Clasificación de balance correcta; el costo 0 en el WACC es un supuesto. |
| Participaciones no controladoras (CB3107: 3,263,361; 4,892,562; «–» en 2023) | Cert. 2021 p. 9, 2022 p. 9 y 2023 p. 8 | `NO_CONTROLADORAS` | Correcta. Patrimonio de la controladora = total − NCI, igual al impreso en 2021 (142,057,829) y 2022 (208,984,202). |
| Reservas y efecto de conversión | 2021–2025 | `OTRAS_RESERVAS` (2021–2023), `RESERVAS_CAPITAL` y `EFECTO_CONVERSION` (2024–2025) | Correcta. El cambio de grupo entre 2023 y 2024 es de presentación, no un error. |

## 8. Errores de fórmulas e implementación

**No se encontraron errores de fórmula ni de implementación.** Fórmulas inspeccionadas (`.venv/calculations/indicadores.py`, salvo indicación) y verificadas con recálculo independiente:

| Grupo | Fórmula en el código | Saldos | Verificación |
|---|---|---|---|
| Capital de trabajo | `_ctn`: AC − PC; `_razon_corriente`: AC/PC; `_prueba_acida`: (AC − INVENTARIOS)/PC | Cierre | Exacto, 5 años. |
| Tesorería y fondo de maniobra | (EFECTIVO + INVERSIONES_CP)/PC × 100; PAT + PNC − ANC | Cierre | Exacto. El fondo de maniobra a largo plazo = CTN en los 5 años (identidad contable). |
| Horizontal | `comparativo.variacion`: Vt − Vt−1 y (Vt − Vt−1)/Vt−1 × 100; base = año anterior inmediato; base 0 o negativa → «no calculable» con motivo | — | Correcto; no inventa porcentajes. |
| Vertical | `comparativo.vertical_comparativo` y `vertical_analysis.py`: BG / activo total y ER / ingresos ordinarios, con signo | — | Correcto; denominadores verificados. El módulo antiguo redondea a 2 decimales al presentar. |
| Actividad | Rotación inv. = CV/INV; PPI = INV/CV × 365; rotación CxC = ING/CxC; PPC = CxC/ING × 365; PPP = CxP/CV × 365; CO = PPI + PPC; CCE = CO − PPP. **No existe rotación de CxP** (solo PPP), igual que en el trabajo. | Cierre, uniforme en los 5 años | Fórmulas correctas. Las **bases** de CxC y CxP no son homogéneas (F‑13). |
| Endeudamiento | TP/TA × 100; TP/PAT; PC/TP × 100; cobertura = UO/(GF − IF), gastos financieros netos; cobertura bruta solo 2024–2025 | Cierre | Exacto. |
| Rentabilidad | Márgenes sobre ingresos; ROA = UN/TA; ROE = UN/PAT total (con NCI) | Cierre | Exacto. Utilidad y patrimonio son coherentes (ambos totales). |
| DuPont al cierre | RSA = margen × rotación; RSP = RSA × MAF; MAF = TA/PAT | Cierre | La identidad se cumple exactamente: RSP DuPont = UN/PAT en los 5 años. |
| DuPont antiguo (`dupont.py`) | Rotación = ING/TA promedio; multiplicador = TA prom./PAT prom.; ROE = UN/PAT prom. | **Promedio** (2021: saldo final como aproximación, advertida) | Correcto según su propia definición; identidad DuPont verificada. ROE redondeado a 2 decimales al presentar. |
| WACC (`wacc.py`) | V = TP + PAT; operativos con costo 0; deuda con tasa × (1 − t); Ke = UN/PAT | Cierre | Aritmética exacta con los supuestos (F‑10 a F‑12). |
| Origen y aplicación (`fuentes_usos.py`) | Variación por grupo; activo: disminución = fuente; pasivo y patrimonio: aumento = fuente | Balances de los 2 ejercicios | Totales iguales en los 4 pares (2022: 287,901,712; 2023: 209,290,574; 2024: 674,042,845; 2025: 408,447,177). |

## 9. Errores del documento académico

Ver la matriz (§12), filas F‑02 a F‑08 y F‑15 a F‑19. El detalle de los hallazgos solicitados es el siguiente.

**Hallazgo 1 — Activo corriente 2023 (F‑02).** El documento dice 429,794,544 (Cert. EFC 2023, p. 7, «Total activos corrientes»); el trabajo usa 541,094,544 en las Tablas 3, 4, 6 y 7 (MD L498, L511, L541 y L563–564; PDF p. 22–27).

- **Origen probable:** el resumen *no auditado* de PCR (`SV-CIALUTECH-202506.pdf`, p. 8) presenta «Total del activo corriente» dic‑23 = 541.1 M. Sus indicadores (p. 9: liquidez 1.6, ácida 1.2, CTN 199.1) son los que reproduce la Tabla 6 (1.58, 1.17 y 198,973,859).
- La cifra del trabajo conserva los dígitos inferiores de la auditada: 541,094,544 − 429,794,544 = 111,300,000 exactos. Es un **híbrido** entre las dos fuentes.
- PCR presenta otra versión de 2023, que no coincide con la auditada: total activo 818.1 frente a 809.1, patrimonio 249.1 frente a 227.7 y utilidad neta 17.2 frente a 13.3.
- **Primer punto de la diferencia:** la elaboración del trabajo, no la app.

**Hallazgo 2 — Pasivo corriente 2023 (F‑03).** El documento dice 333,120,685 (Cert. 2023, p. 7); el trabajo usa 342,120,685 (mismas tablas). PCR p. 8 da 342.1; la diferencia exacta es de 9,000,000. Es el mismo origen híbrido que F‑02.

**Hallazgo 3 — Pasivo corriente 2022 (F‑04).** El documento dice 231,944,180 (Cert. 2022, p. 9); el trabajo usa 231,914,180 en las Tablas 3, 6 y 7. Es una transposición de dígitos (−30,000). PCR p. 8 da 231.9, compatible con ambas cifras. El trabajo usa la cifra correcta en 9.1 y 9.2.1.

**Hallazgo 4 — Utilidad de operación 2022 (F‑05).** El valor respaldado es **31,200,977**, derivado de las partidas impresas y conciliado con la UAI impresa (§5). El trabajo usa 31,200,000\* en la Tabla 5; coincide con PCR p. 8 (31.2 M). Es un **redondeo o una toma de fuente secundaria**, no un error de cálculo. El trabajo usa 31,200,977 en 8.3 B y 8.4. No afecta a la variación presentada (−69.88 % con ambas cifras).

**Hallazgo 5 — Cuentas por cobrar 2023 (F‑06).** En 8.2 B (MD L753, PDF p. 34) el trabajo usa 96,097,483 = 41,272,525 (comerciales) + 54,824,958 (otras), Cert. 2023 p. 6. En 2021–2022 usa solo las comerciales, y en 9.3 (p. 52) usa 41,272,525 para 2023. Es una **inconsistencia metodológica interna del trabajo**.

- Para una serie homogénea 2021–2025 debe usarse «comerciales + otras», porque 2024–2025 no permite separarlas: rotación 2023 = 4.98, PPC = 73.28.
- Si se quiere aislar la cartera comercial, solo es posible en 2021–2023.
- La app calcula ambas bases (`rotacion_cxc`/`ppc` con la línea presentada; `rotacion_cxc_total`/`ppc_total` homogéneas).

**Hallazgo 6 — CxC a largo plazo 2024 (F‑07).** Ver §7.

- La documentación permite clasificarla como «otras cuentas por cobrar a largo plazo» (EEFF 2024 p. 1; PCR p. 8: relacionadas LP 0.0 a dic‑24).
- **No permite afirmar ni descartar que la contraparte sea relacionada**: no verificable.
- El trabajo (9.7, MD L1784 y L1819; PDF p. 75–76) la llama «Cuentas por cobrar empresas relacionadas a LP» y compensa: variación +143,444,117 (uso). La app presenta dos movimientos: fuente de 118,684,551 en «otras» y uso de 262,128,668 en «relacionadas LP».
- Con la clasificación respaldada, los totales 2025/2024 son 408,447,177 (el trabajo da 289,762,626) y el aumento neto de relacionadas CP+LP es 157,470,488 (el trabajo da 38,785,937).
- En ambos casos fuentes = usos (se verificó la igualdad).

**Hallazgo 7 — Utilidad de la controladora 2023 (F‑08).** El mismo documento (Cert. EFC 2023) es contradictorio:

- **Estado de resultados (p. 9):** «Utilidad neta atribuible a: Propietarios de la controladora 13,330,680; Participaciones no controladoras –».
- **Estado de cambios en el patrimonio (p. 11):** ganancia neta del año atribuible a la controladora 12,309,102 y a las no controladoras 1,021,578 (total 13,330,680).

La app (dato complementario `utilidad_controladora_ecp`) y el trabajo usan 12,309,102. Consecuencias en 2023:

| Indicador (controladora) | Con 12,309,102 (estado de cambios en el patrimonio) | Con 13,330,680 (estado de resultados) |
|---|---|---|
| Margen neto | 2.57 % | 2.79 % |
| RSA | 1.52 % | 1.65 % |
| RSP | 5.41 % | 5.86 % |

Cuál es la cifra correcta **no es verificable** sin las notas. El patrimonio de la controladora 2023 = total (227,673,394), porque las NCI al cierre son 0.

**Hallazgo 8 — DuPont (F‑09).** Es una **diferencia metodológica, no un error**. La identidad DuPont se cumple en ambas versiones.

| Año | Rotación al cierre (trabajo = app, Indicadores) | Rotación promedio (app, «Análisis DuPont») | MAF al cierre | Multiplicador promedio | ROE al cierre | ROE promedio |
|---|---:|---:|---:|---:|---:|---:|
| 2021 | 0.9459 | 0.9459 (aprox.: no hay 2020) | 3.8119 | 3.8119 | 47.21 % | 47.21 % |
| 2022 | 0.7435 | 0.8151 | 3.1421 | 3.4131 | 4.70 % | 5.60 % |
| 2023 | 0.5915 | 0.6463 | 3.5538 | 3.3544 | 5.86 % | 6.04 % |
| 2024 | 0.5791 | 0.5855 | 3.6591 | 3.6062 | 1.35 % | 1.35 % |
| 2025 | 0.5622 | 0.5465 | 3.3831 | 3.5196 | 5.15 % | 5.20 % |

El trabajo usa saldos al cierre (8.4 y 9.5–9.6). La página «Indicadores › DuPont (saldos al cierre)» de la app coincide con él en los 5 años.

**Hallazgo 9 — WACC (F‑10 a F‑12).**

| Elemento | Valor usado (trabajo y app) | Respaldo |
|---|---|---|
| Importes y pesos de cada fuente | Saldos del balance | **Documentado** (coinciden con los originales). |
| Clasificación operativo (costo 0) / financiero | Por denominación | Documentado en cuanto a la denominación. El costo 0 de los pasivos operativos es un **supuesto**. |
| Préstamos 7.50 %, arrendamientos 8.00 % (8.50 % CP en 2022), bonos 7.25 %, certificados 7.34 %, titularizaciones 6.90 %, documentos 6.75 % (2021–2023) | — | **No verificable**: el trabajo cita notas 18–25 del informe auditado completo, que no están en `documentos/` (las certificaciones disponibles no traen esas notas). Sin cita para 2022–2023. |
| Títulos valores 7.20 % y otros pasivos financieros 6.75 % (2024–2025) | — | **No verificable** y sin cita. Única evidencia parcial: tramos de CIALUTECH1 (PCR p. 7) del 7.50 % al 9.50 %, promedio ponderado del **8.4 %** sobre USD 30.2 M al 30‑06‑2025, superior al 7.20 % supuesto. Los tramos 1 y 2 (USD 16 M al 7.50 %) son compatibles con el 7.50 % sobre 16 M que el trabajo cita para 2021. |
| ISR 30 % | — | **No verificable**. Tasas efectivas de los estados: 16.13 % (2021), 28.25 %, 41.20 %, 57.40 % y 27.69 % (2025). |
| Ke = ROE al cierre | 47.21 %, 4.70 %, 5.86 %, 1.35 %, 5.15 % | El cálculo es verificable, pero **no es una metodología justificable de costo del patrimonio**: es un rendimiento contable, no la rentabilidad exigida (CAPM u otra). Da Ke < Kd neto en 2022 (4.70 < 5.26), 2024 (1.35 < 5.19) y 2025 (5.15 < 5.17), lo que contradice que el patrimonio es más riesgoso que la deuda. |
| Ponderación | V = pasivo total + patrimonio (incluye pasivos operativos sin costo, a valor en libros) | Es una **elección metodológica** que reduce el WACC. Con solo la deuda con costo y el patrimonio, mismas tasas y Ke, el WACC sería 21.36 %, 5.03 %, 5.47 %, 3.69 % y 5.16 %, frente a 14.59 %, 3.83 %, 3.87 %, 2.58 % y 3.85 %. Este cálculo ilustra la sensibilidad; no es una cifra validada. |

**Hallazgo 10 — Origen y aplicación de fondos (F‑07).**

- **2023/2022:** las 47 líneas y los totales (209,290,574) coinciden entre el trabajo, la app y el recálculo.
- **2025/2024:** 36 de 37 líneas coinciden. La única diferencia es la clasificación de CN1202, que arrastra los totales y el texto de «aumento neto».
- Todas las variaciones se calcularon con los balances de los dos ejercicios comparados. La regla de signos es correcta en ambas fuentes.
- La app compara por grupo de análisis. Esto evita confundir cambios de denominación, pero hace que la cuenta «otras CxC LP» aparezca como línea propia.

**Otros errores académicos (§12):**

- PPC 2025 presentado como 58.3 (correcto: 58.25).
- WACC 2023: 3.88 % en la tabla y 3.87 % en el texto.
- Truncamientos (50.40 %, 73.76 % y 26.24 %).
- Tipografías (denominador 553,995,185; «68,602.739»; título de 6.4 «estado de resultados» para una tabla del balance; «2021-20252»).
- En 8.2 C se declara que no es viable calcular el PPP, pero 9.3 lo calcula.
- En 8.4 C se citan gastos financieros brutos (51,914,906), mientras el resto del trabajo usa los netos (37,399,011).

## 10. Diferencias metodológicas

| ID | Tema | Criterio A | Criterio B | Efecto |
|---|---|---|---|---|
| F‑09 | DuPont | Saldos al cierre (trabajo; app, Indicadores) | Saldos promedio (app, «Análisis DuPont») | ROE 2022: 4.70 % frente a 5.60 %; 2023: 5.86 % frente a 6.04 %. |
| F‑11 | WACC | Ke = ROE; V incluye pasivos operativos sin costo (trabajo y app) | Estructura con deuda con costo y Ke de mercado | WACC 1.1 a 6.8 p.p. menor; Ke < Kd en 3 años. |
| F‑13 | Bases de CxC y CxP en actividad | Línea presentada: 2021–2023 solo comerciales; 2024–2025 comerciales + otras (trabajo 9.3 y app `ppc`, `ppp`, `cce`) | Base homogénea comerciales + otras en los 5 años | Ver la tabla siguiente. **La conclusión del trabajo de que el CCE es negativo desde 2023 no se sostiene con la base homogénea en 2023.** |
| F‑18 | Presentación del Estado de Resultados | 2021–2023: gasto financiero neto y otros ingresos dentro de la operación | 2024–2025: ingresos y gastos financieros brutos y otros ingresos después del resultado financiero | El vertical y la cobertura no son estrictamente comparables entre 2023 y 2024 (estados combinados frente a consolidados). |

**Efecto de F‑13 en el ciclo de conversión del efectivo** (días):

| Año | PPC (línea presentada) | PPC (base homogénea) | PPP (línea presentada) | PPP (base homogénea) | CCE (línea presentada) | CCE (base homogénea) |
|---|---:|---:|---:|---:|---:|---:|
| 2021 | 36.98 | 82.19 | 155.65 | 164.23 | 28.86 | 65.49 |
| 2022 | 23.80 | 62.11 | 85.95 | 93.83 | 63.33 | 93.76 |
| 2023 | 31.47 | 73.28 | 191.12 | 202.98 | **−21.40** | **+8.56** |
| 2024 | 74.07 | 74.07 | 217.70 | 217.70 | −30.72 | −30.72 |
| 2025 | 58.25 | 58.25 | 190.66 | 190.66 | −55.52 | −55.52 |

## 11. Datos no verificables

| Dato | Motivo |
|---|---|
| Tasas de interés de cada fuente de deuda (2021–2025) | No hay notas con tasas en `documentos/`. Solo existe la evidencia parcial de CIALUTECH1 (PCR p. 7). |
| ISR del 30 % | No figura en los estados. Las tasas efectivas van del 16 % al 57 %. |
| Costo del patrimonio como costo exigido | El ROE no lo es; no hay datos de mercado (beta, prima ni precio de las acciones). |
| Contraparte de CN1202 (2024, 118,684,551) | La denominación no indica relacionadas; sin notas, la contraparte es desconocida. |
| Utilidad de la controladora 2023 (12,309,102 o 13,330,680) | Contradicción entre las págs. 9 y 11 del mismo documento. |
| Por qué PCR presenta otro balance 2023 | PCR declara usar estados auditados 2019–2024, pero su dic‑23 no coincide con la certificación auditada. |
| EPS, P/E y M/L | No hay número de acciones ni precio de mercado de las acciones. |
| Cobertura de pagos fijos | Faltan las cuotas de arrendamiento y la amortización del principal. |

## 12. Matriz general de hallazgos

| ID | Año | Módulo o sección | Cuenta o indicador | Valor original | Valor encontrado | Diferencia | Tipo de hallazgo | Origen del error | Impacto | Gravedad | Evidencia |
|---|---|---|---|---:|---:|---:|---|---|---|---|---|
| F‑01 | Todos | Estructura del proyecto | Carpeta `calculations/` | `calculations/` (14 módulos) | `.venv/calculations/` | — | Integridad estructural | Movimiento de carpeta el 2026-11-03 a las 10:50 (no realizado por estas auditorías) | La app depende del `sys.path` del venv; falla con otro intérprete. 7 módulos sin seguimiento quedan en una carpeta ignorada (riesgo de pérdida). `git` registra 7 borrados. | **Crítico** | §2; `git status`; `python -B -c "import calculations"` con el venv y con el Python global. |
| F‑02 | 2023 | Trabajo, Tablas 3, 4, 6 y 7; 6.5 | Total activo corriente | 429,794,544 | 541,094,544 | +111,300,000 (+25.90 %) | Error académico (de origen) | Cifra de PCR no auditada (541.1 M) combinada con los dígitos inferiores de la auditada | Var. AC 2022→23 +20.60 % (real −4.21 %); 2023→24 −20.02 % (real +0.69 %), **signo invertido**. CTN 2023 198,973,859 (real 96,673,859); RC 1.58 (1.29); PA 1.17 (0.87); var. CTN 2023 y 2024; narrativa de 6.5, puntos 2 y 3. Correctos: 7.2, 8.1 y 9.1–9.2. | **Crítico** | Cert. EFC 2023 p. 7; PCR p. 8–9; MD L498 y L511 (PDF p. 22–23). |
| F‑03 | 2023 | Trabajo, Tablas 3, 4, 6 y 7 | Total pasivo corriente | 333,120,685 | 342,120,685 | +9,000,000 (+2.70 %) | Error académico (de origen) | Igual que F‑02 (PCR 342.1) | Var. PC 2022→23 +47.52 % (real +43.62 %); 2023→24 +6.09 % (real +8.96 %); CTN, RC y PA 2023. | **Alto** | Cert. EFC 2023 p. 7; PCR p. 8; MD L499 y L512. |
| F‑04 | 2022 | Trabajo, Tablas 3, 6 y 7 | Total pasivo corriente | 231,944,180 | 231,914,180 | −30,000 (−0.01 %) | Error académico (transcripción) | Transposición de dígitos | CTN 2022 216,758,221 (real 216,728,221); var. CTN 2022 y 2023; var. PC 2022. Inmaterial en las razones. | Medio | Cert. EFC 2022 p. 9; MD L499 y L540. |
| F‑05 | 2022 | Trabajo, Tabla 5 | Utilidad de operación | 31,200,977 (derivada) | 31,200,000\* | −977 | Error académico (redondeo o fuente secundaria) | PCR p. 8 (31.2 M) | Ninguno en los porcentajes. | Bajo | Cert. EFC 2022 p. 10; MD L527. |
| F‑06 | 2023 | Trabajo, 8.2 B | Base de CxC; rotación; PPC | 41,272,525 (comerciales) | 96,097,483 | +54,824,958 | Error académico (clasificación o base) | Suma de «otras CxC» solo en 2023 | Rotación 4.98 frente a 11.60; PPC 73.3 frente a 31.5; texto de 8.2 B. | Medio | Cert. EFC 2023 p. 6; MD L753 y L1283. |
| F‑07 | 2024–2025 | Trabajo 9.7 | «Otras CxC a LP» (CN1202) | 118,684,551 como «otras CxC LP» | Tratada como «CxC relacionadas LP» | Totales 289,762,626 frente a 408,447,177 (−118,684,551) | Error académico de clasificación; contraparte no verificable | Equivalencia por comportamiento, no por denominación | Línea de relacionadas LP, totales de fuentes y usos y «aumento neto» 38,785,937 (frente a 157,470,488). | **Alto** | EEFF 2024 p. 1; PCR p. 8; MD L1784, L1813 y L1819. |
| F‑08 | 2023 | Documento fuente; app y trabajo 9.6 | Utilidad atribuible a la controladora | 13,330,680 (ER p. 9) / 12,309,102 (ECP p. 11) | 12,309,102 | −1,021,578 | Dato no verificable (contradicción en el documento fuente) | Cert. EFC 2023 | Margen, RSA y RSP de la controladora 2023. | No verificable | Cert. EFC 2023 p. 9 y 11; MD L1742. |
| F‑09 | 2022–2025 | App, `dupont.py` («Análisis DuPont») frente al trabajo | Rotación, multiplicador y ROE | Al cierre | Promedio | p. ej., ROE 2022 4.70 % frente a 5.60 % | Diferencia metodológica | Criterio de diseño del reporte antiguo | Dos ROE distintos para el mismo año en la app. | Medio | §9, Hallazgo 8. |
| F‑10 | 2021–2025 | Trabajo 9.4; `fuentes/anf/supuestos_wacc.json` | Tasas de interés por fuente | No documentadas | 6.75 %–8.50 % | — (evidencia parcial: 8.4 % CIALUTECH1 frente a 7.20 %) | Dato no verificable | Notas de auditoría no disponibles; sin cita para 2022–2025 | Costo de la deuda, WACC, spread y diagnóstico. | No verificable | PCR p. 7; MD L1357–1549. |
| F‑11 | 2021–2025 | Trabajo 9.4; app `wacc.py` | Ke y estructura del WACC | — | Ke = ROE; V incluye pasivos operativos | WACC 1.1 a 6.8 p.p. menor que con deuda con costo + patrimonio | Diferencia metodológica (criterio débil) | Diseño del trabajo, reproducido por la app | Conclusiones del WACC y del spread; Ke < Kd en 2022, 2024 y 2025. | **Alto** | §9, Hallazgo 9. |
| F‑12 | 2021–2025 | Trabajo 9.4; app | Tasa de ISR 30 % | No documentada (efectivas 16.1 %–57.4 %) | 30 % | — | Dato no verificable | Supuesto | Escudo fiscal del costo de la deuda. | No verificable | Estados de resultados (ISR/UAI). |
| F‑13 | 2021–2025 | Trabajo 9.3 y 8.2; app `indicadores.py` (`ppc`, `ppp`, `cce`; rubros `CXC_COMERCIALES_PRESENTADA` y `CXP_COMERCIALES_PRESENTADA`) | PPC, PPP y CCE | Base homogénea: CCE 2023 = +8.56 | −21.40 | +29.96 días | Diferencia metodológica (bases mezcladas) | Cambio de presentación 2023→2024 no homogeneizado | Conclusión del trabajo sobre el CCE negativo desde 2023 (9.3 y 11) y serie de PPC y PPP. La app documenta la nota, pero su CCE principal mezcla bases y no ofrece PPP ni CCE homogéneos. | **Alto** | §10; Cert. 2021–2023 p. 6–8; EEFF 2024–2025 p. 1. |
| F‑14 | 2021 | SQLite | 18 importes 0.00 de cuentas del catálogo estándar | — | 0.00 sin fuente | 0 | Datos de prueba conservados | Captura manual del 2026-11-01 (conservada por decisión del usuario) | Ninguno (suman 0); aparecen líneas en cero en los reportes de 2021. | Bajo | §5; `REGISTRO_DE_CAMBIOS.md` §9. |
| F‑15 | 2021–2025 | Trabajo, varias | PPC 2025, WACC 2023, 50.40 %, 73.76 % y 26.24 % | 58.25; 3.8745; 50.4053; 73.7666; 26.2334 | 58.3; 3.88 (3.87 en el texto); 50.40; 73.76; 26.24 | ≤ 1 unidad del último decimal | Error académico (redondeo) | Redondeo hacia arriba, suma de redondeados o truncamiento | Ninguno material. | Bajo | MD L755, L1471, L1475, L796 y L1385. |
| F‑16 | 2021 | Trabajo 6.4, 9.5 y 9.6 | Tipografías | 553,955,185 | 553,995,185; «68,602.739»; «2021-20252»; título 6.4 | — | Error académico (tipográfico) | Edición | Ninguno en los resultados. | Bajo | MD L489, L1623, L1635 y L1702. |
| F‑17 | — | Trabajo 8.2 C frente a 9.3 | PPP y CCE | — | 8.2 C: «no es viable calcular el PPP»; 9.3 lo calcula | — | Error académico (contradicción interna) | Redacción | Coherencia metodológica. | Bajo | MD L759 y L1287–1335. |
| F‑18 | 2021–2025 | Trabajo 7.1; app vertical | Gastos financieros y otros ingresos en el vertical | — | Neto (2021–2023) frente a bruto (2024–2025) | — | Diferencia de presentación de la fuente | Estados combinados frente a consolidados | Comparabilidad 2023→2024. | Bajo | MD L625–628. |
| F‑19 | 2025 | Trabajo 8.4 C frente a 6.7 y 10 | Gastos financieros citados | 37,399,011 (netos) | 51,914,906 (brutos) | — | Error académico (presentación) | Mezcla de bruto y neto | Ninguno en los indicadores. | Bajo | MD L913 y L1887. |
| F‑20 | 2022–2025 | App, `dupont.py` | ROE promedio | 5.6010 % (2022) | 5.60 % | Redondeo de presentación | Presentación (no es error) | `q2` al presentar | Ninguno. | Bajo | `recalculo`: 5 casos. |

**Resumen por gravedad:** Crítico 2 (F‑01 y F‑02) · Alto 4 (F‑03, F‑07, F‑11 y F‑13) · Medio 3 (F‑04, F‑06 y F‑09) · Bajo 8 (F‑05 y F‑14 a F‑20) · No verificable 3 (F‑08, F‑10 y F‑12).

## 13. Impacto financiero y académico

**Trazabilidad de cada error (primer punto donde aparece):**

| ID | Documento original | Transcripción a SQLite | Clasificación | Fórmula | App | Trabajo |
|---|---|---|---|---|---|---|
| F‑02 / F‑03 | Correcto (429,794,544 / 333,120,685) | Correcta | Correcta | Correcta | Correcto | **Error**: toma la cifra de PCR no auditada |
| F‑04 / F‑05 | Correcto | Correcta | Correcta | Correcta | Correcto | **Error**: transposición / redondeo |
| F‑06 | Correcto | Correcta | Correcta | Correcta | Correcto (con ambas bases) | **Error**: base cambiada solo en 2023 |
| F‑07 | Correcto («Otras CxC a LP») | Correcta | Correcta (`OTRAS_CXC_LP`) | Correcta | Correcto | **Error de clasificación** |
| F‑08 | **Contradictorio** | Correcta (las dos cifras registradas) | — | Correcta | Elige el estado de cambios en el patrimonio | Elige el estado de cambios en el patrimonio |
| F‑09 | — | — | — | Correcta | **Metodología distinta** (reporte antiguo) | Al cierre |
| F‑10 a F‑12 | **No contiene tasas** | Supuestos en un archivo separado | — | Aritmética correcta | Reproduce el supuesto | Supuesto |
| F‑13 | **Cambio de presentación** 2023→2024 | Correcta | Grupos correctos, rubro «presentado» heterogéneo | Correcta | Mezcla bases en `ppc`, `ppp` y `cce` | Mezcla bases |
| F‑01 | — | — | — | — | **Estructura del proyecto** | — |

**Resultados afectados y resultados que permanecen correctos:**

- **Afectados (trabajo):**
  - Tablas 3, 4, 6 y 7: AC y PC 2022–2023, sus variaciones, CTN, RC y PA 2023 y la variación del CTN 2022–2024; narrativa de 6.5 y párrafos que citan USD 541.09 M y 342.12 M; 6.8 («desde 2023 se observa…»).
  - 8.2 B (2023).
  - 9.3 y 11 (la afirmación del CCE negativo desde 2023, por F‑13).
  - 9.4 (WACC: magnitud y diagnóstico, por F‑10 a F‑12).
  - 9.6 (controladora 2023, por F‑08).
  - 9.7 2025/2024 (totales y párrafo de relacionadas).
- **Correctos (trabajo):** 7.1 y 7.2 (vertical completo); 8.1 (liquidez con 1.29 y 0.87); 8.2 A y D; 8.3; 8.4; 9.1; 9.2.1 y 9.2.2; 9.5 y 9.6 (enfoque total); 9.7 2023/2022; Tabla 5, salvo la UO 2022; columna de Alutech de la sección 10.
- **Conclusiones (11):** el CTN negativo de 2025, RC 0.67, PA 0.48, endeudamiento del 70.44 % y margen neto del 2.71 % son correctos. Las afirmaciones sobre el CCE negativo y el WACC requieren matizarse (F‑13 y F‑11).

## 14. Resultados correctos y validados

- **Datos:** 247/247 importes; 61/61 totales impresos; 5/5 balances cuadran; las utilidades derivadas concilian con las impresas en los 5 años.
- **Clasificaciones:** las 106 cuentas de Alutech tienen grupo de análisis coherente con su denominación impresa. CN1202 está correctamente clasificada según la documentación disponible.
- **Fórmulas e implementación:** las 39 definiciones de indicadores, el horizontal, el vertical, el DuPont (cierre y promedio), el WACC y el origen y aplicación de fondos están implementados correctamente. Se verificaron 1,183/1,188 recálculos exactos, y los 5 restantes difieren solo por el redondeo de presentación. Hay tratamiento explícito de ceros y negativos.
- **Presentación:** pantalla, Excel y PDF usan las mismas secciones. Los 195 valores de indicadores y las 7,326 celdas de Excel coinciden; no hay fórmulas en las celdas.
- **Pruebas:** 525/525 en una copia aislada.
- **Diferencias solo metodológicas:** DuPont por promedios (F‑09), WACC (F‑11), bases de actividad (F‑13) y presentación neta o bruta (F‑18).
- **No verificables:** F‑08, F‑10, F‑12 y la contraparte de CN1202.

## 15. Conclusiones

1. La **aplicación es exacta respecto de los estados originales**: no hay errores de transcripción, clasificación, fórmula, implementación ni presentación. Sus riesgos son de **integridad del proyecto** (F‑01) y de **criterio metodológico** heredado del trabajo (F‑11 y F‑13) o propio (F‑09, documentado).
2. Los **errores de cifras están en el documento académico**. El primer punto de error en las Tablas 3, 4, 6 y 7 es el uso de cifras del resumen **no auditado** de PCR (p. 8), mezcladas con las auditadas. Estos errores invierten el signo de la variación del activo corriente en 2023 y 2024 y alteran la narrativa de 6.5.
3. Hay resultados que **ninguna de las dos fuentes puede validar** con la documentación disponible: las tasas del WACC, el ISR y la contraparte de CN1202. La utilidad de la controladora 2023 es ambigua en el propio documento.
4. **No puede declararse completamente validado** ni el trabajo (por F‑02 a F‑07 y F‑13) ni el WACC de la app (por F‑10 a F‑12). La app es confiable para el resto de los análisis, una vez resuelto F‑01.

## 16. Recomendaciones de corrección, por prioridad

Ninguna se ha ejecutado; todas requieren autorización.

| Prioridad | ID | Recomendación | Ámbito |
|---|---|---|---|
| 1 — Crítica | F‑01 | Devolver la carpeta a su sitio (`Move-Item .venv\calculations .\calculations`); verificar con `git status` que no quedan borrados; ejecutar la suite. Poner bajo control de versiones los 7 módulos sin seguimiento (commit autorizado) para que no dependan de una carpeta ignorada. | Proyecto |
| 2 — Crítica | F‑02, F‑03 | En las Tablas 3, 4, 6 y 7, usar AC 2023 = 429,794,544 y PC 2023 = 333,120,685; recalcular las variaciones, el CTN, la RC y la PA y reescribir 6.5 (puntos 2 y 3) y 6.8. Citar los estados auditados, no el resumen PCR. | Trabajo |
| 3 — Alta | F‑07 | En 9.7 2025/2024, presentar «Otras CxC a LP» (2024) como línea propia; recalcular los totales (408,447,177) y el párrafo de relacionadas, salvo que se obtenga evidencia documental de que es una cuenta con relacionadas. | Trabajo |
| 4 — Alta | F‑13 | Presentar el PPC, el PPP y el CCE con base homogénea (comerciales + otras) para 2021–2025 y revisar la conclusión del CCE. En la app, añadir PPP y CCE homogéneos o marcar la serie principal como no comparable entre 2023 y 2024 (requiere cambiar el código). | Trabajo y app |
| 5 — Alta | F‑10 a F‑12 | Obtener las notas del informe auditado (tasas) y documentar la tasa legal de ISR; si no es posible, presentar el WACC como escenario. Sustituir Ke = ROE por un método de costo exigido o declarar la limitación, y mostrar la sensibilidad a la estructura con solo deuda con costo. | Trabajo y app |
| 6 — Media | F‑04, F‑06 | Corregir el PC 2022 (231,944,180) y unificar la base de CxC de 8.2 B. | Trabajo |
| 7 — Media | F‑08 | Explicar la contradicción del estado de resultados y el estado de cambios en el patrimonio 2023 y presentar ambos valores de la controladora o elegir uno con una justificación documentada. | Trabajo y app |
| 8 — Media | F‑09 | En la página «Análisis DuPont», indicar que usa saldos promedio y remitir al DuPont al cierre. | App |
| 9 — Baja | F‑05, F‑15 a F‑19 | Corregir los redondeos, las tipografías, la contradicción de 8.2 C y la mezcla de bruto y neto en 8.4 C. | Trabajo |
| 10 — Baja | F‑14 | Decidir si se conservan los 18 ceros de 2021 (hoy se conservan por decisión del usuario). | App |
