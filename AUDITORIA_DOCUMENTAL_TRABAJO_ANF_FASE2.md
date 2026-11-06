# Auditoría documental del trabajo académico ANF (Fase 2 — diagnóstico)
## Alutech, S. A. de C. V. y subsidiarias – División Acero, 2021–2025

Fecha: 2026-11-03 · Rama `correcciones-auditoria` (HEAD `9fb79f4`) · **Solo diagnóstico.** No se modificó el trabajo académico, ningún cálculo, la aplicación, la base de datos ni git. Las correcciones propuestas **no se han ejecutado**.

### Documento auditado y convenciones de referencia

| Elemento | Detalle |
|---|---|
| Versión principal | `Trabajo de investigación ANF.md` (1,970 líneas; modificado el 2026-11-02 a las 20:58; SHA-256 `bcfeb15d…`) y su exportación `Trabajo de investigación ANF.pdf` (83 páginas físicas; 2026-11-02 21:00; SHA-256 `e0776984…`). |
| Cómo se determinó | Son las únicas versiones del trabajo en el proyecto y en `C:\Users\estua\Documents\ANF` (búsqueda por nombre, excluyendo respaldos). El PDF es dos minutos posterior al MD y tiene el mismo contenido: las cifras discutidas aparecen en ambos, con las columnas partidas en el PDF. Ambos archivos son idénticos a los de los respaldos de las Fases 1 y 1.2, así que no han cambiado desde las auditorías anteriores. |
| Otras fuentes revisadas | Estados originales (`documentos/Certificacin_EFC_…2021/2022/2023.pdf`, combinados y auditados; `12_EEFF_diciembre_2024.pdf` (escaneado) y `12_EEFF_diciembre_2025.pdf`, consolidados); informe PCR de calificación `SV-CIALUTECH-202506.pdf` (complementario, **no auditado** en su p. 8); `AUDITORIA_FORENSE_ERRORES_ANF.md` (F‑01 a F‑20). `Balance general.pptx` y `Estados-Financieros.pptx` son material didáctico genérico (empresa de ejemplo «ABC, S.A.») y no contienen datos de Alutech. |
| Referencias | «L*n*» = línea del Markdown; «p. *n*» = página **física** del PDF (el índice impreso no coincide con la paginación física; ver D‑37). «Cert. 2023 p. 7» = página del PDF del estado original. |

---

## A. Resumen ejecutivo

**39 hallazgos:** 3 críticos · 6 altos · 10 medios · 15 bajos · 5 no verificables.

**Principales problemas financieros:**
- Tres cifras base del balance no figuran en los estados auditados: el AC 2023 (541,094,544, cuando el estado dice 429,794,544), el PC 2023 (342,120,685 frente a 333,120,685) y el PC 2022 (231,914,180 frente a 231,944,180). Se usan en las Tablas 3, 4, 6 y 7 y en el texto de 6.5.
- Esas cifras **invierten el signo** de la variación del activo corriente en 2023 (+20.60 % en el trabajo, −4.21 % real) y en 2024 (−20.02 % en el trabajo, +0.69 % real), y desvían el CTN, la RC y la PA de 2023.
- El propio trabajo usa las cifras correctas en 7.2, 8.1, 9.1 y 9.2, así que contiene **dos versiones incompatibles** de la liquidez de 2023.
- Origen probable: el resumen **no auditado** de PCR (p. 8: 541.1, 342.1, 231.9 y 31.2 M), que el trabajo no cita.

**Principales problemas metodológicos:**
- El PPC, el PPP y el CCE mezclan bases distintas entre 2021–2023 y 2024–2025. La conclusión «CCE negativo desde 2023» no se sostiene con base homogénea en 2023 (+8.56 días).
- El WACC usa Ke = ROE (Ke < Kd en 2022, 2024 y 2025), pondera los pasivos operativos sin costo y se apoya en tasas e ISR sin respaldo.
- El *spread* compara un ROA después de intereses con un Kd.
- En 9.7, la cuenta «Otras cuentas por cobrar a LP» de 2024 se trata como relacionada.
- No se advierte del cambio de estados combinados a consolidados.

**Principales problemas de redacción y coherencia:**
- Contradicciones entre apartados: RC 2023 de 1.58 frente a 1.29; 8.2 C dice que el PPP no es calculable y 9.3 lo calcula.
- Explicaciones que los datos no sostienen (8.3 D; tiendas y cuotas de mercado; tasas de CIALUTECH1).
- La tabla vertical 7.1 no cuadra en 2025.
- Asteriscos sin nota, título de 6.4 equivocado, una oración inconclusa (8.5), citas sin bibliografía e índice desactualizado.

**Apartados que requieren mayor atención:** 6.4–6.8 (horizontal y capital de trabajo), 8.2–8.3, 9.3 (CCE), 9.4 (WACC), 9.7 (origen y aplicación), 3.2 (historia) y 11 (conclusiones).

---

## B. Matriz general de hallazgos

| ID | Apartado | Página (PDF) | Ubicación específica | Hallazgo | Valor presentado | Valor verificado | Gravedad | Evidencia |
|---|---|---|---|---|---|---|---|---|
| D‑01 | 6.4–6.6 | 22–27 | Tablas 3 (L498), 4 (L511), 6 (L541), 7 (L563–564); texto 6.5 punto 2 (L549) | Activo corriente 2023 que no figura en el estado original | 541,094,544 («USD 541.09 millones») | 429,794,544 (+111,300,000; +25.90 %) | **Crítico** | Cert. 2023 p. 7 «Total activos corrientes»; PCR p. 8 «541.1» |
| D‑02 | 6.4–6.6 | 22–27 | Tablas 3 (L499), 4 (L512), 6 (L541), 7 (L563–564); texto L549 | Pasivo corriente 2023 que no figura en el estado | 342,120,685 («USD 342.12 millones») | 333,120,685 (+9,000,000; +2.70 %) | **Alto** | Cert. 2023 p. 7; PCR p. 8 «342.1» |
| D‑03 | 6.4–6.6 | 22–27 | Tablas 3 (L499), 6 (L540), 7 (L562–563) | Pasivo corriente 2022 con dígitos transpuestos | 231,914,180 | 231,944,180 (−30,000; −0.01 %) | Medio | Cert. 2022 p. 9 |
| D‑04 | 6.4–6.6 | 22–27 | Tablas 3, 4, 6 y 7 | Resultados derivados de D‑01 a D‑03 (ver la matriz D) | Var. AC 22→23 +20.60 %; 23→24 −20.02 %; CTN 2023 198,973,859; RC 1.58; PA 1.17; var. CTN 2024 −64.92 % | −4.21 %; +0.69 %; 96,673,859; 1.29; 0.87; −27.79 % | **Crítico** | Recálculo con los totales de Cert. 2022–2023 y EEFF 2024 |
| D‑05 | 6.5 y 6.8 | 26–28 | 6.5 puntos 2 (L549) y 3 (L551); 6.8 (L579–581) | La narrativa se basa en D‑01 a D‑04: «el activo corriente aumentó un 20.60 %…», «durante 2024, el activo corriente disminuyó un 20.02 %…», «caída del CTN de USD 129.17 millones» | Ver la celda anterior | El AC bajó en 2023 y subió en 2024; el CTN cayó 120.05 M en 2023 y 26.87 M en 2024 | **Crítico** | Ídem |
| D‑06 | 6.5 frente a 8.1 y 9.2 | 25–26 / 32 / 46–48 | Tabla 6 (L540–541) frente a la tabla de 8.1 (L704–706) y 9.2.1 (L1096–1100) | El trabajo presenta dos valores distintos para el mismo indicador y año | RC 2023 1.58 / 1.29; PA 1.17 / 0.87; CTN 2023 198,973,859 / 96,673,859; CTN 2022 216,758,221 / 216,728,221 | Los de 8.1 y 9.2 son los correctos | **Alto** | Comparación interna; Cert. 2022–2023 |
| D‑07 | 6.4 | 24–25 | Tabla 5, utilidad operativa 2022 (L527) | Cifra aproximada; el asterisco no se explica | 31,200,000\* | 31,200,977 (derivada: 89,322,338 − 18,344,656 − 39,712,552 − 397,016 + 332,863); usada en 8.3 B y 8.4 | Bajo | Cert. 2022 p. 10; PCR p. 8 «31.2» |
| D‑08 | 6.4–6.6 (método) | 22–27 | Tablas 3, 4, 6 y 7 | Uso de una fuente secundaria **no auditada** y no citada, mezclada con cifras auditadas (híbridos con diferencias exactas en millones) | 541,094,544; 342,120,685 | Fuente obligatoria: certificaciones auditadas | **Alto** | PCR p. 8 («Resumen de Estados Financieros no auditados»); su dic‑23 tampoco coincide en total activo (818.1 frente a 809.1), patrimonio (249.1 frente a 227.7) ni utilidad neta (17.2 frente a 13.3) |
| D‑09 | 6.4 y 8.2 B | 22–23 / 34 | Tabla 3 CxC 2023 (L496) frente a Tabla 4 (L509); 8.2 B 2023 (L753) | Dos bases de CxC para 2023 sin explicación; 8.2 B cambia la base solo en 2023 | Tabla 3: 41,272,525; Tabla 4 y 8.2 B: 96,097,483; rotación 4.98; PPC 73.3 | Comerciales: 41,272,525 (rotación 11.60; PPC 31.47, igual que en 9.3); comerciales + otras: 96,097,483 | Medio | Cert. 2023 p. 6 (líneas separadas) |
| D‑10 | 9.3 y 11 | 49–54 / 82–83 | Tablas EPI/PPC/PPP/CO/CCE (L1261–1335); análisis (L1337, L1345); conclusiones (L1926) | PPC y PPP usan bases no homogéneas (2021–2023 solo comerciales; 2024–2025 «comerciales y otras»); la conclusión «CCE negativo a partir de 2023» depende de esa mezcla | CCE 2021 28.86; 2022 63.33; **2023 −21.40** | Con base homogénea (comerciales + otras): 65.49; 93.76; **+8.56**; 2024 y 2025 sin cambio (−30.72 y −55.52) | **Alto** | Cert. 2021 p. 8–9, 2022 p. 8, 2023 p. 6–7 (CxP comerciales, otras CxP, CxC comerciales y otras CxC); EEFF 2024–2025 p. 1 |
| D‑11 | 8.2 | 33–34 | Criterio 2 (L725) y C (L759) frente a 9.3 (L1203–1215, L1287–1301) | Afirma que los estados «no desglosan» los acreedores comerciales y que el PPP no es viable, pero los estados sí presentan la línea y 9.3 calcula el PPP con ella | «No es viable calcular un PPP exacto» | 2021–2023: «Cuentas por pagar comerciales» (156,609,253; 96,629,671; 195,599,671); 2024–2025: «Acreedores comerciales y otras CxP» | Medio | Cert. 2021 p. 8, 2022 p. 8, 2023 p. 7; EEFF 2024–2025 p. 1 |
| D‑12 | 4, 5.6 y 8.2 | 11, 17–20, 33 | Limitación 4 (L252); 5.6 B y Tabla 2 (L378–441) | El marco conceptual define rotaciones con saldos promedio y compras a crédito; la limitación promete promedios «cuando estén disponibles» (lo están para 2022–2025); se aplican saldos al cierre y el costo de ventas | — | Debe declararse como criterio único y su efecto | Bajo | Comparación interna |
| D‑13 | 8.3 B | 36–37 | Tabla de cobertura (L804–810); texto (L812) | La columna «Gastos Financieros» contiene **netos** de ingresos financieros sin indicarlo; además, «el 80 % de la utilidad operativa se destinó al pago de la deuda» confunde intereses netos con pago de deuda | 2024: 28,064,310; 2025: 37,399,011 | Brutos: 43,089,283 y 51,914,906 (cobertura bruta 0.82 y 1.05) | Medio | EEFF 2024 p. 2 y 2025 p. 2 |
| D‑14 | 8.3 C | 37 | L814 | Afirmación sin datos: «cualquier amortización… ubicaría la cobertura real por debajo de 1.0» (el pasivo corriente incluye 173.1 M de acreedores, que no son deuda) | — | No calculable con los documentos | Bajo | EEFF 2025 p. 1 |
| D‑15 | 8.3 D | 37–38 | L830 | La explicación del desapalancamiento de 2025 («amortización de deuda» y «capitalización por utilidades retenidas») contradice los datos y el propio 9.7 | — | Deuda financiera −372,328 (352.5 → 352.1 M, 9.7 L1819); pasivo total −50.2 M, casi todo de acreedores comerciales (−52.0 M); resultados acumulados −4,915,552; el patrimonio sube por reservas (+8,218,446) y por el resultado del período | Medio | EEFF 2024–2025 p. 1 |
| D‑16 | 8.4 C | 40 | L913 | Cita gastos financieros brutos sin advertirlo, mientras la Tabla 5, 6.7 y la sección 10 usan netos | 51,914,906 | Neto 37,399,011 | Bajo | EEFF 2025 p. 2 |
| D‑17 | 7.1 | 29 | Tabla vertical del Estado de Resultados (L617–631) | 2024–2025: «Otros ingresos o gastos» aparece antes del resultado operativo, cuando en los estados consolidados va después del resultado financiero. La tabla no cuadra en 2025; además, mezcla gastos financieros netos (2021–2023) con brutos (2024–2025) | UO 2025 12.43 %; UAI 3.74 % | Suma de filas hasta la UO: 12.25 %; UO + IF + GF = 3.92 %; diferencia −0.18 p.p. (la fila de otros) | Medio | EEFF 2024–2025 p. 2 |
| D‑18 | 6.4, 7.1 y 8.2 | 24–25, 29, 34 | L526, L527, L626 (2022 y 2023), L753 | Asteriscos sin nota explicativa | «Gastos operativos\*», «31,200,000\*», «6.24 %\*», «9.34 %\*», «2023\*» | — | Bajo | Búsqueda de notas: no existen |
| D‑19 | 6.4 | 22, 24 | Título (L487) y texto (L489, L517) | El título «Análisis horizontal del estado de resultados» encabeza tablas del balance; errata «2021-20252» | — | — | Bajo | — |
| D‑20 | 6.2, 6.4, 7, 8 y 9 | 21–54 | 6.2 (L464) y todas las comparaciones 2023→2024 | No se advierte del cambio de estados **combinados** («Alutech – División Acero», 2021–2023) a **consolidados** («Alutech, S. A. de C. V. y subsidiarias», 2024–2025) ni de sus efectos: línea única de CxC, plusvalía dentro de intangibles, gastos financieros brutos, posición de otros ingresos, perímetro | «se consideran las posibles diferencias…» (genérico) | La bibliografía (L1938–1940) reconoce las dos familias, pero el análisis no | Medio | Cert. 2021–2023 frente a EEFF 2024–2025 |
| D‑21 | 9.4 | 55–64 | Columnas «Costo» de las 5 tablas WACC (L1357–1549) | Tasas de interés sin respaldo en los documentos disponibles; para 2022–2025 no hay citas; arrendamientos CP 8.50 % frente a LP 8.00 % en 2022 sin justificar; títulos valores 7.20 % en 2024–2025 | 6.75 %–8.50 % | CIALUTECH1 (PCR p. 7): tramos de 7.50 %–9.50 %, promedio del 8.4 % a jun‑2025 (evidencia parcial) | No verificable | Notas 18–25 citadas: no disponibles |
| D‑22 | 9.4 | 55–65 | Columna «Impuesto» y comparativo (L1571) | ISR del 30 % supuesto | 30 % | Tasas efectivas: 16.13 %, 28.25 %, 41.20 %, 57.40 % y 27.69 % | No verificable | Estados de resultados (ISR/UAI) |
| D‑23 | 9.4 | 55–66 | Patrimonio de cada tabla; comparativo (L1570); conclusión (L1582) | Ke = ROE no es un costo de capital exigido (lo admite L1389) y genera Ke < Kd neto en 2022, 2024 y 2025. La ponderación incluye pasivos operativos a costo 0, lo que reduce el WACC | WACC 14.59; 3.83; 3.88; 2.58; 3.85 % | Con solo deuda con costo + patrimonio (mismas tasas y Ke): 21.36; 5.03; 5.47; 3.69; 5.16 % (sensibilidad, no validado) | **Alto** | Recálculo propio |
| D‑24 | 9.4 | 64–66 | Filas ROA, *spread* y diagnóstico (L1578–1580); conclusión (L1586) | El *spread* compara el ROA (utilidad neta, ya después de intereses e impuestos) con el costo de la deuda después de impuestos: no son magnitudes comparables; el diagnóstico «Insuficiente» se apoya en esa comparación | *Spread* 7.15; −3.76; −3.57; −4.82; −3.65 % | Debería usarse un rendimiento antes de intereses (p. ej., UO × (1 − t)/capital invertido), declarado como supuesto | Medio | Criterio financiero |
| D‑25 | 9.4 | 57, 61–63 | L1385, L1471 frente a L1475 y L1516 | WACC 2023: 3.88 % en la tabla y 3.87 % en el texto; 73.76 % / 26.24 % truncados | 3.88; 73.76; 26.24 | 3.8745 (3.87); 73.77; 26.23 | Bajo | Recálculo |
| D‑26 | 9.6 | 73 | Enfoque controladora 2023 (L1742–1749) | La utilidad atribuible 2023 se toma del estado de cambios en el patrimonio sin advertir que el estado de resultados del mismo documento dice otra cosa | 12,309,102 → margen 2.57 %, RSA 1.52 %, RSP 5.41 % | ER: 13,330,680 a la controladora y «–» a no controladoras → 2.79 %, 1.65 %, 5.86 % | No verificable | Cert. 2023 p. 9 frente a p. 11 |
| D‑27 | 9.5–9.6 | 67–70 | L1623, L1702 (denominador); L1635, L1674 | Tipografías: «553,995,185» (el activo es 553,955,185; el resultado 0.9459 es correcto) y «68,602.739» | — | — | Bajo | Cert. 2021 p. 8 |
| D‑28 | 9.7 | 74–77 | Tabla 2025/2024 (L1784, L1813) y texto (L1817, L1819) | La cuenta de 2024 «Otras cuentas por cobrar a LP» (118,684,551) se presenta como «Cuentas por cobrar empresas relacionadas a LP», se compensa con la de 2025 y se interpreta como «traslado de plazo» | Var. +143,444,117; totales 289,762,626; «aumento neto» 38,785,937 | Líneas separadas: fuente de 118,684,551 y uso de 262,128,668; totales 408,447,177; aumento neto de relacionadas CP + LP 157,470,488 | **Alto** | EEFF 2024 p. 1; PCR p. 8 (dic‑24: «CxC de LP 119.7», relacionadas LP 0.0) |
| D‑29 | 9.7 | 74–79 | Introducción (L1770–1772) e interpretación (L1815–1821) | No se advierte que el método de variaciones netas incluye partidas que no son efectivo (depreciación dentro del PPE neto, efecto de conversión −8.0 M como «uso», derechos de uso) ni que no equivale al estado de flujos de efectivo; el texto lo lee como movimientos de caja («pagó obligaciones», «liberó fondos») | — | Limitación metodológica | Bajo | EEFF 2024–2025 |
| D‑30 | Introducción y 3.2 | 4, 6, 10, 80 | L145, L178, L223–230; sección 10 (L1885, L1901) | Datos de la red comercial incoherentes y contradichos por la única fuente disponible | «128 tiendas»; Honduras 73 %; tabla por país | La tabla suma **142** tiendas; PCR p. 2 y 5: 147 tiendas; Honduras 65.0 %, Nicaragua 15.8 %, El Salvador 7.3 %, Guatemala 5.0 %, Costa Rica 1.3 % | Medio | PCR p. 2 y 5; suma propia |
| D‑31 | 3.2 | 9 | L217 | Condiciones de CIALUTECH1 no respaldadas | Tasas «entre 8.50 % y 9.95 %»; vencimientos «2026-2031» | PCR p. 7: tramos del 7.50 % al 9.50 %, vencimientos de 2025 a 2027 | Medio | PCR p. 7 |
| D‑32 | 3.2 | 6–10 | L177–243 | Datos históricos y societarios sin fuente: escritura, RTN, Euler Hermes, Nucor, planta de Guatemala, empleos, junta directiva | — | No verificables con `documentos/` | No verificable | — |
| D‑33 | 10 | 79–80 | L1878–1914 | Cifras de Ternium sin fuente ni estados en el proyecto; atribuciones causales sin sustento («por la venta minorista directa en sus 128 tiendas») | Ingresos 15,609.09 M; RC 2.49; etc. | No verificables. La columna de Alutech es correcta (ver la auditoría de concordancia) | No verificable | — |
| D‑34 | 9.1 | 46 | L1073 | «Rango referencial óptimo del 10 % al 30 %» sin fuente | — | — | Bajo | — |
| D‑35 | 8.5 | 44 | Final de L1031 | Oración inconclusa: «…se necesitaría confirmar si existe una clase de acciones» | — | — | Bajo | — |
| D‑36 | 5.5 y 12 | 15, 83 | L322 («…rentabilidad\]»), L326 («\[9\]»), L1934–1942 | Cita numerada sin lista numerada; corchete suelto; bibliografía incompleta: Gitman sin edición, editorial ni capítulo; faltan PCR, Ternium y el URL o la fecha de BVES; se cita «la presentación del docente» (p. 50, 52) sin referencia | — | — | Bajo | — |
| D‑37 | Índice | 2–3 | L39–141 | Los números de página del índice no corresponden de forma uniforme a la paginación del PDF | 6.4 → 22; 9.4.1 → 52; 9.7 → 72; 10 → 77; 11 → 80 | Páginas físicas 22; 55; 74; 79; 82 (desfase variable de 0 a 3) | Bajo | PDF |
| D‑38 | 6.7 | 28 | Punto 2 (L573) | El texto exige respaldo para mencionar Los Pinares y Ecotek, pero ese respaldo existe en las fuentes del proyecto y no se usa | — | PCR p. 3: 80.1 M y 41.8 M a jun‑2025, entidades en suspensión temporal | Bajo | PCR p. 3 |
| D‑39 | Introducción, 3 y 10 | 4–10, 79–80 | L145–147, L1882–1901 | La entidad se denomina «Alutech, S.A. de C.V.», mientras el análisis corresponde a la División Acero (combinados 2021–2023: «Alutech – División Acero») | — | Denominación de los estados | Bajo | Encabezados de los estados |

---

## C. Revisión detallada por apartado

### C.1 Capital de trabajo y análisis horizontal (D‑01 a D‑08, D‑19, D‑20)

1. **Dónde:** Tablas 3, 4, 6 y 7 y texto de 6.5–6.8 (p. 22–28).
2. **Qué está mal:** AC 2023, PC 2023 y PC 2022 no coinciden con los totales impresos, y todo lo que se calcula con ellos arrastra el error.
3. **Por qué:** las certificaciones auditadas presentan 429,794,544 y 333,120,685 (Cert. 2023 p. 7) y 231,944,180 (Cert. 2022 p. 9). Las cifras del trabajo coinciden en millones con el resumen no auditado de PCR (p. 8), y en el AC y PC 2023 conservan los dígitos inferiores de las auditadas. Es una mezcla de fuentes.
4. **Comprobación:** CTN = AC − PC; RC = AC/PC; PA = (AC − inventarios)/PC; variación = (Vt − Vt−1)/Vt−1. Con los originales:
   - CTN 2023 = 96,673,859; RC 1.29; PA 0.87.
   - Var. AC 2023 −4.21 %; var. AC 2024 +0.69 %.
   - Var. PC 2022 +12.61 %; 2023 +43.62 %; 2024 +8.96 %.
   - Var. CTN 2022 +21.82 %; 2023 −55.39 %; 2024 −27.79 %.
   - Las operaciones del trabajo son aritméticamente coherentes con sus propios datos de entrada: el error es de dato, no de fórmula.
5. **Otros apartados afectados:** ver la matriz D. 7.2, 8.1, 9.1 y 9.2 usan las cifras correctas, lo que genera la contradicción interna D‑06.
6. **Corrección necesaria (no ejecutada):**
   - Sustituir las tres cifras en todas sus apariciones y recalcular las Tablas 3, 4, 6 y 7.
   - Reescribir 6.5 (puntos 2 y 3) y 6.8.
   - Citar las certificaciones auditadas.
   - Explicar el asterisco de la UO 2022 o sustituirla por 31,200,977.
   - Corregir el título de 6.4 y la errata «2021‑20252».
   - Añadir en 6.2 una advertencia sobre el cambio combinado → consolidado.

### C.2 Análisis vertical (D‑17, D‑18)

7.2 coincide en todos los valores. 7.1 coincide en cada porcentaje individual, pero su **estructura** no refleja los estados consolidados: en 2024–2025, «Otros ingresos (gastos)» va después de los gastos e ingresos financieros (EEFF 2024 y 2025, p. 2). Por eso, en 2025 el resultado operativo (12.43 %) no es la suma de las filas que lo preceden (12.25 %). La fila de gastos financieros mezcla netos (2021–2023) con brutos (2024–2025).

**Corrección:** reordenar o separar la fila de otros por familia de estados y rotular la fila financiera; documentar los asteriscos.

### C.3 Indicadores de actividad (D‑09 a D‑12)

- **Cuentas por cobrar:** 2021–2023 presentan comerciales y otras por separado; 2024–2025, una sola línea «Deudores comerciales y otras». La única serie homogénea es «comerciales + otras». El trabajo usa solo comerciales en 2021–2022, comerciales + otras en 2023 (8.2 B) y solo comerciales en 2023 (9.3).
- **Cuentas por pagar:** igual. 2021–2023 tienen «cuentas por pagar comerciales» y «otras cuentas por pagar»; 2024–2025 tienen «acreedores comerciales y otras». La base homogénea agrega las otras (8,632,737; 8,854,582; 12,127,667).
- **Saldos:** finales en los 5 años (uniforme). Se usa el costo de ventas como aproximación de las compras, declarado en 9.3.
- **Comprobación:** PPC = CxC/ingresos × 365; PPP = CxP/costo × 365; CCE = PPI + PPC − PPP. Con base homogénea: PPC 82.19 / 62.11 / 73.28 / 74.07 / 58.25 días; PPP 164.23 / 93.83 / 202.98 / 217.70 / 190.66; CCE 65.49 / 93.76 / **8.56** / −30.72 / −55.52.
- **Afecta a:** 8.2 B y C, 9.3 (tablas y análisis 2024–2025, punto 3), conclusiones (L1926: «el ciclo de conversión de efectivo negativo…») y la sección 10 (no usa el CCE).
- **Corrección:** presentar la serie homogénea y, si se desea, la comercial solo para 2021–2023, rotulada. Revisar la afirmación de que el CCE es negativo desde 2023 (es negativo desde 2024 con base homogénea). Retirar o corregir la afirmación de 8.2 sobre la falta de desglose y la inviabilidad del PPP. Alinear 5.6 y la limitación 4 con el criterio aplicado.

### C.4 Endeudamiento y rentabilidad (D‑13 a D‑16)

Las fórmulas y los valores de 8.3 A, B y D y de 8.4 son correctos (ver la auditoría de concordancia). Los problemas son de rotulación y de interpretación:
- La cobertura usa gastos financieros netos sin decirlo; con los brutos sería 0.82 (2024) y 1.05 (2025).
- La explicación del desapalancamiento de 2025 contradice los datos: el pasivo bajó por los acreedores comerciales, no por la deuda financiera.
- 8.4 C cita gastos brutos mientras el resto del trabajo usa netos.
- 8.3 C hace una afirmación cuantitativa sin datos.

**Corrección:** rotular la columna como «netos», incluir el bruto como dato complementario, reescribir la explicación de 8.3 D y unificar el uso de netos y brutos.

### C.5 DuPont (D‑26, D‑27)

Los valores del trabajo son correctos con **saldos al cierre**: la identidad margen × rotación × MAF = ROE se cumple en los 5 años. La aplicación tiene, además, un reporte con saldos promedio (F‑09). Es una diferencia metodológica de la app, no un error del trabajo, y no debe declararse incorrecto ninguno de los dos.

La controladora 2023 depende de una cifra contradictoria en el documento fuente (D‑26). Hay tipografías menores (D‑27).

**Corrección:** nota sobre la fuente de la utilidad atribuible en 2023 y corrección tipográfica.

### C.6 WACC (D‑21 a D‑25)

| Tipo de dato | Elementos |
|---|---|
| Comprobable en los estados | Importes de cada fuente, pesos, utilidad neta, patrimonio, ROE y estructura (pasivos/patrimonio). |
| Fuente externa disponible | Tramos de CIALUTECH1 (PCR p. 7), solo para esa emisión. |
| Supuestos | Tasas por tipo de deuda, ISR del 30 %, costo 0 de los pasivos operativos y Ke = ROE. |
| No verificable | Tasas 2021–2025 (sin notas) e ISR. |

**Corrección:**
- Presentar el WACC como **escenario basado en supuestos**.
- Citar o retirar las tasas.
- Justificar el ISR.
- Sustituir Ke = ROE por un costo exigido (p. ej., CAPM con fuente) o declarar expresamente la limitación.
- Mostrar la estructura de deuda con costo + patrimonio.
- Replantear el *spread* con un rendimiento antes de intereses.
- Unificar 3.87 / 3.88.

### C.7 Estado de origen y aplicación de fondos (D‑28, D‑29)

- **2023/2022:** correcto (47 líneas; totales 209,290,574).
- **2025/2024:** 36 de 37 líneas correctas. La de 118,684,551 está mal denominada y compensada con otra cuenta. El trabajo no presenta ninguna evidencia de que sea un saldo con relacionadas; el propio estado de 2024 la llama «Otras cuentas por cobrar a LP» y PCR muestra relacionadas LP = 0.0 a dic‑24.
- El trabajo describe correctamente el método (variaciones de balance), pero no advierte de que no equivale a flujos de efectivo.

**Corrección:** presentar las dos líneas por separado, recalcular los totales y los párrafos de L1815–1821 y añadir la limitación del método.

### C.8 Redacción, fuentes y coherencia (D‑30 a D‑39)

**Datos descriptivos contradictorios:**
- Las tiendas suman 142, no 128.
- PCR da 147 tiendas y un 65 % de cuota en Honduras.
- Las tasas de CIALUTECH1 no coinciden con PCR.

**Afirmaciones sin fuente:** historia, Ternium, rango de tesorería del 10–30 %.

**Defectos formales:**
- Oración inconclusa (8.5).
- Citas y bibliografía incompletas.
- Índice con páginas desfasadas.
- Uso de «Alutech, S.A. de C.V.» como entidad, cuando el análisis es de la División Acero.
- El trabajo no aprovecha la evidencia de PCR sobre Los Pinares y Ecotek.

**Corrección:** verificar o retirar los datos descriptivos, citar las fuentes, completar la bibliografía, cerrar la oración, regenerar el índice y unificar la denominación de la entidad.

---

## D. Matriz de impacto (dependencias entre errores)

| Error de origen | Apariciones del dato | Resultados derivados afectados | Resultados del mismo trabajo que siguen correctos |
|---|---|---|---|
| D‑01 AC 2023 | Tabla 3 (L498), Tabla 4 (L511), Tabla 6 (L541), Tabla 7 (L563, L564), texto 6.5 (L549: «USD 541.09 millones») | Var. AC 22→23 (Tabla 3: +92,422,143 / +20.60 %); var. AC 23→24 (Tabla 4: −108,322,866 / −20.02 %); CTN 2023 (Tablas 6 y 7: 198,973,859); var. CTN 2023 (−17,784,362 / −8.20 %) y 2024 (−129,168,396 / −64.92 %); RC 2023 1.58x; PA 2023 1.17x; texto 6.5 puntos 2 y 3; 6.8 («desde 2023…»); D‑06 | 7.2 (AC 53.12 % de los activos), 8.1 (1.29; 0.87; 96,673,859), 9.2.1 y 9.2.2 (96,673,859) |
| D‑02 PC 2023 | Tablas 3, 4, 6 y 7 (L499, L512, L541, L563–564); texto L549 («USD 342.12 millones») | Var. PC 22→23 (+110,206,505 / +47.52 %); var. PC 23→24 (+20,845,530 / +6.09 %); CTN, RC y PA 2023; textos 6.5 | 7.2 (PC 41.17 %), 8.1, 9.1 (5.86 %), 9.2 |
| D‑03 PC 2022 | Tablas 3 (L499), 6 (L540), 7 (L562, L563) | Var. PC 21→22 (+25,940,950 / +12.59 %); CTN 2022 (216,758,221); var. CTN 2022 (+38,849,904 / +21.84 %) y 2023; texto 6.5 punto 1 («USD 216.76 millones») y 6.8 | 8.1 y 9.2 (216,728,221); 9.1 (231,944,180) |
| D‑07 UO 2022 | Tabla 5 (L527) | Ninguno en los porcentajes presentados | 8.3 B y 8.4 (31,200,977) |
| D‑09 Base de CxC 2023 | Tabla 4 (L509), 8.2 B (L753) | Rotación y PPC 2023 de 8.2 B; var. CxC 23→24 de la Tabla 4 (+1.15 %, correcto solo sobre la base comercial + otras) | 9.3 (31.47 días con base comercial) |
| D‑10 Bases de PPC y PPP | 9.3 (5 tablas), 8.2 C (ciclo operativo 2024–2025) | CO y CCE 2021–2023, análisis de 9.3 (puntos 2 y 3) y conclusiones (L1926) | CCE 2024–2025 (iguales con ambas bases) |
| D‑23/24 Método del WACC | 9.4 (5 tablas y comparativo) | WACC, aportes, *spread*, diagnóstico y conclusiones del WACC (L1582–1586) | Estructura de financiamiento, ROE, ROA y pesos |
| D‑28 CN1202 en 9.7 | L1784, L1813, L1817, L1819 | Totales de fuentes y usos, párrafos de interpretación de relacionadas | Las otras 36 líneas de 2025/2024 y toda la tabla 2023/2022 |
| D‑17 Estructura 7.1 | L625–631 | Lectura del resultado operativo y la UAI 2024–2025 en el vertical | Porcentajes individuales |

---

## E. Hallazgos no verificables

| ID | Afirmación | Documentación necesaria |
|---|---|---|
| D‑21 | Tasas de interés de préstamos, arrendamientos, bonos, certificados, titularizaciones, documentos, títulos valores y otros pasivos financieros | Notas de los estados auditados 2021–2025 (préstamos, arrendamientos, emisiones) o prospectos y fichas de cada emisión |
| D‑22 | ISR del 30 % | Notas de impuestos o legislación aplicable por país y tasa efectiva conciliada |
| D‑26 | Utilidad atribuible a la controladora 2023 | Nota del estado de cambios en el patrimonio o carta del auditor que explique la diferencia con el estado de resultados |
| D‑32 | Historia societaria, escritura, RTN, Euler Hermes, Nucor, planta de Guatemala, empleos y junta directiva | Escrituras, prospectos de emisión, informes anuales o comunicados oficiales |
| D‑33 | Cifras de Ternium 2025 | Estados financieros auditados de Ternium S.A. 2025 (formulario 20‑F o informe anual) |
| D‑28 (parcial) | Contraparte de «Otras cuentas por cobrar a LP» 2024 | Nota de cuentas por cobrar a largo plazo de los estados auditados 2024 |
| D‑30 / D‑31 (parcial) | Número de tiendas y cuotas de mercado a la fecha usada por el trabajo | Fuente fechada (PCR u otra) para cada dato |

---

## F. Plan propuesto de corrección (no ejecutado)

1. **Integridad de las cifras originales:** sustituir AC 2023, PC 2023, PC 2022 y UO 2022 (D‑01 a D‑03, D‑07) en todas sus apariciones; citar las certificaciones auditadas y retirar la dependencia del resumen PCR (D‑08).
2. **Cálculos:** recalcular las variaciones del AC y PC, el CTN, la RC y la PA (D‑04) y unificar con 8.1 y 9.2 (D‑06).
3. **Tablas:** Tablas 3, 4, 6 y 7; estructura de 7.1 (D‑17); notas para los asteriscos (D‑18); título y errata de 6.4 (D‑19).
4. **Homogeneización metodológica:** bases de CxC y CxP (D‑09, D‑10); coherencia entre 5.6 y la limitación 4 y lo aplicado (D‑12); advertencia combinado → consolidado (D‑20); criterio bruto/neto de gastos financieros (D‑13, D‑16, D‑17).
5. **Indicadores:** 8.2 B y C (D‑09, D‑11); 8.3 B, C y D (D‑13 a D‑15).
6. **DuPont y WACC:** nota sobre la controladora 2023 (D‑26); tipografías (D‑27); WACC como escenario, tasas e ISR citados o declarados como supuestos, método de Ke, estructura y *spread* (D‑21 a D‑25).
7. **Origen y aplicación de fondos:** separar CN1202, recalcular los totales y el texto y añadir la limitación del método (D‑28, D‑29).
8. **Interpretaciones y conclusiones:** reescribir 6.5, 6.8, 9.3 (análisis) y las conclusiones afectadas (D‑05, D‑10); matizar el WACC (D‑23, D‑24).
9. **Redacción y presentación:** tiendas, cuotas y CIALUTECH1 (D‑30, D‑31); fuentes de la historia y de Ternium (D‑32, D‑33); rango de tesorería (D‑34); oración de 8.5 (D‑35); bibliografía (D‑36); índice (D‑37); Los Pinares y Ecotek (D‑38); denominación de la entidad (D‑39).

---

## Estado de los hallazgos F‑01 a F‑20 de la auditoría forense

El documento académico **no ha cambiado** desde la auditoría forense (mismo SHA-256 que en los respaldos de las Fases 1 y 1.2).

| F | Tema | Estado actual | Hallazgo de esta auditoría |
|---|---|---|---|
| F‑01 | Estructura de `calculations/` (app) | **Corregido** (Fases 1 y 1.2, commit `9fb79f4`) | — |
| F‑02 | AC 2023 | Sigue presente | D‑01, D‑04, D‑05, D‑06, D‑08 |
| F‑03 | PC 2023 | Sigue presente | D‑02, D‑04, D‑05 |
| F‑04 | PC 2022 | Sigue presente | D‑03, D‑04 |
| F‑05 | UO 2022 | Sigue presente | D‑07 |
| F‑06 | Base de CxC 2023 | Sigue presente; afecta también a la Tabla 4 | D‑09 |
| F‑07 | CN1202 en 9.7 | Sigue presente | D‑28 |
| F‑08 | Controladora 2023 | Sigue sin poder verificarse | D‑26 |
| F‑09 | DuPont promedio frente a cierre | Diferencia de la app; **el trabajo es correcto con saldos al cierre** | — (C.5) |
| F‑10 | Tasas del WACC | Sigue sin poder verificarse | D‑21 |
| F‑11 | Ke = ROE y estructura | Sigue presente; se añade el problema del *spread* | D‑23, D‑24 |
| F‑12 | ISR del 30 % | Sigue sin poder verificarse | D‑22 |
| F‑13 | Homogeneidad de PPC, PPP y CCE | Sigue presente | D‑10 |
| F‑14 | 18 ceros de 2021 (app) | No corresponde al trabajo | — |
| F‑15 | Redondeos | Sigue presente | D‑25 y 9.3/8.2 (PPC 2025 58.3) |
| F‑16 | Tipografías | Sigue presente | D‑19, D‑27 |
| F‑17 | Contradicción sobre el PPP | Sigue presente; además, la afirmación de que no hay desglose de CxP es falsa | D‑11 |
| F‑18 | Gastos financieros netos y brutos en el vertical | Sigue presente; **error adicional**: la tabla 7.1 no cuadra en 2025 | D‑17 |
| F‑19 | Gastos financieros brutos frente a netos en 8.4 C | Sigue presente; también en 8.3 B | D‑13, D‑16 |
| F‑20 | Redondeo del ROE promedio (app) | No corresponde al trabajo | — |

**Hallazgos nuevos respecto de la auditoría forense:** D‑06 (contradicción interna explícita), D‑11 (afirmación falsa sobre el desglose de CxP), D‑12, D‑14, D‑15, D‑17 (la tabla no cuadra), D‑18, D‑20, D‑24, D‑29, D‑30, D‑31, D‑32, D‑33, D‑34, D‑35, D‑36, D‑37, D‑38 y D‑39.

---

## Declaración de cierre de la auditoría

- La auditoría documental de la Fase 2 **está terminada**.
- **No se ha modificado** el trabajo académico (`.md` ni `.pdf`), ningún cálculo, la aplicación, la base de datos ni git. El único archivo creado es este informe.
- Las correcciones propuestas en la sección F **no se han ejecutado**.
- El trabajo **no puede considerarse corregido ni validado** mientras existan los hallazgos D‑01 a D‑39.
- Puede aprobar todas las correcciones, solo algunas (por ID o por paso del plan F) o pedir aclaraciones. Solo se modificarán los apartados que se autoricen expresamente; el resto conservará su contenido original.
