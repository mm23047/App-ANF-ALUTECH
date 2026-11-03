# Aplicación de Análisis Financiero

Aplicación web local (Streamlit + SQLite + SQLAlchemy) para administrar la
información financiera de una sola empresa a lo largo de múltiples
ejercicios fiscales, con captura manual o por Excel, reportes financieros
automatizados (Balance General, Estado de Resultados, Análisis Horizontal y
Vertical, indicadores financieros, Modelo DuPont, WACC, origen y aplicación
de fondos) y exportación a PDF/Excel. Contiene los estados financieros de
Alutech – División Acero 2021–2025 y su comparación con el «Trabajo de
investigación ANF» (ver 3.1).

## 1. Requisitos

- Python 3.12 (probado con 3.12.10 en Windows 11).
- `requirements.txt` fija las versiones exactas con las que pasa la suite
  de pruebas; no se han probado otras versiones ni otros sistemas.

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
BD a la versión de esquema vigente (4; `PRAGMA user_version`, ver
`database/migrations.py`). Si hay que migrar una BD con datos, antes crea
y verifica una copia en `data/backups/financiera_pre_migracion_*.db`. Si
algún importe no puede convertirse sin redondear, la migración se detiene
y la BD no cambia.

## 3.1 Datos de Alutech 2021–2025 (carga, uso y mantenimiento)

La aplicación contiene los estados financieros de **Alutech, S. A. de C. V. y subsidiarias – División Acero** de 2021 a
2025, tomados de la carpeta `documentos/` (certificaciones de estados combinados 2021–2023 y estados consolidados
2024–2025). Las cifras transcritas, con el documento, la página y la denominación original de cada importe, están en
`fuentes/alutech/estados_financieros_2021_2025.json`.

**Cargar (o volver a cargar) los datos**, con la aplicación cerrada:

```bash
python scripts/cargar_alutech.py --simular   # ensaya sobre una copia temporal; no modifica la BD
python scripts/cargar_alutech.py             # carga en data/financiera.db
```

La carga crea primero una copia verificada (`data/backups/financiera_pre_carga_alutech_*.db`), escribe todo en una sola
transacción y, antes de confirmar, compara los 61 totales impresos en los documentos con los que calcula la aplicación:
si uno no coincide, o si un importe ya existe con otro valor, no se guarda nada. Es idempotente: repetirla no duplica ni
modifica datos. Nunca borra ni sobrescribe importes existentes.

**Páginas del análisis 2021–2025:**

- *Datos originales › Trazabilidad y controles*: fuente de cada importe, totales impresos vs calculados, datos
  complementarios y mapeo cuenta → grupo de análisis → indicadores.
- *Reportes › Análisis Horizontal 2021–2025* (rubros del trabajo, grupos de análisis o cuentas), *Análisis Vertical
  comparativo*, *Indicadores financieros* (liquidez y capital de trabajo, actividad, endeudamiento, rentabilidad, DuPont
  al cierre, razones de mercado), *WACC*, *Origen y aplicación de fondos* e *Informe integral* (todo en un Excel o PDF).
- *Validación › Comparación con el trabajo ANF*: resultado calculado vs. valor publicado en el «Trabajo de investigación
  ANF», diferencia, estado y causa documentada.
- El *Dashboard* muestra además el capital de trabajo, la liquidez y la rentabilidad de los cinco ejercicios.

**Mantenimiento:**

- Corregir un dato original: edítelo en *Modificación de datos* (queda en el historial). El control de trazabilidad
  señalará que el importe vigente ya no es el del documento. Si la corrección es de transcripción, corrija también el
  JSON de `fuentes/alutech/`.
- Equivalencias entre ejercicios: cada cuenta tiene un *grupo de análisis* configurable en *Catálogo de cuentas*
  (`MAPEO_FINANCIERO_ALUTECH.md`).
- Supuestos del WACC (tasas e ISR, tomados del trabajo y no verificables con los documentos):
  `fuentes/anf/supuestos_wacc.json`.
- Regenerar el informe de validación: `python scripts/generar_informe_validacion.py` (solo lee la BD).

Documentos de control: `INVESTIGACION_DOCUMENTAL_ANF.md`, `MAPEO_FINANCIERO_ALUTECH.md`, `MATRIZ_ADAPTACION.md`,
`INFORME_VALIDACION_FINANCIERA.md` y `REGISTRO_DE_CAMBIOS.md`.

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
- **Confirmación de operaciones masivas:** "Guardar" en la captura (Balance,
  Resultados, saldos iniciales) y "Guardar cambios" en Modificación de datos
  no escriben nada: muestran el alcance ("Se modificarán N valor(es) … en el
  ejercicio X") con la cuenta, el valor actual y el nuevo. Solo "Confirmar y
  guardar" escribe, una sola vez y en una transacción, y únicamente si esos
  valores no cambiaron mientras tanto. "Cancelar", recargar la página o
  cambiar de página o de ejercicio descartan la operación sin modificar nada.
  Si otra pestaña restaura una copia de seguridad (o la base se sustituye)
  después de preparar la confirmación, "Confirmar y guardar" no escribe nada
  y pide revisar los datos y preparar la operación de nuevo.
- La vista previa de la importación no modifica la BD: indica qué
  ejercicios se crearían y el alcance (importes nuevos, sobrescritos y sin
  cambios). Al confirmar se importa todo o nada, y solo si la vista previa es
  la que se tenía en pantalla: un segundo clic no repite la importación.
- Importación de códigos de cuenta: un código numérico entero (Excel puede
  leer 1001 como 1001.0) se normaliza a "1001". Se reportan como
  `CODIGO_AMBIGUO`, y no se importan, los códigos con decimales, valores
  lógicos, fechas y los que pudieron perder ceros a la izquierda. Los
  códigos escritos como texto se usan tal cual.
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

Los textos escritos por el usuario (nombre de la empresa, moneda, nombres
de cuenta) se muestran siempre como texto literal: en pantalla no se
interpreta HTML ni Markdown, en el PDF no se interpretan etiquetas y en el
Excel nunca se convierten en fórmulas, aunque empiecen con `=`, `+`, `-` o
`@`. Las únicas fórmulas de los Excel son las de control.

## 5. Pruebas automatizadas

```bash
pytest tests/ -v
```

Las pruebas usan bases de datos SQLite temporales y datos sintéticos.
`tests/conftest.py` redirige la ruta de la BD a un archivo temporal y hace
fallar la ejecución si cambia el SHA-256 de `data/financiera.db`.

Estado actual (2026-11-02, fases 0 a 7 del `PLAN_DE_CORRECCION.md`,
adaptación Alutech 2021–2025 y revisión final): **515 aprobadas de 515**.

| Conjunto | Pruebas | Aprobadas |
|---|---|---|
| Originales | 30 | 30 (la comparación de T-15 se ajustó, con autorización, al redondeo de presentación) |
| Auditoría (`test_auditoria.py`) | 47 | 47 (F01 y F03 actualizadas a la convención de signos aprobada) |
| Fase 1 y M-11 (incluye las 24 páginas con `AppTest`) | 140 | 140 |
| Fase 2 | 47 | 47 |
| Fase 3 | 17 | 17 |
| Fase 4 | 77 | 77 |
| B-10 (Excel sin fórmulas en los textos) | 34 | 34 |
| Fase 5: caso controlado de 3 ejercicios (`test_fase5_controlado.py`) | 18 | 18 |
| Fase 5: integración del flujo completo (`test_fase5_integracion.py`) | 16 | 16 |
| Fase 7: correcciones operativas O-1 a O-5 (`test_fase7.py`) | 38 | 38 |
| Adaptación Alutech 2021–2025 (`test_alutech.py`) | 51 | 51 |

F01 y F03 esperaban que la aplicación invirtiera en silencio el signo de una
depreciación capturada en positivo o de un costo negativo. La convención
aprobada es la contraria: el signo nunca se invierte; el importe se muestra
tal como se capturó, con un aviso, guardarlo requiere confirmación y el
reporte queda marcado SIGNO ATÍPICO. En la revisión final (2026-11-02) se
actualizaron para exigir ese comportamiento (la propia docstring de F01 ya
admitía «advertida») y que la captura con el signo correcto dé 700 y 400; no
se eliminó ninguna prueba.

El caso controlado (`tests/fixtures/caso_controlado.json`) tiene valores
calculados a mano para el Balance, el Estado de Resultados, el análisis
vertical y el DuPont de 2021–2023: la aplicación coincide al centavo y en
0,00 puntos porcentuales. Son datos sintéticos.

**Adaptación Alutech 2021–2025 (`tests/test_alutech.py`, 51 pruebas):** carga
de los datos originales (61 totales impresos, idempotencia, no
sobrescritura, simulación, signos, conservación de los 19 importes en cero
de 2021), indicadores y WACC verificados a mano con las cifras de los
documentos, origen y aplicación de fondos, comparación completa con el
trabajo ANF (736 valores: 672 coinciden, 6 por redondeo, 43 diferencias
con causa y categoría documentadas, 15 no aplican), actualización de los
indicadores al cambiar el mapeo, exportaciones, migración v3→v4 y las 24
páginas con los datos cargados. Los estados de 2020 no están en los
documentos: 2021 no tiene saldos promedio (el DuPont con promedios lo marca
APROXIMADO). Detalle en `INFORME_VALIDACION_FINANCIERA.md`.

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
                         importes, saldos iniciales, historial, estado,
                         fuente de cada importe, totales impresos)
  enums.py               Categorías/subcategorías y reglas de clasificación
  connection.py          Engine y sesiones (render_scope sin commit implícito)
  migrations.py          Versión de esquema (PRAGMA user_version) y migraciones
  backup_utils.py        Copia verificada y restauración segura
  repositories.py        Acceso a datos (CRUD + historial de cambios)
  seed.py                Catálogo de cuentas estándar inicial
modules/
  company.py             Datos de la empresa
  accounts.py             Catálogo de cuentas
  data_entry.py            Captura de Balance, Resultados y Saldos iniciales
  excel_import.py           Importación desde Excel con vista previa
  data_edit.py                Modificación de datos ya capturados
  history.py                   Historial de cambios global
  dashboard.py                  Panel principal (incluye 2021–2025)
  backup.py                      Copias de seguridad
  trazabilidad.py                Fuente de cada importe y controles de carga
calculations/
  balance_sheet.py        Subtotales y ecuación contable del Balance
  income_statement.py      Subtotales del Estado de Resultados
  vertical_analysis.py      Análisis vertical (balance y resultados)
  dupont.py                  Modelo DuPont de tres factores
  validation.py              Convención de signos (avisos, nunca invierte)
  controls.py                Conciliación resultado del ejercicio / utilidad neta
  banderas.py                Estado del reporte (DEFINITIVO, INCOMPLETO, ...)
  rubros.py                  Grupos de análisis, rubros y datos por ejercicio
  indicadores.py             Indicadores del trabajo ANF (fórmula, unidad, ...)
  comparativo.py             Análisis horizontal y vertical de varios ejercicios
  wacc.py, fuentes_usos.py   WACC y origen y aplicación de fondos
  controles_carga.py         Totales impresos vs calculados; vigencia de fuentes
  comparacion_anf.py         Comparación con los resultados del trabajo ANF
reports/
  balance_report.py, income_report.py, vertical_report.py,
  dupont_report.py          Reportes en pantalla (tablas + gráficos)
  pdf_export.py, excel_export.py   Exportación a PDF (ReportLab) y Excel
                                    (OpenPyXL)
  secciones.py, exportar_secciones.py, analisis_alutech.py,
  informe_integral.py       Reportes 2021–2025 (pantalla, Excel y PDF)
fuentes/
  alutech/                 Datos originales transcritos (con su fuente)
  anf/                     Referencias, supuestos y observaciones del trabajo ANF
scripts/
  cargar_alutech.py        Carga reproducible de los datos originales
  generar_informe_validacion.py  INFORME_VALIDACION_FINANCIERA.md
components/
  navigation.py, tables.py, avisos.py   Utilidades de interfaz compartidas
  money.py               Validación y formato de importes y años
  transacciones.py       Escrituras explícitas (lote, commit, rollback)
  confirmacion.py        Confirmación de operaciones masivas
  texto.py               Texto literal en elementos Markdown
  celdas_excel.py        Celdas XLSX: texto literal o fórmula de control
tests/                   Suite Pytest: 30 originales, 47 de la auditoría y
                         las de cada fase (515 en total)
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
  desde el Balance final del ejercicio inmediatamente anterior, si está
  completo, cuadra y tiene activo positivo; si no, se usan saldos capturados
  manualmente completos, y si tampoco los hay, una aproximación con el saldo
  final, señalada como APROXIMADO con su causa (ver 4.2).
- **Ecuación contable**: el Balance General y el Estado de Resultados se
  capturan de forma independiente; el reporte de Balance siempre valida
  `Activo = Pasivo + Patrimonio` y muestra la diferencia si no cuadra, sin
  forzar ni sobrescribir ningún valor automáticamente.
