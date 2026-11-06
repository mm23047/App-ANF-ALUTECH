# Aplicación de Análisis Financiero

Aplicación web local para registrar los estados financieros de una empresa, analizarlos a lo largo de varios ejercicios y
exportar los resultados a PDF y Excel. Incluye los datos del caso de estudio de **Alutech, S. A. de C. V. y subsidiarias –
División Acero (2021–2025)** y compara sus resultados con los publicados en el «Trabajo de investigación ANF».

**Qué permite hacer**

- Capturar el Balance General y el Estado de Resultados a mano o desde Excel.
- Generar los estados con subtotales, y el análisis vertical y horizontal.
- Calcular indicadores de liquidez, actividad, endeudamiento y rentabilidad, con su fórmula e interpretación.
- Calcular el modelo DuPont, el WACC y el estado de origen y aplicación de fondos.
- Rastrear cada importe hasta el documento y la página de donde salió.
- Guardar el historial de cambios y hacer copias de seguridad verificadas.

Funciona con Streamlit, SQLite y SQLAlchemy. Los datos se quedan en su equipo: la aplicación solo escucha en `localhost`.

## Contenido

1. [Inicio rápido](#1-inicio-rápido)
2. [Instalación](#2-instalación)
3. [Primer uso](#3-primer-uso)
4. [El menú y las páginas](#4-el-menú-y-las-páginas)
5. [Cómo capturar y corregir datos](#5-cómo-capturar-y-corregir-datos)
6. [Cómo usar los reportes](#6-cómo-usar-los-reportes)
7. [Cómo interpretar los resultados de Alutech](#7-cómo-interpretar-los-resultados-de-alutech)
8. [Copias de seguridad](#8-copias-de-seguridad)
9. [Usar la aplicación con otra empresa](#9-usar-la-aplicación-con-otra-empresa)
10. [Solución de problemas](#10-solución-de-problemas)
11. [Información técnica](#11-información-técnica)

## 1. Inicio rápido

En Windows, desde PowerShell y en la carpeta del proyecto:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```

Se abre el navegador en <http://localhost:8501>. Si la carpeta `data/` todavía no tiene base de datos, siga antes los
pasos de [Primer uso](#3-primer-uso). Para detener la aplicación, pulse `Ctrl+C` en la terminal: los datos no se pierden.

## 2. Instalación

**Requisitos:** Python 3.12. Se probó con Python 3.12.10 en Windows 11 y con las versiones exactas de `requirements.txt`.
La aplicación usa funciones recientes de Streamlit, así que no conviene cambiar esas versiones sin ejecutar las pruebas.
No se ha probado en otros sistemas.

```powershell
# 1. Crear el entorno virtual
py -3.12 -m venv .venv

# 2. Instalar las dependencias
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Activar el entorno es opcional: los comandos de este documento llaman directamente a su Python. Si prefiere activarlo, use
`.venv\Scripts\Activate.ps1` en PowerShell o `source .venv/bin/activate` en macOS y Linux. Con el entorno activo basta
escribir `python` y `streamlit`.

**Ejecutar la aplicación:**

```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```

Si la primera vez Streamlit pide un correo electrónico en la terminal, puede dejarlo vacío y pulsar `Enter`.

## 3. Primer uso

Compruebe primero si existe el archivo `data/financiera.db`. No se publica con el código, porque es local.

### Si ya existe la base de datos

Inicie la aplicación y úsela. Se abre en **Ingreso de datos**, con los cinco ejercicios disponibles. Si la base tiene una
versión antigua, la aplicación la actualiza al arrancar, y antes guarda una copia en `data/backups/`.

### Si no existe: cargar el caso Alutech

Con la aplicación cerrada:

```powershell
# Ensayo sobre una copia temporal; no modifica nada
.venv\Scripts\python.exe scripts/cargar_alutech.py --simular

# Carga real en data/financiera.db
.venv\Scripts\python.exe scripts/cargar_alutech.py
```

La salida debe indicar `Importes creados: 247` y `Controles de totales: 61/61 OK`.

Después inicie la aplicación. **El script no registra la empresa**, así que la primera pantalla será **Datos de la
empresa** y el menú no aparece hasta guardarla. Todos los campos son obligatorios. Para el caso de estudio:

| Campo | Valor |
|---|---|
| Nombre de la empresa | Alutech, S. A. de C. V. y subsidiarias – División Acero |
| Nombre comercial | Alutech – División Acero |
| Actividad económica | metal |
| País | Honduras |
| Moneda de presentación | USD |
| Año inicial de análisis | 2021 |

**Sobre la carga:**

- Es segura de repetir: no duplica datos y nunca sobrescribe ni borra importes.
- Es todo o nada: si un total calculado no coincide con el impreso, o si un importe ya existe con otro valor, no guarda
  nada y muestra `NO SE CARGÓ NADA` con la causa.
- Si ya hay una base de datos, antes crea una copia verificada en `data/backups/`.
- Lee los datos de `fuentes/alutech/estados_financieros_2021_2025.json`, no de los PDF. La carpeta `documentos/` no hace
  falta para ejecutarla.

### Si no existe: empezar con otra empresa

Inicie la aplicación, registre la empresa y comience a capturar. La aplicación crea un catálogo estándar de 30 cuentas,
que puede modificar. Consulte [Usar la aplicación con otra empresa](#9-usar-la-aplicación-con-otra-empresa).

> **Orden de los pasos.** Si carga Alutech *antes* de abrir la aplicación por primera vez, el catálogo tendrá solo sus 106
> cuentas. Si abre la aplicación primero, tendrá además las 30 estándar, que aparecerán vacías en los formularios de
> captura. Las cifras y los indicadores son iguales en ambos casos.

## 4. El menú y las páginas

### Menú visible

| Opción | Para qué sirve |
|---|---|
| **Ingreso de datos** | Capturar el Balance General o el Estado de Resultados de un ejercicio, y crear ejercicios nuevos |
| **Modificación de datos** | Corregir o borrar importes, ver el historial del ejercicio, y cerrar, reabrir o eliminar ejercicios |
| **Indicadores financieros** | Liquidez, actividad, endeudamiento y rentabilidad de todos los ejercicios |
| **Generación de reportes › Balance General** | Balance de un ejercicio con la verificación de la ecuación contable |
| **Generación de reportes › Estado de Resultados** | Estado de un ejercicio con sus utilidades |
| **Generación de reportes › Análisis Vertical** (Balance y Resultados) | Peso de cada cuenta sobre el activo total o los ingresos netos, por ejercicio y comparativo (tablas 7.1 y 7.2 del trabajo) |
| **Generación de reportes › Análisis Horizontal** (Balance y Resultados) | Tablas 3 a 7 del trabajo y comparación de dos ejercicios: saldo actual, saldo anterior, variaciones y sentido del cambio |
| **Generación de reportes › Rentabilidad mediante fórmula DuPont** | Margen neto, rotación, RSA, MAF y RSP/ROE con saldos al cierre, en enfoque total y de la controladora, con interpretación automática |

### Menú completo

El menú normal oculta 17 opciones, entre ellas el Dashboard, los datos de la empresa, el catálogo, la importación desde
Excel y las copias de seguridad. **Para verlas, inicie la aplicación con la variable `ANF_MENU_COMPLETO`.** Aparecen bajo
«Más opciones»:

```powershell
$env:ANF_MENU_COMPLETO = "1"
.venv\Scripts\python.exe -m streamlit run app.py
```

La variable dura mientras esté abierta esa ventana de PowerShell. En `cmd` use `set ANF_MENU_COMPLETO=1`, y en macOS o
Linux `ANF_MENU_COMPLETO=1 streamlit run app.py`.

| Opción | Para qué sirve |
|---|---|
| **Dashboard** | Resumen del último ejercicio, capital de trabajo, liquidez, rentabilidad y evolución entre años |
| **Datos de la empresa** / **Configuración** | Editar los datos de la empresa (ambas abren la misma página) |
| **Catálogo de cuentas** | Crear, editar y desactivar cuentas, y asignar su grupo de análisis |
| **Ingreso de datos › Balance General** / **Estado de Resultados** | Acceso directo a cada formulario de captura |
| **Ingreso de datos › Saldos iniciales** | Registro de los saldos de apertura de cada ejercicio. El DuPont no los usa |
| **Ingreso de datos › Importación Excel** | Descargar plantillas y cargar archivos con vista previa |
| **Datos originales › Trazabilidad y controles** | Documento y página de cada importe, totales impresos contra calculados, y mapeo de cuentas |
| **Reportes › Análisis Horizontal 2021–2025** | Variación absoluta y relativa por rubro, grupo o cuenta |
| **Reportes › Análisis Vertical comparativo 2021–2025** | Análisis vertical de los cinco ejercicios, lado a lado |
| **Reportes › WACC** | Costo promedio ponderado de capital, con sus supuestos y el detalle por ejercicio |
| **Reportes › Origen y aplicación de fondos** | Fuentes y usos entre dos ejercicios consecutivos |
| **Reportes › Informe integral 2021–2025** | Todo el análisis en un solo Excel o PDF |
| **Validación › Comparación con el trabajo ANF** | Resultado calculado contra el publicado, con diferencia, estado y causa |
| **Historial de cambios** | Registro global de cambios, con filtros por tabla, ejercicio y cuenta |
| **Copias de seguridad** | Crear, descargar y restaurar copias |

## 5. Cómo capturar y corregir datos

### Captura manual

1. Abra **Ingreso de datos** y elija *Balance General* o *Estado de Resultados*.
2. Elija el ejercicio. Si no existe, créelo en *Crear nuevo ejercicio fiscal* (años de 1990 a 2100).
3. Escriba los importes y pulse **Guardar**. Esto todavía **no guarda nada**: la aplicación muestra las cuentas, los
   valores actuales y los nuevos.
4. Revise y pulse **Confirmar y guardar**. Con *Cancelar*, o al cambiar de página o de ejercicio, se descarta la operación.

El selector *Borrador / Revisado* es una marca informativa que aparece en el Dashboard y se guarda al cambiarla. No afecta
a los cálculos ni al estado del reporte.

### Reglas de captura

| Situación | Qué hace la aplicación |
|---|---|
| Campo **vacío** | Significa «sin dato» y no se guarda. No equivale a cero |
| **0** escrito | Se guarda como importe igual a cero, y cuenta como dato |
| Vaciar un campo que ya tenía importe | No borra el importe. Use **Borrar importe** en Modificación de datos |
| Más de dos decimales | En la captura se redondea a centavos con aviso; en Excel la fila se rechaza |
| Signo distinto a la convención | Avisa y pide confirmación. **Nunca invierte el signo** |

**Convención de signos:**

| Tipo de cuenta | Signo |
|---|---|
| Ingresos, costos, gastos e impuestos | Positivo; los cálculos ya restan costos y gastos |
| Activos, pasivos y patrimonio | Positivo |
| Cuentas correctoras del activo, como la depreciación acumulada | Negativo |
| Resultados acumulados, resultado del ejercicio y otras cuentas patrimoniales | Pueden ser negativos si hay pérdidas |
| ISR negativo (beneficio fiscal) | Se admite con confirmación |

El Balance y el Estado de Resultados se capturan por separado. La página de captura del Balance muestra la utilidad neta
como referencia, pero no la copia a «Resultado del ejercicio»: si no coinciden, el reporte queda marcado *SIN CONCILIAR*.

### Importación desde Excel

Requiere el [menú completo](#menú-completo).

1. En **Ingreso de datos › Importación Excel**, descargue la plantilla. Trae las cuentas activas del catálogo. Las de
   `assets/plantillas/` son solo una referencia con el catálogo estándar.
2. Complete **Período** (el año) y **Valor monetario** en cada fila que quiera importar. Use punto decimal, sin separador
   de miles y con dos decimales como máximo. Una fila sin valor no se importa. Solo se lee la primera hoja.
3. Suba el archivo `.xlsx`. La vista previa no modifica la base de datos: muestra el estado de cada fila, los ejercicios que
   se crearían y cuántos importes serían nuevos, sobrescritos o sin cambios.
4. Si quiere reemplazar valores existentes, marque *Permitir sobrescribir*. Sin esa casilla, esas filas se omiten.
5. Pulse **Confirmar importación**. Se guardan las filas listas en una sola transacción; las filas con observaciones no se
   importan.

Las causas de rechazo más comunes son `CUENTA_DESCONOCIDA`, `CODIGO_AMBIGUO` (por ejemplo, Excel quitó los ceros a la
izquierda), `DUPLICADA`, `EJERCICIO_CERRADO`, `VALOR_NO_NUMERICO` y `SIGNO_SIN_CONFIRMAR`. La columna *Detalle* explica cada
caso. El tipo de estado se determina por la cuenta del catálogo, no por la columna *Categoría* del archivo.

### Corregir datos ya guardados

En **Modificación de datos**, elija el ejercicio:

- **Balance General / Estado de Resultados:** edite la columna *Valor*, pulse **Guardar cambios** y luego **Confirmar y
  guardar**. Una celda vacía se rechaza.
- **Borrar un importe capturado:** el importe queda como «sin dato», no como cero.
- **Historial de este ejercicio:** muestra la fecha, la operación, la cuenta y los valores anterior y nuevo de cada cambio.
  No indica quién lo hizo, porque la aplicación no tiene usuarios.
- **Ejercicio:** cerrar un ejercicio bloquea su captura, edición, importación y borrado hasta reabrirlo. Solo se pueden
  eliminar ejercicios vacíos.

Si corrige un dato de Alutech, la página de trazabilidad señalará que ya no coincide con el documento. Si se trataba de un
error de transcripción, corrija también `fuentes/alutech/estados_financieros_2021_2025.json`.

### Catálogo de cuentas

Requiere el [menú completo](#menú-completo). Las cuentas no se eliminan: se desactivan. Una cuenta con importes tampoco puede
cambiar de categoría, subcategoría o efecto, para no alterar estados anteriores. Para reclasificarla, cree otra nueva y
desactive la anterior. El *grupo de análisis* es la línea normalizada que permite comparar una cuenta entre ejercicios aunque
cambie su nombre, y se puede cambiar en cualquier momento.

## 6. Cómo usar los reportes

**Reportes de un ejercicio** (Balance, Resultados, Análisis Vertical y DuPont): elija el ejercicio en el selector. El Análisis
Vertical tiene además la pestaña del comparativo de los cinco ejercicios, y el DuPont, sus tablas comparativas al final.

**Indicadores financieros:**

1. Elija el ejercicio de las tarjetas y la interpretación. Las tarjetas muestran el cambio frente al año anterior, sin
   color, porque subir no siempre es favorable.
2. Abra la pestaña *Liquidez*, *Actividad*, *Endeudamiento* o *Rentabilidad*. Cada una trae la tabla comparativa, la base
   financiera, la fórmula, la interpretación, las advertencias metodológicas, un gráfico y su propio PDF y Excel.
3. Al final, *Otros resultados del trabajo* contiene indicadores complementarios, razones de mercado y capital de trabajo.

**Análisis Vertical del Estado de Resultados:** como en la tabla 7.1 del trabajo, los costos, gastos e impuestos tienen
porcentaje negativo. Su importe se muestra como se captura, en positivo, y la columna *Efecto* indica que restan.

**Análisis Horizontal del Balance General y del Estado de Resultados:** las primeras pestañas reproducen las Tablas 3 a 7 del
trabajo. En *Comparar dos ejercicios* elija el par y el nivel de detalle: rubros y totales, grupos de análisis o cuentas con su
denominación original. Una cuenta que no se presenta en un ejercicio figura como *Aparece* o *Desaparece*, sin porcentaje; si
la base es cero o negativa tampoco se calcula el porcentaje. La opción oculta *Análisis Horizontal 2021–2025* se conserva.

**WACC:** vea el resumen de todos los años, los supuestos usados y el detalle del ejercicio que elija.

**Origen y aplicación de fondos:** elija el par de ejercicios. Se construye con variaciones de saldos, así que **no es un
estado de flujos de efectivo**.

**Validación:** filtre por estado y por sección del trabajo. Las coincidencias se ocultan al inicio para centrar la
revisión en las diferencias.

**Informe integral:** en pantalla muestra solo los estados originales. El archivo descargado reúne 11 secciones: estados
originales, horizontal, vertical, indicadores, capital de trabajo, DuPont, WACC, origen y aplicación, comparación con el
trabajo, observaciones y trazabilidad.

### Exportar

Los reportes tienen los botones **Descargar PDF** y **Descargar Excel** al final de la página (en el Informe integral, al
inicio). En el Balance General y el Estado de Resultados, el Excel trae además las columnas *Control* y *Diferencia*, con
fórmulas que recalculan los totales para poder auditarlos.

### Estado del reporte

Cada estado financiero, análisis vertical y DuPont indica si se puede considerar definitivo, en pantalla y en sus archivos:

| Estado | Significado |
|---|---|
| **DEFINITIVO** | Sin observaciones |
| **INCOMPLETO** | Falta una categoría obligatoria: Activo, Pasivo o Patrimonio; o Ingresos, Costo de ventas, Gastos operativos o ISR |
| **DESCUADRADO** | Activo ≠ Pasivo + Patrimonio. Se muestra la diferencia; nada se ajusta automáticamente |
| **SIN CONCILIAR** | El «Resultado del ejercicio» del patrimonio difiere de la utilidad neta |
| **SIGNO ATÍPICO** | Hay importes con signo distinto a la convención |
| **NO INTERPRETABLE** | El patrimonio total al cierre es negativo. Si es cero, el DuPont no se calcula |

## 7. Cómo interpretar los resultados de Alutech

Con los datos correctamente cargados debe obtener estos valores. Son útiles para comprobar una instalación:

| Ejercicio | Activo total (USD) | Utilidad neta (USD) | Capital de trabajo neto (USD) | Razón corriente | ROE al cierre | ROE DuPont | WACC |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2021 | 553,955,185 | 68,602,739 | 177,908,317 | 1.86 | 47.21 % | 47.21 % | 14.59 % |
| 2022 | 672,025,093 | 10,059,310 | 216,728,221 | 1.93 | 4.70 % | 4.70 % | 3.83 % |
| 2023 | 809,100,946 | 13,330,680 | 96,673,859 | 1.29 | 5.86 % | 5.86 % | 3.87 % |
| 2024 | 827,176,374 | 3,060,981 | 69,805,463 | 1.19 | 1.35 % | 1.35 % | 2.58 % |
| 2025 | 782,049,561 | 11,898,987 | −123,568,026 | 0.67 | 5.15 % | 5.15 % | 3.85 % |

Tenga en cuenta lo siguiente al leerlos:

- **El ROE es el mismo en toda la aplicación.** *Indicadores financieros* y *Rentabilidad mediante fórmula DuPont* usan saldos
  **al cierre**, el criterio de las secciones 8.4, 9.5 y 9.6 del trabajo ANF. El producto RSA × MAF coincide con el cálculo
  directo (ganancia neta ÷ patrimonio total al cierre), que el reporte muestra como comprobación.
- **El DuPont de 2021 se calcula de forma normal.** Los saldos al cierre no requieren el balance de 2020, que no se inventa.
- **El reporte DuPont separa dos enfoques.** El total usa la ganancia neta y el patrimonio total. El de la controladora usa las
  cifras atribuibles a sus propietarios, por lo que de 2021 a 2023 da otro resultado: 46.75 %, 4.10 % y 5.41 %.
- **2023 y 2024 no son del todo comparables.** Los estados pasan de combinados a consolidados y cambian denominaciones y
  agrupaciones. En especial, la base de cuentas por cobrar y por pagar cambia, lo que afecta a la rotación de CxC, al PPC, al
  PPP y al ciclo de conversión del efectivo. La pestaña *Actividad* muestra una variante homogénea de los cobros.
- **El WACC es una estimación.** Las tasas de la deuda y el ISR del 30 % son supuestos del trabajo ANF que los documentos
  disponibles no permiten verificar. El costo del patrimonio se aproxima con el ROE y no es un costo exigido por los
  accionistas. Los supuestos están en `fuentes/anf/supuestos_wacc.json`; si los edita, reinicie la aplicación.
- **EPS, P/E y mercado/libro no se calculan.** Los documentos no informan el número de acciones ni un precio de mercado, y la
  aplicación no los inventa. La cobertura de pagos fijos iguala a la de intereses, como indica la sección 8.3 C del trabajo,
  porque los estados no desglosan arrendamientos ni principal: no mide la cobertura real con esos pagos.
- **La página de Validación compara contra la versión vigente del trabajo.** Muestra 741 valores: 711 coinciden, 4 coinciden
  por redondeo, 5 son resultados derivados, 6 difieren y 15 no aplican. Las 6 diferencias vienen del trabajo: la base de cuentas
  por cobrar de 2023 en 8.2 B (3) y la clasificación de una cuenta por cobrar de largo plazo en 9.7 (3). Los derivados son la
  cobertura de pagos fijos: 8.3 C no publica cifras, solo la iguala a la de intereses. Cada fila indica su causa.
- **Ciclo operativo y CCE usan operandos a 2 decimales,** como el desarrollo escrito de la sección 9.3. Por eso el ciclo de 2022
  es 149.28 aunque el valor exacto redondee a 149.29. Los demás indicadores no tienen redondeo intermedio.
- **Cuentas por cobrar tiene dos bases que no son equivalentes.** El indicador principal usa la línea comercial, como 9.3. La
  cartera de comerciales y otras se muestra aparte en la pestaña *Actividad*; 8.2 B publica ese valor solo en 2023.
- **En 2021 no se muestran 18 cuentas del catálogo estándar con importe 0.00.** No figuran en los estados originales ni alteran
  los totales. Siguen guardadas: se ven y se editan en *Modificación de datos*.

Los valores del trabajo ANF nunca se usan como datos ni como resultados: solo sirven para comparar.

## 8. Copias de seguridad

Requiere el [menú completo](#menú-completo). En **Copias de seguridad** puede:

- **Crear una copia:** se guarda y verifica en `data/backups/`.
- **Descargar** cualquier copia existente.
- **Restaurar** una copia existente o un archivo `.db` subido. La aplicación valida el archivo y muestra su contenido antes
  de pedir confirmación. Antes de reemplazar la base, guarda una copia de la actual como `financiera_pre_restauracion_*.db`.
  Si algo falla, la base actual no cambia.

Antes de restaurar, **cierre las demás pestañas de la aplicación**: si otra pestaña o proceso mantiene la base en uso, la
restauración se rechaza. También puede copiar `data/financiera.db` a mano con la aplicación cerrada.

`data/financiera.db` y `data/backups/` no se versionan en Git. Guarde sus copias en otro lugar si necesita conservarlas.

## 9. Usar la aplicación con otra empresa

La aplicación administra **una sola empresa por base de datos**. Para otra empresa, cierre la aplicación, mueva
`data/financiera.db` a otra carpeta, iníciela de nuevo y registre los datos de la empresa. Después:

1. Revise el catálogo y **asigne un grupo de análisis a sus cuentas**. Las 30 cuentas estándar no traen grupo. Sin él, los
   importes entran en los totales pero no en rubros como inventarios o efectivo, por lo que varios indicadores saldrán
   incorrectos o no calculables. Las páginas *Indicadores* y *Análisis Horizontal* avisan cuando falta.
2. Capture o importe los estados de cada ejercicio.

Funcionan sin adaptación los reportes por ejercicio y el DuPont. Estas partes son propias del caso Alutech:

| Parte | Limitación |
|---|---|
| Títulos con «2021–2025» | El texto es fijo, aunque los cálculos usan los ejercicios que existan |
| WACC | Requiere tasas para cada año en `fuentes/anf/supuestos_wacc.json`. Sin ellas, no se calcula |
| Validación | Compara contra el trabajo sobre Alutech y no tiene sentido para otra empresa |
| Trazabilidad | Solo tiene información de lo cargado con `scripts/cargar_alutech.py` |
| Indicadores | Los importes se rotulan siempre en USD y citan secciones del trabajo ANF, aunque la moneda sea otra |

## 10. Solución de problemas

| Problema | Solución |
|---|---|
| No aparece una opción del menú, como Dashboard o Importación Excel | Inicie con `ANF_MENU_COMPLETO=1` ([menú completo](#menú-completo)) |
| Solo se ve «Datos de la empresa» | Es normal mientras no haya empresa registrada. Complete y guarde el formulario |
| PowerShell bloquea `Activate.ps1` | No hace falta activar: use `.venv\Scripts\python.exe` como en este documento |
| `streamlit` no se reconoce como comando | Use `.venv\Scripts\python.exe -m streamlit run app.py` |
| El puerto 8501 está ocupado | Probablemente ya hay una instancia abierta. También puede añadir `--server.port 8502` |
| Una página dice «No hay ejercicios con datos» | Base vacía. [Cargue Alutech](#si-no-existe-cargar-el-caso-alutech) o capture datos |
| `NO SE CARGÓ NADA` al ejecutar el script | Lea la causa: suele ser un importe existente con otro valor o un ejercicio cerrado. La base no cambió |
| Un indicador dice «No calculable» | Debajo de la tabla se indica el motivo; suele faltar un estado o un dato |
| «No se guardó ningún dato» al confirmar | Los datos cambiaron o se restauró una copia desde otra pestaña. Revise y repita la operación |
| No se pueden editar los importes de un año | El ejercicio está cerrado. Reábralo en *Modificación de datos › Ejercicio* |
| «No se pudo actualizar la base de datos» | La migración se detuvo sin aplicar cambios. Revise la copia previa en `data/backups/` |
| Quiero entrar desde otro equipo de la red | No está disponible a propósito: la aplicación no tiene usuarios ni contraseñas y solo atiende a `localhost` |

## 11. Información técnica

### Principios de diseño

- **Precisión:** los importes se guardan como centavos enteros y se calculan con `Decimal`; se redondea solo al presentar.
- **Nada derivado se almacena:** subtotales e indicadores se calculan a partir de los importes vigentes.
- **Una sola definición:** cada indicador está definido una vez en `calculations/indicadores.py`, y lo usan las pantallas,
  las exportaciones y la comparación.
- **Datos, resultados y referencias separados:** datos originales en `fuentes/alutech/`, cálculo en `calculations/` y
  referencias y supuestos del trabajo en `fuentes/anf/`.
- **Nada se corrige en silencio:** signos, descuadres y diferencias se señalan, pero no se ajustan.
- **Texto literal:** lo escrito por el usuario no se interpreta como HTML, Markdown ni fórmulas de Excel.
- **Migraciones automáticas:** al arrancar, la base se lleva a la versión de esquema vigente (4), con copia previa si tiene
  datos. Si un importe no se puede convertir exactamente, la migración se detiene.

### Estructura del proyecto

```text
app.py            Punto de entrada: arranque de la base, menú y enrutamiento
modules/          Páginas de administración y captura: empresa, catálogo, captura, Excel,
                  modificación, Dashboard, historial, copias y trazabilidad
reports/          Reportes en pantalla y exportación a PDF (ReportLab) y Excel (OpenPyXL)
calculations/     Estados, indicadores, DuPont, WACC, origen y aplicación, banderas y comparación
components/       Menú, formato y validación de importes, confirmaciones y transacciones
database/         Modelos, repositorios, migraciones, copias de seguridad y catálogo inicial
fuentes/alutech/  Estados transcritos, con documento, página y denominación original
fuentes/anf/      Referencias, supuestos del WACC y observaciones del trabajo ANF
scripts/          Carga de Alutech y generación del informe de validación
assets/plantillas/ Plantillas Excel de referencia
data/             Base de datos y copias de seguridad (no se versionan)
tests/            Pruebas automatizadas
```

### Scripts

```powershell
# Cargar los estados de Alutech. Opciones: --simular, --bd RUTA.db, --datos ARCHIVO.json
.venv\Scripts\python.exe scripts/cargar_alutech.py

# Regenerar INFORME_VALIDACION_FINANCIERA.md. Solo lee la base. Opciones: --bd RUTA.db, --salida ARCHIVO.md
.venv\Scripts\python.exe scripts/generar_informe_validacion.py
```

### Pruebas

```powershell
.venv\Scripts\python.exe -m pytest tests -q
```

Resultado más reciente: **695 pruebas aprobadas de 695** (2026-11-05, Python 3.12.10, en una copia del proyecto). Las pruebas
usan bases temporales, y `tests/conftest.py` hace fallar la ejecución si cambia `data/financiera.db`.

### Documentación adicional

Estos archivos, junto con `tests/`, `documentos/` y `scripts/generar_informe_validacion.py`, pueden no estar en una copia
publicada del código.

| Archivo | Contenido |
|---|---|
| `REGISTRO_DE_CAMBIOS.md` | Cambios realizados en la adaptación |
| `MAPEO_FINANCIERO_ALUTECH.md` | Correspondencia entre cuentas, grupos, rubros e indicadores |
| `INVESTIGACION_DOCUMENTAL_ANF.md` | Revisión de los documentos fuente |
| `INFORME_VALIDACION_FINANCIERA.md` | Comparación detallada con el trabajo ANF (generado el 2026-11-02) |
| `MATRIZ_ADAPTACION.md` | Relación entre los requerimientos del trabajo y los módulos de la aplicación |
| `MATRIZ_DE_PRUEBAS.md`, `INVENTARIO_DEL_PROYECTO.md` | Pruebas e inventario de la auditoría del 2026-11-01; no reflejan el estado actual |
| `AUDITORIA_*.md`, `INFORME_CIERRE_FASE1.md`, `INFORME_RECUPERACION_CALCULATIONS.md`, `PLAN_DE_CORRECCION.md` | Auditorías y fases de corrección |
