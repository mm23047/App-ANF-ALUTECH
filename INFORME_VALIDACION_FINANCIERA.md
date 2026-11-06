# Informe de validación financiera — Alutech 2021–2025

Generado automáticamente el 2026-11-02 con `scripts/generar_informe_validacion.py` a partir de la base de datos de la aplicación. Compara los resultados que **calcula la aplicación** con los datos originales de los estados financieros (carpeta `documentos/`) contra los **resultados de referencia** publicados en el «Trabajo de investigación ANF». Los valores del trabajo nunca se usan como datos ni como resultados calculados.

## 1. Método y criterios

Para cada valor numérico del trabajo (registrado en `fuentes/anf/resultados_referencia.json` con su sección, tabla, unidad y precisión): (1) se toman los datos originales de la BD; (2) se aplica la fórmula implementada (`calculations/`); (3) se obtiene el resultado calculado; (4) se recupera el valor de referencia; (5) se comparan; (6) se calcula la diferencia absoluta y (7) la porcentual; (8) se clasifica; (9) se documenta la causa (`fuentes/anf/observaciones_validacion.json`).

| Estado | Criterio |
|---|---|
| Coincide | El valor calculado, redondeado (mitad hacia arriba) a la precisión con que el trabajo presenta el dato, es igual al de referencia. |
| Coincidencia por redondeo | No es igual tras redondear, pero la diferencia no supera **una unidad del último decimal presentado** (0.01 en porcentajes y razones con 2 decimales, 0.1 días con 1 decimal, 1 USD en importes enteros). Justificación: el trabajo opera con cifras intermedias ya redondeadas (sumas de días o de aportes al WACC redondeados). |
| Diferencia | La diferencia supera esa tolerancia. Se investiga la causa en el orden de la consigna (extracción, clasificación, conjunto de cuentas, fórmula, base, redondeo, error aritmético, clasificación entre ejercicios). |
| No verificable | La aplicación no puede calcular el valor con los datos disponibles. |
| No aplica | El trabajo declara el indicador no calculable y la aplicación llega a la misma conclusión. |

Ningún dato original ni ninguna fórmula se modificó para provocar una coincidencia.

## 2. Resumen

| Estado | Valores comparados |
|---|---|
| Coincide | 672 |
| Coincidencia por redondeo | 6 |
| Diferencia | 43 |
| No verificable | 0 |
| No aplica | 15 |
| **Total** | **736** |

## 3. Comparación por ejercicio

| Ejercicio | Coincide | Coincidencia por redondeo | Diferencia | No verificable | No aplica | Total |
|---|---|---|---|---|---|---|
| 2021 | 100 | 1 | 0 | 0 | 3 | 104 |
| 2022 | 114 | 1 | 11 | 0 | 3 | 129 |
| 2023 | 160 | 2 | 21 | 0 | 3 | 186 |
| 2024 | 120 | 0 | 8 | 0 | 3 | 131 |
| 2025 | 178 | 2 | 3 | 0 | 3 | 186 |

## 4. Comparación por sección del trabajo

| Sección | Tabla / apartado | Coincide | Coincidencia por redondeo | Diferencia | No verificable | No aplica |
|---|---|---|---|---|---|---|
| 6.4 | Tabla 3 | 47 | 0 | 9 | 0 | 0 |
| 6.4 | Tabla 4 | 50 | 0 | 6 | 0 | 0 |
| 6.4 | Tabla 5 | 62 | 0 | 1 | 0 | 0 |
| 6.5 | Tabla 6 | 20 | 0 | 13 | 0 | 0 |
| 6.6 | Tabla 7 | 4 | 0 | 8 | 0 | 0 |
| 6.7 | Texto | 3 | 0 | 0 | 0 | 0 |
| 7.1 | Vertical ER | 75 | 0 | 0 | 0 | 0 |
| 7.2 | Vertical BG | 40 | 0 | 0 | 0 | 0 |
| 8.1 | Tabla de liquidez | 15 | 0 | 0 | 0 | 0 |
| 8.2 A | Rotación de inventarios | 10 | 0 | 0 | 0 | 0 |
| 8.2 B | Rotación de CxC | 11 | 1 | 3 | 0 | 0 |
| 8.2 C | Texto | 1 | 1 | 0 | 0 | 0 |
| 8.2 D | Rotación de activos totales | 5 | 0 | 0 | 0 | 0 |
| 8.3 A | Índice de endeudamiento | 5 | 0 | 0 | 0 | 0 |
| 8.3 A | Texto | 1 | 1 | 0 | 0 | 0 |
| 8.3 B | Cobertura de intereses | 15 | 0 | 0 | 0 | 0 |
| 8.3 D | Razón deuda-capital | 5 | 0 | 0 | 0 | 0 |
| 8.4 A | Margen bruto | 5 | 0 | 0 | 0 | 0 |
| 8.4 B | Margen operativo | 5 | 0 | 0 | 0 | 0 |
| 8.4 C | Margen neto | 5 | 0 | 0 | 0 | 0 |
| 8.4 C | Texto | 1 | 0 | 0 | 0 | 0 |
| 8.4 D | EPS | 0 | 0 | 0 | 0 | 5 |
| 8.4 E | ROA | 5 | 0 | 0 | 0 | 0 |
| 8.4 F | ROE | 5 | 0 | 0 | 0 | 0 |
| 8.5 A | Razones de mercado | 0 | 0 | 0 | 0 | 5 |
| 8.5 B | Razones de mercado | 0 | 0 | 0 | 0 | 5 |
| 9.1 | Razón de tesorería | 15 | 0 | 0 | 0 | 0 |
| 9.2.1 | Fondo de maniobra (CP) | 10 | 0 | 0 | 0 | 0 |
| 9.2.2 | Fondo de maniobra (LP) | 16 | 0 | 0 | 0 | 0 |
| 9.3 | Ciclo de conversión de efectivo | 28 | 2 | 0 | 0 | 0 |
| 9.4 | Comparativo del WACC | 54 | 1 | 0 | 0 | 0 |
| 9.4.3 | Texto 2023 | 1 | 0 | 0 | 0 | 0 |
| 9.5 | Sistema DuPont (RSA) | 15 | 0 | 0 | 0 | 0 |
| 9.5 | Texto 2021 | 1 | 0 | 0 | 0 | 0 |
| 9.6 | DuPont modificado (RSP) | 10 | 0 | 0 | 0 | 0 |
| 9.6 | DuPont controladora | 30 | 0 | 0 | 0 | 0 |
| 9.7 | Origen y aplicación 2025 vs 2024 | 36 | 0 | 2 | 0 | 0 |
| 9.7 | Texto | 2 | 0 | 1 | 0 | 0 |
| 9.7 | Origen y aplicación 2023 vs 2022 | 48 | 0 | 0 | 0 | 0 |
| 10 | Alutech vs. Ternium | 11 | 0 | 0 | 0 | 0 |

## 5. Comparación por indicador (resultado de la aplicación vs. trabajo ANF)

| Ref. | Secc. | Indicador / concepto | Año | Resultado aplicación | Resultado trabajo ANF | Diferencia | Unidad | Estado |
|---|---|---|---|---|---|---|---|---|
| T3-EFE | 6.4 | Efectivo y equivalentes | 2021 | 10,840,865 | 10,840,865 | 0 | USD | Coincide |
| T3-EFE | 6.4 | Efectivo y equivalentes | 2022 | 20,155,298 | 20,155,298 | 0 | USD | Coincide |
| T3-EFE | 6.4 | Efectivo y equivalentes | 2023 | 12,130,206 | 12,130,206 | 0 | USD | Coincide |
| T3-EFE-VA | 6.4 | Efectivo y equivalentes: variación absoluta | 2022 | 9,314,433 | 9,314,433 | 0 | USD | Coincide |
| T3-EFE-VA | 6.4 | Efectivo y equivalentes: variación absoluta | 2023 | -8,025,092 | -8,025,092 | 0 | USD | Coincide |
| T3-EFE-VR | 6.4 | Efectivo y equivalentes: variación relativa | 2022 | 85.9196 | 85.92 | -0.00 | % | Coincide |
| T3-EFE-VR | 6.4 | Efectivo y equivalentes: variación relativa | 2023 | -39.8163 | -39.82 | 0.00 | % | Coincide |
| T3-CXC | 6.4 | Cuentas por cobrar comerciales | 2021 | 53,081,088 | 53,081,088 | 0 | USD | Coincide |
| T3-CXC | 6.4 | Cuentas por cobrar comerciales | 2022 | 32,581,092 | 32,581,092 | 0 | USD | Coincide |
| T3-CXC | 6.4 | Cuentas por cobrar comerciales | 2023 | 41,272,525 | 41,272,525 | 0 | USD | Coincide |
| T3-CXC-VA | 6.4 | Cuentas por cobrar comerciales: variación absoluta | 2022 | -20,499,996 | -20,499,996 | 0 | USD | Coincide |
| T3-CXC-VA | 6.4 | Cuentas por cobrar comerciales: variación absoluta | 2023 | 8,691,433 | 8,691,433 | 0 | USD | Coincide |
| T3-CXC-VR | 6.4 | Cuentas por cobrar comerciales: variación relativa | 2022 | -38.6202 | -38.62 | -0.00 | % | Coincide |
| T3-CXC-VR | 6.4 | Cuentas por cobrar comerciales: variación relativa | 2023 | 26.6763 | 26.68 | -0.00 | % | Coincide |
| T3-INV | 6.4 | Inventarios (neto) | 2021 | 148,440,504 | 148,440,504 | 0 | USD | Coincide |
| T3-INV | 6.4 | Inventarios (neto) | 2022 | 141,069,442 | 141,069,442 | 0 | USD | Coincide |
| T3-INV | 6.4 | Inventarios (neto) | 2023 | 141,491,319 | 141,491,319 | 0 | USD | Coincide |
| T3-INV-VA | 6.4 | Inventarios: variación absoluta | 2022 | -7,371,062 | -7,371,062 | 0 | USD | Coincide |
| T3-INV-VA | 6.4 | Inventarios: variación absoluta | 2023 | 421,877 | 421,877 | 0 | USD | Coincide |
| T3-INV-VR | 6.4 | Inventarios: variación relativa | 2022 | -4.9657 | -4.97 | 0.00 | % | Coincide |
| T3-INV-VR | 6.4 | Inventarios: variación relativa | 2023 | 0.2991 | 0.30 | -0.00 | % | Coincide |
| T3-AC | 6.4 | Total activo corriente | 2021 | 383,881,547 | 383,881,547 | 0 | USD | Coincide |
| T3-AC | 6.4 | Total activo corriente | 2022 | 448,672,401 | 448,672,401 | 0 | USD | Coincide |
| T3-AC | 6.4 | Total activo corriente | 2023 | 429,794,544 | 541,094,544 | -111,300,000 | USD | Diferencia |
| T3-AC-VA | 6.4 | Activo corriente: variación absoluta | 2022 | 64,790,854 | 64,790,854 | 0 | USD | Coincide |
| T3-AC-VA | 6.4 | Activo corriente: variación absoluta | 2023 | -18,877,857 | 92,422,143 | -111,300,000 | USD | Diferencia |
| T3-AC-VR | 6.4 | Activo corriente: variación relativa | 2022 | 16.8778 | 16.88 | -0.00 | % | Coincide |
| T3-AC-VR | 6.4 | Activo corriente: variación relativa | 2023 | -4.2075 | 20.60 | -24.81 | % | Diferencia |
| T3-PC | 6.4 | Total pasivo corriente | 2021 | 205,973,230 | 205,973,230 | 0 | USD | Coincide |
| T3-PC | 6.4 | Total pasivo corriente | 2022 | 231,944,180 | 231,914,180 | 30,000 | USD | Diferencia |
| T3-PC | 6.4 | Total pasivo corriente | 2023 | 333,120,685 | 342,120,685 | -9,000,000 | USD | Diferencia |
| T3-PC-VA | 6.4 | Pasivo corriente: variación absoluta | 2022 | 25,970,950 | 25,940,950 | 30,000 | USD | Diferencia |
| T3-PC-VA | 6.4 | Pasivo corriente: variación absoluta | 2023 | 101,176,505 | 110,206,505 | -9,030,000 | USD | Diferencia |
| T3-PC-VR | 6.4 | Pasivo corriente: variación relativa | 2022 | 12.6089 | 12.59 | 0.02 | % | Diferencia |
| T3-PC-VR | 6.4 | Pasivo corriente: variación relativa | 2023 | 43.6211 | 47.52 | -3.90 | % | Diferencia |
| T3-TA | 6.4 | Total activo | 2021 | 553,955,185 | 553,955,185 | 0 | USD | Coincide |
| T3-TA | 6.4 | Total activo | 2022 | 672,025,093 | 672,025,093 | 0 | USD | Coincide |
| T3-TA | 6.4 | Total activo | 2023 | 809,100,946 | 809,100,946 | 0 | USD | Coincide |
| T3-TA-VA | 6.4 | Total activo: variación absoluta | 2022 | 118,069,908 | 118,069,908 | 0 | USD | Coincide |
| T3-TA-VA | 6.4 | Total activo: variación absoluta | 2023 | 137,075,853 | 137,075,853 | 0 | USD | Coincide |
| T3-TA-VR | 6.4 | Total activo: variación relativa | 2022 | 21.3140 | 21.31 | 0.00 | % | Coincide |
| T3-TA-VR | 6.4 | Total activo: variación relativa | 2023 | 20.3974 | 20.40 | -0.00 | % | Coincide |
| T3-TP | 6.4 | Total pasivo | 2021 | 408,633,995 | 408,633,995 | 0 | USD | Coincide |
| T3-TP | 6.4 | Total pasivo | 2022 | 458,148,329 | 458,148,329 | 0 | USD | Coincide |
| T3-TP | 6.4 | Total pasivo | 2023 | 581,427,552 | 581,427,552 | 0 | USD | Coincide |
| T3-TP-VA | 6.4 | Total pasivo: variación absoluta | 2022 | 49,514,334 | 49,514,334 | 0 | USD | Coincide |
| T3-TP-VA | 6.4 | Total pasivo: variación absoluta | 2023 | 123,279,223 | 123,279,223 | 0 | USD | Coincide |
| T3-TP-VR | 6.4 | Total pasivo: variación relativa | 2022 | 12.1170 | 12.12 | -0.00 | % | Coincide |
| T3-TP-VR | 6.4 | Total pasivo: variación relativa | 2023 | 26.9081 | 26.91 | -0.00 | % | Coincide |
| T3-PAT | 6.4 | Total patrimonio | 2021 | 145,321,190 | 145,321,190 | 0 | USD | Coincide |
| T3-PAT | 6.4 | Total patrimonio | 2022 | 213,876,764 | 213,876,764 | 0 | USD | Coincide |
| T3-PAT | 6.4 | Total patrimonio | 2023 | 227,673,394 | 227,673,394 | 0 | USD | Coincide |
| T3-PAT-VA | 6.4 | Total patrimonio: variación absoluta | 2022 | 68,555,574 | 68,555,574 | 0 | USD | Coincide |
| T3-PAT-VA | 6.4 | Total patrimonio: variación absoluta | 2023 | 13,796,630 | 13,796,630 | 0 | USD | Coincide |
| T3-PAT-VR | 6.4 | Total patrimonio: variación relativa | 2022 | 47.1752 | 47.18 | -0.00 | % | Coincide |
| T3-PAT-VR | 6.4 | Total patrimonio: variación relativa | 2023 | 6.4507 | 6.45 | 0.00 | % | Coincide |
| T4-EFE | 6.4 | Efectivo y equivalentes | 2023 | 12,130,206 | 12,130,206 | 0 | USD | Coincide |
| T4-EFE | 6.4 | Efectivo y equivalentes | 2024 | 15,782,257 | 15,782,257 | 0 | USD | Coincide |
| T4-EFE | 6.4 | Efectivo y equivalentes | 2025 | 12,551,085 | 12,551,085 | 0 | USD | Coincide |
| T4-EFE-VA | 6.4 | Efectivo y equivalentes: variación absoluta | 2024 | 3,652,051 | 3,652,051 | 0 | USD | Coincide |
| T4-EFE-VA | 6.4 | Efectivo y equivalentes: variación absoluta | 2025 | -3,231,172 | -3,231,172 | 0 | USD | Coincide |
| T4-EFE-VR | 6.4 | Efectivo y equivalentes: variación relativa | 2024 | 30.1071 | 30.11 | -0.00 | % | Coincide |
| T4-EFE-VR | 6.4 | Efectivo y equivalentes: variación relativa | 2025 | -20.4734 | -20.47 | -0.00 | % | Coincide |
| T4-CXC | 6.4 | Cuentas por cobrar comerciales y otras cuentas por cobrar | 2023 | 96,097,483 | 96,097,483 | 0 | USD | Coincide |
| T4-CXC | 6.4 | Cuentas por cobrar comerciales y otras cuentas por cobrar | 2024 | 97,204,415 | 97,204,415 | 0 | USD | Coincide |
| T4-CXC | 6.4 | Cuentas por cobrar comerciales y otras cuentas por cobrar | 2025 | 70,169,882 | 70,169,882 | 0 | USD | Coincide |
| T4-CXC-VA | 6.4 | CxC comerciales y otras: variación absoluta | 2024 | 1,106,932 | 1,106,932 | 0 | USD | Coincide |
| T4-CXC-VA | 6.4 | CxC comerciales y otras: variación absoluta | 2025 | -27,034,533 | -27,034,533 | 0 | USD | Coincide |
| T4-CXC-VR | 6.4 | CxC comerciales y otras: variación relativa | 2024 | 1.1519 | 1.15 | 0.00 | % | Coincide |
| T4-CXC-VR | 6.4 | CxC comerciales y otras: variación relativa | 2025 | -27.8120 | -27.81 | -0.00 | % | Coincide |
| T4-INV | 6.4 | Inventarios (neto) | 2023 | 141,491,319 | 141,491,319 | 0 | USD | Coincide |
| T4-INV | 6.4 | Inventarios (neto) | 2024 | 116,761,311 | 116,761,311 | 0 | USD | Coincide |
| T4-INV | 6.4 | Inventarios (neto) | 2025 | 69,818,060 | 69,818,060 | 0 | USD | Coincide |
| T4-INV-VA | 6.4 | Inventarios: variación absoluta | 2024 | -24,730,008 | -24,730,008 | 0 | USD | Coincide |
| T4-INV-VA | 6.4 | Inventarios: variación absoluta | 2025 | -46,943,251 | -46,943,251 | 0 | USD | Coincide |
| T4-INV-VR | 6.4 | Inventarios: variación relativa | 2024 | -17.4781 | -17.48 | 0.00 | % | Coincide |
| T4-INV-VR | 6.4 | Inventarios: variación relativa | 2025 | -40.2045 | -40.20 | -0.00 | % | Coincide |
| T4-AC | 6.4 | Total activo corriente | 2023 | 429,794,544 | 541,094,544 | -111,300,000 | USD | Diferencia |
| T4-AC | 6.4 | Total activo corriente | 2024 | 432,771,678 | 432,771,678 | 0 | USD | Coincide |
| T4-AC | 6.4 | Total activo corriente | 2025 | 247,705,981 | 247,705,981 | 0 | USD | Coincide |
| T4-AC-VA | 6.4 | Activo corriente: variación absoluta | 2024 | 2,977,134 | -108,322,866 | 111,300,000 | USD | Diferencia |
| T4-AC-VA | 6.4 | Activo corriente: variación absoluta | 2025 | -185,065,697 | -185,065,697 | 0 | USD | Coincide |
| T4-AC-VR | 6.4 | Activo corriente: variación relativa | 2024 | 0.6927 | -20.02 | 20.71 | % | Diferencia |
| T4-AC-VR | 6.4 | Activo corriente: variación relativa | 2025 | -42.7629 | -42.76 | -0.00 | % | Coincide |
| T4-PC | 6.4 | Total pasivo corriente | 2023 | 333,120,685 | 342,120,685 | -9,000,000 | USD | Diferencia |
| T4-PC | 6.4 | Total pasivo corriente | 2024 | 362,966,215 | 362,966,215 | 0 | USD | Coincide |
| T4-PC | 6.4 | Total pasivo corriente | 2025 | 371,274,007 | 371,274,007 | 0 | USD | Coincide |
| T4-PC-VA | 6.4 | Pasivo corriente: variación absoluta | 2024 | 29,845,530 | 20,845,530 | 9,000,000 | USD | Diferencia |
| T4-PC-VA | 6.4 | Pasivo corriente: variación absoluta | 2025 | 8,307,792 | 8,307,792 | 0 | USD | Coincide |
| T4-PC-VR | 6.4 | Pasivo corriente: variación relativa | 2024 | 8.9594 | 6.09 | 2.87 | % | Diferencia |
| T4-PC-VR | 6.4 | Pasivo corriente: variación relativa | 2025 | 2.2889 | 2.29 | -0.00 | % | Coincide |
| T4-TA | 6.4 | Total activo | 2023 | 809,100,946 | 809,100,946 | 0 | USD | Coincide |
| T4-TA | 6.4 | Total activo | 2024 | 827,176,374 | 827,176,374 | 0 | USD | Coincide |
| T4-TA | 6.4 | Total activo | 2025 | 782,049,561 | 782,049,561 | 0 | USD | Coincide |
| T4-TA-VA | 6.4 | Total activo: variación absoluta | 2024 | 18,075,428 | 18,075,428 | 0 | USD | Coincide |
| T4-TA-VA | 6.4 | Total activo: variación absoluta | 2025 | -45,126,813 | -45,126,813 | 0 | USD | Coincide |
| T4-TA-VR | 6.4 | Total activo: variación relativa | 2024 | 2.2340 | 2.23 | 0.00 | % | Coincide |
| T4-TA-VR | 6.4 | Total activo: variación relativa | 2025 | -5.4555 | -5.46 | 0.00 | % | Coincide |
| T4-TP | 6.4 | Total pasivo | 2023 | 581,427,552 | 581,427,552 | 0 | USD | Coincide |
| T4-TP | 6.4 | Total pasivo | 2024 | 601,114,586 | 601,114,586 | 0 | USD | Coincide |
| T4-TP | 6.4 | Total pasivo | 2025 | 550,889,363 | 550,889,363 | 0 | USD | Coincide |
| T4-TP-VA | 6.4 | Total pasivo: variación absoluta | 2024 | 19,687,034 | 19,687,034 | 0 | USD | Coincide |
| T4-TP-VA | 6.4 | Total pasivo: variación absoluta | 2025 | -50,225,223 | -50,225,223 | 0 | USD | Coincide |
| T4-TP-VR | 6.4 | Total pasivo: variación relativa | 2024 | 3.3860 | 3.39 | -0.00 | % | Coincide |
| T4-TP-VR | 6.4 | Total pasivo: variación relativa | 2025 | -8.3553 | -8.36 | 0.00 | % | Coincide |
| T4-PAT | 6.4 | Total patrimonio | 2023 | 227,673,394 | 227,673,394 | 0 | USD | Coincide |
| T4-PAT | 6.4 | Total patrimonio | 2024 | 226,061,788 | 226,061,788 | 0 | USD | Coincide |
| T4-PAT | 6.4 | Total patrimonio | 2025 | 231,160,198 | 231,160,198 | 0 | USD | Coincide |
| T4-PAT-VA | 6.4 | Total patrimonio: variación absoluta | 2024 | -1,611,606 | -1,611,606 | 0 | USD | Coincide |
| T4-PAT-VA | 6.4 | Total patrimonio: variación absoluta | 2025 | 5,098,410 | 5,098,410 | 0 | USD | Coincide |
| T4-PAT-VR | 6.4 | Total patrimonio: variación relativa | 2024 | -0.7079 | -0.71 | 0.00 | % | Coincide |
| T4-PAT-VR | 6.4 | Total patrimonio: variación relativa | 2025 | 2.2553 | 2.26 | -0.00 | % | Coincide |
| T5-ING | 6.4 | Ingresos ordinarios | 2021 | 523,965,227 | 523,965,227 | 0 | USD | Coincide |
| T5-ING | 6.4 | Ingresos ordinarios | 2022 | 499,653,494 | 499,653,494 | 0 | USD | Coincide |
| T5-ING | 6.4 | Ingresos ordinarios | 2023 | 478,623,072 | 478,623,072 | 0 | USD | Coincide |
| T5-ING | 6.4 | Ingresos ordinarios | 2024 | 479,006,719 | 479,006,719 | 0 | USD | Coincide |
| T5-ING | 6.4 | Ingresos ordinarios | 2025 | 439,704,567 | 439,704,567 | 0 | USD | Coincide |
| T5-ING-VR | 6.4 | Ingresos ordinarios: variación relativa | 2022 | -4.6400 | -4.64 | 0.00 | % | Coincide |
| T5-ING-VR | 6.4 | Ingresos ordinarios: variación relativa | 2023 | -4.2090 | -4.21 | 0.00 | % | Coincide |
| T5-ING-VR | 6.4 | Ingresos ordinarios: variación relativa | 2024 | 0.0802 | 0.08 | 0.00 | % | Coincide |
| T5-ING-VR | 6.4 | Ingresos ordinarios: variación relativa | 2025 | -8.2049 | -8.20 | -0.00 | % | Coincide |
| T5-CV | 6.4 | Costo de ventas | 2021 | 367,252,613 | 367,252,613 | 0 | USD | Coincide |
| T5-CV | 6.4 | Costo de ventas | 2022 | 410,331,156 | 410,331,156 | 0 | USD | Coincide |
| T5-CV | 6.4 | Costo de ventas | 2023 | 373,545,631 | 373,545,631 | 0 | USD | Coincide |
| T5-CV | 6.4 | Costo de ventas | 2024 | 377,459,424 | 377,459,424 | 0 | USD | Coincide |
| T5-CV | 6.4 | Costo de ventas | 2025 | 331,430,173 | 331,430,173 | 0 | USD | Coincide |
| T5-CV-VR | 6.4 | Costo de ventas: variación relativa | 2022 | 11.7299 | 11.73 | -0.00 | % | Coincide |
| T5-CV-VR | 6.4 | Costo de ventas: variación relativa | 2023 | -8.9648 | -8.96 | -0.00 | % | Coincide |
| T5-CV-VR | 6.4 | Costo de ventas: variación relativa | 2024 | 1.0477 | 1.05 | -0.00 | % | Coincide |
| T5-CV-VR | 6.4 | Costo de ventas: variación relativa | 2025 | -12.1945 | -12.19 | -0.00 | % | Coincide |
| T5-UB | 6.4 | Utilidad bruta | 2021 | 156,712,614 | 156,712,614 | 0 | USD | Coincide |
| T5-UB | 6.4 | Utilidad bruta | 2022 | 89,322,338 | 89,322,338 | 0 | USD | Coincide |
| T5-UB | 6.4 | Utilidad bruta | 2023 | 105,077,441 | 105,077,441 | 0 | USD | Coincide |
| T5-UB | 6.4 | Utilidad bruta | 2024 | 101,547,295 | 101,547,295 | 0 | USD | Coincide |
| T5-UB | 6.4 | Utilidad bruta | 2025 | 108,274,394 | 108,274,394 | 0 | USD | Coincide |
| T5-UB-VR | 6.4 | Utilidad bruta: variación relativa | 2022 | -43.0025 | -43.00 | -0.00 | % | Coincide |
| T5-UB-VR | 6.4 | Utilidad bruta: variación relativa | 2023 | 17.6385 | 17.64 | -0.00 | % | Coincide |
| T5-UB-VR | 6.4 | Utilidad bruta: variación relativa | 2024 | -3.3596 | -3.36 | 0.00 | % | Coincide |
| T5-UB-VR | 6.4 | Utilidad bruta: variación relativa | 2025 | 6.6246 | 6.62 | 0.00 | % | Coincide |
| T5-GO | 6.4 | Gastos operativos* | 2021 | 53,179,448 | 53,179,448 | 0 | USD | Coincide |
| T5-GO | 6.4 | Gastos operativos* | 2022 | 58,057,208 | 58,057,208 | 0 | USD | Coincide |
| T5-GO | 6.4 | Gastos operativos* | 2023 | 63,602,388 | 63,602,388 | 0 | USD | Coincide |
| T5-GO | 6.4 | Gastos operativos* | 2024 | 66,353,377 | 66,353,377 | 0 | USD | Coincide |
| T5-GO | 6.4 | Gastos operativos* | 2025 | 53,608,750 | 53,608,750 | 0 | USD | Coincide |
| T5-GO-VR | 6.4 | Gastos operativos: variación relativa | 2022 | 9.1723 | 9.17 | 0.00 | % | Coincide |
| T5-GO-VR | 6.4 | Gastos operativos: variación relativa | 2023 | 9.5512 | 9.55 | 0.00 | % | Coincide |
| T5-GO-VR | 6.4 | Gastos operativos: variación relativa | 2024 | 4.3253 | 4.33 | -0.00 | % | Coincide |
| T5-GO-VR | 6.4 | Gastos operativos: variación relativa | 2025 | -19.2072 | -19.21 | 0.00 | % | Coincide |
| T5-UO | 6.4 | Utilidad operativa | 2021 | 103,578,903 | 103,578,903 | 0 | USD | Coincide |
| T5-UO | 6.4 | Utilidad operativa | 2022 | 31,200,977 | 31,200,000 | 977 | USD | Diferencia |
| T5-UO | 6.4 | Utilidad operativa | 2023 | 44,689,021 | 44,689,021 | 0 | USD | Coincide |
| T5-UO | 6.4 | Utilidad operativa | 2024 | 35,193,918 | 35,193,918 | 0 | USD | Coincide |
| T5-UO | 6.4 | Utilidad operativa | 2025 | 54,665,644 | 54,665,644 | 0 | USD | Coincide |
| T5-UO-VR | 6.4 | Utilidad operativa: variación relativa | 2022 | -69.8771 | -69.88 | 0.00 | % | Coincide |
| T5-UO-VR | 6.4 | Utilidad operativa: variación relativa | 2023 | 43.2296 | 43.23 | -0.00 | % | Coincide |
| T5-UO-VR | 6.4 | Utilidad operativa: variación relativa | 2024 | -21.2471 | -21.25 | 0.00 | % | Coincide |
| T5-UO-VR | 6.4 | Utilidad operativa: variación relativa | 2025 | 55.3270 | 55.33 | -0.00 | % | Coincide |
| T5-GF | 6.4 | Gastos financieros netos | 2021 | 21,777,725 | 21,777,725 | 0 | USD | Coincide |
| T5-GF | 6.4 | Gastos financieros netos | 2022 | 17,181,342 | 17,181,342 | 0 | USD | Coincide |
| T5-GF | 6.4 | Gastos financieros netos | 2023 | 22,016,927 | 22,016,927 | 0 | USD | Coincide |
| T5-GF | 6.4 | Gastos financieros netos | 2024 | 28,064,310 | 28,064,310 | 0 | USD | Coincide |
| T5-GF | 6.4 | Gastos financieros netos | 2025 | 37,399,011 | 37,399,011 | 0 | USD | Coincide |
| T5-GF-VR | 6.4 | Gastos financieros netos: variación relativa | 2022 | -21.1059 | -21.11 | 0.00 | % | Coincide |
| T5-GF-VR | 6.4 | Gastos financieros netos: variación relativa | 2023 | 28.1444 | 28.14 | 0.00 | % | Coincide |
| T5-GF-VR | 6.4 | Gastos financieros netos: variación relativa | 2024 | 27.4670 | 27.47 | -0.00 | % | Coincide |
| T5-GF-VR | 6.4 | Gastos financieros netos: variación relativa | 2025 | 33.2618 | 33.26 | 0.00 | % | Coincide |
| T5-UN | 6.4 | Utilidad neta del año | 2021 | 68,602,739 | 68,602,739 | 0 | USD | Coincide |
| T5-UN | 6.4 | Utilidad neta del año | 2022 | 10,059,310 | 10,059,310 | 0 | USD | Coincide |
| T5-UN | 6.4 | Utilidad neta del año | 2023 | 13,330,680 | 13,330,680 | 0 | USD | Coincide |
| T5-UN | 6.4 | Utilidad neta del año | 2024 | 3,060,981 | 3,060,981 | 0 | USD | Coincide |
| T5-UN | 6.4 | Utilidad neta del año | 2025 | 11,898,987 | 11,898,987 | 0 | USD | Coincide |
| T5-UN-VR | 6.4 | Utilidad neta: variación relativa | 2022 | -85.3369 | -85.34 | 0.00 | % | Coincide |
| T5-UN-VR | 6.4 | Utilidad neta: variación relativa | 2023 | 32.5208 | 32.52 | 0.00 | % | Coincide |
| T5-UN-VR | 6.4 | Utilidad neta: variación relativa | 2024 | -77.0381 | -77.04 | 0.00 | % | Coincide |
| T5-UN-VR | 6.4 | Utilidad neta: variación relativa | 2025 | 288.7312 | 288.73 | 0.00 | % | Coincide |
| T6-AC | 6.5 | Activo corriente | 2021 | 383,881,547 | 383,881,547 | 0 | USD | Coincide |
| T6-AC | 6.5 | Activo corriente | 2022 | 448,672,401 | 448,672,401 | 0 | USD | Coincide |
| T6-AC | 6.5 | Activo corriente | 2023 | 429,794,544 | 541,094,544 | -111,300,000 | USD | Diferencia |
| T6-AC | 6.5 | Activo corriente | 2024 | 432,771,678 | 432,771,678 | 0 | USD | Coincide |
| T6-AC | 6.5 | Activo corriente | 2025 | 247,705,981 | 247,705,981 | 0 | USD | Coincide |
| T6-PC | 6.5 | Pasivo corriente | 2021 | 205,973,230 | 205,973,230 | 0 | USD | Coincide |
| T6-PC | 6.5 | Pasivo corriente | 2022 | 231,944,180 | 231,914,180 | 30,000 | USD | Diferencia |
| T6-PC | 6.5 | Pasivo corriente | 2023 | 333,120,685 | 342,120,685 | -9,000,000 | USD | Diferencia |
| T6-PC | 6.5 | Pasivo corriente | 2024 | 362,966,215 | 362,966,215 | 0 | USD | Coincide |
| T6-PC | 6.5 | Pasivo corriente | 2025 | 371,274,007 | 371,274,007 | 0 | USD | Coincide |
| T6-CTN | 6.5 | Capital de trabajo neto | 2021 | 177,908,317 | 177,908,317 | 0 | USD | Coincide |
| T6-CTN | 6.5 | Capital de trabajo neto | 2022 | 216,728,221 | 216,758,221 | -30,000 | USD | Diferencia |
| T6-CTN | 6.5 | Capital de trabajo neto | 2023 | 96,673,859 | 198,973,859 | -102,300,000 | USD | Diferencia |
| T6-CTN | 6.5 | Capital de trabajo neto | 2024 | 69,805,463 | 69,805,463 | 0 | USD | Coincide |
| T6-CTN | 6.5 | Capital de trabajo neto | 2025 | -123,568,026 | -123,568,026 | 0 | USD | Coincide |
| T6-CTN-VA | 6.5 | CTN: variación absoluta | 2022 | 38,819,904 | 38,849,904 | -30,000 | USD | Diferencia |
| T6-CTN-VA | 6.5 | CTN: variación absoluta | 2023 | -120,054,362 | -17,784,362 | -102,270,000 | USD | Diferencia |
| T6-CTN-VA | 6.5 | CTN: variación absoluta | 2024 | -26,868,396 | -129,168,396 | 102,300,000 | USD | Diferencia |
| T6-CTN-VA | 6.5 | CTN: variación absoluta | 2025 | -193,373,489 | -193,373,489 | 0 | USD | Coincide |
| T6-CTN-VR | 6.5 | CTN: variación relativa | 2022 | 21.8202 | 21.84 | -0.02 | % | Diferencia |
| T6-CTN-VR | 6.5 | CTN: variación relativa | 2023 | -55.3940 | -8.20 | -47.19 | % | Diferencia |
| T6-CTN-VR | 6.5 | CTN: variación relativa | 2024 | -27.7928 | -64.92 | 37.13 | % | Diferencia |
| T6-CTN-VR | 6.5 | CTN: variación relativa | 2025 | -277.0177 | -277.02 | 0.00 | % | Coincide |
| T6-RC | 6.5 | Razón corriente | 2021 | 1.8637 | 1.86 | 0.00 | veces | Coincide |
| T6-RC | 6.5 | Razón corriente | 2022 | 1.9344 | 1.93 | 0.00 | veces | Coincide |
| T6-RC | 6.5 | Razón corriente | 2023 | 1.2902 | 1.58 | -0.29 | veces | Diferencia |
| T6-RC | 6.5 | Razón corriente | 2024 | 1.1923 | 1.19 | 0.00 | veces | Coincide |
| T6-RC | 6.5 | Razón corriente | 2025 | 0.6672 | 0.67 | -0.00 | veces | Coincide |
| T6-PA | 6.5 | Prueba ácida | 2021 | 1.1431 | 1.14 | 0.00 | veces | Coincide |
| T6-PA | 6.5 | Prueba ácida | 2022 | 1.3262 | 1.33 | -0.00 | veces | Coincide |
| T6-PA | 6.5 | Prueba ácida | 2023 | 0.8655 | 1.17 | -0.30 | veces | Diferencia |
| T6-PA | 6.5 | Prueba ácida | 2024 | 0.8706 | 0.87 | 0.00 | veces | Coincide |
| T6-PA | 6.5 | Prueba ácida | 2025 | 0.4791 | 0.48 | -0.00 | veces | Coincide |
| T7-CTN | 6.6 | CTN final | 2022 | 216,728,221 | 216,758,221 | -30,000 | USD | Diferencia |
| T7-CTN | 6.6 | CTN final | 2023 | 96,673,859 | 198,973,859 | -102,300,000 | USD | Diferencia |
| T7-CTN | 6.6 | CTN final | 2024 | 69,805,463 | 69,805,463 | 0 | USD | Coincide |
| T7-CTN | 6.6 | CTN final | 2025 | -123,568,026 | -123,568,026 | 0 | USD | Coincide |
| T7-CTN-VA | 6.6 | Variación absoluta del CTN | 2022 | 38,819,904 | 38,849,904 | -30,000 | USD | Diferencia |
| T7-CTN-VA | 6.6 | Variación absoluta del CTN | 2023 | -120,054,362 | -17,784,362 | -102,270,000 | USD | Diferencia |
| T7-CTN-VA | 6.6 | Variación absoluta del CTN | 2024 | -26,868,396 | -129,168,396 | 102,300,000 | USD | Diferencia |
| T7-CTN-VA | 6.6 | Variación absoluta del CTN | 2025 | -193,373,489 | -193,373,489 | 0 | USD | Coincide |
| T7-CTN-VR | 6.6 | Variación relativa del CTN | 2022 | 21.8202 | 21.84 | -0.02 | % | Diferencia |
| T7-CTN-VR | 6.6 | Variación relativa del CTN | 2023 | -55.3940 | -8.20 | -47.19 | % | Diferencia |
| T7-CTN-VR | 6.6 | Variación relativa del CTN | 2024 | -27.7928 | -64.92 | 37.13 | % | Diferencia |
| T7-CTN-VR | 6.6 | Variación relativa del CTN | 2025 | -277.0177 | -277.02 | 0.00 | % | Coincide |
| S67-PC-ACUM | 6.7 | Incremento acumulado del pasivo corriente 2021–2025 | 2025 | 80.2535 | 80.25 | 0.00 | % | Coincide |
| S67-EBITDA | 6.7 | EBITDA convencional 2025 (millones) | 2025 | 61.8334 | 61.83 | 0.00 | USD | Coincide |
| S67-DA | 6.7 | Depreciación y amortización 2025 (millones) | 2025 | 7.1678 | 7.17 | -0.00 | USD | Coincide |
| V1-ING | 7.1 | Ingresos ordinarios (% de ingresos) | 2021 | 100.0000 | 100.00 | 0.00 | % | Coincide |
| V1-ING | 7.1 | Ingresos ordinarios (% de ingresos) | 2022 | 100.0000 | 100.00 | 0.00 | % | Coincide |
| V1-ING | 7.1 | Ingresos ordinarios (% de ingresos) | 2023 | 100.0000 | 100.00 | 0.00 | % | Coincide |
| V1-ING | 7.1 | Ingresos ordinarios (% de ingresos) | 2024 | 100.0000 | 100.00 | 0.00 | % | Coincide |
| V1-ING | 7.1 | Ingresos ordinarios (% de ingresos) | 2025 | 100.0000 | 100.00 | 0.00 | % | Coincide |
| V1-CV | 7.1 | Costo de ventas (% de ingresos) | 2021 | -70.0910 | -70.09 | -0.00 | % | Coincide |
| V1-CV | 7.1 | Costo de ventas (% de ingresos) | 2022 | -82.1231 | -82.12 | -0.00 | % | Coincide |
| V1-CV | 7.1 | Costo de ventas (% de ingresos) | 2023 | -78.0459 | -78.05 | 0.00 | % | Coincide |
| V1-CV | 7.1 | Costo de ventas (% de ingresos) | 2024 | -78.8004 | -78.80 | -0.00 | % | Coincide |
| V1-CV | 7.1 | Costo de ventas (% de ingresos) | 2025 | -75.3756 | -75.38 | 0.00 | % | Coincide |
| V1-UB | 7.1 | Ganancia bruta (% de ingresos) | 2021 | 29.9090 | 29.91 | -0.00 | % | Coincide |
| V1-UB | 7.1 | Ganancia bruta (% de ingresos) | 2022 | 17.8769 | 17.88 | -0.00 | % | Coincide |
| V1-UB | 7.1 | Ganancia bruta (% de ingresos) | 2023 | 21.9541 | 21.95 | 0.00 | % | Coincide |
| V1-UB | 7.1 | Ganancia bruta (% de ingresos) | 2024 | 21.1996 | 21.20 | -0.00 | % | Coincide |
| V1-UB | 7.1 | Ganancia bruta (% de ingresos) | 2025 | 24.6244 | 24.62 | 0.00 | % | Coincide |
| V1-ADM | 7.1 | Gastos de administración (% de ingresos) | 2021 | -3.1936 | -3.19 | -0.00 | % | Coincide |
| V1-ADM | 7.1 | Gastos de administración (% de ingresos) | 2022 | -3.6715 | -3.67 | -0.00 | % | Coincide |
| V1-ADM | 7.1 | Gastos de administración (% de ingresos) | 2023 | -4.1059 | -4.11 | 0.00 | % | Coincide |
| V1-ADM | 7.1 | Gastos de administración (% de ingresos) | 2024 | -1.2314 | -1.23 | -0.00 | % | Coincide |
| V1-ADM | 7.1 | Gastos de administración (% de ingresos) | 2025 | -1.1889 | -1.19 | 0.00 | % | Coincide |
| V1-VTA | 7.1 | Gastos de venta y despacho o distribución (% de ingresos) | 2021 | -6.9558 | -6.96 | 0.00 | % | Coincide |
| V1-VTA | 7.1 | Gastos de venta y despacho o distribución (% de ingresos) | 2022 | -7.9480 | -7.95 | 0.00 | % | Coincide |
| V1-VTA | 7.1 | Gastos de venta y despacho o distribución (% de ingresos) | 2023 | -9.1827 | -9.18 | -0.00 | % | Coincide |
| V1-VTA | 7.1 | Gastos de venta y despacho o distribución (% de ingresos) | 2024 | -5.5072 | -5.51 | 0.00 | % | Coincide |
| V1-VTA | 7.1 | Gastos de venta y despacho o distribución (% de ingresos) | 2025 | -4.3098 | -4.31 | 0.00 | % | Coincide |
| V1-DET | 7.1 | Deterioro de cuentas por cobrar (% de ingresos) | 2021 | -0.0523 | -0.05 | -0.00 | % | Coincide |
| V1-DET | 7.1 | Deterioro de cuentas por cobrar (% de ingresos) | 2022 | -0.0795 | -0.08 | 0.00 | % | Coincide |
| V1-DET | 7.1 | Deterioro de cuentas por cobrar (% de ingresos) | 2023 | -0.1061 | -0.11 | 0.00 | % | Coincide |
| V1-DET | 7.1 | Deterioro de cuentas por cobrar (% de ingresos) | 2024 | 0.0000 | 0.00 | 0.00 | % | Coincide |
| V1-DET | 7.1 | Deterioro de cuentas por cobrar (% de ingresos) | 2025 | 0.0000 | 0.00 | 0.00 | % | Coincide |
| V1-PER | 7.1 | Gastos de personal (% de ingresos) | 2021 | 0.0000 | 0.00 | 0.00 | % | Coincide |
| V1-PER | 7.1 | Gastos de personal (% de ingresos) | 2022 | 0.0000 | 0.00 | 0.00 | % | Coincide |
| V1-PER | 7.1 | Gastos de personal (% de ingresos) | 2023 | 0.0000 | 0.00 | 0.00 | % | Coincide |
| V1-PER | 7.1 | Gastos de personal (% de ingresos) | 2024 | -5.6299 | -5.63 | 0.00 | % | Coincide |
| V1-PER | 7.1 | Gastos de personal (% de ingresos) | 2025 | -5.0631 | -5.06 | -0.00 | % | Coincide |
| V1-DA | 7.1 | Depreciación y amortización (% de ingresos) | 2021 | 0.0000 | 0.00 | 0.00 | % | Coincide |
| V1-DA | 7.1 | Depreciación y amortización (% de ingresos) | 2022 | 0.0000 | 0.00 | 0.00 | % | Coincide |
| V1-DA | 7.1 | Depreciación y amortización (% de ingresos) | 2023 | 0.0000 | 0.00 | 0.00 | % | Coincide |
| V1-DA | 7.1 | Depreciación y amortización (% de ingresos) | 2024 | -1.4838 | -1.48 | -0.00 | % | Coincide |
| V1-DA | 7.1 | Depreciación y amortización (% de ingresos) | 2025 | -1.6301 | -1.63 | -0.00 | % | Coincide |
| V1-OTR | 7.1 | Otros ingresos o gastos (% de ingresos) | 2021 | 0.0610 | 0.06 | 0.00 | % | Coincide |
| V1-OTR | 7.1 | Otros ingresos o gastos (% de ingresos) | 2022 | 0.0666 | 0.07 | -0.00 | % | Coincide |
| V1-OTR | 7.1 | Otros ingresos o gastos (% de ingresos) | 2023 | 0.7776 | 0.78 | -0.00 | % | Coincide |
| V1-OTR | 7.1 | Otros ingresos o gastos (% de ingresos) | 2024 | 0.0116 | 0.01 | 0.00 | % | Coincide |
| V1-OTR | 7.1 | Otros ingresos o gastos (% de ingresos) | 2025 | -0.1846 | -0.18 | -0.00 | % | Coincide |
| V1-UO | 7.1 | Resultado operativo (% de ingresos) | 2021 | 19.7683 | 19.77 | -0.00 | % | Coincide |
| V1-UO | 7.1 | Resultado operativo (% de ingresos) | 2022 | 6.2445 | 6.24 | 0.00 | % | Coincide |
| V1-UO | 7.1 | Resultado operativo (% de ingresos) | 2023 | 9.3370 | 9.34 | -0.00 | % | Coincide |
| V1-UO | 7.1 | Resultado operativo (% de ingresos) | 2024 | 7.3473 | 7.35 | -0.00 | % | Coincide |
| V1-UO | 7.1 | Resultado operativo (% de ingresos) | 2025 | 12.4324 | 12.43 | 0.00 | % | Coincide |
| V1-IF | 7.1 | Ingresos financieros (% de ingresos) | 2021 | 0.0000 | 0.00 | 0.00 | % | Coincide |
| V1-IF | 7.1 | Ingresos financieros (% de ingresos) | 2022 | 0.0000 | 0.00 | 0.00 | % | Coincide |
| V1-IF | 7.1 | Ingresos financieros (% de ingresos) | 2023 | 0.0000 | 0.00 | 0.00 | % | Coincide |
| V1-IF | 7.1 | Ingresos financieros (% de ingresos) | 2024 | 3.1367 | 3.14 | -0.00 | % | Coincide |
| V1-IF | 7.1 | Ingresos financieros (% de ingresos) | 2025 | 3.3013 | 3.30 | 0.00 | % | Coincide |
| V1-GF | 7.1 | Gastos financieros (% de ingresos) | 2021 | -4.1563 | -4.16 | 0.00 | % | Coincide |
| V1-GF | 7.1 | Gastos financieros (% de ingresos) | 2022 | -3.4387 | -3.44 | 0.00 | % | Coincide |
| V1-GF | 7.1 | Gastos financieros (% de ingresos) | 2023 | -4.6001 | -4.60 | -0.00 | % | Coincide |
| V1-GF | 7.1 | Gastos financieros (% de ingresos) | 2024 | -8.9955 | -9.00 | 0.00 | % | Coincide |
| V1-GF | 7.1 | Gastos financieros (% de ingresos) | 2025 | -11.8068 | -11.81 | 0.00 | % | Coincide |
| V1-UAI | 7.1 | Resultado antes de impuestos (% de ingresos) | 2021 | 15.6119 | 15.61 | 0.00 | % | Coincide |
| V1-UAI | 7.1 | Resultado antes de impuestos (% de ingresos) | 2022 | 2.8059 | 2.81 | -0.00 | % | Coincide |
| V1-UAI | 7.1 | Resultado antes de impuestos (% de ingresos) | 2023 | 4.7369 | 4.74 | -0.00 | % | Coincide |
| V1-UAI | 7.1 | Resultado antes de impuestos (% de ingresos) | 2024 | 1.5000 | 1.50 | 0.00 | % | Coincide |
| V1-UAI | 7.1 | Resultado antes de impuestos (% de ingresos) | 2025 | 3.7423 | 3.74 | 0.00 | % | Coincide |
| V1-ISR | 7.1 | Impuestos sobre la renta (% de ingresos) | 2021 | -2.5190 | -2.52 | 0.00 | % | Coincide |
| V1-ISR | 7.1 | Impuestos sobre la renta (% de ingresos) | 2022 | -0.7926 | -0.79 | -0.00 | % | Coincide |
| V1-ISR | 7.1 | Impuestos sobre la renta (% de ingresos) | 2023 | -1.9517 | -1.95 | -0.00 | % | Coincide |
| V1-ISR | 7.1 | Impuestos sobre la renta (% de ingresos) | 2024 | -0.8610 | -0.86 | -0.00 | % | Coincide |
| V1-ISR | 7.1 | Impuestos sobre la renta (% de ingresos) | 2025 | -1.0362 | -1.04 | 0.00 | % | Coincide |
| V1-UN | 7.1 | Ganancia o resultado neto (% de ingresos) | 2021 | 13.0930 | 13.09 | 0.00 | % | Coincide |
| V1-UN | 7.1 | Ganancia o resultado neto (% de ingresos) | 2022 | 2.0133 | 2.01 | 0.00 | % | Coincide |
| V1-UN | 7.1 | Ganancia o resultado neto (% de ingresos) | 2023 | 2.7852 | 2.79 | -0.00 | % | Coincide |
| V1-UN | 7.1 | Ganancia o resultado neto (% de ingresos) | 2024 | 0.6390 | 0.64 | -0.00 | % | Coincide |
| V1-UN | 7.1 | Ganancia o resultado neto (% de ingresos) | 2025 | 2.7061 | 2.71 | -0.00 | % | Coincide |
| V2-AC | 7.2 | Activos corrientes (% de activos) | 2021 | 69.2983 | 69.30 | -0.00 | % | Coincide |
| V2-AC | 7.2 | Activos corrientes (% de activos) | 2022 | 66.7642 | 66.76 | 0.00 | % | Coincide |
| V2-AC | 7.2 | Activos corrientes (% de activos) | 2023 | 53.1200 | 53.12 | 0.00 | % | Coincide |
| V2-AC | 7.2 | Activos corrientes (% de activos) | 2024 | 52.3192 | 52.32 | -0.00 | % | Coincide |
| V2-AC | 7.2 | Activos corrientes (% de activos) | 2025 | 31.6739 | 31.67 | 0.00 | % | Coincide |
| V2-INV | 7.2 | Inventarios (% de activos) | 2021 | 26.7965 | 26.80 | -0.00 | % | Coincide |
| V2-INV | 7.2 | Inventarios (% de activos) | 2022 | 20.9917 | 20.99 | 0.00 | % | Coincide |
| V2-INV | 7.2 | Inventarios (% de activos) | 2023 | 17.4875 | 17.49 | -0.00 | % | Coincide |
| V2-INV | 7.2 | Inventarios (% de activos) | 2024 | 14.1156 | 14.12 | -0.00 | % | Coincide |
| V2-INV | 7.2 | Inventarios (% de activos) | 2025 | 8.9276 | 8.93 | -0.00 | % | Coincide |
| V2-ANC | 7.2 | Activos no corrientes (% de activos) | 2021 | 30.7017 | 30.70 | 0.00 | % | Coincide |
| V2-ANC | 7.2 | Activos no corrientes (% de activos) | 2022 | 33.2358 | 33.24 | -0.00 | % | Coincide |
| V2-ANC | 7.2 | Activos no corrientes (% de activos) | 2023 | 46.8800 | 46.88 | -0.00 | % | Coincide |
| V2-ANC | 7.2 | Activos no corrientes (% de activos) | 2024 | 47.6808 | 47.68 | 0.00 | % | Coincide |
| V2-ANC | 7.2 | Activos no corrientes (% de activos) | 2025 | 68.3261 | 68.33 | -0.00 | % | Coincide |
| V2-TA | 7.2 | Total activos (% de activos) | 2021 | 100.0000 | 100.00 | 0.00 | % | Coincide |
| V2-TA | 7.2 | Total activos (% de activos) | 2022 | 100.0000 | 100.00 | 0.00 | % | Coincide |
| V2-TA | 7.2 | Total activos (% de activos) | 2023 | 100.0000 | 100.00 | 0.00 | % | Coincide |
| V2-TA | 7.2 | Total activos (% de activos) | 2024 | 100.0000 | 100.00 | 0.00 | % | Coincide |
| V2-TA | 7.2 | Total activos (% de activos) | 2025 | 100.0000 | 100.00 | 0.00 | % | Coincide |
| V2-PC | 7.2 | Pasivos corrientes (% de activos) | 2021 | 37.1823 | 37.18 | 0.00 | % | Coincide |
| V2-PC | 7.2 | Pasivos corrientes (% de activos) | 2022 | 34.5142 | 34.51 | 0.00 | % | Coincide |
| V2-PC | 7.2 | Pasivos corrientes (% de activos) | 2023 | 41.1717 | 41.17 | 0.00 | % | Coincide |
| V2-PC | 7.2 | Pasivos corrientes (% de activos) | 2024 | 43.8801 | 43.88 | 0.00 | % | Coincide |
| V2-PC | 7.2 | Pasivos corrientes (% de activos) | 2025 | 47.4745 | 47.47 | 0.00 | % | Coincide |
| V2-PNC | 7.2 | Pasivos no corrientes (% de activos) | 2021 | 36.5843 | 36.58 | 0.00 | % | Coincide |
| V2-PNC | 7.2 | Pasivos no corrientes (% de activos) | 2022 | 33.6601 | 33.66 | 0.00 | % | Coincide |
| V2-PNC | 7.2 | Pasivos no corrientes (% de activos) | 2023 | 30.6892 | 30.69 | -0.00 | % | Coincide |
| V2-PNC | 7.2 | Pasivos no corrientes (% de activos) | 2024 | 28.7905 | 28.79 | 0.00 | % | Coincide |
| V2-PNC | 7.2 | Pasivos no corrientes (% de activos) | 2025 | 22.9673 | 22.97 | -0.00 | % | Coincide |
| V2-TP | 7.2 | Total pasivos (% de activos) | 2021 | 73.7666 | 73.77 | -0.00 | % | Coincide |
| V2-TP | 7.2 | Total pasivos (% de activos) | 2022 | 68.1743 | 68.17 | 0.00 | % | Coincide |
| V2-TP | 7.2 | Total pasivos (% de activos) | 2023 | 71.8609 | 71.86 | 0.00 | % | Coincide |
| V2-TP | 7.2 | Total pasivos (% de activos) | 2024 | 72.6707 | 72.67 | 0.00 | % | Coincide |
| V2-TP | 7.2 | Total pasivos (% de activos) | 2025 | 70.4417 | 70.44 | 0.00 | % | Coincide |
| V2-PAT | 7.2 | Patrimonio (% de activos) | 2021 | 26.2334 | 26.23 | 0.00 | % | Coincide |
| V2-PAT | 7.2 | Patrimonio (% de activos) | 2022 | 31.8257 | 31.83 | -0.00 | % | Coincide |
| V2-PAT | 7.2 | Patrimonio (% de activos) | 2023 | 28.1391 | 28.14 | -0.00 | % | Coincide |
| V2-PAT | 7.2 | Patrimonio (% de activos) | 2024 | 27.3293 | 27.33 | -0.00 | % | Coincide |
| V2-PAT | 7.2 | Patrimonio (% de activos) | 2025 | 29.5583 | 29.56 | -0.00 | % | Coincide |
| L-RC | 8.1 | Razón circulante | 2021 | 1.8637 | 1.86 | 0.00 | veces | Coincide |
| L-RC | 8.1 | Razón circulante | 2022 | 1.9344 | 1.93 | 0.00 | veces | Coincide |
| L-RC | 8.1 | Razón circulante | 2023 | 1.2902 | 1.29 | 0.00 | veces | Coincide |
| L-RC | 8.1 | Razón circulante | 2024 | 1.1923 | 1.19 | 0.00 | veces | Coincide |
| L-RC | 8.1 | Razón circulante | 2025 | 0.6672 | 0.67 | -0.00 | veces | Coincide |
| L-PA | 8.1 | Prueba ácida | 2021 | 1.1431 | 1.14 | 0.00 | veces | Coincide |
| L-PA | 8.1 | Prueba ácida | 2022 | 1.3262 | 1.33 | -0.00 | veces | Coincide |
| L-PA | 8.1 | Prueba ácida | 2023 | 0.8655 | 0.87 | -0.00 | veces | Coincide |
| L-PA | 8.1 | Prueba ácida | 2024 | 0.8706 | 0.87 | 0.00 | veces | Coincide |
| L-PA | 8.1 | Prueba ácida | 2025 | 0.4791 | 0.48 | -0.00 | veces | Coincide |
| L-CT | 8.1 | Capital de trabajo | 2021 | 177,908,317 | 177,908,317 | 0 | USD | Coincide |
| L-CT | 8.1 | Capital de trabajo | 2022 | 216,728,221 | 216,728,221 | 0 | USD | Coincide |
| L-CT | 8.1 | Capital de trabajo | 2023 | 96,673,859 | 96,673,859 | 0 | USD | Coincide |
| L-CT | 8.1 | Capital de trabajo | 2024 | 69,805,463 | 69,805,463 | 0 | USD | Coincide |
| L-CT | 8.1 | Capital de trabajo | 2025 | -123,568,026 | -123,568,026 | 0 | USD | Coincide |
| A-RI | 8.2 A | Rotación de inventarios | 2021 | 2.4741 | 2.47 | 0.00 | veces | Coincide |
| A-RI | 8.2 A | Rotación de inventarios | 2022 | 2.9087 | 2.91 | -0.00 | veces | Coincide |
| A-RI | 8.2 A | Rotación de inventarios | 2023 | 2.6401 | 2.64 | 0.00 | veces | Coincide |
| A-RI | 8.2 A | Rotación de inventarios | 2024 | 3.2327 | 3.23 | 0.00 | veces | Coincide |
| A-RI | 8.2 A | Rotación de inventarios | 2025 | 4.7471 | 4.75 | -0.00 | veces | Coincide |
| A-PPI | 8.2 A | PPI | 2021 | 147.530 | 147.5 | 0.0 | días | Coincide |
| A-PPI | 8.2 A | PPI | 2022 | 125.485 | 125.5 | -0.0 | días | Coincide |
| A-PPI | 8.2 A | PPI | 2023 | 138.254 | 138.3 | -0.0 | días | Coincide |
| A-PPI | 8.2 A | PPI | 2024 | 112.907 | 112.9 | 0.0 | días | Coincide |
| A-PPI | 8.2 A | PPI | 2025 | 76.890 | 76.9 | -0.0 | días | Coincide |
| B-CXC | 8.2 B | Cuentas por cobrar usadas | 2021 | 53,081,088 | 53,081,088 | 0 | USD | Coincide |
| B-CXC | 8.2 B | Cuentas por cobrar usadas | 2022 | 32,581,092 | 32,581,092 | 0 | USD | Coincide |
| B-CXC | 8.2 B | Cuentas por cobrar usadas | 2023 | 41,272,525 | 96,097,483 | -54,824,958 | USD | Diferencia |
| B-CXC | 8.2 B | Cuentas por cobrar usadas | 2024 | 97,204,415 | 97,204,415 | 0 | USD | Coincide |
| B-CXC | 8.2 B | Cuentas por cobrar usadas | 2025 | 70,169,882 | 70,169,882 | 0 | USD | Coincide |
| B-RCC | 8.2 B | Rotación de CxC | 2021 | 9.8710 | 9.87 | 0.00 | veces | Coincide |
| B-RCC | 8.2 B | Rotación de CxC | 2022 | 15.3357 | 15.34 | -0.00 | veces | Coincide |
| B-RCC | 8.2 B | Rotación de CxC | 2023 | 11.5967 | 4.98 | 6.62 | veces | Diferencia |
| B-RCC | 8.2 B | Rotación de CxC | 2024 | 4.9278 | 4.93 | -0.00 | veces | Coincide |
| B-RCC | 8.2 B | Rotación de CxC | 2025 | 6.2663 | 6.27 | -0.00 | veces | Coincide |
| B-PPC | 8.2 B | PPC | 2021 | 36.977 | 37.0 | -0.0 | días | Coincide |
| B-PPC | 8.2 B | PPC | 2022 | 23.801 | 23.8 | 0.0 | días | Coincide |
| B-PPC | 8.2 B | PPC | 2023 | 31.475 | 73.3 | -41.8 | días | Diferencia |
| B-PPC | 8.2 B | PPC | 2024 | 74.069 | 74.1 | -0.0 | días | Coincide |
| B-PPC | 8.2 B | PPC | 2025 | 58.248 | 58.3 | -0.1 | días | Coincidencia por redondeo |
| C-CO82 | 8.2 C | Ciclo operativo (PPI + PPC) | 2024 | 186.976 | 187.0 | -0.0 | días | Coincide |
| C-CO82 | 8.2 C | Ciclo operativo (PPI + PPC) | 2025 | 135.138 | 135.2 | -0.1 | días | Coincidencia por redondeo |
| D-RA | 8.2 D | Rotación de activos | 2021 | 0.9459 | 0.95 | -0.00 | veces | Coincide |
| D-RA | 8.2 D | Rotación de activos | 2022 | 0.7435 | 0.74 | 0.00 | veces | Coincide |
| D-RA | 8.2 D | Rotación de activos | 2023 | 0.5915 | 0.59 | 0.00 | veces | Coincide |
| D-RA | 8.2 D | Rotación de activos | 2024 | 0.5791 | 0.58 | -0.00 | veces | Coincide |
| D-RA | 8.2 D | Rotación de activos | 2025 | 0.5622 | 0.56 | 0.00 | veces | Coincide |
| E-END | 8.3 A | Índice de endeudamiento | 2021 | 73.7666 | 73.77 | -0.00 | % | Coincide |
| E-END | 8.3 A | Índice de endeudamiento | 2022 | 68.1743 | 68.17 | 0.00 | % | Coincide |
| E-END | 8.3 A | Índice de endeudamiento | 2023 | 71.8609 | 71.86 | 0.00 | % | Coincide |
| E-END | 8.3 A | Índice de endeudamiento | 2024 | 72.6707 | 72.67 | 0.00 | % | Coincide |
| E-END | 8.3 A | Índice de endeudamiento | 2025 | 70.4417 | 70.44 | 0.00 | % | Coincide |
| E-PCP | 8.3 A | Pasivo corriente / pasivo total | 2021 | 50.4053 | 50.40 | 0.01 | % | Coincidencia por redondeo |
| E-PCP | 8.3 A | Pasivo corriente / pasivo total | 2025 | 67.3954 | 67.40 | -0.00 | % | Coincide |
| E-UO | 8.3 B | Utilidad de operación | 2021 | 103,578,903 | 103,578,903 | 0 | USD | Coincide |
| E-UO | 8.3 B | Utilidad de operación | 2022 | 31,200,977 | 31,200,977 | 0 | USD | Coincide |
| E-UO | 8.3 B | Utilidad de operación | 2023 | 44,689,021 | 44,689,021 | 0 | USD | Coincide |
| E-UO | 8.3 B | Utilidad de operación | 2024 | 35,193,918 | 35,193,918 | 0 | USD | Coincide |
| E-UO | 8.3 B | Utilidad de operación | 2025 | 54,665,644 | 54,665,644 | 0 | USD | Coincide |
| E-GF | 8.3 B | Gastos financieros | 2021 | 21,777,725 | 21,777,725 | 0 | USD | Coincide |
| E-GF | 8.3 B | Gastos financieros | 2022 | 17,181,342 | 17,181,342 | 0 | USD | Coincide |
| E-GF | 8.3 B | Gastos financieros | 2023 | 22,016,927 | 22,016,927 | 0 | USD | Coincide |
| E-GF | 8.3 B | Gastos financieros | 2024 | 28,064,310 | 28,064,310 | 0 | USD | Coincide |
| E-GF | 8.3 B | Gastos financieros | 2025 | 37,399,011 | 37,399,011 | 0 | USD | Coincide |
| E-COB | 8.3 B | Cobertura (veces) | 2021 | 4.7562 | 4.76 | -0.00 | veces | Coincide |
| E-COB | 8.3 B | Cobertura (veces) | 2022 | 1.8160 | 1.82 | -0.00 | veces | Coincide |
| E-COB | 8.3 B | Cobertura (veces) | 2023 | 2.0298 | 2.03 | -0.00 | veces | Coincide |
| E-COB | 8.3 B | Cobertura (veces) | 2024 | 1.2540 | 1.25 | 0.00 | veces | Coincide |
| E-COB | 8.3 B | Cobertura (veces) | 2025 | 1.4617 | 1.46 | 0.00 | veces | Coincide |
| E-DC | 8.3 D | Razón deuda-capital | 2021 | 2.8119 | 2.81 | 0.00 | veces | Coincide |
| E-DC | 8.3 D | Razón deuda-capital | 2022 | 2.1421 | 2.14 | 0.00 | veces | Coincide |
| E-DC | 8.3 D | Razón deuda-capital | 2023 | 2.5538 | 2.55 | 0.00 | veces | Coincide |
| E-DC | 8.3 D | Razón deuda-capital | 2024 | 2.6591 | 2.66 | -0.00 | veces | Coincide |
| E-DC | 8.3 D | Razón deuda-capital | 2025 | 2.3831 | 2.38 | 0.00 | veces | Coincide |
| R-MB | 8.4 A | Margen de utilidad bruta | 2021 | 29.9090 | 29.91 | -0.00 | % | Coincide |
| R-MB | 8.4 A | Margen de utilidad bruta | 2022 | 17.8769 | 17.88 | -0.00 | % | Coincide |
| R-MB | 8.4 A | Margen de utilidad bruta | 2023 | 21.9541 | 21.95 | 0.00 | % | Coincide |
| R-MB | 8.4 A | Margen de utilidad bruta | 2024 | 21.1996 | 21.20 | -0.00 | % | Coincide |
| R-MB | 8.4 A | Margen de utilidad bruta | 2025 | 24.6244 | 24.62 | 0.00 | % | Coincide |
| R-MO | 8.4 B | Margen de utilidad operativa | 2021 | 19.7683 | 19.77 | -0.00 | % | Coincide |
| R-MO | 8.4 B | Margen de utilidad operativa | 2022 | 6.2445 | 6.24 | 0.00 | % | Coincide |
| R-MO | 8.4 B | Margen de utilidad operativa | 2023 | 9.3370 | 9.34 | -0.00 | % | Coincide |
| R-MO | 8.4 B | Margen de utilidad operativa | 2024 | 7.3473 | 7.35 | -0.00 | % | Coincide |
| R-MO | 8.4 B | Margen de utilidad operativa | 2025 | 12.4324 | 12.43 | 0.00 | % | Coincide |
| R-MN | 8.4 C | Margen de utilidad neta | 2021 | 13.0930 | 13.09 | 0.00 | % | Coincide |
| R-MN | 8.4 C | Margen de utilidad neta | 2022 | 2.0133 | 2.01 | 0.00 | % | Coincide |
| R-MN | 8.4 C | Margen de utilidad neta | 2023 | 2.7852 | 2.79 | -0.00 | % | Coincide |
| R-MN | 8.4 C | Margen de utilidad neta | 2024 | 0.6390 | 0.64 | -0.00 | % | Coincide |
| R-MN | 8.4 C | Margen de utilidad neta | 2025 | 2.7061 | 2.71 | -0.00 | % | Coincide |
| R-GF25 | 8.4 C | Gastos financieros 2025 | 2025 | 51,914,906 | 51,914,906 | 0 | USD | Coincide |
| R-EPS | 8.4 D | Ganancia por acción | 2021 | No calculable | No calculable |  | USD | No aplica |
| R-EPS | 8.4 D | Ganancia por acción | 2022 | No calculable | No calculable |  | USD | No aplica |
| R-EPS | 8.4 D | Ganancia por acción | 2023 | No calculable | No calculable |  | USD | No aplica |
| R-EPS | 8.4 D | Ganancia por acción | 2024 | No calculable | No calculable |  | USD | No aplica |
| R-EPS | 8.4 D | Ganancia por acción | 2025 | No calculable | No calculable |  | USD | No aplica |
| R-ROA | 8.4 E | ROA | 2021 | 12.3842 | 12.38 | 0.00 | % | Coincide |
| R-ROA | 8.4 E | ROA | 2022 | 1.4969 | 1.50 | -0.00 | % | Coincide |
| R-ROA | 8.4 E | ROA | 2023 | 1.6476 | 1.65 | -0.00 | % | Coincide |
| R-ROA | 8.4 E | ROA | 2024 | 0.3701 | 0.37 | 0.00 | % | Coincide |
| R-ROA | 8.4 E | ROA | 2025 | 1.5215 | 1.52 | 0.00 | % | Coincide |
| R-ROE | 8.4 F | ROE | 2021 | 47.2077 | 47.21 | -0.00 | % | Coincide |
| R-ROE | 8.4 F | ROE | 2022 | 4.7033 | 4.70 | 0.00 | % | Coincide |
| R-ROE | 8.4 F | ROE | 2023 | 5.8552 | 5.86 | -0.00 | % | Coincide |
| R-ROE | 8.4 F | ROE | 2024 | 1.3540 | 1.35 | 0.00 | % | Coincide |
| R-ROE | 8.4 F | ROE | 2025 | 5.1475 | 5.15 | -0.00 | % | Coincide |
| M-PE | 8.5 A | Relación precio/ganancias | 2021 | No calculable | No calculable |  | veces | No aplica |
| M-PE | 8.5 A | Relación precio/ganancias | 2022 | No calculable | No calculable |  | veces | No aplica |
| M-PE | 8.5 A | Relación precio/ganancias | 2023 | No calculable | No calculable |  | veces | No aplica |
| M-PE | 8.5 A | Relación precio/ganancias | 2024 | No calculable | No calculable |  | veces | No aplica |
| M-PE | 8.5 A | Relación precio/ganancias | 2025 | No calculable | No calculable |  | veces | No aplica |
| M-ML | 8.5 B | Razón mercado/libro | 2021 | No calculable | No calculable |  | veces | No aplica |
| M-ML | 8.5 B | Razón mercado/libro | 2022 | No calculable | No calculable |  | veces | No aplica |
| M-ML | 8.5 B | Razón mercado/libro | 2023 | No calculable | No calculable |  | veces | No aplica |
| M-ML | 8.5 B | Razón mercado/libro | 2024 | No calculable | No calculable |  | veces | No aplica |
| M-ML | 8.5 B | Razón mercado/libro | 2025 | No calculable | No calculable |  | veces | No aplica |
| T-TES | 9.1 | Tesorería activa | 2021 | 38,740,865 | 38,740,865 | 0 | USD | Coincide |
| T-TES | 9.1 | Tesorería activa | 2022 | 27,155,298 | 27,155,298 | 0 | USD | Coincide |
| T-TES | 9.1 | Tesorería activa | 2023 | 19,530,206 | 19,530,206 | 0 | USD | Coincide |
| T-TES | 9.1 | Tesorería activa | 2024 | 29,717,333 | 29,717,333 | 0 | USD | Coincide |
| T-TES | 9.1 | Tesorería activa | 2025 | 26,342,741 | 26,342,741 | 0 | USD | Coincide |
| T-PC | 9.1 | Pasivo corriente | 2021 | 205,973,230 | 205,973,230 | 0 | USD | Coincide |
| T-PC | 9.1 | Pasivo corriente | 2022 | 231,944,180 | 231,944,180 | 0 | USD | Coincide |
| T-PC | 9.1 | Pasivo corriente | 2023 | 333,120,685 | 333,120,685 | 0 | USD | Coincide |
| T-PC | 9.1 | Pasivo corriente | 2024 | 362,966,215 | 362,966,215 | 0 | USD | Coincide |
| T-PC | 9.1 | Pasivo corriente | 2025 | 371,274,007 | 371,274,007 | 0 | USD | Coincide |
| T-RT | 9.1 | Razón de tesorería | 2021 | 18.8087 | 18.81 | -0.00 | % | Coincide |
| T-RT | 9.1 | Razón de tesorería | 2022 | 11.7077 | 11.71 | -0.00 | % | Coincide |
| T-RT | 9.1 | Razón de tesorería | 2023 | 5.8628 | 5.86 | 0.00 | % | Coincide |
| T-RT | 9.1 | Razón de tesorería | 2024 | 8.1874 | 8.19 | -0.00 | % | Coincide |
| T-RT | 9.1 | Razón de tesorería | 2025 | 7.0952 | 7.10 | -0.00 | % | Coincide |
| F-AC | 9.2.1 | Activo corriente | 2021 | 383,881,547 | 383,881,547 | 0 | USD | Coincide |
| F-AC | 9.2.1 | Activo corriente | 2022 | 448,672,401 | 448,672,401 | 0 | USD | Coincide |
| F-AC | 9.2.1 | Activo corriente | 2023 | 429,794,544 | 429,794,544 | 0 | USD | Coincide |
| F-AC | 9.2.1 | Activo corriente | 2024 | 432,771,678 | 432,771,678 | 0 | USD | Coincide |
| F-AC | 9.2.1 | Activo corriente | 2025 | 247,705,981 | 247,705,981 | 0 | USD | Coincide |
| F-FM | 9.2.1 | Fondo de maniobra | 2021 | 177,908,317 | 177,908,317 | 0 | USD | Coincide |
| F-FM | 9.2.1 | Fondo de maniobra | 2022 | 216,728,221 | 216,728,221 | 0 | USD | Coincide |
| F-FM | 9.2.1 | Fondo de maniobra | 2023 | 96,673,859 | 96,673,859 | 0 | USD | Coincide |
| F-FM | 9.2.1 | Fondo de maniobra | 2024 | 69,805,463 | 69,805,463 | 0 | USD | Coincide |
| F-FM | 9.2.1 | Fondo de maniobra | 2025 | -123,568,026 | -123,568,026 | 0 | USD | Coincide |
| F-PNC | 9.2.2 | Pasivo no corriente 2021 | 2021 | 202,660,765 | 202,660,765 | 0 | USD | Coincide |
| F-CP | 9.2.2 | Capitales permanentes | 2021 | 347,981,955 | 347,981,955 | 0 | USD | Coincide |
| F-CP | 9.2.2 | Capitales permanentes | 2022 | 440,080,913 | 440,080,913 | 0 | USD | Coincide |
| F-CP | 9.2.2 | Capitales permanentes | 2023 | 475,980,261 | 475,980,261 | 0 | USD | Coincide |
| F-CP | 9.2.2 | Capitales permanentes | 2024 | 464,210,159 | 464,210,159 | 0 | USD | Coincide |
| F-CP | 9.2.2 | Capitales permanentes | 2025 | 410,775,554 | 410,775,554 | 0 | USD | Coincide |
| F-ANC | 9.2.2 | Activo no corriente | 2021 | 170,073,638 | 170,073,638 | 0 | USD | Coincide |
| F-ANC | 9.2.2 | Activo no corriente | 2022 | 223,352,692 | 223,352,692 | 0 | USD | Coincide |
| F-ANC | 9.2.2 | Activo no corriente | 2023 | 379,306,402 | 379,306,402 | 0 | USD | Coincide |
| F-ANC | 9.2.2 | Activo no corriente | 2024 | 394,404,696 | 394,404,696 | 0 | USD | Coincide |
| F-ANC | 9.2.2 | Activo no corriente | 2025 | 534,343,580 | 534,343,580 | 0 | USD | Coincide |
| F-FMLP | 9.2.2 | Fondo de maniobra a largo plazo | 2021 | 177,908,317 | 177,908,317 | 0 | USD | Coincide |
| F-FMLP | 9.2.2 | Fondo de maniobra a largo plazo | 2022 | 216,728,221 | 216,728,221 | 0 | USD | Coincide |
| F-FMLP | 9.2.2 | Fondo de maniobra a largo plazo | 2023 | 96,673,859 | 96,673,859 | 0 | USD | Coincide |
| F-FMLP | 9.2.2 | Fondo de maniobra a largo plazo | 2024 | 69,805,463 | 69,805,463 | 0 | USD | Coincide |
| F-FMLP | 9.2.2 | Fondo de maniobra a largo plazo | 2025 | -123,568,026 | -123,568,026 | 0 | USD | Coincide |
| C-EPI | 9.3 | Edad promedio del inventario | 2021 | 147.5300 | 147.53 | 0.00 | días | Coincide |
| C-EPI | 9.3 | Edad promedio del inventario | 2022 | 125.4849 | 125.48 | 0.00 | días | Coincide |
| C-EPI | 9.3 | Edad promedio del inventario | 2023 | 138.2544 | 138.25 | 0.00 | días | Coincide |
| C-EPI | 9.3 | Edad promedio del inventario | 2024 | 112.9072 | 112.91 | -0.00 | días | Coincide |
| C-EPI | 9.3 | Edad promedio del inventario | 2025 | 76.8898 | 76.89 | -0.00 | días | Coincide |
| C-PPC | 9.3 | Período promedio de cobro | 2021 | 36.9769 | 36.98 | -0.00 | días | Coincide |
| C-PPC | 9.3 | Período promedio de cobro | 2022 | 23.8007 | 23.80 | 0.00 | días | Coincide |
| C-PPC | 9.3 | Período promedio de cobro | 2023 | 31.4746 | 31.47 | 0.00 | días | Coincide |
| C-PPC | 9.3 | Período promedio de cobro | 2024 | 74.0691 | 74.07 | -0.00 | días | Coincide |
| C-PPC | 9.3 | Período promedio de cobro | 2025 | 58.2482 | 58.25 | -0.00 | días | Coincide |
| C-CXP | 9.3 | Cuentas por pagar comerciales | 2021 | 156,609,253 | 156,609,253 | 0 | USD | Coincide |
| C-CXP | 9.3 | Cuentas por pagar comerciales | 2022 | 96,629,671 | 96,629,671 | 0 | USD | Coincide |
| C-CXP | 9.3 | Cuentas por pagar comerciales | 2023 | 195,599,671 | 195,599,671 | 0 | USD | Coincide |
| C-CXP | 9.3 | Cuentas por pagar comerciales | 2024 | 225,126,517 | 225,126,517 | 0 | USD | Coincide |
| C-CXP | 9.3 | Cuentas por pagar comerciales | 2025 | 173,120,913 | 173,120,913 | 0 | USD | Coincide |
| C-PPP | 9.3 | Período promedio de pago | 2021 | 155.6487 | 155.65 | -0.00 | días | Coincide |
| C-PPP | 9.3 | Período promedio de pago | 2022 | 85.9546 | 85.95 | 0.00 | días | Coincide |
| C-PPP | 9.3 | Período promedio de pago | 2023 | 191.1249 | 191.12 | 0.00 | días | Coincide |
| C-PPP | 9.3 | Período promedio de pago | 2024 | 217.6954 | 217.70 | -0.00 | días | Coincide |
| C-PPP | 9.3 | Período promedio de pago | 2025 | 190.6559 | 190.66 | -0.00 | días | Coincide |
| C-CO | 9.3 | Ciclo operativo | 2021 | 184.5069 | 184.51 | -0.00 | días | Coincide |
| C-CO | 9.3 | Ciclo operativo | 2022 | 149.2855 | 149.28 | 0.01 | días | Coincidencia por redondeo |
| C-CO | 9.3 | Ciclo operativo | 2023 | 169.7290 | 169.72 | 0.01 | días | Coincidencia por redondeo |
| C-CO | 9.3 | Ciclo operativo | 2024 | 186.9763 | 186.98 | -0.00 | días | Coincide |
| C-CO | 9.3 | Ciclo operativo | 2025 | 135.1380 | 135.14 | -0.00 | días | Coincide |
| C-CCE | 9.3 | Ciclo de conversión de efectivo | 2021 | 28.8582 | 28.86 | -0.00 | días | Coincide |
| C-CCE | 9.3 | Ciclo de conversión de efectivo | 2022 | 63.3310 | 63.33 | 0.00 | días | Coincide |
| C-CCE | 9.3 | Ciclo de conversión de efectivo | 2023 | -21.3959 | -21.40 | 0.00 | días | Coincide |
| C-CCE | 9.3 | Ciclo de conversión de efectivo | 2024 | -30.7191 | -30.72 | 0.00 | días | Coincide |
| C-CCE | 9.3 | Ciclo de conversión de efectivo | 2025 | -55.5180 | -55.52 | 0.00 | días | Coincide |
| W-POP | 9.4 | Pasivos operativos sin costo (% del total) | 2021 | 31.7249 | 31.72 | 0.00 | % | Coincide |
| W-POP | 9.4 | Pasivos operativos sin costo (% del total) | 2022 | 23.8931 | 23.89 | 0.00 | % | Coincide |
| W-POP | 9.4 | Pasivos operativos sin costo (% del total) | 2023 | 29.1468 | 29.15 | -0.00 | % | Coincide |
| W-POP | 9.4 | Pasivos operativos sin costo (% del total) | 2024 | 30.0559 | 30.06 | -0.00 | % | Coincide |
| W-POP | 9.4 | Pasivos operativos sin costo (% del total) | 2025 | 25.4156 | 25.42 | -0.00 | % | Coincide |
| W-PDF | 9.4 | Deuda financiera con costo (% del total) | 2021 | 42.0417 | 42.04 | 0.00 | % | Coincide |
| W-PDF | 9.4 | Deuda financiera con costo (% del total) | 2022 | 44.2812 | 44.28 | 0.00 | % | Coincide |
| W-PDF | 9.4 | Deuda financiera con costo (% del total) | 2023 | 42.7141 | 42.71 | 0.00 | % | Coincide |
| W-PDF | 9.4 | Deuda financiera con costo (% del total) | 2024 | 42.6147 | 42.61 | 0.00 | % | Coincide |
| W-PDF | 9.4 | Deuda financiera con costo (% del total) | 2025 | 45.0261 | 45.03 | -0.00 | % | Coincide |
| W-PPAT | 9.4 | Patrimonio (% del total) | 2021 | 26.2334 | 26.23 | 0.00 | % | Coincide |
| W-PPAT | 9.4 | Patrimonio (% del total) | 2022 | 31.8257 | 31.83 | -0.00 | % | Coincide |
| W-PPAT | 9.4 | Patrimonio (% del total) | 2023 | 28.1391 | 28.14 | -0.00 | % | Coincide |
| W-PPAT | 9.4 | Patrimonio (% del total) | 2024 | 27.3293 | 27.33 | -0.00 | % | Coincide |
| W-PPAT | 9.4 | Patrimonio (% del total) | 2025 | 29.5583 | 29.56 | -0.00 | % | Coincide |
| W-KE | 9.4 | Costo del patrimonio (Ke = ROE) | 2021 | 47.2077 | 47.21 | -0.00 | % | Coincide |
| W-KE | 9.4 | Costo del patrimonio (Ke = ROE) | 2022 | 4.7033 | 4.70 | 0.00 | % | Coincide |
| W-KE | 9.4 | Costo del patrimonio (Ke = ROE) | 2023 | 5.8552 | 5.86 | -0.00 | % | Coincide |
| W-KE | 9.4 | Costo del patrimonio (Ke = ROE) | 2024 | 1.3540 | 1.35 | 0.00 | % | Coincide |
| W-KE | 9.4 | Costo del patrimonio (Ke = ROE) | 2025 | 5.1475 | 5.15 | -0.00 | % | Coincide |
| W-ISR | 9.4 | Tasa de ISR (supuesto) | 2021 | 30.0000 | 30.00 | 0.00 | % | Coincide |
| W-ISR | 9.4 | Tasa de ISR (supuesto) | 2022 | 30.0000 | 30.00 | 0.00 | % | Coincide |
| W-ISR | 9.4 | Tasa de ISR (supuesto) | 2023 | 30.0000 | 30.00 | 0.00 | % | Coincide |
| W-ISR | 9.4 | Tasa de ISR (supuesto) | 2024 | 30.0000 | 30.00 | 0.00 | % | Coincide |
| W-ISR | 9.4 | Tasa de ISR (supuesto) | 2025 | 30.0000 | 30.00 | 0.00 | % | Coincide |
| W-KD | 9.4 | Costo neto promedio de la deuda financiera | 2021 | 5.2377 | 5.24 | -0.00 | % | Coincide |
| W-KD | 9.4 | Costo neto promedio de la deuda financiera | 2022 | 5.2616 | 5.26 | 0.00 | % | Coincide |
| W-KD | 9.4 | Costo neto promedio de la deuda financiera | 2023 | 5.2136 | 5.21 | 0.00 | % | Coincide |
| W-KD | 9.4 | Costo neto promedio de la deuda financiera | 2024 | 5.1871 | 5.19 | -0.00 | % | Coincide |
| W-KD | 9.4 | Costo neto promedio de la deuda financiera | 2025 | 5.1718 | 5.17 | 0.00 | % | Coincide |
| W-AD | 9.4 | Aporte de la deuda al WACC | 2021 | 2.2020 | 2.20 | 0.00 | % | Coincide |
| W-AD | 9.4 | Aporte de la deuda al WACC | 2022 | 2.3299 | 2.33 | -0.00 | % | Coincide |
| W-AD | 9.4 | Aporte de la deuda al WACC | 2023 | 2.2269 | 2.23 | -0.00 | % | Coincide |
| W-AD | 9.4 | Aporte de la deuda al WACC | 2024 | 2.2104 | 2.21 | 0.00 | % | Coincide |
| W-AD | 9.4 | Aporte de la deuda al WACC | 2025 | 2.3286 | 2.33 | -0.00 | % | Coincide |
| W-AP | 9.4 | Aporte del patrimonio al WACC | 2021 | 12.3842 | 12.38 | 0.00 | % | Coincide |
| W-AP | 9.4 | Aporte del patrimonio al WACC | 2022 | 1.4969 | 1.50 | -0.00 | % | Coincide |
| W-AP | 9.4 | Aporte del patrimonio al WACC | 2023 | 1.6476 | 1.65 | -0.00 | % | Coincide |
| W-AP | 9.4 | Aporte del patrimonio al WACC | 2024 | 0.3701 | 0.37 | 0.00 | % | Coincide |
| W-AP | 9.4 | Aporte del patrimonio al WACC | 2025 | 1.5215 | 1.52 | 0.00 | % | Coincide |
| W-WACC | 9.4 | WACC | 2021 | 14.5862 | 14.59 | -0.00 | % | Coincide |
| W-WACC | 9.4 | WACC | 2022 | 3.8268 | 3.83 | -0.00 | % | Coincide |
| W-WACC | 9.4 | WACC | 2023 | 3.8745 | 3.88 | -0.01 | % | Coincidencia por redondeo |
| W-WACC | 9.4 | WACC | 2024 | 2.5805 | 2.58 | 0.00 | % | Coincide |
| W-WACC | 9.4 | WACC | 2025 | 3.8502 | 3.85 | 0.00 | % | Coincide |
| W-WACC-TXT | 9.4.3 | WACC 2023 según el texto | 2023 | 3.8745 | 3.87 | 0.00 | % | Coincide |
| W-ROA | 9.4 | ROA (utilidad neta / financiamiento total) | 2021 | 12.3842 | 12.38 | 0.00 | % | Coincide |
| W-ROA | 9.4 | ROA (utilidad neta / financiamiento total) | 2022 | 1.4969 | 1.50 | -0.00 | % | Coincide |
| W-ROA | 9.4 | ROA (utilidad neta / financiamiento total) | 2023 | 1.6476 | 1.65 | -0.00 | % | Coincide |
| W-ROA | 9.4 | ROA (utilidad neta / financiamiento total) | 2024 | 0.3701 | 0.37 | 0.00 | % | Coincide |
| W-ROA | 9.4 | ROA (utilidad neta / financiamiento total) | 2025 | 1.5215 | 1.52 | 0.00 | % | Coincide |
| W-SPREAD | 9.4 | Spread (ROA − costo neto de la deuda) | 2021 | 7.1465 | 7.15 | -0.00 | % | Coincide |
| W-SPREAD | 9.4 | Spread (ROA − costo neto de la deuda) | 2022 | -3.7648 | -3.76 | -0.00 | % | Coincide |
| W-SPREAD | 9.4 | Spread (ROA − costo neto de la deuda) | 2023 | -3.5660 | -3.57 | 0.00 | % | Coincide |
| W-SPREAD | 9.4 | Spread (ROA − costo neto de la deuda) | 2024 | -4.8170 | -4.82 | 0.00 | % | Coincide |
| W-SPREAD | 9.4 | Spread (ROA − costo neto de la deuda) | 2025 | -3.6502 | -3.65 | -0.00 | % | Coincide |
| D-MN | 9.5 | Margen de utilidad neta | 2021 | 13.0930 | 13.09 | 0.00 | % | Coincide |
| D-MN | 9.5 | Margen de utilidad neta | 2022 | 2.0133 | 2.01 | 0.00 | % | Coincide |
| D-MN | 9.5 | Margen de utilidad neta | 2023 | 2.7852 | 2.79 | -0.00 | % | Coincide |
| D-MN | 9.5 | Margen de utilidad neta | 2024 | 0.6390 | 0.64 | -0.00 | % | Coincide |
| D-MN | 9.5 | Margen de utilidad neta | 2025 | 2.7061 | 2.71 | -0.00 | % | Coincide |
| D-RA | 9.5 | Rotación de activos totales | 2021 | 0.9459 | 0.95 | -0.00 | veces | Coincide |
| D-RA | 9.5 | Rotación de activos totales | 2022 | 0.7435 | 0.74 | 0.00 | veces | Coincide |
| D-RA | 9.5 | Rotación de activos totales | 2023 | 0.5915 | 0.59 | 0.00 | veces | Coincide |
| D-RA | 9.5 | Rotación de activos totales | 2024 | 0.5791 | 0.58 | -0.00 | veces | Coincide |
| D-RA | 9.5 | Rotación de activos totales | 2025 | 0.5622 | 0.56 | 0.00 | veces | Coincide |
| D-RA4 | 9.5 | Rotación de activos totales 2021 (4 decimales) | 2021 | 0.945862 | 0.9459 | -0.0000 | veces | Coincide |
| D-RSA | 9.5 | RSA / ROA (fórmula DuPont) | 2021 | 12.3842 | 12.38 | 0.00 | % | Coincide |
| D-RSA | 9.5 | RSA / ROA (fórmula DuPont) | 2022 | 1.4969 | 1.50 | -0.00 | % | Coincide |
| D-RSA | 9.5 | RSA / ROA (fórmula DuPont) | 2023 | 1.6476 | 1.65 | -0.00 | % | Coincide |
| D-RSA | 9.5 | RSA / ROA (fórmula DuPont) | 2024 | 0.3701 | 0.37 | 0.00 | % | Coincide |
| D-RSA | 9.5 | RSA / ROA (fórmula DuPont) | 2025 | 1.5215 | 1.52 | 0.00 | % | Coincide |
| D-MAF | 9.6 | Multiplicador de capital (MAF) | 2021 | 3.8119 | 3.81 | 0.00 | veces | Coincide |
| D-MAF | 9.6 | Multiplicador de capital (MAF) | 2022 | 3.1421 | 3.14 | 0.00 | veces | Coincide |
| D-MAF | 9.6 | Multiplicador de capital (MAF) | 2023 | 3.5538 | 3.55 | 0.00 | veces | Coincide |
| D-MAF | 9.6 | Multiplicador de capital (MAF) | 2024 | 3.6591 | 3.66 | -0.00 | veces | Coincide |
| D-MAF | 9.6 | Multiplicador de capital (MAF) | 2025 | 3.3831 | 3.38 | 0.00 | veces | Coincide |
| D-RSP | 9.6 | RSP / ROE (fórmula modificada) | 2021 | 47.2077 | 47.21 | -0.00 | % | Coincide |
| D-RSP | 9.6 | RSP / ROE (fórmula modificada) | 2022 | 4.7033 | 4.70 | 0.00 | % | Coincide |
| D-RSP | 9.6 | RSP / ROE (fórmula modificada) | 2023 | 5.8552 | 5.86 | -0.00 | % | Coincide |
| D-RSP | 9.6 | RSP / ROE (fórmula modificada) | 2024 | 1.3540 | 1.35 | 0.00 | % | Coincide |
| D-RSP | 9.6 | RSP / ROE (fórmula modificada) | 2025 | 5.1475 | 5.15 | -0.00 | % | Coincide |
| D-UC | 9.6 | Ganancia atribuible a la controladora | 2021 | 66,407,462 | 66,407,462 | 0 | USD | Coincide |
| D-UC | 9.6 | Ganancia atribuible a la controladora | 2022 | 8,559,346 | 8,559,346 | 0 | USD | Coincide |
| D-UC | 9.6 | Ganancia atribuible a la controladora | 2023 | 12,309,102 | 12,309,102 | 0 | USD | Coincide |
| D-UC | 9.6 | Ganancia atribuible a la controladora | 2024 | 3,060,981 | 3,060,981 | 0 | USD | Coincide |
| D-UC | 9.6 | Ganancia atribuible a la controladora | 2025 | 11,898,987 | 11,898,987 | 0 | USD | Coincide |
| D-PC | 9.6 | Patrimonio de la controladora | 2021 | 142,057,829 | 142,057,829 | 0 | USD | Coincide |
| D-PC | 9.6 | Patrimonio de la controladora | 2022 | 208,984,202 | 208,984,202 | 0 | USD | Coincide |
| D-PC | 9.6 | Patrimonio de la controladora | 2023 | 227,673,394 | 227,673,394 | 0 | USD | Coincide |
| D-PC | 9.6 | Patrimonio de la controladora | 2024 | 226,061,788 | 226,061,788 | 0 | USD | Coincide |
| D-PC | 9.6 | Patrimonio de la controladora | 2025 | 231,160,198 | 231,160,198 | 0 | USD | Coincide |
| D-MNC | 9.6 | Margen neto (controladora) | 2021 | 12.6740 | 12.67 | 0.00 | % | Coincide |
| D-MNC | 9.6 | Margen neto (controladora) | 2022 | 1.7131 | 1.71 | 0.00 | % | Coincide |
| D-MNC | 9.6 | Margen neto (controladora) | 2023 | 2.5718 | 2.57 | 0.00 | % | Coincide |
| D-MNC | 9.6 | Margen neto (controladora) | 2024 | 0.6390 | 0.64 | -0.00 | % | Coincide |
| D-MNC | 9.6 | Margen neto (controladora) | 2025 | 2.7061 | 2.71 | -0.00 | % | Coincide |
| D-RSAC | 9.6 | RSA (controladora) | 2021 | 11.9879 | 11.99 | -0.00 | % | Coincide |
| D-RSAC | 9.6 | RSA (controladora) | 2022 | 1.2737 | 1.27 | 0.00 | % | Coincide |
| D-RSAC | 9.6 | RSA (controladora) | 2023 | 1.5213 | 1.52 | 0.00 | % | Coincide |
| D-RSAC | 9.6 | RSA (controladora) | 2024 | 0.3701 | 0.37 | 0.00 | % | Coincide |
| D-RSAC | 9.6 | RSA (controladora) | 2025 | 1.5215 | 1.52 | 0.00 | % | Coincide |
| D-MAFC | 9.6 | MAF (controladora) | 2021 | 3.8995 | 3.90 | -0.00 | veces | Coincide |
| D-MAFC | 9.6 | MAF (controladora) | 2022 | 3.2157 | 3.22 | -0.00 | veces | Coincide |
| D-MAFC | 9.6 | MAF (controladora) | 2023 | 3.5538 | 3.55 | 0.00 | veces | Coincide |
| D-MAFC | 9.6 | MAF (controladora) | 2024 | 3.6591 | 3.66 | -0.00 | veces | Coincide |
| D-MAFC | 9.6 | MAF (controladora) | 2025 | 3.3831 | 3.38 | 0.00 | veces | Coincide |
| D-RSPC | 9.6 | RSP / ROE (controladora) | 2021 | 46.7468 | 46.75 | -0.00 | % | Coincide |
| D-RSPC | 9.6 | RSP / ROE (controladora) | 2022 | 4.0957 | 4.10 | -0.00 | % | Coincide |
| D-RSPC | 9.6 | RSP / ROE (controladora) | 2023 | 5.4065 | 5.41 | -0.00 | % | Coincide |
| D-RSPC | 9.6 | RSP / ROE (controladora) | 2024 | 1.3540 | 1.35 | 0.00 | % | Coincide |
| D-RSPC | 9.6 | RSP / ROE (controladora) | 2025 | 5.1475 | 5.15 | -0.00 | % | Coincide |
| FU25-EFECTIVO | 9.7 | Efectivo y equivalentes: variación | 2025 | -3,231,172 | -3,231,172 | 0 | USD | Coincide |
| FU25-INVERSIONES_CP | 9.7 | Inversiones (corriente): variación | 2025 | -143,420 | -143,420 | 0 | USD | Coincide |
| FU25-DEUDORES | 9.7 | Deudores comerciales y otras CxC: variación | 2025 | -27,034,533 | -27,034,533 | 0 | USD | Coincide |
| FU25-CXCR_CP | 9.7 | CxC empresas relacionadas (corriente): variación | 2025 | -104,658,180 | -104,658,180 | 0 | USD | Coincide |
| FU25-INV | 9.7 | Inventario: variación | 2025 | -46,943,251 | -46,943,251 | 0 | USD | Coincide |
| FU25-ANT | 9.7 | Pagos por anticipado: variación | 2025 | 455,817 | 455,817 | 0 | USD | Coincide |
| FU25-IMPA | 9.7 | Impuestos corrientes (activo): variación | 2025 | -3,510,958 | -3,510,958 | 0 | USD | Coincide |
| FU25-CXCLP | 9.7 | Cuentas por cobrar a largo plazo: variación | 2025 | 1,561,607 | 1,561,607 | 0 | USD | Coincide |
| FU25-CXCR_LP | 9.7 | CxC empresas relacionadas a LP: variación | 2025 | 262,128,668 | 143,444,117 | 118,684,551 | USD | Diferencia |
| FU25-INVLP | 9.7 | Inversiones (no corriente): variación | 2025 | -6,191,725 | -6,191,725 | 0 | USD | Coincide |
| FU25-PINV | 9.7 | Propiedades de inversión: variación | 2025 | 5,527,883 | 5,527,883 | 0 | USD | Coincide |
| FU25-PPE | 9.7 | Propiedades, planta y equipo: variación | 2025 | 1,283,610 | 1,283,610 | 0 | USD | Coincide |
| FU25-DU | 9.7 | Activos por derechos de uso: variación | 2025 | -6,007,437 | -6,007,437 | 0 | USD | Coincide |
| FU25-INT | 9.7 | Activos intangibles: variación | 2025 | -1,787,240 | -1,787,240 | 0 | USD | Coincide |
| FU25-IDA | 9.7 | Impuestos diferidos (activo): variación | 2025 | 572,580 | 572,580 | 0 | USD | Coincide |
| FU25-OAF | 9.7 | Otros activos financieros: variación | 2025 | 1,535,489 | 1,535,489 | 0 | USD | Coincide |
| FU25-PRCP | 9.7 | Préstamos de corto plazo: variación | 2025 | -7,341,995 | -7,341,995 | 0 | USD | Coincide |
| FU25-ARCP | 9.7 | Pasivos por arrendamientos (CP): variación | 2025 | -2,137,877 | -2,137,877 | 0 | USD | Coincide |
| FU25-TVCP | 9.7 | Títulos valores (CP): variación | 2025 | 67,211,061 | 67,211,061 | 0 | USD | Coincide |
| FU25-OPFCP | 9.7 | Otros pasivos financieros (CP): variación | 2025 | 1,705,111 | 1,705,111 | 0 | USD | Coincide |
| FU25-ACR | 9.7 | Acreedores comerciales y otras CxP: variación | 2025 | -52,005,604 | -52,005,604 | 0 | USD | Coincide |
| FU25-CXPR | 9.7 | CxP empresas relacionadas: variación | 2025 | 1,358,488 | 1,358,488 | 0 | USD | Coincide |
| FU25-IMPP | 9.7 | Impuestos corrientes (pasivo): variación | 2025 | -481,392 | -481,392 | 0 | USD | Coincide |
| FU25-PRLP | 9.7 | Préstamos y otras obligaciones (LP): variación | 2025 | -9,911,305 | -9,911,305 | 0 | USD | Coincide |
| FU25-ARLP | 9.7 | Pasivos por arrendamientos (LP): variación | 2025 | -5,315,358 | -5,315,358 | 0 | USD | Coincide |
| FU25-TVLP | 9.7 | Títulos valores (LP): variación | 2025 | -35,391,265 | -35,391,265 | 0 | USD | Coincide |
| FU25-OPFLP | 9.7 | Otros pasivos financieros (LP): variación | 2025 | -9,190,700 | -9,190,700 | 0 | USD | Coincide |
| FU25-PROV | 9.7 | Provisiones: variación | 2025 | -685,456 | -685,456 | 0 | USD | Coincide |
| FU25-IDP | 9.7 | Impuestos diferidos (pasivo): variación | 2025 | 1,961,069 | 1,961,069 | 0 | USD | Coincide |
| FU25-CS | 9.7 | Capital social: variación | 2025 | -2,000 | -2,000 | 0 | USD | Coincide |
| FU25-CA | 9.7 | Capital adicional: variación | 2025 | 0 | 0 | 0 | USD | Coincide |
| FU25-RL | 9.7 | Reserva legal: variación | 2025 | 962,529 | 962,529 | 0 | USD | Coincide |
| FU25-SA | 9.7 | Superávit por acciones: variación | 2025 | 0 | 0 | 0 | USD | Coincide |
| FU25-RC | 9.7 | Reservas de capital: variación | 2025 | 8,218,446 | 8,218,446 | 0 | USD | Coincide |
| FU25-EC | 9.7 | Efecto de conversión: variación | 2025 | -8,003,019 | -8,003,019 | 0 | USD | Coincide |
| FU25-RA | 9.7 | Resultados acumulados: variación | 2025 | -4,915,552 | -4,915,552 | 0 | USD | Coincide |
| FU25-RP | 9.7 | Resultado del período: variación | 2025 | 8,838,006 | 8,838,006 | 0 | USD | Coincide |
| FU25-TOTAL | 9.7 | Total fuentes = total usos | 2025 | 408,447,177 | 289,762,626 | 118,684,551 | USD | Diferencia |
| FU25-CXCR-NETO | 9.7 | Aumento neto de CxC relacionadas (CP + LP) | 2025 | 157,470,488 | 38,785,937 | 118,684,551 | USD | Diferencia |
| FU25-DF | 9.7 | Deuda financiera total 2025 (millones) | 2024 | 352.499 | 352.5 | -0.0 | USD | Coincide |
| FU25-DF | 9.7 | Deuda financiera total 2025 (millones) | 2025 | 352.127 | 352.1 | 0.0 | USD | Coincide |
| FU23-EFECTIVO | 9.7 | Efectivo: variación | 2023 | -8,025,092 | -8,025,092 | 0 | USD | Coincide |
| FU23-CDCP | 9.7 | Certificados de depósito (corriente): variación | 2023 | 400,000 | 400,000 | 0 | USD | Coincide |
| FU23-CXC | 9.7 | Cuentas por cobrar comerciales: variación | 2023 | 8,691,433 | 8,691,433 | 0 | USD | Coincide |
| FU23-CXCR | 9.7 | CxC partes relacionadas (corriente): variación | 2023 | -19,456,261 | -19,456,261 | 0 | USD | Coincide |
| FU23-OCXC | 9.7 | Otras cuentas por cobrar (corriente): variación | 2023 | 2,383,745 | 2,383,745 | 0 | USD | Coincide |
| FU23-INV | 9.7 | Inventarios: variación | 2023 | 421,877 | 421,877 | 0 | USD | Coincide |
| FU23-GPA | 9.7 | Gastos pagados por anticipado: variación | 2023 | -80,852 | -80,852 | 0 | USD | Coincide |
| FU23-AISR | 9.7 | Anticipos de ISR: variación | 2023 | -3,212,707 | -3,212,707 | 0 | USD | Coincide |
| FU23-CDLP | 9.7 | Certificados de depósito (no corriente): variación | 2023 | 0 | 0 | 0 | USD | Coincide |
| FU23-CXCRLP | 9.7 | CxC partes relacionadas (no corriente): variación | 2023 | 110,380,709 | 110,380,709 | 0 | USD | Coincide |
| FU23-OCXCLP | 9.7 | Otras cuentas por cobrar (no corriente): variación | 2023 | 924,000 | 924,000 | 0 | USD | Coincide |
| FU23-IACC | 9.7 | Inversiones en acciones: variación | 2023 | -24,486 | -24,486 | 0 | USD | Coincide |
| FU23-PINV | 9.7 | Propiedades de inversión: variación | 2023 | 2,246,534 | 2,246,534 | 0 | USD | Coincide |
| FU23-PPE | 9.7 | Propiedades, planta y equipo: variación | 2023 | 19,676,858 | 19,676,858 | 0 | USD | Coincide |
| FU23-DU | 9.7 | Activos por derecho de uso: variación | 2023 | -86,597 | -86,597 | 0 | USD | Coincide |
| FU23-INT | 9.7 | Activos intangibles: variación | 2023 | -509,971 | -509,971 | 0 | USD | Coincide |
| FU23-PLUS | 9.7 | Plusvalía mercantil: variación | 2023 | 23,625,815 | 23,625,815 | 0 | USD | Coincide |
| FU23-OA | 9.7 | Otros activos: variación | 2023 | 182,620 | 182,620 | 0 | USD | Coincide |
| FU23-IDA | 9.7 | Activo por ISR diferido: variación | 2023 | -461,772 | -461,772 | 0 | USD | Coincide |
| FU23-PRCP | 9.7 | Préstamos bancarios (corriente): variación | 2023 | 14,064,043 | 14,064,043 | 0 | USD | Coincide |
| FU23-ARCP | 9.7 | Arrendamientos (corriente): variación | 2023 | 33,471 | 33,471 | 0 | USD | Coincide |
| FU23-BOCP | 9.7 | Bonos corporativos (corriente): variación | 2023 | 8,181,371 | 8,181,371 | 0 | USD | Coincide |
| FU23-CICP | 9.7 | Certificados de inversión (corriente): variación | 2023 | -447,165 | -447,165 | 0 | USD | Coincide |
| FU23-TICP | 9.7 | Derechos titularizados (corriente): variación | 2023 | -22,466 | -22,466 | 0 | USD | Coincide |
| FU23-DPCP | 9.7 | Documentos por pagar (corriente): variación | 2023 | 6,583,804 | 6,583,804 | 0 | USD | Coincide |
| FU23-CXP | 9.7 | Cuentas por pagar comerciales: variación | 2023 | 98,970,000 | 98,970,000 | 0 | USD | Coincide |
| FU23-CXPR | 9.7 | CxP partes relacionadas: variación | 2023 | -30,142,617 | -30,142,617 | 0 | USD | Coincide |
| FU23-OCXP | 9.7 | Otras cuentas por pagar (corriente): variación | 2023 | 3,273,085 | 3,273,085 | 0 | USD | Coincide |
| FU23-ISRCP | 9.7 | ISR por pagar (corriente): variación | 2023 | 682,979 | 682,979 | 0 | USD | Coincide |
| FU23-PRLP | 9.7 | Préstamos bancarios (no corriente): variación | 2023 | 4,270,376 | 4,270,376 | 0 | USD | Coincide |
| FU23-ARLP | 9.7 | Arrendamientos (no corriente): variación | 2023 | -2,886,152 | -2,886,152 | 0 | USD | Coincide |
| FU23-BOLP | 9.7 | Bonos corporativos (no corriente): variación | 2023 | -350,112 | -350,112 | 0 | USD | Coincide |
| FU23-CILP | 9.7 | Certificados de inversión (no corriente): variación | 2023 | 3,682,672 | 3,682,672 | 0 | USD | Coincide |
| FU23-TILP | 9.7 | Derechos titularizados (no corriente): variación | 2023 | -1,575,171 | -1,575,171 | 0 | USD | Coincide |
| FU23-DPLP | 9.7 | Documentos por pagar a largo plazo: variación | 2023 | 16,484,899 | 16,484,899 | 0 | USD | Coincide |
| FU23-OCXPLP | 9.7 | Otras cuentas por pagar (no corriente): variación | 2023 | 293,522 | 293,522 | 0 | USD | Coincide |
| FU23-PVA | 9.7 | Pasivo por prima en venta de acciones: variación | 2023 | -40,738 | -40,738 | 0 | USD | Coincide |
| FU23-BPE | 9.7 | Beneficios post empleo: variación | 2023 | 203,726 | 203,726 | 0 | USD | Coincide |
| FU23-ISRLP | 9.7 | ISR por pagar (no corriente): variación | 2023 | 465,955 | 465,955 | 0 | USD | Coincide |
| FU23-IDP | 9.7 | Pasivo por ISR diferido: variación | 2023 | 1,553,741 | 1,553,741 | 0 | USD | Coincide |
| FU23-CS | 9.7 | Capital social: variación | 2023 | 0 | 0 | 0 | USD | Coincide |
| FU23-PA | 9.7 | Prima sobre acciones: variación | 2023 | 0 | 0 | 0 | USD | Coincide |
| FU23-AC | 9.7 | Aportaciones de capital: variación | 2023 | 84,787 | 84,787 | 0 | USD | Coincide |
| FU23-RL | 9.7 | Reserva legal: variación | 2023 | 846,319 | 846,319 | 0 | USD | Coincide |
| FU23-ORC | 9.7 | Otras reservas de capital: variación | 2023 | 920,851 | 920,851 | 0 | USD | Coincide |
| FU23-RA | 9.7 | Resultados acumulados: variación | 2023 | 16,837,235 | 16,837,235 | 0 | USD | Coincide |
| FU23-NC | 9.7 | Participaciones no controladoras: variación | 2023 | -4,892,562 | -4,892,562 | 0 | USD | Coincide |
| FU23-TOTAL | 9.7 | Total fuentes = total usos | 2023 | 209,290,574 | 209,290,574 | 0 | USD | Coincide |
| S10-ING | 10 | Ingresos ordinarios Alutech 2025 (millones) | 2025 | 439.7046 | 439.70 | 0.00 | USD | Coincide |
| S10-MB | 10 | Margen bruto Alutech 2025 | 2025 | 24.6244 | 24.62 | 0.00 | % | Coincide |
| S10-MO | 10 | Margen operativo Alutech 2025 | 2025 | 12.4324 | 12.43 | 0.00 | % | Coincide |
| S10-MN | 10 | Margen neto Alutech 2025 | 2025 | 2.7061 | 2.71 | -0.00 | % | Coincide |
| S10-RC | 10 | Razón corriente Alutech 2025 | 2025 | 0.6672 | 0.67 | -0.00 | veces | Coincide |
| S10-PA | 10 | Prueba ácida Alutech 2025 | 2025 | 0.4791 | 0.48 | -0.00 | veces | Coincide |
| S10-CTN | 10 | Capital de trabajo neto Alutech 2025 (millones) | 2025 | -123.5680 | -123.57 | 0.00 | USD | Coincide |
| S10-END | 10 | Endeudamiento Alutech 2025 | 2025 | 70.4417 | 70.44 | 0.00 | % | Coincide |
| S10-ROA | 10 | ROA Alutech 2025 | 2025 | 1.5215 | 1.52 | 0.00 | % | Coincide |
| S10-ROE | 10 | ROE Alutech 2025 | 2025 | 5.1475 | 5.15 | -0.00 | % | Coincide |
| S10-GF | 10 | Gastos financieros Alutech 2025 (millones) | 2025 | 37.399 | 37.4 | -0.0 | USD | Coincide |

## 6. Resultados con diferencias, coincidencias por redondeo y no verificables

| Ref. | Año | Concepto | Aplicación | Trabajo ANF | Diferencia | Dif. % | Estado | Categoría de la causa |
|---|---|---|---|---|---|---|---|---|
| T3-AC | 2023 | Total activo corriente | 429,794,544 | 541,094,544 | -111,300,000 | -20.57% | Diferencia | Error en el trabajo académico |
| T3-AC-VA | 2023 | Activo corriente: variación absoluta | -18,877,857 | 92,422,143 | -111,300,000 | -120.43% | Diferencia | Error en el trabajo académico |
| T3-AC-VR | 2023 | Activo corriente: variación relativa | -4.2075 | 20.60 | -24.81 | -120.42% | Diferencia | Error en el trabajo académico |
| T3-PC | 2022 | Total pasivo corriente | 231,944,180 | 231,914,180 | 30,000 | 0.01% | Diferencia | Error en el trabajo académico |
| T3-PC | 2023 | Total pasivo corriente | 333,120,685 | 342,120,685 | -9,000,000 | -2.63% | Diferencia | Error en el trabajo académico |
| T3-PC-VA | 2022 | Pasivo corriente: variación absoluta | 25,970,950 | 25,940,950 | 30,000 | 0.12% | Diferencia | Error en el trabajo académico |
| T3-PC-VA | 2023 | Pasivo corriente: variación absoluta | 101,176,505 | 110,206,505 | -9,030,000 | -8.19% | Diferencia | Error en el trabajo académico |
| T3-PC-VR | 2022 | Pasivo corriente: variación relativa | 12.6089 | 12.59 | 0.02 | 0.15% | Diferencia | Error en el trabajo académico |
| T3-PC-VR | 2023 | Pasivo corriente: variación relativa | 43.6211 | 47.52 | -3.90 | -8.20% | Diferencia | Error en el trabajo académico |
| T4-AC | 2023 | Total activo corriente | 429,794,544 | 541,094,544 | -111,300,000 | -20.57% | Diferencia | Error en el trabajo académico |
| T4-AC-VA | 2024 | Activo corriente: variación absoluta | 2,977,134 | -108,322,866 | 111,300,000 | 102.75% | Diferencia | Error en el trabajo académico |
| T4-AC-VR | 2024 | Activo corriente: variación relativa | 0.6927 | -20.02 | 20.71 | 103.46% | Diferencia | Error en el trabajo académico |
| T4-PC | 2023 | Total pasivo corriente | 333,120,685 | 342,120,685 | -9,000,000 | -2.63% | Diferencia | Error en el trabajo académico |
| T4-PC-VA | 2024 | Pasivo corriente: variación absoluta | 29,845,530 | 20,845,530 | 9,000,000 | 43.17% | Diferencia | Error en el trabajo académico |
| T4-PC-VR | 2024 | Pasivo corriente: variación relativa | 8.9594 | 6.09 | 2.87 | 47.12% | Diferencia | Error en el trabajo académico |
| T5-UO | 2022 | Utilidad operativa | 31,200,977 | 31,200,000 | 977 | 0.00% | Diferencia | Diferencia de redondeo |
| T6-AC | 2023 | Activo corriente | 429,794,544 | 541,094,544 | -111,300,000 | -20.57% | Diferencia | Error en el trabajo académico |
| T6-PC | 2022 | Pasivo corriente | 231,944,180 | 231,914,180 | 30,000 | 0.01% | Diferencia | Error en el trabajo académico |
| T6-PC | 2023 | Pasivo corriente | 333,120,685 | 342,120,685 | -9,000,000 | -2.63% | Diferencia | Error en el trabajo académico |
| T6-CTN | 2022 | Capital de trabajo neto | 216,728,221 | 216,758,221 | -30,000 | -0.01% | Diferencia | Error en el trabajo académico |
| T6-CTN | 2023 | Capital de trabajo neto | 96,673,859 | 198,973,859 | -102,300,000 | -51.41% | Diferencia | Error en el trabajo académico |
| T6-CTN-VA | 2022 | CTN: variación absoluta | 38,819,904 | 38,849,904 | -30,000 | -0.08% | Diferencia | Error en el trabajo académico |
| T6-CTN-VA | 2023 | CTN: variación absoluta | -120,054,362 | -17,784,362 | -102,270,000 | -575.06% | Diferencia | Error en el trabajo académico |
| T6-CTN-VA | 2024 | CTN: variación absoluta | -26,868,396 | -129,168,396 | 102,300,000 | 79.20% | Diferencia | Error en el trabajo académico |
| T6-CTN-VR | 2022 | CTN: variación relativa | 21.8202 | 21.84 | -0.02 | -0.09% | Diferencia | Error en el trabajo académico |
| T6-CTN-VR | 2023 | CTN: variación relativa | -55.3940 | -8.20 | -47.19 | -575.54% | Diferencia | Error en el trabajo académico |
| T6-CTN-VR | 2024 | CTN: variación relativa | -27.7928 | -64.92 | 37.13 | 57.19% | Diferencia | Error en el trabajo académico |
| T6-RC | 2023 | Razón corriente | 1.2902 | 1.58 | -0.29 | -18.34% | Diferencia | Error en el trabajo académico |
| T6-PA | 2023 | Prueba ácida | 0.8655 | 1.17 | -0.30 | -26.03% | Diferencia | Error en el trabajo académico |
| T7-CTN | 2022 | CTN final | 216,728,221 | 216,758,221 | -30,000 | -0.01% | Diferencia | Error en el trabajo académico |
| T7-CTN | 2023 | CTN final | 96,673,859 | 198,973,859 | -102,300,000 | -51.41% | Diferencia | Error en el trabajo académico |
| T7-CTN-VA | 2022 | Variación absoluta del CTN | 38,819,904 | 38,849,904 | -30,000 | -0.08% | Diferencia | Error en el trabajo académico |
| T7-CTN-VA | 2023 | Variación absoluta del CTN | -120,054,362 | -17,784,362 | -102,270,000 | -575.06% | Diferencia | Error en el trabajo académico |
| T7-CTN-VA | 2024 | Variación absoluta del CTN | -26,868,396 | -129,168,396 | 102,300,000 | 79.20% | Diferencia | Error en el trabajo académico |
| T7-CTN-VR | 2022 | Variación relativa del CTN | 21.8202 | 21.84 | -0.02 | -0.09% | Diferencia | Error en el trabajo académico |
| T7-CTN-VR | 2023 | Variación relativa del CTN | -55.3940 | -8.20 | -47.19 | -575.54% | Diferencia | Error en el trabajo académico |
| T7-CTN-VR | 2024 | Variación relativa del CTN | -27.7928 | -64.92 | 37.13 | 57.19% | Diferencia | Error en el trabajo académico |
| B-CXC | 2023 | Cuentas por cobrar usadas | 41,272,525 | 96,097,483 | -54,824,958 | -57.05% | Diferencia | Diferencia de fórmula |
| B-RCC | 2023 | Rotación de CxC | 11.5967 | 4.98 | 6.62 | 132.86% | Diferencia | Diferencia de fórmula |
| B-PPC | 2023 | PPC | 31.475 | 73.3 | -41.8 | -57.06% | Diferencia | Diferencia de fórmula |
| B-PPC | 2025 | PPC | 58.248 | 58.3 | -0.1 | -0.09% | Coincidencia por redondeo | Diferencia de redondeo |
| C-CO82 | 2025 | Ciclo operativo (PPI + PPC) | 135.138 | 135.2 | -0.1 | -0.05% | Coincidencia por redondeo | Diferencia de redondeo |
| E-PCP | 2021 | Pasivo corriente / pasivo total | 50.4053 | 50.40 | 0.01 | 0.01% | Coincidencia por redondeo | Diferencia de redondeo |
| C-CO | 2022 | Ciclo operativo | 149.2855 | 149.28 | 0.01 | 0.00% | Coincidencia por redondeo | Diferencia de redondeo |
| C-CO | 2023 | Ciclo operativo | 169.7290 | 169.72 | 0.01 | 0.01% | Coincidencia por redondeo | Diferencia de redondeo |
| W-WACC | 2023 | WACC | 3.8745 | 3.88 | -0.01 | -0.14% | Coincidencia por redondeo | Diferencia de redondeo |
| FU25-CXCR_LP | 2025 | CxC empresas relacionadas a LP: variación | 262,128,668 | 143,444,117 | 118,684,551 | 82.74% | Diferencia | Error de clasificación |
| FU25-TOTAL | 2025 | Total fuentes = total usos | 408,447,177 | 289,762,626 | 118,684,551 | 40.96% | Diferencia | Error de clasificación |
| FU25-CXCR-NETO | 2025 | Aumento neto de CxC relacionadas (CP + LP) | 157,470,488 | 38,785,937 | 118,684,551 | 306.00% | Diferencia | Error de clasificación |

Resumen de las discrepancias y de las coincidencias condicionadas a supuestos, por categoría de causa:

| Categoría de la causa | Estado | Valores |
|---|---|---|
| Diferencia de fórmula | Diferencia | 3 |
| Diferencia de redondeo | Coincidencia por redondeo | 6 |
| Diferencia de redondeo | Diferencia | 1 |
| Error de clasificación | Diferencia | 3 |
| Error en el trabajo académico | Diferencia | 36 |
| Supuesto no verificable | Coincide | 25 |

## 7. Causas identificadas

**OBS-01 — Error en el trabajo académico: Error del trabajo: cifra no rastreable a los estados financieros.** El estado combinado de situación financiera 2023 (Certificación 2023, pág. 7 del PDF) presenta «Total activos corrientes» 429,794,544, y la suma de sus partidas coincide con ese total. Las Tablas 3, 4 y 6 del trabajo usan 541,094,544 (111,300,000 más). El propio trabajo usa la cifra correcta en el análisis vertical (53.12 %), la razón circulante de 8.1 (1.29) y el fondo de maniobra de 9.2. 541,094,544 no aparece en ningún documento de la carpeta; el informe PCR (SV-CIALUTECH-202506) muestra 541.1 M para dic‑23, pero con otro perímetro de consolidación (activo total 818.1 M frente a 809.1 M). Se conserva el dato del estado financiero original.

Valores afectados: T3-AC (2023), T4-AC (2023), T6-AC (2023).

**OBS-02 — Error en el trabajo académico: Error del trabajo: cifra no rastreable a los estados financieros.** El estado 2023 (pág. 7) presenta «Total pasivos corrientes» 333,120,685, igual a la suma de sus partidas. Las Tablas 3, 4 y 6 usan 342,120,685 (9,000,000 más). La razón de tesorería (9.1), el fondo de maniobra (9.2) y el vertical (41.17 %) del propio trabajo usan 333,120,685. El informe PCR muestra 342.1 M para dic‑23 con otro perímetro.

Valores afectados: T3-PC (2023), T4-PC (2023), T6-PC (2023).

**OBS-03 — Error en el trabajo académico: Error de transcripción del trabajo.** El estado 2022 (Certificación 2022, pág. 9) presenta «Total pasivos corrientes» 231,944,180 (= 458,148,329 − 226,204,149). Las Tablas 3, 6 y 7 usan 231,914,180 (dígitos 4 y 1 intercambiados: 30,000 menos). Las secciones 9.1 y 9.2 del trabajo usan la cifra correcta.

Valores afectados: T3-PC (2022), T6-PC (2022).

**OBS-04 — Error en el trabajo académico: Diferencia derivada de OBS-03 (pasivo corriente 2022).** Variaciones y capital de trabajo calculados con el pasivo corriente 2022 mal transcrito (231,914,180 en lugar de 231,944,180). Con la cifra del documento el CTN 2022 es 216,728,221, el mismo valor que el trabajo presenta en 8.1 y 9.2.

Valores afectados: T3-PC-VA (2022), T3-PC-VR (2022), T6-CTN (2022), T6-CTN-VA (2022), T6-CTN-VR (2022), T7-CTN (2022), T7-CTN-VA (2022), T7-CTN-VR (2022).

**OBS-05 — Error en el trabajo académico: Diferencia derivada de OBS-01, OBS-02 y OBS-03.** Variaciones, capital de trabajo, razón corriente y prueba ácida calculados por el trabajo con el activo corriente (541,094,544) y el pasivo corriente (342,120,685) de 2023 que no corresponden al documento. Con las cifras originales: CTN 2023 = 96,673,859; razón corriente 1.29; prueba ácida 0.87 (los mismos valores que el trabajo presenta en 8.1 y 9.2). Las variaciones 2023→2024 cambian en consecuencia (p. ej. activo corriente +0.69 % en lugar de −20.02 %). La interpretación de 6.5 («2022–2023: presión sobre el capital de trabajo», CTN −8.20 %) subestima el deterioro: con los datos originales el CTN cae 55.39 % en 2023.

Valores afectados: T3-AC-VA (2023), T3-AC-VR (2023), T3-PC-VA (2023), T3-PC-VR (2023), T4-AC-VA (2024), T4-AC-VR (2024), T4-PC-VA (2024), T4-PC-VR (2024), T6-CTN (2023), T6-CTN-VA (2023), T6-CTN-VA (2024), T6-CTN-VR (2023), T6-CTN-VR (2024), T6-PA (2023), T6-RC (2023), T7-CTN (2023), T7-CTN-VA (2023), T7-CTN-VA (2024), T7-CTN-VR (2023), T7-CTN-VR (2024).

**OBS-06 — Diferencia de redondeo: Presentación del trabajo (cifra redondeada y señalada con *).** El estado de resultados 2022 no presenta la utilidad de operación; la aplicación la obtiene como subtotal: 89,322,338 − 18,344,656 − 39,712,552 − 397,016 + 332,863 = 31,200,977. La Tabla 5 muestra 31,200,000* (redondeado y marcado con asterisco); las secciones 8.3 B y 8.4 del trabajo usan 31,200,977. Las variaciones relativas de la Tabla 5 coinciden con la cifra exacta.

Valores afectados: T5-UO (2022).

**OBS-07 — Diferencia de fórmula: Base de cálculo distinta (inconsistencia interna del trabajo).** En 8.2 B el trabajo usa solo cuentas por cobrar comerciales en 2021–2022 (53,081,088 y 32,581,092) y comerciales + otras en 2023 (41,272,525 + 54,824,958 = 96,097,483), como señala su asterisco. La aplicación aplica la misma base en todos los años (línea comercial presentada). Con la base «comerciales y otras» la aplicación obtiene para 2023 una rotación de 4.98 veces y 73.28 días (indicadores «rotacion_cxc_total» y «ppc_total»), iguales a los del trabajo. En 9.3 el propio trabajo usa 41,272,525 para 2023 (31.47 días), que coincide con la aplicación.

Valores afectados: B-CXC (2023), B-PPC (2023), B-RCC (2023).

**OBS-08 — Diferencia de redondeo: Redondeo del trabajo.** 365 / 6.2663 = 58.248 días; el trabajo presenta 58.3, posiblemente por redondeo doble (58.248 → 58.25 → 58.3). Diferencia de 0.05 días, menor que una unidad del decimal presentado.

Valores afectados: B-PPC (2025).

**OBS-09 — Diferencia de redondeo: Redondeo del trabajo (suma de componentes redondeados).** El trabajo suma el período de inventario y el de cobro ya redondeados (p. ej. 76.9 + 58.3 = 135.2; 125.48 + 23.80 = 149.28); la aplicación suma los valores sin redondear (135.14 y 149.29). La diferencia no supera una unidad del último decimal presentado.

Valores afectados: C-CO (2022), C-CO (2023), C-CO82 (2025).

**OBS-10 — Diferencia de redondeo: Redondeo del trabajo.** 205,973,230 / 408,633,995 = 50.4053 %, que redondea a 50.41 %; el trabajo presenta 50.40 % (truncado). Diferencia de 0.005 puntos.

Valores afectados: E-PCP (2021).

**OBS-11 — Diferencia de redondeo: Redondeo e inconsistencia interna del trabajo.** El cálculo da un WACC 2023 de 3.8745 % (3.87 %). El cuadro del trabajo muestra 3.88 % (suma de los aportes ya redondeados por línea), mientras que el texto de 9.4.3 dice 3.87 %, que coincide con la aplicación (referencia W-WACC-TXT).

Valores afectados: W-WACC (2023).

**OBS-12 — Error de clasificación: Error de clasificación del trabajo: equivalencia no respaldada por los documentos.** En 9.7 el trabajo trata «Otras cuentas por cobrar a LP» de 2024 (118,684,551; 12_EEFF_diciembre_2024.pdf, pág. 1) como si fuera la misma partida que «Cuentas por cobrar Empresas Relacionadas a LP» de 2025 (262,128,668) y obtiene una variación de 143,444,117. El estado de 2024 no la identifica como cuenta con partes relacionadas y el informe PCR (SV-CIALUTECH-202506, balance resumido) presenta a dic‑24 «Cuentas por cobrar de LP» 119.7 M y «Cuentas por cobrar a partes relacionadas» (no corriente) 0.0. La aplicación conserva la denominación de 2024 en el grupo «Otras cuentas por cobrar (no corrientes)»: en 2025 la cuenta de relacionadas a LP aumenta 262,128,668 (uso) y la de otras CxC a LP disminuye 118,684,551 (fuente); el total de fuentes y usos es 408,447,177 en lugar de 289,762,626 (ambos totales cuadran). El aumento neto «relacionadas CP + LP» es 157,470,488 en lugar de 38,785,937. Ningún indicador cambia: usan totales.

Valores afectados: FU25-CXCR-NETO (2025), FU25-CXCR_LP (2025), FU25-TOTAL (2025).

**OBS-13 — Supuesto no verificable: Supuesto no verificable con los documentos (WACC).** La coincidencia se obtiene con las tasas de interés (6.75 % a 8.50 %) y la tasa de ISR (30 %) que supone el trabajo; ninguna figura en los documentos de la carpeta (el trabajo cita notas del informe auditado que no están disponibles y, para 2024–2025, no cita fuente; la certificación 2021 indica tasas de ISR de 25 % a 30 % según el país). La aplicación reproduce correctamente el método, pero el resultado no es verificable con las fuentes originales. Los pesos, el costo del patrimonio (ROE) y el ROA sí provienen de los estados financieros.

Valores afectados: W-WACC (2023).

## 8. Fórmulas utilizadas por la aplicación

| Indicador | Fórmula | Cuentas / rubros | Unidad | Sección del trabajo |
|---|---|---|---|---|
| Capital de trabajo neto (fondo de maniobra a corto plazo) | Activo corriente − Pasivo corriente | Total activo corriente; total pasivo corriente | USD | 5.6 a, 6.5, 8.1 C, 9.2.1 |
| Razón corriente (circulante) | Activo corriente / Pasivo corriente | Total activo corriente; total pasivo corriente | veces | 5.6 b, 6.5, 8.1 A |
| Prueba ácida | (Activo corriente − Inventarios) / Pasivo corriente | Total activo corriente; inventarios; total pasivo corriente | veces | 5.6 c, 6.5, 8.1 B |
| Razón de efectivo | Efectivo y equivalentes / Pasivo corriente | Efectivo y equivalentes; total pasivo corriente | veces | 5.6 d (definida; el trabajo no presenta resultados) |
| Razón de tesorería | (Efectivo + inversiones y depósitos corrientes) / Pasivo corriente × 100 | Efectivo; certificados de depósito, bonos e inversiones corrientes; total pasivo corriente | % | 9.1 |
| Capitales permanentes | Patrimonio + Pasivo no corriente | Total patrimonio; total pasivo no corriente | USD | 9.2.2 |
| Fondo de maniobra a largo plazo | Capitales permanentes − Activo no corriente | Total patrimonio; total pasivo no corriente; total activo no corriente | USD | 9.2.2 |
| Rotación de inventarios | Costo de ventas / Inventarios (saldo al cierre) | Costo de ventas; inventarios | veces | 8.2 A |
| Período promedio (edad promedio) de inventario | Inventarios / Costo de ventas × 365 | Inventarios; costo de ventas | días | 8.2 A, 9.3 |
| Rotación de cuentas por cobrar comerciales | Ingresos ordinarios / Cuentas por cobrar comerciales (línea presentada) | Ingresos ordinarios (aproximación de las ventas a crédito); cuentas por cobrar comerciales | veces | 8.2 B |
| Período promedio de cobro | Cuentas por cobrar comerciales / Ingresos ordinarios × 365 | Cuentas por cobrar comerciales (línea presentada); ingresos ordinarios | días | 8.2 B, 9.3 |
| Rotación de cuentas por cobrar comerciales y otras | Ingresos ordinarios / (Cuentas por cobrar comerciales + otras cuentas por cobrar corrientes) | Ingresos ordinarios; cuentas por cobrar comerciales y otras | veces | 8.2 B (variante homogénea) |
| Período de cobro (cartera comercial y otras) | (Cuentas por cobrar comerciales + otras) / Ingresos ordinarios × 365 | Cuentas por cobrar comerciales y otras; ingresos ordinarios | días | 8.2 B (variante homogénea) |
| Período promedio de pago | Cuentas por pagar comerciales / Costo de ventas × 365 | Cuentas por pagar comerciales (línea presentada); costo de ventas (aproximación de las compras) | días | 9.3 |
| Ciclo operativo | PPI + PPC | Período promedio de inventario; período promedio de cobro | días | 8.2 C, 9.3 |
| Ciclo de conversión del efectivo | Ciclo operativo − PPP | Ciclo operativo; período promedio de pago | días | 5.6 k, 9.3 |
| Rotación de activos totales | Ingresos ordinarios / Activo total | Ingresos ordinarios; total activo | veces | 8.2 D, 9.5 |
| Índice de endeudamiento | Pasivo total / Activo total × 100 | Total pasivo; total activo | % | 8.3 A |
| Pasivo corriente sobre pasivo total | Pasivo corriente / Pasivo total × 100 | Total pasivo corriente; total pasivo | % | 8.3 A (texto) |
| Razón deuda-capital patrimonial | Pasivo total / Patrimonio total | Total pasivo; total patrimonio | veces | 8.3 D |
| Razón de cargos de interés fijo | Utilidad de operación / Gastos financieros netos | Utilidad de operación; gastos financieros − ingresos financieros | veces | 8.3 B |
| Cobertura con gastos financieros brutos | Utilidad de operación / Gastos financieros (brutos) | Utilidad de operación; gastos financieros | veces | Complementario (no figura en el trabajo) |
| Índice de cobertura de pagos fijos | (UAII + arrendamientos) / (intereses + arrendamientos + principal / (1 − t)) | No disponible en los documentos | veces | 8.3 C |
| Margen de utilidad bruta | Utilidad bruta / Ingresos ordinarios × 100 | Utilidad bruta; ingresos ordinarios | % | 8.4 A |
| Margen de utilidad operativa | Utilidad de operación / Ingresos ordinarios × 100 | Utilidad de operación; ingresos ordinarios | % | 8.4 B |
| Margen de utilidad neta | Utilidad neta / Ingresos ordinarios × 100 | Utilidad neta del ejercicio; ingresos ordinarios | % | 8.4 C, 9.5 |
| Rendimiento sobre los activos totales (ROA) | Utilidad neta / Activo total al cierre × 100 | Utilidad neta; total activo | % | 8.4 E |
| Retorno sobre el patrimonio (ROE) | Utilidad neta / Patrimonio total al cierre × 100 | Utilidad neta; total patrimonio (incluye participaciones no controladoras) | % | 8.4 F |
| EBITDA | Utilidad de operación + Depreciación y amortización | Utilidad de operación; depreciación y amortización (estado de resultados o flujo de efectivo) | USD | 6.7 (texto, 2025) |
| Ganancia por acción (EPS) | Utilidad atribuible a accionistas comunes / Promedio ponderado de acciones | Número de acciones (no disponible) | USD | 8.4 D |
| Relación precio/ganancias (P/E) | Precio de mercado por acción / EPS | Precio por acción y EPS (no disponibles) | veces | 8.5 A |
| Razón mercado/libro (M/L) | Precio de mercado por acción / Valor contable por acción | Precio y número de acciones (no disponibles) | veces | 8.5 B |
| Multiplicador del apalancamiento financiero (MAF) | Activo total / Patrimonio total | Total activo; total patrimonio | veces | 9.6 |
| RSA (ROA) por DuPont | Margen de utilidad neta × Rotación de activos totales | Margen neto; rotación de activos | % | 9.5 |
| RSP (ROE) por DuPont modificado | RSA × MAF | RSA; MAF | % | 9.6 |
| Margen neto (controladora) | Utilidad atribuible a la controladora / Ingresos ordinarios × 100 | Utilidad atribuible a los propietarios de la controladora; ingresos ordinarios | % | 9.6 (controladora) |
| RSA (controladora) | Margen neto (controladora) × Rotación de activos | Margen neto de la controladora; rotación de activos | % | 9.6 (controladora) |
| MAF (controladora) | Activo total / Patrimonio atribuible a la controladora | Total activo; total patrimonio − participaciones no controladoras | veces | 9.6 (controladora) |
| RSP (ROE) de la controladora | RSA (controladora) × MAF (controladora) | RSA y MAF de la controladora | % | 9.6 (controladora) |

## 9. Análisis de las discrepancias

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

## 10. Fuera del alcance de la comparación

- Sección 10: cifras de Ternium S.A. (ingresos USD 15,609.09 M, márgenes 15.08 % / 4.52 % / 1.94 %, razón corriente 2.49x, prueba ácida 1.45x, CTN USD 5,862.16 M, endeudamiento 31.62 %, ROA 1.28 %, ROE 1.88 %, patrimonio USD 16,147.75 M). Provienen de una fuente externa que no está en documentos/: no son verificables y la aplicación no las registra.
- Sección 3.2: historia, cuota de mercado, red de tiendas, junta directiva. Información descriptiva sin cálculos.
- Sección 8.3 C: el índice de cobertura de pagos fijos no se cuantifica (el trabajo indica que iguala a la razón de cargos de interés fijo por falta de desglose).
- Sección 9.4: tablas detalladas por cuenta de cada año. La aplicación reproduce cada línea (pantalla y exportaciones); la comparación numérica se hace con el cuadro comparativo 2021–2025 y los totales de cada año.

Coinciden 672 valores, 6 coinciden por redondeo, 43 presentan diferencias con causa documentada, 0 no son verificables y 15 no aplican (no calculables en ambos).
