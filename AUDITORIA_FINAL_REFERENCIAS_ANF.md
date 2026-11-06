# Auditoría final de concordancia académica e integridad de referencias ANF

Fecha: 2026-11-05. Rama `correcciones-auditoria`, HEAD `4506ed8`. Revisión de solo lectura: no se modificó ningún archivo del proyecto ni del respaldo. Los cálculos se hicieron en copias aisladas.

## Resumen

| Pregunta | Respuesta |
|---|---|
| ¿Se modificó alguna referencia para ocultar diferencias? | **No.** Las 37 referencias corregidas coinciden con el documento vigente, y las 6 diferencias restantes quedaron intactas |
| ¿La integridad del proyecto está confirmada? | **Sí.** Base de datos, documento y estados sin cambios; sin commits nuevos; sin cambios sin documentar |
| ¿Existe concordancia total? | **No.** Hay 9 celdas que no coinciden (7 valores distintos): 3 son una diferencia metodológica real y 6 son de redondeo |
| ¿Corrijo algo de mi informe anterior? | **Sí.** Cinco afirmaciones eran inexactas o incompletas; ver el anexo |
| ¿Se puede autorizar el commit? | **Sí, con dos condiciones**; ver sección 10 |

**Hallazgo principal:** el problema de 2023 no es de presentación. El signo del ciclo de conversión de efectivo de 2023 cambia según la base usada: −21.40, +8.56 o +20.41 días. Eso afecta una conclusión del documento.

## 1. Integridad de los dos JSON

### `fuentes/anf/resultados_referencia.json`

La comparación contra el respaldo se hizo fila por fila y por posición.

| Cambio | Cantidad | Detalle |
|---|---:|---|
| Valores modificados | 37 | Todos pasan de «Diferencia» a «Coincide» |
| Filas agregadas | 1 (5 valores) | `E-CPF`, sección 8.3 C |
| Notas quitadas de «fuera de alcance» | 1 | La de 8.3 C, porque ahora se compara |
| Metadatos alterados (sección, tabla, métrica, unidad, decimales) | 0 | |
| Filas eliminadas | 0 | |
| `calculations/comparacion_anf.py` (criterios y tolerancia) | Sin cambios | Igual al respaldo |

**Motivo de los 37:** el documento fue corregido en la fase del 2026-11-03 y el JSON no se había actualizado. Las cifras anteriores (541,094,544, 342,120,685, 231,914,180 y 31,200,000) están 5, 5, 4 y 1 veces en la versión del documento del commit `4506ed8`, y **ninguna vez** en el Markdown ni en el PDF vigentes.

**Impacto en Validación:** de 672 / 6 / 43 / 0 / 15 (736 valores) a 714 / 6 / 6 / 0 / 15 (741 valores).

| Efecto | Coinciden | Diferencias |
|---|---:|---:|
| Base | 672 | 43 |
| 37 referencias al día | +37 | −37 |
| 5 valores de `E-CPF` | +5 | 0 |
| **Final** | **714** | **6** |

### Dictamen sobre `E-CPF`

**Legítima, pero más débil que las otras.** El documento no publica esas cinco cifras en 8.3 C: dice que el índice «iguala matemáticamente» a la razón de 8.3 B, y yo copié los valores de 8.3 B. No ocultan ninguna diferencia, pero **suman 5 coincidencias sin una cifra publicada propia**. Sin ellas el resultado sería 709 / 6 / 6 / 0 / 15.

### `fuentes/anf/observaciones_validacion.json`

| Elemento | Resultado |
|---|---|
| OBS-07 a OBS-13 | Vigentes, idénticas al respaldo |
| OBS-01 a OBS-06 | Movidas sin cambios a `observaciones_historicas`, con nota; ya no se aplican porque esas cifras ya no están en el documento |
| Eliminadas | 0 |
| Formato | El archivo se reescribió entero al serializarlo: el hash cambia también por formato, no solo por contenido |

### Dictamen

**Ninguna referencia se modificó para ocultar o reducir artificialmente diferencias.** Evidencia:

- Los 37 valores actuales son iguales a lo publicado hoy, celda por celda.
- Los tres saldos primarios coinciden con los totales impresos en las certificaciones; los demás son aritmética de esos saldos.
- Las referencias que aún difieren (`B-CXC`, `B-RCC`, `B-PPC` y `FU25-*`) no se tocaron.
- La tolerancia de comparación no cambió.

## 2. Comparación con el documento académico

### Cotejo de todas las referencias

| Método | Valores | Resultado | Solidez |
|---|---:|---|---|
| Contra la celda exacta de las tablas vigentes | 365 | 0 desiguales | Alta |
| Por presencia de la cifra en el texto del documento (8.x, 9.x, WACC, prosa) | 361 | 0 ausentes | **Media:** una cifra puede aparecer en otro lugar |
| «No calculable» | 15 | Coinciden con la aplicación | Alta |
| **Total** | **741** | | |

**Markdown frente a PDF:** las 2,291 cifras de las tablas de las secciones 6 a 9 están en el PDF. Es una búsqueda por cadena, no celda por celda. Las siete cifras disputadas se ubicaron en ambas versiones.

### Las 37 modificaciones

Motivo común: la cifra anterior corresponde a la versión previa del documento. Las líneas y páginas son las del documento vigente.

| Ref. | Año | Anterior | Actual | Publicado hoy | MD, línea | PDF, pág. | Respaldo primario | Validación |
|---|---:|---:|---:|---:|---:|---:|---|---|
| T3-AC | 2023 | 541,094,544 | 429,794,544 | 429,794,544 | 500 | 23 | Impreso 429,794,544 (CERT_2023, p. 7) | Diferencia → Coincide |
| T3-AC-VA | 2023 | 92,422,143 | -18,877,857 | -18,877,857 | 500 | 23 | Aritmética de saldos impresos | Diferencia → Coincide |
| T3-AC-VR | 2023 | 20.60 | -4.21 | -4.21 | 500 | 23 | Aritmética de saldos impresos | Diferencia → Coincide |
| T3-PC | 2022 | 231,914,180 | 231,944,180 | 231,944,180 | 501 | 23 | Impreso 231,944,180 (CERT_2022, p. 9) | Diferencia → Coincide |
| T3-PC | 2023 | 342,120,685 | 333,120,685 | 333,120,685 | 501 | 23 | Impreso 333,120,685 (CERT_2023, p. 7) | Diferencia → Coincide |
| T3-PC-VA | 2022 | 25,940,950 | 25,970,950 | 25,970,950 | 501 | 23 | Aritmética de saldos impresos | Diferencia → Coincide |
| T3-PC-VA | 2023 | 110,206,505 | 101,176,505 | 101,176,505 | 501 | 23 | Aritmética de saldos impresos | Diferencia → Coincide |
| T3-PC-VR | 2022 | 12.59 | 12.61 | 12.61 | 501 | 23 | Aritmética de saldos impresos | Diferencia → Coincide |
| T3-PC-VR | 2023 | 47.52 | 43.62 | 43.62 | 501 | 23 | Aritmética de saldos impresos | Diferencia → Coincide |
| T4-AC | 2023 | 541,094,544 | 429,794,544 | 429,794,544 | 515 | 24 | Impreso 429,794,544 (CERT_2023, p. 7) | Diferencia → Coincide |
| T4-AC-VA | 2024 | -108,322,866 | 2,977,134 | 2,977,134 | 515 | 24 | Aritmética de saldos impresos | Diferencia → Coincide |
| T4-AC-VR | 2024 | -20.02 | 0.69 | 0.69 | 515 | 24 | Aritmética de saldos impresos | Diferencia → Coincide |
| T4-PC | 2023 | 342,120,685 | 333,120,685 | 333,120,685 | 516 | 24 | Impreso 333,120,685 (CERT_2023, p. 7) | Diferencia → Coincide |
| T4-PC-VA | 2024 | 20,845,530 | 29,845,530 | 29,845,530 | 516 | 24 | Aritmética de saldos impresos | Diferencia → Coincide |
| T4-PC-VR | 2024 | 6.09 | 8.96 | 8.96 | 516 | 24 | Aritmética de saldos impresos | Diferencia → Coincide |
| T5-UO | 2022 | 31,200,000 | 31,200,977 | 31,200,977 | 533 | 25–26 | Suma de partidas impresas; el documento muestra la suma | Diferencia → Coincide |
| T6-AC | 2023 | 541,094,544 | 429,794,544 | 429,794,544 | 555 | 27 | Impreso 429,794,544 (CERT_2023, p. 7) | Diferencia → Coincide |
| T6-PC | 2022 | 231,914,180 | 231,944,180 | 231,944,180 | 554 | 26 | Impreso 231,944,180 (CERT_2022, p. 9) | Diferencia → Coincide |
| T6-PC | 2023 | 342,120,685 | 333,120,685 | 333,120,685 | 555 | 27 | Impreso 333,120,685 (CERT_2023, p. 7) | Diferencia → Coincide |
| T6-CTN | 2022 | 216,758,221 | 216,728,221 | 216,728,221 | 554 | 26 | Aritmética de saldos impresos | Diferencia → Coincide |
| T6-CTN | 2023 | 198,973,859 | 96,673,859 | 96,673,859 | 555 | 27 | Aritmética de saldos impresos | Diferencia → Coincide |
| T6-CTN-VA | 2022 | 38,849,904 | 38,819,904 | 38,819,904 | 554 | 26 | Aritmética de saldos impresos | Diferencia → Coincide |
| T6-CTN-VA | 2023 | -17,784,362 | -120,054,362 | -120,054,362 | 555 | 27 | Aritmética de saldos impresos | Diferencia → Coincide |
| T6-CTN-VA | 2024 | -129,168,396 | -26,868,396 | -26,868,396 | 556 | 27 | Aritmética de saldos impresos | Diferencia → Coincide |
| T6-CTN-VR | 2022 | 21.84 | 21.82 | 21.82 | 554 | 26 | Aritmética de saldos impresos | Diferencia → Coincide |
| T6-CTN-VR | 2023 | -8.20 | -55.39 | -55.39 | 555 | 27 | Aritmética de saldos impresos | Diferencia → Coincide |
| T6-CTN-VR | 2024 | -64.92 | -27.79 | -27.79 | 556 | 27 | Aritmética de saldos impresos | Diferencia → Coincide |
| T6-RC | 2023 | 1.58 | 1.29 | 1.29 | 555 | 27 | Aritmética de saldos impresos | Diferencia → Coincide |
| T6-PA | 2023 | 1.17 | 0.87 | 0.87 | 555 | 27 | Aritmética de saldos impresos | Diferencia → Coincide |
| T7-CTN | 2022 | 216,758,221 | 216,728,221 | 216,728,221 | 576 | 28 | Aritmética de saldos impresos | Diferencia → Coincide |
| T7-CTN | 2023 | 198,973,859 | 96,673,859 | 96,673,859 | 577 | 28 | Aritmética de saldos impresos | Diferencia → Coincide |
| T7-CTN-VA | 2022 | 38,849,904 | 38,819,904 | 38,819,904 | 576 | 28 | Aritmética de saldos impresos | Diferencia → Coincide |
| T7-CTN-VA | 2023 | -17,784,362 | -120,054,362 | -120,054,362 | 577 | 28 | Aritmética de saldos impresos | Diferencia → Coincide |
| T7-CTN-VA | 2024 | -129,168,396 | -26,868,396 | -26,868,396 | 578 | 28 | Aritmética de saldos impresos | Diferencia → Coincide |
| T7-CTN-VR | 2022 | 21.84 | 21.82 | 21.82 | 576 | 28 | Aritmética de saldos impresos | Diferencia → Coincide |
| T7-CTN-VR | 2023 | -8.20 | -55.39 | -55.39 | 577 | 28 | Aritmética de saldos impresos | Diferencia → Coincide |
| T7-CTN-VR | 2024 | -64.92 | -27.79 | -27.79 | 578 | 28 | Aritmética de saldos impresos | Diferencia → Coincide |

## 3. Análisis de las nueve diferencias

Las 9 celdas son 7 valores distintos, porque el ciclo operativo de 2022 y de 2023 se publica en dos tablas de 9.3.

| # | Valor | Publicado | Aplicación | Dónde | Naturaleza | En Validación |
|---:|---|---:|---:|---|---|---|
| 1 | CxC 2023 | 96,097,483 | 41,272,525 | 8.2 B, MD 767, PDF 36 | **Metodológica** | Diferencia |
| 2 | Rotación CxC 2023 | 4.98 | 11.60 | 8.2 B | **Metodológica** | Diferencia |
| 3 | PPC 2023 | 73.3 | 31.47 | 8.2 B | **Metodológica** | Diferencia |
| 4 | PPC 2025 | 58.3 | 58.25 | 8.2 B, PDF 36–37 | Redondeo, presentación | Por redondeo |
| 5–6 | CO 2022 | 149.28 | 149.29 | 9.3, MD 1328 y 1346 | Convención de redondeo | Por redondeo |
| 7–8 | CO 2023 | 169.72 | 169.73 | 9.3, MD 1329 y 1347 | Convención de redondeo | Por redondeo |
| 9 | CO 2025 | 135.2 | 135.14 | 8.2 C, MD 776, PDF 37 | Redondeo arrastrado | Por redondeo |

## 4. Metodología de cuentas por cobrar de 2023

### Cuentas y saldos

| Año | Línea del estado | Saldo | Fuente |
|---:|---|---:|---|
| 2021 | Cuentas por cobrar comerciales + Otras cuentas por cobrar | 53,081,088 + 64,903,087 | Cert. 2021, p. 8 |
| 2022 | Las mismas | 32,581,092 + 52,441,213 | Cert. 2022, p. 8 |
| 2023 | Las mismas | 41,272,525 + 54,824,958 | Cert. 2023, p. 6 |
| 2024 | Deudores comerciales y Otras Cuentas por Cobrar, una sola línea | 97,204,415 | EEFF 2024, p. 1 |
| 2025 | La misma | 70,169,882 | EEFF 2025, p. 1 |

### Reconstrucción

Ingresos 2023: 478,623,072.

| Base 2023 | Saldo | Rotación | PPC |
|---|---:|---:|---:|
| 9.3: comerciales | 41,272,525 | 478,623,072 / 41,272,525 = 11.5967 | 365 / 11.5967 = 31.4746 |
| 8.2 B: comerciales + otras | 96,097,483 | 478,623,072 / 96,097,483 = 4.9806 | 365 / 4.9806 = 73.2844 |

### Las series, año por año

| Serie | 2021 | 2022 | 2023 | 2024 | 2025 | Quiebre |
|---|---:|---:|---:|---:|---:|---|
| 8.2 B publicada, PPC | 37.0 | 23.8 | **73.3** | 74.1 | 58.3 | Entre 2022 y 2023, por decisión del análisis |
| 9.3 publicada, PPC | 36.98 | 23.80 | **31.47** | 74.07 | 58.25 | Entre 2023 y 2024, por cambio de presentación |
| Homogénea (comerciales + otras), PPC | 82.19 | 62.11 | 73.28 | 74.07 | 58.25 | Ninguno; 2021–2022 no están publicados |

### Por qué difieren

- **8.2 B** une comerciales y otras desde 2023 para poder comparar con 2024–2025, que presentan una sola línea. Lo explica en la prosa («incluyendo "otras cuentas por cobrar" a partir de 2023»). El asterisco de 2023 no tiene nota al pie.
- **9.3** define la fórmula con «Cuentas por cobrar comerciales» y usa la línea presentada. En 2024–2025 esa línea ya incluye otras, aunque la columna siga llamándose «comerciales».

### Qué respalda el documento

**Ambas están documentadas y ninguna es homogénea.** Las dos aritméticas son correctas.

| Criterio | 8.2 B | 9.3 |
|---|---|---|
| Fórmula escrita | Genérica: «Cuentas por cobrar» | Explícita: «comerciales» |
| Cálculo desarrollado | Tabla | Tabla y desarrollo por año |
| Sostiene el CCE publicado | No | **Sí** |
| Publica la rotación de CxC | **Sí, es el único lugar** | No, solo PPC |
| Comparable 2023–2024 | **Sí** | No |
| Comparable 2022–2023 | No | **Sí** |

### Consecuencia académica

| Base | CCE 2023 | Signo |
|---|---:|---|
| 9.3, publicada | −21.40 | Negativo |
| CxC de 8.2 B con PPP de 9.3 | +20.41 | Positivo |
| Comerciales + otras en cobros y en pagos | +8.56 | Positivo |

El documento afirma que el CCE se tornó negativo «a partir de 2023» y lo presenta como un giro estratégico. **Con las bases homogéneas, el cambio de signo ocurre en 2024**, no en 2023 (65.49, 93.76, 8.56, −30.72 y −55.52). Además, 9.3 atribuye el ciclo de 2024 a «retrasos de cobro», pero el salto de 31.47 a 74.07 días incluye el cambio de presentación. Un tercer pasaje dice que el PPC de 2021 a 2023 estuvo «entre 24 y 37 días», contrario a los 73 días de 8.2 B.

### Evaluación

- **Conservar 9.3 en la aplicación es defendible** como cálculo principal: tiene fórmula explícita, regla única y es la base del CCE publicado.
- **Pero no basta: el documento necesita una unificación académica.** La rotación de 2023 que muestra la aplicación (11.60) no está publicada en ninguna parte; la única publicada es 4.98.
- **No se puede resolver en la aplicación sin una excepción por año**, porque 2022 y 2023 tienen las mismas cuentas y 8.2 B las trata distinto. La aplicación ya muestra 4.98 y 73.28 como variante.

## 5. Redondeo de 2025

| Paso | Resultado |
|---|---|
| Datos | 70,169,882 / 439,704,567 × 365 |
| Exacto | **58.248217** |
| A 2 decimales (9.3) | 58.25 |
| A 1 decimal, directo | **58.2** |
| Primero a 2 y luego a 1 decimal, mitad hacia arriba | **58.3** |
| 365 / rotación ya redondeada (6.27) | 58.21, a 1 decimal 58.2 |

**Criterio identificado:** el único procedimiento probado que da 58.3 es el doble redondeo. Es una inferencia: el documento no enuncia ninguna regla de redondeo. En los otros cuatro años de 8.2 B, el redondeo directo y el doble dan lo mismo.

**Dictamen: es exclusivamente de presentación, 0.05 días.** No hay cambio de cuenta, base ni fórmula, y el documento publica 58.25 en 9.3. Sin embargo, a la precisión publicada de 8.2 B, 58.3 no es el redondeo correcto. Se arrastra al 135.2 de 8.2 C.

## 6. Ciclo operativo

### Metodología escrita

La fórmula es CO = EPI + PPC. El documento no da una regla de redondeo, pero **su desarrollo escrito suma las cifras ya redondeadas**: «CO = 147.53 + 36.98» (9.3, 2021), «125.48 + 23.80» y «138.25 + 31.47» (MD 1328–1329).

### Recálculo de los cinco años

| Año | EPI exacto | PPC exacto | **CO sin redondear** | A 2 decimales | **Operandos redondeados (EPI + PPC)** | Publicado 9.3 | Diferencia |
|---:|---:|---:|---:|---:|---|---:|---:|
| 2021 | 147.530016 | 36.976876 | 184.506892 | 184.51 | 147.53 + 36.98 = 184.51 | 184.51 | 0 |
| 2022 | 125.484857 | 23.800691 | 149.285548 | **149.29** | 125.48 + 23.80 = **149.28** | 149.28 | 0.01 |
| 2023 | 138.254412 | 31.474604 | 169.729016 | **169.73** | 138.25 + 31.47 = **169.72** | 169.72 | 0.01 |
| 2024 | 112.907178 | 74.069131 | 186.976309 | 186.98 | 112.91 + 74.07 = 186.98 | 186.98 | 0 |
| 2025 | 76.889776 | 58.248217 | 135.137993 | 135.14 | 76.89 + 58.25 = 135.14 | 135.14 | 0 |

**El procedimiento de operandos redondeados reproduce los cinco valores de 9.3.** Corresponde a la metodología tal como está escrita. El cálculo sin redondear es más exacto, pero no es lo que el documento desarrolla.

**El CCE no se ve afectado:** da 28.86, 63.33, −21.40, −30.72 y −55.52 con ambos procedimientos, igual a lo publicado.

### Sección 8.2 C, a un decimal

| Año | Publicado | Operandos a 1 decimal | Exacto a 1 decimal |
|---:|---:|---|---:|
| 2024 | 187.0 | 112.9 + 74.1 = 187.0 | 187.0 |
| 2025 | 135.2 | 76.9 + 58.3 = 135.2 | 135.1 |

El 135.2 hereda el 58.3 analizado en la sección 5; con 58.2 daría 135.1. Además contradice el 135.14 de 9.3 para el mismo año.

### Dictamen

Son diferencias de **0.01 días y de convención, no errores** de 9.3. La aplicación usa el cálculo exacto. Para 9.3 existe una regla general, sin excepción por año, que eliminaría las 4 celdas: sumar EPI y PPC redondeados a 2 decimales. **El 135.2 de 8.2 C no se debe reproducir**, porque depende del doble redondeo.

## 7. Integridad de la base de datos y los documentos

| Comprobación | Resultado |
|---|---|
| `data/financiera.db` | `39ee3739…ebcba77`: **igual** a la referencia y al respaldo |
| Contenido de la base, en copia y solo lectura | 247 de 247 importes iguales a `fuentes/alutech/`. Otras 18 filas: las cuentas en cero de 2021, conocidas |
| `documentos/` (estados financieros originales) | 9 archivos: **sin cambios** |
| `fuentes/alutech/estados_financieros_2021_2025.json` | **Sin cambios** |
| `Trabajo de investigación ANF.md` y `.pdf` | `5d5e3164…` y `f6b0bc64…`: **sin cambios** |
| `fuentes/anf/supuestos_wacc.json` | **Sin cambios** |
| Cambios respecto del respaldo | 27 archivos modificados y 5 nuevos, **todos documentados** en la sección 11 del informe. Ninguno adicional |
| `data/backups/` | 5 archivos, sin cambios |
| Literales numéricos en el código nuevo | Solo formatos y notas de texto. **Sin resultados escritos a mano** |
| Git | HEAD `4506ed8` y misma rama. **Sin commits nuevos** ni `stash` |
| Suite, en copia nueva | **656 de 656** |

### ¿El respaldo corresponde a la línea base?

**Sí.** Se reconstruyó la línea base desde el commit `4506ed8` más el parche guardado, y se comparó con el respaldo:

| Elemento | Resultado |
|---|---|
| Manifiesto SHA-256 | 118 de 118 correctos |
| Reconstrucción contra respaldo, sin contar finales de línea | 105 archivos, 0 distintos |
| Solo en el respaldo | 6, esperados: 3 que estaban sin seguimiento al inicio y 3 registros de Streamlit ignorados por Git |
| Base de datos y PDF | Comparados por hash: iguales |

**Debo declarar algo que no te informé:** en la tarea anterior ejecuté una recolección de pruebas dentro del respaldo para comparar listas, lo que creó carpetas `__pycache__`. Las borré y el manifiesto volvió a validar; ningún archivo original cambió. Aun así, fue una escritura en un respaldo que debía quedar intacto.

## 8. Riesgos identificados

| Nivel | Riesgo | Efecto |
|---|---|---|
| **Alto, académico** | La conclusión «CCE negativo a partir de 2023» depende de la base | Quien evalúe el trabajo puede cuestionarla |
| **Medio** | La rotación 2023 de la aplicación (11.60) no está en el documento | Diferencia visible para quien compare 8.2 B con la pantalla |
| **Medio** | Figuras DuPont del PDF con importes intermedios erróneos | Sus cifras no se pueden reproducir |
| **Medio** | El repositorio remoto es público y el commit incluye el trabajo académico | **Un `git push` publicaría nombres y documentos excluidos** |
| Bajo | El commit mezcla 30 archivos anteriores a esta tarea con los de esta tarea | Historial difícil de revisar |
| Bajo | `E-CPF` cuenta como coincidencia sin cifra publicada | Infla el contador en 5 |
| Bajo | Id duplicado `D-RA` en las referencias, ya en la línea base (8.2 D y 9.5) | Una observación por id se aplicaría a ambas filas; hoy ninguna lo usa |
| Bajo | OBS-07 dice «como señala su asterisco», pero no hay nota al pie | Texto impreciso |
| Bajo | El cotejo de 361 referencias de prosa es por presencia | Menor certeza que el de tablas |

## 9. Decisiones académicas pendientes

| # | Decisión | Opciones | Recomendación |
|---:|---|---|---|
| 1 | **Base de CxC de 2023** | a) Mantener las dos bases, con aviso. b) Unificar en 9.3. c) Serie homogénea | **Unificar el documento:** en 8.2 B, publicar 2023 con ambas bases en filas separadas, y conservar 9.3 como base del CCE |
| 2 | **Conclusión del CCE 2023** | Mantener el texto, o aclarar que el signo depende de la base | **Aclararlo**, aunque decidas otra cosa en la 1 |
| 3 | **Ciclo operativo de 9.3** | a) Mantener el cálculo exacto. b) Sumar operandos a 2 decimales | **b)**, por ser lo que el documento escribe y una regla general. Elimina 4 celdas y no altera el CCE |
| 4 | **8.2 B y 8.2 C de 2025** | Corregir 58.3 y 135.2 en el documento, o dejarlas documentadas | Corregir a 58.2 y 135.1, o usar 58.25 y 135.14 |
| 5 | **`E-CPF`** | Conservar o quitar | Conservar, pero separarla de las coincidencias con cifra publicada |
| 6 | **Figuras DuPont del PDF** | Rehacerlas o aclarar su alcance | Rehacerlas, si el documento se volverá a entregar |

## 10. Recomendación final

**Sí: el proyecto está listo para autorizar el commit, como respaldo técnico del estado actual, no como declaración de concordancia total.** La integridad está confirmada, las referencias son legítimas y la suite pasa. Ninguna decisión pendiente se resuelve mejor sin un commit previo que proteja este trabajo.

### Condiciones

1. **Que `INFORME_AUDITORIA_RUBRICA_ANF.md` no entre tal como está**, o que entre junto con este informe, para no versionar sin corregir las afirmaciones señaladas en el anexo.
2. **No hacer `git push`** de esta rama a `origin`, que es público.

### Lo que el commit no significa

Permanecen 9 celdas sin coincidir. **No existe concordancia total** y las 3 de cuentas por cobrar siguen sin resolverse académicamente. La aprobación final del trabajo debería esperar a las decisiones 1 y 2.

## Anexo. Correcciones a mi informe anterior

`INFORME_AUDITORIA_RUBRICA_ANF.md` sigue sin cambios, porque esta revisión es de solo lectura.

| Sección | Decía | Corrección |
|---|---|---|
| Conclusión | Los 9 valores «no se sustentan con la fórmula aplicada a los datos originales, o contradicen otra sección» | **Demasiado fuerte.** Los 4 del ciclo operativo de 9.3 sí salen de la fórmula con los operandos que el documento escribe |
| 8, D-3 | Corregir «exigiría redondeo intermedio», como si fuera un impedimento | Es una decisión, no un impedimento: hay una regla general posible |
| 8, D-1, y recomendación | Mantener 9.3 porque mantiene «una regla única» | **Incompleto.** Omití que 9.3 también tiene quiebre en 2023–2024, que 11.60 no está publicado y que el signo del CCE 2023 depende de la base |
| 1 y 6 | «828 de 837 valores» | Son **celdas**, no valores únicos: una misma cifra se repite en varias tablas. Las 9 diferencias son 7 valores distintos |
| 6 | 714 coincidencias en Validación | Incluye los 5 valores derivados de `E-CPF` |
