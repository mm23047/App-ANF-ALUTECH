# Informe de implementación del análisis horizontal

**Fecha:** 5 de noviembre de 2026
**Rama:** `correcciones-auditoria`. El trabajo parte del commit `3dcdcdd` («ultimos cambios», creado por Estuardo durante la sesión). **Sin commit ni push:** los cambios quedan para revisión manual.
**Respaldo previo:** `C:\Users\estua\Documents\ANF\respaldos_appfinanciera\horizontal_20261105\`

## 1. Resultado

| Comprobación | Resultado |
|---|---|
| Suite completa en copia aislada | **740 de 740** (695 anteriores + 45 nuevas). Ninguna eliminada ni omitida |
| Tablas 3 a 7 contra el documento | **242 de 242** celdas sin cambios |
| Reconstrucción independiente tras los cambios | Grupos 936 y cuentas 1,612 celdas, **0 diferencias** |
| Pantalla real contra secciones | **1,775 de 1,775** celdas en 5 vistas, sin excepciones |
| PDF exportado contra pantalla, por posición | **0 diferencias** en los 3 niveles de ambos estados |
| Excel contra pantalla | **0 diferencias de cifra.** Quedan diferencias de formato (sección 5) |
| Exportaciones según el nivel elegido | **Comprobado** a través de la página real |
| PDF del documento contra Markdown, por posición | **309 de 309** celdas de tablas |
| Revisión visual | Páginas 2 y 21 a 29 del documento; muestras de los PDF exportados |
| Base de datos y estados originales | **Sin cambios** (hashes iguales) |

**R-15 no se aplicó:** la descripción quedó revisada en `DESCRIPCION_ACADEMICA_ANALISIS_HORIZONTAL.md`, pero, como pediste, no se insertó en el documento principal.

## 2. Cambios en la aplicación

### R-1. Grupos sin cuentas

Un grupo sin cuentas en un ejercicio ya no vale cero. Ahora se distinguen estas situaciones:

| Situación | Saldos | Variación | Sentido | Ejemplo |
|---|---|---|---|---|
| **Saldo cero explícito** | 0 | Se calcula; si la base es cero, solo la absoluta | Según el cambio | Participaciones no controladoras 2022–2023: −100 % válido, porque el estado imprime «-» |
| **Ausencia de presentación** | «—» | No | Aparece o Desaparece | Beneficios post empleo 2023–2024 |
| **Agrupación en otro rubro** | «—» en un lado | No | Presentación agrupada | Cuentas por pagar comerciales 2023–2024 |
| **Falta de comparabilidad** | Ambos | No | No comparable | Activos intangibles 2023–2024 (antes, +2,588.44 %) |
| **Agrupación analítica** | Ambos | Sí, con advertencia | Según el cambio | CxC comerciales y otras 2023–2024 (+1.15 %) |

Efecto en el nivel de grupos:

| Par | Presentación agrupada | No comparable | Antes |
|---|---:|---:|---|
| 2023–2024 | 32 | 5 | 24 filas en −100 % y 18 con base cero |
| 2024–2025 | 2 | 0 | 1 fila en −100 % y 1 con base cero |

**La regla no depende de ningún año.** En `calculations/rubros.py` se declaran familias de grupos relacionados por su denominación. La familia se considera reorganizada cuando, entre dos ejercicios, una línea sale y otra entra, o cuando una línea cambia mientras otra conserva el nombre con cuentas distintas. Una prueba lo comprueba con ejercicios ficticios de 1999 y 2000, y otra verifica que el código de la regla no contenga años.

### D-1 y D-2. Agrupaciones y cuentas por cobrar

- La advertencia usa el texto acordado: «Agrupación analítica; comparabilidad no confirmada».
- La Tabla 3 no cambia y B2 no sustituye a ningún resultado principal.
- La CxC de línea presentada ya no muestra +135.52 % en 2023–2024: figura como «No comparable».
- B2 se presenta como alternativa analítica, con la condición de confirmar que la línea unificada contiene exactamente esas cuentas, sin conceptos adicionales.
- Se retiró el término «homogénea» en los textos que lo afirmaban para esta base (`rubros.py`, `indicadores.py` e `indicadores_financieros.py`). Un nombre interno de prueba conserva la palabra, pero no se muestra.

### R-4. Advertencias en las filas

- **Comparar dos ejercicios:** la advertencia aparece en la columna «Observación» de la fila.
- **Tablas 3 a 5:** la fila lleva la marca † y la explicación va al pie. Están marcadas CxC en la Tabla 4, y gastos operativos y gastos financieros netos en la Tabla 5.
- **Cuentas:** `CN1202` y `CN1203`, y las demás cuentas de familias reorganizadas, indican que pueden corresponder a otra denominación.

### R-5. Cambios de signo

- **Tablas 6 y 7:** la fila de 2025 lleva † y una nota generada a partir de los datos, con la advertencia de leer el porcentaje junto con la variación absoluta. Las cifras no cambian (−277.02 %).
- **De negativo a positivo:** el mensaje ya no menciona un porcentaje que no existe.

### R-3. Exportaciones

Las hojas interanuales usan el nivel elegido en pantalla. El nombre del archivo lo refleja (por ejemplo, `analisis_horizontal_balance_cuentas`) y una leyenda lo explica. Se incluyen todos los pares de ejercicios, no solo el visible. Si prefieres exportar solo el par elegido, es un ajuste menor.

### D-4. Capital social

El importe de 2024 se conserva. La fila indica «El capital social difiere en USD 2,000 respecto de…» y que requiere confirmación documental, tanto en 2023–2024 como en 2024–2025. El texto se genera del dato: se señala cualquier cambio de capital social inferior a 0.01 %; un aumento real, como el de 2021–2022, no se señala.

## 3. Cambios en el documento

| # | Cambio | Dónde |
|---|---|---|
| R-11 | Base negativa: no se calcula porcentaje; cambio de positivo a negativo: leerlo con la variación absoluta | 6.3 |
| R-12 | Nota de cambio de signo y marca † | Tablas 6 y 7 |
| R-13 | Nota sobre la utilidad operativa 2023–2024 | Notas de la Tabla 5 |
| R-14 | Título de 6.4 (índice y página), fórmulas legibles, «2021-2025.» y cifras sin partir | PDF |
| D-2 | Marca † y nota: comparabilidad no confirmada | Tabla 4 |
| D-3 | «Tabla 5 (continuación)» con las 28 variaciones absolutas | Después de la Tabla 5 |
| D-4 | Observación sobre el capital social | Después de la Tabla 4 |

Las 28 variaciones absolutas se comprobaron contra los saldos publicados en la propia Tabla 5.

**PDF del documento.** No hay fuente exportable en el proyecto, así que se siguió el procedimiento ya registrado: las páginas 21 a 29 se recompusieron desde el Markdown y las demás se conservaron.

- Pasa de 85 a 84 páginas. La sección 7 vuelve a empezar en la página 29, como indica el índice.
- 74 de las 76 páginas no recompuestas son idénticas. Las otras dos cambian a propósito: el índice (página 2) y la que recibe el título 6.8.
- Se comprobaron 52 de 52 enlaces del índice y 57 de 57 marcadores.

## 4. Archivos afectados

| Archivo | Cambio |
|---|---|
| `calculations/comparativo.py` | R-1, R-4, R-5 y D-4: estados de comparabilidad |
| `calculations/rubros.py` | Familias de presentación; nota de B2 |
| `calculations/indicadores.py`, `reports/indicadores_financieros.py` | Solo texto: «alternativa analítica» (D-2) |
| `reports/secciones.py` | Marcas, notas, títulos y leyenda de sentidos |
| `reports/analisis_alutech.py` | R-3 |
| `Trabajo de investigación ANF.md`, `.pdf` | Sección 3 |
| `DESCRIPCION_ACADEMICA_ANALISIS_HORIZONTAL.md` | Revisada; sin insertar |
| `README.md`, `REGISTRO_DE_CAMBIOS.md` | Documentación del cambio |
| `tests/test_fase11_horizontal.py`, `tests/humo_exportes_nivel.py` | **Nuevos:** 45 pruebas |
| `tests/concordancia_documento.py` | El lector de celdas ignora la llamada † (ajuste necesario; no relaja ninguna comprobación numérica) |

**Sin cambios:** `data/financiera.db`, `documentos/`, `fuentes/alutech/` y `fuentes/anf/`.

## 5. Diferencias pendientes

| # | Pendiente | Situación |
|---|---|---|
| 1 | **R-15** | Espera tu revisión de la descripción |
| 2 | **Excel:** «—» sale vacío y «+0» o «+0.00%» salen sin signo | Solo formato; se resuelve con R-6 y R-9 |
| 3 | **Tabla 5 de la aplicación** sin nota de utilidad operativa | Es R-7. El documento ya la lleva (R-13), así que hoy difieren en esa nota |
| 4 | **6.5:** «déficit operativo» y «modelo holgado de liquidez» | No figuraba en R-11 a R-14, no se tocó. Requiere tu decisión |
| 5 | **Índice impreso** | Las secciones 6 y 7 coinciden con la paginación real. Las demás entradas no se revisaron una a una; desde 9.3 persiste el desfase ya registrado, ahora con una página menos |
| 6 | **Google Docs:** si existe la fuente original, no tiene estas correcciones | No se consultó |
| 7 | **Composición de 2024–2025 y capital social** | Requieren documentación de la empresa |
| 8 | **Familias de presentación** | Se apoyan en la denominación. Son un criterio revisable en `rubros.py` |
| 9 | `INFORME_AUDITORIA_ANALISIS_HORIZONTAL.md` | Conserva la situación anterior a las correcciones, como registro histórico |

## 6. Correcciones que requieren tu autorización

Ninguna está implementada.

### R-2. Filas de agrupación analítica en el nivel de grupos

- **Cambio:** añadir filas que sumen las líneas de cada familia reorganizada, calculadas con la advertencia acordada. Se usarían, por ejemplo, para CxP comerciales + otras (+8.38 %), intangibles + plusvalía (+3.54 %), títulos corrientes (+9.55 %) y no corrientes (+7.50 %), y resultados acumulados + del período (+1.53 %), todas en 2023–2024.
- **Justificación:** hoy el nivel de grupos ya no engaña, pero en 2023–2024 tampoco ofrece variación para esas partidas. Aplica D-1 y da un dato útil sin afirmar que sea comparable.
- **Archivos:** `calculations/comparativo.py` y `calculations/rubros.py` (reutilizan las familias), `reports/secciones.py`, `tests/test_fase11_horizontal.py`.
- **A considerar:** decidir si incluir también gastos de operación y resultado financiero, que ya existen como rubros.

### R-6. «No calculable» en lugar de la raya

- **Cambio:** mostrar el motivo en la celda: «Sin dato», «No calculable» o «No comparable».
- **Justificación:** hoy «—» reúne causas distintas, y solo la comparación de dos ejercicios las explica fila por fila. Lo pediste como criterio en la auditoría.
- **Archivos:** `calculations/comparativo.py`, `reports/secciones.py` (`formatear` y sus secciones), `reports/exportar_secciones.py`, las pruebas que esperan «—» y la frase correspondiente de la descripción.
- **A considerar:** textos más largos en columnas numéricas, lo que reduce el tamaño de letra en los PDF. Una opción más compacta es «N/C» con su leyenda.

### R-7. Nota de la utilidad operativa en la Tabla 5 de la aplicación

- **Cambio:** añadir la nota del documento y marcar la fila con †.
- **Justificación:** iguala aplicación y documento, y advierte del −21.25 % de 2023–2024. Sin otros ingresos en 2023, la variación sería −14.09 %.
- **Archivos:** `calculations/comparativo.py` o `reports/secciones.py`, una prueba nueva.

### R-8. Aviso de balance descuadrado o incompleto

- **Cambio:** mostrar un aviso en las páginas del apartado si un ejercicio no cuadra o no está completo.
- **Justificación:** en la prueba de la auditoría, con una diferencia de USD 1,000,000, las variaciones se calcularon sin ningún aviso. Con los datos actuales no aparecería ninguno.
- **Archivos:** `reports/analisis_alutech.py`, una prueba nueva.

### R-9. Formato uniforme de saldos sin cambio y de Excel

- **Cambio:** mostrar «0» y «0.00%» en saldos sin variación, e igualar Excel a la pantalla, incluidas las celdas sin valor.
- **Justificación:** «+0» sugiere un aumento inexistente, y la misma cifra se ve distinta según el formato.
- **Archivos:** `reports/secciones.py` (`formatear`), `reports/exportar_secciones.py`, pruebas de formato.

### R-10. Robustez y limpieza

- **Filas vacías:** quitar las 18 filas de la página oculta, procedentes de los ceros del catálogo en 2021. Sin borrar datos. Archivo: `calculations/comparativo.py`.
- **`CN7201` y `CN7202`:** presentar «Otros Ingresos (Gastos)» como una sola partida en el nivel de cuentas, para mostrar la variación de −867,141. Archivos: `calculations/comparativo.py`, y posiblemente `scripts/cargar_alutech.py` sin tocar la base de datos.
- **Tablas 3 y 4 por año:** formarlas por año, no por posición, para que un ejercicio faltante no altere sus títulos. Archivo: `reports/secciones.py`.
- **Justificación:** claridad y robustez. No cambia ninguna cifra actual de las Tablas 3 a 7.

### R-16. Auditores en los metadatos

- **Cambio:** corregir la descripción de 2022 y 2023 en el JSON de fuentes: las certificaciones indican KPMG, no PwC.
- **Justificación:** es un error de texto que no interviene en ningún cálculo.
- **Archivos:** `fuentes/alutech/estados_financieros_2021_2025.json`, solo el campo de descripción.
- **A considerar:** su hash cambiaría, aunque ningún importe. Por eso conviene una autorización expresa.
