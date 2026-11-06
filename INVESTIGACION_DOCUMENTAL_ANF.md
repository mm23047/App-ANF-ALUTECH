# Investigación documental — Alutech, S. A. de C. V. y subsidiarias, División Acero (2021–2025)

Etapa 1 de la adaptación de la aplicación. Se revisaron todos los documentos de la carpeta `documentos/` y las dos
versiones del «Trabajo de investigación ANF». Ninguna cifra financiera se tomó de internet ni de otra fuente externa.

Distinción que se mantiene en todo el proyecto:

| Elemento | Dónde está | Uso |
|---|---|---|
| Datos originales | Estados financieros de `documentos/` → `fuentes/alutech/estados_financieros_2021_2025.json` → base de datos | Datos de entrada de la aplicación |
| Resultados calculados | `calculations/` (se calculan al consultar; no se almacenan) | Reportes, dashboard, exportaciones |
| Resultados de referencia | Trabajo ANF → `fuentes/anf/resultados_referencia.json` | Solo para la comparación (`INFORME_VALIDACION_FINANCIERA.md`) |

## 1. Inventario de documentos revisados

| Documento | Tipo | Período | Págs. | Función en el proyecto | Observaciones de lectura |
|---|---|---|---:|---|---|
| `Certificacin_EFC_Alutech_Divisin_Acero_2021VF_Mod010925.pdf` | Certificación de estados financieros **combinados** (Espinoza Auditores, 26‑07‑2025); estados auditados por PricewaterhouseCoopers Honduras (informe del 05‑02‑2024) | Ejercicio terminado el 31‑12‑2021 | 17 | **Fuente primaria 2021** | Contiene situación financiera (págs. 8–9), resultados (10), resultado integral (11), cambios en el patrimonio (12) y flujos de efectivo (13–14). No incluye las notas a los estados (solo la nota del ISR y hechos posteriores). Capa de texto desalineada: se leyó con `pdftotext -table` y se validó con los totales. |
| `Certificacin_EFC_Alutech_Divisin_Acero_2022_VFMod_010925.pdf` | Ídem, combinados | 31‑12‑2022 | 17 | **Fuente primaria 2022** | Situación financiera (8–9), resultados (10), ORI (11), cambios en el patrimonio (12), flujos (13–14). El estado de resultados **no presenta la utilidad de operación** ni la atribución de la utilidad (esta sí aparece en el estado de cambios en el patrimonio). |
| `Certificacin_EFC_Alutech_Divisin_Acero_2023_VFMod010925.pdf` | Ídem, combinados | 31‑12‑2023 | 17 | **Fuente primaria 2023** | Situación financiera (6–8), resultados (9), ORI (10), cambios en el patrimonio (11), flujos (12–13). Sin utilidad de operación en el estado de resultados. |
| `12_EEFF_diciembre_2024.pdf` | Estados **consolidados** de situación financiera y de resultados, firmados por el representante legal y el contador general | 31‑12‑2024 | 2 | **Fuente primaria 2024** | PDF **escaneado sin capa de texto**: se transcribió visualmente y se validó con todos los subtotales impresos (12 de 12 coinciden). No incluye notas, flujo de efectivo ni cambios en el patrimonio. |
| `12_EEFF_diciembre_2025.pdf` | Estados consolidados, firmados por el representante legal y el contador general | 31‑12‑2025 | 2 | **Fuente primaria 2025** | Capa de texto con columnas desplazadas una línea: se verificó visualmente y con los subtotales (12 de 12). |
| `SV-CIALUTECH-202506.pdf` | Informe de clasificación de riesgo de PCR (comité 269/2025) con estados no auditados a junio de 2025 | Dic‑2020 a jun‑2025 (cifras en millones) | 9 | Complementario, **no** fuente de datos | Sirvió para contrastar: muestra para dic‑23 un activo corriente de 541.1 M y un pasivo corriente de 342.1 M con otro perímetro (activo total 818.1 M), lo que explica de dónde pudieron salir cifras del trabajo que no están en los estados (ver §8). Respalda la mención del trabajo a Inversiones Los Pinares y Ecotek (saldos por cobrar de USD 80.1 M y 41.8 M a junio 2025). Su balance resumido clasifica las cuentas por cobrar de LP de dic‑24 (119.7 M) como no relacionadas (ver §8, punto 4 de los documentos originales). |
| `Balance general.pptx` | Presentación didáctica (19 diapositivas) | — | — | No aplica | Teoría del balance y ejercicios de cargo/abono; sin cifras de Alutech. |
| `Estados-Financieros.pptx` | Presentación didáctica (10 diapositivas) | — | — | No aplica | Ejemplos de estados (ABC, S.A.; Ebenezer, S.A.); sin cifras de Alutech. |
| `libro adm financ.pdf` | Gitman, *Principios de administración financiera*, 11.ª ed. | — | 682 | Referencia teórica | Fórmulas de razones financieras y DuPont; sin cifras de Alutech. |
| `Trabajo de investigación ANF.md` | Trabajo académico (fuente principal de la referencia) | 2021–2025 | 1,969 líneas (texto en 1–1942; imágenes en base64 al final) | Referencia de comparación | Contiene fórmulas en imágenes (`image2` a `image12`) y dos gráficos DuPont (`image13`, `image14`). |
| `Trabajo de investigación ANF.pdf` | Mismo trabajo en PDF | 2021–2025 | 82 | Contraste del Markdown | Ver §6. |

Las dos familias de estados no son homogéneas: **2021–2023 son estados combinados** («Alutech – División Acero», certificados
y auditados) y **2024–2025 son estados consolidados** («Alutech, S. A. de C. V., y subsidiarias – División Acero») preparados
y firmados por la administración, con otra denominación y agrupación de las cuentas.

## 2. Información extraída de los estados financieros de cada año

Transcripción completa con trazabilidad (documento, página del PDF y denominación original). El archivo estructurado
`fuentes/alutech/estados_financieros_2021_2025.json` contiene exactamente estas cifras y es el que carga la aplicación
(`scripts/cargar_alutech.py`). Los paréntesis indican cifras negativas o deducciones, tal como están impresas.

**Comprobaciones realizadas en los cinco ejercicios** (todas se cumplen, 61 de 61 totales impresos):
Activo corriente + Activo no corriente = Activo total; Pasivo corriente + Pasivo no corriente = Pasivo total;
Activo total = Pasivo total + Patrimonio; Ingresos − Costo de ventas = Utilidad bruta; utilidad de operación (cuando se
presenta), utilidad antes de impuestos y utilidad neta = suma de sus partidas; patrimonio de la controladora = patrimonio
total − participaciones no controladoras (2021–2023).

### 2021 — `documentos/Certificacin_EFC_Alutech_Divisin_Acero_2021VF_Mod010925.pdf`

Certificación de estados financieros combinados al 31-12-2021 (Espinoza Auditores, 26-07-2025). Estados auditados por PricewaterhouseCoopers Honduras (informe del 05-02-2024). Alutech - División Acero, estados combinados.

**Estado de situación financiera**

| Clasificación | Cuenta (denominación original) | Importe impreso (USD) | Pág. PDF | Código asignado |
|---|---|---:|---:|---|
| Activo corriente | Efectivo | 10,840,865 | 8 | CB1101 |
| Activo corriente | Certificados de depósitos a plazo fijo | 25,900,000 | 8 | CB1102 |
| Activo corriente | Inversiones en bonos | 2,000,000 | 8 | CB1103 |
| Activo corriente | Cuentas por cobrar comerciales - neto | 53,081,088 | 8 | CB1104 |
| Activo corriente | Cuentas por cobrar a partes relacionadas | 75,454,125 | 8 | CB1105 |
| Activo corriente | Otras cuentas por cobrar | 64,903,087 | 8 | CB1106 |
| Activo corriente | Inventarios - neto | 148,440,504 | 8 | CB1107 |
| Activo corriente | Gastos pagados por anticipado | 1,538,667 | 8 | CB1108 |
| Activo corriente | Anticipos al impuesto sobre la renta | 1,723,211 | 8 | CB1109 |
| Activo no corriente | Certificados de depósitos a plazo fijo | 1,000,000 | 8 | CB1201 |
| Activo no corriente | Inversiones en acciones | 24,950,870 | 8 | CB1204 |
| Activo no corriente | Propiedades de inversión | 5,597,009 | 8 | CB1205 |
| Activo no corriente | Propiedades, planta y equipo - neto | 106,623,719 | 8 | CB1206 |
| Activo no corriente | Activos por derecho de uso - neto | 16,702,267 | 8 | CB1207 |
| Activo no corriente | Activos intangibles - neto | 2,585,345 | 8 | CB1208 |
| Activo no corriente | Plusvalía mercantil | 11,668,154 | 8 | CB1209 |
| Activo no corriente | Otros activos | 299,603 | 8 | CB1210 |
| Activo no corriente | Activo por impuestos sobre la renta diferidos | 646,671 | 8 | CB1211 |
| Pasivo corriente | Préstamos bancarios por pagar | 25,039,997 | 8 | CB2101 |
| Pasivo corriente | Arrendamientos por pagar | 4,872,937 | 8 | CB2102 |
| Pasivo corriente | Obligaciones por derechos titularizados | 1,652,870 | 8 | CB2105 |
| Pasivo corriente | Porción de los documentos por pagar a largo plazo | 80,133 | 8 | CB2106 |
| Pasivo corriente | Cuentas por pagar comérciales | 156,609,253 | 8 | CB2108 |
| Pasivo corriente | Cuentas por pagar a partes relacionadas | 1,171,548 | 8 | CB2109 |
| Pasivo corriente | Otras cuentas por pagar | 8,632,737 | 9 | CB2110 |
| Pasivo corriente | Impuesto sobre la renta por pagar | 7,913,755 | 9 | CB2111 |
| Pasivo no corriente | Préstamos bancarios por pagar | 114,626,074 | 9 | CB2201 |
| Pasivo no corriente | Arrendamientos a largo plazo | 24,556,484 | 9 | CB2202 |
| Pasivo no corriente | Bonos corporativos | 32,758,231 | 9 | CB2203 |
| Pasivo no corriente | Certificados de inversión | 18,271,064 | 9 | CB2204 |
| Pasivo no corriente | Obligaciones por derechos titularizados | 10,847,273 | 9 | CB2205 |
| Pasivo no corriente | Documentos por pagar a largo plazo | 186,964 | 9 | CB2206 |
| Pasivo no corriente | Pasivos por beneficios post empleo | 592,568 | 9 | CB2209 |
| Pasivo no corriente | Pasivo por impuestos diferidos | 822,107 | 9 | CB2211 |
| Patrimonio | Capital social | 79,411,060 | 9 | CB3101 |
| Patrimonio | Aportaciones de capital | 84,787 | 9 | CB3103 |
| Patrimonio | Reserva legal | 4,325,495 | 9 | CB3104 |
| Patrimonio | Otras reservas de capital | -1,183,613 | 9 | CB3105 |
| Patrimonio | Utilidades acumuladas | 59,420,100 | 9 | CB3106 |
| Patrimonio | Participaciones no controladoras | 3,263,361 | 9 | CB3107 |

**Estado de resultados**

| Cuenta (denominación original) | Importe impreso (USD) | Pág. PDF | Código asignado |
|---|---:|---:|---|
| Ingresos de actividades ordinarias | 523,965,227 | 10 | CB4101 |
| Costo de ventas | (367,252,613) | 10 | CB5101 |
| Gastos de administración | (16,733,467) | 10 | CB6101 |
| Gastos de venta y despacho | (36,445,981) | 10 | CB6102 |
| (Pérdidas) reversión por deterioro de valor de cuentas por cobrar, neto | (274,140) | 10 | CB6103 |
| Otros ingresos - neto | 319,877 | 10 | CB6104 |
| Gastos financieros - (neto) | (21,777,725) | 10 | CB7101 |
| Impuesto sobre la renta | (13,198,439) | 10 | CB8101 |

**Totales y subtotales impresos (controles de la extracción)**

| Concepto | Denominación impresa | Importe | Pág. PDF | Verificación |
|---|---|---:|---:|---|
| total_activo_corriente | Total activos corrientes | 383,881,547 | 8 | Coincide con la suma de las partidas |
| total_activo_no_corriente | Total activos no corrientes | 170,073,638 | 8 | Coincide con la suma de las partidas |
| total_activo | Total activos | 553,955,185 | 8 | Coincide con la suma de las partidas |
| total_pasivo_corriente | Total pasivos corrientes | 205,973,230 | 9 | Coincide con la suma de las partidas |
| total_pasivo_no_corriente | Total pasivos no corrientes | 202,660,765 | 9 | Coincide con la suma de las partidas |
| total_pasivo | Total pasivos | 408,633,995 | 9 | Coincide con la suma de las partidas |
| patrimonio_controladora | Total patrimonio atribuible a los propietarios de la controladora | 142,057,829 | 9 | Coincide con la suma de las partidas |
| total_patrimonio | Total patrimonio | 145,321,190 | 9 | Coincide con la suma de las partidas |
| total_pasivo_patrimonio | Total pasivo y patrimonio | 553,955,185 | 9 | Coincide con la suma de las partidas |
| utilidad_bruta | Ganancia bruta | 156,712,614 | 10 | Coincide con la suma de las partidas |
| utilidad_operativa | Utilidad de operación | 103,578,903 | 10 | Coincide con la suma de las partidas |
| utilidad_antes_impuestos | Ganancia antes de impuesto sobre la renta | 81,801,178 | 10 | Coincide con la suma de las partidas |
| utilidad_neta | Ganancia neta del año | 68,602,739 | 10 | Coincide con la suma de las partidas |

**Datos de otros estados (complementarios)**

| Clave | Denominación original | Importe | Pág. PDF | Estado financiero |
|---|---|---:|---:|---|
| utilidad_controladora_er | Atribuible a: Propietarios de la controladora (Estado de resultados) | 66,407,462 | 10 | Estado combinado de resultados |
| utilidad_no_controladora_er | Atribuible a: Participaciones no controladoras (Estado de resultados) | 2,195,277 | 10 | Estado combinado de resultados |
| utilidad_controladora_ecp | Ganancia neta del año atribuible a los propietarios de la controladora (Estado de cambios en el patrimonio) | 66,407,462 | 12 | Estado combinado de cambios en el patrimonio |
| depreciacion_amortizacion_fe | Depreciaciones y amortizaciones (ajuste del flujo de efectivo) | 8,610,532 | 13 | Estado combinado de flujos de efectivo |

### 2022 — `documentos/Certificacin_EFC_Alutech_Divisin_Acero_2022_VFMod_010925.pdf`

Certificación de estados financieros combinados al 31-12-2022 (Espinoza Auditores). Estados auditados por PwC Honduras. Alutech - División Acero, estados combinados.

**Estado de situación financiera**

| Clasificación | Cuenta (denominación original) | Importe impreso (USD) | Pág. PDF | Código asignado |
|---|---|---:|---:|---|
| Activo corriente | Efectivo | 20,155,298 | 8 | CB1101 |
| Activo corriente | Certificados de depósitos a plazo fijo | 7,000,000 | 8 | CB1102 |
| Activo corriente | Cuentas por cobrar comerciales - neto | 32,581,092 | 8 | CB1104 |
| Activo corriente | Cuentas por cobrar a partes relacionadas | 187,750,230 | 8 | CB1105 |
| Activo corriente | Otras cuentas por cobrar | 52,441,213 | 8 | CB1106 |
| Activo corriente | Inventarios | 141,069,442 | 8 | CB1107 |
| Activo corriente | Gastos pagados por anticipado | 1,035,731 | 8 | CB1108 |
| Activo corriente | Anticipos al impuesto sobre la renta | 6,639,395 | 8 | CB1109 |
| Activo no corriente | Certificados de depósitos a plazo fijo | 8,000,000 | 8 | CB1201 |
| Activo no corriente | Inversiones en acciones | 24,658,197 | 8 | CB1204 |
| Activo no corriente | Propiedades de inversión | 6,078,838 | 8 | CB1205 |
| Activo no corriente | Propiedades, planta y equipo - neto | 154,006,305 | 8 | CB1206 |
| Activo no corriente | Activos por derecho de uso - neto | 15,720,434 | 8 | CB1207 |
| Activo no corriente | Activos intangibles - neto | 1,923,631 | 8 | CB1208 |
| Activo no corriente | Plusvalía mercantil | 11,668,154 | 8 | CB1209 |
| Activo no corriente | Otros activos | 473,223 | 8 | CB1210 |
| Activo no corriente | Activo por impuestos sobre la renta diferidos | 823,910 | 8 | CB1211 |
| Pasivo corriente | Préstamos bancarios por pagar | 81,331,433 | 8 | CB2101 |
| Pasivo corriente | Arredramientos por pagar | 5,373,076 | 8 | CB2102 |
| Pasivo corriente | Certificación de inversión | 2,745,704 | 8 | CB2104 |
| Pasivo corriente | Obligaciones por derechos titularizados | 1,817,611 | 8 | CB2105 |
| Pasivo corriente | Porción corriente de los documentos por pagar a largo plazo | 120,013 | 8 | CB2106 |
| Pasivo corriente | Cuentas por pagar comerciales | 96,629,671 | 8 | CB2108 |
| Pasivo corriente | Cuentas por pagar a partes relacionadas | 34,655,602 | 8 | CB2109 |
| Pasivo corriente | Otras cuentas por pagar | 8,854,582 | 8 | CB2110 |
| Pasivo corriente | Impuesto sobre la renta por pagar | 416,488 | 9 | CB2111 |
| Pasivo no corriente | Préstamos bancarios por pagar | 108,327,468 | 9 | CB2201 |
| Pasivo no corriente | Arrendamientos por pagar | 36,108,070 | 9 | CB2202 |
| Pasivo no corriente | Bonos corporativos | 32,083,941 | 9 | CB2203 |
| Pasivo no corriente | Certificados de inversión | 20,447,743 | 9 | CB2204 |
| Pasivo no corriente | Obligaciones por derechos titularizados | 9,029,662 | 9 | CB2205 |
| Pasivo no corriente | Documentos por pagar a largo plazo | 195,923 | 9 | CB2206 |
| Pasivo no corriente | Pasivos por prima en venta de acciones de subsidiaria | 18,771,142 | 9 | CB2208 |
| Pasivo no corriente | Pasivos por beneficios post empleo | 728,759 | 9 | CB2209 |
| Pasivo no corriente | Pasivo por impuesto sobre la renta diferido | 511,441 | 9 | CB2211 |
| Patrimonio | Capital social | 119,389,833 | 9 | CB3101 |
| Patrimonio | Primas sobre acciones | 56,160,201 | 9 | CB3102 |
| Patrimonio | Aportaciones de capital | 84,787 | 9 | CB3103 |
| Patrimonio | Reserva legal | 4,694,588 | 9 | CB3104 |
| Patrimonio | Otras reservas de capital | -2360428 | 9 | CB3105 |
| Patrimonio | Utilidad acumulada | 31,015,221 | 9 | CB3106 |
| Patrimonio | Participación no controladora | 4,892,562 | 9 | CB3107 |

**Estado de resultados**

| Cuenta (denominación original) | Importe impreso (USD) | Pág. PDF | Código asignado |
|---|---:|---:|---|
| Ingresos por actividades ordinarias | 499,653,494 | 10 | CB4101 |
| Costo de ventas | (410,331,156) | 10 | CB5101 |
| Gastos de administración | (18,344,656) | 10 | CB6101 |
| Gastos de venta y despacho | (39,712,552) | 10 | CB6102 |
| Pérdidas por deterioro de valor de cuentas por cobrar | (397,016) | 10 | CB6103 |
| Otros ingresos (neto) | 332,863 | 10 | CB6104 |
| Gastos financieros (neto) | (17,181,342) | 10 | CB7101 |
| Impuesto sobre la renta | (3,960,325) | 10 | CB8101 |

**Totales y subtotales impresos (controles de la extracción)**

| Concepto | Denominación impresa | Importe | Pág. PDF | Verificación |
|---|---|---:|---:|---|
| total_activo_corriente | Total activos corrientes | 448,672,401 | 8 | Coincide con la suma de las partidas |
| total_activo_no_corriente | Total activos no corrientes | 223,352,692 | 8 | Coincide con la suma de las partidas |
| total_activo | Total activos | 672,025,093 | 8 | Coincide con la suma de las partidas |
| total_pasivo_corriente | Total pasivos corrientes | 231,944,180 | 9 | Coincide con la suma de las partidas |
| total_pasivo_no_corriente | Total pasivos no corrientes: | 226,204,149 | 9 | Coincide con la suma de las partidas |
| total_pasivo | Total pasivo | 458,148,329 | 9 | Coincide con la suma de las partidas |
| patrimonio_controladora | Total patrimonio atribuible a los propietarios de la controladora | 208,984,202 | 9 | Coincide con la suma de las partidas |
| total_patrimonio | Total patrimonio | 213,876,764 | 9 | Coincide con la suma de las partidas |
| total_pasivo_patrimonio | Total pasivo y patrimonio | 672,025,093 | 9 | Coincide con la suma de las partidas |
| utilidad_bruta | Ganancia bruta | 89,322,338 | 10 | Coincide con la suma de las partidas |
| utilidad_antes_impuestos | Ganancia antes de impuesto sobre la renta | 14,019,635 | 10 | Coincide con la suma de las partidas |
| utilidad_neta | Ganancia neta del año | 10,059,310 | 10 | Coincide con la suma de las partidas |

**Datos de otros estados (complementarios)**

| Clave | Denominación original | Importe | Pág. PDF | Estado financiero |
|---|---|---:|---:|---|
| utilidad_controladora_ecp | Ganancia neta del año atribuible a los propietarios de la controladora (Estado de cambios en el patrimonio) | 8,559,346 | 12 | Estado combinado de cambios en el patrimonio |
| utilidad_no_controladora_ecp | Ganancia neta del año atribuible a participaciones no controladoras (Estado de cambios en el patrimonio) | 1,499,964 | 12 | Estado combinado de cambios en el patrimonio |
| depreciacion_amortizacion_fe | Depreciaciones y amortizaciones (ajuste del flujo de efectivo) | 10,984,898 | 13 | Estado combinado de flujos de efectivo |

### 2023 — `documentos/Certificacin_EFC_Alutech_Divisin_Acero_2023_VFMod010925.pdf`

Certificación de estados financieros combinados al 31-12-2023 (Espinoza Auditores). Estados auditados por PwC Honduras. Alutech - División Acero, estados combinados.

**Estado de situación financiera**

| Clasificación | Cuenta (denominación original) | Importe impreso (USD) | Pág. PDF | Código asignado |
|---|---|---:|---:|---|
| Activo corriente | Efectivo | 12,130,206 | 6 | CB1101 |
| Activo corriente | Certificados de depósitos a plazo fijo | 7,400,000 | 6 | CB1102 |
| Activo corriente | Cuentas por cobrar comerciales (neto) | 41,272,525 | 6 | CB1104 |
| Activo corriente | Cuentas por cobrar a partes relacionadas | 168,293,969 | 6 | CB1105 |
| Activo corriente | Otras cuentas por cobrar | 54,824,958 | 6 | CB1106 |
| Activo corriente | Inventarios | 141,491,319 | 6 | CB1107 |
| Activo corriente | Gastos pagados por anticipado | 954,879 | 7 | CB1108 |
| Activo corriente | Anticipos al impuesto sobre la renta | 3,426,688 | 7 | CB1109 |
| Activo no corriente | Certificados de depósitos a plazo fijo | 8,000,000 | 7 | CB1201 |
| Activo no corriente | Cuentas por cobrar a partes relacionadas | 110,380,709 | 7 | CB1202 |
| Activo no corriente | Otras cuentas por cobrar | 924,000 | 7 | CB1203 |
| Activo no corriente | Inversiones en acciones | 24,633,711 | 7 | CB1204 |
| Activo no corriente | Propiedades de Inversión | 8,325,372 | 7 | CB1205 |
| Activo no corriente | Propiedades, planta y equipo (neto) | 173,683,163 | 7 | CB1206 |
| Activo no corriente | Activos por derecho de uso (neto) | 15,633,837 | 7 | CB1207 |
| Activo no corriente | Activos intangibles (neto) | 1,413,660 | 7 | CB1208 |
| Activo no corriente | Plusvalía mercantil | 35,293,969 | 7 | CB1209 |
| Activo no corriente | Otros activos | 655,843 | 7 | CB1210 |
| Activo no corriente | Activo por impuesto sobre la renta diferido | 362,138 | 7 | CB1211 |
| Pasivo corriente | Préstamos bancarios por pagar | 95,395,476 | 7 | CB2101 |
| Pasivo corriente | Arrendamientos por pagar | 5,406,547 | 7 | CB2102 |
| Pasivo corriente | Bonos corporativos | 8,181,371 | 7 | CB2103 |
| Pasivo corriente | Certificados de inversión | 2,298,539 | 7 | CB2104 |
| Pasivo corriente | Obligaciones por derechos titularizados | 1,795,145 | 7 | CB2105 |
| Pasivo corriente | Documentos por pagar | 6,703,817 | 7 | CB2107 |
| Pasivo corriente | Cuentas por pagar comerciales | 195,599,671 | 7 | CB2108 |
| Pasivo corriente | Cuentas por pagar a partes relacionadas | 4,512,985 | 7 | CB2109 |
| Pasivo corriente | Otras cuentas por pagar | 12,127,667 | 7 | CB2110 |
| Pasivo corriente | Impuesto sobre la renta por pagar | 1,099,467 | 7 | CB2111 |
| Pasivo no corriente | Préstamos bancarios por pagar | 112,597,844 | 7 | CB2201 |
| Pasivo no corriente | Arrendamientos por pagar | 33,221,918 | 7 | CB2202 |
| Pasivo no corriente | Bonos corporativos | 31,733,829 | 7 | CB2203 |
| Pasivo no corriente | Certificados de inversión | 24,130,415 | 7 | CB2204 |
| Pasivo no corriente | Obligaciones por derechos titularizados | 7,454,491 | 7 | CB2205 |
| Pasivo no corriente | Documentos por pagar | 16,680,822 | 7 | CB2206 |
| Pasivo no corriente | Otras cuentas por pagar | 293,522 | 7 | CB2207 |
| Pasivo no corriente | Pasivo por prima en venta de acciones de subsidiaría | 18,730,404 | 8 | CB2208 |
| Pasivo no corriente | Pasivos por beneficios post empleo | 932,485 | 8 | CB2209 |
| Pasivo no corriente | Impuesto sobre la renta por pagar | 465,955 | 8 | CB2210 |
| Pasivo no corriente | Pasivo por impuesto sobre la renta diferido | 2,065,182 | 8 | CB2211 |
| Patrimonio | Capital social | 119,389,833 | 8 | CB3101 |
| Patrimonio | Prima sobre acciones | 56,160,201 | 8 | CB3102 |
| Patrimonio | Aportaciones de capital | 169,574 | 8 | CB3103 |
| Patrimonio | Reserva legal | 5,540,907 | 8 | CB3104 |
| Patrimonio | Otras reservas de capital | (1,439,577) | 8 | CB3105 |
| Patrimonio | Resultados acumulads | 47,852,456 | 8 | CB3106 |
| Patrimonio | Participaciones no controladoras | - | 8 | CB3107 |

**Estado de resultados**

| Cuenta (denominación original) | Importe impreso (USD) | Pág. PDF | Código asignado |
|---|---:|---:|---|
| Ingresos de actividades ordinarias | 478,623,072 | 9 | CB4101 |
| Costo de ventas | (373,545,631) | 9 | CB5101 |
| Gastos de administración | (19,651,834) | 9 | CB6101 |
| Gastos de venta y despacho | (43,950,554) | 9 | CB6102 |
| Pérdidas por deterioro de valor de cuentas por cobrar | (507,752) | 9 | CB6103 |
| Otros ingresos (neto) | 3,721,720 | 9 | CB6104 |
| Gastos financieros (neto) | (22,016,927) | 9 | CB7101 |
| Impuesto sobre la renta | (9,341,414) | 9 | CB8101 |

**Totales y subtotales impresos (controles de la extracción)**

| Concepto | Denominación impresa | Importe | Pág. PDF | Verificación |
|---|---|---:|---:|---|
| total_activo_corriente | Total activos corrientes | 429,794,544 | 7 | Coincide con la suma de las partidas |
| total_activo_no_corriente | Total activos no corrientes | 379,306,402 | 7 | Coincide con la suma de las partidas |
| total_activo | Total activos | 809,100,946 | 7 | Coincide con la suma de las partidas |
| total_pasivo_corriente | Total pasivos corrientes | 333,120,685 | 7 | Coincide con la suma de las partidas |
| total_pasivo_no_corriente | Total pasivos no corrientes | 248,306,867 | 8 | Coincide con la suma de las partidas |
| total_pasivo | Total pasivos | 581,427,552 | 8 | Coincide con la suma de las partidas |
| patrimonio_controladora | Total patrimonio atribuible a los propietarios de la controladora | 227,673,394 | 8 | Coincide con la suma de las partidas |
| total_patrimonio | Total patrimonio | 227,673,394 | 8 | Coincide con la suma de las partidas |
| total_pasivo_patrimonio | Total pasivo y patrimonio | 809,100,946 | 8 | Coincide con la suma de las partidas |
| utilidad_bruta | Ganancia bruta | 105,077,441 | 9 | Coincide con la suma de las partidas |
| utilidad_antes_impuestos | Ganancia antes de impuesto sobre la renta | 22,672,094 | 9 | Coincide con la suma de las partidas |
| utilidad_neta | Ganancia neta del año | 13,330,680 | 9 | Coincide con la suma de las partidas |

**Datos de otros estados (complementarios)**

| Clave | Denominación original | Importe | Pág. PDF | Estado financiero |
|---|---|---:|---:|---|
| utilidad_controladora_er | Utilidad neta atribuible a: Propietarios de la controladora (Estado de resultados) | 13,330,680 | 9 | Estado combinado de resultados |
| utilidad_no_controladora_er | Utilidad neta atribuible a: Participaciones no controladoras (Estado de resultados) | - | 9 | Estado combinado de resultados |
| utilidad_controladora_ecp | Ganancia neta del año atribuible a los propietarios de la controladora (Estado de cambios en el patrimonio) | 12,309,102 | 11 | Estado combinado de cambios en el patrimonio |
| utilidad_no_controladora_ecp | Ganancia neta del año atribuible a participaciones no controladoras (Estado de cambios en el patrimonio) | 1,021,578 | 11 | Estado combinado de cambios en el patrimonio |
| depreciaciones_fe | Depreciaciones (ajuste del flujo de efectivo) | 11,173,984 | 12 | Estado combinado de flujos de efectivo |
| amortizaciones_fe | Amortizaciones (ajuste del flujo de efectivo) | 592,672 | 12 | Estado combinado de flujos de efectivo |

### 2024 — `documentos/12_EEFF_diciembre_2024.pdf`

Estados consolidados de situación financiera y de resultados al 31-12-2024, firmados por el representante legal y el contador general. PDF escaneado sin capa de texto: transcripción visual verificada con todos los subtotales impresos.

**Estado de situación financiera**

| Clasificación | Cuenta (denominación original) | Importe impreso (USD) | Pág. PDF | Código asignado |
|---|---|---:|---:|---|
| Activo corriente | Efectivo y Equivalentes de Efectivo | 15,782,257 | 1 | CN1101 |
| Activo corriente | Inversiones | 13,935,076 | 1 | CN1102 |
| Activo corriente | Deudores comerciales y Otras Cuentas por Cobrar (Netos) | 97,204,415 | 1 | CN1103 |
| Activo corriente | Cuentas por cobrar Empresas Relacionadas | 182,232,841 | 1 | CN1104 |
| Activo corriente | Inventario (Materiales, Suministros, etc.) | 116,761,311 | 1 | CN1105 |
| Activo corriente | Pagos por Anticipado | 1,939,012 | 1 | CN1106 |
| Activo corriente | Impuestos Corrientes | 4,916,766 | 1 | CN1107 |
| Activo no corriente | Cuentas por cobrar a LP | 983,263 | 1 | CN1201 |
| Activo no corriente | Otras cuentas por cobrar a LP | 118,684,551 | 1 | CN1202 |
| Activo no corriente | Inversiones | 32,166,255 | 1 | CN1204 |
| Activo no corriente | Propiedades de Inversión | 7,052,552 | 1 | CN1205 |
| Activo no corriente | Propiedades, Planta y Equipo (Neto) | 179,359,645 | 1 | CN1206 |
| Activo no corriente | Activos por derechos de Uso(neto) | 17,127,186 | 1 | CN1207 |
| Activo no corriente | Activos intangibles | 38,005,433 | 1 | CN1208 |
| Activo no corriente | Impuestos Diferidos | 223,586 | 1 | CN1209 |
| Activo no corriente | Otros Activos financieros | 802,225 | 1 | CN1210 |
| Pasivo corriente | Préstamos de Corto Plazo | 95,128,624 | 1 | CN2101 |
| Pasivo corriente | Pasivos por arrendamientos | 6,252,051 | 1 | CN2102 |
| Pasivo corriente | Obligaciones Emisión de Títulos valores | 13,447,268 | 1 | CN2103 |
| Pasivo corriente | Otros Pasivos Financieros | 19,727,330 | 1 | CN2104 |
| Pasivo corriente | Acreedores comerciales y Otras Cuentas por Pagar | 225,126,517 | 1 | CN2105 |
| Pasivo corriente | Cuentas por Pagar Empresas Relacionadas | 2,098,612 | 1 | CN2106 |
| Pasivo corriente | Impuestos Corrientes | 1,185,813 | 1 | CN2107 |
| Pasivo no corriente | Préstamos y Otras Obligaciones Financieras | 98,999,095 | 1 | CN2201 |
| Pasivo no corriente | Pasivos por arrendamientos | 34,065,636 | 1 | CN2202 |
| Pasivo no corriente | Obligaciones Emisión de Títulos valores | 68,067,653 | 1 | CN2203 |
| Pasivo no corriente | Otros Pasivos Financieros | 16,811,464 | 1 | CN2204 |
| Pasivo no corriente | Provisiones | 18,192,624 | 1 | CN2205 |
| Pasivo no corriente | Impuestos Diferidos | 2,011,899 | 1 | CN2206 |
| Patrimonio | Capital Social | 119,391,833 | 1 | CN3101 |
| Patrimonio | Capital Adicional | 169,574 | 1 | CN3102 |
| Patrimonio | Reserva Legal | 5,540,907 | 1 | CN3103 |
| Patrimonio | Superávit por Acciones | 56,160,201 | 1 | CN3104 |
| Patrimonio | Reservas de Capital | 5,188,768 | 1 | CN3105 |
| Patrimonio | Efecto de Conversion Entidades Extranjeras | (8,973,683) | 1 | CN3106 |
| Patrimonio | Resultados Acumulados | 45,523,207 | 1 | CN3107 |
| Patrimonio | Resultado del Período | 3,060,981 | 1 | CN3108 |

**Estado de resultados**

| Cuenta (denominación original) | Importe impreso (USD) | Pág. PDF | Código asignado |
|---|---:|---:|---|
| Ingresos Ordinarios | 479,006,719 | 2 | CN4101 |
| Costo de Ventas | (377,459,424) | 2 | CN5101 |
| Gastos de Venta y Distribución | (26,379,749) | 2 | CN6101 |
| Gastos de Administración | (5,898,635) | 2 | CN6102 |
| Gastos de Personal | (26,967,511) | 2 | CN6103 |
| Gastos de Depreciación y Amortización | (7,107,482) | 2 | CN6104 |
| Ingresos Financieros | 15,024,973 | 2 | CN7101 |
| Gastos Financieros | (43,089,283) | 2 | CN7102 |
| Otros Ingresos (Gastos) | 55,570 | 2 | CN7201 |
| Impuestos | (4,124,197) | 2 | CN8101 |

**Totales y subtotales impresos (controles de la extracción)**

| Concepto | Denominación impresa | Importe | Pág. PDF | Verificación |
|---|---|---:|---:|---|
| total_activo_corriente | Total activos circulantes | 432,771,678 | 1 | Coincide con la suma de las partidas |
| total_activo_no_corriente | Total activos no circulantes | 394,404,696 | 1 | Coincide con la suma de las partidas |
| total_activo | Total activos | 827,176,374 | 1 | Coincide con la suma de las partidas |
| total_pasivo_corriente | Total pasivos circulantes | 362,966,215 | 1 | Coincide con la suma de las partidas |
| total_pasivo_no_corriente | Total pasivos no circulantes | 238,148,371 | 1 | Coincide con la suma de las partidas |
| total_pasivo | Total pasivos | 601,114,586 | 1 | Coincide con la suma de las partidas |
| total_patrimonio | Total patrimonio | 226,061,788 | 1 | Coincide con la suma de las partidas |
| total_pasivo_patrimonio | Total pasivos y patrimonio | 827,176,374 | 1 | Coincide con la suma de las partidas |
| utilidad_bruta | Resultado bruto | 101,547,295 | 2 | Coincide con la suma de las partidas |
| utilidad_operativa | Resultado de Operación | 35,193,918 | 2 | Coincide con la suma de las partidas |
| utilidad_antes_impuestos | Resultado antes de Reserva e Impuesto | 7,185,178 | 2 | Coincide con la suma de las partidas |
| utilidad_neta | Resultado del año | 3,060,981 | 2 | Coincide con la suma de las partidas |

### 2025 — `documentos/12_EEFF_diciembre_2025.pdf`

Estados consolidados de situación financiera y de resultados al 31-12-2025, firmados por el representante legal y el contador general.

**Estado de situación financiera**

| Clasificación | Cuenta (denominación original) | Importe impreso (USD) | Pág. PDF | Código asignado |
|---|---|---:|---:|---|
| Activo corriente | Efectivo y Equivalentes de Efectivo | 12,551,085 | 1 | CN1101 |
| Activo corriente | Inversiones | 13,791,656 | 1 | CN1102 |
| Activo corriente | Deudores comerciales y Otras Cuentas por Cobrar (Netos) | 70,169,882 | 1 | CN1103 |
| Activo corriente | Cuentas por cobrar Empresas Relacionadas | 77,574,661 | 1 | CN1104 |
| Activo corriente | Inventario (Materiales, Suministros, etc.) | 69,818,060 | 1 | CN1105 |
| Activo corriente | Pagos por Anticipado | 2,394,829 | 1 | CN1106 |
| Activo corriente | Impuestos Corrientes | 1,405,808 | 1 | CN1107 |
| Activo no corriente | Cuentas por cobrar a LP | 2,544,870 | 1 | CN1201 |
| Activo no corriente | Cuentas por cobrar Empresas Relacionadas a LP | 262,128,668 | 1 | CN1203 |
| Activo no corriente | Inversiones | 25,974,530 | 1 | CN1204 |
| Activo no corriente | Propiedades de Inversión | 12,580,435 | 1 | CN1205 |
| Activo no corriente | Propiedades, Planta y Equipo (Neto) | 180,643,255 | 1 | CN1206 |
| Activo no corriente | Activos por derechos de Uso(neto) | 11,119,749 | 1 | CN1207 |
| Activo no corriente | Activos intangibles | 36,218,193 | 1 | CN1208 |
| Activo no corriente | Impuestos Diferidos | 796,166 | 1 | CN1209 |
| Activo no corriente | Otros Activos financieros | 2,337,714 | 1 | CN1210 |
| Pasivo corriente | Préstamos de Corto Plazo | 87,786,629 | 1 | CN2101 |
| Pasivo corriente | Pasivos por arrendamientos | 4,114,174 | 1 | CN2102 |
| Pasivo corriente | Obligaciones Emisión de Títulos valores | 80,658,329 | 1 | CN2103 |
| Pasivo corriente | Otros Pasivos Financieros | 21,432,441 | 1 | CN2104 |
| Pasivo corriente | Acreedores comerciales y Otras Cuentas por Pagar | 173,120,913 | 1 | CN2105 |
| Pasivo corriente | Cuentas por Pagar Empresas Relacionadas | 3,457,100 | 1 | CN2106 |
| Pasivo corriente | Impuestos Corrientes | 704,421 | 1 | CN2107 |
| Pasivo no corriente | Préstamos y Otras Obligaciones Financieras | 89,087,790 | 1 | CN2201 |
| Pasivo no corriente | Pasivos por arrendamientos | 28,750,278 | 1 | CN2202 |
| Pasivo no corriente | Obligaciones Emisión de Títulos valores | 32,676,388 | 1 | CN2203 |
| Pasivo no corriente | Otros Pasivos Financieros | 7,620,764 | 1 | CN2204 |
| Pasivo no corriente | Provisiones | 17,507,168 | 1 | CN2205 |
| Pasivo no corriente | Impuestos Diferidos | 3,972,968 | 1 | CN2206 |
| Patrimonio | Capital Social | 119,389,833 | 1 | CN3101 |
| Patrimonio | Capital Adicional | 169,574 | 1 | CN3102 |
| Patrimonio | Reserva Legal | 6,503,436 | 1 | CN3103 |
| Patrimonio | Superávit por Acciones | 56,160,201 | 1 | CN3104 |
| Patrimonio | Reservas de Capital | 13,407,214 | 1 | CN3105 |
| Patrimonio | Efecto de Conversion Entidades Extranjeras | (16,976,702) | 1 | CN3106 |
| Patrimonio | Resultados Acumulados | 40,607,655 | 1 | CN3107 |
| Patrimonio | Resultado del Período | 11,898,987 | 1 | CN3108 |

**Estado de resultados**

| Cuenta (denominación original) | Importe impreso (USD) | Pág. PDF | Código asignado |
|---|---:|---:|---|
| Ingresos Ordinarios | 439,704,567 | 2 | CN4101 |
| Costo de Ventas | (331,430,173) | 2 | CN5101 |
| Gastos de Venta y Distribución | (18,950,398) | 2 | CN6101 |
| Gastos de Administración | (5,227,785) | 2 | CN6102 |
| Gastos de Personal | (22,262,768) | 2 | CN6103 |
| Gastos de Depreciación y Amortización | (7,167,799) | 2 | CN6104 |
| Ingresos Financieros | 14,515,895 | 2 | CN7101 |
| Gastos Financieros | (51,914,906) | 2 | CN7102 |
| Otros Ingresos (Gastos) | (811,571) | 2 | CN7202 |
| Impuestos | (4,556,075) | 2 | CN8101 |

**Totales y subtotales impresos (controles de la extracción)**

| Concepto | Denominación impresa | Importe | Pág. PDF | Verificación |
|---|---|---:|---:|---|
| total_activo_corriente | Total activos circulantes | 247,705,981 | 1 | Coincide con la suma de las partidas |
| total_activo_no_corriente | Total activos no circulantes | 534,343,580 | 1 | Coincide con la suma de las partidas |
| total_activo | Total activos | 782,049,561 | 1 | Coincide con la suma de las partidas |
| total_pasivo_corriente | Total pasivos circulantes | 371,274,007 | 1 | Coincide con la suma de las partidas |
| total_pasivo_no_corriente | Total pasivos no circulantes | 179,615,356 | 1 | Coincide con la suma de las partidas |
| total_pasivo | Total pasivos | 550,889,363 | 1 | Coincide con la suma de las partidas |
| total_patrimonio | Total patrimonio | 231,160,198 | 1 | Coincide con la suma de las partidas |
| total_pasivo_patrimonio | Total pasivos y patrimonio | 782,049,561 | 1 | Coincide con la suma de las partidas |
| utilidad_bruta | Resultado bruto | 108,274,394 | 2 | Coincide con la suma de las partidas |
| utilidad_operativa | Resultado de Operación | 54,665,644 | 2 | Coincide con la suma de las partidas |
| utilidad_antes_impuestos | Resultado antes de Reserva e Impuesto | 16,455,062 | 2 | Coincide con la suma de las partidas |
| utilidad_neta | Resultado del Periodo | 11,898,987 | 2 | Coincide con la suma de las partidas |


## 3. Catálogo de cuentas identificado

- 2021–2023 (estados combinados): 49 cuentas de balance distintas (contando por separado las porciones corriente y no
  corriente) y 8 de resultados. 2024–2025 (consolidados): 38 cuentas de balance y 10 líneas de resultados; «Otros Ingresos
  (Gastos)» se registra en dos cuentas (ingreso neto en 2024, gasto neto en 2025) para respetar la convención de signos.
- La aplicación crea **106 cuentas** con la denominación original (códigos `CB…` para la familia combinada y `CN…` para la
  consolidada), conserva la clasificación corriente/no corriente y la naturaleza del documento, y las relaciona entre
  ejercicios mediante **73 grupos de análisis** y 16 rubros. Detalle y justificación de cada equivalencia en
  `MAPEO_FINANCIERO_ALUTECH.md`.
- Cuentas que cambian de denominación o de agrupación entre 2023 y 2024 (principales): «Efectivo» → «Efectivo y
  Equivalentes de Efectivo»; «Certificados de depósitos a plazo fijo» e «Inversiones en bonos» → «Inversiones»;
  «Cuentas por cobrar comerciales» + «Otras cuentas por cobrar» → «Deudores comerciales y Otras Cuentas por Cobrar
  (Netos)»; «Cuentas por pagar comerciales» + «Otras cuentas por pagar» → «Acreedores comerciales y Otras Cuentas por
  Pagar»; préstamos bancarios → «Préstamos de Corto Plazo» / «Préstamos y Otras Obligaciones Financieras»; bonos,
  certificados de inversión y derechos titularizados → «Obligaciones Emisión de Títulos valores»; documentos por pagar →
  «Otros Pasivos Financieros» (presumible, no demostrable); «Prima sobre acciones» → «Superávit por Acciones» (mismo
  importe, 56,160,201); «Aportaciones de capital» → «Capital Adicional» (mismo importe que 2023, 169,574); «Otras reservas
  de capital» → «Reservas de Capital» + «Efecto de Conversión»; «Utilidades acumuladas» (incluye el resultado del año) →
  «Resultados Acumulados» + «Resultado del Período»; desaparecen «Plusvalía mercantil» y «Participaciones no
  controladoras»; aparecen «Gastos de Personal», «Gastos de Depreciación y Amortización», «Ingresos Financieros» y
  «Provisiones».
- Dentro de 2021–2023 hay variantes de escritura que se tratan como la misma cuenta y se conservan como denominación
  original de cada año: «Arredramientos por pagar» (2022), «Certificación de inversión» (2022), «Resultados acumulads»
  (2023), «Cuentas por pagar comérciales» (2021), «Utilidad acumulada» (2022).

## 4. Indicadores y fórmulas encontrados en el trabajo

| Sección | Indicador | Fórmula en el trabajo | Datos que usa el trabajo | Observación |
|---|---|---|---|---|
| 5.6 a, 6.5, 8.1 C, 9.2.1 | Capital de trabajo neto / fondo de maniobra CP | AC − PC | Totales del balance | — |
| 9.2.2 | Fondo de maniobra LP | (Patrimonio + PNC) − ANC | Totales del balance | Demuestra que FM CP = FM LP. |
| 5.6 b, 8.1 A | Razón corriente | AC / PC | Totales | — |
| 5.6 c, 8.1 B | Prueba ácida | (AC − Inventarios) / PC | Totales e inventarios | — |
| 5.6 d | Razón de efectivo | Efectivo / PC | — | Definida, **no calculada** en el trabajo. |
| 9.1 | Razón de tesorería | (Tesorería + valores negociables) / PC × 100 | Efectivo + depósitos a plazo + bonos (2021–2023); efectivo + inversiones (2024–2025) | — |
| 5.6 e–f, 8.2 B, 9.3 | Rotación de CxC y PPC | 5.6: ventas a crédito / CxC promedio; aplicado: ingresos / CxC al cierre; PPC = 365 / rotación = CxC / ingresos × 365 | Ingresos ordinarios como aproximación | Saldos al cierre (no hay balance 2020). Base de CxC no homogénea en 8.2 B (ver §8). |
| 5.6 g–h, 8.2 A, 9.3 | Rotación de inventarios, PPI / EPI | Costo de ventas / inventarios; 365 / rotación | Saldos al cierre | — |
| 5.6 i–j, 9.3 | Rotación de CxP, PPP | 5.6: compras a crédito / CxP promedio; aplicado en 9.3: CxP comerciales / costo de ventas × 365 | Costo de ventas como aproximación de las compras | En 8.2 C el trabajo considera inviable el PPP y en 9.3 lo calcula con la aproximación. |
| 5.6 k, 8.2 C, 9.3 | Ciclo operativo y ciclo de conversión del efectivo | CO = PPI + PPC; CCE = CO − PPP | — | — |
| 8.2 D | Rotación de activos totales | Ingresos / activo total | — | — |
| 8.3 A | Índice de endeudamiento | Pasivo total / activo total × 100 | — | También PC / pasivo total (texto). |
| 8.3 B | Razón de cargos de interés fijo | Utilidad de operación / gastos financieros | Gastos financieros **netos** (2024–2025: gastos − ingresos financieros) | — |
| 8.3 C | Cobertura de pagos fijos | — | — | No se cuantifica (falta desglose). |
| 8.3 D | Razón deuda‑capital | Pasivo total / patrimonio total | — | — |
| 8.4 A–C | Márgenes bruto, operativo y neto | Utilidad / ingresos × 100 | — | — |
| 8.4 D, 8.5 | EPS, P/E, M/L | — | — | Declarados **no calculables** (sin número ni precio de acciones). |
| 8.4 E–F | ROA y ROE | Utilidad neta / activo o patrimonio total al cierre × 100 | — | Patrimonio total (incluye no controladoras). |
| 6.7 | EBITDA 2025 | Utilidad de operación + depreciación y amortización | — | Solo 2025 (texto). |
| 6.3, 6.4 | Análisis horizontal | ΔV = Vt − Vt−1; Δ% = ΔV / Vt−1 × 100 | Rubros clave y totales (Tablas 3–5); CTN (Tablas 6–7) | El trabajo advierte sobre bases cero o negativas. |
| 7.1, 7.2 | Análisis vertical | Partida / ingresos × 100; partida / activo total × 100 | — | Costos y gastos con signo negativo. |
| 9.4 | WACC | Σ peso × costo neto; deuda × (1 − t); Ke = ROE | Tasas de 6.75 % a 8.50 % y ISR 30 % (supuestos) | Tasas tomadas de notas del informe auditado que **no** están en `documentos/`; 2024–2025 sin cita. |
| 9.5, 9.6 | DuPont (RSA, RSP) total y de la controladora | RSA = margen neto × rotación; RSP = RSA × MAF; MAF = activo / patrimonio | Utilidad y patrimonio atribuibles a la controladora (2021–2023 del estado de cambios en el patrimonio) | — |
| 9.7 | Estado de origen y aplicación de fondos 2025 vs 2024 y 2023 vs 2022 | Variaciones del balance: activo ↓ = fuente, ↑ = uso; pasivo/patrimonio ↑ = fuente, ↓ = uso | Balances por cuenta | No es un flujo de efectivo. |
| 10 | Comparación con Ternium | — | Cifras de Ternium de fuente externa | Fuera del alcance: no verificable con los documentos. |

## 5. Resultados de referencia del trabajo ANF

Se registraron **736 valores numéricos** del trabajo (secciones 6.4 a 10, años 2021–2025) en
`fuentes/anf/resultados_referencia.json`, cada uno con su sección, tabla, concepto, métrica equivalente de la aplicación,
unidad y precisión presentada. Incluyen: Tablas 3, 4 y 5 (análisis horizontal), Tablas 6 y 7 (capital de trabajo), textos
de 6.7, vertical del estado de resultados (75 valores) y del balance (40), liquidez (8.1), actividad (8.2), endeudamiento
(8.3), rentabilidad (8.4), razones de mercado (8.5, «no calculable»), tesorería (9.1), fondo de maniobra (9.2), ciclo de
conversión (9.3), cuadro comparativo del WACC (9.4), DuPont total y de la controladora (9.5–9.6), origen y aplicación 2025
vs 2024 y 2023 vs 2022 (9.7) y las cifras de Alutech de la sección 10. El detalle por valor y su comparación están en
`INFORME_VALIDACION_FINANCIERA.md` (sección 5).

Resumen de los principales resultados que presenta el trabajo:

| Indicador | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|---:|
| Capital de trabajo (8.1 / 9.2) | 177,908,317 | 216,728,221 | 96,673,859 | 69,805,463 | −123,568,026 |
| Capital de trabajo (Tabla 6) | 177,908,317 | 216,758,221 | 198,973,859 | 69,805,463 | −123,568,026 |
| Razón corriente (8.1 / Tabla 6) | 1.86 | 1.93 | 1.29 / 1.58 | 1.19 | 0.67 |
| Prueba ácida (8.1 / Tabla 6) | 1.14 | 1.33 | 0.87 / 1.17 | 0.87 | 0.48 |
| Razón de tesorería | 18.81 % | 11.71 % | 5.86 % | 8.19 % | 7.10 % |
| Endeudamiento | 73.77 % | 68.17 % | 71.86 % | 72.67 % | 70.44 % |
| Cobertura de intereses | 4.76 | 1.82 | 2.03 | 1.25 | 1.46 |
| Margen neto | 13.09 % | 2.01 % | 2.79 % | 0.64 % | 2.71 % |
| ROA / ROE | 12.38 % / 47.21 % | 1.50 % / 4.70 % | 1.65 % / 5.86 % | 0.37 % / 1.35 % | 1.52 % / 5.15 % |
| CCE (días) | 28.86 | 63.33 | −21.40 | −30.72 | −55.52 |
| WACC | 14.59 % | 3.83 % | 3.88 % (texto: 3.87 %) | 2.58 % | 3.85 % |

## 6. Diferencias entre las versiones Markdown y PDF

Método: se extrajo el texto del PDF (`pdftotext -table`, 82 páginas) y se compararon el índice, los títulos y el conjunto
de cifras de ambas versiones (1,067 cifras distintas en el Markdown, 1,187 fragmentos en el PDF).

Resultado: **ambas versiones corresponden al mismo contenido**. Tienen los mismos 12 capítulos y subsecciones (índice de
la pág. 2–3 del PDF), las mismas tablas y las mismas cifras. Las diferencias encontradas son solo de extracción o formato:

- En el PDF las celdas largas de las tablas se parten en varias líneas (p. ej. «342,120» / «,685»), lo que genera
  fragmentos numéricos que no aparecen como tales en el Markdown; reconstruidas, las cifras son iguales.
- Las fórmulas de 7.1, 7.2 y 8.1 son imágenes (`image2`–`image12`) y los dos gráficos DuPont (`image13`, `image14`) están
  incrustados en base64 al final del Markdown; en el PDF aparecen en su posición. Su contenido se verificó con las tablas
  de resultados correspondientes.
- El Markdown conserva escapes de formato (`\$`, `\-`, `\*`) y anclas `{#…}`; el PDF tiene numeración de páginas y saltos.
- Artefactos comunes a ambas versiones (no son diferencias entre ellas): «2021-20252» en 6.4 (llamada de nota pegada al
  año), «Razón corriente (RC)l» en 5.6 b, separadores de miles con punto en las tablas DuPont (523.965.227) y decimales con
  coma (12,38 %).

No se encontró ninguna cifra que difiera entre el Markdown y el PDF.

## 7. Información faltante o insuficiente

| Información | Efecto | Tratamiento en la aplicación |
|---|---|---|
| Balance general 2020 (solo hay el patrimonio 2020 en el estado de cambios en el patrimonio 2021) | No pueden calcularse saldos promedio para 2021 | Indicadores con saldos al cierre (criterio del trabajo). El reporte DuPont existente (promedios) marca 2021 como APROXIMADO. |
| Notas a los estados financieros (tasas de interés, vencimientos, composición de cuentas) | Las tasas del WACC no son verificables | Tasas registradas como supuestos del trabajo (`fuentes/anf/supuestos_wacc.json`), separadas de los datos. |
| Ventas a crédito, compras y CxC/CxP comerciales separadas en 2024–2025 | Rotaciones aproximadas; base no homogénea | Ingresos y costo de ventas como aproximación (como el trabajo); notas en cada indicador. |
| Número y precio de las acciones | EPS, P/E y M/L no calculables | Se presentan como «no calculable» con la causa. |
| Estados de flujos de efectivo y de cambios en el patrimonio 2024–2025 | Sin depreciación separada del flujo, sin atribución de la utilidad | D&A 2024–2025 del estado de resultados; utilidad de la controladora = utilidad neta (supuesto explícito, sin no controladoras presentadas). |
| Utilidad de operación 2022 y 2023 | No se presenta en el estado de resultados | Subtotal calculado por la aplicación (31,200,977 y 44,689,021). |
| Depreciación y amortización 2021–2023 | No es una línea del estado de resultados | Dato complementario del estado de flujos de efectivo (para el EBITDA). |
| Cifras de Ternium (sección 10) | Fuente externa | Fuera del alcance; no se registran. |
| Desglose de cuotas de arrendamiento y amortización del principal | Cobertura de pagos fijos no calculable | Indicador «no calculable» con la causa. |

## 8. Observaciones sobre posibles inconsistencias

**En el trabajo ANF** (detalle y efecto en `INFORME_VALIDACION_FINANCIERA.md`):

1. Activo corriente 2023 = 541,094,544 y pasivo corriente 2023 = 342,120,685 en las Tablas 3, 4 y 6; el documento presenta
   429,794,544 y 333,120,685, y el propio trabajo usa estas últimas en 7.2, 8.1 y 9.2. Las cifras del trabajo no están en
   ningún documento; en magnitud coinciden con el informe PCR (otro perímetro).
2. Pasivo corriente 2022 = 231,914,180 en las Tablas 3, 6 y 7 (documento: 231,944,180).
3. Utilidad operativa 2022 = 31,200,000* en la Tabla 5 (exacta: 31,200,977, usada en 8.3 y 8.4).
4. 8.2 B mezcla bases de cuentas por cobrar (comerciales en 2021–2022; comerciales + otras en 2023).
5. WACC 2023: 3.88 % en el cuadro y 3.87 % en el texto.
6. Erratas sin efecto numérico: divisor 553,995,185 en 9.5 (el resultado usa 553,955,185); «68,602.739».
7. 9.4: las tasas citan notas del informe auditado que no forman parte de los documentos disponibles; 2024–2025 sin cita.

**En los documentos originales** (no afectan los totales; se conservan tal como están):

1. 2023: la utilidad atribuible a la controladora es 13,330,680 en el estado de resultados y 12,309,102 en el estado de
   cambios en el patrimonio (con 1,021,578 para las no controladoras).
2. 2024: capital social 119,391,833 frente a 119,389,833 en 2022, 2023 y 2025.
3. 2021: el estado de cambios en el patrimonio cierra en 145,321,189 (no controladoras 3,263,360) frente a 145,321,190
   (3,263,361) en el balance.
4. 2024 «Otras cuentas por cobrar a LP» (118,684,551) no se identifica como partida con relacionadas; en 2025 la línea de
   esa posición se denomina «Cuentas por cobrar Empresas Relacionadas a LP». **Revisión final (2026-11-02):** el balance
   resumido del informe PCR presenta a dic‑24 «Cuentas por cobrar de LP» 119.7 M (= 983,263 + 118,684,551) y «Cuentas por
   cobrar a partes relacionadas» no corrientes 0.0 (121.9 M recién a jun‑25). No hay evidencia de que la partida de 2024
   sea con relacionadas: la aplicación no adopta esa equivalencia.
5. La certificación 2021 menciona tasas de ISR y hechos de 2023 (redactada en 2025).
