# Análisis financiero horizontal

## Concepto y finalidad

El análisis horizontal es una técnica de análisis financiero que compara el saldo de una misma partida en dos o más períodos contables. Su propósito es medir cuánto y en qué proporción cambió cada partida, con el fin de estudiar la evolución de la situación financiera y de los resultados de la empresa a lo largo del tiempo.

A diferencia del análisis vertical, que relaciona cada partida con una base dentro de un mismo ejercicio, el análisis horizontal examina el comportamiento de una partida entre ejercicios. Permite observar la magnitud de los cambios, identificar las partidas que más variaron y disponer de una base para investigar sus causas. Por sí solo mide variaciones, pero no las explica: las causas deben buscarse en los estados financieros, en sus notas y en otra información verificable.

## Procedimiento y fórmulas

El procedimiento compara el saldo de cada partida en un ejercicio con su saldo en el ejercicio inmediatamente anterior, que actúa como base de la comparación. Para cada par de ejercicios consecutivos se determinan dos medidas: la variación absoluta y la variación relativa.

$$
VA = VP_t - VP_{t-1}
$$

$$
VR = \frac{VP_t - VP_{t-1}}{VP_{t-1}} \times 100
$$

Donde:

- $VA$: variación absoluta, expresada en dólares estadounidenses.
- $VR$: variación relativa porcentual.
- $VP_t$: valor de la partida en el período actual.
- $VP_{t-1}$: valor de la partida en el período anterior.

La variación absoluta indica la magnitud monetaria del cambio, y su signo muestra si el saldo aumentó o disminuyó. La variación relativa expresa ese cambio como porcentaje del saldo anterior. Por ejemplo, el efectivo y sus equivalentes pasaron de USD 10,840,865 en 2021 a USD 20,155,298 en 2022, lo que representa una variación absoluta de +USD 9,314,433 y una variación relativa de +85.92 %.

Los cálculos se realizan en la aplicación financiera desarrollada para este trabajo, a partir de los saldos registrados de los estados financieros de Alutech, S. A. de C. V. y subsidiarias, División Acero. Los subtotales y totales no se capturan: se obtienen de las cuentas registradas. Las variaciones se recalculan cada vez que se consultan, de modo que cualquier cambio en un saldo registrado se refleja en los ejercicios y en las partidas afectadas. Los porcentajes se calculan con la precisión completa y se redondean a dos decimales solo para su presentación. Si un balance registrado no cuadra o un estado está incompleto, la aplicación lo advierte e indica la diferencia, sin modificar los datos.

## Períodos analizados

El análisis comprende los ejercicios terminados el 31 de diciembre de 2021, 2022, 2023, 2024 y 2025, en dólares estadounidenses. Cada ejercicio se compara con el anterior, lo que da lugar a cuatro comparaciones interanuales consecutivas: 2021–2022, 2022–2023, 2023–2024 y 2024–2025. El ejercicio 2021 actúa únicamente como base, porque no se dispone de información de 2020 dentro del período analizado.

Las cifras de 2021 a 2023 proceden de certificaciones de estados financieros combinados, y las de 2024 y 2025, de estados financieros consolidados. Cada documento presenta un solo ejercicio, por lo que las comparaciones se construyen con el saldo de cada año tal como fue informado en su propio documento.

## Análisis del Balance General

En el Balance General, denominado estado de situación financiera en los documentos de la empresa, se comparan los saldos al cierre de cada ejercicio de las cuentas seleccionadas y de los totales de activo corriente, pasivo corriente, activo, pasivo y patrimonio. Esta comparación permite observar cómo cambiaron los recursos de la empresa, sus obligaciones y su patrimonio. Los resultados se presentan en dos tablas: 2021–2023 y 2023–2025.

Las cuentas por cobrar requieren una precisión. La tabla 2021–2023 utiliza la línea «Cuentas por cobrar comerciales». La tabla 2023–2025 utiliza, como agrupación analítica, las cuentas por cobrar comerciales y las otras cuentas por cobrar, porque los estados de 2024 y 2025 presentan una sola línea denominada «Deudores comerciales y Otras Cuentas por Cobrar». Por esta razón, el importe de 2023 es de USD 41,272,525 en la primera tabla y de USD 96,097,483 en la segunda.

A partir de los mismos saldos se calcula el capital de trabajo neto, definido como activo corriente menos pasivo corriente, y se aplican a este resultado las fórmulas anteriores. Así se observa cómo evolucionó la diferencia entre los activos y los pasivos corrientes, junto con la razón corriente y la prueba ácida de cada ejercicio.

## Análisis del Estado de Resultados

En el Estado de Resultados se comparan los ingresos ordinarios, el costo de ventas, los gastos operativos y los gastos financieros netos, así como la utilidad bruta, la utilidad operativa y la utilidad neta. Esta comparación permite observar cómo cambiaron los ingresos, los costos, los gastos y los resultados de cada ejercicio. Los costos y gastos se expresan en positivo: una variación positiva en estas partidas significa un mayor costo o gasto.

Algunas partidas se construyen para hacer posible la comparación. Los gastos operativos reúnen los gastos de administración y de venta o distribución y, en 2024 y 2025, también los de personal y los de depreciación y amortización. Los gastos financieros netos corresponden al importe neto presentado en 2021–2023 y a la diferencia entre gastos e ingresos financieros en 2024–2025. La utilidad operativa de 2022 y 2023, que esos estados no imprimen, se obtiene de sus partidas impresas.

## Niveles de detalle

Además de las tablas anteriores, la aplicación permite comparar dos ejercicios consecutivos en tres niveles de detalle:

- **Rubros y totales:** las partidas principales de cada estado.
- **Grupos de análisis:** las cuentas clasificadas en categorías normalizadas.
- **Cuentas:** cada cuenta con su denominación original.

Para cada partida se presenta el saldo actual, el saldo anterior, las dos variaciones, el sentido del cambio y, cuando corresponde, una observación en la propia fila. Las descargas en PDF y Excel incluyen todos los pares de ejercicios con el nivel de detalle seleccionado.

## Tratamiento de las partidas no presentadas

La ausencia de una partida en un estado financiero no equivale a un saldo de cero. Por ello se distinguen dos situaciones:

- **Saldo cero informado.** El estado presenta la partida con un importe nulo. Se trata como un saldo real: las participaciones no controladoras, por ejemplo, pasan a cero en 2023, y esa variación de −100 % es válida.
- **Partida no presentada.** La partida no figura en uno de los dos ejercicios. No se le asigna ningún saldo, la celda indica «Sin dato», no se calcula variación y la partida se identifica como una que aparece o desaparece.

Cuando una partida deja de presentarse por separado y, por su denominación, podría estar comprendida en otra línea, se identifica como «Presentación agrupada». Es el caso de las cuentas por pagar comerciales de 2023 frente a la línea «Acreedores comerciales y Otras Cuentas por Pagar» de 2024. Si una línea conserva su nombre, pero la presentación de las partidas relacionadas cambia entre ambos ejercicios, se muestran sus saldos y se indica «No comparable», porque la variación compararía contenidos posiblemente distintos. Es el caso de los activos intangibles entre 2023 y 2024.

## Agrupaciones analíticas

Una agrupación analítica es la suma de varias líneas que, en otro ejercicio, parecen presentarse en una sola. Permite obtener una referencia de comparación cuando las líneas individuales no son comparables. Sin embargo, la coincidencia o la semejanza de las denominaciones no demuestra que los conceptos sean equivalentes.

Por este motivo, las agrupaciones cuya composición no ha podido comprobarse se identifican como «Agrupación analítica; comparabilidad no confirmada». La variación se calcula, pero no debe interpretarse como plenamente comparable. Esto se aplica entre 2023 y 2024 a las cuentas por cobrar comerciales y otras (+1.15 %), a los gastos operativos (+4.33 %) y a los gastos financieros netos (+27.47 %). En el caso de las cuentas por cobrar, la comparabilidad depende de confirmar que la línea unificada de 2024 y 2025 contiene exactamente las cuentas comerciales y las otras cuentas por cobrar, sin conceptos adicionales.

## Variaciones no calculables

Cuando una variación no se presenta, la celda indica el motivo:

- **«Sin dato»:** falta el importe de uno de los ejercicios, por lo que no existe base de comparación.
- **«No calculable»:** el saldo anterior es cero o negativo. Si es cero, la fórmula implicaría dividir entre cero; si es negativo, el signo del cociente no representaría el sentido del cambio. En ambos casos se conserva la variación absoluta. «Otras reservas de capital», por ejemplo, pasó de −USD 2,360,428 en 2022 a −USD 1,439,577 en 2023, con una variación absoluta de +USD 920,851.
- **«No comparable»:** la presentación de la partida cambia entre los dos ejercicios, por lo que no se calcula ninguna variación.

## Cambios de signo

Cuando una partida pasa de un saldo positivo a uno negativo, la base es positiva y el porcentaje puede calcularse, pero una disminución superior a 100 % indica que la partida cambió de signo. El capital de trabajo neto pasó de +USD 69,805,463 en 2024 a −USD 123,568,026 en 2025, con una variación absoluta de −USD 193,373,489 y una relativa de −277.02 %. Este porcentaje no debe interpretarse sin considerar la variación absoluta y el cambio de signo. Cuando el cambio es de negativo a positivo, la base es negativa: no se calcula el porcentaje, se informa la variación absoluta y se advierte el cambio de signo.

## Interpretación financiera de los resultados

Un aumento indica que el saldo actual es mayor que el anterior, y una disminución, que es menor. El signo describe el sentido del cambio, pero no permite juzgar por sí solo si la situación financiera mejoró o empeoró. Una variación positiva no significa necesariamente una mejora, ni una variación negativa, un deterioro: la interpretación depende de la naturaleza de la partida y de su relación con las demás.

Un aumento del activo corriente puede ser favorable para la liquidez, mientras que un aumento del pasivo corriente representa mayores obligaciones de corto plazo. Una reducción de los costos debe valorarse junto con la evolución de los ingresos: entre 2024 y 2025, el costo de ventas disminuyó 12.19 %, los ingresos ordinarios disminuyeron 8.20 % y la utilidad bruta aumentó 6.62 %. De igual forma, la reducción de los inventarios de 40.20 % en el mismo período no basta para saber, sin información adicional, si responde a una mejor gestión, a menores compras o a otra causa.

La variación relativa debe leerse junto con la absoluta, porque una base pequeña puede producir un porcentaje muy alto. La utilidad neta, por ejemplo, aumentó 288.73 % entre 2024 y 2025 al pasar de USD 3,060,981 a USD 11,898,987. El porcentaje es correcto, pero en parte refleja el reducido saldo de partida. Del mismo modo, los otros ingresos o gastos pasaron de USD 55,570 a −USD 811,571, lo que equivale a −1560.45 %: la cifra combina una base muy pequeña con un cambio de signo.

## Limitaciones de comparabilidad

Los resultados deben interpretarse considerando las siguientes limitaciones, comprobadas durante la revisión de los documentos:

1. **Cambio de estados combinados a consolidados.** Los ejercicios 2021–2023 se presentan como estados combinados y los de 2024–2025, como estados consolidados, con otra estructura y otras denominaciones. Las cuentas individuales de ambos conjuntos no se enlazan directamente, y las variaciones de 2023–2024 deben interpretarse con especial cautela.
2. **Compañías incluidas.** Las certificaciones de 2021 a 2023 no enumeran el mismo conjunto de compañías combinadas, y los documentos de 2024 y 2025 no presentan esa relación. Por ello, parte de las variaciones podría deberse a cambios en las entidades incluidas, y no solo a la evolución de sus operaciones.
3. **Composición no comprobada de las líneas unificadas.** Los estados de 2024 y 2025 no detallan la composición de sus líneas ni incluyen notas. La relación con las partidas de años anteriores se apoya en sus denominaciones y, en algunos casos, en un resumen no auditado de la empresa calificadora, cuyas cifras de 2023 no coinciden con las certificaciones. Ninguno de estos elementos demuestra por sí solo la equivalencia.
4. **Diferente composición de la utilidad operativa.** En 2023, la utilidad operativa incluye los otros ingresos netos y el deterioro de cuentas por cobrar. En 2024, los otros ingresos o gastos se presentan después del resultado de operación. Por ello, la variación de 2023–2024 (−21.25 %) no es plenamente comparable.
5. **Cuentas por cobrar a largo plazo.** La línea de mayor importe dentro de las cuentas por cobrar a largo plazo se refiere a partes relacionadas en 2023 y 2025, pero en 2024 se denomina «Otras cuentas por cobrar a LP», sin que el documento explique la diferencia. Además, los saldos con partes relacionadas pueden haberse reclasificado entre corriente y no corriente, por lo que la variación de una sola de esas líneas no permite concluir sobre la evolución de esos saldos en conjunto.
6. **Diferencia en el capital social de 2024.** El estado de 2024 imprime un capital social de USD 119,391,833, USD 2,000 más que los de 2022, 2023 y 2025. Se conserva el importe del estado original, que cuadra con su total de patrimonio; la diferencia requiere confirmación documental.
7. **Información disponible.** Los documentos de 2024 y 2025 contienen únicamente el estado de situación financiera y el estado de resultados, por lo que no permiten examinar la composición de las partidas ni las causas de sus variaciones.

Estas limitaciones no invalidan el cálculo de las variaciones, pero sí condicionan el alcance de lo que puede concluirse a partir de ellas.

---

<!-- FIN DEL TEXTO PARA EL DOCUMENTO. LO QUE SIGUE NO DEBE COPIARSE. -->

# Notas para la persona que revisa (no copiar al documento)

Estas notas no forman parte del texto académico.

1. **Estado.** Versión para tu revisión. **No se ha insertado en el documento principal ni se ha regenerado el PDF** (R-15).
2. **Encaje con el documento.** Cubre lo que hoy tratan 6.1 a 6.3 y amplía el método; no sustituye las tablas ni el análisis de 6.4 a 6.8.
3. **Notación.** Se usan $VA$, $VR$ y $VP_t$, según lo solicitado. El documento vigente usa $ΔV$, $Δ\%$ y $V_t$ en 6.3. Hay que elegir una sola al incorporar el texto.
4. **Agrupaciones.** La sección solo describe las que hoy calcula la aplicación. Si autorizas filas nuevas de R-2, hay que ampliarla.
5. **Limitación 3.** Menciona el informe de PCR de forma genérica; conviene citarlo con la referencia de la bibliografía aprobada, si se conserva.
6. **Citas.** No se añadieron referencias bibliográficas porque 6.1 a 6.3 no las incluyen. Si la rúbrica las exige, deben tomarse de la bibliografía ya aprobada.
7. **Base B2.** Si se comprueba la composición de la línea unificada y se adopta B2, hay que actualizar la sección de agrupaciones y la del Balance General.
