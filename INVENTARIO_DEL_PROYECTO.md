# Inventario del proyecto

**Proyecto:** Aplicación de Análisis Financiero (Streamlit + SQLAlchemy + SQLite)
**Fecha del inventario:** 2026-11-01
**Alcance:** todo el código fuente en `C:\Users\estua\Documents\ANF\appfinanciera`, excepto `.venv/`, `__pycache__/` y `.pytest_cache/`.
**Total de código Python:** 4.109 líneas en 35 archivos `.py`.

---

## 1. Árbol de archivos

```
appfinanciera/
├── app.py                         113  Punto de entrada Streamlit: restauración pendiente, init BD, enrutamiento
├── requirements.txt                    Dependencias con rangos de versión
├── README.md                           Documentación de usuario
├── .gitignore                          Excluye .venv, data/*.db, data/backups/
├── streamlit_run.log / _err.log / .pid  Restos de una ejecución previa (09:43). El PID 16320 ya no existe
├── assets/
│   └── plantillas/
│       ├── plantilla_balance_general.xlsx      Plantilla estática de referencia
│       └── plantilla_estado_resultados.xlsx    Plantilla estática de referencia
├── data/
│   └── financiera.db                   BD de trabajo (69.632 bytes): 1 empresa, 1 ejercicio (2021), 19 saldos en 0.00
├── documentos/                         Material didáctico (no contiene cifras de Alutech)
│   ├── Balance general.pptx
│   ├── Estados-Financieros.pptx
│   └── libro adm financ.pdf
├── database/
│   ├── enums.py                   121  Categorías, subcategorías, efecto, estados
│   ├── models.py                  245  Modelos ORM (8 tablas)
│   ├── connection.py               77  Engine, PRAGMA foreign_keys, session_scope
│   ├── repositories.py            424  CRUD y registro del historial
│   └── seed.py                     77  Catálogo estándar (30 cuentas)
├── calculations/
│   ├── balance_sheet.py           106  Subtotales y ecuación contable
│   ├── income_statement.py        144  Subtotales del Estado de Resultados
│   ├── vertical_analysis.py        88  Análisis vertical (balance y resultados)
│   └── dupont.py                  229  DuPont de 3 factores, saldos iniciales e interpretación
├── components/
│   ├── money.py                    33  q2 (ROUND_HALF_UP), formato de importes, % y "veces"
│   ├── navigation.py               73  Menú lateral y selector/creador de ejercicios
│   └── tables.py                   31  Tablas de grupos (HTML con unsafe_allow_html)
├── modules/
│   ├── company.py                  51  Datos de la empresa
│   ├── accounts.py                178  Catálogo: alta, edición y desactivación
│   ├── data_entry.py              187  Captura de Balance, Resultados y saldos iniciales
│   ├── excel_import.py            215  Plantillas, vista previa e importación
│   ├── data_edit.py               125  Edición de importes con data_editor
│   ├── history.py                  49  Historial global
│   ├── dashboard.py                85  Indicadores del último ejercicio y gráfico de evolución
│   └── backup.py                   84  Crear, descargar y restaurar copias
├── reports/
│   ├── balance_report.py           72  Balance en pantalla + descargas
│   ├── income_report.py            70  Estado de Resultados en pantalla + descargas
│   ├── vertical_report.py          97  Análisis vertical en pantalla + Excel
│   ├── dupont_report.py            98  DuPont en pantalla + PDF/Excel
│   ├── pdf_export.py              204  ReportLab: Balance, Resultados, DuPont
│   └── excel_export.py            237  OpenPyXL: Balance, Resultados, Vertical, DuPont
└── tests/
    ├── conftest.py                 26  Fixture con BD temporal sembrada
    ├── test_accounts.py           147  8 pruebas
    ├── test_balance.py             74  6 pruebas
    ├── test_dupont.py              94  5 pruebas
    ├── test_import_export.py      135  4 pruebas
    ├── test_income.py              54  3 pruebas
    └── test_vertical.py            66  4 pruebas
```

## 2. Esquema de base de datos (verificado en `data/financiera.db`)

| Tabla | Clave primaria | Claves foráneas | Restricciones únicas | Filas actuales |
|---|---|---|---|---|
| `company` | id | — | — | 1 |
| `fiscal_period` | id | — | `anio` | 1 (2021) |
| `account` | id | — | `codigo` | 30 |
| `balance_entry` | id | `fiscal_period_id` → CASCADE; `account_id` → RESTRICT | (`fiscal_period_id`, `account_id`) | 19 (todas 0.00) |
| `income_entry` | id | igual que `balance_entry` | (`fiscal_period_id`, `account_id`) | 0 |
| `initial_balance` | id | igual que `balance_entry` | (`fiscal_period_id`, `account_id`) | 0 |
| `statement_status` | id | `fiscal_period_id` → CASCADE | (`fiscal_period_id`, `tipo`) | 1 |
| `change_history` | id | **ninguna** | — | 52 |

- `PRAGMA foreign_keys=ON` se activa en cada conexión (`database/connection.py:29-33`).
- `PRAGMA integrity_check` = `ok`. Modo de journal: `delete`.
- Los importes se declaran `NUMERIC(18,2)`, pero SQLite los almacena como `REAL` (coma flotante binaria; comprobado con `typeof(valor)`).
- No hay sistema de migraciones: el esquema se crea con `Base.metadata.create_all` (`database/connection.py:46`).

## 3. Dependencias

### 3.1 Declaradas e instaladas (.venv, Python 3.12.10)

| Paquete | Rango en requirements.txt | Instalado | Uso |
|---|---|---|---|
| streamlit | >=1.38,<2.0 | 1.66.1 | Interfaz |
| SQLAlchemy | >=2.0,<2.1 | 2.0.55 | ORM |
| pandas | >=2.2,<3.0 | 2.3.3 | Lectura de Excel, tablas |
| numpy | >=1.26,<2.3 | 2.2.6 | Indirecta (pandas) |
| plotly | >=5.24,<6.0 | 5.24.1 | Gráficos |
| openpyxl | >=3.1,<4.0 | 3.1.5 | Plantillas y exportación Excel |
| reportlab | >=4.2,<5.0 | 4.5.1 | Exportación PDF |
| pytest | >=8.3,<9.0 | 8.4.2 | Pruebas |

Observación: el código usa `width="stretch"` en `st.dataframe`/`st.plotly_chart`, un parámetro de versiones recientes de Streamlit. No se verificó la compatibilidad con el mínimo declarado (1.38).

### 3.2 Dependencias internas entre módulos

```
app.py ─► components.navigation ─► database.repositories
       ─► database.connection ─► database.models ─► database.enums
       ─► database.seed ─► database.repositories
       ─► modules.* / reports.*  (import diferido según la página)

calculations.balance_sheet    ─► database.repositories, components.money
calculations.income_statement ─► database.repositories, components.money
calculations.vertical_analysis ─► calculations.balance_sheet, calculations.income_statement
calculations.dupont           ─► calculations.balance_sheet, calculations.income_statement, database.repositories

reports.*_report  ─► calculations.*, components.*, reports.pdf_export / reports.excel_export
reports.pdf_export ─► components.money  (import diferido de calculations.dupont)
modules.data_entry ─► calculations.income_statement, components.navigation, database.repositories
modules.data_edit  ─► calculations.balance_sheet, database.repositories
modules.excel_import ─► database.repositories
modules.dashboard  ─► calculations.*, database.repositories
modules.backup     ─► database.connection (solo constantes DATA_DIR y DB_PATH)
```

No hay importaciones circulares: los 24 módulos de la aplicación se importaron uno por uno sin errores. La capa `calculations/` depende de `database.repositories`, es decir, los cálculos consultan la BD directamente en lugar de recibir datos. Esto dificulta probarlos de forma aislada.

## 4. Función de cada módulo

| Módulo | Responsabilidad | Entradas | Escribe en BD |
|---|---|---|---|
| `app.py` | Restauración pendiente, inicialización, CSS y enrutamiento. Envuelve toda la página en un solo `session_scope()` que hace commit al final | session_state | Sí (commit implícito) |
| `database/enums.py` | Única fuente de reglas de clasificación | — | No |
| `database/models.py` | Modelos ORM | — | — |
| `database/connection.py` | Engine global de proceso y fábrica de sesiones | Ruta de BD | — |
| `database/repositories.py` | CRUD de empresa, ejercicios, cuentas, importes, saldos iniciales, estados e historial | Session | Sí (flush; commit del llamador) |
| `database/seed.py` | Siembra 30 cuentas si el catálogo está vacío | Session | Sí |
| `calculations/balance_sheet.py` | Agrupa por categoría y subcategoría y suma | `fiscal_period_id` | No |
| `calculations/income_statement.py` | Subtotales con reglas de signo fijas por categoría | `fiscal_period_id` | No |
| `calculations/vertical_analysis.py` | % sobre activo total o sobre ingresos netos por cuenta | `fiscal_period_id` | No |
| `calculations/dupont.py` | Saldos iniciales, promedios, factores, ROE e interpretación | `FiscalPeriod` | No |
| `components/money.py` | Redondeo HALF_UP y formato | Decimal | No |
| `components/navigation.py` | Menú y selector de ejercicio (puede crear ejercicios) | Session | Sí |
| `components/tables.py` | Render de grupos | Grupo | No |
| `modules/company.py` | Alta y edición de la empresa | Formulario | Sí |
| `modules/accounts.py` | Catálogo de cuentas | Formulario | Sí |
| `modules/data_entry.py` | Captura de importes por formulario | `number_input` (float) | Sí |
| `modules/excel_import.py` | Importación por archivo | XLSX | Sí (también durante la vista previa; ver hallazgo C-02) |
| `modules/data_edit.py` | Edición de importes existentes | `data_editor` (float) | Sí |
| `modules/history.py` | Consulta del historial | — | No |
| `modules/dashboard.py` | Resumen y evolución | — | No |
| `modules/backup.py` | Copias y restauración | Archivos .db | Sistema de archivos |
| `reports/*_report.py` | Presentación en pantalla y botones de descarga | — | No |
| `reports/pdf_export.py` | PDF de Balance, Resultados y DuPont | Resultados de cálculo | No |
| `reports/excel_export.py` | XLSX de Balance, Resultados, Vertical y DuPont | Resultados de cálculo | No |

## 5. Funcionalidades

### 5.1 Implementadas y verificadas por ejecución

| Funcionalidad | Evidencia |
|---|---|
| Alta de cuentas, prevención de código duplicado y desactivación sin borrado | `tests/test_accounts.py` (aprobadas) |
| Ejercicio fiscal único por año | `uq_fiscal_period_anio`; prueba aprobada |
| FK: no se puede asociar un importe a un ejercicio inexistente | Prueba B04 aprobada |
| Unicidad cuenta-ejercicio | Prueba B05 aprobada |
| Persistencia tras cerrar y reabrir el engine | `test_persistencia_en_sqlite` aprobada |
| Subtotales de Balance y diferencia sin forzar el cuadre | `test_balance.py`, F05 aprobadas |
| Estado de Resultados con todas las categorías | F04 aprobada |
| Identidad DuPont = ROE directo con datos válidos | A05 aprobada |
| Bloqueo de DuPont con ingresos, activo o patrimonio promedio igual a cero | A07, A08, `test_dupont` aprobadas |
| Exportación PDF y Excel generan archivos válidos sin modificar la BD | G03, G04 aprobadas |

### 5.2 Implementadas parcialmente o con defectos comprobados

| Funcionalidad | Limitación (ver AUDITORIA_INTEGRAL.md) |
|---|---|
| Importación Excel con vista previa | La vista previa crea ejercicios; cancelar no revierte; vacíos aceptados como NaN (C-02, A-07, M-01) |
| Catálogo de cuentas | Reclasificación retroactiva de importes históricos (C-03) |
| Historial de modificaciones | No identifica ejercicio ni cuenta; `registro_id` inconsistente; filtro por ejercicio inexistente (A-08) |
| Restauración de copias | Sin validación ni copia previa (C-01) |
| DuPont: saldos iniciales | Ejercicios no consecutivos, ceros y capturas parciales tomados como dato real (A-01, A-02); patrimonio negativo (A-04) |
| Análisis vertical | Sin subtotales, sin líneas de ingresos ni utilidades, sin exportación PDF (M-03) |
| Exportación Excel | Referencias circulares cuando un grupo está vacío (A-06) |
| Estado BORRADOR/REVISADO | Solo informativo: no bloquea la edición (M-05) |

### 5.3 Faltantes

| Funcionalidad | Observación |
|---|---|
| Cierre de ejercicios | `EstadoEjercicio.CERRADO` existe en `database/enums.py:108`, pero ningún módulo lo usa |
| Eliminación de importes capturados | `repositories.delete_entry` existe, pero ninguna pantalla la invoca |
| Eliminación o corrección de ejercicios creados por error | No existe |
| Exportación PDF del análisis vertical | No existe (sí existe en Excel) |
| Indicador de completitud de un estado financiero | No existe (ver M-04) |
| Validación de signo según la naturaleza del saldo | `naturaleza_saldo` es solo informativo (A-05) |
| Validación de integridad de copias de seguridad | No existe |
| Migraciones de esquema | No existe (M-09) |
| Datos de Alutech, S. A. de C. V. 2021–2025 | No están cargados en la BD |
