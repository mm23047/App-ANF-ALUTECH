# Informe de auditoría previa a las correcciones — Proyecto ANF Alutech 2021–2025

Fecha: 2026-11-05. Rama `correcciones-auditoria`, HEAD `4506ed8`. Fases 0, 1, 2 y 3, en solo lectura: este informe es el único archivo creado en el proyecto. Los cálculos se ejecutaron en copias aisladas.

**Estado: en espera de tu autorización. No se implementó ninguna corrección.**

## 1. Resumen ejecutivo

| Tema | Resultado | Decisión que requiere |
|---|---|---|
| Integridad | Base de datos, documento y estados originales sin cambios; sin commits | Ninguna |
| Datos | PDF, transcripción y base coinciden en todos los importes | Ninguna |
| Composición de CxC 2024–2025 | **No comprobable.** Los estados tienen 2 páginas y no incluyen notas. La línea se llama «Deudores comerciales y Otras Cuentas por Cobrar» y existe por separado la de empresas relacionadas | Conseguir las notas |
| Base de CxC | **Cambio mi recomendación anterior:** ahora recomiendo comerciales + otras en cobros y en pagos (alternativa B2). La línea comercial no representa lo mismo en los cinco años | **Sí** |
| Conclusión del CCE | Con B2, el paso a negativo ocurre en 2024, no en 2023 | **Sí** |
| Cuenta de largo plazo de 2024 (9.7) | **No verificable con la documentación disponible.** Hay indicios convergentes de que es relacionada, pero ninguna prueba. La observación OBS-12 afirma de más | **Sí** |
| Figuras DuPont | 29 de 65 importes difieren de los estados. Las razones finales coinciden | **Sí** |
| Redondeo | 716 de 726 referencias numéricas son redondeo simple. Hay 1 truncamiento, 2 casos compatibles con redondeo doble, y el resto son diferencias de base | **Sí** |
| Aplicación | Una sola metodología y sin excepciones por año en los cálculos. Pantalla, PDF y Excel coinciden | Solo si cambia la base |
| Pruebas | **Tienen puntos débiles:** no detectaron un PDF con las filas invertidas ni una base financiera con filas erróneas | Autorizar su refuerzo |

## 2. Estado de integridad del proyecto

| Elemento | Resultado |
|---|---|
| Ruta | `C:\Users\estua\Documents\ANF\appfinanciera\` |
| Rama y commit | `correcciones-auditoria`, `4506ed8ff24906d44a3e7c22cba8e111094759db` |
| `git status` al iniciar | 55 entradas: 44 modificadas y 11 sin seguimiento. Sin commits nuevos. Todo se conservó |
| Informes en la carpeta indicada | **Diferencia con tu solicitud:** `unificacion_metodologica_20261105\` guarda el respaldo previo a esa tarea. Solo tiene `MATRIZ_CONCORDANCIA_ANF.md` en su versión anterior. Los tres informes vigentes están en la raíz del proyecto |

| Archivo | SHA-256 | Estado |
|---|---|---|
| `data/financiera.db` | `39ee373979fe9a72740c29e534ecdfe3e8c2ef0e145f7164c8b1a0675ebcba77` | Igual a la referencia |
| `Trabajo de investigación ANF.md` | `5d5e316425292d83e65a436a8a167239dfb1e0daf669442bd20828b23156b80c` | Igual |
| `Trabajo de investigación ANF.pdf` | `f6b0bc64738fad2b3e014b68d1aba06387a38c32ae05bcbea4de7f435509d957` | Igual |
| `fuentes/alutech/estados_financieros_2021_2025.json` | `c96af696ca71a3700c5a01a7833399a878b729cb80d5d1d014cb2feee8310321` | Igual |
| `fuentes/anf/resultados_referencia.json` | `d545fe53866449d93ab48698609ce124b2861b7901193c68d9b6efaabd43cc2f` | Vigente tras la unificación |
| `fuentes/anf/observaciones_validacion.json` | `2dd4dde804a708c108d12bc85077c9e190da66ced2720f6be421944dbbd599cb` | Vigente tras la unificación |
| `documentos/12_EEFF_diciembre_2024.pdf` | `be249cbf3ceb3d19d5b88fbc3d4d44aa04628b3482ce16a5b098691b950829b2` | Igual |
| `documentos/12_EEFF_diciembre_2025.pdf` | `b66cf4a3695e41828bd4c981eb97a0f9becebdd89ed58ba90b13ec6bb0035416` | Igual |
| `documentos/Balance general.pptx` | `b0471a2219cd298a93bb2240a24eaafd23896249969d5b9c17d4f1eef23e9386` | Igual |
| `documentos/Certificacin_EFC_…2021VF_Mod010925.pdf` | `a9e6f2e31fb39aa9b46fea1ca528960cb9a71c56f5dd9b7a02d71c96b0666d3f` | Igual |
| `documentos/Certificacin_EFC_…2022_VFMod_010925.pdf` | `addf42b4772d91a5e306b1ab22154add6641f3f3a4c510c983127d0f0439a270` | Igual |
| `documentos/Certificacin_EFC_…2023_VFMod010925.pdf` | `9019a54d71bf287b4e63bb1477b2f9673b2de749768df60a19abf588b9853f52` | Igual |
| `documentos/Estados-Financieros.pptx` | `06bc7e34aad5373a113caa152863c65a00c9a4da8eae60184e2b3c8b05958103` | Igual |
| `documentos/SV-CIALUTECH-202506.pdf` | `6d30a6facc4052e1adebaa18ac2e8efe87f4b007da2a381bfc8e2f0e9b2cae70` | Igual |
| `documentos/libro adm financ.pdf` | `eea6b01cc42eb81fbc538880aca89084c56aabf3e574fa5862a054c9aea16221` | Igual |

## 3. Fuentes consultadas y páginas

Las páginas son las del archivo PDF.

| Fuente | Páginas | Uso | Limitación |
|---|---|---|---|
| Certificación 2021 | 8 y 9 (balance), 10 (resultados), 12 (patrimonio) | CxC y CxP | Remite a notas adjuntas que no están en la carpeta |
| Certificación 2022 | 8 (balance), 12 (patrimonio) | CxC y CxP | Igual |
| Certificación 2023 | 6 y 7 (balance), 9 (resultados), 11 (patrimonio), 12 (flujos) | CxC, LP y controladora | Igual |
| `12_EEFF_diciembre_2024.pdf` | 1 y 2 | Estados 2024 | **Imagen escaneada, leída a la vista.** Sin notas ni columna comparativa |
| `12_EEFF_diciembre_2025.pdf` | 1 y 2 | Estados 2025 | Sin notas ni columna comparativa de 2024 |
| `SV-CIALUTECH-202506.pdf` (PCR) | 2, 3, 5 y 8 | Indicios | **«Estados Financieros no auditados»**; su 2023 no coincide con el certificado |
| Documento ANF | MD líneas 342–441, 732–776, 1185–1360 y 1782–1888; PDF 36–37, 54–56 y 72–74 | Metodología y figuras | — |
| `Balance general.pptx`, `Estados-Financieros.pptx` | Todas | Revisadas | Solo material general; no definen estos indicadores |
| `libro adm financ.pdf` | 690 págs. | Búsqueda automática de fórmulas | **No localicé las fórmulas con la búsqueda; no lo uso como evidencia** |

## 4. Composición de cuentas por cobrar por año

| Año | Cuenta presentada | Importe | Composición comprobada | Fuente y página | Clasificación |
|---:|---|---:|---|---|---|
| 2021 | Cuentas por cobrar comerciales - neto | 53,081,088 | Solo la denominación; neta de deterioro según el nombre | Cert. 2021, p. 8 | Comercial |
| 2021 | Otras cuentas por cobrar | 64,903,087 | **No comprobada** | Cert. 2021, p. 8 | Otras, corriente |
| 2021 | Cuentas por cobrar a partes relacionadas | 75,454,125 | Línea separada | Cert. 2021, p. 8 | Relacionada, corriente |
| 2022 | Cuentas por cobrar comerciales - neto | 32,581,092 | Solo la denominación | Cert. 2022, p. 8 | Comercial |
| 2022 | Otras cuentas por cobrar | 52,441,213 | **No comprobada** | Cert. 2022, p. 8 | Otras, corriente |
| 2022 | Cuentas por cobrar a partes relacionadas | 187,750,230 | Línea separada | Cert. 2022, p. 8 | Relacionada, corriente |
| 2023 | Cuentas por cobrar comerciales (neto) | 41,272,525 | Solo la denominación | Cert. 2023, p. 6 | Comercial |
| 2023 | Otras cuentas por cobrar | 54,824,958 | **No comprobada** | Cert. 2023, p. 6 | Otras, corriente |
| 2023 | Cuentas por cobrar a partes relacionadas | 168,293,969 | Línea separada | Cert. 2023, p. 6 | Relacionada, corriente |
| 2023 | Cuentas por cobrar a partes relacionadas | 110,380,709 | Línea separada | Cert. 2023, p. 7 | Relacionada, no corriente |
| 2023 | Otras cuentas por cobrar | 924,000 | **No comprobada** | Cert. 2023, p. 7 | Otras, no corriente |
| 2024 | Deudores comerciales y Otras Cuentas por Cobrar (Netos) | 97,204,415 | **No comprobada: sin notas** | EEFF 2024, p. 1 | Mixta por denominación |
| 2024 | Cuentas por cobrar Empresas Relacionadas | 182,232,841 | Línea separada | EEFF 2024, p. 1 | Relacionada, corriente |
| 2024 | Cuentas por cobrar a LP | 983,263 | **No comprobada** | EEFF 2024, p. 1 | No corriente |
| 2024 | Otras cuentas por cobrar a LP | 118,684,551 | **No comprobada** | EEFF 2024, p. 1 | No corriente; ver sección 6 |
| 2025 | Deudores comerciales y Otras Cuentas por Cobrar (Netos) | 70,169,882 | **No comprobada: sin notas** | EEFF 2025, p. 1 | Mixta por denominación |
| 2025 | Cuentas por cobrar Empresas Relacionadas | 77,574,661 | Línea separada | EEFF 2025, p. 1 | Relacionada, corriente |
| 2025 | Cuentas por cobrar a LP | 2,544,870 | **No comprobada** | EEFF 2025, p. 1 | No corriente |
| 2025 | Cuentas por cobrar Empresas Relacionadas a LP | 262,128,668 | Línea separada | EEFF 2025, p. 1 | Relacionada, no corriente |

### Respuestas a lo que pediste comprobar

| Pregunta | Respuesta | Certeza |
|---|---|---|
| ¿2024–2025 presentan una línea unificada? | **Sí:** «Deudores comerciales y Otras Cuentas por Cobrar (Netos)» | Comprobado en los PDF |
| ¿Contiene comerciales? | Según su nombre | Denominación, no composición |
| ¿Contiene otras cuentas por cobrar? | Según su nombre | Denominación, no composición |
| ¿Excluye relacionadas? | Se presentan en otra línea. **No se puede descartar** que contenga alguna partida relacionada | No comprobable sin notas |
| ¿Hay cambio de clasificación entre combinados y consolidados? | **Sí en la presentación:** cambian las denominaciones, las líneas y la entidad que reporta | Comprobado |
| ¿Se pueden desagregar deterioro y estimaciones? | **No.** Solo está el gasto de 2021–2023 (274,140; 397,016; 507,752); 2024–2025 no lo presentan | Comprobado |
| ¿Coincide la transcripción? | **Sí** en todos los importes, y los subtotales del balance cuadran con los impresos en los cinco años | Comprobado; 2024 a la vista |

**Respaldo adicional, con reservas:** PCR agrupa en «Cuentas y documentos por cobrar CP» 118.0 en dic-21, igual a comerciales + otras (117.98), y 97.2 en dic-24, igual a la línea unificada. Es un indicio de continuidad, no una prueba: no está auditado, y sus 84.1 de dic-22 y 109.5 de dic-23 no coinciden con 85.02 y 96.10.

## 5. Comparación de alternativas metodológicas

Mismos períodos, saldos al cierre, 365 días y operandos a 2 decimales en CO y CCE.

### Alternativa A: línea comercial (la vigente en la aplicación)

| | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|---:|
| Saldo CxC | 53,081,088 | 32,581,092 | 41,272,525 | 97,204,415 | 70,169,882 |
| Rotación | 9.87 | 15.34 | 11.60 | 4.93 | 6.27 |
| PPC | 36.98 | 23.80 | 31.47 | 74.07 | 58.25 |
| Ciclo operativo | 184.51 | 149.28 | 169.72 | 186.98 | 135.14 |
| PPP (CxP de línea comercial) | 155.65 | 85.95 | 191.12 | 217.70 | 190.66 |
| CCE | 28.86 | 63.33 | −21.40 | −30.72 | −55.52 |

### Alternativa B2: comerciales + otras en cobros y en pagos

| | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|---:|
| Saldo CxC | 117,984,175 | 85,022,305 | 96,097,483 | 97,204,415 | 70,169,882 |
| Rotación | 4.44 | 5.88 | 4.98 | 4.93 | 6.27 |
| PPC | 82.19 | 62.11 | 73.28 | 74.07 | 58.25 |
| Ciclo operativo | 229.72 | 187.59 | 211.53 | 186.98 | 135.14 |
| Saldo CxP | 165,241,990 | 105,484,253 | 207,727,338 | 225,126,517 | 173,120,913 |
| PPP | 164.23 | 93.83 | 202.98 | 217.70 | 190.66 |
| CCE | 65.49 | 93.76 | **8.55** | −30.72 | −55.52 |

### Otras alternativas

| Alternativa | CCE 2021–2025 | Por qué se descarta o se limita |
|---|---|---|
| **B1:** cobros como B, pagos como A | 74.07, 101.64, 20.41, −30.72, −55.52 | Trata de forma asimétrica cobros y pagos: los acreedores de 2024–2025 también incluyen «otras» |
| **C:** comercial estricta | 2021–2023 como A; 2024–2025 **No calculable** | La más pura en concepto, pero sin serie de cinco años. Útil como dato informativo |
| **D:** añadir relacionadas corrientes | 116.89, 200.08, 132.50, 106.12, 5.07 | PCR indica que provienen «principalmente de préstamos, pagos a proveedores y transferencias por anticipos». No son cobros de ventas, y además bajaron 104.7 millones en 2025 |

### Evaluación

| Criterio | A | B2 |
|---|---|---|
| ¿Representa lo mismo en los cinco años? | **No:** comercial hasta 2023, mixta después | **Sí, por denominación** |
| Variación de la base 2023→2024 | +135.5 %, en su mayor parte por presentación | +1.15 % |
| La usa el documento para comparar 2023–2025 | No | **Sí:** Tabla 4 y su nota |
| Pureza del concepto | Mejor en 2021–2023 | Incluye «otras» no comerciales en todos los años |
| Coincide con las cifras de 9.3 | **Sí** | Solo 2024–2025 |
| Cifras que habría que cambiar en el documento | Las de 2023 en 8.2 B | 2021–2023 en 8.2 B y 9.3, y conclusiones |

### Recomendación: B2

**Es la única serie que usa los mismos conceptos en los cinco años, y el propio documento la adopta en la Tabla 4 por esa razón.** Reconozco que **cambia mi recomendación anterior**, que favorecía A. Antes di más peso a la fórmula escrita en 9.3; al comprobar los estados, la continuidad de A resulta aparente, porque su etiqueta «comerciales» no describe 2024–2025.

**Por qué las otras son menos adecuadas:**
- **A** coincide con más cifras, pero mide cosas distintas antes y después de 2024; su salto de 31.47 a 74.07 días es en su mayor parte de presentación.
- **B1** mezcla bases entre cobros y pagos.
- **C** no permite una serie de cinco años.
- **D** mezcla financiamiento a relacionadas con cobro de ventas.

**Limitaciones de B2 que deben declararse:**
- El PPC y el PPP no miden solo cobros y pagos comerciales: incluyen «otras».
- La equivalencia en 2024–2025 se apoya en la denominación, no en las notas.
- **No es posible construir una serie estrictamente comercial de cinco años con los documentos disponibles.**

**Se debe conservar A como dato informativo** para 2021–2023, rotulada «solo comerciales», con 2024–2025 como «No separable».

### Efecto sobre las conclusiones

| Conclusión vigente | Con B2 |
|---|---|
| CCE negativo «a partir de 2023» (9.3, MD 1351) | Positivo en 2023 (+8.55); **negativo desde 2024** |
| «Giro estratégico» a partir de 2023 | Habría que reubicarlo en 2024 y advertir el cambio de presentación |
| Retrasos de cobro en 2024 (MD 1333) | De 73.28 a 74.07 días: **prácticamente sin cambio** |
| Cobranza «sumamente ágil» en 2021–2022 (8.2 B) | Válida solo para la línea comercial |
| PPC de 2021 a 2023 «entre 24 y 37 días» | Válida solo para la línea comercial |
| CCE negativo 2024–2025 (conclusiones, sección 11) | **Se mantiene** |

## 6. Reconstrucción de la cuenta de largo plazo de 2024

### Saldos

| Partida | 2023 (Cert., p. 7) | 2024 (EEFF, p. 1) | 2025 (EEFF, p. 1) |
|---|---:|---:|---:|
| Cuentas por cobrar a partes relacionadas, LP | 110,380,709 | Sin línea | 262,128,668 |
| Otras cuentas por cobrar, LP | 924,000 | **118,684,551** | Sin línea |
| Cuentas por cobrar a LP | Sin línea | 983,263 | 2,544,870 |

### Las dos reconstrucciones de 9.7

Comprobé la tabla publicada (MD 1793–1827): las sumas son correctas, y fuentes y usos cuadran.

| Tratamiento | Línea | Fuente | Uso | Total |
|---|---|---:|---:|---:|
| **Documento:** la trata como la misma partida | Relacionadas LP: 262,128,668 − 118,684,551 | — | 143,444,117 | **289,762,626** |
| **Líneas presentadas** | Otras LP desaparece | 118,684,551 | — | |
| | Relacionadas LP aparece | — | 262,128,668 | **408,447,177** |

La diferencia entre totales es 118,684,551. El efecto neto sobre los fondos es idéntico: solo cambia si se muestra bruto o neto.

### Evidencia

| A favor de que sea relacionada | En contra o neutral |
|---|---|
| En 2023 existía una cuenta LP relacionada de 110.4 millones, y en 2024 desaparece esa línea | **El estado de 2024 la llama «Otras»**, no relacionada |
| «Otras LP» de 2023 (924,000) es del orden de «Cuentas por cobrar a LP» de 2024 (983,263), no de 118.7 millones | PCR, en dic-24, la agrupa en «Cuentas por cobrar de LP» (119.7) con relacionadas LP en 0.0 |
| PCR, en jun-24: LP en 0.9 y relacionadas CP en 264.3; en dic-24: relacionadas CP en 182.2 y LP en 119.7 | PCR no está auditado |
| PCR, en jun-25: relacionadas LP en 121.9, igual a Los Pinares (80.1) + Ecotek (41.8), y LP de terceros en 4.4 | No hay nota del auditor ni detalle por deudor a dic-24 |

### Dictamen

**No verificable con la documentación disponible.** Los indicios apuntan a que es sustancialmente relacionada, pero ningún documento lo afirma para el 31-12-2024.

- La categoría «Error de clasificación» de OBS-12 **afirma de más**, y mi informe anterior («sin respaldo») también fue impreciso. Debe ser «No verificable».
- La cifra de 408,447,177 es la única que no depende de un supuesto. La de 289,762,626 es razonable, pero requiere declararlo.

### Recomendación

En 9.7, **presentar las líneas tal como figuran en los estados** (total 408,447,177) y añadir una nota con el neto de 143,444,117 y el motivo. La alternativa de conservar 289,762,626 con una nota de supuesto es aceptable, pero menos sólida, porque su cifra principal depende de algo no demostrado. Se resuelve definitivamente con la nota de partes relacionadas de los estados auditados de 2024.

## 7. Auditoría del ciclo operativo y del ciclo de conversión

| Elemento | 5.6 | 8.2 / 8.2 B / 8.2 C | 9.3 | ¿Contradicción? |
|---|---|---|---|---|
| Saldos | **Promedio** | **Cierre** | **Cierre** | **Sí** (D-7) |
| Base CxC | «Cuentas por cobrar» | Comercial, y comercial + otras en 2023 | «Comerciales» | **Sí** |
| Ventas | A crédito, o netas como aproximación | Ingresos ordinarios | Ingresos ordinarios | No: 5.6 lo permite |
| Base CxP | «Comerciales» | **«No es viable»** | Línea comercial | **Sí** (D-8) |
| Compras | A crédito; aproximación justificada | No aplica | Costo de ventas | No |
| Días | 365 | 365 | 365 | No |
| PPI | 365 / RI | 365 / Rotación | Inventarios / Costo × 365 | No: equivalentes sin redondear |
| PPC | 365 / RCC | 365 / Rotación | CxC / Ingresos × 365 | No |
| PPP | 365 / RCP | Declarado inviable | CxP / Costo × 365 | **Sí** |
| Ciclo operativo | No se define aparte | PPI + PPC, a 1 decimal | EPI + PPC, a 2 decimales | Precisión distinta |
| CCE | PPI + PPC − PPP | No se calcula | CO − PPP | No: equivalentes |
| Redondeo intermedio | No dice | Implícito | Implícito en el desarrollo | Sin regla escrita |

**Metodología realmente expresada:** el documento no tiene una sola. 5.6 es una definición general; 8.2 fija saldos al cierre; 9.3 es el único cálculo completo del ciclo. **Ninguna sección prevalece por sí misma**, por lo que hay que declararlo en el documento.

**Redacción propuesta (para 5.6 o el inicio de 8.2):**

> «Las fórmulas de esta sección son las definiciones generales, que usan saldos promedio. Por uniformidad de la serie y por no disponer de estados auditados con detalle de 2020, este trabajo calcula todos los indicadores con saldos al cierre. Se emplean los ingresos ordinarios como aproximación de las ventas a crédito y el costo de ventas como aproximación de las compras.
>
> Cuentas por cobrar y por pagar: los estados de 2021–2023 presentan por separado las partidas comerciales y otras; los de 2024–2025 las presentan en una sola línea. Para mantener una base comparable se utilizan, en los cinco años, las comerciales más las otras, excluidas las de partes relacionadas. Por ello, el período de cobro y el de pago no miden exclusivamente operaciones comerciales. Las notas de los estados no están disponibles para comprobar la composición de esa línea.»

(El texto sobre la base se ajustaría si no autorizas B2.)

En 8.2 C habría que sustituir la afirmación de que el PPP no es viable.

## 8. Auditoría de redondeo

| Valor | Exacto | Publicado | Naturaleza | Regla propuesta |
|---|---:|---:|---|---|
| PPC 2025, 8.2 B | 58.2482 | 58.3 | Compatible con **redondeo doble**: 58.25 → 58.3 | 58.25 en todo el documento |
| PPC 2025, 9.3 | 58.2482 | 58.25 | Simple, correcto | Conservar |
| CO 2025, 8.2 C | 135.1380 | 135.2 | Arrastra el 58.3 | 135.14 |
| CO 2025, 9.3 | 135.1380 | 135.14 | Correcto | Conservar |
| CO 2022 | 149.2855 | 149.28 | **Intermedio:** 125.48 + 23.80 | Decisión R-1 |
| CO 2023 | 169.7290 | 169.72 | **Intermedio:** 138.25 + 31.47 | Decisión R-1 |
| CCE 2021–2025 (A) | 28.8582; 63.3310; −21.3959; −30.7191; −55.5180 | 28.86; 63.33; −21.40; −30.72; −55.52 | Iguales con ambos procedimientos | — |
| PC / pasivo 2021, 8.3 A | 50.4053 | 50.40 | **Truncamiento** | 50.41 |
| WACC 2023, tabla | 3.8745 | 3.88 | Suma de aportes redondeados; **el texto de 9.4.3 dice 3.87** | 3.87 |
| Las demás referencias numéricas (716) | — | — | Redondeo simple, mitad hacia arriba | — |

**Aplicación:** interno sin redondear; intermedio solo en CO y CCE; presentación mitad hacia arriba, una vez. Queda un duplicado menor: `comparacion_anf._redondear` repite el criterio de `components/money.py`, sin efecto en los resultados.

**Límite de esta revisión:** cubre las 741 referencias, no cada cifra de la prosa.

**Regla propuesta para el documento y la aplicación:**

> «Los cálculos se realizan sin redondeo intermedio. Los resultados se presentan con dos decimales, redondeando una sola vez al valor más cercano, con los casos medios hacia arriba. Excepción: el ciclo operativo y el ciclo de conversión se calculan con sus componentes ya presentados a dos decimales, para que cada operación pueda comprobarse con las cifras de la tabla.»

**R-1:** ¿se mantiene esa excepción, o se elimina y se cambian 149.28 y 169.72 por 149.29 y 169.73? Recomiendo **mantenerla**: ya está implementada y permite comprobar las tablas a mano. El efecto es de 0.01 días.

**También habría que uniformar 8.2 a dos decimales**, para que no coexistan 147.5 y 147.53 del mismo indicador.

## 9. Auditoría de figuras DuPont

El PDF contiene 5 figuras (páginas 72 a 74). El Markdown solo incluye 2, de 2021 y 2024, con los mismos errores. Transcribí los importes a la vista y los comparé con los estados. **Conviene que revises esta transcripción sobre las imágenes.**

**Resultado: 29 de 65 importes difieren. Las 5 razones finales de cada figura son correctas**, porque ventas, ganancia neta, total de activos y patrimonio están bien en todas. **Los errores son de presentación, pero contradicen las tablas de 9.5 y 9.6 y los estados.**

| Año | Concepto | En la figura | Correcto (estados) | Diferencia |
|---:|---|---:|---:|---:|
| 2021 | Activos circulantes | 321,944,537 | 383,881,547 | −61,937,010 |
| 2021 | Activos no circulantes | 232,010,648 | 170,073,638 | +61,937,010 |
| 2022 | Costo de ventas | 388,240,555 | 410,331,156 | −22,090,601 |
| 2022 | Gastos de operación | 78,055,307 | 58,057,208 | +19,998,099 |
| 2022 | Gastos por intereses | 18,080,842 | 17,181,342 | +899,500 |
| 2022 | Impuestos | 5,217,420 | 3,960,325 | +1,257,095 |
| 2022 | Activos circulantes | 333,168,323 | 448,672,401 | −115,504,078 |
| 2022 | Activos no circulantes | 338,856,770 | 223,352,692 | +115,504,078 |
| 2022 | Pasivos circulantes | 227,979,029 | 231,944,180 | −3,965,151 |
| 2022 | Pasivos no circulantes | 230,169,300 | 226,204,149 | +3,965,151 |
| 2023 | Costo de ventas | 372,122,848 | 373,545,631 | −1,422,783 |
| 2023 | Gastos de operación | 77,245,412 | 63,602,388 | +13,643,024 |
| 2023 | Gastos por intereses | 14,508,739 | 22,016,927 | −7,508,188 |
| 2023 | Impuestos | 1,416,073 | 9,341,414 | −7,925,341 |
| 2023 | Activos circulantes | 378,285,662 | 429,794,544 | −51,508,882 |
| 2023 | Activos no circulantes | 430,815,284 | 379,306,402 | +51,508,882 |
| 2023 | Pasivos circulantes | 301,980,465 | 333,120,685 | −31,140,220 |
| 2023 | Pasivos no circulantes | 293,747,645 | 248,306,867 | +45,440,778 |
| 2023 | Total pasivos | 595,728,110 | 581,427,552 | +14,300,558 |
| 2024 | Costo de ventas | 354,864,973 | 377,459,424 | −22,594,451 |
| 2024 | Gastos de operación | 87,952,645 | 66,353,377 | +21,599,268 |
| 2024 | Gastos por intereses | 21,305,704 | 28,064,310 | −6,758,606 |
| 2024 | Impuestos | 11,822,416 | 4,124,197 | +7,698,219 |
| 2024 | Activos circulantes | 449,863,281 | 432,771,678 | +17,091,603 |
| 2024 | Activos no circulantes | 377,313,093 | 394,404,696 | −17,091,603 |
| 2024 | Pasivos circulantes | 303,442,160 | 362,966,215 | −59,524,055 |
| 2024 | Pasivos no circulantes | 299,654,120 | 238,148,371 | +61,505,749 |
| 2024 | Total pasivos | 603,096,280 | 601,114,586 | +1,981,694 |
| 2025 | Gastos por intereses | 38,210,582 | 37,399,011 | +811,571 |

**Observaciones:**
- **2025:** los 38,210,582 son gastos financieros netos más «otros» (811,571). Hace cuadrar la figura, pero el rótulo es incorrecto.
- **2021:** con sus cifras, las líneas de resultados suman 68,557,002, no 68,602,739: falta el efecto neto de deterioro y otros ingresos (+45,737).
- **2022 y 2023:** las líneas de resultados no cuadran con la ganancia neta, por 60 y −680.
- **2023 y 2024:** Total pasivos + patrimonio no iguala el total de activos, por 14,300,558 y 1,981,694.
- **Rótulos:** la de 2021 usa «Gastos operativos» y «Gastos financieros netos»; las demás, «Gastos de operación» y «Gastos por intereses».
- **Diseño:** la figura necesita una línea adicional («Otros, neto») para que los resultados sumen sin alterar nada.

## 10. Contradicciones documentales

| ID | Hallazgo | Efecto | Propuesta |
|---|---|---|---|
| **D-7** | 5.6 con promedios; 8.2 y 8.4 con cierre | Interpretación | Redacción de la sección 7. **Además, «no se dispone de 2020» es impreciso:** PCR tiene dic-20 sin auditar y la certificación 2021 tiene patrimonio de 2020 |
| **D-8** | 8.2 dice que los estados no desglosan acreedores comerciales y que el PPP no es viable; los estados sí presentan esa línea y 9.3 lo calcula | **Cálculo e interpretación** | Sustituir ese texto en 8.2 y 8.2 C |
| **D-10** | «Otros ingresos o gastos» aparece antes del resultado operativo en 7.1; en 2024–2025 se suma después | Interpretación | Nota al pie, o fila aparte después del resultado en 2024–2025 |
| **D-11** | 6.24 %\* y 9.34 %\* sin nota; 2023\* en 8.2 B tampoco | Editorial | Nota: «subtotal no impreso en los estados» |
| **D-12** | 8.3 B rotula «Gastos financieros» importes netos; 8.4 C cita el bruto | Interpretación | Rotular «netos» y aclarar el bruto |
| **D-13** | 2023: el estado de resultados atribuye 13,330,680 a la controladora (Cert., p. 9) y el de patrimonio, 12,309,102 + 1,021,578 no controladoras (p. 11). Cierre sin no controladoras, tras «Incorporación por adquisición» | **Cálculo:** ROE de la controladora 5.41 % o 5.86 % | Conservar 12,309,102, con nota. **Los estados no lo resuelven** |
| — | 2024–2025 no informan atribución a la controladora: se iguala a la ganancia total | **Cálculo:** es un supuesto | Declararlo en el documento |
| **D-14** | 9.5 y 9.6 mezclan «13,09 %», «$523.965.227» y «0.95 veces» | Editorial | Uniformar a 13.09 % y 523,965,227 |
| **D-15** | Índice: **29 de 51 entradas desfasadas**, desde 6.5, de +1 a +5 páginas | Editorial | Regenerar, tras cerrar los cambios |

## 11. Auditoría de la implementación

### Flujo seguido

`documentos/` → `fuentes/alutech/*.json` → `scripts/cargar_alutech.py` → base de datos → `calculations/balance_sheet.py` e `income_statement.py` → `rubros.py` → `indicadores.py` y `dupont.py` → `reports/secciones.py` → pantalla, `exportar_secciones.py` y `excel_export.py` / `pdf_export.py`.

### Cotejo por niveles

| Niveles | Alcance | Resultado |
|---|---|---:|
| Estados originales ↔ JSON | 308 importes y totales: 249 con búsqueda en el texto del PDF; 59 de 2024, a la vista | Sin diferencias |
| Subtotales impresos ↔ suma de cuentas | AC, ANC, PC, PNC y patrimonio, 5 años | Sin diferencias |
| JSON ↔ base de datos | 247 importes (ejecutado en esta sesión, sobre una copia); más 18 ceros de 2021 | Sin diferencias |
| Recálculo independiente ↔ aplicación | 837 celdas, sin usar funciones de producción | Sin diferencias |
| Aplicación ↔ documento | 837 celdas | **5 difieren** |
| Pantalla ↔ PDF ↔ Excel | 29 filas de indicadores, leyendo los archivos generados | Sin diferencias |

### Hallazgos

| Metodología | Resultado |
|---|---|
| ¿Una sola fórmula en los cinco años? | **Sí.** Sin condiciones por año en los cálculos |
| ¿Fórmulas duplicadas? | No en estos indicadores. WACC usa su propio Ke, igual al ROE |
| ¿Literales de año en el código? | Solo en notas y títulos, no en cálculos (p. ej. `_NOTA_2023_2024`, «Indicadores financieros 2021–2025») |
| **Etiqueta** | **Problema:** «Rotación de cuentas por cobrar comerciales» y «PPC» muestran en 2024–2025 una línea mixta. Hay advertencia, pero el rótulo es inexacto |

### Referencias y matriz

| Comprobación | Resultado |
|---|---|
| Referencias frente al documento vigente | 365 contra la celda exacta, sin diferencias; 361 por presencia en el texto, ninguna ausente (menor certeza) |
| Derivados separados | **Sí**, los 5 de E-CPF |
| **Observaciones con fundamento** | **Parcial: OBS-12 afirma un «Error de clasificación» no demostrado** |
| Clasificación en la matriz | **Coincidencia metodológica sobrestimada.** Marca «Coincide» en PPC 9.3 de 2024–2025, aunque el documento los llama «comerciales», y en la utilidad de la controladora 2024–2025, que es un supuesto |
| Campos de la matriz | **Le faltan** datos usados, resultado exacto y fuente con página, que pides en la fase 4.3 |
| Alcance de la matriz | No incluye 9.4 ni 9.7 |
| Id duplicado | `D-RA`, en 8.2 D y 9.5; heredado y sin efecto hoy |

### Errores en mis informes anteriores

| Dónde | Decía | Correcto |
|---|---|---|
| `INFORME_UNIFICACION…`, sección 8 | PPP 202.97 y CCE +8.56, con base homogénea | PPP **202.98** y CCE **+8.55** con operandos a 2 decimales; +8.56 solo con el valor exacto |
| `INFORME_UNIFICACION…`, sección 1 | 832 con «coincidencia metodológica» | Sobrestimado, por lo indicado arriba |
| `INFORME_UNIFICACION…` | Justificaba la línea comercial como base única | Ver sección 5: la evidencia favorece B2 |
| `INFORME_AUDITORIA_RUBRICA…`, D-4 | «Sin respaldo documental» | No verificable, con indicios |

### Revisión de las pruebas

Introduje errores en copias y ejecuté la suite completa:

| Error introducido | ¿Detectado? |
|---|---|
| Excel con columnas invertidas | **Sí**, por `test_fase8`, no por las pruebas nuevas de esa exportación |
| PPP con otras cuentas por pagar | **Sí** |
| Cuenta mal agrupada en la transcripción | **Sí**, al compararla con el documento |
| **PDF con filas en orden inverso** | **NO** |
| **Base financiera con filas repetidas** | **NO** |

| Debilidad | Dónde | Efecto |
|---|---|---|
| Buscan una cifra **en cualquier parte** del PDF o de la hoja | `test_pdf_y_excel_…`, `test_actividad_y_deuda_…` | No comprueban fila ni columna |
| Prueba casi vacía, repetida 5 veces | `test_bases_financieras_de_los_ratios` | Solo revisa el título y el número de filas |
| El recálculo usa el `grupo` de la transcripción | `concordancia_documento.py` | Un error de agrupación solo se ve al comparar con el documento |
| Conteos fijos | Validación, 741 y 711 | Detectan cambios, no su causa |
| Observaciones | Solo se exige que la causa no esté vacía | No valida su contenido |
| Código sin usar | `_publicada` en `test_fase9_rubrica.py` | Sin efecto |

**Lo que sí es sólido:** las referencias leen el documento y recalculan con fracciones, y en la tarea anterior detectaron los 8 fallos de metodología introducidos. Son buenas para fórmulas y bases; **débiles para la posición de las cifras en las exportaciones**.

**Prueba adicional que no sirvió:** vaciar parcialmente el texto de OBS-12 no se detectó, pero mi cambio solo quitaba el inicio del texto. No la cuento como evidencia.

## 12. Matriz de diferencias

| ID | Problema | Evidencia documental | Resultado de auditoría | Corrección propuesta | Archivo afectado | Requiere autorización |
|---|---|---|---:|---|---|---|
| H-01 | Base de CxC no uniforme | Cert. 2021–2023 p. 8/6; EEFF p. 1; Tabla 4; 8.2 B; 9.3 | A no representa lo mismo los 5 años | Adoptar B2 y conservar A como informativo | Documento; `calculations/rubros.py`, `indicadores.py`; reportes | **Sí, académica** |
| H-02 | Base de CxP asimétrica | Acreedores comerciales y Otras, EEFF p. 1 | Debe seguir a H-01 | CxP comerciales + otras | Igual | **Sí** |
| H-03 | CCE «a partir de 2023» | MD 1351; sección 5 | Depende de H-01 | Reescribir 9.3 y sección 11 | Documento | **Sí** |
| H-04 | Composición 2024–2025 no comprobable | Sin notas | No verificable | Obtener notas; declarar la limitación | Documento | **Sí** |
| H-05 | 9.7: cuenta LP 2024 | EEFF 2024 p. 1; PCR p. 3, 8 | No verificable | Líneas presentadas y nota con el neto | Documento; `fuentes/anf/` | **Sí** |
| H-06 | OBS-12 afirma de más | Sección 6 | Sobrestimada | Categoría «No verificable» | `observaciones_validacion.json` | Sí |
| H-07 | PPC 2025: 58.3 | MD 767; 9.3 | Redondeo doble probable | 58.25 | Documento | **Sí** |
| H-08 | CO 2025: 135.2 | MD 776; 9.3 | Arrastre | 135.14 | Documento | **Sí** |
| H-09 | Sin regla de redondeo | Todo el documento | Falta | Añadir regla; decidir R-1 | Documento | **Sí** |
| H-10 | 50.40 % y 3.88 % | 8.3 A; 9.4 | Truncamiento y suma | 50.41 % y 3.87 % | Documento | **Sí** |
| H-11 | Figuras DuPont | PDF p. 72–74 | 29 de 65 | Rehacer las 5 con la tabla de la sección 9 | PDF y Markdown | **Sí** |
| H-12 | 5.6 frente a 8.2 | MD 381; 738 | Contradicción | Redacción de la sección 7 | Documento | **Sí** |
| H-13 | 8.2 C: PPP «no viable» | MD 739, 773; 9.3 | Contradicción | Reescribir | Documento | **Sí** |
| H-14 | D-10, 11, 12, 14 y 15 | Sección 10 | Interpretación y editorial | Notas, rótulos, formato e índice | Documento | **Sí** |
| H-15 | Controladora 2023 y 2024–2025 | Cert. 2023 p. 9 y 11 | Conflicto en las fuentes; supuesto | Notas | Documento | **Sí** |
| H-16 | Rótulo «comerciales» en 2024–2025 | Sección 11 | Inexacto | Rótulo según H-01 | `calculations/indicadores.py`, `reports/` | Sí |
| H-17 | Matriz incompleta y sobrestimada | Sección 11 | Faltan campos | Regenerar según 4.3 | `MATRIZ_CONCORDANCIA_ANF.md` | Sí |
| H-18 | Pruebas no verifican posición | Mutaciones | 2 errores sin detectar | Comparar por fila y columna | `tests/` | Sí |
| H-19 | Errores en informes anteriores | Sección 11 | PPP y CCE | Fe de erratas o corrección | Informes | Sí |

## 13. Correcciones propuestas

### Documento académico

1. Sección 5.6 u 8.2: declarar criterio, bases y regla de redondeo.
2. 8.2 B: cinco años con una sola base, con nota de cambio de presentación.
3. 8.2 C: sustituir el texto del PPP y actualizar el ciclo, con 2 decimales.
4. 9.3: tablas, desarrollo por año y análisis según la base aprobada. **Si es B2, cambian 2021, 2022 y 2023.**
5. Sección 11 y 9.3: conclusiones del CCE.
6. 9.7: presentación de la cuenta de largo plazo.
7. Figuras DuPont: 5 figuras.
8. D-10 a D-15 y H-10.
9. **Actualizar el PDF en coherencia.** El documento proviene de Google Docs; si existe el original, es mejor corregirlo allí, porque el PDF actual ya es una reconstrucción parcial.

### Aplicación

1. Base única según H-01 y H-02, en `rubros.py`, sin condición de año.
2. Indicadores y rótulos: la serie principal y la línea comercial informativa, «No separable» en 2024–2025.
3. Advertencias y notas de Actividad.
4. Referencias y observaciones según el documento ya corregido.
5. Matriz con los campos de la fase 4.3.

**Orden importante:** el documento debe corregirse primero o a la vez, porque si no, las referencias no tendrían versión publicada contra la cual comparar.

## 14. Riesgos y limitaciones

| Riesgo | Efecto | Mitigación |
|---|---|---|
| **Corregir el documento altera un trabajo ya revisado o entregado** | Cambian cifras y conclusiones de 2021–2023 | Decisión tuya; conservar una versión anterior |
| **Sin notas, B2 se apoya en la denominación** | Podría no ser exactamente equivalente | Declararlo; pedir las notas |
| **PCR no está auditado** | Solo sirve como indicio | No usarlo como fuente de cifras |
| **Transcripción de figuras y de 2024 hecha a la vista** | Posible error humano | Revisar en las imágenes |
| **PDF reconstruido** | Cambios adicionales pueden desalinear páginas | Corregir la fuente en Google Docs, si existe |
| **Repositorio remoto público** | Un `push` publicaría el documento | No se hará; ya está prohibido |
| **Cotejo de prosa por presencia** | Puede haber cifras en texto no verificadas | Revisar las secciones que se reescriban |

## 15. Archivos que sería necesario modificar

| Grupo | Archivos |
|---|---|
| **Documento** | `Trabajo de investigación ANF.md`, `Trabajo de investigación ANF.pdf` |
| **Cálculo** | `calculations/rubros.py`, `calculations/indicadores.py` |
| **Reportes** | `reports/secciones.py`, `reports/indicadores_financieros.py` |
| **Referencias** | `fuentes/anf/resultados_referencia.json`, `fuentes/anf/observaciones_validacion.json` |
| **Pruebas** | `tests/concordancia_documento.py`, `tests/test_fase9_rubrica.py`, `tests/test_fase10_metodologia.py`, `tests/test_alutech.py`, `tests/test_fase8_vertical_dupont.py` y otras que dependan de las cifras |
| **Documentación** | `MATRIZ_CONCORDANCIA_ANF.md`, `README.md`, `REGISTRO_DE_CAMBIOS.md`, informes |

**No se tocarían:** la base de datos, `fuentes/alutech/` ni `documentos/`. No haría falta ninguna migración.

## 16. Pruebas que deberían agregarse o actualizarse

| Prueba | Detecta |
|---|---|
| Composición de CxC por año desde códigos de cuenta y línea del estado | Cuenta equivocada, sin depender del `grupo` |
| Serie B2 y línea comercial, los cinco años, con «No separable» | Mezcla de bases |
| CxP simétrica con CxC | Asimetría |
| Lectura del PDF y del Excel **por fila y columna** | Filas o columnas invertidas |
| Filas exactas de la base financiera de cada ratio | Conceptos equivocados |
| Clasificación de la cuenta LP 2024 como «No verificable» | Afirmaciones sin respaldo |
| Figuras: importes contra estados, si se rehacen como tablas de datos | Regresión de las correcciones |
| Regla de redondeo, incluido el caso 58.2482 | Doble redondeo |
| Referencias con origen: publicada, derivada o no verificable | Coincidencias sin cifra propia |
| **Sustituir** `test_bases_financieras_de_los_ratios` por una versión con contenido, sin eliminar ningún caso | Prueba casi vacía |
| Nueva ronda de errores introducidos, incluidos los dos no detectados | Fuerza de la suite |

## 17. Decisiones que requieren autorización académica

| # | Decisión | Mi recomendación | Alternativa y por qué es menos adecuada |
|---:|---|---|---|
| **1** | **Base de CxC y CxP** | **B2:** comerciales + otras, sin relacionadas, los 5 años. Línea comercial como informativa en 2021–2023 | **A:** conserva las cifras de 9.3, pero mide cosas distintas antes y después de 2024 |
| **2** | **Conclusión del CCE** | Reescribir: negativo desde 2024, con advertencia por cambio de presentación. Conclusión general: **se mantiene** para 2024–2025 | Mantenerla: solo es válida si eliges A |
| **3** | **9.7, cuenta de largo plazo** | Líneas presentadas (408,447,177) y nota con el neto. Clasificar «No verificable» | 289,762,626 con nota: razonable, pero su cifra principal depende de un supuesto |
| **4** | **Solicitar notas de 2024 y 2025** | Sí, si puedes obtenerlas. Resolverían 3 hallazgos | Seguir sin ellas: todo queda declarado como limitación |
| **5** | **Regla de redondeo y R-1** | La regla propuesta, manteniendo operandos a 2 decimales en CO y CCE | Eliminar la excepción: obliga a cambiar 149.28 y 169.72 |
| **6** | **58.3, 135.2, 50.40 % y 3.88 %** | 58.25, 135.14, 50.41 % y 3.87 % | Dejarlos con nota: conserva cifras incorrectas o incoherentes |
| **7** | **Figuras DuPont** | Rehacer las 5, con una línea «Otros, neto» y rótulos uniformes. Regenerarlas exige herramienta gráfica o reemplazo por imágenes nuevas | Una nota que aclare los errores: no los corrige |
| **8** | **Controladora 2023 y supuesto 2024–2025** | Conservar 12,309,102 y añadir notas | 13,330,680: daría 5.86 %, pero ignora el estado de patrimonio |
| **9** | **D-7, D-8, D-10 a D-15** | Aplicar las propuestas | — |
| **10** | **¿Se puede modificar el documento?** | Solo tras confirmar que no se ha entregado una versión definitiva | **Es la decisión que condiciona las demás** |

### Si no autorizas cambiar el documento

Mantendría la aplicación con A, corregiría solo rótulos y notas, pruebas, matriz y OBS-12, y las diferencias con 8.2 B quedarían documentadas.

**Se autoriza por número.** No hay ninguna corrección implementada, ni commit, ni push.
