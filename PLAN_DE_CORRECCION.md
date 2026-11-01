# Plan de corrección

**Base:** `AUDITORIA_INTEGRAL.md` (2026-11-01). Los identificadores (C-, A-, M-, B-) remiten a los hallazgos de ese documento.
**Estado:** Fase 0 completada (2026-11-01). Fases 1–5 pendientes de autorización.

## Principios de orden

1. Se corrige primero lo que **destruye o altera datos** y después lo que los **interpreta**: un cálculo correcto sobre datos dañados no sirve.
2. Los cambios de **esquema** se agrupan en un solo paso con migración (fase 1.1), para no migrar la BD varias veces.
3. Se crea una sola función de **validación de importes** (fase 1.2), que reutilizan la captura, la importación y la edición, en lugar de corregir cada pantalla por separado.
4. Los **cálculos** se corrigen antes que los **reportes**, porque los reportes solo presentan lo que devuelven los cálculos.
5. Cada corrección se cierra con su prueba de aceptación. Las 47 pruebas de verificación de la auditoría se incorporan al proyecto en la fase 0 y deben pasar de FALLIDO a APROBADO.

## Resumen de fases

| Fase | Contenido | Hallazgos | Prioridad | Depende de |
|---|---|---|---|---|
| 0 | Preparación: copia de la BD, incorporar pruebas de auditoría | — | Obligatoria | — |
| 1 | Integridad y protección de datos | C-01, C-02, C-03, A-03, A-07, A-08, M-01, M-02, M-05, M-06, M-09, M-10 | Crítica | 0 |
| 2 | Exactitud financiera | A-01, A-02, A-04, A-05, M-04, M-07, B-01, B-02, B-08 | Alta | 1.1, 1.2 |
| 3 | Reportes y exportaciones | A-06, M-03, M-08, B-03 | Alta / Media | 2 |
| 4 | Interfaz y funcionamiento | B-04, B-05, B-06, B-07, mensajes y confirmaciones | Media / Baja | 1–3 |
| 5 | Pruebas y validación final con datos de Alutech | B-09 + conciliación | Obligatoria | 1–4 |

---

## FASE 0. Preparación

| Paso | Acción |
|---|---|
| 0.1 | Copiar `data/financiera.db` a un lugar seguro y registrar su SHA-256 (`f026863d…630a82d` al 2026-11-01) |
| 0.2 | Inicializar Git en el proyecto (no es un repositorio): permite revisar cada fase como un diff y revertirla |
| 0.3 | Copiar `test_auditoria.py` (scratchpad de la auditoría) a `tests/test_auditoria.py` |
| 0.4 | Agregar `.streamlit/config.toml` con `server.address = "localhost"` (M-10). No toca código |

**Aceptación:** `pytest tests/` muestra 30 + 17 aprobadas y 30 fallidas (línea base reproducible).

**Estado: COMPLETADA (2026-11-01).**

| Paso | Resultado | Evidencia |
|---|---|---|
| 0.1 | Copia byte a byte en `C:\Users\estua\Documents\ANF\respaldos_appfinanciera\financiera_ORIGINAL_fase0_20261101.db` (fuera del proyecto, solo lectura) | SHA-256 de original y copia: `f026863d00f841c042c996e0ccb12a1317992ede97d2e544f4cba5955630a82d`; `cmp` sin diferencias; `PRAGMA integrity_check` de la copia = `ok` |
| 0.2 | Repositorio Git creado (rama `main` = línea base auditada; correcciones en la rama `correcciones-auditoria`). Se excluyen `data/*.db`, `documentos/` y `streamlit_run.*` | Commit `2913c49` |
| 0.3 | `tests/test_auditoria.py` incorporado. Solo cambió la cabecera (ruta relativa); los 47 cuerpos de prueba son los originales. `tests/conftest.py` redirige `DB_PATH` a un archivo temporal en cada prueba y falla si cambia el hash de `data/financiera.db` | SHA-256 del archivo original: `d9cb83a8…c018266c` |
| 0.4 | `.streamlit/config.toml` con `server.address = "localhost"` | Prueba con una app mínima: escucha en `127.0.0.1:8599`; HTTP 200 por localhost; conexión por la IP de red rechazada |
| Línea base | `pytest tests/` → **47 aprobadas, 30 fallidas** (las mismas 30 IDs de `MATRIZ_DE_PRUEBAS.md`) | Hash de la BD igual antes y después |

---

## FASE 1. Integridad y protección de datos

### 1.1 Esquema y migraciones (M-09, A-08, M-05)
- **Archivos:** `database/models.py`, `database/connection.py`, un nuevo `database/migrations.py` (o Alembic).
- **Cambios:**
  - Control de versión del esquema con `PRAGMA user_version` y migraciones idempotentes.
  - `change_history`: agregar las columnas `fiscal_period_id`, `account_id` y `lote_id` (nullable).
  - Usar `fiscal_period.estado` (ABIERTO/CERRADO), ya existente, para el cierre de ejercicios.
  - Opcional, según la decisión de 1.4: crear la tabla `account_classification` (vigencias).
  - Opcional: guardar los importes como centavos enteros (M-02). Si se adopta, la migración convierte los REAL existentes con `ROUND(valor*100)`.
- **Riesgos:** migrar la BD real. Se mitiga con la copia de 0.1 y una prueba de migración sobre esa copia.
- **Aceptación:** al abrir la BD actual, se migra sin pérdida (mismas filas, mismos importes); `user_version` queda actualizado; volver a abrir no repite la migración.

### 1.2 Validación única de importes y períodos (A-07, M-01, M-02, B-08)
- **Archivos:** `components/money.py` (nuevas `parse_importe` y `parse_anio`), `modules/data_entry.py`, `modules/data_edit.py`, `modules/excel_import.py`.
- **Cambios:**
  - `parse_importe` rechaza vacío, NaN, ±inf, más de 2 decimales (o cuantiza HALF_UP con aviso) y valores fuera de `NUMERIC(18,2)`.
  - `parse_anio` exige un entero exacto dentro del rango configurado.
  - Nuevos estados en la importación: `VALOR_VACIO` y `PERIODO_FUERA_DE_RANGO`.
- **Depende de:** nada (puede ir en paralelo con 1.1).
- **Aceptación:** D03, D04, D05, D06, D07, E03 e I02 aprueban.

### 1.3 Transacciones y vista previa sin efectos (C-02, M-06)
- **Archivos:** `app.py`, `modules/excel_import.py`, `components/navigation.py`.
- **Cambios:**
  - `app.py`: la sesión de render no hace commit implícito (rollback al final o sesión de solo lectura). Cada acción de guardado abre su propia transacción explícita con try/except y un mensaje legible.
  - `excel_import.py`: la vista previa usa `get_fiscal_period` (lectura) y marca "se creará el ejercicio N"; `get_or_create_fiscal_period` solo se llama tras confirmar; una sola transacción con rollback total si falla una fila.
  - Revisar todos los `session.commit()` dispersos en módulos (`navigation.py:58`, `data_entry.py:72,104,185`, `accounts.py`, `company.py`, `data_edit.py`) para que sigan funcionando con el nuevo modelo.
- **Riesgos:** **es el cambio más transversal.** Si una pantalla dependía del commit implícito, dejará de guardar. Se mitiga con una revisión pantalla por pantalla y pruebas I01, D10 y D11.
- **Aceptación:** D01 y D02 aprueban; D10, D11 y todas las pruebas originales siguen aprobando.

### 1.4 Protección del catálogo histórico (C-03)
- **Archivos:** `database/repositories.py` (`update_account`), `modules/accounts.py`, opcionalmente `calculations/*` si se elige el versionado.
- **Decisión requerida del usuario:**
  - (a) **Bloqueo simple (recomendado para el alcance académico):** prohibir cambiar `categoria_principal`, `subcategoria` y `efecto` si `account_has_movements`. Para reclasificar, se crea una cuenta nueva y se desactiva la anterior.
  - (b) **Clasificación versionada:** tabla `account_classification(account_id, desde_anio, …)`; los cálculos usan la clasificación vigente para el año del ejercicio. Permite reexpresar.
- **Depende de:** 1.1 si se elige (b).
- **Aceptación:** B01, B02 y B03 aprueban; cambiar el nombre o el orden de presentación sigue permitido.

### 1.5 Captura sin ceros implícitos y borrado controlado (A-03, M-05)
- **Archivos:** `modules/data_entry.py`, `modules/data_edit.py`, `components/navigation.py`, `database/repositories.py`.
- **Cambios:**
  - Campos vacíos por defecto, usando `st.number_input(value=None)` o `st.text_input` + `parse_importe`. Se guardan solo los valores informados y se ofrece "Borrar valor" (usar `delete_entry`, con historial).
  - Cierre y reapertura de ejercicios: con CERRADO se bloquean la captura, edición e importación de ese año.
  - Borrado de ejercicios **vacíos** (sin importes).
- **Depende de:** 1.2 y 1.3.
- **Riesgos:** la BD real ya tiene 19 ceros en 2021. Hay que decidir si se eliminan (son ceros de un guardado vacío) o se conservan.
- **Aceptación:** I01 aprueba; nuevas pruebas: "editar un ejercicio cerrado es rechazado" y "borrar un ejercicio vacío" funciona.

### 1.6 Historial completo (A-08)
- **Archivos:** `database/repositories.py` (`log_change`, `upsert_entry`, `upsert_initial_balance`, `delete_entry`), `modules/history.py`, `modules/data_edit.py`.
- **Cambios:**
  - Registrar siempre el id real del registro, el `fiscal_period_id`, el `account_id` y el `lote_id` (un guardado o una importación).
  - La pestaña de `data_edit` filtra por el ejercicio seleccionado.
  - `history.py` muestra año, código y nombre de la cuenta, con filtros por ejercicio y cuenta.
- **Depende de:** 1.1 y 1.3.
- **Aceptación:** C01 aprueba; el historial de 2022 no muestra registros de 2021.

### 1.7 Copias de seguridad y restauración seguras (C-01, M-09 b)
- **Archivos:** `modules/backup.py`, `app.py:16-25`, nuevo `database/backup_utils.py`.
- **Cambios:**
  - Crear la copia con `sqlite3.Connection.backup` + `integrity_check`.
  - La restauración valida en un archivo temporal: encabezado, `integrity_check`, tablas y columnas, una fila en `company` y `user_version` compatible (o migrable).
  - Antes de restaurar, copia automática `financiera_pre_restauracion_<ts>.db`.
  - Reemplazo atómico con try/except y rollback a la copia previa.
  - Mostrar un resumen del contenido del archivo antes de confirmar.
- **Depende de:** 1.1 (versión de esquema).
- **Riesgos:** bloqueo de archivo en Windows con otras pestañas abiertas. Hay que liberar el engine y reintentar, o pedir que se cierren las demás pestañas.
- **Aceptación:** H01 y H02 aprueban; restaurar una copia válida funciona y deja la copia previa; restaurar un archivo inválido muestra un error y deja la BD intacta (mismo hash).

---

## FASE 2. Exactitud financiera

### 2.1 Saldos iniciales DuPont (A-01, A-02)
- **Archivos:** `database/repositories.py` (nueva `get_period_by_year(anio-1)`; mantener o eliminar `get_previous_period`), `calculations/dupont.py`, `modules/data_entry.py:151-159` (aviso coherente).
- **Regla nueva:**
  1. Usar el balance de `anio-1` si existe y es **completo** (activo > 0, patrimonio capturado y cuadra; usa la noción de completitud de 2.3).
  2. Si no, usar los saldos iniciales manuales si son completos (activo y patrimonio).
  3. Si no, usar la aproximación con el saldo final, con `aproximado=True` y la causa concreta en `fuente` (por ejemplo, "no existe el ejercicio 2022" o "el balance de 2022 está incompleto").
- **Depende de:** 1.5 (no más ceros implícitos) y 2.3.
- **Aceptación:** A01, A03 y A04 aprueban; `test_saldos_iniciales_se_encadenan_entre_ejercicios` sigue aprobando.

### 2.2 Patrimonio negativo y casos especiales (A-04, B-02)
- **Archivos:** `calculations/dupont.py`, `reports/dupont_report.py`, `reports/pdf_export.py`.
- **Cambios:**
  - Nuevo estado `interpretable: bool` y lista `advertencias`.
  - Si el patrimonio inicial, final o promedio es ≤ 0, el ROE se muestra con la advertencia "no interpretable" y se omite la interpretación de los factores.
  - Sustituir el control tautológico por controles útiles (balance cuadrado en ambos años, completitud).
- **Aceptación:** A02 aprueba; A05, A07, A08 y A09 siguen aprobando.

### 2.3 Completitud y ausencia de datos (M-04)
- **Archivos:** `calculations/balance_sheet.py`, `calculations/income_statement.py`, `calculations/vertical_analysis.py`.
- **Cambios:** el resultado incluye `cuentas_sin_dato` (cuentas activas sin registro) y `completo`. Los grupos distinguen "sin dato" de 0.
- **Aceptación:** F08 aprueba.

### 2.4 Signos y cuentas correctoras (A-05)
- **Archivos:** `database/enums.py` (reglas de signo esperadas por categoría y naturaleza), `components/money.py` o un nuevo `calculations/validation.py`, `modules/data_entry.py`, `modules/excel_import.py`, `modules/data_edit.py`, plantillas Excel.
- **Decisión requerida:** ¿la convención es "capturar como en el estado publicado" (los costos entre paréntesis son negativos) o "capturar en valor absoluto" (la convención actual)? Se recomienda mantener la actual y **validarla**:
  - Cuenta ACREEDORA dentro de ACTIVO → debe ser ≤ 0.
  - COSTOS, GASTOS, GASTOS_FINANCIEROS e IMPUESTOS → deben ser ≥ 0 (un ISR negativo, es decir un beneficio fiscal, se permite con confirmación).
  - INGRESOS → debe ser ≥ 0.
  - La violación produce una advertencia que requiere confirmación (no un rechazo silencioso).
- **Aceptación:** F01 y F03 aprueban (advertencia o rechazo); F02, F04 y F05 siguen aprobando.

### 2.5 Conciliación entre estados (M-07)
- **Archivos:** `calculations/balance_sheet.py` o un nuevo `calculations/controls.py`, `reports/balance_report.py`.
- **Cambio:** control "Resultado del ejercicio (patrimonio) frente a la utilidad neta del ER" con la diferencia mostrada.
- **Aceptación:** prueba nueva con una diferencia conocida.

### 2.6 Precisión y redondeo (M-02, B-01, B-08)
- **Archivos:** `calculations/dupont.py`, `components/money.py`, `modules/data_entry.py`, `modules/data_edit.py`.
- **Cambios:**
  - Promedios y factores sin redondear en el resultado; `q2` solo al formatear.
  - Mostrar los factores con 4 decimales o con una nota de redondeo.
  - Sustituir `round(float)` por `parse_importe` (de 1.2).
- **Aceptación:** A06 y E03 aprueban; A05 sigue aprobando.

---

## FASE 3. Reportes y exportaciones

### 3.1 Excel sin referencias circulares (A-06, B-03)
- **Archivo:** `reports/excel_export.py`.
- **Cambios:**
  - `_escribir_grupo` devuelve `None` para grupos vacíos y los totales excluyen esos `None`.
  - Escribir el valor calculado por `calculations/` en cada subtotal o total y la fórmula en una columna de "control" (o fórmula con valor en caché).
  - La base del vertical como número.
  - Bandera "APROXIMADO" o "INCOMPLETO" en una celda propia.
- **Depende de:** 2.2 y 2.3 (banderas).
- **Aceptación:** G01 y G02 aprueban; una prueba nueva recalcula con LibreOffice headless (si está disponible) y compara con `compute_*` al centavo.

### 3.2 Análisis vertical completo (M-03)
- **Archivos:** `calculations/vertical_analysis.py`, `reports/vertical_report.py`, `reports/pdf_export.py` (nuevo `export_vertical_pdf`), `reports/excel_export.py`.
- **Cambios:**
  - Balance: filas de AC, ANC, total activo (100%), PC, PNC, total pasivo, patrimonio y total P+P.
  - Resultados: ingresos (100%), utilidad bruta, operativa, antes de impuestos y neta, con su %.
  - Indicar que los costos y gastos restan.
- **Aceptación:** F06 y F07 aprueban; la suma de los % de AC + ANC = 100,00 ± 0,01.

### 3.3 Advertencias consistentes en todos los formatos (M-04, M-08)
- **Archivos:** `modules/dashboard.py`, todos los `reports/*`.
- **Cambio:** las mismas banderas (INCOMPLETO, APROXIMADO, NO INTERPRETABLE, DESCUADRADO) en pantalla, PDF, Excel y Dashboard.
- **Aceptación:** inspección de los cuatro formatos con un ejercicio aproximado e incompleto.

---

## FASE 4. Interfaz y funcionamiento

| Paso | Hallazgo | Archivos | Cambio | Aceptación |
|---|---|---|---|---|
| 4.1 | — | `modules/data_entry.py`, plantillas | Instrucciones de signo visibles en cada grupo; ayuda en las cuentas correctoras | Revisión de pantalla |
| 4.2 | M-10 | `data_entry.py`, `data_edit.py` | Resumen de cambios ("se modificarán N valores en el ejercicio X") y confirmación | Revisión de pantalla |
| 4.3 | — | todos los módulos con commit | Errores técnicos sustituidos por mensajes comprensibles | D04, I02 sin trazas |
| 4.4 | B-04 | `components/tables.py` | Escapar HTML o usar componentes nativos | Moneda `<b>x</b>` se muestra como texto |
| 4.5 | B-06 | `excel_import.py` | Normalizar códigos numéricos | D08 aprueba |
| 4.6 | B-05 | `requirements.txt` | Fijar las versiones probadas | `pip install -r` en un entorno limpio + pytest |
| 4.7 | B-07 | Datos (no código) | El usuario corrige los datos de la empresa | Encabezados correctos |
| 4.8 | — | `components/navigation.py` | Eliminar el duplicado "Configuración" o darle un contenido propio | — |

---

## FASE 5. Pruebas y validación final

| Paso | Acción | Aceptación |
|---|---|---|
| 5.1 | Unitarias: las 47 pruebas de auditoría + las 30 originales en `tests/` | 77/77 aprobadas |
| 5.2 | Integración: flujo completo (empresa → catálogo → importar 2020–2025 → reportes → exportar → respaldo → restaurar) sobre una BD temporal | Sin excepciones; hash de BD restaurada = hash de la copia |
| 5.3 | Regresión: ejecutar la suite completa después de cada fase | Ninguna prueba previa pasa a fallida |
| 5.4 | **Datos financieros controlados:** un caso sintético con resultados calculados a mano (Balance, ER, vertical y DuPont de 3 años consecutivos) en un archivo de valores esperados | Diferencia 0,00 en importes y ≤ 0,01 pp en porcentajes |
| 5.5 | **Conciliación con Alutech:** cargar los estados 2021–2025 (y 2020 para el saldo inicial) y comparar totales, utilidades y ROE contra los estados publicados y un cálculo independiente en hoja de cálculo | Diferencias documentadas y explicadas |
| 5.6 | Persistencia real: cerrar el proceso Streamlit, reabrir y comparar | Mismos datos |
| 5.7 | Actualizar el README (B-09) y la matriz de pruebas | Documentación coherente con la suite |

---

## Riesgos generales de implementación

1. **La fase 1.3 cambia el modelo de transacciones de toda la aplicación.** Es el punto con mayor probabilidad de regresiones. Conviene implementarlo antes que el resto de la fase 1 y probarlo pantalla por pantalla.
2. **Migración de la BD real.** Siempre sobre una copia primero; nunca sin la copia de 0.1.
3. **Decisiones del usuario pendientes:**
   - Opción (a) o (b) en 1.4.
   - Convención de signos en 2.4.
   - Qué hacer con los 19 ceros de 2021.
   - Criterio de ROE (total o atribuible a la controladora) para Alutech consolidado.
4. **Fuera de alcance:** autenticación multiusuario. Se mitiga restringiendo el servidor a localhost (0.4).
