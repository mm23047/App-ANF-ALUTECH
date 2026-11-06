# Auditoría integral técnica, funcional y financiera

**Aplicación:** Análisis Financiero (Python 3.12 · Streamlit 1.66.1 · SQLAlchemy 2.0.55 · SQLite)
**Caso de uso:** trabajo académico de ANF con los estados de Alutech, S. A. de C. V. y subsidiarias, División Acero, ejercicios 2021–2025
**Fecha:** 2026-11-01
**Tipo:** auditoría de solo lectura. No se modificó código, base de datos, dependencias ni importes.

Documentos relacionados: `PLAN_DE_CORRECCION.md`, `MATRIZ_DE_PRUEBAS.md`, `INVENTARIO_DEL_PROYECTO.md`.

---

## 0. Estado de corrección (actualizado 2026-11-01, tras la fase 7, salvo la conciliación con Alutech)

Los hallazgos originales se conservan sin cambios en las secciones siguientes. Esta tabla registra su estado.

| ID | Estado | Evidencia |
|---|---|---|
| C-01 | CORREGIDO | `database/backup_utils.py`, `app.py`, `modules/backup.py`. H01 y H02 aprueban; `tests/test_fase1_restauracion.py` |
| C-02 | CORREGIDO | `modules/excel_import.py` (vista previa solo de lectura), `app.py` (`render_scope`). D01 y D02 aprueban |
| C-03 | CORREGIDO (bloqueo simple) | `database/repositories.update_account`, `modules/accounts.py`. B01–B03 aprueban |
| A-03 | CORREGIDO | `modules/data_entry.py`: campos vacíos, solo se guardan importes informados. I01 aprueba. Los 19 ceros heredados de 2021 se conservan por decisión del usuario |
| A-07 | CORREGIDO | `components/money.py` + `components/transacciones.py`. D03, D04 e I02 aprueban |
| A-08 | CORREGIDO | `change_history.fiscal_period_id/account_id/lote_id`; id real del registro; filtros. C01 aprueba. Las 52 filas heredadas no se reescriben (sus columnas nuevas quedan en NULL) |
| M-01 | CORREGIDO | `parse_anio` (1990–2100, entero exacto). D05 y D06 aprueban |
| M-02 | CORREGIDO | Importes en centavos enteros (`Centavos`) + `parse_importe`. D07 e I03 aprueban; E01 y E02 siguen aprobando |
| M-05 | CORREGIDO | Cierre, reapertura, borrado de importes y de ejercicios vacíos; disparadores en la BD |
| M-06 | CORREGIDO | `render_scope` y `ejecutar_escritura` |
| M-09 | CORREGIDO | `database/migrations.py` (user_version) y `sqlite3.backup` con verificación |
| M-10 | CORREGIDO | Servidor solo en localhost (fase 0). Fase 4: `components/confirmacion.py`; la captura (Balance, Resultados, saldos iniciales) y la edición muestran el alcance (cuenta, valor actual, valor nuevo) y solo escriben tras "Confirmar y guardar", en una transacción; la importación muestra el alcance y solo importa la vista previa revisada. Cancelar, recargar, navegar o repetir el clic no escriben nada. `tests/test_fase4.py` |
| B-08 | CORREGIDO | `parse_importe(..., redondear=True)` con HALF_UP. E03 aprueba |
| M-11 | CORREGIDO | `reports/vertical_report.py` (tabla formateada desde Decimal). `tests/test_m11_vertical.py` y las páginas verticales de `tests/test_fase1_paginas.py` aprueban |
| A-01 | CORREGIDO | `calculations/dupont.py`: solo N-1. A01 aprueba |
| A-02 | CORREGIDO | N-1 utilizable solo si está completo, con activo > 0 y cuadra; saldos manuales solo si son completos; si no, aproximado con la causa. A03 y A04 aprueban |
| A-04 | CORREGIDO | Patrimonio inicial, final o promedio ≤ 0: ROE NO INTERPRETABLE, sin interpretación. A02 aprueba |
| A-05 | CORREGIDO (advertencia y confirmación) | `calculations/validation.py`; avisos en los reportes; confirmación en captura, edición e importación. El signo nunca se invierte. F01 y F03 siguen fallando por diseño: su expectativa exigiría invertir el signo |
| M-04 | CORREGIDO | `completo`, `categorias_faltantes` y `cuentas_sin_dato`. La bandera INCOMPLETO aparece en pantalla, PDF, Excel y Dashboard (`calculations/banderas.py`). F08 aprueba |
| M-07 | CORREGIDO | `calculations/controls.py`; conciliación en los reportes de Balance y Resultados y como control en DuPont |
| B-01 | CORREGIDO | DuPont sin redondeo intermedio; factores con 4 decimales en pantalla y PDF. A06 aprueba. La prueba original T-15, que exige el factor redondeado, falla: decisión pendiente |
| B-02 | CORREGIDO | La coincidencia tautológica se reemplazó por 7 controles útiles |
| A-06 | CORREGIDO | `reports/excel_export.py`: importes calculados en la columna C y fórmulas de control en la D, que solo leen la C. G01 y G02 aprueban; las fórmulas se evalúan en `tests/test_fase3.py` |
| M-03 | CORREGIDO | Vertical con subtotales, totales y utilidades, y su efecto; PDF del vertical (`export_vertical_pdf`). F06 y F07 aprueban |
| M-08 | CORREGIDO | El Dashboard indica si el ROE es definitivo, APROXIMADO (con la causa) o NO INTERPRETABLE, y etiqueta los indicadores incompletos |
| B-03 | CORREGIDO | Valores calculados en lugar de fórmulas sin caché; base del vertical numérica; banderas en celdas propias |
| B-04 | CORREGIDO | `components/tables.py` usa `st.markdown` nativo (sin HTML) con `text_alignment="right"`; `components/texto.md` escapa los datos del usuario (empresa, moneda, nombres de cuenta) en todo elemento Markdown; el PDF escapa la moneda en los 2 párrafos que no lo hacían (Balance descuadrado y base del vertical: con la moneda `<x` el PDF fallaba). El único `unsafe_allow_html` es el CSS constante de `app.py` |
| B-05 | CORREGIDO | `requirements.txt` fija las 8 versiones probadas (las instaladas; no se actualizó ninguna). Ver `PLAN_DE_CORRECCION.md`, fase 4 |
| B-06 | CORREGIDO | `modules/excel_import.normalizar_codigo`: un número entero exacto (1001.0) se normaliza a "1001"; decimales, valores lógicos, fechas, infinitos y enteros > 2^53 se reportan como `CODIGO_AMBIGUO`; también un número que coincide con un código con ceros a la izquierda y un texto "1003.0". Los textos válidos no cambian. D08 aprueba |
| B-07 | CORREGIDO (datos, con autorización) | `data/financiera.db`, tabla `company`: `alutech` → `Alutech`, `aluetch sv` → `Alutech SV`, `El Salvaodr` → `El Salvador`. Valores anteriores en `change_history` (ids 53–55, un lote) y en la copia `data/backups/financiera_pre_b07_20261101_182614_096704.db` |
| B-10 | CORREGIDO (con autorización, antes de la fase 5) | `components/celdas_excel.py`: todo texto se escribe como cadena literal (`data_type = "s"`) y, si empieza con `=`, `+`, `-`, `@`, tabulador o retorno de carro, con `quotePrefix`; las fórmulas de control solo se escriben con `formula()`. Usado en `reports/excel_export.py` (31 escrituras de datos, 3 de fórmulas) y en la plantilla de importación. `tests/test_b10.py` |
| B-09 | CORREGIDO | `README.md` actualizado (fase 5-F): estado real de la suite (418 pruebas: 416 aprobadas, F01 y F03 por diseño), versiones probadas, confirmaciones, códigos de importación, texto literal en las exportaciones y estructura vigente. Ya no menciona "18 casos requeridos" |
| Fase 5 | COMPLETADA salvo 5.5 | Caso controlado de 3 ejercicios (0,00 de diferencia), integración del flujo completo (restauración con la misma huella SHA-256) y persistencia con el proceso real de Streamlit. Ver `PLAN_DE_CORRECCION.md` |
| Conciliación con Alutech (5.5, N-01) | PENDIENTE | Requiere los estados financieros originales 2020–2025; no se usaron cifras ficticias |
| Fase 6 (validación operativa) | COMPLETADA | 22 libros abiertos en Microsoft Excel 16 (instalado en el equipo: la afirmación de la auditoría y de la fase 3 de que no había hoja de cálculo era incorrecta), 16 páginas recorridas en Edge real, restauración con dos pestañas, acceso desde la red local bloqueado por `server.address = "localhost"`. Hallazgos O-1 a O-7 (abajo) |
| O-1 | CORREGIDO (fase 7.1) | Una confirmación preparada en una pestaña se guardaba sobre la base restaurada desde otra. `components/confirmacion.py`: `EstadoBase` (identidad del archivo SQLite + último registro del historial) se guarda al preparar y se comprueba antes de guardar y dentro de la transacción; la importación lo incluye en su firma. `tests/test_fase7.py` (8) y escenario de dos pestañas en Edge: no se escribe nada y se pide preparar de nuevo |
| O-2 | CORREGIDO (fase 7.2) | Una restauración rechazada (archivo en uso) dejaba `financiera_pre_restauracion_*`; tampoco se limpiaba si la copia previa no se podía verificar. `database/backup_utils.restaurar` elimina el `.restaurando` y la copia de la operación si no hubo reemplazo y la base sigue intacta (mismo SHA-256); en caso de duda o de reversión la conserva. `tests/test_fase7.py` (8), incluido un bloqueo real de Windows |
| O-3, O-4 | CORREGIDOS (fase 7.3) | Excel: etiquetas cortadas e impresión en varias páginas de ancho. Columna B según su texto, textos largos ajustados, impresión horizontal en una página de ancho con encabezado repetido. Valores, fórmulas y formatos idénticos celda por celda; verificado en Excel y en PDF |
| O-5 | CORREGIDO (fase 7.4) | DuPont: tabla de resultados completa (el ROE ya no queda oculto) y detalle de los controles legible; Modificación de datos sin la columna `account_id` (sigue en los datos) |
| O-6 | INVESTIGADO, sin cambios (fase 7.5) | El aviso "File change · Rerun" lo provoca la escritura de `.pyc` en `__pycache__`: los paquetes no tienen `__init__.py` y Streamlit vigila esos directorios completos. Aparece en árboles sin `__pycache__` o tras cambiar el código; es inocuo. Opciones propuestas, pendientes de autorización: `__init__.py` en los paquetes o `server.fileWatcherType = "none"` |
| O-7 | OBSERVACIÓN (no es un error) | Con la BD de trabajo, el Balance 2021 figura como DEFINITIVO aunque todos sus importes son 0,00: por la regla aprobada, un 0 escrito cuenta como dato, y los 19 ceros de 2021 se conservan por decisión del usuario. No es un error de cálculo y no se modifica |
| Resto | PENDIENTE (autorización independiente) | Pasos 4.1 (ayuda de signos por grupo y plantillas estáticas de `assets/plantillas/` sin la hoja "Convención de signos"), 4.3 (mensajes de error técnicos) y 4.8 (página "Configuración" duplicada). F01 y F03 siguen fallando por diseño (ver A-05) |

**Hallazgo nuevo B-10 (preexistente, detectado en la fase 4).** Verificación: COMPROBADO (`openpyxl` 3.1.5).
- **Archivo:** `reports/excel_export.py` (líneas 40, 42, 81, 89 y 92: nombre de la empresa, moneda, grupos y nombres de cuenta).
- **Problema:** `openpyxl` guarda como fórmula cualquier texto que empiece con `=`. Un nombre de empresa o de cuenta como `=HYPERLINK("http://…","x")` se exportaría como fórmula activa (inyección de fórmulas en hojas de cálculo).
- **Riesgo:** bajo en uso local con un solo usuario; los datos los escribe el mismo usuario.
- **Corrección propuesta (no aplicada, requiere autorización):** escribir esas celdas como texto (`cell.data_type = "s"`) o anteponer un apóstrofo a los textos que empiecen con `=`, `+`, `-` o `@`.
- **Alcance real (revisión de la corrección):** además de esas líneas, todas las escrituras de texto de `reports/excel_export.py` (títulos, banderas, etiquetas, conceptos del vertical, controles y fuente de saldos del DuPont) y la plantilla de importación de `modules/excel_import.py`, que escribe códigos y nombres de cuenta. No hay otros puntos que generen XLSX.
- **Solución aplicada (autorizada):** `components/celdas_excel.py` separa los dos caminos. `texto()`/`escribir()` guardan cualquier `str` como cadena literal (en el archivo, `t="inlineStr"`, sin `<f>`) y marcan con `quotePrefix` los que empiezan con un signo de fórmula, para que Excel los mantenga como texto aunque se edite la celda; el texto no se altera (sin apóstrofo añadido). `formula()` es el único camino para las fórmulas de control y rechaza lo que no empiece con `=`. Los caracteres de control que XLSX no admite (U+0000–U+0008, U+000B, U+000C, U+000E–U+001F) se eliminan, porque openpyxl no puede guardarlos; los saltos de línea se conservan (un retorno de carro se lee como salto de línea, normalización propia de XML).
- **Verificación:** con datos normales, los 6 libros (4 reportes, el vertical en formato anterior y la plantilla) son idénticos celda por celda (valor, tipo, formato, negrita) a los del código anterior, incluidas las 58 fórmulas de control. Las pruebas de `tests/test_b10.py` que exportan reportes fallan con el código anterior (14) y aprueban con el corregido.

**Hallazgo nuevo M-11 (preexistente, detectado en la fase 1).** Verificación: COMPROBADO (prueba de humo con `AppTest`).
- **Archivo:** `reports/vertical_report.py` (líneas 22–23 y 46–48; igual en el reporte de resultados).
- **Problema:** convierte los importes a `float` y después llama a `format_money(float)`, que usa `Decimal.quantize`.
- **Consecuencia:** las páginas "Análisis Vertical del Balance General" y "del Estado de Resultados" fallan con `AttributeError: 'float' object has no attribute 'quantize'` en cuanto el ejercicio tiene importes. Con la BD actual (solo ceros) no se manifiesta, porque la base es 0 y el reporte termina antes.
- **Antigüedad:** el archivo no cambió respecto a la línea base (`git diff 2913c49`), y el `format_money` original también falla con un `float`.
- **Solución propuesta:** se corrige junto con M-03 en la fase 3.
- **Prueba:** `tests/test_fase1_paginas.py`.
- **Estado:** CORREGIDO antes de la fase 2, con autorización del usuario (ver `PLAN_DE_CORRECCION.md`).

---

## 1. Resumen ejecutivo

La aplicación tiene una base razonable:
- Separa los cálculos de la persistencia.
- Usa `Decimal` en los cálculos.
- No almacena subtotales.
- Tiene claves foráneas y restricciones de unicidad activas.
- Las fórmulas centrales del Balance General, el Estado de Resultados y la identidad DuPont son aritméticamente correctas con datos limpios.

**Sin embargo, todavía no produce información financiera confiable ni verificable para el trabajo académico.** Se comprobaron por ejecución defectos que:

1. **Pueden destruir la base de datos.** La restauración acepta un archivo corrupto o ajeno, sobrescribe la BD válida y no guarda una copia previa (C-01).
2. **Modifican datos sin confirmación.** La vista previa de la importación Excel crea ejercicios fiscales permanentes, incluso si el usuario cancela (C-02).
3. **Alteran retroactivamente los estados históricos.** Reclasificar una cuenta con saldos cambia o hace desaparecer importes de ejercicios anteriores (C-03).
4. **Distorsionan el ROE DuPont sin avisar.** El saldo inicial se toma de ejercicios no consecutivos (A-01), de ejercicios guardados en ceros (A-02) o de capturas parciales (A-02). El ROE con patrimonio negativo se presenta como válido (A-04).
5. **No distinguen ausencia de dato y cero.** El formulario guarda 0.00 en todas las cuentas, y un balance vacío "cuadra" (A-03).
6. **No validan signos.** Una depreciación positiva infla el activo y un costo negativo infla la utilidad (A-05).
7. **Generan archivos Excel con referencias circulares** cuando falta un grupo de cuentas (A-06).

**Resultado de pruebas:** se ejecutaron 77 pruebas: 47 aprobadas y 30 fallidas.
- Las 30 pruebas originales del proyecto aprueban.
- De las 47 pruebas de verificación escritas para esta auditoría, 17 aprueban y 30 fallan. Cada fallo corresponde a un defecto confirmado.

Que las 30 pruebas originales aprueben **no demuestra** la corrección financiera: no cubren ninguno de los escenarios en los que se encontraron los defectos.

**Recuento de hallazgos:** 3 CRÍTICOS, 8 ALTOS, 10 MEDIOS y 9 BAJOS.

**Limitación principal:** la BD no contiene datos de Alutech. Solo tiene el ejercicio 2021 con 19 saldos en 0.00, y los documentos de `documentos/` son material didáctico. Por eso no fue posible conciliar ningún reporte contra los estados publicados de 2021–2025.

---

## 2. Arquitectura revisada

```
Interfaz (Streamlit)        app.py, components/, modules/, reports/*_report.py
        │  una sola Session por ejecución de página (app.py:44) con commit al final
Lógica de cálculo           calculations/ (lee la BD a través de repositories)
Persistencia                database/ (models, repositories, connection, seed)
Exportación                 reports/pdf_export.py, reports/excel_export.py
```

**Fortalezas:**
- La capa de cálculo es única: los reportes en pantalla, PDF y Excel consumen los mismos objetos de resultado. No hay fórmulas financieras duplicadas en los reportes, salvo las fórmulas nativas de Excel (ver A-06).
- Los subtotales no se almacenan, de acuerdo con el principio declarado en el README.
- Las enumeraciones (`database/enums.py`) centralizan las reglas de clasificación.
- No hay importaciones circulares (se importaron los 24 módulos uno por uno).
- El código es legible, con nombres consistentes y dataclasses tipadas.

**Debilidades:**
- **Transacción implícita por página.** `app.py:44` abre un `session_scope()` que envuelve toda la página y hace `commit` al terminar. Cualquier `flush()` realizado al renderizar, aunque sea durante una "vista previa", se vuelve permanente. Esta es la causa raíz de C-02 (hallazgo M-06).
- **Cálculos acoplados a la BD.** `calculations/` llama a `database.repositories`; no se pueden calcular estados a partir de datos en memoria. Esto impide probar las fórmulas de forma independiente y hacer simulaciones.
- **Engine global de proceso.** `database/connection.py:38-39` es compartido por todas las pestañas o usuarios conectados al mismo servidor Streamlit. Una restauración en una pestaña afecta a todas.
- **Manejo de excepciones.** Solo hay 5 bloques `except` en toda la aplicación. Los errores de integridad (`IntegrityError`) y de E/S en importación, edición, respaldo y restauración no se controlan y llegan al usuario como trazas de Python.
- **Sin migraciones.** `create_all` no altera tablas existentes (M-09).

**Conclusión de arquitectura:** el diseño por capas es adecuado para una aplicación local de una sola empresa con varios ejercicios. Las correcciones necesarias son localizadas y no exigen reescribir la aplicación, con dos excepciones: el ciclo de vida de la transacción por página y el versionado de la clasificación de cuentas.

---

## 3. Módulos inspeccionados

Se leyeron completos los 35 archivos `.py` (4.109 líneas), además de `requirements.txt`, `README.md`, `.gitignore`, los registros de la última ejecución, el esquema real de `data/financiera.db` (en una copia de solo lectura) y el texto de los dos `.pptx` de `documentos/`. El PDF de `documentos/` (9,9 MB, libro de texto) no se analizó. El detalle está en `INVENTARIO_DEL_PROYECTO.md`.

---

## 4. Resultados: base de datos

| Verificación | Resultado | Evidencia |
|---|---|---|
| PK en todas las tablas | Correcto | Esquema real |
| FK de importes a ejercicio y cuenta | Correcto (CASCADE en ejercicio, RESTRICT en cuenta) | `models.py:139-144`; prueba B04 aprobada |
| `PRAGMA foreign_keys=ON` | Correcto | `connection.py:29-33` |
| Ejercicio único por año | Correcto | `uq_fiscal_period_anio` |
| Cuenta única por código | Correcto | `uq_account_codigo`; prueba aprobada |
| Importe único por cuenta y ejercicio | Correcto | Prueba B05 aprobada |
| Eliminación de cuentas usadas | Protegida: no existe función de borrado; RESTRICT en BD | `repositories.py`, `accounts.py:170-178` |
| Subtotales no almacenados | Correcto | `models.py` |
| Modificar un ejercicio no altera otro | Correcto | Prueba B06 aprobada |
| **Integridad histórica ante cambios del catálogo** | **Fallo comprobado** | C-03 (B01–B03) |
| **Historial identifica ejercicio y registro** | **Fallo comprobado** | A-08 (C01) |
| Tipo de almacenamiento de importes | `REAL` (binario), no decimal exacto | M-02 (I03) |
| Sesiones y transacciones | `session_scope` correcto; uso por página con commit implícito | M-06 |
| Errores de SQLite | No controlados en importación, edición ni restauración | A-07, C-01 |
| Ampliaciones futuras | Sin migraciones | M-09 |
| Ejercicios cerrados | `CERRADO` definido y nunca usado; nada impide editar ejercicios revisados | M-05 |

**Integridad histórica: mecanismo propuesto** (detalle en el plan, fase 1):
1. Bloquear en `update_account` los cambios de `categoria_principal`, `subcategoria` y `efecto` cuando la cuenta tenga movimientos.
2. Ofrecer como alternativa una **reclasificación explícita**: desactivar la cuenta vieja, crear una nueva y, opcionalmente, trasladar saldos solo desde un ejercicio dado en adelante. La operación debe quedar en el historial con su ejercicio de vigencia.
3. Si se requiere reclasificación retroactiva (reexpresión), guardar en cada `balance_entry` e `income_entry` una instantánea de la clasificación vigente al capturar, o una tabla `account_classification(account_id, desde_anio, categoria, subcategoria, efecto)` que los cálculos consulten según el año del ejercicio.

---

## 5. Resultados: captura y modificación de datos

### 5.1 Captura manual (`modules/data_entry.py`)

| Aspecto | Resultado |
|---|---|
| Validación de importes | `st.number_input` solo acepta números. No hay validación de rango ni de signo (A-05) |
| Valores vacíos | No posibles: cada campo vale 0.00 por defecto. **Al guardar se crean registros 0.00 para todas las cuentas activas** (A-03; prueba I01 y BD real con 19 ceros) |
| Negativos | Aceptados sin advertencia. Son necesarios para la depreciación, pero no hay indicación en pantalla (A-05) |
| Separador decimal | Lo controla el widget de Streamlit; no aplica |
| Precisión | `float` → `round(x, 2)` (redondeo bancario sobre binario) → `Decimal`. Ejemplo: 2.675 se guarda como 2.67 (prueba E03; B-08) |
| Validación de cuentas | Solo muestra cuentas activas del catálogo; correcto |
| Confirmación antes de guardar | No hay; un clic en "Guardar" escribe todas las cuentas (M-10) |
| Saldos iniciales | El aviso de `data_entry.py:151-159` usa la misma lógica defectuosa de "ejercicio anterior con huecos" (A-01) |

### 5.2 Importación Excel (`modules/excel_import.py`)

| Aspecto | Resultado | Prueba |
|---|---|---|
| Validación de columnas | Correcta (`excel_import.py:145-148`) | — |
| Cuentas inexistentes | Detectadas | Original aprobada |
| Cuentas inactivas | Detectadas | — |
| Duplicados dentro del archivo | Detectados (código + período) | D09 aprobada |
| Reimportar el mismo archivo | No duplica (upsert) | D11 aprobada |
| No sobrescribir sin autorización | Implementado mediante casilla | Inspección |
| Errores parciales | Importa solo las filas OK | D10 aprobada |
| **La vista previa no modifica la BD** | **FALLA: crea el ejercicio y su historial** | D01 (C-02) |
| **Cancelar no deja rastro** | **FALLA: el ejercicio creado permanece** | D02 (C-02) |
| **Valor vacío** | **FALLA: se acepta como `Decimal('NaN')` con estado OK** | D03 (A-07) |
| **Confirmar con valor vacío** | **`IntegrityError` no controlado; toda la importación aborta con traza** | D04 (A-07) |
| Período con decimales | 2021.9 se trunca a 2021 sin aviso | D05 (M-01) |
| Período fuera de rango | Año 21 aceptado: crearía el ejercicio "21" | D06 (M-01) |
| Más de 2 decimales | 0.30000000000000004 aceptado sin cuantizar | D07 (M-02) |
| Código numérico | 1001.0 se reporta como cuenta desconocida | D08 (B-06) |
| Transacción y reversión | Una sola transacción por ejecución; ante una excepción se revierte todo, sin mensaje legible | D04 |

### 5.3 Modificación (`modules/data_edit.py`)

| Aspecto | Resultado |
|---|---|
| Solo se modifica el registro seleccionado | Correcto: compara fila por fila y hace upsert por cuenta y ejercicio (B06) |
| Celda vaciada | **`IntegrityError` no controlado** (prueba I02; A-07) |
| Valor anterior y nuevo en el historial | Sí, como texto |
| Ejercicio y cuenta en el historial | **No** (A-08) |
| Pestaña "Historial de este ejercicio" | **Muestra el historial de todos los ejercicios** (`data_edit.py:101-105`; A-08) |
| Eliminar un importe capturado | No disponible (`delete_entry` no se usa; M-05) |

### 5.4 Catálogo (`modules/accounts.py`)
- Permite editar categoría, subcategoría y efecto de cuentas con movimientos. El aviso "tiene movimientos históricos" solo aparece en el botón de desactivar (`accounts.py:172-173`), no al editar (C-03).
- No hay borrado de cuentas (correcto). El código de cuenta no es editable desde la interfaz.

### 5.5 Empresa (`modules/company.py`)
- Valida campos obligatorios. La BD real contiene datos con errores tipográficos: nombre comercial "aluetch sv", país "El Salvaodr" y nombre legal "alutech" en minúsculas. Aparecerán en los encabezados de todos los PDF y Excel (B-07).

---

## 6. Resultados: cálculos financieros

### 6.1 Balance General (`calculations/balance_sheet.py`)

| Fórmula | Implementación | Estado |
|---|---|---|
| AC + ANC = Activo total | `balance_sheet.py:78` | Correcta (pruebas aprobadas) |
| PC + PNC = Pasivo total | `:82` | Correcta |
| Pasivo + Patrimonio = Total P+P | `:89` | Correcta |
| Diferencia = Activo − (P+P) | `:90` | Correcta; no se corrige automáticamente (prueba original aprobada) |
| Activo, pasivo o patrimonio negativos | Suma algebraica | Correcta (F05) |
| **Cuentas correctoras** | Suma el valor tal como se capturó; `naturaleza_saldo` se ignora | **La depreciación capturada en positivo aumenta el activo** (F01: 1.000 + 300 = 1.300 en vez de 700). Comprobado (A-05) |
| **Ausencia frente a cero** | `tiene_datos = len(entries) > 0` | **Un estado con una sola cuenta se considera "con datos"; las cuentas faltantes valen 0. Un balance guardado en ceros "cuadra"** (F08, I01; A-03, M-04) |
| Presentación de la diferencia | En pantalla, PDF y Excel | Correcta |

Regla de signo identificada: **el importe se suma con el signo con que se capturó**. Los activos, pasivos y patrimonio se capturan en positivo y las correctoras en negativo. Esta convención es válida, pero no está documentada en la pantalla ni se valida.

### 6.2 Estado de Resultados (`calculations/income_statement.py`)

| Fórmula solicitada | Implementación | Estado |
|---|---|---|
| UB = Ingresos − Costo | `:86` | Correcta |
| UO = UB − Gastos operativos netos | `:100-106`: UB − Admin − Ventas + Otros ingresos op. − Otros gastos op. | Correcta (F04, prueba original) |
| RF = Ingresos financieros − Gastos financieros | `:110` | Correcta |
| UAI = UO + RF + Otros no operativos | `:118-120` | Correcta |
| UN = UAI − ISR | `:123` | Correcta |
| Resultados negativos | Algebraicos | Correctos (A09) |
| **Signos** | Regla fija: costos y gastos se capturan en positivo y se restan | **Un costo capturado como (600) negativo suma: UB = 1.600 en vez de 400** (F03). Riesgo alto, porque los estados publicados suelen mostrar los costos entre paréntesis (A-05) |
| Otros ingresos y gastos operativos | Subcategoría `OTROS_OPERATIVOS` + `efecto` | Correcto, pero el efecto es editable de forma retroactiva (C-03, B02: la utilidad de 2021 pasó de 1.100 a 900) |

**Limitaciones del modelo:** solo hay una línea de ingresos (`INGRESOS`), sin devoluciones ni descuentos. Tampoco hay participación en asociadas, operaciones discontinuadas, partidas de ORI, participación no controladora ni otras subcategorías de gasto. Para Alutech "y subsidiarias" (estados consolidados) esto puede ser relevante: el **interés minoritario** no tiene categoría en el patrimonio y la utilidad neta no distingue la parte atribuible a la controladora. Esto afecta el ROE (ver 7).

### 6.3 Análisis vertical del Balance (`calculations/vertical_analysis.py:43-56`)
- Base = activo total del mismo ejercicio. **Correcta.**
- No calcula si la base es 0 (devuelve `None`). **Correcto.**
- Las correctoras mantienen su signo. **Correcto.**
- **No incluye subtotales** (AC, ANC, total pasivo, total patrimonio ni total P+P). Solo lista cuentas (F07; M-03).
- No distingue cuentas sin dato de cuentas en cero (M-04).

### 6.4 Análisis vertical del Estado de Resultados (`vertical_analysis.py:66-88`)
- Base = ingresos netos del mismo ejercicio. **Correcta.**
- Con ingresos en 0 no calcula. **Correcto** (prueba original aprobada).
- **Omite las líneas de ingresos (100%) y todas las utilidades** (bruta, operativa, antes de impuestos y neta). El grupo `inc.ingresos_netos` no está en la tupla de `:70-81` (F06; M-03). Un análisis vertical de resultados sin margen bruto, operativo y neto es incompleto para el análisis académico.
- Costos y gastos aparecen con % positivo; la presentación no indica que restan.

---

## 7. Resultados: DuPont (`calculations/dupont.py`)

### 7.1 Fórmulas

| Fórmula | Implementación | Estado |
|---|---|---|
| Margen = UN / Ingresos | `:167` | Correcta |
| Rotación = Ingresos / Activo promedio | `:168` | Correcta |
| Multiplicador = Activo prom. / Patrimonio prom. | `:169` | Correcta |
| ROE DuPont = producto | `:171` | Correcto; calculado con factores sin redondear |
| ROE directo = UN / Patrimonio prom. | `:173` | Correcto (A05: 15.19% = esperado) |
| Coincidencia | `:175`, tolerancia 0.01 pp | Es una **identidad algebraica** sobre los mismos datos: no puede fallar salvo por redondeo, así que no valida nada (B-02) |
| Promedios = (inicial + final) / 2 | `:154-155` | Correcto, aunque se redondean a 2 decimales antes de dividir (B-01) |

### 7.2 Origen de los saldos iniciales (`get_saldos_iniciales`, `:67-96`)

1. `get_previous_period` (`repositories.py:117-126`) devuelve el **ejercicio más reciente anterior, aunque no sea el inmediato** (el docstring lo dice: "Soporta huecos").
2. Si ese ejercicio tiene **al menos un registro** de balance, aunque sean ceros o esté incompleto, su total se usa como saldo inicial **con `aproximado=False`**.
3. Si no, se usan los saldos manuales. **Cualquier** registro manual activa esta vía, y las categorías no capturadas valen 0 con `aproximado=False`.
4. Si no hay nada, se usa el saldo final con `aproximado=True` y se muestra una advertencia. **Correcto.**

| Caso especial | Resultado observado | Estado |
|---|---|---|
| Ingresos = 0 | No disponible | Correcto (A07) |
| Activo promedio = 0 | No disponible | Correcto (A08) |
| Patrimonio promedio = 0 | No disponible | Correcto (prueba original) |
| **Patrimonio promedio negativo** | UN = −100, Pat. = −200 → **ROE = +50,00%**, multiplicador −5,00; sin advertencia. La interpretación dice que un mayor multiplicador significa "mayor proporción... financiada con deuda" | **FALLA** (A02; A-04) |
| Utilidad negativa | ROE −20%, margen −10% | Correcto (A09) |
| **Ejercicio no consecutivo (2021 → 2023)** | Activo inicial de 2023 = activo final de 2021; fuente "Balance final del ejercicio 2021"; `aproximado=False` | **FALLA**: viola la regla obligatoria (A01; A-01) |
| **Ejercicio anterior guardado en ceros** | Activo inicial 0,00 → activo promedio a la mitad → **ROE 40% en vez de 20%**; `aproximado=False` | **FALLA** (A03; A-02) |
| **Saldos manuales parciales** (solo patrimonio) | Activo inicial 0,00 → rotación 2,00 en vez de 1,00; `aproximado=False` | **FALLA** (A04; A-02) |
| Modificación de un balance histórico | El ROE del ejercicio siguiente cambia automáticamente (los promedios se recalculan). Es correcto como cálculo, pero el usuario no recibe ningún aviso y el historial no permite saber qué ejercicio cambió | Comportamiento esperado; trazabilidad insuficiente (A-08) |
| Reclasificaciones y reexpresiones | No hay mecanismo; los cambios del catálogo alteran todo el historial (C-03) | No soportado |
| Primer ejercicio (2021) | Si no se capturan saldos de 2020, se usa el saldo final como aproximación, con advertencia en pantalla y PDF | Correcto, **pero el Dashboard muestra ese ROE sin advertencia** (`dashboard.py:42`; M-08) |

### 7.3 Presentación
- Los factores mostrados se redondean (margen al 0,01%, rotación y multiplicador a 2 decimales) y su producto no reproduce el ROE mostrado: 1,58% × 2,33 × 3,00 = 11,04%, frente a un ROE de 11,07% (A06; B-01). Para un trabajo académico, el lector no puede verificar el resultado con los factores impresos.
- Para Alutech consolidado: el ROE usa el patrimonio total, incluida la participación no controladora si se captura dentro del patrimonio, y la utilidad neta total. Debe documentarse el criterio (ROE de la controladora frente a ROE total).

---

## 8. Resultados: precisión monetaria

| Etapa | Tipo | Observación |
|---|---|---|
| Captura por formulario | `float` (`st.number_input`) → `Decimal(str(round(x,2)))` | Redondeo bancario sobre binario: 2.675 → 2.67 (E03). Riesgo bajo, porque el widget muestra 2 decimales |
| Importación Excel | `Decimal(str(valor_pandas))` | No cuantiza (0.30000000000000004 aceptado, D07). `NaN` aceptado (D03) |
| Edición | `float` → `Decimal(str(round(x,2)))` | Igual que la captura; NaN no controlado (I02) |
| **Persistencia** | Columna `NUMERIC(18,2)`; SQLite la guarda como **REAL** (I03) | Exacta para importes típicos (E02) y hasta 123.456.789.012.345,67 (E01), pero no es almacenamiento decimal |
| Cálculos | `Decimal` + `q2` HALF_UP en cada subtotal | Correcto. El redondeo intermedio de subtotales es inocuo si los datos ya tienen 2 decimales |
| Vertical | `Decimal`, redondeo final a 2 decimales | Correcto |
| DuPont | `Decimal`; promedios redondeados a 2 decimales antes de dividir; factores devueltos ya redondeados | Redondeo prematuro menor (B-01) |
| Excel | `float(Decimal)` | Aceptable para presentación |
| PDF | Texto formateado | Correcto |
| Dashboard y gráficos | `float` | Solo presentación |

**Criterio uniforme propuesto:**
1. Convertir **todas** las entradas con una única función `parse_importe(x) -> Decimal` que rechace NaN e infinitos, rechace más de 2 decimales (o los cuantice HALF_UP con aviso explícito) y valide el rango de `NUMERIC(18,2)`.
2. Persistir como **entero en centavos** (`BigInteger`) o como `String` decimal con un `TypeDecorator`, para evitar `REAL`.
3. Calcular siempre con `Decimal` sin redondear y aplicar `q2` solo en la presentación y exportación. Las razones se guardan sin redondear y se formatean con 2 decimales.
4. Expresar los porcentajes siempre como fracción interna y ×100 solo al presentar.

---

## 9. Resultados: reportes y exportaciones

| Verificación | Resultado |
|---|---|
| Los reportes usan los cálculos centrales | Sí, los 4 reportes y ambos exportadores |
| Importes coinciden con la BD | Sí (mismos objetos `Linea`) |
| Subtotales coinciden | En pantalla y PDF, sí. **En Excel, las fórmulas son circulares cuando hay grupos vacíos** (G01: `C12 = C10+C12`; G02: `C22 = C20-C22`; A-06) |
| Porcentajes | Correctos sobre las filas incluidas; faltan subtotales (M-03) |
| Ejercicio identificado | Sí, en el encabezado de pantalla, PDF y Excel |
| Datos incompletos señalados | **No** (M-04) |
| Aproximaciones señaladas | DuPont en pantalla y PDF: sí. Excel DuPont: solo el texto de "fuente". **Dashboard: no** (M-08) |
| Excel conserva valores numéricos | Las líneas sí (float con formato `#,##0.00`). Los subtotales son fórmulas **sin valor en caché**: las herramientas que no recalculan (pandas, visores web) los ven vacíos (B-03) |
| PDF | Correcto. Un nombre con "&" no rompe el documento (G03) |
| Las exportaciones no alteran la BD | Comprobado: hash idéntico (G04) |
| Coherencia entre reportes | Balance, Resultados, Vertical y DuPont leen los mismos datos y son coherentes entre sí. No hay conciliación entre "Resultado del ejercicio" del balance y la utilidad neta del ER; solo un aviso informativo en la captura (`data_entry.py:116-123`) (M-07) |
| Exportación PDF del vertical | **No existe** (M-03) |

---

## 10. Resultados: copias de seguridad (`modules/backup.py`, `app.py:16-25`)

| Verificación | Resultado |
|---|---|
| Creación | `shutil.copy2` del archivo vivo con nombre `financiera_YYYYmmdd_HHMMSS.db`. No usa la API de respaldo de SQLite ni verifica la integridad (M-09, punto b) |
| Descarga | Correcta |
| Identificación | Por marca de tiempo; correcta |
| **Validación al restaurar** | **Ninguna**: no comprueba encabezado SQLite, `integrity_check`, esquema ni la presencia de `company` |
| **Archivo corrupto** | Sobrescribe la BD y la aplicación cae con `DatabaseError: file is not a database`. **La BD original se pierde** (H01) |
| **SQLite ajena** | Se acepta, se muestra "Base de datos restaurada correctamente." y la empresa y todos los datos desaparecen (H02) |
| Protección de la BD actual | **No se crea una copia previa automática** |
| Sesiones abiertas | `dispose_engine()` libera el pool del proceso, pero otras pestañas comparten el engine. En Windows, un archivo abierto podría impedir la copia (no verificado) |
| Excepciones | `app.py:21-25` no tiene try/except y la bandera `pending_restore` se elimina antes de copiar |
| Reversibilidad | No es reversible si no existe una copia manual previa |

---

## 11. Resultados: interfaz y experiencia de usuario

Revisión por inspección de código. La interfaz no se navegó manualmente; ver la sección 14.

- La navegación es un radio lateral con 16 opciones. Hasta registrar la empresa solo se muestra "Datos de la empresa". Funciona.
- El selector de ejercicio es compartido. Cada reporte usa su propia clave y por defecto toma el **último** ejercicio. Los reportes solo muestran el ejercicio seleccionado: correcto.
- El **Dashboard** siempre muestra el último ejercicio, aunque esté vacío. Lo indica ("Último ejercicio disponible"), pero no advierte si el ROE es aproximado (M-08).
- `select_fiscal_period` incluye "Crear nuevo ejercicio" en las páginas de captura. No hay forma de borrar un ejercicio creado por error (M-05).
- **Exacto, aproximado, incompleto o inválido:** DuPont distingue "aproximado" e "inválido" (división entre 0). **No existe el estado "incompleto"** en ningún reporte (M-04). Los casos de A-01, A-02 y A-04 se presentan como exactos.
- Mensajes de error: los errores de integridad se muestran como trazas técnicas (A-07).
- La captura no explica la convención de signos (A-05).
- Confirmaciones: la restauración pide confirmación (aunque no valida, C-01). La captura y la edición no piden confirmación (M-10).
- La "Configuración" del menú abre el mismo formulario que "Datos de la empresa".

---

## 12. Resultados de pruebas

### 12.1 Entorno
- Python 3.12.10 en `.venv`; todas las dependencias instaladas dentro de los rangos declarados (ver inventario).
- Comando ejecutado: `.venv\Scripts\python -m pytest tests/ -v` → **30 aprobadas, 0 fallidas, 0 errores** (6,9 s).

### 12.2 Pruebas de verificación de la auditoría
- Archivo: `C:\Users\estua\AppData\Local\Temp\claude\c--Users-estua-Documents-ANF-appfinanciera\9682c29f-24d7-41f1-98d9-8fdb842605d9\scratchpad\audit_tests\test_auditoria.py`. Está fuera del proyecto y es temporal de esta sesión. Se recomienda incorporarlo al proyecto en la fase 5, con autorización. *(Actualización: se incorporó en la fase 0 como `tests/test_auditoria.py`; ver `PLAN_DE_CORRECCION.md`, paso 0.3.)*
- Cada prueba afirma el **comportamiento correcto esperado**; un fallo confirma el defecto.
- Resultado: **47 ejecutadas: 17 aprobadas y 30 fallidas.** Detalle en `MATRIZ_DE_PRUEBAS.md`.
- Todas usan BD SQLite temporales. El hash SHA-256 de `data/financiera.db` es idéntico antes y después: `f026863d00f841c042c996e0ccb12a1317992ede97d2e544f4cba5955630a82d`.

### 12.3 Simulaciones (mocks) utilizadas y lo que dejaron sin verificar

| Prueba | Simulado | Sin verificar |
|---|---|---|
| D01, D02, D04, D10, D11 | `st.file_uploader` (devuelve un XLSX en memoria), `st.button` y `st.checkbox`. Se ejecutó el `render()` real dentro de `session_scope()`, igual que en `app.py` | Interacción real del navegador y reruns de Streamlit |
| I01 | `st.form_submit_button=True`, `st.rerun` | Render visual del formulario |
| I02 | `st.data_editor` devuelve NaN en una celda; `st.button`; `st.rerun` | Si el widget real de 1.66 entrega NaN o None al vaciar una celda (ambos casos llevan al mismo `round(float(...))`) |
| H01, H02 | Se usó `streamlit.testing.v1.AppTest` sobre el `app.py` real. Solo se redirigió `database.connection.DB_PATH` a una BD temporal | Bloqueos de archivo de Windows con varias pestañas abiertas |

### 12.4 Cobertura de los 24 escenarios solicitados
Ver la tabla "Cobertura de escenarios requeridos" en `MATRIZ_DE_PRUEBAS.md`. De los 24 escenarios, las pruebas originales cubrían 6 de forma total o parcial. Con las pruebas de auditoría se ejecutaron 22. Quedaron sin ejecutar: "persistencia tras cerrar la aplicación real" (cubierta solo a nivel de engine) y "restauración con la aplicación abierta en varias pestañas".

---

## 13. Hallazgos clasificados por prioridad

Leyenda de verificación: **COMPROBADO** = reproducido por ejecución; **CÓDIGO** = evidente por inspección, sin ejecutar; **RIESGO** = potencial, depende del uso.

### CRÍTICOS

#### C-01 · Restauración sin validación destruye la base de datos
- **Verificación:** COMPROBADO (H01, H02)
- **Archivos:** `app.py:16-25`; `modules/backup.py:58-80`
- **Problema:** el archivo elegido o subido se copia sobre `data/financiera.db` sin validar que sea SQLite, que esté íntegro ni que tenga el esquema de la aplicación. No se respalda la BD actual antes de sobrescribirla. La copia no tiene manejo de errores.
- **Evidencia:**
  ```python
  origen = st.session_state.pop("pending_restore")
  dispose_engine()
  shutil.copy2(origen, DB_PATH)
  st.session_state["db_inicializada"] = False
  st.success("Base de datos restaurada correctamente.")
  ```
- **Escenario:** se sube un `.db` dañado, de otra aplicación o vacío y se confirma.
- **Consecuencia:** pérdida total e irreversible de los datos. Con un archivo corrupto la aplicación no vuelve a arrancar. Con una SQLite ajena se muestra "restaurada correctamente" y la empresa desaparece.
- **Solución:**
  1. Validar el archivo en una copia temporal: encabezado `SQLite format 3\0`, `PRAGMA integrity_check == 'ok'`, tablas y columnas esperadas, exactamente una fila en `company`.
  2. Crear siempre una copia automática `financiera_pre_restauracion_<ts>.db` con `sqlite3.Connection.backup`.
  3. Restaurar con la API de respaldo o con reemplazo atómico (`os.replace`) dentro de try/except y revertir ante cualquier error.
  4. Mostrar un resumen (empresa, ejercicios, cantidad de registros) antes de confirmar.
- **Prueba de verificación:** H01 y H02 deben aprobar. Agregar una prueba que restaure una copia válida y verifique que existe la copia previa.

#### C-02 · La vista previa de la importación Excel modifica la BD; cancelar no revierte
- **Verificación:** COMPROBADO (D01, D02)
- **Archivos:** `modules/excel_import.py:159-172` (línea 164), `:200-203`; causa raíz en `app.py:44`
- **Evidencia:**
  ```python
  periodo_existente = get_or_create_fiscal_period(session, fila.periodo)[0]   # durante la vista previa
  ```
  `get_or_create_fiscal_period` hace `session.add` + `flush` + `log_change`, y el `session_scope` de `app.py` hace commit al terminar la página. El botón "Cancelar" solo hace `return`.
- **Escenario:** se sube un archivo con el período 2024 y no se confirma, o se pulsa Cancelar. El ejercicio 2024 y su registro en el historial quedan guardados.
- **Consecuencia:** ejercicios basura permanentes que no se pueden borrar (M-05). Pueden aparecer como "ejercicio anterior" en DuPont (A-01, A-02). Combinado con D06, un archivo con "21" en lugar de "2021" crea el ejercicio 21.
- **Solución:** en la vista previa, usar solo `get_fiscal_period` (lectura) y marcar las filas "creará ejercicio N". Crear los ejercicios solo al confirmar. Además, cambiar el modelo de sesión de `app.py` (M-06) para que nada se confirme sin una acción explícita.
- **Prueba de verificación:** D01 y D02 deben aprobar; el historial no debe tener registros nuevos tras la vista previa.

#### C-03 · Reclasificar una cuenta con movimientos altera retroactivamente los estados históricos
- **Verificación:** COMPROBADO (B01, B02, B03)
- **Archivos:** `database/repositories.py:229-250` (`update_account`); `modules/accounts.py:152-169`
- **Evidencia:** `update_account` solo valida que la nueva clasificación sea coherente; no consulta `account_has_movements`. Los cálculos filtran por la clasificación **actual** de la cuenta (`balance_sheet.py:68-74`, `income_statement.py:75-82`).
- **Escenarios y resultados:**
  - Efectivo (ACTIVO, 500 en 2021) pasa a INGRESOS: el activo de 2021 baja de 500 a 0 y los ingresos de 2021 quedan en 0. **El importe desaparece de ambos estados**, porque sigue en `balance_entry` y el ER solo lee `income_entry`.
  - "Otros ingresos operativos" cambia su efecto a GASTO: la utilidad neta de 2021 pasa de 1.100 a 900.
  - Inventarios pasa de CORRIENTE a NO_CORRIENTE: el activo corriente de 2021 pasa de 400 a 0.
- **Consecuencia:** resultados históricos (2021–2025) alterados sin advertencia, con efecto en razones, análisis vertical y DuPont. El historial solo registra el cambio de la cuenta, no el efecto sobre los estados.
- **Solución:** ver la sección 4 (bloquear, reclasificación explícita con vigencia, o clasificación versionada). Como mínimo, prohibir el cambio de categoría principal entre Balance y Resultados cuando existan movimientos.
- **Prueba de verificación:** B01–B03 deben aprobar (cambio bloqueado o sin efecto en ejercicios previos a la vigencia).

### ALTOS

#### A-01 · DuPont toma saldos iniciales de un ejercicio no consecutivo sin advertencia
- **Verificación:** COMPROBADO (A01)
- **Archivos:** `database/repositories.py:117-126`; `calculations/dupont.py:70-79`; `modules/data_entry.py:151-159`
- **Evidencia:** `.where(FiscalPeriod.anio < anio).order_by(FiscalPeriod.anio.desc())`, con docstring "Soporta huecos: si no existe anio-1 pero existe anio-3, se devuelve ese".
- **Escenario:** existen 2021 y 2023, sin 2022. El activo inicial de 2023 es el activo final de 2021, la fuente dice "Balance final del ejercicio 2021" y `aproximado=False`.
- **Consecuencia:** promedios y ROE incorrectos presentados como exactos. Viola la regla obligatoria del encargo.
- **Solución:** buscar exactamente `anio - 1`. Si no existe, o no tiene balance **completo**, usar los saldos iniciales manuales completos. Si tampoco los hay, usar la aproximación marcada, indicando el motivo en la fuente.
- **Prueba:** A01 debe aprobar. Agregar casos para "anio−1 existe sin datos" y "anio−1 incompleto".

#### A-02 · DuPont acepta como saldo inicial real un ejercicio guardado en ceros o saldos manuales parciales
- **Verificación:** COMPROBADO (A03, A04)
- **Archivos:** `calculations/dupont.py:49-64` y `:72-79`
- **Evidencia:** `if bs_anterior.tiene_datos:` es verdadero con un solo registro, aunque sea 0. `_saldos_iniciales_desde_tabla` devuelve `(0, patrimonio)` si solo se capturó patrimonio.
- **Escenarios:**
  - 2022 guardado en ceros (A-03) y 2023 con datos: activo inicial 0, promedio a la mitad, **ROE 40% en lugar de 20%**.
  - Saldo inicial manual solo de patrimonio: activo inicial 0 y **rotación 2,00 en lugar de 1,00**.
- **Consecuencia:** ROE y rotación duplicados, presentados como exactos.
- **Solución:** exigir que el saldo inicial tenga activo total > 0 y patrimonio capturado (y, idealmente, que el balance anterior cuadre). Si no, tratarlo como insuficiente y pasar a la aproximación marcada.
- **Prueba:** A03 y A04 deben aprobar.

#### A-03 · El formulario de captura guarda 0.00 en todas las cuentas
- **Verificación:** COMPROBADO (I01; la BD real tiene 19 registros en 0.00 para 2021)
- **Archivo:** `modules/data_entry.py:80-104`
- **Evidencia:** `for account_id, valor in nuevos_valores.items(): upsert_entry(...)` recorre todas las cuentas activas, cada una con valor por defecto 0.00.
- **Escenario:** el usuario abre la captura de 2022 y pulsa "Guardar" sin completar, o solo completa algunas cuentas.
- **Consecuencia:** se pierde la distinción entre "sin dato" y "cero". El reporte muestra un balance vacío que **cuadra** (0 = 0). Esos ceros alimentan A-02. El historial se llena de registros "CREAR 0.00".
- **Solución:** campos opcionales (vacío = sin registro); guardar solo los valores informados o modificados; ofrecer un borrado explícito de cuentas (M-05).
- **Prueba:** I01 debe aprobar.

#### A-04 · El ROE con patrimonio promedio negativo se presenta como válido y la interpretación es engañosa
- **Verificación:** COMPROBADO (A02)
- **Archivo:** `calculations/dupont.py:160-165` y `:213-217`
- **Escenario:** pérdida de 100 con patrimonio −200: **ROE +50%** y multiplicador −5,00. El texto automático dice que un mayor multiplicador significa más financiamiento con deuda.
- **Consecuencia:** una empresa con pérdidas y patrimonio negativo aparece con rentabilidad positiva.
- **Solución:** si el patrimonio inicial, final o promedio es ≤ 0, marcar el ROE como "no interpretable", mostrar una advertencia explícita y omitir la interpretación de los factores.
- **Prueba:** A02 debe aprobar.

#### A-05 · No se validan ni explican los signos: correctoras positivas y costos negativos distorsionan los estados
- **Verificación:** COMPROBADO (F01, F03). Que el usuario capture de esa forma es un RIESGO.
- **Archivos:** `calculations/balance_sheet.py:60-62`; `calculations/income_statement.py:84-123`; `modules/data_entry.py:90-98`; `modules/excel_import.py:97-100`; `database/enums.py:3-7` (naturaleza ignorada)
- **Escenario:** depreciación acumulada de 300 en positivo → ANC = 1.300 en vez de 700. Costo de ventas (600) en negativo, como suele aparecer en los estados publicados → UB = 1.600 en vez de 400.
- **Consecuencia:** activos, utilidades, márgenes, vertical y ROE sobrestimados.
- **Solución:** documentar la convención en la captura y en la plantilla Excel. Validar con `naturaleza_saldo` (por ejemplo, una cuenta ACREEDORA dentro de ACTIVO debe ser ≤ 0; una cuenta de COSTOS o GASTOS debe ser ≥ 0) con un error, o con una advertencia que requiera confirmación.
- **Prueba:** F01 y F03 deben aprobar (rechazo o advertencia); F02 debe seguir aprobando.

#### A-06 · El Excel de Balance y de Resultados contiene referencias circulares cuando un grupo está vacío
- **Verificación:** COMPROBADO (G01, G02)
- **Archivo:** `reports/excel_export.py:32-33` (`return fila, fila` para grupos vacíos) y su uso en `:77`, `:88`, `:98-103`, `:140-165`
- **Evidencia (G01):** `C12 '=C10+C12'` (TOTAL ACTIVO), `C20 '=C18+C20'`, `C28 '=C26+C28+C28+C28+C28'`. En G02: `C22 '=C20-C22'` (UTILIDAD NETA sin ISR).
- **Escenario:** cualquier ejercicio sin cuentas en algún grupo, por ejemplo uno importado desde Excel solo con las cuentas usadas: sin activo no corriente, sin "Otras patrimoniales" o sin ISR.
- **Consecuencia:** Excel muestra una advertencia de referencia circular y totales en 0 o erróneos. El archivo entregado no coincide con la pantalla ni con el PDF.
- **Solución:** devolver `None` como fila de subtotal para los grupos vacíos y excluirlos de las fórmulas, o escribir los totales calculados por `calculations/` con la fórmula solo como respaldo. Añadir una celda de control que compare ambos.
- **Prueba:** G01 y G02 deben aprobar. Recalcular con LibreOffice en modo headless y comparar contra `compute_*`.

#### A-07 · Valores vacíos o NaN no validados: importación y edición terminan en `IntegrityError` no controlado
- **Verificación:** COMPROBADO (D03, D04, I02)
- **Archivos:** `modules/excel_import.py:97-100` y `:205-215`; `modules/data_edit.py:57-67`
- **Evidencia:** `Decimal(str(nan))` no lanza excepción (da `Decimal('NaN')`), así que la fila queda en estado OK. Al confirmar: `IntegrityError: NOT NULL constraint failed: balance_entry.valor`. En la edición, `round(float(nan), 2) != original` lleva al mismo error.
- **Consecuencia:** una sola celda vacía aborta toda la importación con una traza técnica; el usuario no sabe qué fila falló. En la edición se pierden todos los cambios de la pantalla.
- **Solución:** `parse_importe` común (sección 8) que rechace NaN e infinitos con estado `VALOR_VACIO`; try/except alrededor de los commits con un mensaje legible.
- **Prueba:** D03, D04 e I02 deben aprobar.

#### A-08 · El historial no permite reconstruir qué cambió, en qué ejercicio ni en qué cuenta
- **Verificación:** COMPROBADO (C01) y CÓDIGO
- **Archivos:** `database/models.py:233-245`; `database/repositories.py:309`, `:311`, `:351`; `modules/data_edit.py:101-105`; `modules/history.py`
- **Evidencia:**
  - En CREAR se registra `registro_id = account_id` (`repositories.py:309`); en EDITAR, `registro_id = existente.id` (`:311`). La prueba muestra `entry.id=1`, `account.id=2` y `registro_id=2`.
  - `ChangeHistory` no tiene ejercicio ni cuenta.
  - La pestaña "Historial de este ejercicio" llama a `list_history(tabla_afectada=...)` **sin filtrar por ejercicio**.
- **Consecuencia:** la pista de auditoría no sirve para el requisito "identificar ejercicio, cuenta, fecha y tipo de modificación". El mismo `registro_id` mezcla dos espacios de identificadores.
- **Solución:** agregar `fiscal_period_id` y `account_id` (nullable, sin FK o con SET NULL) a `change_history`; registrar siempre el id real del registro; filtrar por ejercicio en `data_edit`; mostrar año, código y nombre de cuenta en `history.py`. Opcionalmente, añadir un identificador de lote por guardado o importación.
- **Prueba:** C01 debe aprobar; filtrar el historial de 2022 no debe mostrar registros de 2021.

### MEDIOS

| ID | Verif. | Archivo / sección | Problema y evidencia | Consecuencia | Solución | Prueba |
|---|---|---|---|---|---|---|
| M-01 | COMPROBADO (D05, D06) | `excel_import.py:91-95` | `int(periodo_raw)` trunca 2021.9 a 2021 y acepta 21 | Datos en un ejercicio equivocado; ejercicios absurdos | Exigir un entero exacto dentro de un rango (p. ej. 1990–2100) o dentro de los ejercicios existentes | D05, D06 |
| M-02 | COMPROBADO (D07, I03) | `models.py:34`; `excel_import.py:98`; persistencia | Importes sin cuantizar; SQLite almacena REAL | Riesgo de diferencias de centavos con importes muy grandes; reimportar el mismo valor no cuantizado puede registrar EDITAR repetidos (no verificado) | Criterio uniforme de la sección 8 | D07, I03, E01 |
| M-03 | COMPROBADO (F06, F07) y CÓDIGO | `vertical_analysis.py:47-52`, `:70-84`; `vertical_report.py` | Vertical sin subtotales ni utilidades ni línea de ingresos; sin PDF | Análisis vertical incompleto para el trabajo académico | Incluir filas de subtotal y utilidades con su %; exportar a PDF | F06, F07 |
| M-04 | COMPROBADO (F08) | `balance_sheet.py:94`, `income_statement.py:126`; todos los reportes | No existe noción de estado completo; las cuentas faltantes cuentan como 0 | Reportes de estados parciales presentados como definitivos | Agregar `cuentas_sin_dato` y `completo` al resultado y mostrar "INCOMPLETO" en pantalla, PDF y Excel | F08 |
| M-05 | CÓDIGO | `enums.py:106-108`; `repositories.py:315` sin uso; `navigation.py:54-63` | No hay cierre de ejercicio (CERRADO sin uso), REVISADO no bloquea la edición, no se pueden borrar importes ni ejercicios | Ejercicios de 2021–2025 ya revisados siguen editables; la basura de C-02 es permanente | Implementar cierre (bloquea captura, edición e importación), borrar importes con historial y borrar ejercicios vacíos | Nuevas: editar un ejercicio cerrado → rechazado |
| M-06 | CÓDIGO (causa de C-02) | `app.py:44-113` | Una sesión con commit implícito por página | Cualquier efecto secundario de lectura se persiste | Sesión de solo lectura para render (`autoflush=False` y rollback al final) y transacciones explícitas en las acciones | D01, D02 |
| M-07 | CÓDIGO | `data_entry.py:116-123`; `balance_sheet.py` | No se concilia "Resultado del ejercicio" (patrimonio) contra la utilidad neta del ER | Inconsistencias entre estados sin detectar | Control de conciliación con la diferencia mostrada en ambos reportes | Nueva |
| M-08 | CÓDIGO | `dashboard.py:42` | El ROE del Dashboard no indica si es aproximado ni la fuente del saldo inicial | El usuario toma un ROE aproximado como exacto | Mostrar un indicador o advertencia junto a la métrica | Inspección UI |
| M-09 | CÓDIGO | `connection.py:46`; `backup.py:38-44` | (a) Sin migraciones: `create_all` no altera tablas existentes. (b) La copia usa `shutil.copy2` sobre el archivo vivo, sin API de respaldo ni `integrity_check` | (a) Las correcciones de esquema (A-08, M-05) no llegarán a BD existentes. (b) Copias potencialmente inconsistentes | (a) Alembic o un control `PRAGMA user_version`. (b) `sqlite3.backup` + verificación | Prueba de migración sobre una copia de la BD real |
| M-10 | CÓDIGO / RIESGO | `streamlit_run.log`; ausencia de `.streamlit/config.toml`; `data_entry.py`, `data_edit.py` | El servidor escuchó en todas las interfaces (el log muestra "Network URL" y "External URL: 168.243.189.202") sin autenticación. La captura y la edición no piden confirmación | Cualquiera en la red podría ver, editar o **restaurar** la BD | `server.address = "localhost"` en `.streamlit/config.toml`; confirmación antes de guardar cambios masivos | Verificar que el servidor solo escuche en 127.0.0.1 |

### BAJOS

| ID | Verif. | Archivo | Problema | Solución |
|---|---|---|---|---|
| B-01 | COMPROBADO (A06) | `dupont.py:154-155`, `:188-190` | Promedios redondeados antes de dividir; los factores se devuelven redondeados; su producto (11,04%) no reproduce el ROE mostrado (11,07%) | Conservar sin redondear y mostrar 4 decimales en los factores, o una nota de redondeo |
| B-02 | CÓDIGO | `dupont.py:175`; `dupont_report.py:43-46` | La "coincidencia" DuPont frente al ROE directo es tautológica | Sustituir por controles útiles (cuadre del balance, conciliación UN–patrimonio, completitud) |
| B-03 | CÓDIGO | `excel_export.py` | Subtotales como fórmulas sin valor en caché; base del vertical como texto; el DuPont en Excel no tiene una marca "APROXIMADO" separada | Escribir valores calculados (y la fórmula en una columna de control); bandera explícita |
| B-04 | CÓDIGO | `components/tables.py:23,30`; `app.py:41` | `unsafe_allow_html` con `company.moneda` (dato del usuario) interpolado | Escapar con `html.escape` o usar componentes nativos. Riesgo bajo en uso local |
| B-05 | RIESGO | `requirements.txt` | Mínimo `streamlit>=1.38`, pero se usa `width="stretch"` (API reciente); no verificado con 1.38 | Subir el mínimo a la versión probada o fijar versiones (lockfile) |
| B-06 | COMPROBADO (D08) | `excel_import.py:75` | El código 1001.0 (columna numérica con celdas vacías) se trata como cuenta desconocida | Normalizar códigos numéricos enteros |
| B-07 | COMPROBADO (BD real) | `data/financiera.db`, tabla `company` | Datos con errores tipográficos ("aluetch sv", "El Salvaodr", "alutech") | Corregir desde "Datos de la empresa" antes de generar reportes |
| B-08 | COMPROBADO (E03) | `data_entry.py:54-55`; `data_edit.py:59-64` | `round(float)` usa redondeo bancario binario (2.675 → 2.67) | `Decimal(str(x)).quantize(..., ROUND_HALF_UP)` |
| B-09 | CÓDIGO | `README.md:66-73` | El README afirma que las pruebas cubren "los 18 casos requeridos"; no cubren los escenarios en los que se encontraron 30 defectos | Actualizar la documentación tras la fase 5 |

Otras observaciones sin hallazgo:
- La importación no contrasta el nombre del archivo con el del catálogo (solo usa el código).
- "Configuración" duplica "Datos de la empresa".
- Quedan en la raíz los archivos `streamlit_run.*` de la última ejecución.

---

## 14. Limitaciones de la auditoría

1. **Sin datos de Alutech.** La BD solo tiene 2021 con ceros y `documentos/` no contiene sus estados. No se conciliaron los reportes contra cifras reales 2021–2025 ni se validó la adecuación del catálogo de 30 cuentas a la estructura consolidada de Alutech (por ejemplo, interés minoritario). **Información necesaria:** estados financieros de Alutech, División Acero, 2021–2025 (y el balance de 2020 para el saldo inicial de DuPont 2021), con sus notas.
2. **Interfaz no navegada manualmente.** No se levantó el servidor ni se usó un navegador. La sección 11 se basa en el código. Los flujos de importación, edición y restauración se ejecutaron con el código real, simulando solo los widgets indicados en 12.3.
3. **Restauración con varias sesiones abiertas en Windows** (bloqueo de archivo): no verificada.
4. **Apertura de los Excel en Microsoft Excel o LibreOffice:** las referencias circulares se verificaron leyendo las fórmulas con openpyxl, no abriendo el archivo en una hoja de cálculo.
5. **Revisión visual de los PDF:** solo se verificó que se generan (`%PDF`), no su maquetación.
6. **Compatibilidad con las versiones mínimas declaradas** (p. ej. Streamlit 1.38): no verificada; solo con las versiones instaladas.
7. `documentos/libro adm financ.pdf` (libro de texto) no se analizó.

---

## 15. Conclusión técnica y financiera

**Técnica:** la estructura por capas, el uso de `Decimal`, las restricciones de integridad referencial y la ausencia de subtotales almacenados son una buena base. Los defectos se concentran en tres áreas:
- Los **límites de la transacción** (la vista previa persiste datos).
- La **protección de datos** (restauración sin validación; catálogo mutable con efecto retroactivo).
- La **validación de entradas** (NaN, signos, períodos).

Todos se pueden corregir sin rediseñar la aplicación siguiendo el orden de `PLAN_DE_CORRECCION.md`.

**Financiera:** con datos limpios, completos, consecutivos y con signos correctos, las fórmulas del Balance General, el Estado de Resultados, el análisis vertical (por cuenta) y DuPont dan resultados matemáticamente correctos. Sin embargo, la aplicación **no detecta ni advierte** las condiciones habituales que invalidan esos resultados: ejercicios faltantes o en ceros, saldos parciales, signos invertidos, patrimonio negativo y reclasificaciones. En esas condiciones presenta cifras erróneas como exactas. Además, el análisis vertical omite los subtotales y márgenes que exige el análisis académico, y el Excel exportado puede contener referencias circulares.

**Dictamen:** **no apta todavía** para producir la información de 2021–2025 del trabajo académico. Se recomienda completar al menos las fases 1 y 2 del plan, cargar los datos de Alutech y conciliarlos contra los estados publicados antes de usar sus reportes.

*No se implementó ninguna corrección. Se espera autorización.*
