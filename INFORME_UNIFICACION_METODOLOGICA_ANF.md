# Unificación metodológica de la aplicación con el documento ANF

**Alutech, S. A. de C. V., y subsidiarias – División Acero · 2021–2025**
Fecha: 2026-11-05. Rama: `correcciones-auditoria`. Sin commit. Anexo: [MATRIZ_CONCORDANCIA_ANF.md](MATRIZ_CONCORDANCIA_ANF.md).

## 1. Resumen de la auditoría

| Medida | Antes | Ahora |
|---|---:|---:|
| Celdas publicadas (rúbrica) que difieren | 9 de 837 | **5 de 837** |
| Diferencias atribuibles al software | 4 | **0** |
| Validación: coinciden / por redondeo / derivados / difieren / no aplican | 714 / 6 / 0 / 6 / 15 | **711 / 4 / 5 / 6 / 15** |
| Pruebas | 656 de 656 | **695 de 695** |

La aplicación ya aplica una sola metodología, igual en los cinco años, y cada resultado se recalculó de forma independiente desde los estados originales.

**No hay concordancia total con el documento.** Las 5 celdas restantes vienen de inconsistencias internas del documento; reproducirlas exigiría una excepción para 2023 o un doble redondeo, ambos prohibidos. Requieren una decisión académica tuya.

### Cómo leer los resultados

| Concepto | Significado | Situación |
|---|---|---|
| **Coincidencia numérica** | La cifra es igual a la publicada | 832 de 837 celdas |
| **Coincidencia metodológica** | Además, misma cuenta, base, fórmula, período, signo y redondeo | Las mismas 832 |
| **Exactitud matemática** | La cifra es el redondeo del valor exacto | Todo, salvo CO 2022 y 2023 (0.01 días, procedimiento del documento) y las 5 diferencias |
| **Resultado derivado** | No hay cifra publicada propia | 5 valores de 8.3 C, contados aparte |
| **Inconsistencia del documento** | Contradice otra sección o su propia regla | 5 celdas |

## 2. Metodología identificada en el documento

| Elemento | Criterio del documento | Dónde |
|---|---|---|
| Datos | Estados financieros de 2021–2025 | 6.2 |
| Saldos | Al cierre, no promedios. 5.6 los define con promedios; 8.2 fija el cierre y es el que se aplica | 8.2, 8.4 |
| Días del período | 365 | 8.2, 9.3 |
| Ventas a crédito y compras | Se aproximan con ingresos ordinarios y costo de ventas | 8.2 B, 9.3 |
| Gastos financieros | Netos de ingresos financieros | Tabla 5, 8.3 B |
| Precisión intermedia | Sin redondeo en razones y DuPont («12.3842 % × 3.81194») | 9.6 |
| Ciclo operativo y CCE | Operandos a 2 decimales («125.48 + 23.80 = 149.28») | 9.3 |
| Regla de redondeo | **No se enuncia.** Se deduce de las tablas | — |

**Versiones del documento:** Markdown del 2026-11-03 16:59 y PDF del 2026-11-03 17:56, sin cambios desde entonces. Las 2,291 cifras de las tablas de las secciones 6 a 9 del Markdown aparecen en el PDF (búsqueda por cadena, no celda por celda). Las secciones 8.2 B, 8.3 C y 9.3 dicen lo mismo en ambas versiones. Las figuras DuPont solo se revisaron en el PDF.

## 3. Diferencias metodológicas encontradas

| # | Diferencia | Causa | Tratamiento |
|---:|---|---|---|
| 1 | CO 2022 y 2023 en 9.3 (4 celdas) | **Software:** sumaba valores exactos y el documento suma operandos a 2 decimales | **Corregido** |
| 2 | CxC 2023 en 8.2 B (3 celdas) | **Documento:** cambia de base solo en 2023 | Regla única en la aplicación; documentado |
| 3 | PPC 2025 en 8.2 B | **Documento:** 58.3 exige redondear dos veces | No se reproduce; documentado |
| 4 | CO 2025 en 8.2 C | **Documento:** hereda el 58.3 y contradice el 135.14 de 9.3 | No se reproduce; documentado |
| 5 | 8.3 C contada como coincidencia | **Software:** presentaba un derivado como cifra publicada | **Corregido** |
| 6 | Redondeos mezclados en presentación | **Software:** mitad al par en unas tablas y mitad hacia arriba en otras. Sin efecto en las cifras actuales | **Corregido** |

## 4. Las dos bases de cuentas por cobrar de 2023

### Cuentas de los estados originales

Certificación 2023, página 6 del PDF, verificada directamente en el archivo:

| Cuenta | Saldo 2023 | 8.2 B | 9.3 |
|---|---:|:---:|:---:|
| Cuentas por cobrar comerciales (neto) | 41,272,525 | Sí | Sí |
| Otras cuentas por cobrar | 54,824,958 | Sí | No |
| Cuentas por cobrar a partes relacionadas | 168,293,969 | No | No |
| **Base** | | **96,097,483** | **41,272,525** |

### Reconstrucción

| Sección | Saldo | Rotación (478,623,072 / saldo) | Período de cobro |
|---|---:|---:|---:|
| 9.3 | 41,272,525 | 11.5967 | 31.4746 |
| 8.2 B | 96,097,483 | 4.9806 | 73.2844 |

### ¿Son el mismo indicador?

**Sí.** Ambas secciones llaman al resultado «período promedio de cobro» y coinciden en 2021, 2022, 2024 y 2025. Solo difieren en 2023:

| Año | 8.2 B | 9.3 | Regla de 8.2 B |
|---:|---:|---:|---|
| 2021 | 53,081,088 | 53,081,088 | Línea comercial |
| 2022 | 32,581,092 | 32,581,092 | Línea comercial |
| **2023** | **96,097,483** | **41,272,525** | **Comerciales + otras** |
| 2024 | 97,204,415 | 97,204,415 | Línea única |
| 2025 | 70,169,882 | 70,169,882 | Línea única |

2022 y 2023 tienen las mismas cuentas y 8.2 B las trata distinto. **El propio documento tiene una excepción para 2023.**

### Metodología única aplicada

**Indicador principal: línea comercial presentada (fórmula explícita de 9.3), en los cinco años.** La elegí porque:

- Es la única sección con la fórmula escrita con esa cuenta y desarrollada año por año.
- Es la base del CO y del CCE que publica el documento.
- Usa una sola regla. Seguir 8.2 B exigiría la excepción para 2023 que prohibiste.

No la elegí por coincidir con más tablas. **Consecuencia que debes conocer:** la rotación 2023 (11.60) no está publicada; la única publicada es 4.98.

**Limitación:** esta base también tiene un quiebre entre 2023 y 2024, inevitable, porque los estados de 2024–2025 unen ambas líneas. La aplicación lo advierte.

**Indicador aparte: comerciales y otras, también en los cinco años.** Reproduce 96,097,483, 4.98 y 73.28. Aparece en la tabla «Cuentas por cobrar: dos bases que no son equivalentes», en pantalla, PDF y Excel.

| Base | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|---:|
| Línea comercial: saldo | 53,081,088 | 32,581,092 | 41,272,525 | 97,204,415 | 70,169,882 |
| Línea comercial: rotación | 9.87 | 15.34 | 11.60 | 4.93 | 6.27 |
| Línea comercial: período | 36.98 | 23.80 | 31.47 | 74.07 | 58.25 |
| Comerciales y otras: saldo | 117,984,175 | 85,022,305 | 96,097,483 | 97,204,415 | 70,169,882 |
| Comerciales y otras: rotación | 4.44 | 5.88 | 4.98 | 4.93 | 6.27 |
| Comerciales y otras: período | 82.19 | 62.11 | 73.28 | 74.07 | 58.25 |

### Corrección académica propuesta

No modifiqué el documento. En 8.2 B, usar 41,272,525, 11.60 y 31.5 en 2023 y agregar: «Si se incluyen las otras cuentas por cobrar (54,824,958), la cartera de 2023 es 96,097,483, con una rotación de 4.98 veces y 73.3 días; esa base es la comparable con la línea única de 2024–2025». También habría que ajustar la prosa de 8.2 B y explicar el asterisco de 2023, que no tiene nota.

## 5. Correcciones realizadas en la aplicación

1. **Ciclo operativo y CCE** siguen el procedimiento escrito de 9.3, con una regla general.
2. **Redondeo único** en `components/money.py`, usado por tablas, indicadores e interpretaciones. Las interpretaciones ahora muestran la misma cifra que las tablas (58.25, no 58.2).
3. **Nueva tabla de las dos bases de CxC**, en pantalla, PDF y Excel.
4. **Nuevo estado «Resultado derivado»** en Validación para los 5 valores de 8.3 C.
5. **Observaciones actualizadas:** OBS-07, OBS-08 y OBS-09 con la causa precisa; OBS-14 nueva.

**Sin cambios, porque ya coincidían:** liquidez, rotaciones, PPI, PPP, endeudamiento, rentabilidad y DuPont. Tampoco cambió `calculations/dupont.py`.

## 6. Fórmulas implementadas

| Indicador | Fórmula | Base | Sección |
|---|---|---|---|
| Capital de trabajo | AC − PC | Cierre | 8.1 C, 9.2.1 |
| Razón corriente | AC / PC | Cierre | 8.1 A |
| Prueba ácida | (AC − Inventarios) / PC | Cierre | 8.1 B |
| Tesorería | (Efectivo + inversiones corrientes) / PC × 100 | Cierre | 9.1 |
| Rotación de inventarios | Costo de ventas / Inventarios | Cierre | 8.2 A |
| PPI / EPI | Inventarios / Costo de ventas × 365 | Cierre | 8.2 A, 9.3 |
| Rotación de CxC | Ingresos / CxC línea comercial | Cierre | 8.2 B, base 9.3 |
| PPC | CxC línea comercial / Ingresos × 365 | Cierre | 9.3 |
| PPP | CxP línea comercial / Costo de ventas × 365 | Cierre | 9.3 |
| **Ciclo operativo** | **PPI a 2 decimales + PPC a 2 decimales** | Cierre | 9.3 |
| **CCE** | **CO − PPP a 2 decimales** | Cierre | 9.3 |
| Rotación de activos | Ingresos / Activo total | Cierre | 8.2 D |
| Endeudamiento | Pasivo / Activo × 100 | Cierre | 8.3 A |
| Cobertura de intereses | Utilidad de operación / Gastos financieros netos | Ejercicio | 8.3 B |
| **Cobertura de pagos fijos** | **Misma función que 8.3 B** | Ejercicio | 8.3 C |
| Deuda-capital | Pasivo / Patrimonio | Cierre | 8.3 D |
| Márgenes bruto, operativo y neto | Utilidad / Ingresos × 100 | Ejercicio | 8.4 A–C |
| ROA y ROE | Ganancia neta / Activo o Patrimonio × 100 | Cierre | 8.4 E–F |
| DuPont | Margen × Rotación × MAF, sin redondeo intermedio | Cierre | 9.5, 9.6 |

### Cobertura de pagos fijos (8.3 C)

La sección 8.3 C **no da fórmula ni cifras**: dice que el índice «iguala matemáticamente» a 8.3 B por falta de desglose. La fórmula general es la del texto de finanzas, no del documento.

- **Datos:** la utilidad de operación y los gastos financieros netos están disponibles en los cinco años.
- **Validez:** la igualdad es matemáticamente válida solo con arrendamientos y amortización del principal en cero. Es un supuesto por falta de datos, no un hecho: **no mide la cobertura real**, como advierte el propio documento.
- **Implementación:** ya era una función compartida, sin valores copiados en el cálculo.

## 7. Criterios de redondeo

| Capa | Regla |
|---|---|
| Precisión interna | Decimal sin redondear |
| Redondeo intermedio | **Solo** CO y CCE, porque 9.3 lo escribe: 2 decimales |
| Presentación | Mitad hacia arriba, una sola vez, con una función central |
| Pantalla y PDF | Misma función, misma cifra |
| Excel | Guarda el valor y lo muestra con formato de 2 decimales |

**Período de cobro 2025:** 70,169,882 / 439,704,567 × 365 = 58.2482. Los datos, la base y los 365 días coinciden con 9.3. A 2 decimales da 58.25, como 9.3; a 1 decimal da 58.2. El 58.3 de 8.2 B solo sale de redondear dos veces, **así que no se reproduce**.

## 8. Resultados de los cinco períodos

| Concepto | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---:|---:|---:|---:|---:|
| PPI | 147.53 | 125.48 | 138.25 | 112.91 | 76.89 |
| PPC | 36.98 | 23.80 | 31.47 | 74.07 | 58.25 |
| **Ciclo operativo** | **184.51** | **149.28** | **169.72** | **186.98** | **135.14** |
| PPP | 155.65 | 85.95 | 191.12 | 217.70 | 190.66 |
| **CCE** | **28.86** | **63.33** | **−21.40** | **−30.72** | **−55.52** |
| CO exacto, solo como referencia | 184.5069 | 149.2855 | 169.7290 | 186.9763 | 135.1380 |
| Cobertura de intereses | 4.76 | 1.82 | 2.03 | 1.25 | 1.46 |
| Pagos fijos (derivado) | 4.76 | 1.82 | 2.03 | 1.25 | 1.46 |

Los cinco valores de CO y de CCE son iguales a 9.3.

### Sensibilidad del CCE 2023

| Base | PPI | PPC | PPP | CCE | Signo |
|---|---:|---:|---:|---:|---|
| **9.3: la que usa la aplicación** | 138.25 | 31.47 | 191.12 | **−21.40** | Negativo |
| CxC de 8.2 B con PPP de 9.3 | 138.25 | 73.28 | 191.12 | +20.41 | Positivo |
| Comerciales + otras en cobros y en pagos | 138.25 | 73.28 | 202.97 | +8.56 | Positivo |

**La conclusión de 9.3 («a partir de 2023 … negativo») es válida con la metodología de 9.3**, y por eso se mantiene en la aplicación. **Pero depende de la base.** Con cobros y pagos en base homogénea, los cinco años son 65.49, 93.76, 8.56, −30.72 y −55.52: el cambio de signo ocurre en 2024. Parte del salto 2023–2024 es, además, un cambio de presentación. Si unificas de otra forma, habría que corregir esa conclusión.

## 9. Matriz completa de concordancia

Las 837 celdas, con fórmula, base, resultado, diferencia, estado y clasificación, están en [MATRIZ_CONCORDANCIA_ANF.md](MATRIZ_CONCORDANCIA_ANF.md).

| Clasificación | Celdas |
|---|---:|
| Coinciden | 832 |
| Error de implementación | **0** |
| Diferencia de datos | **0** |
| Diferencia de metodología atribuible al software | **0** |
| Inconsistencia del documento, base de CxC 2023 | 3 |
| Inconsistencia del documento, redondeo (PPC 2025 y CO 8.2 C) | 2 |
| **Total** | **837** |
| Derivados, sin cifra publicada, contados aparte | 5 |

| Indicador | Año | Publicado | Aplicación, a esa precisión | Diferencia | Clasificación |
|---|---:|---:|---:|---:|---|
| CxC (8.2 B) | 2023 | 96,097,483 | 41,272,525 | −54,824,958 | Inconsistencia del documento |
| Rotación CxC (8.2 B) | 2023 | 4.98 | 11.60 | +6.62 | Inconsistencia del documento |
| PPC (8.2 B) | 2023 | 73.3 | 31.5 | −41.8 | Inconsistencia del documento |
| PPC (8.2 B) | 2025 | 58.3 | 58.2 | −0.1 | Redondeo, inconsistencia del documento |
| CO (8.2 C) | 2025 | 135.2 | 135.1 | −0.1 | Redondeo, inconsistencia del documento |

**Validación** cuenta 741 valores porque abarca también WACC, 9.7 y textos. Sus 6 diferencias son las 3 de CxC 2023 y las 3 de la clasificación de una cuenta en 9.7, ambas del documento.

## 10. Resultados de pruebas

| Concepto | Resultado |
|---|---|
| Suite completa, en copia aislada | **695 aprobadas, 0 fallidas, 0 omitidas** |
| Nuevas | 39, en `tests/test_fase10_metodologia.py` |
| Eliminadas | **0** |
| Ajustadas por el cambio legítimo | `test_alutech.py` (3 pruebas), `test_fase8_vertical_dupont.py` (1), la lista de discrepancias de `test_fase9_rubrica.py`, `concordancia_documento.py` y `humo_horizontal.py` |

Las referencias se leen del documento o se calculan con fracciones desde los estados originales, sin usar `calculations/`.

Para comprobar que las pruebas detectan errores, introduje 8 fallos en copias, uno a la vez, y **los 8 se detectaron**: suma exacta en CO; PPP sin redondear en CCE; CO a 1 decimal; excepción de 2023 en el PPC; cartera total como base única; doble redondeo; pagos fijos desligado de 8.3 B, y E-CPF contado como coincidencia.

**Pantalla, PDF y Excel:** las pruebas comparan las cifras de los tres formatos en Actividad y Endeudamiento. La pantalla real se comprobó con AppTest. Revisé en Excel real 12 libros, sin `###` ni errores, y vi la primera página del PDF de Actividad. **No abrí esta versión en un navegador ni pulsé sus descargas.**

## 11. Archivos modificados

Cambios de esta tarea, respecto del respaldo:

| Archivo | Motivo |
|---|---|
| `calculations/indicadores.py` | CO y CCE según 9.3, redondeo central e interpretaciones |
| `calculations/comparacion_anf.py` | Estado «Resultado derivado» |
| `components/money.py` | Función pública de redondeo |
| `reports/secciones.py` | Tabla de las dos bases y redondeo central |
| `reports/indicadores_financieros.py` | Tabla en Actividad y advertencia del procedimiento |
| `fuentes/anf/resultados_referencia.json` | Marca `E-CPF` como derivada; **sin cambiar ningún valor** |
| `fuentes/anf/observaciones_validacion.json` | OBS-07, OBS-08 y OBS-09 corregidas; OBS-14 nueva |
| `tests/concordancia_documento.py`, `tests/test_fase9_rubrica.py`, `tests/test_alutech.py`, `tests/test_fase8_vertical_dupont.py`, `tests/humo_horizontal.py` | Expectativas según la metodología |
| `tests/test_fase10_metodologia.py` | **Nuevo** |
| `MATRIZ_CONCORDANCIA_ANF.md` | Regenerada con fórmula, base y clasificación |
| `INFORME_AUDITORIA_RUBRICA_ANF.md` | Nota de actualización al inicio |
| `AUDITORIA_FINAL_REFERENCIAS_ANF.md` | **Copiado** desde mi carpeta temporal, porque no estaba en el proyecto |
| `README.md`, `REGISTRO_DE_CAMBIOS.md` | Documentación |
| Este informe | **Nuevo** |

**Respaldo:** `C:\Users\estua\Documents\ANF\respaldos_appfinanciera\unificacion_metodologica_20261105\`, con 123 archivos y manifiesto SHA-256 verificado. El respaldo anterior se mantiene intacto: 118 de 118 archivos correctos.

## 12. Integridad de la base de datos

`data/financiera.db`: `39ee373979fe9a72740c29e534ecdfe3e8c2ef0e145f7164c8b1a0675ebcba77`. **Sin cambios.** No hubo migración ni reconstrucción; las pruebas usaron copias.

## 13. Integridad de los documentos originales

| Archivo | SHA-256 | Estado |
|---|---|---|
| `Trabajo de investigación ANF.md` | `5d5e3164…` | Sin cambios |
| `Trabajo de investigación ANF.pdf` | `f6b0bc64…` | Sin cambios |
| `fuentes/alutech/estados_financieros_2021_2025.json` | `c96af696…` | Sin cambios |
| `documentos/` (9 archivos) | Lista en el respaldo | Sin cambios |

## 14. Diferencias pendientes

| Diferencia | Justificación | Se resuelve con |
|---|---|---|
| CxC 2023 en 8.2 B (3 celdas) | Excepción del documento para un solo año | Decisión 1 |
| PPC 2025 en 8.2 B | Doble redondeo | Decisión 3 |
| CO 2025 en 8.2 C | Hereda el anterior | Decisión 3 |
| Tres valores de 9.7 en Validación | Clasificación de una cuenta sin respaldo | Decisión 5 |
| PC / pasivo 2021 (50.40 % frente a 50.41 %) y WACC 2023 (3.88 % frente a 3.87 %) | Truncado y suma de redondeados, fuera de la rúbrica | Sin acción |

Ninguna queda sin justificar. **Ninguna es atribuible al software.**

## 15. Decisiones académicas pendientes

| # | Decisión | Recomendación |
|---:|---|---|
| 1 | **Base de CxC en 8.2 B.** ¿Aceptas la línea comercial como indicador único? | Sí, con la corrección de la sección 4. Si prefieres comerciales y otras en todo, cambian 2021, 2022 y 2023 en 8.2 B, 9.3 y el CCE |
| 2 | **Conclusión del CCE de 2023** | Mantenerla si aceptas la decisión 1, pero añadir que el signo depende de la base (sección 8) |
| 3 | **58.3 y 135.2 de 2025** | Corregir a 58.2 y 135.1, o unificar con 58.25 y 135.14 |
| 4 | **Declarar la regla de redondeo** | Añadir: «Razones sin redondeo intermedio; el CO y el CCE operan con cifras a 2 decimales; resultados redondeados mitad hacia arriba» |
| 5 | **Cuenta de largo plazo en 9.7** (variación 143,444,117 frente a 262,128,668) | Confirmarla con los estados o corregirla |
| 6 | **Figuras DuPont del PDF**, con importes intermedios erróneos | Rehacerlas si el documento se vuelve a entregar |
| 7 | **Contradicciones de texto:** 5.6 con promedios frente a 8.2 con cierre; 8.2 C dice que el PPP no es viable y 9.3 lo calcula | Aclararlas en el documento |
| 8 | **Commit** | Decidir tras tu revisión manual |

## 16. Estado final de Git

**No se realizó ningún commit ni `push`.** Rama `correcciones-auditoria`, HEAD `4506ed8`. Todos los cambios siguen sin confirmar en el directorio de trabajo.
