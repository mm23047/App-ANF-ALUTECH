# Mapeo financiero — Alutech 2021–2025

Catálogo de cuentas, equivalencias entre ejercicios y clasificación financiera que usa la aplicación (Etapa 3). Las
tablas de este documento se generaron a partir del catálogo cargado y de `calculations/rubros.py` /
`calculations/indicadores.py`; en la aplicación se consultan en «Datos originales › Trazabilidad y controles › Mapeo de
cuentas».

## 1. Principios del mapeo

1. **Denominación original.** Cada cuenta del catálogo conserva la denominación del estado financiero. Las variantes de
   escritura de un mismo año a otro dentro de una familia de estados (p. ej. «Arredramientos por pagar» 2022) se
   registran como denominación original del importe en `fuente_importe`, sin crear cuentas duplicadas.
2. **Dos familias de presentación.** 2021–2023 (estados combinados, códigos `CB…`) y 2024–2025 (estados consolidados,
   códigos `CN…`) tienen cuentas propias: aunque algunas denominaciones coinciden, la base de preparación, el perímetro y
   la agrupación cambian (p. ej. «Utilidades acumuladas» 2021–2023 incluye el resultado del año; «Resultados Acumulados»
   2024–2025 no). Así un cambio de presentación no se confunde con una variación real.
3. **Clasificación contable.** Categoría (activo, pasivo, patrimonio, ingresos, costos, gastos operativos, ingresos y
   gastos financieros, otros, impuestos), subcategoría (corriente / no corriente; capital, reservas, resultados…) y
   efecto (ingreso o gasto para los «otros») determinan los estados y sus subtotales; se tomaron del documento y no se
   pueden cambiar si la cuenta tiene importes.
4. **Grupo de análisis.** Línea normalizada (`account.grupo_analisis`) que relaciona cuentas equivalentes de ambas
   familias. Es **configurable** desde «Catálogo de cuentas» (no depende de coincidencias de texto) y cada cambio queda
   en el historial. Se usa para el análisis horizontal por grupo, el origen y aplicación de fondos, los rubros de los
   indicadores y la clasificación operativo/financiero del WACC.
5. **Rubro.** Suma de grupos que usan los indicadores y el análisis horizontal (p. ej. «Tesorería» = efectivo +
   inversiones corrientes).
6. **Sin equivalencias presuntas.** Una equivalencia solo se adopta si la respaldan los documentos (denominación, importe
   idéntico o presentación); si no, la cuenta queda en un grupo que no presupone su naturaleza.
7. **Sin cuentas ni importes inventados.** Solo se crearon cuentas que aparecen en los documentos. La única división es
   «Otros Ingresos (Gastos)» 2024–2025: un ingreso neto (2024, 55,570) y un gasto neto (2025, (811,571)) se registran en dos
   cuentas con efecto ingreso y gasto, porque la convención de la aplicación captura los gastos en positivo y nunca
   invierte un signo.

**Convención de signos al cargar:** balance con el signo impreso (las otras reservas de 2021–2023 y el efecto de conversión
de 2024–2025 son negativos y su subcategoría admite cualquier signo); resultados en positivo, comprobando que el signo
impreso sea coherente con la cuenta (ingresos positivos; costos, gastos e impuestos entre paréntesis).

## 2. Equivalencias y su justificación

| Equivalencia (grupo) | 2021–2023 | 2024–2025 | Justificación | Grado |
|---|---|---|---|---|
| `EFECTIVO` | Efectivo | Efectivo y Equivalentes de Efectivo | Misma naturaleza; el trabajo los compara directamente (Tablas 3–4). | Directa |
| `INVERSIONES_CP` | Certificados de depósito a plazo (corriente); Inversiones en bonos (2021) | Inversiones (corriente) | Inversiones financieras corrientes; el trabajo las suma a la tesorería en 9.1. | Directa |
| `CXC_COMERCIALES` / `OTRAS_CXC_CP` → `DEUDORES_COMERCIALES_OTRAS` | Comerciales y otras por separado | Una sola línea | **No son el mismo grupo**: la línea 2024–2025 incluye otras cuentas por cobrar. Se comparan con el rubro `CXC_COMERCIALES_Y_OTRAS` (base homogénea) o con `CXC_COMERCIALES_PRESENTADA` (línea presentada, base no homogénea, criterio de 8.2 B y 9.3). | Por rubro |
| `CXC_RELACIONADAS_CP` | Cuentas por cobrar a partes relacionadas | Cuentas por cobrar Empresas Relacionadas | Misma naturaleza. | Directa |
| `CXC_RELACIONADAS_LP` / `OTRAS_CXC_LP` | CxC a partes relacionadas (no corriente, 2023) → `CXC_RELACIONADAS_LP`; Otras cuentas por cobrar (no corriente, 2023) → `OTRAS_CXC_LP` | 2024: «Otras cuentas por cobrar a LP» → `OTRAS_CXC_LP`; 2025: «Cuentas por cobrar Empresas Relacionadas a LP» → `CXC_RELACIONADAS_LP` | **Equivalencia retirada en la revisión final (2026-11-02).** El estado de 2024 denomina la partida «Otras cuentas por cobrar a LP» y no la identifica como relacionada; el informe PCR presenta a dic‑24 «Cuentas por cobrar de LP» 119.7 M (= 983,263 + 118,684,551) y «Cuentas por cobrar a partes relacionadas» no corrientes 0.0. Se conserva la denominación original en el grupo neutral «Otras cuentas por cobrar (no corrientes)». El trabajo (9.7) sí las trata como la misma partida (ver OBS‑12). Efecto: solo el horizontal por grupos y el origen y aplicación de fondos 2024 y 2025; ningún indicador ni el vertical (usan totales). | No adoptada |
| `INVENTARIOS` | Inventarios (neto) | Inventario (Materiales, Suministros, etc.) | Misma naturaleza. | Directa |
| `PAGOS_ANTICIPADOS`, `IMPUESTOS_ACTIVO_CP` | Gastos pagados por anticipado; Anticipos al ISR | Pagos por Anticipado; Impuestos Corrientes | Misma naturaleza. | Directa |
| `INTANGIBLES` (+ `PLUSVALIA`) | Activos intangibles; Plusvalía mercantil (por separado) | Activos intangibles | 2024–2025 no presenta plusvalía: el rubro `INTANGIBLES_Y_PLUSVALIA` permite compararlos juntos. | Por rubro |
| `PRESTAMOS_CP` / `PRESTAMOS_LP` | Préstamos bancarios por pagar | Préstamos de Corto Plazo; Préstamos y Otras Obligaciones Financieras | Deuda bancaria; el LP 2024–2025 incluye «otras obligaciones». | Directa |
| `ARRENDAMIENTOS_*` | Arrendamientos por pagar | Pasivos por arrendamientos | Misma naturaleza. | Directa |
| `BONOS_*`, `CERTIFICADOS_INVERSION_*`, `TITULARIZACION_*` → `TITULOS_VALORES_*` | Tres instrumentos por separado | Obligaciones Emisión de Títulos valores | Grupos distintos (2024–2025 no desglosa); todos son deuda financiera para el WACC. | Por tipo |
| `DOCUMENTOS_POR_PAGAR_*` / `OTROS_PASIVOS_FINANCIEROS_*` | Documentos por pagar | Otros Pasivos Financieros | Grupos distintos: no se puede demostrar la equivalencia. Ambos son deuda financiera para el WACC. | Por tipo |
| `CXP_COMERCIALES` / `OTRAS_CXP_CP` → `ACREEDORES_COMERCIALES_OTRAS` | Comerciales y otras por separado | Una sola línea | Igual que las cuentas por cobrar: rubro `CXP_COMERCIALES_PRESENTADA` para el período de pago (criterio de 9.3). | Por rubro |
| `PRIMA_ACCIONES` | Primas sobre acciones | Superávit por Acciones | Mismo importe en 2022, 2023, 2024 y 2025 (56,160,201). | Directa |
| `APORTACIONES_CAPITAL` | Aportaciones de capital | Capital Adicional | Mismo importe en 2023, 2024 y 2025 (169,574). | Directa |
| `OTRAS_RESERVAS` / `RESERVAS_CAPITAL` + `EFECTO_CONVERSION` | Otras reservas de capital (incluye ORI y conversión) | Reservas de Capital; Efecto de Conversión | 2024–2025 separan la conversión: grupos distintos. | Por rubro |
| `RESULTADOS_ACUMULADOS` (+ `RESULTADO_PERIODO`) | Utilidades acumuladas (incluye el resultado del año) | Resultados Acumulados + Resultado del Período | La línea 2021–2023 equivale a la suma de las dos de 2024–2025. | Por rubro |
| `GASTOS_FINANCIEROS_NETOS` / `GASTOS_FINANCIEROS` + `INGRESOS_FINANCIEROS` | Gastos financieros (neto) | Ingresos y gastos financieros por separado | La aplicación calcula «gastos financieros netos» en todos los años (criterio de la Tabla 5 y de 8.3 B). | Por cálculo |
| `OTROS_INGRESOS_OPERATIVOS` / `OTROS_NO_OPERATIVOS` | Otros ingresos (neto), dentro de la utilidad de operación | Otros Ingresos (Gastos), después del resultado financiero | Distinta posición en el estado: grupos distintos; el rubro `OTROS_INGRESOS_GASTOS` los presenta juntos (vertical 7.1). | Por rubro |

## 3. Catálogo de cuentas de Alutech y su mapeo

| Código | Cuenta (catálogo) | Denominación original por año | Categoría / subcategoría (efecto) | Grupo de análisis | Indicadores en los que participa |
|---|---|---|---|---|---|
| CB1101 | Efectivo | Efectivo (2021, 2022, 2023) | ACTIVO / Corriente | `EFECTIVO` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, rotacion_activos, endeudamiento, roa |
| CB1102 | Certificados de depósitos a plazo fijo (corriente) | Certificados de depósitos a plazo fijo (2021, 2022, 2023) | ACTIVO / Corriente | `INVERSIONES_CP` | ctn, razon_corriente, prueba_acida, razon_tesoreria, rotacion_activos, endeudamiento, roa |
| CB1103 | Inversiones en bonos | Inversiones en bonos (2021) | ACTIVO / Corriente | `INVERSIONES_CP` | ctn, razon_corriente, prueba_acida, razon_tesoreria, rotacion_activos, endeudamiento, roa |
| CB1104 | Cuentas por cobrar comerciales - neto | Cuentas por cobrar comerciales - neto (2021, 2022); Cuentas por cobrar comerciales (neto) (2023) | ACTIVO / Corriente | `CXC_COMERCIALES` | ctn, razon_corriente, prueba_acida, rotacion_cxc, ppc, rotacion_cxc_total, ppc_total, ciclo_operativo, cce, rotacion_activos, endeudamiento, roa |
| CB1105 | Cuentas por cobrar a partes relacionadas (corriente) | Cuentas por cobrar a partes relacionadas (2021, 2022, 2023) | ACTIVO / Corriente | `CXC_RELACIONADAS_CP` | ctn, razon_corriente, prueba_acida, rotacion_activos, endeudamiento, roa |
| CB1106 | Otras cuentas por cobrar (corriente) | Otras cuentas por cobrar (2021, 2022, 2023) | ACTIVO / Corriente | `OTRAS_CXC_CP` | ctn, razon_corriente, prueba_acida, rotacion_cxc_total, ppc_total, rotacion_activos, endeudamiento, roa |
| CB1107 | Inventarios - neto | Inventarios - neto (2021); Inventarios (2022, 2023) | ACTIVO / Corriente | `INVENTARIOS` | ctn, razon_corriente, prueba_acida, rotacion_inventarios, ppi, ciclo_operativo, cce, rotacion_activos, endeudamiento, roa |
| CB1108 | Gastos pagados por anticipado | Gastos pagados por anticipado (2021, 2022, 2023) | ACTIVO / Corriente | `PAGOS_ANTICIPADOS` | ctn, razon_corriente, prueba_acida, rotacion_activos, endeudamiento, roa |
| CB1109 | Anticipos al impuesto sobre la renta | Anticipos al impuesto sobre la renta (2021, 2022, 2023) | ACTIVO / Corriente | `IMPUESTOS_ACTIVO_CP` | ctn, razon_corriente, prueba_acida, rotacion_activos, endeudamiento, roa |
| CB1201 | Certificados de depósitos a plazo fijo (no corriente) | Certificados de depósitos a plazo fijo (2021, 2022, 2023) | ACTIVO / No corriente | `DEPOSITOS_PLAZO_LP` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CB1202 | Cuentas por cobrar a partes relacionadas (no corriente) | Cuentas por cobrar a partes relacionadas (2023) | ACTIVO / No corriente | `CXC_RELACIONADAS_LP` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CB1203 | Otras cuentas por cobrar (no corriente) | Otras cuentas por cobrar (2023) | ACTIVO / No corriente | `OTRAS_CXC_LP` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CB1204 | Inversiones en acciones | Inversiones en acciones (2021, 2022, 2023) | ACTIVO / No corriente | `INVERSIONES_ACCIONES` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CB1205 | Propiedades de inversión | Propiedades de inversión (2021, 2022); Propiedades de Inversión (2023) | ACTIVO / No corriente | `PROPIEDADES_INVERSION` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CB1206 | Propiedades, planta y equipo - neto | Propiedades, planta y equipo - neto (2021, 2022); Propiedades, planta y equipo (neto) (2023) | ACTIVO / No corriente | `PPE` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CB1207 | Activos por derecho de uso - neto | Activos por derecho de uso - neto (2021, 2022); Activos por derecho de uso (neto) (2023) | ACTIVO / No corriente | `DERECHO_USO` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CB1208 | Activos intangibles - neto | Activos intangibles - neto (2021, 2022); Activos intangibles (neto) (2023) | ACTIVO / No corriente | `INTANGIBLES` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CB1209 | Plusvalía mercantil | Plusvalía mercantil (2021, 2022, 2023) | ACTIVO / No corriente | `PLUSVALIA` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CB1210 | Otros activos | Otros activos (2021, 2022, 2023) | ACTIVO / No corriente | `OTROS_ACTIVOS_NC` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CB1211 | Activo por impuestos sobre la renta diferidos | Activo por impuestos sobre la renta diferidos (2021, 2022); Activo por impuesto sobre la renta diferido (2023) | ACTIVO / No corriente | `IMPUESTO_DIFERIDO_ACTIVO` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CB2101 | Préstamos bancarios por pagar (corriente) | Préstamos bancarios por pagar (2021, 2022, 2023) | PASIVO / Corriente | `PRESTAMOS_CP` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2102 | Arrendamientos por pagar (corriente) | Arrendamientos por pagar (2021, 2023); Arredramientos por pagar (2022) | PASIVO / Corriente | `ARRENDAMIENTOS_CP` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2103 | Bonos corporativos (corriente) | Bonos corporativos (2023) | PASIVO / Corriente | `BONOS_CP` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2104 | Certificados de inversión (corriente) | Certificación de inversión (2022); Certificados de inversión (2023) | PASIVO / Corriente | `CERTIFICADOS_INVERSION_CP` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2105 | Obligaciones por derechos titularizados (corriente) | Obligaciones por derechos titularizados (2021, 2022, 2023) | PASIVO / Corriente | `TITULARIZACION_CP` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2106 | Porción corriente de los documentos por pagar a largo plazo | Porción de los documentos por pagar a largo plazo (2021); Porción corriente de los documentos por pagar a largo plazo (2022) | PASIVO / Corriente | `DOCUMENTOS_POR_PAGAR_CP` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2107 | Documentos por pagar (corriente) | Documentos por pagar (2023) | PASIVO / Corriente | `DOCUMENTOS_POR_PAGAR_CP` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2108 | Cuentas por pagar comerciales | Cuentas por pagar comérciales (2021); Cuentas por pagar comerciales (2022, 2023) | PASIVO / Corriente | `CXP_COMERCIALES` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, ppp, cce, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2109 | Cuentas por pagar a partes relacionadas | Cuentas por pagar a partes relacionadas (2021, 2022, 2023) | PASIVO / Corriente | `CXP_RELACIONADAS_CP` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2110 | Otras cuentas por pagar (corriente) | Otras cuentas por pagar (2021, 2022, 2023) | PASIVO / Corriente | `OTRAS_CXP_CP` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2111 | Impuesto sobre la renta por pagar (corriente) | Impuesto sobre la renta por pagar (2021, 2022, 2023) | PASIVO / Corriente | `IMPUESTOS_PASIVO_CP` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2201 | Préstamos bancarios por pagar (no corriente) | Préstamos bancarios por pagar (2021, 2022, 2023) | PASIVO / No corriente | `PRESTAMOS_LP` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2202 | Arrendamientos por pagar (no corriente) | Arrendamientos a largo plazo (2021); Arrendamientos por pagar (2022, 2023) | PASIVO / No corriente | `ARRENDAMIENTOS_LP` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2203 | Bonos corporativos (no corriente) | Bonos corporativos (2021, 2022, 2023) | PASIVO / No corriente | `BONOS_LP` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2204 | Certificados de inversión (no corriente) | Certificados de inversión (2021, 2022, 2023) | PASIVO / No corriente | `CERTIFICADOS_INVERSION_LP` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2205 | Obligaciones por derechos titularizados (no corriente) | Obligaciones por derechos titularizados (2021, 2022, 2023) | PASIVO / No corriente | `TITULARIZACION_LP` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2206 | Documentos por pagar a largo plazo | Documentos por pagar a largo plazo (2021, 2022); Documentos por pagar (2023) | PASIVO / No corriente | `DOCUMENTOS_POR_PAGAR_LP` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2207 | Otras cuentas por pagar (no corriente) | Otras cuentas por pagar (2023) | PASIVO / No corriente | `OTRAS_CXP_LP` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2208 | Pasivos por prima en venta de acciones de subsidiaria | Pasivos por prima en venta de acciones de subsidiaria (2022); Pasivo por prima en venta de acciones de subsidiaría (2023) | PASIVO / No corriente | `PRIMA_VENTA_ACCIONES` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2209 | Pasivos por beneficios post empleo | Pasivos por beneficios post empleo (2021, 2022, 2023) | PASIVO / No corriente | `BENEFICIOS_POST_EMPLEO` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2210 | Impuesto sobre la renta por pagar (no corriente) | Impuesto sobre la renta por pagar (2023) | PASIVO / No corriente | `IMPUESTOS_PASIVO_LP` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB2211 | Pasivo por impuestos sobre la renta diferidos | Pasivo por impuestos diferidos (2021); Pasivo por impuesto sobre la renta diferido (2022, 2023) | PASIVO / No corriente | `IMPUESTO_DIFERIDO_PASIVO` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CB3101 | Capital social | Capital social (2021, 2022, 2023) | PATRIMONIO / Capital social | `CAPITAL_SOCIAL` | capitales_permanentes, fondo_maniobra_lp, deuda_capital, roe, maf |
| CB3102 | Primas sobre acciones | Primas sobre acciones (2022); Prima sobre acciones (2023) | PATRIMONIO / Capital social | `PRIMA_ACCIONES` | capitales_permanentes, fondo_maniobra_lp, deuda_capital, roe, maf |
| CB3103 | Aportaciones de capital | Aportaciones de capital (2021, 2022, 2023) | PATRIMONIO / Capital social | `APORTACIONES_CAPITAL` | capitales_permanentes, fondo_maniobra_lp, deuda_capital, roe, maf |
| CB3104 | Reserva legal | Reserva legal (2021, 2022, 2023) | PATRIMONIO / Reservas | `RESERVA_LEGAL` | capitales_permanentes, fondo_maniobra_lp, deuda_capital, roe, maf |
| CB3105 | Otras reservas de capital | Otras reservas de capital (2021, 2022, 2023) | PATRIMONIO / Otras patrimoniales | `OTRAS_RESERVAS` | capitales_permanentes, fondo_maniobra_lp, deuda_capital, roe, maf |
| CB3106 | Utilidades acumuladas | Utilidades acumuladas (2021); Utilidad acumulada (2022); Resultados acumulads (2023) | PATRIMONIO / Resultados acumulados | `RESULTADOS_ACUMULADOS` | capitales_permanentes, fondo_maniobra_lp, deuda_capital, roe, maf |
| CB3107 | Participaciones no controladoras | Participaciones no controladoras (2021, 2023); Participación no controladora (2022) | PATRIMONIO / Otras patrimoniales | `NO_CONTROLADORAS` | capitales_permanentes, fondo_maniobra_lp, deuda_capital, roe, maf, margen_neto_controladora, maf_controladora |
| CB4101 | Ingresos de actividades ordinarias | Ingresos de actividades ordinarias (2021, 2023); Ingresos por actividades ordinarias (2022) | INGRESOS | `INGRESOS_ORDINARIOS` | rotacion_cxc, ppc, rotacion_cxc_total, ppc_total, rotacion_activos, margen_bruto, margen_operativo, margen_neto |
| CB5101 | Costo de ventas | Costo de ventas (2021, 2022, 2023) | COSTOS | `COSTO_VENTAS` | rotacion_inventarios, ppi, ppp, margen_bruto |
| CB6101 | Gastos de administración | Gastos de administración (2021, 2022, 2023) | GASTOS_OPERATIVOS / Administración | `GASTOS_ADMINISTRACION` | — |
| CB6102 | Gastos de venta y despacho | Gastos de venta y despacho (2021, 2022, 2023) | GASTOS_OPERATIVOS / Ventas | `GASTOS_VENTA` | — |
| CB6103 | Pérdidas por deterioro de valor de cuentas por cobrar, neto | (Pérdidas) reversión por deterioro de valor de cuentas por cobrar, neto (2021); Pérdidas por deterioro de valor de cuentas por cobrar (2022, 2023) | GASTOS_OPERATIVOS / Otros operativos (GASTO) | `DETERIORO_CXC` | — |
| CB6104 | Otros ingresos - neto | Otros ingresos - neto (2021); Otros ingresos (neto) (2022, 2023) | GASTOS_OPERATIVOS / Otros operativos (INGRESO) | `OTROS_INGRESOS_OPERATIVOS` | — |
| CB7101 | Gastos financieros - neto | Gastos financieros - (neto) (2021); Gastos financieros (neto) (2022, 2023) | GASTOS_FINANCIEROS | `GASTOS_FINANCIEROS_NETOS` | cobertura_intereses |
| CB8101 | Impuesto sobre la renta | Impuesto sobre la renta (2021, 2022, 2023) | IMPUESTOS | `IMPUESTO_RENTA` | — |
| CN1101 | Efectivo y Equivalentes de Efectivo | Efectivo y Equivalentes de Efectivo (2024, 2025) | ACTIVO / Corriente | `EFECTIVO` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, rotacion_activos, endeudamiento, roa |
| CN1102 | Inversiones (corriente) | Inversiones (2024, 2025) | ACTIVO / Corriente | `INVERSIONES_CP` | ctn, razon_corriente, prueba_acida, razon_tesoreria, rotacion_activos, endeudamiento, roa |
| CN1103 | Deudores comerciales y Otras Cuentas por Cobrar (Netos) | Deudores comerciales y Otras Cuentas por Cobrar (Netos) (2024, 2025) | ACTIVO / Corriente | `DEUDORES_COMERCIALES_OTRAS` | ctn, razon_corriente, prueba_acida, rotacion_cxc, ppc, rotacion_cxc_total, ppc_total, ciclo_operativo, cce, rotacion_activos, endeudamiento, roa |
| CN1104 | Cuentas por cobrar Empresas Relacionadas (corriente) | Cuentas por cobrar Empresas Relacionadas (2024, 2025) | ACTIVO / Corriente | `CXC_RELACIONADAS_CP` | ctn, razon_corriente, prueba_acida, rotacion_activos, endeudamiento, roa |
| CN1105 | Inventario (Materiales, Suministros, etc.) | Inventario (Materiales, Suministros, etc.) (2024, 2025) | ACTIVO / Corriente | `INVENTARIOS` | ctn, razon_corriente, prueba_acida, rotacion_inventarios, ppi, ciclo_operativo, cce, rotacion_activos, endeudamiento, roa |
| CN1106 | Pagos por Anticipado | Pagos por Anticipado (2024, 2025) | ACTIVO / Corriente | `PAGOS_ANTICIPADOS` | ctn, razon_corriente, prueba_acida, rotacion_activos, endeudamiento, roa |
| CN1107 | Impuestos Corrientes (activo) | Impuestos Corrientes (2024, 2025) | ACTIVO / Corriente | `IMPUESTOS_ACTIVO_CP` | ctn, razon_corriente, prueba_acida, rotacion_activos, endeudamiento, roa |
| CN1201 | Cuentas por cobrar a LP | Cuentas por cobrar a LP (2024, 2025) | ACTIVO / No corriente | `CXC_LP` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CN1202 | Otras cuentas por cobrar a LP | Otras cuentas por cobrar a LP (2024) | ACTIVO / No corriente | `OTRAS_CXC_LP` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CN1203 | Cuentas por cobrar Empresas Relacionadas a LP | Cuentas por cobrar Empresas Relacionadas a LP (2025) | ACTIVO / No corriente | `CXC_RELACIONADAS_LP` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CN1204 | Inversiones (no corriente) | Inversiones (2024, 2025) | ACTIVO / No corriente | `INVERSIONES_LP` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CN1205 | Propiedades de Inversión | Propiedades de Inversión (2024, 2025) | ACTIVO / No corriente | `PROPIEDADES_INVERSION` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CN1206 | Propiedades, Planta y Equipo (Neto) | Propiedades, Planta y Equipo (Neto) (2024, 2025) | ACTIVO / No corriente | `PPE` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CN1207 | Activos por derechos de Uso (neto) | Activos por derechos de Uso(neto) (2024, 2025) | ACTIVO / No corriente | `DERECHO_USO` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CN1208 | Activos intangibles | Activos intangibles (2024, 2025) | ACTIVO / No corriente | `INTANGIBLES` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CN1209 | Impuestos Diferidos (activo) | Impuestos Diferidos (2024, 2025) | ACTIVO / No corriente | `IMPUESTO_DIFERIDO_ACTIVO` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CN1210 | Otros Activos financieros | Otros Activos financieros (2024, 2025) | ACTIVO / No corriente | `OTROS_ACTIVOS_FINANCIEROS_NC` | fondo_maniobra_lp, rotacion_activos, endeudamiento, roa |
| CN2101 | Préstamos de Corto Plazo | Préstamos de Corto Plazo (2024, 2025) | PASIVO / Corriente | `PRESTAMOS_CP` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CN2102 | Pasivos por arrendamientos (corriente) | Pasivos por arrendamientos (2024, 2025) | PASIVO / Corriente | `ARRENDAMIENTOS_CP` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CN2103 | Obligaciones Emisión de Títulos valores (corriente) | Obligaciones Emisión de Títulos valores (2024, 2025) | PASIVO / Corriente | `TITULOS_VALORES_CP` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CN2104 | Otros Pasivos Financieros (corriente) | Otros Pasivos Financieros (2024, 2025) | PASIVO / Corriente | `OTROS_PASIVOS_FINANCIEROS_CP` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CN2105 | Acreedores comerciales y Otras Cuentas por Pagar | Acreedores comerciales y Otras Cuentas por Pagar (2024, 2025) | PASIVO / Corriente | `ACREEDORES_COMERCIALES_OTRAS` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, ppp, cce, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CN2106 | Cuentas por Pagar Empresas Relacionadas | Cuentas por Pagar Empresas Relacionadas (2024, 2025) | PASIVO / Corriente | `CXP_RELACIONADAS_CP` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CN2107 | Impuestos Corrientes (pasivo) | Impuestos Corrientes (2024, 2025) | PASIVO / Corriente | `IMPUESTOS_PASIVO_CP` | ctn, razon_corriente, prueba_acida, razon_efectivo, razon_tesoreria, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CN2201 | Préstamos y Otras Obligaciones Financieras | Préstamos y Otras Obligaciones Financieras (2024, 2025) | PASIVO / No corriente | `PRESTAMOS_LP` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CN2202 | Pasivos por arrendamientos (no corriente) | Pasivos por arrendamientos (2024, 2025) | PASIVO / No corriente | `ARRENDAMIENTOS_LP` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CN2203 | Obligaciones Emisión de Títulos valores (no corriente) | Obligaciones Emisión de Títulos valores (2024, 2025) | PASIVO / No corriente | `TITULOS_VALORES_LP` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CN2204 | Otros Pasivos Financieros (no corriente) | Otros Pasivos Financieros (2024, 2025) | PASIVO / No corriente | `OTROS_PASIVOS_FINANCIEROS_LP` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CN2205 | Provisiones | Provisiones (2024, 2025) | PASIVO / No corriente | `PROVISIONES_LP` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CN2206 | Impuestos Diferidos (pasivo) | Impuestos Diferidos (2024, 2025) | PASIVO / No corriente | `IMPUESTO_DIFERIDO_PASIVO` | capitales_permanentes, fondo_maniobra_lp, endeudamiento, pc_sobre_pasivo, deuda_capital |
| CN3101 | Capital Social | Capital Social (2024, 2025) | PATRIMONIO / Capital social | `CAPITAL_SOCIAL` | capitales_permanentes, fondo_maniobra_lp, deuda_capital, roe, maf |
| CN3102 | Capital Adicional | Capital Adicional (2024, 2025) | PATRIMONIO / Capital social | `APORTACIONES_CAPITAL` | capitales_permanentes, fondo_maniobra_lp, deuda_capital, roe, maf |
| CN3103 | Reserva Legal | Reserva Legal (2024, 2025) | PATRIMONIO / Reservas | `RESERVA_LEGAL` | capitales_permanentes, fondo_maniobra_lp, deuda_capital, roe, maf |
| CN3104 | Superávit por Acciones | Superávit por Acciones (2024, 2025) | PATRIMONIO / Capital social | `PRIMA_ACCIONES` | capitales_permanentes, fondo_maniobra_lp, deuda_capital, roe, maf |
| CN3105 | Reservas de Capital | Reservas de Capital (2024, 2025) | PATRIMONIO / Reservas | `RESERVAS_CAPITAL` | capitales_permanentes, fondo_maniobra_lp, deuda_capital, roe, maf |
| CN3106 | Efecto de Conversion Entidades Extranjeras | Efecto de Conversion Entidades Extranjeras (2024, 2025) | PATRIMONIO / Otras patrimoniales | `EFECTO_CONVERSION` | capitales_permanentes, fondo_maniobra_lp, deuda_capital, roe, maf |
| CN3107 | Resultados Acumulados | Resultados Acumulados (2024, 2025) | PATRIMONIO / Resultados acumulados | `RESULTADOS_ACUMULADOS` | capitales_permanentes, fondo_maniobra_lp, deuda_capital, roe, maf |
| CN3108 | Resultado del Período | Resultado del Período (2024, 2025) | PATRIMONIO / Resultado del ejercicio | `RESULTADO_PERIODO` | capitales_permanentes, fondo_maniobra_lp, deuda_capital, roe, maf |
| CN4101 | Ingresos Ordinarios | Ingresos Ordinarios (2024, 2025) | INGRESOS | `INGRESOS_ORDINARIOS` | rotacion_cxc, ppc, rotacion_cxc_total, ppc_total, rotacion_activos, margen_bruto, margen_operativo, margen_neto |
| CN5101 | Costo de Ventas | Costo de Ventas (2024, 2025) | COSTOS | `COSTO_VENTAS` | rotacion_inventarios, ppi, ppp, margen_bruto |
| CN6101 | Gastos de Venta y Distribución | Gastos de Venta y Distribución (2024, 2025) | GASTOS_OPERATIVOS / Ventas | `GASTOS_VENTA` | — |
| CN6102 | Gastos de Administración | Gastos de Administración (2024, 2025) | GASTOS_OPERATIVOS / Administración | `GASTOS_ADMINISTRACION` | — |
| CN6103 | Gastos de Personal | Gastos de Personal (2024, 2025) | GASTOS_OPERATIVOS / Otros operativos (GASTO) | `GASTOS_PERSONAL` | — |
| CN6104 | Gastos de Depreciación y Amortización | Gastos de Depreciación y Amortización (2024, 2025) | GASTOS_OPERATIVOS / Otros operativos (GASTO) | `DEPRECIACION_AMORTIZACION` | ebitda |
| CN7101 | Ingresos Financieros | Ingresos Financieros (2024, 2025) | INGRESOS_FINANCIEROS | `INGRESOS_FINANCIEROS` | cobertura_intereses |
| CN7102 | Gastos Financieros | Gastos Financieros (2024, 2025) | GASTOS_FINANCIEROS | `GASTOS_FINANCIEROS` | cobertura_intereses, cobertura_intereses_bruta |
| CN7201 | Otros Ingresos (Gastos) - neto ingreso | Otros Ingresos (Gastos) (2024) | OTROS_INGRESOS_GASTOS (INGRESO) | `OTROS_NO_OPERATIVOS` | — |
| CN7202 | Otros Ingresos (Gastos) - neto gasto | Otros Ingresos (Gastos) (2025) | OTROS_INGRESOS_GASTOS (GASTO) | `OTROS_NO_OPERATIVOS` | — |
| CN8101 | Impuestos | Impuestos (2024, 2025) | IMPUESTOS | `IMPUESTO_RENTA` | — |

Las 30 cuentas del catálogo estándar de la aplicación (códigos 1001–8001) se conservan sin grupo de análisis; 19 de ellas
tienen importes en cero en 2021, que se conservan intactos por decisión del usuario.

## 4. Grupos de análisis

| Grupo | Nombre normalizado | Clase | Tipo de pasivo (WACC) | Cuentas 2021–2023 | Cuentas 2024–2025 |
|---|---|---|---|---|---|
| `EFECTIVO` | Efectivo y equivalentes de efectivo | Activo corriente | — | CB1101 | CN1101 |
| `INVERSIONES_CP` | Inversiones y depósitos a plazo (corrientes) | Activo corriente | — | CB1102, CB1103 | CN1102 |
| `CXC_COMERCIALES` | Cuentas por cobrar comerciales (neto) | Activo corriente | — | CB1104 | — |
| `OTRAS_CXC_CP` | Otras cuentas por cobrar (corrientes) | Activo corriente | — | CB1106 | — |
| `DEUDORES_COMERCIALES_OTRAS` | Deudores comerciales y otras cuentas por cobrar (neto) | Activo corriente | — | — | CN1103 |
| `CXC_RELACIONADAS_CP` | Cuentas por cobrar a partes relacionadas (corrientes) | Activo corriente | — | CB1105 | CN1104 |
| `INVENTARIOS` | Inventarios | Activo corriente | — | CB1107 | CN1105 |
| `PAGOS_ANTICIPADOS` | Gastos y pagos por anticipado | Activo corriente | — | CB1108 | CN1106 |
| `IMPUESTOS_ACTIVO_CP` | Anticipos de ISR e impuestos corrientes (activo) | Activo corriente | — | CB1109 | CN1107 |
| `DEPOSITOS_PLAZO_LP` | Certificados de depósito a plazo (no corrientes) | Activo no corriente | — | CB1201 | — |
| `INVERSIONES_ACCIONES` | Inversiones en acciones | Activo no corriente | — | CB1204 | — |
| `INVERSIONES_LP` | Inversiones (no corrientes) | Activo no corriente | — | — | CN1204 |
| `CXC_LP` | Cuentas por cobrar a largo plazo | Activo no corriente | — | — | CN1201 |
| `CXC_RELACIONADAS_LP` | Cuentas por cobrar a partes relacionadas (no corrientes) | Activo no corriente | — | CB1202 | CN1203 |
| `OTRAS_CXC_LP` | Otras cuentas por cobrar (no corrientes) | Activo no corriente | — | CB1203 | CN1202 |
| `PROPIEDADES_INVERSION` | Propiedades de inversión | Activo no corriente | — | CB1205 | CN1205 |
| `PPE` | Propiedades, planta y equipo (neto) | Activo no corriente | — | CB1206 | CN1206 |
| `DERECHO_USO` | Activos por derecho de uso (neto) | Activo no corriente | — | CB1207 | CN1207 |
| `INTANGIBLES` | Activos intangibles | Activo no corriente | — | CB1208 | CN1208 |
| `PLUSVALIA` | Plusvalía mercantil | Activo no corriente | — | CB1209 | — |
| `OTROS_ACTIVOS_NC` | Otros activos (no corrientes) | Activo no corriente | — | CB1210 | — |
| `OTROS_ACTIVOS_FINANCIEROS_NC` | Otros activos financieros (no corrientes) | Activo no corriente | — | — | CN1210 |
| `IMPUESTO_DIFERIDO_ACTIVO` | Impuesto sobre la renta diferido (activo) | Activo no corriente | — | CB1211 | CN1209 |
| `PRESTAMOS_CP` | Préstamos bancarios (corrientes) | Pasivo corriente | FINANCIERO | CB2101 | CN2101 |
| `ARRENDAMIENTOS_CP` | Pasivos por arrendamientos (corrientes) | Pasivo corriente | FINANCIERO | CB2102 | CN2102 |
| `BONOS_CP` | Bonos corporativos (corrientes) | Pasivo corriente | FINANCIERO | CB2103 | — |
| `CERTIFICADOS_INVERSION_CP` | Certificados de inversión (corrientes) | Pasivo corriente | FINANCIERO | CB2104 | — |
| `TITULARIZACION_CP` | Obligaciones por derechos titularizados (corrientes) | Pasivo corriente | FINANCIERO | CB2105 | — |
| `TITULOS_VALORES_CP` | Obligaciones por emisión de títulos valores (corrientes) | Pasivo corriente | FINANCIERO | — | CN2103 |
| `DOCUMENTOS_POR_PAGAR_CP` | Documentos por pagar (corrientes) | Pasivo corriente | FINANCIERO | CB2106, CB2107 | — |
| `OTROS_PASIVOS_FINANCIEROS_CP` | Otros pasivos financieros (corrientes) | Pasivo corriente | FINANCIERO | — | CN2104 |
| `CXP_COMERCIALES` | Cuentas por pagar comerciales | Pasivo corriente | OPERATIVO | CB2108 | — |
| `OTRAS_CXP_CP` | Otras cuentas por pagar (corrientes) | Pasivo corriente | OPERATIVO | CB2110 | — |
| `ACREEDORES_COMERCIALES_OTRAS` | Acreedores comerciales y otras cuentas por pagar | Pasivo corriente | OPERATIVO | — | CN2105 |
| `CXP_RELACIONADAS_CP` | Cuentas por pagar a partes relacionadas | Pasivo corriente | OPERATIVO | CB2109 | CN2106 |
| `IMPUESTOS_PASIVO_CP` | Impuesto sobre la renta e impuestos por pagar (corrientes) | Pasivo corriente | OPERATIVO | CB2111 | CN2107 |
| `PRESTAMOS_LP` | Préstamos y otras obligaciones financieras (no corrientes) | Pasivo no corriente | FINANCIERO | CB2201 | CN2201 |
| `ARRENDAMIENTOS_LP` | Pasivos por arrendamientos (no corrientes) | Pasivo no corriente | FINANCIERO | CB2202 | CN2202 |
| `BONOS_LP` | Bonos corporativos (no corrientes) | Pasivo no corriente | FINANCIERO | CB2203 | — |
| `CERTIFICADOS_INVERSION_LP` | Certificados de inversión (no corrientes) | Pasivo no corriente | FINANCIERO | CB2204 | — |
| `TITULARIZACION_LP` | Obligaciones por derechos titularizados (no corrientes) | Pasivo no corriente | FINANCIERO | CB2205 | — |
| `TITULOS_VALORES_LP` | Obligaciones por emisión de títulos valores (no corrientes) | Pasivo no corriente | FINANCIERO | — | CN2203 |
| `DOCUMENTOS_POR_PAGAR_LP` | Documentos por pagar (no corrientes) | Pasivo no corriente | FINANCIERO | CB2206 | — |
| `OTROS_PASIVOS_FINANCIEROS_LP` | Otros pasivos financieros (no corrientes) | Pasivo no corriente | FINANCIERO | — | CN2204 |
| `OTRAS_CXP_LP` | Otras cuentas por pagar (no corrientes) | Pasivo no corriente | OPERATIVO | CB2207 | — |
| `PRIMA_VENTA_ACCIONES` | Pasivo por prima en venta de acciones de subsidiaria | Pasivo no corriente | OPERATIVO | CB2208 | — |
| `BENEFICIOS_POST_EMPLEO` | Pasivos por beneficios post empleo | Pasivo no corriente | OPERATIVO | CB2209 | — |
| `PROVISIONES_LP` | Provisiones (no corrientes) | Pasivo no corriente | OPERATIVO | — | CN2205 |
| `IMPUESTOS_PASIVO_LP` | Impuesto sobre la renta por pagar (no corriente) | Pasivo no corriente | OPERATIVO | CB2210 | — |
| `IMPUESTO_DIFERIDO_PASIVO` | Impuesto sobre la renta diferido (pasivo) | Pasivo no corriente | OPERATIVO | CB2211 | CN2206 |
| `CAPITAL_SOCIAL` | Capital social | Patrimonio | — | CB3101 | CN3101 |
| `PRIMA_ACCIONES` | Prima / superávit por acciones | Patrimonio | — | CB3102 | CN3104 |
| `APORTACIONES_CAPITAL` | Aportaciones de capital / capital adicional | Patrimonio | — | CB3103 | CN3102 |
| `RESERVA_LEGAL` | Reserva legal | Patrimonio | — | CB3104 | CN3103 |
| `OTRAS_RESERVAS` | Otras reservas de capital (incluye otros resultados integrales) | Patrimonio | — | CB3105 | — |
| `RESERVAS_CAPITAL` | Reservas de capital | Patrimonio | — | — | CN3105 |
| `EFECTO_CONVERSION` | Efecto de conversión de entidades extranjeras | Patrimonio | — | — | CN3106 |
| `RESULTADOS_ACUMULADOS` | Resultados (utilidades) acumulados | Patrimonio | — | CB3106 | CN3107 |
| `RESULTADO_PERIODO` | Resultado del período | Patrimonio | — | — | CN3108 |
| `NO_CONTROLADORAS` | Participaciones no controladoras | Patrimonio | — | CB3107 | — |
| `INGRESOS_ORDINARIOS` | Ingresos de actividades ordinarias | Estado de resultados | — | CB4101 | CN4101 |
| `COSTO_VENTAS` | Costo de ventas | Estado de resultados | — | CB5101 | CN5101 |
| `GASTOS_ADMINISTRACION` | Gastos de administración | Estado de resultados | — | CB6101 | CN6102 |
| `GASTOS_VENTA` | Gastos de venta y despacho / distribución | Estado de resultados | — | CB6102 | CN6101 |
| `DETERIORO_CXC` | Deterioro de cuentas por cobrar | Estado de resultados | — | CB6103 | — |
| `GASTOS_PERSONAL` | Gastos de personal | Estado de resultados | — | — | CN6103 |
| `DEPRECIACION_AMORTIZACION` | Depreciación y amortización | Estado de resultados | — | — | CN6104 |
| `OTROS_INGRESOS_OPERATIVOS` | Otros ingresos operativos (neto) | Estado de resultados | — | CB6104 | — |
| `INGRESOS_FINANCIEROS` | Ingresos financieros | Estado de resultados | — | — | CN7101 |
| `GASTOS_FINANCIEROS` | Gastos financieros | Estado de resultados | — | — | CN7102 |
| `GASTOS_FINANCIEROS_NETOS` | Gastos financieros (neto, presentado así) | Estado de resultados | — | CB7101 | — |
| `OTROS_NO_OPERATIVOS` | Otros ingresos (gastos) no operativos | Estado de resultados | — | — | CN7201, CN7202 |
| `IMPUESTO_RENTA` | Impuesto sobre la renta | Estado de resultados | — | CB8101 | CN8101 |

## 5. Rubros

| Rubro | Nombre | Grupos que suma | Nota |
|---|---|---|---|
| `EFECTIVO` | Efectivo y equivalentes de efectivo | EFECTIVO |  |
| `INVERSIONES_CP` | Inversiones y depósitos a plazo (corrientes) | INVERSIONES_CP |  |
| `TESORERIA` | Tesorería y valores negociables (efectivo + inversiones corrientes) | EFECTIVO, INVERSIONES_CP |  |
| `CXC_COMERCIALES_PRESENTADA` | Cuentas por cobrar comerciales (línea presentada) | CXC_COMERCIALES, DEUDORES_COMERCIALES_OTRAS | 2021–2023: solo cuentas por cobrar comerciales; 2024–2025 el estado presenta una sola línea 'Deudores comerciales y otras cuentas por cobrar'. La base no es homogénea entre ambos períodos. |
| `CXC_COMERCIALES_Y_OTRAS` | Cuentas por cobrar comerciales y otras (corrientes) | CXC_COMERCIALES, OTRAS_CXC_CP, DEUDORES_COMERCIALES_OTRAS | Base homogénea 2021–2025: comerciales + otras cuentas por cobrar corrientes. |
| `CXC_RELACIONADAS_CP` | Cuentas por cobrar a partes relacionadas (corrientes) | CXC_RELACIONADAS_CP |  |
| `CXC_RELACIONADAS_LP` | Cuentas por cobrar a partes relacionadas (no corrientes) | CXC_RELACIONADAS_LP |  |
| `INVENTARIOS` | Inventarios | INVENTARIOS |  |
| `CXP_COMERCIALES_PRESENTADA` | Cuentas por pagar comerciales (línea presentada) | CXP_COMERCIALES, ACREEDORES_COMERCIALES_OTRAS | 2021–2023: cuentas por pagar comerciales; 2024–2025 'Acreedores comerciales y otras cuentas por pagar' (incluye otras cuentas por pagar). |
| `DEUDA_FINANCIERA` | Deuda financiera con costo (préstamos, arrendamientos y títulos valores) | PRESTAMOS_CP, ARRENDAMIENTOS_CP, BONOS_CP, CERTIFICADOS_INVERSION_CP, TITULARIZACION_CP, TITULOS_VALORES_CP, DOCUMENTOS_POR_PAGAR_CP, OTROS_PASIVOS_FINANCIEROS_CP, PRESTAMOS_LP, ARRENDAMIENTOS_LP, BONOS_LP, CERTIFICADOS_INVERSION_LP, TITULARIZACION_LP, TITULOS_VALORES_LP, DOCUMENTOS_POR_PAGAR_LP, OTROS_PASIVOS_FINANCIEROS_LP |  |
| `PASIVOS_OPERATIVOS` | Pasivos operativos sin costo explícito | CXP_COMERCIALES, OTRAS_CXP_CP, ACREEDORES_COMERCIALES_OTRAS, CXP_RELACIONADAS_CP, IMPUESTOS_PASIVO_CP, OTRAS_CXP_LP, PRIMA_VENTA_ACCIONES, BENEFICIOS_POST_EMPLEO, PROVISIONES_LP, IMPUESTOS_PASIVO_LP, IMPUESTO_DIFERIDO_PASIVO |  |
| `INVERSIONES_NC` | Inversiones y depósitos (no corrientes) | DEPOSITOS_PLAZO_LP, INVERSIONES_ACCIONES, INVERSIONES_LP |  |
| `INTANGIBLES_Y_PLUSVALIA` | Activos intangibles y plusvalía | INTANGIBLES, PLUSVALIA | Los estados 2024–2025 no presentan plusvalía por separado. |
| `PPE` | Propiedades, planta y equipo (neto) | PPE |  |
| `GASTOS_OPERATIVOS_ANF` | Gastos operativos (administración, venta, personal y depreciación) | GASTOS_ADMINISTRACION, GASTOS_VENTA, GASTOS_PERSONAL, DEPRECIACION_AMORTIZACION | Criterio del trabajo ANF (Tabla 5): excluye el deterioro de cuentas por cobrar y los otros ingresos. |
| `OTROS_INGRESOS_GASTOS` | Otros ingresos o gastos (neto) | OTROS_INGRESOS_OPERATIVOS, OTROS_NO_OPERATIVOS | 2021–2023 se presentan dentro de la utilidad de operación; 2024–2025, después del resultado financiero. |

## 6. Indicadores y sus insumos

| Indicador (clave) | Nombre | Fórmula | Insumos | Unidad |
|---|---|---|---|---|
| `ctn` | Capital de trabajo neto (fondo de maniobra a corto plazo) | Activo corriente − Pasivo corriente | Total activo corriente; total pasivo corriente | USD |
| `razon_corriente` | Razón corriente (circulante) | Activo corriente / Pasivo corriente | Total activo corriente; total pasivo corriente | veces |
| `prueba_acida` | Prueba ácida | (Activo corriente − Inventarios) / Pasivo corriente | Total activo corriente; inventarios; total pasivo corriente | veces |
| `razon_efectivo` | Razón de efectivo | Efectivo y equivalentes / Pasivo corriente | Efectivo y equivalentes; total pasivo corriente | veces |
| `razon_tesoreria` | Razón de tesorería | (Efectivo + inversiones y depósitos corrientes) / Pasivo corriente × 100 | Efectivo; certificados de depósito, bonos e inversiones corrientes; total pasivo corriente | % |
| `capitales_permanentes` | Capitales permanentes | Patrimonio + Pasivo no corriente | Total patrimonio; total pasivo no corriente | USD |
| `fondo_maniobra_lp` | Fondo de maniobra a largo plazo | Capitales permanentes − Activo no corriente | Total patrimonio; total pasivo no corriente; total activo no corriente | USD |
| `rotacion_inventarios` | Rotación de inventarios | Costo de ventas / Inventarios (saldo al cierre) | Costo de ventas; inventarios | veces |
| `ppi` | Período promedio (edad promedio) de inventario | Inventarios / Costo de ventas × 365 | Inventarios; costo de ventas | días |
| `rotacion_cxc` | Rotación de cuentas por cobrar comerciales | Ingresos ordinarios / Cuentas por cobrar comerciales (línea presentada) | Ingresos ordinarios (aproximación de las ventas a crédito); cuentas por cobrar comerciales | veces |
| `ppc` | Período promedio de cobro | Cuentas por cobrar comerciales / Ingresos ordinarios × 365 | Cuentas por cobrar comerciales (línea presentada); ingresos ordinarios | días |
| `rotacion_cxc_total` | Rotación de cuentas por cobrar comerciales y otras | Ingresos ordinarios / (Cuentas por cobrar comerciales + otras cuentas por cobrar corrientes) | Ingresos ordinarios; cuentas por cobrar comerciales y otras | veces |
| `ppc_total` | Período de cobro (cartera comercial y otras) | (Cuentas por cobrar comerciales + otras) / Ingresos ordinarios × 365 | Cuentas por cobrar comerciales y otras; ingresos ordinarios | días |
| `ppp` | Período promedio de pago | Cuentas por pagar comerciales / Costo de ventas × 365 | Cuentas por pagar comerciales (línea presentada); costo de ventas (aproximación de las compras) | días |
| `ciclo_operativo` | Ciclo operativo | PPI + PPC | Período promedio de inventario; período promedio de cobro | días |
| `cce` | Ciclo de conversión del efectivo | Ciclo operativo − PPP | Ciclo operativo; período promedio de pago | días |
| `rotacion_activos` | Rotación de activos totales | Ingresos ordinarios / Activo total | Ingresos ordinarios; total activo | veces |
| `endeudamiento` | Índice de endeudamiento | Pasivo total / Activo total × 100 | Total pasivo; total activo | % |
| `pc_sobre_pasivo` | Pasivo corriente sobre pasivo total | Pasivo corriente / Pasivo total × 100 | Total pasivo corriente; total pasivo | % |
| `deuda_capital` | Razón deuda-capital patrimonial | Pasivo total / Patrimonio total | Total pasivo; total patrimonio | veces |
| `cobertura_intereses` | Razón de cargos de interés fijo | Utilidad de operación / Gastos financieros netos | Utilidad de operación; gastos financieros − ingresos financieros | veces |
| `cobertura_intereses_bruta` | Cobertura con gastos financieros brutos | Utilidad de operación / Gastos financieros (brutos) | Utilidad de operación; gastos financieros | veces |
| `cobertura_pagos_fijos` | Índice de cobertura de pagos fijos | (UAII + arrendamientos) / (intereses + arrendamientos + principal / (1 − t)) | No disponible en los documentos | veces |
| `margen_bruto` | Margen de utilidad bruta | Utilidad bruta / Ingresos ordinarios × 100 | Utilidad bruta; ingresos ordinarios | % |
| `margen_operativo` | Margen de utilidad operativa | Utilidad de operación / Ingresos ordinarios × 100 | Utilidad de operación; ingresos ordinarios | % |
| `margen_neto` | Margen de utilidad neta | Utilidad neta / Ingresos ordinarios × 100 | Utilidad neta del ejercicio; ingresos ordinarios | % |
| `roa` | Rendimiento sobre los activos totales (ROA) | Utilidad neta / Activo total al cierre × 100 | Utilidad neta; total activo | % |
| `roe` | Retorno sobre el patrimonio (ROE) | Utilidad neta / Patrimonio total al cierre × 100 | Utilidad neta; total patrimonio (incluye participaciones no controladoras) | % |
| `ebitda` | EBITDA | Utilidad de operación + Depreciación y amortización | Utilidad de operación; depreciación y amortización (estado de resultados o flujo de efectivo) | USD |
| `eps` | Ganancia por acción (EPS) | Utilidad atribuible a accionistas comunes / Promedio ponderado de acciones | Número de acciones (no disponible) | USD |
| `per` | Relación precio/ganancias (P/E) | Precio de mercado por acción / EPS | Precio por acción y EPS (no disponibles) | veces |
| `ml` | Razón mercado/libro (M/L) | Precio de mercado por acción / Valor contable por acción | Precio y número de acciones (no disponibles) | veces |
| `maf` | Multiplicador del apalancamiento financiero (MAF) | Activo total / Patrimonio total | Total activo; total patrimonio | veces |
| `roa_dupont` | RSA (ROA) por DuPont | Margen de utilidad neta × Rotación de activos totales | Margen neto; rotación de activos | % |
| `roe_dupont` | RSP (ROE) por DuPont modificado | RSA × MAF | RSA; MAF | % |
| `margen_neto_controladora` | Margen neto (controladora) | Utilidad atribuible a la controladora / Ingresos ordinarios × 100 | Utilidad atribuible a los propietarios de la controladora; ingresos ordinarios | % |
| `roa_controladora` | RSA (controladora) | Margen neto (controladora) × Rotación de activos | Margen neto de la controladora; rotación de activos | % |
| `maf_controladora` | MAF (controladora) | Activo total / Patrimonio atribuible a la controladora | Total activo; total patrimonio − participaciones no controladoras | veces |
| `roe_controladora` | RSP (ROE) de la controladora | RSA (controladora) × MAF (controladora) | RSA y MAF de la controladora | % |

## 7. Ejercicios fiscales

| Ejercicio | Documento | Familia | Estado en la aplicación |
|---|---|---|---|
| 2021 | Certificación de estados combinados 2021 | Combinados (`CB`) | Ejercicio existente (abierto); se agregaron las cuentas de Alutech sin tocar los 19 importes en cero previos |
| 2022 | Certificación de estados combinados 2022 | Combinados (`CB`) | Creado por la carga (abierto) |
| 2023 | Certificación de estados combinados 2023 | Combinados (`CB`) | Creado por la carga (abierto) |
| 2024 | 12_EEFF_diciembre_2024 | Consolidados (`CN`) | Creado por la carga (abierto) |
| 2025 | 12_EEFF_diciembre_2025 | Consolidados (`CN`) | Creado por la carga (abierto) |
