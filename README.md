# Aplicación de Análisis Financiero

Aplicación web local (Streamlit + SQLite + SQLAlchemy) para administrar la
información financiera de una sola empresa a lo largo de múltiples
ejercicios fiscales, con captura manual o por Excel, reportes financieros
automatizados (Balance General, Estado de Resultados, Análisis Vertical,
Modelo DuPont) y exportación a PDF/Excel.

## 1. Requisitos

- Python 3.11 o superior (desarrollado y probado con 3.12).
- Windows, macOS o Linux.

## 2. Instalación

```bash
# 1. Crear el entorno virtual
python -m venv .venv

# 2. Activar el entorno virtual
#    Windows (PowerShell):
.venv\Scripts\Activate.ps1
#    Windows (cmd):
.venv\Scripts\activate.bat
#    macOS / Linux:
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

## 3. Ejecución

```bash
streamlit run app.py
```

Esto abre el navegador en `http://localhost:8501`. La base de datos SQLite
se crea automáticamente en `data/financiera.db` en el primer arranque, con
un catálogo de cuentas estándar ya sembrado (editable desde el módulo
"Catálogo de cuentas"). La base de datos persiste entre ejecuciones: cerrar
la terminal no borra la información.

**Primer uso:** la aplicación pedirá registrar los datos de la empresa
antes de habilitar el resto de los módulos (menú "Datos de la empresa").

El servidor solo escucha en `localhost` (`.streamlit/config.toml`): la
aplicación no tiene autenticación y no debe ser accesible desde la red.

**Actualización de la base de datos:** al arrancar, la aplicación lleva la
BD a la versión de esquema vigente (`PRAGMA user_version`, ver
`database/migrations.py`). Si hay que migrar una BD con datos, antes crea
y verifica una copia en `data/backups/financiera_pre_migracion_*.db`. Si
algún importe no puede convertirse sin redondear, la migración se detiene
y la BD no cambia.

## 4. Copias de seguridad

Desde el menú "Copias de seguridad":

- **Crear copia de seguridad ahora**: guarda en `data/backups/` una copia
  hecha con la API de respaldo de SQLite y verificada (`integrity_check`
  y conteo de filas).
- **Restaurar**: selecciona una copia existente o sube un archivo `.db`.
  La aplicación valida que sea una SQLite íntegra de esta aplicación y
  muestra su contenido (empresa, ejercicios, registros) antes de pedir la
  confirmación. Al restaurar, guarda primero una copia exacta de la BD
  actual (`financiera_pre_restauracion_*.db`). Si algo falla, la BD actual
  queda igual que antes. Si otra pestaña tiene la BD abierta, la
  restauración se rechaza: cierre las demás pestañas y repita.

También puedes respaldar manualmente copiando el archivo
`data/financiera.db` mientras la aplicación está cerrada.

## 4.1 Captura, ejercicios e historial

- Un campo de importe vacío significa **sin dato** y no se guarda. Un `0`
  escrito explícitamente se guarda como importe cero. Vaciar un campo no
  borra el importe guardado: use "Borrar importe" (Modificación de datos).
- Los importes se guardan como centavos enteros. Se aceptan como máximo dos
  decimales: en la captura manual un tercer decimal se redondea (redondeo
  comercial) con aviso; en la importación Excel se rechaza, salvo el ruido
  binario de Excel (p. ej. 0.30000000000000004), que se redondea con aviso
  en la vista previa.
- La vista previa de la importación no modifica la BD: indica qué
  ejercicios se crearían. Al confirmar se importa todo o nada.
- "Modificación de datos › Ejercicio" permite cerrar un ejercicio, lo que
  bloquea su captura, edición, importación y borrado (también desde la BD
  mediante disparadores), reabrirlo y eliminar ejercicios vacíos.
- Una cuenta con importes no puede cambiar su categoría, subcategoría ni
  efecto. Para reclasificar, cree una cuenta nueva y desactive la anterior.
- El historial registra fecha, operación, tabla, id real del registro,
  ejercicio, cuenta, valores anterior y nuevo y lote de cada guardado o
  importación.

## 4.2 Convención de signos, completitud y DuPont

- **Signos:** ingresos, costos, gastos e impuestos se capturan en positivo
  (los cálculos restan costos y gastos). Activos, pasivos y patrimonio, en
  positivo. Las cuentas correctoras del activo (depreciación acumulada), en
  negativo. Los resultados acumulados o del ejercicio pueden ser negativos.
  Un importe con otro signo se advierte y requiere confirmación; nunca se
  invierte.
- **Completitud:** un estado está INCOMPLETO si una categoría obligatoria
  no tiene ninguna cuenta capturada. Balance: Activo, Pasivo y Patrimonio.
  Resultados: Ingresos, Costo de ventas, Gastos operativos e ISR. Un 0
  escrito cuenta como dato.
- **Conciliación:** se compara el "Resultado del ejercicio" del patrimonio
  con la utilidad neta, y se muestra la diferencia sin corregir nada.
- **DuPont:** el saldo inicial es el Balance del ejercicio inmediatamente
  anterior (completo y cuadrado), o bien saldos manuales completos. Si no
  hay ninguno, el ROE se marca como APROXIMADO e indica la causa. Si el
  patrimonio inicial, final o promedio es ≤ 0, el ROE es NO INTERPRETABLE.
  El ROE usa el patrimonio total.

## 4.3 Estado de los reportes y exportaciones

Cada reporte (pantalla, PDF, Excel y Dashboard) muestra el mismo "Estado del
reporte": DEFINITIVO, o una o varias banderas: INCOMPLETO, DESCUADRADO,
APROXIMADO, NO INTERPRETABLE, SIGNO ATÍPICO y SIN CONCILIAR, con su causa. En
los Excel, la columna "Importe" contiene los valores calculados por la
aplicación, y las columnas "Control" y "Diferencia" contienen fórmulas de
Excel que los recalculan para auditarlos. El análisis vertical incluye
subtotales, totales y utilidades, y se exporta a PDF y a Excel.

## 5. Pruebas automatizadas

```bash
pytest tests/ -v
```

Las pruebas usan bases de datos SQLite temporales y datos sintéticos.
`tests/conftest.py` redirige la ruta de la BD a un archivo temporal y hace
fallar la ejecución si cambia el SHA-256 de `data/financiera.db`.

Estado actual (2026-11-01, tras las fases 1 a 3 del `PLAN_DE_CORRECCION.md`):
**270 aprobadas y 3 fallidas de 273**.
- 30 pruebas originales: todas aprueban. La comparación de T-15 se ajustó, con
  autorización, al redondeo de presentación (B-01).
- 47 pruebas de la auditoría: 44 aprueban. F01 y F03 fallan por diseño: el
  signo no se invierte, se advierte y se pide confirmación. D08 corresponde a
  la fase 4.
- 132 pruebas de la fase 1 y de M-11, 47 de la fase 2 y 17 de la fase 3:
  todas aprueban.

Que una prueba falle significa que el defecto que describe sigue presente.
Detalle en `MATRIZ_DE_PRUEBAS.md`. Las cifras de los reportes todavía no se
han conciliado con los estados publicados de Alutech.

## 6. Plantillas de Excel

Plantillas de ejemplo (con el catálogo estándar ya volcado) en
`assets/plantillas/`. También se pueden descargar actualizadas en
cualquier momento desde "Ingreso de datos › Importación Excel" — esas
siempre reflejan el catálogo de cuentas vigente, mientras que los archivos
en `assets/plantillas/` son una referencia estática.

## 7. Estructura del proyecto

```
app.py                  Punto de entrada Streamlit (routing + sidebar)
database/
  models.py             Modelos SQLAlchemy (empresa, ejercicios, cuentas,
                         importes, saldos iniciales, historial, estado)
  enums.py               Categorías/subcategorías y reglas de clasificación
  connection.py          Engine, sesiones, respaldo/restauración
  repositories.py        Acceso a datos (CRUD + historial de cambios)
  seed.py                Catálogo de cuentas estándar inicial
modules/
  company.py             Datos de la empresa
  accounts.py             Catálogo de cuentas
  data_entry.py            Captura de Balance, Resultados y Saldos iniciales
  excel_import.py           Importación desde Excel con vista previa
  data_edit.py                Modificación de datos ya capturados
  history.py                   Historial de cambios global
  dashboard.py                  Panel principal
  backup.py                      Copias de seguridad
calculations/
  balance_sheet.py        Subtotales y ecuación contable del Balance
  income_statement.py      Subtotales del Estado de Resultados
  vertical_analysis.py      Análisis vertical (balance y resultados)
  dupont.py                  Modelo DuPont de tres factores
reports/
  balance_report.py, income_report.py, vertical_report.py,
  dupont_report.py          Reportes en pantalla (tablas + gráficos)
  pdf_export.py, excel_export.py   Exportación a PDF (ReportLab) y Excel
                                    (OpenPyXL)
components/
  navigation.py, tables.py, money.py   Utilidades de interfaz compartidas
tests/                   Suite Pytest (18 casos + regresiones)
data/                    Base de datos SQLite y copias de seguridad
                         (fuera de control de versiones)
assets/plantillas/       Plantillas Excel de referencia
```

Principio de diseño clave: los subtotales e indicadores (utilidad bruta,
totales de balance, ROE, análisis vertical, etc.) **nunca se almacenan**
en la base de datos — se calculan en `calculations/` a partir de los
importes capturados vigentes, para evitar datos derivados desactualizados.

## 8. Decisiones de diseño relevantes

- **Precisión monetaria**: todos los cálculos usan `Decimal`, nunca
  `float`, para evitar errores de redondeo.
- **"Otros ingresos/gastos operativos"**: se modelan como subcategoría
  `OTROS_OPERATIVOS` dentro de "Gastos operativos", con un campo `efecto`
  (INGRESO/GASTO) que determina el signo en la Utilidad Operativa.
- **Saldos iniciales del modelo DuPont**: se encadenan automáticamente
  desde el Balance final del ejercicio fiscal anterior cuando existe; solo
  se usan saldos capturados manualmente (o una aproximación con el saldo
  final, claramente señalada) cuando no hay ejercicio anterior registrado.
- **Ecuación contable**: el Balance General y el Estado de Resultados se
  capturan de forma independiente; el reporte de Balance siempre valida
  `Activo = Pasivo + Patrimonio` y muestra la diferencia si no cuadra, sin
  forzar ni sobrescribir ningún valor automáticamente.
