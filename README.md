# Aplicación de Análisis Financiero – Alutech, División Acero

Aplicación web local para registrar los estados financieros de una empresa, analizarlos a lo largo de varios ejercicios y
exportar los resultados a PDF y Excel. El repositorio incluye el caso de estudio de **Alutech, S. A. de C. V. y subsidiarias –
División Acero (ejercicios 2021–2025)**, listo para usar desde la primera ejecución.

## Contenido

1. [Presentación](#1-presentación)
2. [Funcionalidades](#2-funcionalidades)
3. [Requisitos previos](#3-requisitos-previos)
4. [Instalación en Windows](#4-instalación-en-windows)
5. [Instalación en Debian/Linux](#5-instalación-en-debianlinux)
6. [Ejecutar la aplicación](#6-ejecutar-la-aplicación)
7. [Base de datos](#7-base-de-datos)
8. [Documentos](#8-documentos)
9. [El menú y las páginas](#9-el-menú-y-las-páginas)
10. [Cómo capturar y corregir datos](#10-cómo-capturar-y-corregir-datos)
11. [Cómo usar los reportes](#11-cómo-usar-los-reportes)
12. [Cómo interpretar los resultados de Alutech](#12-cómo-interpretar-los-resultados-de-alutech)
13. [Usar la aplicación con otra empresa](#13-usar-la-aplicación-con-otra-empresa)
14. [Pruebas](#14-pruebas)
15. [Solución de problemas](#15-solución-de-problemas)
16. [Información técnica](#16-información-técnica)
17. [Créditos y contexto académico](#17-créditos-y-contexto-académico)

## 1. Presentación

**Objetivo.** Automatizar el análisis financiero del caso Alutech conforme a la metodología del documento «Trabajo de
investigación ANF»: la aplicación registra la información, la procesa, calcula los indicadores y análisis, y genera reportes.

**Cómo funciona.** Los importes se guardan en una base de datos local. Cada reporte e indicador se calcula a partir de los
importes vigentes, de modo que si corrige un dato, todos los resultados se actualizan. Los valores publicados en el trabajo
académico no se usan como datos ni como resultados: solo sirven para compararlos en la página de validación.

**Tecnologías.** Python, Streamlit (interfaz), SQLite y SQLAlchemy (datos), pandas y Plotly (tablas y gráficos), ReportLab
(PDF), OpenPyXL (Excel) y pytest (pruebas).

## 2. Funcionalidades

**En el menú principal:**

- Ingreso y modificación de datos: Balance General y Estado de Resultados, con historial y cierre de ejercicios.
- Indicadores financieros: liquidez y capital de trabajo, actividad, endeudamiento y rentabilidad, con fórmula e interpretación.
- Reportes: Balance General, Estado de Resultados, análisis vertical y horizontal de ambos, y rentabilidad con DuPont.
- Descarga de los reportes en PDF y Excel.

**En el menú completo**, que se activa con una variable ([cómo activarlo](#menú-completo)):

- WACC, estado de origen y aplicación de fondos e informe integral 2021–2025.
- Dashboard, datos de la empresa y catálogo de cuentas.
- Importación desde Excel y saldos iniciales.
- Trazabilidad de cada importe hasta su documento y página, y comparación con el trabajo académico.
- Historial global de cambios y copias de seguridad.

## 3. Requisitos previos

| Requisito | Detalle |
|---|---|
| Sistema operativo | **Probado:** Windows 11 y Ubuntu 24.04 (WSL). **Esperado, sin probar:** Debian 12 y 13 |
| Python | **3.12, la versión recomendada** (3.12.10 en Windows y 3.12.3 en Ubuntu). También pasan las pruebas en Ubuntu con **3.11 y 3.13** |
| Espacio en disco | Para el entorno virtual, unos **500 MB en Windows y 750 MB en Linux**, más unos 50 MB del repositorio |
| Internet | Solo para clonar el repositorio e instalar las dependencias. La aplicación funciona sin conexión |
| Navegador | Cualquiera actual. Se probó con Microsoft Edge |

## 4. Instalación en Windows

Use **PowerShell**.

**1. Instale Python 3.12** desde <https://www.python.org/downloads/>. En el instalador marque *Add python.exe to PATH*.
Compruébelo:

```powershell
py -3.12 --version
```

**2. Instale Git** desde <https://git-scm.com/download/win> y **clone el repositorio:**

```powershell
git clone https://github.com/mm23047/App-ANF-ALUTECH.git
cd App-ANF-ALUTECH
```

**3. Cree el entorno virtual e instale las dependencias:**

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**4. Inicie la aplicación:**

```powershell
.venv\Scripts\python.exe -m streamlit run app.py
```

No hace falta ninguna otra configuración: en la primera ejecución se crea `data/financiera.db` a partir de la base inicial.

Activar el entorno es opcional, porque estos comandos llaman directamente a su Python. Si prefiere activarlo, use
`.venv\Scripts\Activate.ps1`; después basta con escribir `python` y `streamlit`. Si PowerShell lo bloquea, consulte
[Solución de problemas](#15-solución-de-problemas).

## 5. Instalación en Debian/Linux

**1. Instale Git y Python** con sus herramientas:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv
python3 --version
```

Debian 12 trae Python 3.11 y Debian 13, Python 3.13. Las pruebas pasaron con ambas versiones, pero en Ubuntu 24.04: **en Debian
no se ha probado directamente**.

**2. Clone el repositorio:**

```bash
git clone https://github.com/mm23047/App-ANF-ALUTECH.git
cd App-ANF-ALUTECH
```

**3. Cree el entorno virtual, actívelo e instale las dependencias:**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

**4. Inicie la aplicación:**

```bash
python -m streamlit run app.py
```

No hace falta ninguna otra configuración. En cada terminal nueva, active el entorno con `source .venv/bin/activate`.

## 6. Ejecutar la aplicación

El archivo de entrada es `app.py`. En Windows use `.venv\Scripts\python.exe` en lugar de `python`, salvo que haya activado el
entorno.

| Acción | Cómo |
|---|---|
| Iniciar | `python -m streamlit run app.py` |
| Abrir | <http://localhost:8501>, el puerto predeterminado. Normalmente el navegador se abre solo |
| Detener | `Ctrl+C` en la terminal. Los datos no se pierden |
| Cambiar de puerto | `python -m streamlit run app.py --server.port 8502` |

Si la primera vez Streamlit pide un correo electrónico en la terminal, déjelo vacío y pulse `Enter`.

La aplicación se abre en **Ingreso de datos**, con los cinco ejercicios disponibles.

**Acceso desde otra computadora.** Por defecto solo atiende a su propio equipo, porque **no tiene usuarios ni contraseñas**:
cualquiera que llegue a ella puede modificar los datos. Si necesita mostrarla en una red de confianza, inicie así y entre con
la IP de su equipo; es posible que deba autorizar el puerto en el cortafuegos:

```bash
python -m streamlit run app.py --server.address 0.0.0.0
```

No lo use en redes públicas.

## 7. Base de datos

La aplicación usa **SQLite**: toda la información está en un archivo, sin servidor que instalar.

| Archivo | Para qué sirve | ¿En Git? |
|---|---|---|
| `data/inicial/financiera.db` | Base de partida con Alutech 2021–2025. **No la modifique ni la elimine** | Sí |
| `data/financiera.db` | Su base de trabajo. Aquí se guardan todos sus cambios | No |
| `data/backups/` | Copias de seguridad automáticas y manuales | No |

**Inicialización.** Si no existe `data/financiera.db`, la aplicación la crea copiando la base inicial. Nunca sobrescribe una
base existente. Si la base tiene una versión antigua, la actualiza al arrancar, y antes guarda una copia en `data/backups/`.

**Trabaje con su propia copia.** Cada integrante tiene su base local, y sus cambios no llegan a los demás mediante Git. No
coloque `data/financiera.db` en una carpeta sincronizada (Drive, OneDrive, Dropbox) para usarla entre varios: SQLite no está
pensado para ese uso y la base podría dañarse. Para compartir datos, descargue una copia y envíela.

**Volver a los datos originales de Alutech.** Cierre la aplicación, mueva o renombre `data/financiera.db` a otra carpeta e
iníciela de nuevo.

### Copias de seguridad

Requiere el [menú completo](#menú-completo). En **Copias de seguridad** puede:

- **Crear una copia:** se guarda y verifica en `data/backups/`.
- **Descargar** cualquier copia existente.
- **Restaurar** una copia existente o un archivo `.db` subido. La aplicación valida el archivo y muestra su contenido antes
  de pedir confirmación. Antes de reemplazar la base, guarda una copia de la actual como `financiera_pre_restauracion_*.db`.
  Si algo falla, la base actual no cambia.

Antes de restaurar, **cierre las demás pestañas de la aplicación**: si otra pestaña o proceso mantiene la base en uso, la
restauración se rechaza. También puede copiar `data/financiera.db` a mano con la aplicación cerrada.

Guarde sus copias también en otro lugar si necesita conservarlas: `data/financiera.db` y `data/backups/` no se versionan.

## 8. Documentos

| Ubicación | Contenido | Propósito |
|---|---|---|
| `Trabajo de investigación ANF.md` y `.pdf` | Trabajo académico | Referencia metodológica: fórmulas, indicadores y criterios. Las pruebas comparan los resultados con la versión Markdown |
| `documentos/` | 5 estados financieros de Alutech: 2 EEFF (2024 y 2025) y 3 certificaciones (2021 a 2023) | Fuente de cada importe. La página de trazabilidad cita su documento y página |
| `fuentes/alutech/` | Estados transcritos en JSON | Datos con los que se puede regenerar la base |
| `fuentes/anf/` | Valores de referencia y supuestos del WACC | Comparación con el trabajo y supuestos no verificables con los estados |
| `MAPEO_FINANCIERO_ALUTECH.md` | Correspondencia entre cuentas, grupos, rubros e indicadores | Consulta técnica |
| `DESCRIPCION_ACADEMICA_ANALISIS_HORIZONTAL.md` | Descripción del análisis horizontal | Consulta académica |
| `assets/plantillas/` | Plantillas de Excel | Referencia para la importación |

La aplicación no abre los PDF para funcionar: lee los datos de la base. Los materiales de terceros, como el libro de texto y
las presentaciones de clase, no se distribuyen en este repositorio.

## 9. El menú y las páginas

### Menú principal

| Opción | Para qué sirve |
|---|---|
| **Ingreso de datos** | Capturar el Balance General o el Estado de Resultados de un ejercicio, y crear ejercicios nuevos |
| **Modificación de datos** | Corregir o borrar importes, ver el historial del ejercicio, y cerrar, reabrir o eliminar ejercicios |
| **Indicadores financieros** | Liquidez, actividad, endeudamiento y rentabilidad de todos los ejercicios |
| **Generación de reportes › Balance General** | Balance de un ejercicio con la verificación de la ecuación contable |
| **Generación de reportes › Estado de Resultados** | Estado de un ejercicio con sus utilidades |
| **Generación de reportes › Análisis Vertical** (Balance y Resultados) | Peso de cada cuenta sobre el activo total o los ingresos netos, por ejercicio y comparativo (tablas 7.1 y 7.2 del trabajo) |
| **Generación de reportes › Análisis Horizontal** (Balance y Resultados) | Análisis de la situación financiera, del estado de resultados y del capital de trabajo, calculados por la aplicación, y comparación de dos ejercicios: saldo actual, saldo anterior, variaciones y sentido del cambio |
| **Generación de reportes › Rentabilidad mediante fórmula DuPont** | Margen neto, rotación, RSA, MAF y RSP/ROE con saldos al cierre, en enfoque total y de la controladora, con interpretación automática |

### Menú completo

El menú normal oculta 17 opciones, entre ellas el Dashboard, los datos de la empresa, el catálogo, la importación desde
Excel y las copias de seguridad. **Para verlas, inicie la aplicación con la variable `ANF_MENU_COMPLETO`.** Aparecen bajo
«Más opciones»:

En Windows, con PowerShell:

```powershell
$env:ANF_MENU_COMPLETO = "1"
.venv\Scripts\python.exe -m streamlit run app.py
```

En Debian/Linux, con el entorno activado:

```bash
ANF_MENU_COMPLETO=1 python -m streamlit run app.py
```

La variable dura mientras esté abierta esa terminal.

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

## 10. Cómo capturar y corregir datos

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

## 11. Cómo usar los reportes

**Reportes de un ejercicio** (Balance, Resultados, Análisis Vertical y DuPont): elija el ejercicio en el selector. El Análisis
Vertical tiene además la pestaña del comparativo de los cinco ejercicios, y el DuPont, sus tablas comparativas al final.

**Indicadores financieros:**

1. Elija el ejercicio de las tarjetas y la interpretación. Las tarjetas muestran el cambio frente al año anterior, sin
   color, porque subir no siempre es favorable.
2. Abra la pestaña *Liquidez*, *Actividad*, *Endeudamiento* o *Rentabilidad*. Cada una trae la tabla comparativa, la base
   financiera, la fórmula, la interpretación, las advertencias metodológicas, un gráfico y su propio PDF y Excel.
3. Al final, *Otros resultados* contiene indicadores complementarios, razones de mercado y capital de trabajo.

**Análisis Vertical del Estado de Resultados:** como en la tabla 7.1 del trabajo, los costos, gastos e impuestos tienen
porcentaje negativo. Su importe se muestra como se captura, en positivo, y la columna *Efecto* indica que restan.

**Análisis Horizontal del Balance General y del Estado de Resultados:** las primeras pestañas presentan los análisis calculados a
partir de la información financiera registrada, conforme a la metodología del trabajo ANF. En *Comparar dos ejercicios* elija el par y el nivel de detalle: rubros y totales, grupos de análisis o cuentas con su
denominación original. Una partida que no se presenta en un ejercicio figura como *Aparece* o *Desaparece*, sin variación, y no
se iguala a cero; si puede estar agrupada en otra línea figura como *Presentación agrupada*, y si cambió su contenido, como
*No comparable*. Las sumas con composición no comprobada calculan la variación con la advertencia «Agrupación analítica;
comparabilidad no confirmada». Cada celda sin valor indica su causa: *Sin dato*, *No calculable* (base cero o negativa) o *No comparable*.
Si un balance no cuadra o un estado está incompleto, la página lo advierte sin corregir los datos. Las descargas usan el nivel
elegido. La opción oculta *Análisis Horizontal 2021–2025* se conserva.

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

## 12. Cómo interpretar los resultados de Alutech

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

## 13. Usar la aplicación con otra empresa

La aplicación administra **una sola empresa por base de datos**. Para otra empresa, cierre la aplicación, mueva
`data/financiera.db` a otra carpeta e iníciela con la variable `ANF_BASE_VACIA`, para que no copie la base de Alutech:

```powershell
# Windows (PowerShell)
$env:ANF_BASE_VACIA = "1"
.venv\Scripts\python.exe -m streamlit run app.py
```

```bash
# Debian/Linux
ANF_BASE_VACIA=1 python -m streamlit run app.py
```

Solo hace falta en esa primera ejecución: la aplicación crea una base vacía con un catálogo estándar de 30 cuentas. Registre los
datos de la empresa y, después:

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
| Trazabilidad | Solo tiene información de los importes de Alutech |
| Indicadores | Los importes se rotulan siempre en USD y citan secciones del trabajo ANF, aunque la moneda sea otra |

## 14. Pruebas

Las dependencias de `requirements.txt` ya incluyen pytest.

```powershell
# Windows
.venv\Scripts\python.exe -m pytest tests -q
```

```bash
# Debian/Linux, con el entorno activado
python -m pytest tests -q
```

Resultado más reciente: **en un clon nuevo, 1156 aprobadas y 2 omitidas en Windows 11, y 1154 aprobadas y 4 omitidas en Ubuntu 24.04 (2026-11-06).
Dos omisiones esperan a que exista `data/financiera.db`: con ella, en Windows son 1158 aprobadas. Las otras dos, solo en Linux,
comprueban bloqueos de archivos propios de Windows**. Tarda varios minutos. Las pruebas usan bases temporales, y `tests/conftest.py` hace
fallar la ejecución si cambia `data/financiera.db`. Antes de cambiar una versión de `requirements.txt`, ejecute la suite.

Para comprobar una instalación a simple vista, compare con los valores de la sección
[Cómo interpretar los resultados de Alutech](#12-cómo-interpretar-los-resultados-de-alutech).

## 15. Solución de problemas

| Problema | Solución |
|---|---|
| `py` o `python` no se reconoce (Windows) | Reinstale Python 3.12 marcando *Add python.exe to PATH* y abra otra terminal |
| `python3 -m venv` falla: falta `ensurepip` (Debian/Linux) | Instale el paquete: `sudo apt install python3-venv` |
| `ModuleNotFoundError` al iniciar | Faltan dependencias o no usa el entorno. Repita `pip install -r requirements.txt` con el Python de `.venv` |
| `No matching distribution found` al instalar | Su versión de Python no tiene esas versiones de los paquetes. Use una versión de Python de la tabla de requisitos |
| PowerShell bloquea `Activate.ps1` | No hace falta activar: use `.venv\Scripts\python.exe`. Si quiere activar, ejecute antes `Set-ExecutionPolicy -Scope Process RemoteSigned` |
| `streamlit` no se reconoce como comando | Use `python -m streamlit run app.py` con el Python del entorno |
| El puerto 8501 está ocupado | Probablemente ya hay una instancia abierta. Ciérrela o añada `--server.port 8502` |
| No existe `data/financiera.db` | Es normal antes de la primera ejecución: se crea al iniciar. Si también falta `data/inicial/financiera.db`, recupérela con `git checkout -- data/inicial/financiera.db` |
| Solo se ve «Datos de la empresa» o «No hay ejercicios con datos» | La base está vacía. Cierre la aplicación, mueva `data/financiera.db` a otra carpeta e iníciela sin `ANF_BASE_VACIA` |
| `Permission denied` o `attempt to write a readonly database` | No tiene permisos sobre la carpeta `data/`. Clone el repositorio en una carpeta de su usuario, fuera de carpetas sincronizadas o protegidas |
| «database is locked» | Otra instancia usa la base, o está en una carpeta sincronizada. Cierre las demás instancias |
| El botón de descarga de PDF o Excel no responde | Tras cada descarga la página se actualiza un momento. Espere a que termine y vuelva a pulsar |
| Falla la generación de PDF o Excel por un paquete | Compruebe que están instalados: `python -m pip show reportlab openpyxl` |
| No aparece una opción del menú, como Dashboard o WACC | Inicie con `ANF_MENU_COMPLETO=1` ([menú completo](#menú-completo)) |
| Un indicador dice «No calculable» | Debajo de la tabla se indica el motivo; suele faltar un estado o un dato, o una cuenta no tiene grupo de análisis |
| «No se guardó ningún dato» al confirmar | Los datos cambiaron o se restauró una copia desde otra pestaña. Revise y repita la operación |
| No se pueden editar los importes de un año | El ejercicio está cerrado. Reábralo en *Modificación de datos › Ejercicio* |
| «No se pudo actualizar la base de datos» | La migración se detuvo sin aplicar cambios. Revise la copia previa en `data/backups/` |

## 16. Información técnica

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

### Variables de entorno

Son opcionales y se definen en la terminal; la aplicación no usa archivo `.env` ni credenciales.

| Variable | Efecto |
|---|---|
| `ANF_MENU_COMPLETO=1` | Muestra las opciones de «Más opciones» |
| `ANF_BASE_VACIA=1` | Si no hay base de trabajo, crea una vacía en vez de copiar la de Alutech |

### Estructura del proyecto

```text
app.py              Punto de entrada: arranque de la base, menú y enrutamiento
requirements.txt    Dependencias con versiones probadas
modules/            Páginas de administración y captura
reports/            Reportes en pantalla y exportación a PDF y Excel
calculations/       Estados, indicadores, DuPont, WACC, origen y aplicación, y comparación
components/         Menú, formato y validación de importes, confirmaciones y transacciones
database/           Modelos, repositorios, migraciones, copias de seguridad y catálogo inicial
fuentes/alutech/    Estados transcritos, con documento, página y denominación original
fuentes/anf/        Referencias, supuestos del WACC y observaciones del trabajo ANF
scripts/            Carga de Alutech e informe de validación
assets/plantillas/  Plantillas Excel de referencia
data/inicial/       Base de partida con Alutech 2021–2025
documentos/         Estados financieros originales de Alutech
tests/              Pruebas automatizadas
.streamlit/         Configuración del servidor
```

### Scripts

Opcionales: la base inicial ya contiene estos datos. Ejecútelos con la aplicación cerrada.

```powershell
# Cargar los estados de Alutech. Opciones: --simular, --bd RUTA.db, --datos ARCHIVO.json
.venv\Scripts\python.exe scripts/cargar_alutech.py

# Generar INFORME_VALIDACION_FINANCIERA.md. Solo lee la base. Opciones: --bd RUTA.db, --salida ARCHIVO.md
.venv\Scripts\python.exe scripts/generar_informe_validacion.py
```

La carga no duplica datos ni sobrescribe importes: si un importe ya existe con otro valor, no guarda nada y muestra
`NO SE CARGÓ NADA` con la causa. No registra la empresa.

## 17. Créditos y contexto académico

Aplicación desarrollada para el trabajo académico de la materia Análisis Financiero, Departamento de Ingeniería y Arquitectura,
Facultad Multidisciplinaria de Occidente, Universidad de El Salvador. La catedrática y los integrantes del equipo figuran en la
portada de `Trabajo de investigación ANF`.

Los estados financieros pertenecen a su emisor, Alutech, S. A. de C. V. Este repositorio tiene fines académicos: sus resultados
no constituyen una opinión de auditoría ni una recomendación financiera.
