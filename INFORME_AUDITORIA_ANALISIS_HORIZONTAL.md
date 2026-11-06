# Informe de auditoría del análisis horizontal

**Empresa:** Alutech, S. A. de C. V., y subsidiarias — División Acero, 2021–2025
**Fecha:** 5 de noviembre de 2026
**Alcance:** apartado «Análisis horizontal» de la aplicación y secciones 6.1 a 6.8 del «Trabajo de investigación ANF»
**Modalidad:** solo lectura. Las pruebas se hicieron en copias aisladas. No se modificó nada del proyecto, salvo la creación de este informe y de `DESCRIPCION_ACADEMICA_ANALISIS_HORIZONTAL.md`.

---

## 1. Resumen ejecutivo

**Veredicto.** Las Tablas 3 a 7 y el nivel de rubros son confiables: sus cálculos son dinámicos y sus fórmulas son correctas. Las tablas proceden de los estados originales y coinciden al 100 % con el documento académico. El nivel «Grupos de análisis» es aritméticamente correcto, pero **no debe usarse para interpretar 2023–2024 sin corregirlo**: presenta como −100 % partidas que solo cambiaron de presentación.

| Pregunta | Resultado |
|---|---|
| ¿Los cálculos son dinámicos? | **Sí.** Ninguna cifra fija interviene en el cálculo o en las tablas |
| ¿Las fórmulas son correctas? | **Sí.** Sin inversión de períodos, errores de signo ni denominadores incorrectos |
| ¿Los datos coinciden con los estados originales? | **Sí.** 247 de 247 importes; 63 de 63 relaciones contables; 75 de 75 totales |
| ¿Los resultados coinciden con el documento? | **Sí.** 242 de 242 celdas de las Tablas 3 a 7; 62 de 62 cifras de la narrativa |
| ¿Son reproducibles de forma independiente? | **Sí.** 2,808 celdas reconstruidas en los tres niveles, sin diferencias |
| ¿Excel y PDF coinciden con la pantalla? | **Cifras: sí.** 52 de 2,190 celdas de Excel difieren solo en el formato |
| ¿Presentación libre de resultados engañosos? | **No en todos los niveles.** Véase AH-01 |

**Diferencias numéricas:** ninguna, ni atribuible a la aplicación ni al documento.

**Hallazgos:** 16, de los cuales 1 es alto, 4 medios, 8 bajos y 3 son observaciones documentales o de origen sin efecto en los cálculos.

**Hallazgo principal (AH-01).** Cuando un grupo de análisis no tiene cuentas en un ejercicio, la aplicación le asigna cero. Entre 2023 y 2024, 24 de los 73 grupos muestran −100.00 % con el sentido «Disminución» y otros 18 muestran base cero. Por ejemplo, «Cuentas por pagar comerciales» figura en −100.00 % porque en 2024 ese saldo se presenta como «Acreedores comerciales y otras cuentas por pagar». El total del pasivo corriente sí es correcto. Este nivel es además el único que incluyen las hojas interanuales de Excel y PDF.

**Situación:** nada se corrigió. Las correcciones de la sección 12 esperan autorización.

---

## 2. Archivos y funciones examinados

### Protección del proyecto (fase 0)

| Elemento | Valor |
|---|---|
| Ruta | `C:\Users\estua\Documents\ANF\appfinanciera\` |
| Rama | `correcciones-auditoria` |
| Commit | `4506ed8ff24906d44a3e7c22cba8e111094759db` |
| `git status` al iniciar | 44 archivos modificados y 12 sin seguimiento, todos anteriores a esta auditoría |
| `data/financiera.db` | `39ee373979fe9a72740c29e534ecdfe3e8c2ef0e145f7164c8b1a0675ebcba77` |
| `Trabajo de investigación ANF.md` | `5d5e316425292d83e65a436a8a167239dfb1e0daf669442bd20828b23156b80c` |
| `Trabajo de investigación ANF.pdf` | `f6b0bc64738fad2b3e014b68d1aba06387a38c32ae05bcbea4de7f435509d957` |
| `fuentes/alutech/estados_financieros_2021_2025.json` | `c96af696ca71a3700c5a01a7833399a878b729cb80d5d1d014cb2feee8310321` |
| `fuentes/anf/resultados_referencia.json` | `d545fe53866449d93ab48698609ce124b2861b7901193c68d9b6efaabd43cc2f` |
| `fuentes/anf/observaciones_validacion.json` | `2dd4dde804a708c108d12bc85077c9e190da66ced2720f6be421944dbbd599cb` |

Estados originales, en `documentos/`:

| Ejercicio | Archivo | Páginas leídas |
|---|---|---|
| 2021 | `Certificacin_EFC_Alutech_Divisin_Acero_2021VF_Mod010925.pdf` | 8, 9 y 10 |
| 2022 | `Certificacin_EFC_Alutech_Divisin_Acero_2022_VFMod_010925.pdf` | 8, 9 y 10 |
| 2023 | `Certificacin_EFC_Alutech_Divisin_Acero_2023_VFMod010925.pdf` | 6, 7, 8 y 9 |
| 2024 | `12_EEFF_diciembre_2024.pdf` (escaneado, sin capa de texto) | 1 y 2 |
| 2025 | `12_EEFF_diciembre_2025.pdf` | 1 y 2 |

### Código y pruebas

| Función | Ubicación |
|---|---|
| Rutas de las páginas | [app.py:61-63](app.py#L61-L63), [components/navigation.py:59-60](components/navigation.py#L59-L60) |
| Interfaz visible | `render_horizontal_balance` y `render_horizontal_resultados` en [reports/analisis_alutech.py:83-123](reports/analisis_alutech.py#L83-L123) |
| Interfaz oculta | `render_horizontal` en [reports/analisis_alutech.py:40-52](reports/analisis_alutech.py#L40-L52) (requiere `ANF_MENU_COMPLETO=1`) |
| Fórmulas | `variacion` en [calculations/comparativo.py:159-169](calculations/comparativo.py#L159-L169) |
| Filas por ejercicio | `_fila` en [calculations/comparativo.py:184-195](calculations/comparativo.py#L184-L195) |
| Niveles | `horizontal_conceptos`, `horizontal_grupos`, `horizontal_cuentas` y `horizontal_de_estado` en [calculations/comparativo.py:198-347](calculations/comparativo.py#L198-L347) |
| Comparar dos ejercicios | `dos_ejercicios`, `tendencia` y `_nota_dos_ejercicios` en [calculations/comparativo.py:295-372](calculations/comparativo.py#L295-L372) |
| Agregación | `DatosEjercicio` y `datos_ejercicio` en [calculations/rubros.py:195-301](calculations/rubros.py#L195-L301) |
| Totales | [calculations/balance_sheet.py:76-122](calculations/balance_sheet.py#L76-L122), [calculations/income_statement.py:87-164](calculations/income_statement.py#L87-L164) |
| Acceso a datos | `list_entries` y `list_fiscal_periods` en [database/repositories.py:362-372](database/repositories.py#L362-L372) |
| Modelos | `BalanceEntry`, `IncomeEntry`, `Account`, `FiscalPeriod` y `Centavos` en [database/models.py](database/models.py) |
| Tablas del reporte | [reports/secciones.py:180-265](reports/secciones.py#L180-L265) y [reports/secciones.py:349-392](reports/secciones.py#L349-L392) |
| Formato | `formatear` en [reports/secciones.py:63-83](reports/secciones.py#L63-L83) |
| Pantalla | `a_dataframe`, `mostrar_seccion` y `descargas` en [components/secciones_ui.py](components/secciones_ui.py) |
| Exportación | `secciones_a_excel` y `secciones_a_pdf` en [reports/exportar_secciones.py:93-227](reports/exportar_secciones.py#L93-L227) |
| Otro consumidor | [reports/informe_integral.py:34](reports/informe_integral.py#L34) (página oculta) |
| Pruebas | `tests/test_fase9_rubrica.py`, `tests/test_alutech.py`, `tests/test_fase10_metodologia.py`, `tests/test_fase1_paginas.py`, `tests/concordancia_documento.py`, `tests/humo_horizontal.py` |

### Secciones del documento

| Sección | Línea en el Markdown | Página del PDF | Contenido |
|---|---:|---:|---|
| 6.1–6.3 | 447–487 | 20–22 | Concepto, períodos y fórmulas |
| 6.4 | 489–543 | 22–26 | Tablas 3, 4 y 5 |
| 6.5 | 545–567 | 26–28 | Tabla 6 y subperíodos |
| 6.6 | 569–579 | 28 | Tabla 7 |
| 6.7–6.8 | 581–599 | 29–30 | Interpretación y conclusión |

---

## 3. Flujo de datos del análisis horizontal

```
Estados originales (PDF)
  │  transcripción con documento y página
  ▼
fuentes/alutech/estados_financieros_2021_2025.json
  │  scripts/cargar_alutech.py (carga única, con controles)
  ▼
SQLite: balance_entry, income_entry, account, fiscal_period
  │  list_entries (cada vez que se abre la página)
  ▼
compute_balance_sheet / compute_income_statement  →  subtotales y totales en memoria
  │
datos_ejercicio  →  DatosEjercicio: grupos, rubros y signos
  │
_fila + variacion  →  VA y VR sin redondear (Decimal)
  │
reports/secciones.py  →  Seccion: una sola estructura de celdas
  ├──► a_dataframe  →  pantalla
  ├──► secciones_a_excel  →  valor sin redondear + formato
  └──► secciones_a_pdf  →  texto formateado
```

### Mecanismos que intervienen

| Mecanismo | ¿Se usa? | Detalle |
|---|---|---|
| Datos de la base de datos | **Sí** | Son la única entrada numérica del cálculo |
| Valores introducidos a mano | Solo como entrada | Los importes se registran por carga o captura; no hay cifras en el cálculo |
| Valores derivados | **Sí** | Subtotales, rubros, CTN y variaciones |
| Resultados almacenados | **No** | Las tablas no guardan subtotales ni variaciones |
| Referencias del documento | **No en este apartado** | Solo los usa la página de validación; prueba P4 |

Los importes se almacenan como enteros de centavos y se operan con `Decimal`, sin coma flotante. El redondeo a dos decimales (mitad hacia arriba) ocurre solo al presentar. En Excel se conserva el valor sin redondear: por ejemplo, 85.91964755579929 con formato de dos decimales.

---

## 4. Fórmulas verificadas

| Fórmula | Implementación | Resultado |
|---|---|---|
| $VA = VP_t - VP_{t-1}$ | `absoluta = actual - anterior` | **Correcta** |
| $VR = (VP_t - VP_{t-1}) / VP_{t-1} × 100$ | `absoluta / anterior * CIEN` | **Correcta** |
| Par de ejercicios | `zip(lista, lista[1:])`, solo si `actual.anio == anterior.anio + 1` | **Correcto**, sin inversión |
| Saldos intermedios | Los subtotales se calculan antes de la variación | **Correcto** |
| CTN | AC − PC, luego las mismas fórmulas | **Correcto** |
| Sentido | Compara saldo actual y anterior | **Correcto** como aritmética; véase AH-01 |

La reconstrucción independiente no usó el código de la aplicación. Partió de una transcripción propia de los PDF y de una lectura directa de la base de datos, y usó fracciones exactas.

| Nivel | Filas | Celdas comprobadas | Diferencias |
|---|---:|---:|---:|
| Cuentas | 124 (106 con datos) | 1,612 | 0 |
| Grupos (sin `OTROS_NO_OPERATIVOS`) | 72 | 936 | 0 |
| Rubros y totales | 20 | 260 | 0 |
| **Total** | | **2,808** | **0** |

`OTROS_NO_OPERATIVOS` se comprobó aparte porque compara el neto con signo: de +55,570 a −811,571 equivale a −867,141 y −1560.45 %, igual que la aplicación.

---

## 5. Validación de los datos de entrada

### Método

Se leyeron como imagen las 14 páginas de los cinco estados. A partir de esa lectura se hizo una transcripción propia, independiente de la del proyecto, que se comparó con el JSON y con la base de datos.

| Prueba | Resultado |
|---|---|
| Importes: lectura propia = JSON = base de datos | **247 de 247** |
| Relaciones contables (sumas, A = P + Pat, cadena de resultados) | **63 de 63** |
| Totales de la aplicación = estados originales | **75 de 75** |
| Balance cuadrado según la aplicación | **5 de 5 ejercicios** |
| Importes en la base de datos sin respaldo en un estado | 18 ceros del catálogo estándar en 2021 (sin grupo, no afectan ningún total; AH-10) |

### Conceptos principales (USD)

| Concepto | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|---:|
| Activos corrientes | 383,881,547 | 448,672,401 | 429,794,544 | 432,771,678 | 247,705,981 |
| Activos no corrientes | 170,073,638 | 223,352,692 | 379,306,402 | 394,404,696 | 534,343,580 |
| **Total de activos** | **553,955,185** | **672,025,093** | **809,100,946** | **827,176,374** | **782,049,561** |
| Pasivos corrientes | 205,973,230 | 231,944,180 | 333,120,685 | 362,966,215 | 371,274,007 |
| Pasivos no corrientes | 202,660,765 | 226,204,149 | 248,306,867 | 238,148,371 | 179,615,356 |
| **Total de pasivos** | **408,633,995** | **458,148,329** | **581,427,552** | **601,114,586** | **550,889,363** |
| **Patrimonio** | **145,321,190** | **213,876,764** | **227,673,394** | **226,061,788** | **231,160,198** |
| Comprobación A − (P + Pat) | 0 | 0 | 0 | 0 | 0 |
| Ingresos ordinarios | 523,965,227 | 499,653,494 | 478,623,072 | 479,006,719 | 439,704,567 |
| Costo de ventas | 367,252,613 | 410,331,156 | 373,545,631 | 377,459,424 | 331,430,173 |
| Utilidad bruta | 156,712,614 | 89,322,338 | 105,077,441 | 101,547,295 | 108,274,394 |
| Gastos de operación (criterio de la Tabla 5) | 53,179,448 | 58,057,208 | 63,602,388 | 66,353,377 | 53,608,750 |
| Resultado operativo | 103,578,903 | 31,200,977 ¹ | 44,689,021 ¹ | 35,193,918 | 54,665,644 |
| Ingresos financieros | neto ² | neto ² | neto ² | 15,024,973 | 14,515,895 |
| Gastos financieros | 21,777,725 ² | 17,181,342 ² | 22,016,927 ² | 43,089,283 | 51,914,906 |
| Otros ingresos (gastos) después de operación | — | — | — | 55,570 | (811,571) |
| Utilidad antes de impuestos | 81,801,178 | 14,019,635 | 22,672,094 | 7,185,178 | 16,455,062 |
| Impuesto sobre la renta | 13,198,439 | 3,960,325 | 9,341,414 | 4,124,197 | 4,556,075 |
| **Utilidad neta** | **68,602,739** | **10,059,310** | **13,330,680** | **3,060,981** | **11,898,987** |

¹ No impreso en esos estados; se obtiene de las partidas impresas y es coherente con la utilidad antes de impuestos impresa.
² Los estados de 2021–2023 solo presentan «Gastos financieros (neto)».

El Anexo C lista las 106 cuentas individuales con su procedencia.

### Cambios de nombre, agrupación y clasificación

| Situación | 2021–2023 | 2024–2025 | Tratamiento en la aplicación |
|---|---|---|---|
| Códigos de cuenta | Familia `CB…` | Familia `CN…` | Sin enlace en el nivel de cuentas: «Aparece» o «Desaparece» (correcto) |
| Cuentas por cobrar | Comerciales y otras, separadas | Una sola línea | Tabla 3 con comerciales; Tabla 4 con ambas, y lo advierte (correcto) |
| Cuentas por pagar | Comerciales y otras, separadas | Una sola línea | Comparadas por separado; AH-01 |
| Intangibles | Intangibles y plusvalía, separados | Solo «Activos intangibles» | Comparados por separado: +2,588.44 % y −100 %; AH-01 |
| Títulos | Bonos, certificados y titularizaciones | «Obligaciones Emisión de Títulos valores» | Comparados por separado; AH-01 |
| Inversiones no corrientes | Certificados de depósito y acciones | «Inversiones» | Comparados por separado; AH-01 |
| Patrimonio: resultados | Acumulados incluyen el resultado del año | Acumulados y del período, separados | Comparados por separado; AH-01 |
| CxC a largo plazo | 2023: «partes relacionadas» y «otras» | 2024: «Otras cuentas por cobrar a LP»; 2025: «Empresas Relacionadas a LP» | Se respeta la denominación impresa: +12,744.65 % en 2023–24; AH-01 |
| Gastos | Administración y venta | Se suman personal y depreciación | Total comparable en la Tabla 5, con nota; por separado, AH-01 |
| Utilidad operativa | Incluye otros ingresos y deterioro | Otros, después de operación | Nota parcial; AH-06 |
| Gastos financieros | Neto impreso | Gastos − ingresos | Rubro neto homogéneo (correcto) |
| «Otros Ingresos (Gastos)» | — | La misma línea, en `CN7201` y `CN7202` según su signo | Correcto en el nivel de grupos; AH-11 en el de cuentas |

### Observación sobre el origen

**Capital social 2024.** El estado de 2024 imprime 119,391,833; los de 2022, 2023 y 2025 imprimen 119,389,833. La cifra de 2024 suma correctamente con el total de patrimonio impreso (226,061,788), así que no es un error de transcripción. La diferencia produce variaciones de +2,000 y −2,000, sin efecto práctico. No se ajustó (AH-15).

**Alcance de los documentos.** Cada PDF presenta un solo ejercicio, sin cifras comparativas, por lo que no puede detectarse ninguna reexpresión de saldos anteriores. Los de 2024 y 2025 tienen dos páginas, sin notas ni dictamen, y están firmados por el representante legal y el contador general.

---

## 6. Resultados de la comparación 2021–2025

La comparación se hizo celda por celda entre tres fuentes: el texto de pantalla de la aplicación, la celda del Markdown y la reconstrucción independiente. El Anexo A presenta la tabla de auditoría completa, con 68 filas.

| Tabla | Saldos | VA | VR | Otras | Total | Coinciden |
|---|---:|---:|---:|---:|---:|---:|
| 3. Balance 2021–2023 | 24 | 16 | 16 | 0 | 56 | 56 |
| 4. Balance 2023–2025 | 24 | 16 | 16 | 0 | 56 | 56 |
| 5. Resultados 2021–2025 | 35 | no se publica | 28 | 0 | 63 | 63 |
| 6. Capital de trabajo | 15 | 4 | 4 | 12 (razones y «Base») | 35 | 35 |
| 7. Resumen del CTN | 24 | 4 | 4 | 0 | 32 | 32 |
| **Total** | **122** | **40** | **68** | **12** | **242** | **242** |

### Clasificación

| Clase | Cantidad | Detalle |
|---|---:|---|
| Coincidencia exacta | **242** | Tablas 3 a 7 |
| Coincidencia exacta en la narrativa | **62** | 6.5, 6.7 y 6.8 (Anexo B) |
| Diferencia de redondeo | 0 | |
| Diferencia de datos de origen | 0 | |
| Diferencia de fórmula | 0 | |
| Diferencia de período | 0 | |
| Diferencia de clasificación contable | 0 | Hay limitaciones de comparabilidad compartidas por ambos (AH-06) |
| Diferencia atribuible al software | 0 | |
| Resultado derivado no publicado | 28 + detalle | VA de la Tabla 5, razón de tesorería de la Tabla 6 y niveles de grupos y cuentas |
| No aplicable | — | Niveles que el documento no presenta |

Ambos resultados se comprobaron contra los estados originales y las fórmulas, de modo que la coincidencia no se tomó por sí misma como prueba de corrección.

**PDF del documento.** Las 240 celdas numéricas de las Tablas 3 a 7 del Markdown aparecen en las páginas correspondientes del PDF. Esta prueba comprueba su presencia, no su posición dentro de la tabla.

---

## 7. Diferencias entre aplicación y documento

No hay diferencias numéricas. Las diferencias son de método o de presentación:

| # | Diferencia | Aplicación | Documento | Cuál debe prevalecer |
|---|---|---|---|---|
| 1 | Base negativa | No calcula el porcentaje | 6.3 dice que debe «interpretarse con cautela», lo que supone calcularlo | **Aplicación.** Ajustar la frase de 6.3. Sin efecto numérico: ninguna tabla tiene base negativa |
| 2 | Cambio de positivo a negativo (CTN 2024–25) | −277.02 %, sin advertencia en las Tablas 6 y 7 | −277.02 %, sin advertencia | **Ambos** deben añadir una nota (AH-04) |
| 3 | VA en la Tabla 5 | La muestra | No la publica | **Ninguna diferencia de resultado.** Decidir si se publica (D-3) |
| 4 | Otras columnas | Razón de tesorería en la Tabla 6 | No la incluye | Derivado no publicado, sin conflicto |
| 5 | Niveles de detalle | Rubros, grupos y cuentas | Solo las tablas | Ampliación de la aplicación |
| 6 | Denominaciones | «Utilidad de operación», «Utilidad neta del ejercicio» | «Utilidad operativa», «Utilidad neta del año» | Sin efecto; puede unificarse |

### Observaciones sobre el documento, sin efecto en sus cifras

| # | Ubicación | Observación |
|---|---|---|
| a | PDF, pág. 22 | El título dice «6.4 Análisis horizontal del estado de resultados», mientras que el Markdown dice «…del estado de situación financiera y del estado de resultados». La sección abre con la situación financiera |
| b | PDF, págs. 21–22 | Los subíndices de las fórmulas se ven como un recuadro vacío («V□»), por lo que la fórmula queda ilegible |
| c | PDF, pág. 22 | Se lee «2021-20252» en lugar de «2021-2025.» |
| d | PDF, Tabla 3 | Las cifras se parten en dos líneas («10,840,8 / 65»), lo que dificulta leerlas |
| e | 6.5, primer párrafo | «Déficit operativo de corto plazo» y «modelo holgado de liquidez» van más allá de lo que muestra el dato: el CTN es negativo en 2025, pero el resultado de operación es positivo |

---

## 8. Verificación de cálculos dinámicos

Las pruebas se hicieron sobre copias de la base de datos, comparando una fotografía de **3,193 celdas** antes y después de cada cambio.

| Prueba | Cambio | Resultado |
|---|---|---|
| **P1** | Inventarios 2022 +1,000,000 | Cambian 75 celdas: solo 2022 y las comparaciones 21–22 y 22–23. Tablas 4 y 5 intactas |
| **P2** | Costo de ventas 2024 +500,000 | Cambian 93 celdas: solo 2024 y las comparaciones 23–24 y 24–25. Balance intacto |
| **P3** | Editar y restaurar | **0 diferencias** |
| **P4** | Registrar los archivos abiertos al calcular y presentar | **Ningún JSON ni archivo de `fuentes/`**. Sin el archivo de referencias: 0 celdas distintas |
| **P5** | Base cero, base negativa y cuenta sin importe en 2022 | «—» y sin error; revela AH-01 y AH-05 |
| **P6** | Sin datos de 2022 | Sin error; revela AH-08 y AH-12 |
| **P7** | Pantalla real tras el cambio de P1 | La pantalla muestra los valores nuevos; revela AH-07 |

### Detalle de P1 y P2: aplicación contra cálculo independiente

| Celda | Antes | Después | Independiente |
|---|---:|---:|---:|
| Inventarios, VA 21–22 | −7,371,062 | −6,371,062 | −6,371,062 |
| Inventarios, VR 21–22 | −4.97 % | −4.29 % | −4.29 % |
| Inventarios, VA 22–23 | +421,877 | −578,123 | −578,123 |
| Inventarios, VR 22–23 | +0.30 % | −0.41 % | −0.41 % |
| Activo corriente, VR 22–23 | −4.21 % | −4.42 % | −4.42 % |
| Costo de ventas, VR 23–24 | +1.05 % | +1.18 % | +1.18 % |
| Costo de ventas, VR 24–25 | −12.19 % | −12.31 % | −12.31 % |
| Utilidad operativa, VR 24–25 | +55.33 % | +57.57 % | +57.57 % |
| Utilidad neta, VR 24–25 | +288.73 % | +364.63 % | +364.63 % |

### Cifras fijas identificadas

| Tipo | Ubicación | ¿Sustituye un cálculo? |
|---|---|---|
| Datos financieros de entrada | Base de datos, cargada desde `fuentes/alutech/*.json` | No: es la entrada |
| Valores de referencia para validación | `fuentes/anf/resultados_referencia.json` (Tablas 3–7), leído en [calculations/comparacion_anf.py:44](calculations/comparacion_anf.py#L44) | **No** (P4) |
| Observaciones de validación | `fuentes/anf/observaciones_validacion.json` | No |
| Parámetros metodológicos | `CLAVES_TABLA_3/4/5`, definición de rubros y grupos | Son criterios; no contienen importes |
| Textos con años | Notas de [reports/secciones.py:174-177](reports/secciones.py#L174-L177) y 232-239 | No: texto explicativo |
| Cifras dentro de texto | [reports/indicadores_financieros.py:87-88](reports/indicadores_financieros.py#L87-L88) (otra página) | No: nota sobre la base de CxC, que no se recalcula si cambian los datos |
| Pruebas | `tests/` | No: solo se usan al probar |

La búsqueda de números de siete o más cifras en `app.py`, `calculations/`, `components/`, `modules/` y `reports/` no halló ningún resultado financiero fijo.

### Suite de pruebas en copia aislada

**695 de 695 pruebas aprobadas.** La base de datos real no se tocó.

---

## 9. Tratamiento de casos especiales

| Caso | VA | VR | Sentido | Observación mostrada | Evaluación |
|---|---|---|---|---|---|
| Anterior = 0 | Sí | «—» | Aumento o Disminución | Base cero, no se puede calcular | **Correcto** |
| Ambos = 0 | +0 | «—» | Fila omitida | — | **Correcto** |
| Anterior negativo, actual menos negativo | Sí | «—» | Aumento | Base negativa, usar VA | **Correcto** |
| Ambos negativos, más negativo | Sí | «—» | Disminución | Base negativa, usar VA | **Correcto** |
| Positivo → negativo | Sí | Calculada (−150 %) | Disminución | Cambia de signo, con cautela | **Correcto** en la comparación; sin nota en las Tablas 6–7 (AH-04) |
| Negativo → positivo | Sí | «—» | Aumento | «Interpretar el porcentaje con cautela» | **Incoherente**: no hay porcentaje (AH-05) |
| Positivo → 0 | Sí | −100 % | Disminución | — | **Correcto** si el cero existe |
| Valor no disponible | «—» | «—» | Aparece o Desaparece | No se presenta en ese año | **Correcto** |
| Cuenta en un año y no en otro | «—» | «—» | Aparece o Desaparece | No se presenta | **Correcto en cuentas; incorrecto en grupos** (AH-01) |
| Cambio de clasificación | — | — | — | Nota general de 2023–2024 | **Insuficiente** (AH-01 y AH-03) |
| Ejercicio intermedio faltante | «—» | «—» | — | No visible en las tablas | **Insuficiente** (AH-08) |
| Redondeo | Sin redondeo al operar | 2 decimales al presentar | — | — | **Correcto** |

No se generan porcentajes infinitos ni errores de división en ningún caso.

### Casos reales en los datos

| Partida | Par | Valores | VR de la aplicación | Lectura |
|---|---|---|---|---|
| Otras reservas de capital | 21–22, 22–23 | Ambos negativos | «—» | Correcta |
| Efecto de conversión | 24–25 | −8,973,683 → −16,976,702 | «—» | Correcta |
| Capital de trabajo neto | 24–25 | +69,805,463 → −123,568,026 | −277.02 % | Numéricamente válida; económicamente, cambio de signo |
| Otros ingresos (gastos) | 24–25 | +55,570 → −811,571 | −1560.45 % | Válida con la advertencia mostrada; base muy pequeña |
| Utilidad neta | 24–25 | 3,060,981 → 11,898,987 | +288.73 % | Válida; base pequeña |
| CxC comerciales (línea presentada) | 23–24 | 41,272,525 → 97,204,415 | +135.52 % | Numéricamente válida; **no comparable** (AH-03) |
| Cuentas por pagar comerciales | 23–24 | 195,599,671 → 0 | −100.00 % | **Engañosa** (AH-01) |
| Otras CxC no corrientes | 23–24 | 924,000 → 118,684,551 | +12,744.65 % | **No interpretable** por cambio de denominación (AH-01) |

---

## 10. Auditoría de presentación

| # | Aspecto | Evaluación | Nota |
|---|---|---|---|
| 1 | Claridad de las columnas | **Bien** | Encabezados con período: «Var. abs. 21–22» |
| 2 | Identificación de los períodos | **Bien**, con un detalle | El selector dice «2024 vs 2023» y la Tabla 7, «2023 vs 2024». Ambos se entienden |
| 3 | Variaciones absolutas | **Bien** | Con signo en las páginas visibles |
| 4 | Variaciones porcentuales | **Bien** | Con signo y dos decimales |
| 5 | Signos | **Bien**, con un detalle | «+0» y «+0.00 %» en saldos sin cambio sugieren un aumento (AH-09) |
| 6 | Miles y decimales | **Bien**, con un detalle | Formato igual al documento. «+12744.65%» no lleva separador de miles |
| 7 | Porcentajes y redondeo | **Bien** | Redondeo solo al presentar |
| 8 | Nulos y no calculables | **Mejorable** | «—» reúne varias causas; solo la comparación de dos ejercicios las explica fila por fila (AH-08) |
| 9 | Orden y agrupación | **Bien** | Orden del documento y del estado |
| 10 | Coherencia BG y ER | **Bien**, con un detalle | La Tabla 5 agrupa las columnas de forma distinta a las Tablas 3 y 4, igual que el documento |

### Pantalla, Excel y PDF

| Comparación | Celdas | Iguales | Diferencias |
|---|---:|---:|---|
| Pantalla real (AppTest) contra secciones | 1,489 | 1,489 | Ninguna |
| Excel contra pantalla | 2,190 | 2,138 | 52 de formato; ninguna cifra |
| PDF contra pantalla (presencia del texto de cada celda) | 2,190 | 2,190 | Ninguna; las notas también aparecen |

Las 52 diferencias de Excel son: 31 celdas «—» que quedan vacías, 11 «+0.00%» que se muestran como «0.00%» y 10 «+0» que se muestran como «0».

**Alcance de las descargas.** Las hojas interanuales de Excel y PDF son siempre de nivel «grupos», sea cual sea el nivel elegido en pantalla (AH-02).

**Sin excepciones en pantalla.** Las cinco vistas abiertas se presentaron sin errores y con botones de descarga.

---

## 11. Problemas encontrados

Severidad: **Alta** puede llevar a una conclusión financiera equivocada; **Media** puede confundir en un caso real; **Baja** es de claridad, robustez o de un caso que hoy no ocurre.

| ID | Sev. | Problema | Evidencia | Atribuible a |
|---|---|---|---|---|
| **AH-01** | **Alta** | Un grupo sin cuentas se trata como cero. Produce −100 %, «Disminución» y base cero por cambios de presentación. El título dice «cuentas comparables entre ejercicios» | [comparativo.py:108-110](calculations/comparativo.py#L108-L110), [rubros.py:218-219](calculations/rubros.py#L218-L219), [secciones.py:153](reports/secciones.py#L153). 54 pares afectados, 44 en 2023–24 | Aplicación |
| **AH-02** | Media | Las hojas interanuales de las descargas son siempre de «grupos», por lo que difunden AH-01 y no siguen la selección de pantalla | [analisis_alutech.py:79-80](reports/analisis_alutech.py#L79-L80) | Aplicación |
| **AH-03** | Media | La nota de una partida no homogénea no llega a «Comparar dos ejercicios». CxC comerciales 2023–24: +135.52 % sin observación en la fila | [comparativo.py:368-371](calculations/comparativo.py#L368-L371), [rubros.py:149-152](calculations/rubros.py#L149-L152) | Aplicación |
| **AH-04** | Media | Las Tablas 6 y 7 presentan −277.02 % sin advertir el cambio de signo | [secciones.py:365-370](reports/secciones.py#L365-L370), [secciones.py:387-391](reports/secciones.py#L387-L391) | Aplicación y documento |
| **AH-06** | Media | La utilidad operativa no es homogénea en 2023–24: −21.25 %; sin otros ingresos en 2023 sería −14.09 %. La nota actual no lo dice expresamente | [secciones.py:234-237](reports/secciones.py#L234-L237); nota de la Tabla 5 | Aplicación y documento |
| **AH-05** | Baja | Con cambio de negativo a positivo se pide «interpretar el porcentaje con cautela», pero no hay porcentaje y se pierde la causa real. Sin casos en los datos | [comparativo.py:355-356](calculations/comparativo.py#L355-L356); P5 | Aplicación |
| **AH-07** | Baja | Las páginas del apartado no avisan si el balance no cuadra o está incompleto. En P1, con diferencia de 1,000,000, no hubo aviso | [analisis_alutech.py:88](reports/analisis_alutech.py#L88); P7 | Aplicación |
| **AH-08** | Baja | «—» reúne causas distintas y no dice «No calculable». En las tablas, un año faltante no se explica | [secciones.py:64-65](reports/secciones.py#L64-L65), [secciones.py:193-198](reports/secciones.py#L193-L198); P6 | Aplicación |
| **AH-09** | Baja | «+0» y «+0.00 %» en saldos sin cambio; Excel los muestra sin signo y deja vacío «—» | [secciones.py:70-74](reports/secciones.py#L70-L74), [exportar_secciones.py:67](reports/exportar_secciones.py#L67) | Aplicación |
| **AH-10** | Baja | La página oculta muestra 18 filas vacías, procedentes de los ceros de 2021, y variaciones sin signo | [comparativo.py:250-254](calculations/comparativo.py#L250-L254), [secciones.py:156](reports/secciones.py#L156) | Aplicación |
| **AH-11** | Baja | En el nivel de cuentas, «Otros Ingresos (Gastos)» 2024–25 aparece como dos cuentas que «Desaparece» y «Aparece» en vez de una variación de −867,141 | `CN7201` y `CN7202`. El nivel de grupos sí lo compara | Aplicación |
| **AH-12** | Baja | Las Tablas 3 y 4 se forman por posición (`anios[:3]`, `anios[2:]`). Sin 2022, se titula «Tabla 3 (2021–2024)». Sin efecto hoy | [secciones.py:205-218](reports/secciones.py#L205-L218); P6 | Aplicación |
| **AH-16** | Baja | Las pruebas no cubren AH-01: al simular su corrección en una copia, las 695 siguen aprobadas | Simulación aislada; [test_fase9_rubrica.py:187-232](tests/test_fase9_rubrica.py#L187-L232) | Pruebas |
| **AH-13** | Obs. | Defectos del PDF del documento y frase de 6.3 (sección 7) | PDF, págs. 21–22; Markdown, línea 487 | Documento |
| **AH-14** | Obs. | El JSON describe los estados de 2022 y 2023 como auditados por PwC; las certificaciones dicen KPMG. No interviene en ningún cálculo | `documentos` del JSON; certificaciones | Metadatos |
| **AH-15** | Obs. | Capital social 2024: +2,000 respecto de los demás años, según lo impreso | Estado de 2024, pág. 1 | Origen |

### Detalle de AH-01

| Par | Grupos | Sin cuentas en un ejercicio | Muestran −100 % | Muestran base cero |
|---|---:|---:|---:|---:|
| 2021–2022 | 73 | 3 | 0 | 3 |
| 2022–2023 | 73 | 5 | 0 | 5 |
| **2023–2024** | **73** | **44** | **24** | **18** |
| 2024–2025 | 73 | 2 | 1 | 1 |

Los otros dos casos de 2023–2024 son «Otras reservas de capital» (base negativa, sin porcentaje) y «Participaciones no controladoras» (cero en ambos ejercicios, fila omitida). Fuera de 2023–2024, un grupo sin cuentas puede corresponder a una partida que realmente no existía, pero la ausencia sigue sin ser un cero informado por el estado.

El efecto de este hallazgo se suma al de partidas que sí tienen datos en ambos ejercicios, pero que cambiaron de contenido. Intangibles (+2,588.44 %), Otras CxC no corrientes (+12,744.65 %), Administración (−69.98 %) y Venta (−39.98 %) no se resuelven solo con la corrección de AH-01 y requieren una nota o una agrupación homogénea.

Comparaciones ilustrativas con agrupación por denominación (su equivalencia no puede comprobarse sin notas):

| Agrupación | 2023 | 2024 | Nivel de grupos hoy | Agrupada |
|---|---:|---:|---|---:|
| Intangibles + plusvalía | 36,707,629 | 38,005,433 | +2,588.44 % y −100 % | **+3.54 %** |
| CxC comerciales + otras | 96,097,483 | 97,204,415 | −100 %, −100 % y base cero | **+1.15 %** |
| CxP comerciales + otras | 207,727,338 | 225,126,517 | −100 %, −100 % y base cero | **+8.38 %** |
| Bonos + certificados + titularización (corrientes) | 12,275,055 | 13,447,268 | −100 % ×3 y base cero | **+9.55 %** |
| Ídem (no corrientes) | 63,318,735 | 68,067,653 | −100 % ×3 y base cero | **+7.50 %** |
| Resultados acumulados + del período | 47,852,456 | 48,584,188 | −4.87 % y base cero | **+1.53 %** |

---

## 12. Correcciones recomendadas

Ninguna se ha aplicado. Se autorizan por número.

### Aplicación

| # | Corrige | Propuesta | Beneficio |
|---|---|---|---|
| **R-1** | AH-01 | Devolver «sin dato» cuando un grupo no tiene cuentas, en vez de cero; cambiar el título que afirma que es comparable | Las partidas pasan a «Aparece» o «Desaparece». Simulado en copia: 695 de 695 pruebas aprobadas; no altera Tablas 3–7 |
| **R-2** | AH-01 | Añadir filas de agrupación homogénea en el nivel de grupos, marcadas como agrupación por denominación | Permite leer 2023–2024 con cifras comparables. **Requiere D-1** |
| **R-3** | AH-02 | Elegir el nivel de las hojas interanuales o incluir los tres; como mínimo, hacerlo tras R-1 | El archivo coincide con lo que se ve |
| **R-4** | AH-03 | Llevar la nota de la partida a la observación de la fila | Advierte de +135.52 % donde se lee |
| **R-5** | AH-04, AH-05 | Añadir nota de cambio de signo en las Tablas 6 y 7; separar los mensajes de negativo a positivo | Evita leer −277.02 % como una simple caída |
| **R-6** | AH-08 | Sustituir «—» por «No calculable» o «Sin dato», según la causa; mantener la causa en notas | Cumple el criterio solicitado |
| **R-7** | AH-06 | Añadir a la Tabla 5 una nota expresa sobre la utilidad operativa 2023–2024 | Declara el límite de comparación |
| **R-8** | AH-07 | Mostrar un aviso si un ejercicio no cuadra o está incompleto | Evita analizar datos inconsistentes |
| **R-9** | AH-09 | Mostrar saldo sin cambio como «0» y «0.00 %»; igualar Excel a la pantalla, incluidos los «no calculables» | Uniformidad entre formatos |
| **R-10** | AH-10, AH-11, AH-12 | Quitar filas vacías; unir cuentas `CN7201` y `CN7202` en la presentación; formar las tablas por año | Robustez; sin efecto en las cifras actuales |

### Documento

| # | Corrige | Propuesta |
|---|---|---|
| **R-11** | Sección 7, 1 | Ajustar la frase de 6.3 sobre la base negativa: no se calcula porcentaje |
| **R-12** | AH-04 | Añadir nota al −277.02 % en las Tablas 6 y 7 |
| **R-13** | AH-06 | Añadir la nota sobre la utilidad operativa en 2023–2024 |
| **R-14** | AH-13 | Corregir el título de 6.4, las fórmulas, «20252» y el ancho de las columnas al regenerar el PDF |
| **R-15** | — | Incorporar la descripción académica aprobada |

### Datos

| # | Corrige | Propuesta |
|---|---|---|
| **R-16** | AH-14 | Corregir los auditores de 2022 y 2023 en los metadatos del JSON (solo el texto, sin tocar ningún importe) |

### Decisiones académicas

| # | Decisión | Mi recomendación |
|---|---|---|
| **D-1** | ¿Se publican agrupaciones homogéneas para 2023–2024, aun sin notas que las respalden? | Sí, en la aplicación y marcadas como tales; en el documento, solo si el análisis las cita |
| **D-2** | ¿Se mantiene la Tabla 3 con la línea comercial o se adopta la base B2? | Resolver junto con la decisión pendiente de `INFORME_AUDITORIA_PREVIA_CORRECCIONES_ANF.md`. Con B2, la Tabla 3 cambiaría a −27.94 % y +13.03 % |
| **D-3** | ¿Se añade la variación absoluta a la Tabla 5 del documento? | Sí: 6.3 la define y la aplicación ya la calcula |
| **D-4** | Capital social 2024: ¿solo informar o consultar a la empresa? | Informar y conservar la cifra impresa |

---

## 13. Pruebas necesarias

Si se autorizan las correcciones, deberían añadirse las siguientes:

| # | Prueba | Protege |
|---|---|---|
| 1 | Un grupo sin cuentas en un ejercicio da «sin dato», no cero, y el sentido es «Aparece» o «Desaparece» | R-1 |
| 2 | Un grupo con cero registrado (`CB3107` en 2023) sigue siendo cero | R-1 |
| 3 | Ninguna fila 2023–2024 del nivel de grupos muestra −100 % por ausencia | R-1 |
| 4 | Los totales de los niveles de grupos y cuentas siguen cuadrando | R-1 |
| 5 | Las Tablas 3 a 7 siguen coincidiendo con las 242 celdas | R-1 a R-10 |
| 6 | Cada agrupación homogénea suma sus componentes | R-2 |
| 7 | Las descargas contienen el nivel elegido | R-3 |
| 8 | La fila de CxC 2023–24 trae su observación | R-4 |
| 9 | Las Tablas 6 y 7 traen la nota de cambio de signo solo en 2024–25 | R-5 |
| 10 | De negativo a positivo, el mensaje no menciona un porcentaje | R-5 |
| 11 | Cada causa muestra su texto, en pantalla, Excel y PDF | R-6, R-9 |
| 12 | Saldo sin cambio: «0» y «0.00 %» en los tres formatos | R-9 |
| 13 | Aviso cuando el balance no cuadra, y sin aviso con los datos reales | R-8 |
| 14 | Editar un saldo cambia solo sus ejercicios y comparaciones (P1 y P2 como prueba permanente) | Dinamismo |
| 15 | Las páginas no abren archivos JSON de referencia al calcular (P4 como prueba permanente) | Separación de referencias |

---

## 14. Conclusión sobre la confiabilidad del apartado

| Criterio de aceptación | Resultado | Fundamento |
|---|---|---|
| Los datos provienen de los estados originales | **Cumplido** | 247 de 247 importes; 63 de 63 relaciones |
| Las variaciones usan fórmulas correctas | **Cumplido** | Sección 4 |
| Los cálculos se actualizan al cambiar los datos | **Cumplido** | P1, P2, P3 y P7 |
| Los resultados son reproducibles de forma independiente | **Cumplido** | 2,808 celdas sin diferencias |
| Aplicación y documento coinciden, o se justifica | **Cumplido** | 242 de 242 y 62 de 62; diferencias de método en la sección 7 |
| La descripción refleja el procedimiento implementado | **Cumplido** | Depende de R-1 solo en lo señalado en sus notas |
| Limitaciones y excepciones documentadas | **Cumplido** | Secciones 5, 9 y 11; descripción académica |
| Sin resultados engañosos | **Cumplido en Tablas 3–7, rubros y cuentas. No cumplido en grupos** | AH-01 |

**Puede usarse sin reservas:** las Tablas 3 a 7, el nivel de rubros con la excepción de CxC comerciales 2023–24 (AH-03) y el nivel de cuentas con la excepción de «Otros Ingresos (Gastos)» 2024–25 (AH-11).

**Debe corregirse antes de citarse:** el nivel de grupos en 2023–2024 y sus hojas de Excel y PDF.

**Limitaciones de esta auditoría.** Las transcripciones de los estados se apoyan en la lectura de imágenes y se confirmaron con los subtotales impresos. No pudo comprobarse la composición de las líneas de 2024 y 2025 porque esos documentos no incluyen notas. La comparación con el PDF exportado comprueba la presencia del texto de cada celda, no su posición. No se realizó una prueba con un navegador real; la pantalla se verificó con el marco de pruebas de Streamlit (AppTest).

**Elementos usados fuera del proyecto.** Copias y resultados intermedios se guardaron en la carpeta temporal de la sesión. Para ver los PDF se instaló temporalmente PyMuPDF en `C:\Temp\anfpdf`, fuera del proyecto y de su entorno virtual.

---

## Anexo A. Comparación celda por celda con el documento (Tablas 3 a 7)

Cada fila reúne, para un par de ejercicios, la variación de la pantalla de la aplicación y la publicada en el documento. Los dos resultados se contrastaron además con una reconstrucción independiente hecha desde los estados originales. VA = variación absoluta; VR = variación relativa.

| Estado financiero | Cuenta | Año anterior | Año actual | VA app | VA documento | VR app | VR documento | Resultado |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Balance General (Tabla 3) | Efectivo y Equivalentes | 2021 | 2022 | +9,314,433 | +9,314,433 | +85.92% | +85.92% | Coincidencia exacta |
| Balance General (Tabla 3) | Efectivo y Equivalentes | 2022 | 2023 | -8,025,092 | -8,025,092 | -39.82% | -39.82% | Coincidencia exacta |
| Balance General (Tabla 3) | Cuentas por Cobrar Com. | 2021 | 2022 | -20,499,996 | -20,499,996 | -38.62% | -38.62% | Coincidencia exacta |
| Balance General (Tabla 3) | Cuentas por Cobrar Com. | 2022 | 2023 | +8,691,433 | +8,691,433 | +26.68% | +26.68% | Coincidencia exacta |
| Balance General (Tabla 3) | Inventarios (Neto) | 2021 | 2022 | -7,371,062 | -7,371,062 | -4.97% | -4.97% | Coincidencia exacta |
| Balance General (Tabla 3) | Inventarios (Neto) | 2022 | 2023 | +421,877 | +421,877 | +0.30% | +0.30% | Coincidencia exacta |
| Balance General (Tabla 3) | Total Activo Corriente | 2021 | 2022 | +64,790,854 | **+64,790,854** | +16.88% | **+16.88%** | Coincidencia exacta |
| Balance General (Tabla 3) | Total Activo Corriente | 2022 | 2023 | -18,877,857 | **-18,877,857** | -4.21% | **-4.21%** | Coincidencia exacta |
| Balance General (Tabla 3) | Total Pasivo Corriente | 2021 | 2022 | +25,970,950 | **+25,970,950** | +12.61% | **+12.61%** | Coincidencia exacta |
| Balance General (Tabla 3) | Total Pasivo Corriente | 2022 | 2023 | +101,176,505 | **+101,176,505** | +43.62% | **+43.62%** | Coincidencia exacta |
| Balance General (Tabla 3) | Total Activo | 2021 | 2022 | +118,069,908 | +118,069,908 | +21.31% | +21.31% | Coincidencia exacta |
| Balance General (Tabla 3) | Total Activo | 2022 | 2023 | +137,075,853 | +137,075,853 | +20.40% | +20.40% | Coincidencia exacta |
| Balance General (Tabla 3) | Total Pasivo | 2021 | 2022 | +49,514,334 | +49,514,334 | +12.12% | +12.12% | Coincidencia exacta |
| Balance General (Tabla 3) | Total Pasivo | 2022 | 2023 | +123,279,223 | +123,279,223 | +26.91% | +26.91% | Coincidencia exacta |
| Balance General (Tabla 3) | Total Patrimonio | 2021 | 2022 | +68,555,574 | +68,555,574 | +47.18% | +47.18% | Coincidencia exacta |
| Balance General (Tabla 3) | Total Patrimonio | 2022 | 2023 | +13,796,630 | +13,796,630 | +6.45% | +6.45% | Coincidencia exacta |
| Balance General (Tabla 4) | Efectivo y equivalentes | 2023 | 2024 | +3,652,051 | +3,652,051 | +30.11% | +30.11% | Coincidencia exacta |
| Balance General (Tabla 4) | Efectivo y equivalentes | 2024 | 2025 | -3,231,172 | −3,231,172 | -20.47% | −20.47% | Coincidencia exacta |
| Balance General (Tabla 4) | Cuentas por cobrar comerciales y otras cuentas por cobrar | 2023 | 2024 | +1,106,932 | +1,106,932 | +1.15% | +1.15% | Coincidencia exacta |
| Balance General (Tabla 4) | Cuentas por cobrar comerciales y otras cuentas por cobrar | 2024 | 2025 | -27,034,533 | −27,034,533 | -27.81% | −27.81% | Coincidencia exacta |
| Balance General (Tabla 4) | Inventarios (neto) | 2023 | 2024 | -24,730,008 | −24,730,008 | -17.48% | −17.48% | Coincidencia exacta |
| Balance General (Tabla 4) | Inventarios (neto) | 2024 | 2025 | -46,943,251 | −46,943,251 | -40.20% | −40.20% | Coincidencia exacta |
| Balance General (Tabla 4) | Total activo corriente | 2023 | 2024 | +2,977,134 | +2,977,134 | +0.69% | +0.69% | Coincidencia exacta |
| Balance General (Tabla 4) | Total activo corriente | 2024 | 2025 | -185,065,697 | −185,065,697 | -42.76% | −42.76% | Coincidencia exacta |
| Balance General (Tabla 4) | Total pasivo corriente | 2023 | 2024 | +29,845,530 | +29,845,530 | +8.96% | +8.96% | Coincidencia exacta |
| Balance General (Tabla 4) | Total pasivo corriente | 2024 | 2025 | +8,307,792 | +8,307,792 | +2.29% | +2.29% | Coincidencia exacta |
| Balance General (Tabla 4) | Total activo | 2023 | 2024 | +18,075,428 | +18,075,428 | +2.23% | +2.23% | Coincidencia exacta |
| Balance General (Tabla 4) | Total activo | 2024 | 2025 | -45,126,813 | −45,126,813 | -5.46% | −5.46% | Coincidencia exacta |
| Balance General (Tabla 4) | Total pasivo | 2023 | 2024 | +19,687,034 | +19,687,034 | +3.39% | +3.39% | Coincidencia exacta |
| Balance General (Tabla 4) | Total pasivo | 2024 | 2025 | -50,225,223 | −50,225,223 | -8.36% | −8.36% | Coincidencia exacta |
| Balance General (Tabla 4) | Total patrimonio | 2023 | 2024 | -1,611,606 | −1,611,606 | -0.71% | −0.71% | Coincidencia exacta |
| Balance General (Tabla 4) | Total patrimonio | 2024 | 2025 | +5,098,410 | +5,098,410 | +2.26% | +2.26% | Coincidencia exacta |
| Estado de Resultados (Tabla 5) | Ingresos ordinarios | 2021 | 2022 | -24,311,733 | no se publica | -4.64% | −4.64% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Ingresos ordinarios | 2022 | 2023 | -21,030,422 | no se publica | -4.21% | −4.21% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Ingresos ordinarios | 2023 | 2024 | +383,647 | no se publica | +0.08% | +0.08% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Ingresos ordinarios | 2024 | 2025 | -39,302,152 | no se publica | -8.20% | −8.20% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Costo de ventas | 2021 | 2022 | +43,078,543 | no se publica | +11.73% | +11.73% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Costo de ventas | 2022 | 2023 | -36,785,525 | no se publica | -8.96% | −8.96% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Costo de ventas | 2023 | 2024 | +3,913,793 | no se publica | +1.05% | +1.05% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Costo de ventas | 2024 | 2025 | -46,029,251 | no se publica | -12.19% | −12.19% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Utilidad bruta | 2021 | 2022 | -67,390,276 | no se publica | -43.00% | −43.00% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Utilidad bruta | 2022 | 2023 | +15,755,103 | no se publica | +17.64% | +17.64% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Utilidad bruta | 2023 | 2024 | -3,530,146 | no se publica | -3.36% | −3.36% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Utilidad bruta | 2024 | 2025 | +6,727,099 | no se publica | +6.62% | +6.62% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Gastos operativos | 2021 | 2022 | +4,877,760 | no se publica | +9.17% | +9.17% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Gastos operativos | 2022 | 2023 | +5,545,180 | no se publica | +9.55% | +9.55% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Gastos operativos | 2023 | 2024 | +2,750,989 | no se publica | +4.33% | +4.33% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Gastos operativos | 2024 | 2025 | -12,744,627 | no se publica | -19.21% | −19.21% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Utilidad operativa | 2021 | 2022 | -72,377,926 | no se publica | -69.88% | −69.88% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Utilidad operativa | 2022 | 2023 | +13,488,044 | no se publica | +43.23% | +43.23% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Utilidad operativa | 2023 | 2024 | -9,495,103 | no se publica | -21.25% | −21.25% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Utilidad operativa | 2024 | 2025 | +19,471,726 | no se publica | +55.33% | +55.33% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Gastos financieros netos | 2021 | 2022 | -4,596,383 | no se publica | -21.11% | −21.11% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Gastos financieros netos | 2022 | 2023 | +4,835,585 | no se publica | +28.14% | +28.14% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Gastos financieros netos | 2023 | 2024 | +6,047,383 | no se publica | +27.47% | +27.47% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Gastos financieros netos | 2024 | 2025 | +9,334,701 | no se publica | +33.26% | +33.26% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Utilidad neta del año | 2021 | 2022 | -58,543,429 | no se publica | -85.34% | −85.34% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Utilidad neta del año | 2022 | 2023 | +3,271,370 | no se publica | +32.52% | +32.52% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Utilidad neta del año | 2023 | 2024 | -10,269,699 | no se publica | -77.04% | −77.04% | Coincidencia exacta (VR); VA derivada no publicada |
| Estado de Resultados (Tabla 5) | Utilidad neta del año | 2024 | 2025 | +8,838,006 | no se publica | +288.73% | +288.73% | Coincidencia exacta (VR); VA derivada no publicada |
| Capital de trabajo (Tabla 6) | Capital de trabajo neto | 2021 | 2022 | +38,819,904 | +38,819,904 | +21.82% | +21.82% | Coincidencia exacta |
| Capital de trabajo (Tabla 6) | Capital de trabajo neto | 2022 | 2023 | -120,054,362 | -120,054,362 | -55.39% | -55.39% | Coincidencia exacta |
| Capital de trabajo (Tabla 6) | Capital de trabajo neto | 2023 | 2024 | -26,868,396 | -26,868,396 | -27.79% | -27.79% | Coincidencia exacta |
| Capital de trabajo (Tabla 6) | Capital de trabajo neto | 2024 | 2025 | -193,373,489 | -193,373,489 | -277.02% | -277.02% | Coincidencia exacta |
| Capital de trabajo (Tabla 7) | Capital de trabajo neto | 2021 | 2022 | +38,819,904 | +38,819,904 | +21.82% | +21.82% | Coincidencia exacta |
| Capital de trabajo (Tabla 7) | Capital de trabajo neto | 2022 | 2023 | -120,054,362 | -120,054,362 | -55.39% | -55.39% | Coincidencia exacta |
| Capital de trabajo (Tabla 7) | Capital de trabajo neto | 2023 | 2024 | -26,868,396 | -26,868,396 | -27.79% | -27.79% | Coincidencia exacta |
| Capital de trabajo (Tabla 7) | Capital de trabajo neto | 2024 | 2025 | -193,373,489 | -193,373,489 | -277.02% | -277.02% | Coincidencia exacta |

Los saldos de estas tablas (122 celdas) y las razones de la Tabla 6 (10 celdas) coinciden también en las tres fuentes; las dos celdas «Base» de 2021 en la Tabla 6 son iguales en la aplicación y en el documento.

## Anexo B. Cifras de la narrativa de las secciones 6.5, 6.7 y 6.8

| Sección | Afirmación | Documento | Reconstrucción | Resultado |
|---|---|---:|---:|---|
| 6.5 | CTN aumentó USD 38.82 M | 38.82 | 38.82 | Coincidencia |
| 6.5 | crecimiento 21.82% | 21.82 | 21.82 | Coincidencia |
| 6.5 | CTN 2021 USD 177.91 M | 177.91 | 177.91 | Coincidencia |
| 6.5 | CTN 2022 USD 216.73 M | 216.73 | 216.73 | Coincidencia |
| 6.5 | AC +16.88% | 16.88 | 16.88 | Coincidencia |
| 6.5 | PC +12.61% | 12.61 | 12.61 | Coincidencia |
| 6.5 | RC 1.86x | 1.86 | 1.86 | Coincidencia |
| 6.5 | RC 1.93x | 1.93 | 1.93 | Coincidencia |
| 6.5 | AC −4.21% 2023 | 4.21 | 4.21 | Coincidencia |
| 6.5 | AC USD 429.79 M | 429.79 | 429.79 | Coincidencia |
| 6.5 | PC +43.62% | 43.62 | 43.62 | Coincidencia |
| 6.5 | PC USD 333.12 M | 333.12 | 333.12 | Coincidencia |
| 6.5 | CTN −USD 120.05 M | 120.05 | 120.05 | Coincidencia |
| 6.5 | CTN −55.39% | 55.39 | 55.39 | Coincidencia |
| 6.5 | CTN USD 96.67 M | 96.67 | 96.67 | Coincidencia |
| 6.5 | RC 1.29x | 1.29 | 1.29 | Coincidencia |
| 6.5 | PA 1.33x | 1.33 | 1.33 | Coincidencia |
| 6.5 | PA 0.87x | 0.87 | 0.87 | Coincidencia |
| 6.5 | AC +0.69% 2024 | 0.69 | 0.69 | Coincidencia |
| 6.5 | AC USD 432.77 M | 432.77 | 432.77 | Coincidencia |
| 6.5 | PC +8.96% | 8.96 | 8.96 | Coincidencia |
| 6.5 | PC USD 362.97 M | 362.97 | 362.97 | Coincidencia |
| 6.5 | Inventario −17.48% | 17.48 | 17.48 | Coincidencia |
| 6.5 | CTN −USD 26.87 M | 26.87 | 26.87 | Coincidencia |
| 6.5 | CTN −27.79% | 27.79 | 27.79 | Coincidencia |
| 6.5 | CTN USD 69.81 M | 69.81 | 69.81 | Coincidencia |
| 6.5 | RC 1.19x | 1.19 | 1.19 | Coincidencia |
| 6.5 | PA 2024 0.87x | 0.87 | 0.87 | Coincidencia |
| 6.5 | AC −42.76% | 42.76 | 42.76 | Coincidencia |
| 6.5 | AC USD 247.71 M | 247.71 | 247.71 | Coincidencia |
| 6.5 | Inventario −40.20% | 40.20 | 40.20 | Coincidencia |
| 6.5 | Inventario USD 69.82 M | 69.82 | 69.82 | Coincidencia |
| 6.5 | PC +2.29% | 2.29 | 2.29 | Coincidencia |
| 6.5 | PC USD 371.27 M | 371.27 | 371.27 | Coincidencia |
| 6.5 | CTN −USD 123.57 M | 123.57 | 123.57 | Coincidencia |
| 6.5 | Var. CTN USD 193.37 M | 193.37 | 193.37 | Coincidencia |
| 6.5 | RC 0.67x | 0.67 | 0.67 | Coincidencia |
| 6.5 | PA 0.48x | 0.48 | 0.48 | Coincidencia |
| 6.7 | PC 2021 USD 205.97 M | 205.97 | 205.97 | Coincidencia |
| 6.7 | PC 2025 USD 371.27 M | 371.27 | 371.27 | Coincidencia |
| 6.7 | Incremento acumulado 80.25% | 80.25 | 80.25 | Coincidencia |
| 6.7 | Resultado operativo USD 54.67 M | 54.67 | 54.67 | Coincidencia |
| 6.7 | GF netos USD 37.40 M | 37.40 | 37.40 | Coincidencia |
| 6.7 | GF netos 2024 USD 28.06 M | 28.06 | 28.06 | Coincidencia |
| 6.7 | GF +33.26% | 33.26 | 33.26 | Coincidencia |
| 6.7 | UO +55.33% | 55.33 | 55.33 | Coincidencia |
| 6.7 | D y A USD 7.17 M | 7.17 | 7.17 | Coincidencia |
| 6.7 | EBITDA USD 61.83 M | 61.83 | 61.83 | Coincidencia |
| 6.8 | CTN 2021 177.91 | 177.91 | 177.91 | Coincidencia |
| 6.8 | CTN 2022 216.73 | 216.73 | 216.73 | Coincidencia |
| 6.8 | RC 1.86 | 1.86 | 1.86 | Coincidencia |
| 6.8 | RC 1.93 | 1.93 | 1.93 | Coincidencia |
| 6.8 | CTN 2023 96.67 | 96.67 | 96.67 | Coincidencia |
| 6.8 | RC 1.29 | 1.29 | 1.29 | Coincidencia |
| 6.8 | PA 0.87 | 0.87 | 0.87 | Coincidencia |
| 6.8 | CTN 2024 69.81 | 69.81 | 69.81 | Coincidencia |
| 6.8 | RC 1.19 | 1.19 | 1.19 | Coincidencia |
| 6.8 | AC 247.71 | 247.71 | 247.71 | Coincidencia |
| 6.8 | PC 371.27 | 371.27 | 371.27 | Coincidencia |
| 6.8 | CTN −123.57 | 123.57 | 123.57 | Coincidencia |
| 6.8 | RC 0.67 | 0.67 | 0.67 | Coincidencia |
| 6.8 | PA 0.48 | 0.48 | 0.48 | Coincidencia |

## Anexo C. Cuentas individuales registradas y su procedencia

Importes de la base de datos en USD, con la convención de la aplicación (costos y gastos en positivo). Las 106 cuentas coinciden con la lectura propia de los estados originales. «—» indica que la cuenta no se presenta en ese ejercicio. Página: la del archivo PDF.

| Código | Cuenta | 2021 | 2022 | 2023 | 2024 | 2025 | Páginas (año:pág.) |
|---|---|---:|---:|---:|---:|---:|---|
| CB1101 | Efectivo | 10,840,865 | 20,155,298 | 12,130,206 | — | — | 21:8, 22:8, 23:6 |
| CB1102 | Certificados de depósitos a plazo fijo (corriente) | 25,900,000 | 7,000,000 | 7,400,000 | — | — | 21:8, 22:8, 23:6 |
| CB1103 | Inversiones en bonos | 2,000,000 | — | — | — | — | 21:8 |
| CB1104 | Cuentas por cobrar comerciales - neto | 53,081,088 | 32,581,092 | 41,272,525 | — | — | 21:8, 22:8, 23:6 |
| CB1105 | Cuentas por cobrar a partes relacionadas (corriente) | 75,454,125 | 187,750,230 | 168,293,969 | — | — | 21:8, 22:8, 23:6 |
| CB1106 | Otras cuentas por cobrar (corriente) | 64,903,087 | 52,441,213 | 54,824,958 | — | — | 21:8, 22:8, 23:6 |
| CB1107 | Inventarios - neto | 148,440,504 | 141,069,442 | 141,491,319 | — | — | 21:8, 22:8, 23:6 |
| CB1108 | Gastos pagados por anticipado | 1,538,667 | 1,035,731 | 954,879 | — | — | 21:8, 22:8, 23:7 |
| CB1109 | Anticipos al impuesto sobre la renta | 1,723,211 | 6,639,395 | 3,426,688 | — | — | 21:8, 22:8, 23:7 |
| CN1101 | Efectivo y Equivalentes de Efectivo | — | — | — | 15,782,257 | 12,551,085 | 24:1, 25:1 |
| CN1102 | Inversiones (corriente) | — | — | — | 13,935,076 | 13,791,656 | 24:1, 25:1 |
| CN1103 | Deudores comerciales y Otras Cuentas por Cobrar (Netos) | — | — | — | 97,204,415 | 70,169,882 | 24:1, 25:1 |
| CN1104 | Cuentas por cobrar Empresas Relacionadas (corriente) | — | — | — | 182,232,841 | 77,574,661 | 24:1, 25:1 |
| CN1105 | Inventario (Materiales, Suministros, etc.) | — | — | — | 116,761,311 | 69,818,060 | 24:1, 25:1 |
| CN1106 | Pagos por Anticipado | — | — | — | 1,939,012 | 2,394,829 | 24:1, 25:1 |
| CN1107 | Impuestos Corrientes (activo) | — | — | — | 4,916,766 | 1,405,808 | 24:1, 25:1 |
| CB1201 | Certificados de depósitos a plazo fijo (no corriente) | 1,000,000 | 8,000,000 | 8,000,000 | — | — | 21:8, 22:8, 23:7 |
| CB1202 | Cuentas por cobrar a partes relacionadas (no corriente) | — | — | 110,380,709 | — | — | 23:7 |
| CB1203 | Otras cuentas por cobrar (no corriente) | — | — | 924,000 | — | — | 23:7 |
| CB1204 | Inversiones en acciones | 24,950,870 | 24,658,197 | 24,633,711 | — | — | 21:8, 22:8, 23:7 |
| CB1205 | Propiedades de inversión | 5,597,009 | 6,078,838 | 8,325,372 | — | — | 21:8, 22:8, 23:7 |
| CB1206 | Propiedades, planta y equipo - neto | 106,623,719 | 154,006,305 | 173,683,163 | — | — | 21:8, 22:8, 23:7 |
| CB1207 | Activos por derecho de uso - neto | 16,702,267 | 15,720,434 | 15,633,837 | — | — | 21:8, 22:8, 23:7 |
| CB1208 | Activos intangibles - neto | 2,585,345 | 1,923,631 | 1,413,660 | — | — | 21:8, 22:8, 23:7 |
| CB1209 | Plusvalía mercantil | 11,668,154 | 11,668,154 | 35,293,969 | — | — | 21:8, 22:8, 23:7 |
| CB1210 | Otros activos | 299,603 | 473,223 | 655,843 | — | — | 21:8, 22:8, 23:7 |
| CB1211 | Activo por impuestos sobre la renta diferidos | 646,671 | 823,910 | 362,138 | — | — | 21:8, 22:8, 23:7 |
| CN1201 | Cuentas por cobrar a LP | — | — | — | 983,263 | 2,544,870 | 24:1, 25:1 |
| CN1202 | Otras cuentas por cobrar a LP | — | — | — | 118,684,551 | — | 24:1 |
| CN1203 | Cuentas por cobrar Empresas Relacionadas a LP | — | — | — | — | 262,128,668 | 25:1 |
| CN1204 | Inversiones (no corriente) | — | — | — | 32,166,255 | 25,974,530 | 24:1, 25:1 |
| CN1205 | Propiedades de Inversión | — | — | — | 7,052,552 | 12,580,435 | 24:1, 25:1 |
| CN1206 | Propiedades, Planta y Equipo (Neto) | — | — | — | 179,359,645 | 180,643,255 | 24:1, 25:1 |
| CN1207 | Activos por derechos de Uso (neto) | — | — | — | 17,127,186 | 11,119,749 | 24:1, 25:1 |
| CN1208 | Activos intangibles | — | — | — | 38,005,433 | 36,218,193 | 24:1, 25:1 |
| CN1209 | Impuestos Diferidos (activo) | — | — | — | 223,586 | 796,166 | 24:1, 25:1 |
| CN1210 | Otros Activos financieros | — | — | — | 802,225 | 2,337,714 | 24:1, 25:1 |
| CB2101 | Préstamos bancarios por pagar (corriente) | 25,039,997 | 81,331,433 | 95,395,476 | — | — | 21:8, 22:8, 23:7 |
| CB2102 | Arrendamientos por pagar (corriente) | 4,872,937 | 5,373,076 | 5,406,547 | — | — | 21:8, 22:8, 23:7 |
| CB2103 | Bonos corporativos (corriente) | — | — | 8,181,371 | — | — | 23:7 |
| CB2104 | Certificados de inversión (corriente) | — | 2,745,704 | 2,298,539 | — | — | 22:8, 23:7 |
| CB2105 | Obligaciones por derechos titularizados (corriente) | 1,652,870 | 1,817,611 | 1,795,145 | — | — | 21:8, 22:8, 23:7 |
| CB2106 | Porción corriente de los documentos por pagar a largo plazo | 80,133 | 120,013 | — | — | — | 21:8, 22:8 |
| CB2107 | Documentos por pagar (corriente) | — | — | 6,703,817 | — | — | 23:7 |
| CB2108 | Cuentas por pagar comerciales | 156,609,253 | 96,629,671 | 195,599,671 | — | — | 21:8, 22:8, 23:7 |
| CB2109 | Cuentas por pagar a partes relacionadas | 1,171,548 | 34,655,602 | 4,512,985 | — | — | 21:8, 22:8, 23:7 |
| CB2110 | Otras cuentas por pagar (corriente) | 8,632,737 | 8,854,582 | 12,127,667 | — | — | 21:9, 22:8, 23:7 |
| CB2111 | Impuesto sobre la renta por pagar (corriente) | 7,913,755 | 416,488 | 1,099,467 | — | — | 21:9, 22:9, 23:7 |
| CN2101 | Préstamos de Corto Plazo | — | — | — | 95,128,624 | 87,786,629 | 24:1, 25:1 |
| CN2102 | Pasivos por arrendamientos (corriente) | — | — | — | 6,252,051 | 4,114,174 | 24:1, 25:1 |
| CN2103 | Obligaciones Emisión de Títulos valores (corriente) | — | — | — | 13,447,268 | 80,658,329 | 24:1, 25:1 |
| CN2104 | Otros Pasivos Financieros (corriente) | — | — | — | 19,727,330 | 21,432,441 | 24:1, 25:1 |
| CN2105 | Acreedores comerciales y Otras Cuentas por Pagar | — | — | — | 225,126,517 | 173,120,913 | 24:1, 25:1 |
| CN2106 | Cuentas por Pagar Empresas Relacionadas | — | — | — | 2,098,612 | 3,457,100 | 24:1, 25:1 |
| CN2107 | Impuestos Corrientes (pasivo) | — | — | — | 1,185,813 | 704,421 | 24:1, 25:1 |
| CB2201 | Préstamos bancarios por pagar (no corriente) | 114,626,074 | 108,327,468 | 112,597,844 | — | — | 21:9, 22:9, 23:7 |
| CB2202 | Arrendamientos por pagar (no corriente) | 24,556,484 | 36,108,070 | 33,221,918 | — | — | 21:9, 22:9, 23:7 |
| CB2203 | Bonos corporativos (no corriente) | 32,758,231 | 32,083,941 | 31,733,829 | — | — | 21:9, 22:9, 23:7 |
| CB2204 | Certificados de inversión (no corriente) | 18,271,064 | 20,447,743 | 24,130,415 | — | — | 21:9, 22:9, 23:7 |
| CB2205 | Obligaciones por derechos titularizados (no corriente) | 10,847,273 | 9,029,662 | 7,454,491 | — | — | 21:9, 22:9, 23:7 |
| CB2206 | Documentos por pagar a largo plazo | 186,964 | 195,923 | 16,680,822 | — | — | 21:9, 22:9, 23:7 |
| CB2207 | Otras cuentas por pagar (no corriente) | — | — | 293,522 | — | — | 23:7 |
| CB2208 | Pasivos por prima en venta de acciones de subsidiaria | — | 18,771,142 | 18,730,404 | — | — | 22:9, 23:8 |
| CB2209 | Pasivos por beneficios post empleo | 592,568 | 728,759 | 932,485 | — | — | 21:9, 22:9, 23:8 |
| CB2210 | Impuesto sobre la renta por pagar (no corriente) | — | — | 465,955 | — | — | 23:8 |
| CB2211 | Pasivo por impuestos sobre la renta diferidos | 822,107 | 511,441 | 2,065,182 | — | — | 21:9, 22:9, 23:8 |
| CN2201 | Préstamos y Otras Obligaciones Financieras | — | — | — | 98,999,095 | 89,087,790 | 24:1, 25:1 |
| CN2202 | Pasivos por arrendamientos (no corriente) | — | — | — | 34,065,636 | 28,750,278 | 24:1, 25:1 |
| CN2203 | Obligaciones Emisión de Títulos valores (no corriente) | — | — | — | 68,067,653 | 32,676,388 | 24:1, 25:1 |
| CN2204 | Otros Pasivos Financieros (no corriente) | — | — | — | 16,811,464 | 7,620,764 | 24:1, 25:1 |
| CN2205 | Provisiones | — | — | — | 18,192,624 | 17,507,168 | 24:1, 25:1 |
| CN2206 | Impuestos Diferidos (pasivo) | — | — | — | 2,011,899 | 3,972,968 | 24:1, 25:1 |
| CB3101 | Capital social | 79,411,060 | 119,389,833 | 119,389,833 | — | — | 21:9, 22:9, 23:8 |
| CB3102 | Primas sobre acciones | — | 56,160,201 | 56,160,201 | — | — | 22:9, 23:8 |
| CB3103 | Aportaciones de capital | 84,787 | 84,787 | 169,574 | — | — | 21:9, 22:9, 23:8 |
| CB3104 | Reserva legal | 4,325,495 | 4,694,588 | 5,540,907 | — | — | 21:9, 22:9, 23:8 |
| CB3105 | Otras reservas de capital | -1,183,613 | -2,360,428 | -1,439,577 | — | — | 21:9, 22:9, 23:8 |
| CB3106 | Utilidades acumuladas | 59,420,100 | 31,015,221 | 47,852,456 | — | — | 21:9, 22:9, 23:8 |
| CB3107 | Participaciones no controladoras | 3,263,361 | 4,892,562 | 0 | — | — | 21:9, 22:9, 23:8 |
| CN3101 | Capital Social | — | — | — | 119,391,833 | 119,389,833 | 24:1, 25:1 |
| CN3102 | Capital Adicional | — | — | — | 169,574 | 169,574 | 24:1, 25:1 |
| CN3103 | Reserva Legal | — | — | — | 5,540,907 | 6,503,436 | 24:1, 25:1 |
| CN3104 | Superávit por Acciones | — | — | — | 56,160,201 | 56,160,201 | 24:1, 25:1 |
| CN3105 | Reservas de Capital | — | — | — | 5,188,768 | 13,407,214 | 24:1, 25:1 |
| CN3106 | Efecto de Conversion Entidades Extranjeras | — | — | — | -8,973,683 | -16,976,702 | 24:1, 25:1 |
| CN3107 | Resultados Acumulados | — | — | — | 45,523,207 | 40,607,655 | 24:1, 25:1 |
| CN3108 | Resultado del Período | — | — | — | 3,060,981 | 11,898,987 | 24:1, 25:1 |
| CB4101 | Ingresos de actividades ordinarias | 523,965,227 | 499,653,494 | 478,623,072 | — | — | 21:10, 22:10, 23:9 |
| CN4101 | Ingresos Ordinarios | — | — | — | 479,006,719 | 439,704,567 | 24:2, 25:2 |
| CB5101 | Costo de ventas | 367,252,613 | 410,331,156 | 373,545,631 | — | — | 21:10, 22:10, 23:9 |
| CN5101 | Costo de Ventas | — | — | — | 377,459,424 | 331,430,173 | 24:2, 25:2 |
| CB6101 | Gastos de administración | 16,733,467 | 18,344,656 | 19,651,834 | — | — | 21:10, 22:10, 23:9 |
| CB6102 | Gastos de venta y despacho | 36,445,981 | 39,712,552 | 43,950,554 | — | — | 21:10, 22:10, 23:9 |
| CB6103 | Pérdidas por deterioro de valor de cuentas por cobrar, neto | 274,140 | 397,016 | 507,752 | — | — | 21:10, 22:10, 23:9 |
| CB6104 | Otros ingresos - neto | 319,877 | 332,863 | 3,721,720 | — | — | 21:10, 22:10, 23:9 |
| CN6101 | Gastos de Venta y Distribución | — | — | — | 26,379,749 | 18,950,398 | 24:2, 25:2 |
| CN6102 | Gastos de Administración | — | — | — | 5,898,635 | 5,227,785 | 24:2, 25:2 |
| CN6103 | Gastos de Personal | — | — | — | 26,967,511 | 22,262,768 | 24:2, 25:2 |
| CN6104 | Gastos de Depreciación y Amortización | — | — | — | 7,107,482 | 7,167,799 | 24:2, 25:2 |
| CB7101 | Gastos financieros - neto | 21,777,725 | 17,181,342 | 22,016,927 | — | — | 21:10, 22:10, 23:9 |
| CN7101 | Ingresos Financieros | — | — | — | 15,024,973 | 14,515,895 | 24:2, 25:2 |
| CN7102 | Gastos Financieros | — | — | — | 43,089,283 | 51,914,906 | 24:2, 25:2 |
| CN7201 | Otros Ingresos (Gastos) - neto ingreso | — | — | — | 55,570 | — | 24:2 |
| CN7202 | Otros Ingresos (Gastos) - neto gasto | — | — | — | — | 811,571 | 25:2 |
| CB8101 | Impuesto sobre la renta | 13,198,439 | 3,960,325 | 9,341,414 | — | — | 21:10, 22:10, 23:9 |
| CN8101 | Impuestos | — | — | — | 4,124,197 | 4,556,075 | 24:2, 25:2 |

## Anexo D. Variaciones por grupo de análisis

Es la presentación actual de la aplicación en el nivel «Grupos de análisis». Todas las celdas coinciden con la reconstrucción independiente. Aritméticamente son correctas, pero **★** marca las celdas que dependen de un grupo sin cuentas en uno de los dos ejercicios. No deben leerse como una variación económica sin revisar la partida (hallazgo AH-01). Otras celdas sin marca también pueden estar afectadas por cambios de contenido, como Activos intangibles y Otras cuentas por cobrar no corrientes en 2023–2024.

| Grupo | VA 21–22 | VR 21–22 | VA 22–23 | VR 22–23 | VA 23–24 | VR 23–24 | VA 24–25 | VR 24–25 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Efectivo y equivalentes de efectivo | +9,314,433 | +85.92% | -8,025,092 | -39.82% | +3,652,051 | +30.11% | -3,231,172 | -20.47% |
| Inversiones y depósitos a plazo (corrientes) | -20,900,000 | -74.91% | +400,000 | +5.71% | +6,535,076 | +88.31% | -143,420 | -1.03% |
| Cuentas por cobrar comerciales (neto) | -20,499,996 | -38.62% | +8,691,433 | +26.68% | -41,272,525 ★ | -100.00% ★ | +0 | — |
| Otras cuentas por cobrar (corrientes) | -12,461,874 | -19.20% | +2,383,745 | +4.55% | -54,824,958 ★ | -100.00% ★ | +0 | — |
| Deudores comerciales y otras cuentas por cobrar (neto) | +0 | — | +0 | — | +97,204,415 ★ | — ★ | -27,034,533 | -27.81% |
| Cuentas por cobrar a partes relacionadas (corrientes) | +112,296,105 | +148.83% | -19,456,261 | -10.36% | +13,938,872 | +8.28% | -104,658,180 | -57.43% |
| Inventarios | -7,371,062 | -4.97% | +421,877 | +0.30% | -24,730,008 | -17.48% | -46,943,251 | -40.20% |
| Gastos y pagos por anticipado | -502,936 | -32.69% | -80,852 | -7.81% | +984,133 | +103.06% | +455,817 | +23.51% |
| Anticipos de ISR e impuestos corrientes (activo) | +4,916,184 | +285.29% | -3,212,707 | -48.39% | +1,490,078 | +43.48% | -3,510,958 | -71.41% |
| **Total activo corriente** | +64,790,854 | +16.88% | -18,877,857 | -4.21% | +2,977,134 | +0.69% | -185,065,697 | -42.76% |
| Certificados de depósito a plazo (no corrientes) | +7,000,000 | +700.00% | +0 | +0.00% | -8,000,000 ★ | -100.00% ★ | +0 | — |
| Inversiones en acciones | -292,673 | -1.17% | -24,486 | -0.10% | -24,633,711 ★ | -100.00% ★ | +0 | — |
| Inversiones (no corrientes) | +0 | — | +0 | — | +32,166,255 ★ | — ★ | -6,191,725 | -19.25% |
| Cuentas por cobrar a largo plazo | +0 | — | +0 | — | +983,263 ★ | — ★ | +1,561,607 | +158.82% |
| Cuentas por cobrar a partes relacionadas (no corrientes) | +0 | — | +110,380,709 ★ | — ★ | -110,380,709 ★ | -100.00% ★ | +262,128,668 ★ | — ★ |
| Otras cuentas por cobrar (no corrientes) | +0 | — | +924,000 ★ | — ★ | +117,760,551 | +12744.65% | -118,684,551 ★ | -100.00% ★ |
| Propiedades de inversión | +481,829 | +8.61% | +2,246,534 | +36.96% | -1,272,820 | -15.29% | +5,527,883 | +78.38% |
| Propiedades, planta y equipo (neto) | +47,382,586 | +44.44% | +19,676,858 | +12.78% | +5,676,482 | +3.27% | +1,283,610 | +0.72% |
| Activos por derecho de uso (neto) | -981,833 | -5.88% | -86,597 | -0.55% | +1,493,349 | +9.55% | -6,007,437 | -35.08% |
| Activos intangibles | -661,714 | -25.59% | -509,971 | -26.51% | +36,591,773 | +2588.44% | -1,787,240 | -4.70% |
| Plusvalía mercantil | +0 | +0.00% | +23,625,815 | +202.48% | -35,293,969 ★ | -100.00% ★ | +0 | — |
| Otros activos (no corrientes) | +173,620 | +57.95% | +182,620 | +38.59% | -655,843 ★ | -100.00% ★ | +0 | — |
| Otros activos financieros (no corrientes) | +0 | — | +0 | — | +802,225 ★ | — ★ | +1,535,489 | +191.40% |
| Impuesto sobre la renta diferido (activo) | +177,239 | +27.41% | -461,772 | -56.05% | -138,552 | -38.26% | +572,580 | +256.09% |
| **Total activo no corriente** | +53,279,054 | +31.33% | +155,953,710 | +69.82% | +15,098,294 | +3.98% | +139,938,884 | +35.48% |
| **Total activo** | +118,069,908 | +21.31% | +137,075,853 | +20.40% | +18,075,428 | +2.23% | -45,126,813 | -5.46% |
| Préstamos bancarios (corrientes) | +56,291,436 | +224.81% | +14,064,043 | +17.29% | -266,852 | -0.28% | -7,341,995 | -7.72% |
| Pasivos por arrendamientos (corrientes) | +500,139 | +10.26% | +33,471 | +0.62% | +845,504 | +15.64% | -2,137,877 | -34.19% |
| Bonos corporativos (corrientes) | +0 | — | +8,181,371 ★ | — ★ | -8,181,371 ★ | -100.00% ★ | +0 | — |
| Certificados de inversión (corrientes) | +2,745,704 ★ | — ★ | -447,165 | -16.29% | -2,298,539 ★ | -100.00% ★ | +0 | — |
| Obligaciones por derechos titularizados (corrientes) | +164,741 | +9.97% | -22,466 | -1.24% | -1,795,145 ★ | -100.00% ★ | +0 | — |
| Obligaciones por emisión de títulos valores (corrientes) | +0 | — | +0 | — | +13,447,268 ★ | — ★ | +67,211,061 | +499.81% |
| Documentos por pagar (corrientes) | +39,880 | +49.77% | +6,583,804 | +5485.91% | -6,703,817 ★ | -100.00% ★ | +0 | — |
| Otros pasivos financieros (corrientes) | +0 | — | +0 | — | +19,727,330 ★ | — ★ | +1,705,111 | +8.64% |
| Cuentas por pagar comerciales | -59,979,582 | -38.30% | +98,970,000 | +102.42% | -195,599,671 ★ | -100.00% ★ | +0 | — |
| Otras cuentas por pagar (corrientes) | +221,845 | +2.57% | +3,273,085 | +36.96% | -12,127,667 ★ | -100.00% ★ | +0 | — |
| Acreedores comerciales y otras cuentas por pagar | +0 | — | +0 | — | +225,126,517 ★ | — ★ | -52,005,604 | -23.10% |
| Cuentas por pagar a partes relacionadas | +33,484,054 | +2858.10% | -30,142,617 | -86.98% | -2,414,373 | -53.50% | +1,358,488 | +64.73% |
| Impuesto sobre la renta e impuestos por pagar (corrientes) | -7,497,267 | -94.74% | +682,979 | +163.99% | +86,346 | +7.85% | -481,392 | -40.60% |
| **Total pasivo corriente** | +25,970,950 | +12.61% | +101,176,505 | +43.62% | +29,845,530 | +8.96% | +8,307,792 | +2.29% |
| Préstamos y otras obligaciones financieras (no corrientes) | -6,298,606 | -5.49% | +4,270,376 | +3.94% | -13,598,749 | -12.08% | -9,911,305 | -10.01% |
| Pasivos por arrendamientos (no corrientes) | +11,551,586 | +47.04% | -2,886,152 | -7.99% | +843,718 | +2.54% | -5,315,358 | -15.60% |
| Bonos corporativos (no corrientes) | -674,290 | -2.06% | -350,112 | -1.09% | -31,733,829 ★ | -100.00% ★ | +0 | — |
| Certificados de inversión (no corrientes) | +2,176,679 | +11.91% | +3,682,672 | +18.01% | -24,130,415 ★ | -100.00% ★ | +0 | — |
| Obligaciones por derechos titularizados (no corrientes) | -1,817,611 | -16.76% | -1,575,171 | -17.44% | -7,454,491 ★ | -100.00% ★ | +0 | — |
| Obligaciones por emisión de títulos valores (no corrientes) | +0 | — | +0 | — | +68,067,653 ★ | — ★ | -35,391,265 | -51.99% |
| Documentos por pagar (no corrientes) | +8,959 | +4.79% | +16,484,899 | +8413.97% | -16,680,822 ★ | -100.00% ★ | +0 | — |
| Otros pasivos financieros (no corrientes) | +0 | — | +0 | — | +16,811,464 ★ | — ★ | -9,190,700 | -54.67% |
| Otras cuentas por pagar (no corrientes) | +0 | — | +293,522 ★ | — ★ | -293,522 ★ | -100.00% ★ | +0 | — |
| Pasivo por prima en venta de acciones de subsidiaria | +18,771,142 ★ | — ★ | -40,738 | -0.22% | -18,730,404 ★ | -100.00% ★ | +0 | — |
| Pasivos por beneficios post empleo | +136,191 | +22.98% | +203,726 | +27.96% | -932,485 ★ | -100.00% ★ | +0 | — |
| Provisiones (no corrientes) | +0 | — | +0 | — | +18,192,624 ★ | — ★ | -685,456 | -3.77% |
| Impuesto sobre la renta por pagar (no corriente) | +0 | — | +465,955 ★ | — ★ | -465,955 ★ | -100.00% ★ | +0 | — |
| Impuesto sobre la renta diferido (pasivo) | -310,666 | -37.79% | +1,553,741 | +303.80% | -53,283 | -2.58% | +1,961,069 | +97.47% |
| **Total pasivo no corriente** | +23,543,384 | +11.62% | +22,102,718 | +9.77% | -10,158,496 | -4.09% | -58,533,015 | -24.58% |
| **Total pasivo** | +49,514,334 | +12.12% | +123,279,223 | +26.91% | +19,687,034 | +3.39% | -50,225,223 | -8.36% |
| Capital social | +39,978,773 | +50.34% | +0 | +0.00% | +2,000 | +0.00% | -2,000 | -0.00% |
| Prima / superávit por acciones | +56,160,201 ★ | — ★ | +0 | +0.00% | +0 | +0.00% | +0 | +0.00% |
| Aportaciones de capital / capital adicional | +0 | +0.00% | +84,787 | +100.00% | +0 | +0.00% | +0 | +0.00% |
| Reserva legal | +369,093 | +8.53% | +846,319 | +18.03% | +0 | +0.00% | +962,529 | +17.37% |
| Otras reservas de capital (incluye otros resultados integrales) | -1,176,815 | — | +920,851 | — | +1,439,577 ★ | — ★ | +0 | — |
| Reservas de capital | +0 | — | +0 | — | +5,188,768 ★ | — ★ | +8,218,446 | +158.39% |
| Efecto de conversión de entidades extranjeras | +0 | — | +0 | — | -8,973,683 ★ | — ★ | -8,003,019 | — |
| Resultados (utilidades) acumulados | -28,404,879 | -47.80% | +16,837,235 | +54.29% | -2,329,249 | -4.87% | -4,915,552 | -10.80% |
| Resultado del período | +0 | — | +0 | — | +3,060,981 ★ | — ★ | +8,838,006 | +288.73% |
| Participaciones no controladoras | +1,629,201 | +49.92% | -4,892,562 | -100.00% | +0 ★ | — ★ | +0 | — |
| **Total patrimonio** | +68,555,574 | +47.18% | +13,796,630 | +6.45% | -1,611,606 | -0.71% | +5,098,410 | +2.26% |
| Ingresos de actividades ordinarias | -24,311,733 | -4.64% | -21,030,422 | -4.21% | +383,647 | +0.08% | -39,302,152 | -8.20% |
| Costo de ventas | +43,078,543 | +11.73% | -36,785,525 | -8.96% | +3,913,793 | +1.05% | -46,029,251 | -12.19% |
| Gastos de administración | +1,611,189 | +9.63% | +1,307,178 | +7.13% | -13,753,199 | -69.98% | -670,850 | -11.37% |
| Gastos de venta y despacho / distribución | +3,266,571 | +8.96% | +4,238,002 | +10.67% | -17,570,805 | -39.98% | -7,429,351 | -28.16% |
| Deterioro de cuentas por cobrar | +122,876 | +44.82% | +110,736 | +27.89% | -507,752 ★ | -100.00% ★ | +0 | — |
| Gastos de personal | +0 | — | +0 | — | +26,967,511 ★ | — ★ | -4,704,743 | -17.45% |
| Depreciación y amortización | +0 | — | +0 | — | +7,107,482 ★ | — ★ | +60,317 | +0.85% |
| Otros ingresos operativos (neto) | +12,986 | +4.06% | +3,388,857 | +1018.09% | -3,721,720 ★ | -100.00% ★ | +0 | — |
| Ingresos financieros | +0 | — | +0 | — | +15,024,973 ★ | — ★ | -509,078 | -3.39% |
| Gastos financieros | +0 | — | +0 | — | +43,089,283 ★ | — ★ | +8,825,623 | +20.48% |
| Gastos financieros (neto, presentado así) | -4,596,383 | -21.11% | +4,835,585 | +28.14% | -22,016,927 ★ | -100.00% ★ | +0 | — |
| Otros ingresos (gastos) no operativos | +0 | — | +0 | — | +55,570 ★ | — ★ | -867,141 | -1560.45% |
| Impuesto sobre la renta | -9,238,114 | -69.99% | +5,381,089 | +135.87% | -5,217,217 | -55.85% | +431,878 | +10.47% |
| **Utilidad bruta** | -67,390,276 | -43.00% | +15,755,103 | +17.64% | -3,530,146 | -3.36% | +6,727,099 | +6.62% |
| **Utilidad de operación** | -72,377,926 | -69.88% | +13,488,044 | +43.23% | -9,495,103 | -21.25% | +19,471,726 | +55.33% |
| **Utilidad antes de impuestos** | -67,781,543 | -82.86% | +8,652,459 | +61.72% | -15,486,916 | -68.31% | +9,269,884 | +129.01% |
| **Utilidad neta del ejercicio** | -58,543,429 | -85.34% | +3,271,370 | +32.52% | -10,269,699 | -77.04% | +8,838,006 | +288.73% |
