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

## 4. Copias de seguridad

Desde el menú "Copias de seguridad":

- **Crear copia de seguridad ahora**: guarda una copia con marca de tiempo
  en `data/backups/`, descargable desde la misma pantalla.
- **Restaurar**: selecciona una copia existente o sube un archivo `.db`,
  confirma la advertencia (la restauración sobrescribe todos los datos
  actuales) y la aplicación se reinicia con esos datos.

También puedes respaldar manualmente copiando el archivo
`data/financiera.db` mientras la aplicación está cerrada.

## 5. Pruebas automatizadas

```bash
pytest tests/ -v
```

Las pruebas usan bases de datos SQLite temporales y datos sintéticos
(nunca tocan `data/financiera.db`). Cubren los 18 casos requeridos:
registro/modificación de cuentas, registro de ejercicios, persistencia,
cálculo de activos/pasivos/patrimonio, validación de la ecuación contable,
cálculo de utilidad neta, análisis vertical (balance y resultados), margen
neto, rotación de activos, multiplicador del capital, ROE DuPont y su
coincidencia con el ROE directo, importación de Excel y exportación a
PDF/Excel.

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
