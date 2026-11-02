# Matriz de pruebas

**Fecha de ejecución:** 2026-11-01 · **Entorno:** Windows 11, Python 3.12.10 (`.venv`), pytest 8.4.2, Streamlit 1.66.1, SQLAlchemy 2.0.55
**Base de datos:** todas las pruebas usan SQLite temporales. El hash de `data/financiera.db` fue el mismo antes y después (`f026863d…630a82d`).

## Estado tras la corrección de B-10 (2026-11-01)

Comando: `.venv\Scripts\python -m pytest tests/ -q` → **382 aprobadas, 2 fallidas** (384 pruebas). Las únicas fallidas siguen siendo F01 y F03 (por diseño). Hash de `data/financiera.db` igual antes y después (`c69020b6…ee10ac`).

| Conjunto | Ejecutadas | Aprobadas | Fallidas |
|---|---|---|---|
| Originales | 30 | 30 | 0 |
| Auditoría | 47 | 45 | 2 (F01, F03) |
| Fase 1 + M-11 (incluye las 16 páginas) | 132 | 132 | 0 |
| Fase 2 | 47 | 47 | 0 |
| Fase 3 | 17 | 17 | 0 |
| Fase 4 | 77 | 77 | 0 |
| B-10 (`tests/test_b10.py`) | 34 | 34 | 0 |

`tests/test_b10.py` cubre:
- 15 textos guardados y releídos con openpyxl: 8 con signo de fórmula (`=`, `+`, `-`, `@`, `=HYPERLINK(...)`, `=cmd|...`, tabulador y retorno de carro iniciales) y 7 especiales (espacios exteriores, salto de línea, `Ñandú & <b>€</b> 'x' "y"`, vacío, "1001", "-", "="): mismo valor, tipo `s`, `quotePrefix` solo en los peligrosos y sin `<f>` en el XML.
- Caracteres de control no admitidos (se eliminan), números y vacíos sin cambios, `formula()` rechaza lo que no es fórmula, `agregar_fila`.
- Los 4 reportes (y el vertical en formato anterior) con empresa y 6 cuentas de nombre peligroso o especial: cada texto del usuario es una celda de tipo `s`; toda fórmula está en las columnas D–F y tiene la forma de una fórmula de control; fórmulas y números idénticos a los del mismo reporte con nombres normales; importes del Balance (300, 1.000 y 400).
- XML de cada hoja: ningún `<f>` contiene datos del usuario.
- Plantilla de importación: nombres como texto, ninguna fórmula, y se sigue leyendo con los mismos nombres.

Comprobaciones adicionales: las 14 pruebas de reportes fallan con el código anterior; con datos normales, los 6 libros generados son idénticos celda por celda a los del código anterior (58 fórmulas de control).

## Estado tras la fase 4 (2026-11-01)

Comando: `.venv\Scripts\python -m pytest tests/ -q` → **348 aprobadas, 2 fallidas** (350 pruebas). Mismo resultado en un entorno limpio instalado solo con `pip install -r requirements.txt` (su `pip freeze` es idéntico al de `.venv`). Hash de `data/financiera.db` igual antes y después de la suite (`c69020b6…ee10ac`, el de después de B-07).

| Conjunto | Ejecutadas | Aprobadas | Fallidas | Fallidas (motivo) |
|---|---|---|---|---|
| Originales | 30 | 30 | 0 | — |
| Auditoría | 47 | 45 | 2 | F01 y F03 (por diseño: contradicen la convención de signos aprobada) |
| Fase 1 + M-11 | 132 | 132 | 0 | — (incluye las 16 páginas con `AppTest`) |
| Fase 2 | 47 | 47 | 0 | — |
| Fase 3 | 17 | 17 | 0 | — |
| Fase 4 (`tests/test_fase4.py`) | 77 | 77 | 0 | — |

La prueba de auditoría de la fase 4 pasó de FALLIDO a APROBADO: D08.

`tests/test_fase4.py` cubre:
- **B-04:** `md()` con 18 entradas (HTML, `<script>`, Markdown, `:red[]`, `$LaTeX$`, entidades, enlaces `javascript:`); análisis del código fuente: el único `unsafe_allow_html` es el CSS de `app.py` y solo interpola la constante `PRIMARY`; subtotales y totales nativos y alineados a la derecha; PDF con 4 monedas maliciosas (con `<x` fallaba); el `app.py` real con `AppTest` y una empresa con nombre malicioso (se muestra literal, solo el CSS lleva HTML).
- **B-05:** las 8 versiones fijadas son las instaladas; `requirements.txt` cubre todas las librerías de terceros importadas; las APIs de Streamlit usadas existen.
- **B-06:** 15 casos de normalización, 9 de códigos ambiguos, los 30 códigos del catálogo sin cambios, ceros a la izquierda, texto "1003.0", duplicado en dos formatos e importación real de un Excel con columna numérica y fila vacía.
- **B-07:** la BD de trabajo (solo lectura) tiene los datos corregidos, la evidencia en el historial y los 19 ceros de 2021; el encabezado del Excel y del PDF muestra "Alutech" (sobre una copia).
- **D08 (confirmaciones):** proponer no escribe; cancelar, recargar (sesión nueva), navegar y repetir el clic no modifican la BD (comparación de las tablas o del SHA-256); confirmar escribe exactamente lo propuesto en un lote; datos cambiados entre la vista previa y la confirmación → no escribe; fallo a mitad → nada guardado; saldos iniciales y edición también confirman; la edición cambiada después de proponer se descarta; la importación muestra el alcance, no se repite y no importa si la BD cambió tras la vista previa.

Pruebas existentes adaptadas (solo la acción simulada del usuario, no lo que se comprueba): `tests/test_fase1_integridad.py::_capturar` y `tests/test_fase2.py` (`_capturar_formulario` y la edición con signo atípico) pulsan también "Confirmar y guardar", porque guardar ahora tiene dos pasos. `tests/conftest.py` vacía `st.session_state` en cada prueba (sin servidor es global del proceso).

Las pruebas nuevas se ejecutaron también contra el código anterior (HEAD `2899301`, con solo los dos módulos nuevos añadidos para poder importarlas): 43 fallidas y 2 errores, es decir, detectan los defectos.

Verificación de páginas con datos reales: `tests/humo_paginas.py` sobre una copia de la BD de trabajo corregida → las 16 páginas sin excepciones y la copia sin cambios.

## Estado tras la fase 3 (2026-11-01)

Comando: `.venv\Scripts\python -m pytest tests/ -q` → **270 aprobadas, 3 fallidas** (273 pruebas).

| Conjunto | Ejecutadas | Aprobadas | Fallidas | Fallidas (motivo) |
|---|---|---|---|---|
| Originales | 30 | 30 | 0 | — (T-15 resuelto con autorización: comparación al redondeo de presentación) |
| Auditoría | 47 | 44 | 3 | F01 y F03 (por diseño: contradicen la convención de signos aprobada); D08 (fase 4) |
| Fase 1 + M-11 | 132 | 132 | 0 | — |
| Fase 2 | 47 | 47 | 0 | — |
| Fase 3 (`tests/test_fase3.py`) | 17 | 17 | 0 | — |

Las 4 pruebas de auditoría que corresponden a la fase 3 pasaron de FALLIDO a APROBADO: F06, F07, G01 y G02.

`tests/test_fase3.py` cubre:
- Excel: fórmulas de control evaluadas y comparadas con Python, ausencia de referencias circulares, columna C sin fórmulas, lectura sin recálculo, banderas iguales a las de pantalla, base vertical numérica (también en el formato anterior con `df`), DuPont aproximado y no interpretable.
- Análisis vertical: subtotales, totales y utilidades del Balance y de Resultados, márgenes coherentes, grupos vacíos ("Sin datos") y base cero.
- PDF: banderas, nombre de cuenta largo sin cortar, vertical y DuPont.
- Dashboard: ROE definitivo, aproximado con causa, no interpretable, e indicadores incompletos etiquetados.

Verificaciones no ejecutadas:
- **N-04:** LibreOffice no está instalado. Se sustituye por el evaluador propio de fórmulas; abrir los archivos en una hoja de cálculo sigue pendiente.
- **N-05:** cubierta. Se revisaron visualmente 8 PDF con datos sintéticos; aún no con datos de Alutech.

## Estado tras la fase 2 (2026-11-01)

Comando: `.venv\Scripts\python -m pytest tests/ -q` → **248 aprobadas, 8 fallidas** (256 pruebas).

| Conjunto | Ejecutadas | Aprobadas | Fallidas | Fallidas (motivo) |
|---|---|---|---|---|
| Originales | 30 | 29 | 1 | T-15: conflicto con B-01, decisión pendiente (ver `PLAN_DE_CORRECCION.md`) |
| Auditoría | 47 | 40 | 7 | F01 y F03 (por diseño); F06, F07, G01 y G02 (fase 3); D08 (fase 4) |
| Fase 1 + M-11 | 132 | 132 | 0 | — |
| Fase 2 (`tests/test_fase2.py`) | 47 | 47 | 0 | — |

Las 6 pruebas de auditoría que corresponden a la fase 2 pasaron de FALLIDO a APROBADO: A01, A02, A03, A04, A06 y F08.

`tests/test_fase2.py` cubre:
- Saldos iniciales: N-1 completo; ejercicio inexistente, incompleto, descuadrado y en ceros (siempre aproximado y con la causa); saldos manuales completos y parciales.
- Patrimonio inicial, final o promedio ≤ 0: ROE no interpretable, también en el reporte de pantalla. Pérdida con patrimonio positivo: sigue siendo válida.
- Precisión: promedios y factores sin redondeo intermedio; los factores con 4 decimales reproducen el ROE en 3 casos.
- Los 7 controles del DuPont.
- Completitud: ausencia frente a cero explícito.
- Signos: 14 casos de la convención; el importe no se invierte; la captura, la edición y la importación exigen confirmación; la plantilla documenta la convención.
- Conciliación: conciliado, diferencia real, diferencia por datos faltantes y sin datos.

## Estado tras la corrección de M-11 (2026-11-01)

Comando: `.venv\Scripts\python -m pytest tests/ -q` → **196 aprobadas, 13 fallidas** (209 pruebas).

| Conjunto | Ejecutadas | Aprobadas | Fallidas |
|---|---|---|---|
| Originales | 30 | 30 | 0 |
| Auditoría | 47 | 34 | 13 (las mismas de fases 2–4) |
| Fase 1 (123 + 2 comprobaciones del contenido de las páginas verticales) | 125 | 125 | 0 |
| M-11 (`tests/test_m11_vertical.py`) | 7 | 7 | 0 |

`tests/test_m11_vertical.py` cubre:
- El análisis vertical del Balance y del Estado de Resultados con importes positivos, negativos (depreciación, patrimonio, ISR) y cero.
- Un ejercicio sin datos.
- Base igual a cero (porcentaje `None`).
- Redondeo HALF_UP (0.125 → 0.13).
- La tabla de pantalla formateada desde `Decimal`, incluido "No disponible".
- Que los centavos almacenados no cambian al calcular ni al presentar.

Las 2 páginas verticales, que antes fallaban por M-11, ahora aprueban en `tests/test_fase1_paginas.py`, y también se comprueban los importes y porcentajes que muestran.

## Estado tras la fase 1 (2026-11-01)

Comando: `.venv\Scripts\python -m pytest tests/ -q` → **185 aprobadas, 15 fallidas** (200 pruebas).

| Conjunto | Ejecutadas | Aprobadas | Fallidas | Fallidas (motivo) |
|---|---|---|---|---|
| Originales (6 archivos) | 30 | 30 | 0 | — |
| Auditoría (`tests/test_auditoria.py`) | 47 | 34 | 13 | A01–A04, A06, F01, F03, F08 (fase 2); F06, F07, G01, G02 (fase 3); D08 (fase 4) |
| Nuevas de la fase 1 | 123 | 121 | 2 | Páginas de análisis vertical: hallazgo nuevo M-11, preexistente (fase 3) |

Las 17 pruebas de auditoría que corresponden a la fase 1 pasaron de FALLIDO a APROBADO: B01–B03, C01, D01–D07, E03, H01, H02, I01–I03.

Pruebas nuevas de la fase 1:

| Archivo | Pruebas | Cubre |
|---|---|---|
| `tests/test_fase1_money.py` | 50 | `parse_importe` (vacío, NaN, ±inf, comas, >2 decimales, HALF_UP con aviso, rango NUMERIC(18,2), floats de más de 15 dígitos, numpy) y `parse_anio` |
| `tests/test_fase1_migracion.py` | 12 | Migración v0 → v3 sin pérdida (comparación fila por fila), conservación de 19 ceros, copia previa íntegra, idempotencia, mismo esquema que una BD nueva, detención ante importes ambiguos con BD intacta (mismo SHA-256), historial heredado sin reescribir, esquema futuro rechazado |
| `tests/test_fase1_restauracion.py` | 17 | Copia con API SQLite, inspección, 7 tipos de archivo inválido, restauración válida con copia previa de mismo SHA-256, restauración de copias v0, reemplazo bloqueado (simulado y bloqueo real de Windows), diario pendiente, reversión tras fallo posterior |
| `tests/test_fase1_integridad.py` | 27 | `render_scope` sin commit, `ejecutar_escritura`, catálogo protegido, cierre/reapertura (repositorio y disparadores), eliminación de ejercicios vacíos, borrado de importes, historial (id real, ejercicio, cuenta, lote, filtros), captura sin ceros implícitos, edición e importación en ejercicio cerrado, importación todo-o-nada, ruido binario frente a tercer decimal |
| `tests/test_fase1_paginas.py` | 17 | Las 16 páginas del `app.py` real con `AppTest` (en subproceso) sin excepciones y sin modificar la BD |

Verificaciones no ejecutadas: siguen pendientes N-01, N-04, N-05, N-06 y N-07. N-02 está cubierta en parte (las 16 páginas se renderizan con `AppTest`, sin navegador). En N-03 se verificó el bloqueo de archivo con otra conexión abierta, no con dos pestañas reales. N-08: el servidor escucha solo en 127.0.0.1 (fase 0), sin prueba desde un segundo equipo.

---

## Resumen (auditoría original)

| Conjunto | Ejecutadas | Aprobadas | Fallidas | No ejecutadas |
|---|---|---|---|---|
| Pruebas originales (`tests/`) | 30 | 30 | 0 | — |
| Pruebas de verificación de la auditoría (`test_auditoria.py`) | 47 | 17 | 30 | — |
| Verificaciones manuales o de entorno | — | — | — | 8 |
| **Total** | **77** | **47** | **30** | **8** |

**Cómo leer el estado:** las pruebas de auditoría afirman el **comportamiento correcto esperado**. FALLIDO significa que el defecto está confirmado. APROBADO significa que el comportamiento es correcto en ese escenario, lo que no prueba que la fórmula sea correcta en general.

**Ubicación de las pruebas de auditoría:** `C:\Users\estua\AppData\Local\Temp\claude\c--Users-estua-Documents-ANF-appfinanciera\9682c29f-24d7-41f1-98d9-8fdb842605d9\scratchpad\audit_tests\test_auditoria.py` (temporal; se propone moverlas a `tests/` en la fase 0 del plan).
**Comando:** `cd <carpeta> && <proyecto>\.venv\Scripts\python -m pytest test_auditoria.py -v -s`

---

## 1. Pruebas originales del proyecto (`pytest tests/ -v`)

| ID | Módulo | Escenario | Datos de prueba | Resultado esperado | Resultado obtenido | Estado |
|---|---|---|---|---|---|---|
| T-01 | Catálogo | Registro de cuenta | Cuenta 9999 ACTIVO/CORRIENTE | Se crea con id | Creada | APROBADO |
| T-02 | Catálogo | Código duplicado | 9998 dos veces | ValueError | ValueError | APROBADO |
| T-03 | Catálogo | Modificar nombre y orden | 9997 → "Editada", orden 5 | Cambios aplicados | Aplicados | APROBADO |
| T-04 | Catálogo | Desactivar sin eliminar | 9996 | Estado INACTIVA, la cuenta existe | Correcto | APROBADO |
| T-05 | Catálogo | Detección de movimientos | 1001 con 100.00 | `True` | `True` | APROBADO |
| T-06 | BD | Enum reconstruido en una sesión nueva | 1001 | `isinstance(Cat)` | Correcto | APROBADO |
| T-07 | Ejercicios | Registro y unicidad | 2021 dos veces, 2022 | 1 creado, luego reutilizado; [2021, 2022] | Correcto | APROBADO |
| T-08 | BD | Persistencia tras cerrar y reabrir el engine | Empresa + cuenta 7777 | Recuperadas | Recuperadas | APROBADO |
| T-09 | Balance | Total activo | AC 500, ANC 500 | 1.000,00 | 1.000,00 | APROBADO |
| T-10 | Balance | Total pasivo | PC 250, PNC 150 | 400,00 | 400,00 | APROBADO |
| T-11 | Balance | Patrimonio | 500 + 100 | 600,00 | 600,00 | APROBADO |
| T-12 | Balance | Ecuación cuadra | 1.000 = 400 + 600 | `cuadra`, dif. 0 | Correcto | APROBADO |
| T-13 | Balance | Descuadre detectado | Solo activo 1.000 | Dif. 1.000, no cuadra | Correcto | APROBADO |
| T-14 | Balance | Sin datos | Ejercicio vacío | `tiene_datos=False` | Correcto | APROBADO |
| T-15 | DuPont | Factores | A 1.000, P 600, I 1.000, UN 100 | 0,10 / 1,00 / 1,67 | Correcto | APROBADO (comparación al redondeo de presentación `q2`, autorizada; antes FALLIDO por B-01) |
| T-16 | DuPont | ROE DuPont = directo | Igual | 16,67% | 16,67% | APROBADO |
| T-17 | DuPont | Encadenamiento 2021 → 2022 | Dos ejercicios consecutivos | Activo prom. 1.100; Pat. prom. 650 | Correcto | APROBADO |
| T-18 | DuPont | Sin saldo inicial → aproximación | Solo 2021 | `aproximado=True` | Correcto | APROBADO |
| T-19 | DuPont | Patrimonio promedio = 0 | A 1.000, P 1.000 | No disponible | No disponible | APROBADO |
| T-20 | Importación | Errores por fila | OK, inexistente, no numérico, duplicada | Estados correctos | Correctos | APROBADO |
| T-21 | Importación | `_validar_dataframe` no escribe | Valor existente 111 | Sigue en 111 | 111 | APROBADO |
| T-22 | PDF | Balance y ER generados | Ejercicio completo | Empiezan con `%PDF` | Correcto | APROBADO |
| T-23 | Excel | Balance, vertical y ER generados | Igual | Libros legibles | Correcto | APROBADO |
| T-24 | ER | Utilidad neta | I 1.000, CV 600, GA 150, GV 50, GF 50, ISR 50 | UB 400, UO 200, UAI 150, UN 100 | Correcto | APROBADO |
| T-25 | ER | Otros operativos ± | +30 / −10 | UO 620 | 620 | APROBADO |
| T-26 | ER | Sin datos | Vacío | `tiene_datos=False` | Correcto | APROBADO |
| T-27 | Vertical | Balance % | 300 / 700 | 30% / 70% | Correcto | APROBADO |
| T-28 | Vertical | Sin datos | Vacío | No disponible | Correcto | APROBADO |
| T-29 | Vertical | ER % | I 1.000, CV 250 | 25% | 25% | APROBADO |
| T-30 | Vertical | Ingresos = 0 | Solo CV 100 | No disponible | Correcto | APROBADO |

---

## 2. Pruebas de verificación de la auditoría

| ID | Módulo | Escenario | Datos de prueba | Resultado esperado | Resultado obtenido | Estado | Hallazgo |
|---|---|---|---|---|---|---|---|
| A01 | DuPont | Ejercicio no consecutivo | 2021 (A 1.000) y 2023 (A 2.000), sin 2022 | No usar 2021 como saldo inicial sin marcarlo | Activo inicial 1.000; fuente "Balance final del ejercicio 2021"; `aproximado=False` | APROBADO (fase 2; antes FALLIDO) | A-01 |
| A02 | DuPont | Patrimonio promedio negativo | A 1.000, P −200, UN −100 | No disponible o con advertencia | ROE **+50,00%**, mult. −5,00, sin advertencia | APROBADO (fase 2; antes FALLIDO) | A-04 |
| A03 | DuPont | Ejercicio anterior guardado en ceros | 2022 en ceros; 2023 A 2.000, P 1.000, UN 200 | Activo inicial ≠ 0 o aproximado | Activo inicial 0 → prom. 1.000 → **ROE 40%** (real 20%); `aproximado=False` | APROBADO (fase 2; antes FALLIDO) | A-02 |
| A04 | DuPont | Saldos manuales parciales | Solo patrimonio inicial 500 | Activo inicial ≠ 0 o aproximado | Activo inicial 0; **rotación 2,00** (real 1,00) | APROBADO (fase 2; antes FALLIDO) | A-02 |
| A05 | DuPont | Identidad con datos válidos | 2021 → 2022, I 1.234,56, UN 98,76 | ROE 15,19% en ambos | 15,19% = 15,19% | APROBADO | — |
| A06 | DuPont | Factores mostrados reproducen el ROE | A 3.333, P 1.111, I 7.777, UN 123 | Producto ≈ ROE ± 0,01 | 1,58% × 2,33 × 3,00 = 11,04% frente a ROE 11,07% | APROBADO (fase 2; antes FALLIDO) | B-01 |
| A07 | DuPont | Ingresos = 0 | I 0 | No disponible | No disponible | APROBADO | — |
| A08 | DuPont | Activo promedio = 0 | A 0 | No disponible | No disponible | APROBADO | — |
| A09 | DuPont | Utilidad negativa | A 1.000, P 500, UN −100 | ROE −20%, margen −10% | Correcto | APROBADO | — |
| B01 | Catálogo | Reclasificar ACTIVO → INGRESOS con saldo | 1001 = 500 en 2021 | Bloqueado o importe conservado | Activo 500 → 0; ingresos 0: **el importe desaparece** | APROBADO (fase 1; antes FALLIDO) | C-03 |
| B02 | Catálogo | Cambiar efecto INGRESO → GASTO | 6003 = 100 en 2021 | UN 2021 sin cambio | UN 1.100 → 900 | APROBADO (fase 1; antes FALLIDO) | C-03 |
| B03 | Catálogo | CORRIENTE → NO_CORRIENTE | 1003 = 400 | AC 2021 sin cambio | AC 400 → 0 | APROBADO (fase 1; antes FALLIDO) | C-03 |
| B04 | BD | Importe con ejercicio inexistente | `fiscal_period_id=999` | IntegrityError | IntegrityError | APROBADO | — |
| B05 | BD | Importe duplicado cuenta/ejercicio | 2 filas iguales | IntegrityError | IntegrityError | APROBADO | — |
| B06 | BD | Modificar 2022 no altera 2021 | 2022: 1001 = 1.500 | Activo 2021 = 1.000 | 1.000 | APROBADO | — |
| C01 | Historial | CREAR identifica registro y ejercicio | 1002 = 10 | `registro_id` = id del registro; columna de ejercicio | `registro_id=2` (id de cuenta) y entry.id=1; sin columna de ejercicio | APROBADO (fase 1; antes FALLIDO) | A-08 |
| D01 | Importación | Solo vista previa (sin confirmar) | XLSX período 2024 | No se crea 2024 | **Ejercicio 2024 creado** + 1 registro en el historial | APROBADO (fase 1; antes FALLIDO) | C-02 |
| D02 | Importación | Cancelar | XLSX período 2025 + "Cancelar" | No se crea 2025 | **Ejercicio 2025 creado** | APROBADO (fase 1; antes FALLIDO) | C-02 |
| D03 | Importación | Valor vacío | Celda vacía | Estado ≠ OK | Estado **OK**, valor `NaN` | APROBADO (fase 1; antes FALLIDO) | A-07 |
| D04 | Importación | Confirmar con valor vacío | Igual + Confirmar | Error controlado, nada guardado | **IntegrityError no controlado** (NOT NULL) | APROBADO (fase 1; antes FALLIDO) | A-07 |
| D05 | Importación | Período decimal | 2021.9 | Rechazado | OK, período 2021 | APROBADO (fase 1; antes FALLIDO) | M-01 |
| D06 | Importación | Período fuera de rango | 21 | Rechazado | OK | APROBADO (fase 1; antes FALLIDO) | M-01 |
| D07 | Importación | Más de 2 decimales | 0,1 + 0,2 | Rechazado o cuantizado | 0.30000000000000004, OK | APROBADO (fase 1; antes FALLIDO) | M-02 |
| D08 | Importación | Código numérico | 1001.0 | OK | CUENTA_DESCONOCIDA | APROBADO (fase 4; antes FALLIDO) | B-06 |
| D09 | Importación | Duplicado dentro del archivo | 1001/2021 × 2 | OK + DUPLICADA | Correcto | APROBADO | — |
| D10 | Importación | Errores parciales | 1 válida + 1 inexistente | Solo se importa la válida | {1001: 100,00} | APROBADO | — |
| D11 | Importación | Reimportar el mismo archivo | 2 veces | 1 registro | 1 | APROBADO | — |
| E01 | Precisión | Importe grande | 123.456.789.012.345,67 | Exacto tras reabrir | Exacto | APROBADO | — |
| E02 | Precisión | Importes típicos | 0,10; 0,20; 1.234.567,89; −98.765,43; 99.999.999,99 | Suma exacta | 101.135.802,75 exacto | APROBADO | — |
| E03 | Precisión | Conversión de float en la captura | 2,675 | 2,68 (HALF_UP) | 2,67 | APROBADO (fase 1; antes FALLIDO) | B-08 |
| F01 | Balance | Depreciación positiva | PPE 1.000, dep. +300 | ANC 700 o rechazo | ANC **1.300** | FALLIDO (por diseño: el signo no se invierte; se advierte y se pide confirmación) | A-05 |
| F02 | Balance | Depreciación negativa | PPE 1.000, dep. −300 | ANC 700 | 700 | APROBADO | — |
| F03 | ER | Costo capturado negativo | I 1.000, CV −600 | UB 400 o rechazo | UB **1.600** | FALLIDO (por diseño: el signo no se invierte; se advierte y se pide confirmación) | A-05 |
| F04 | ER | Estado completo (todas las categorías) | 11 cuentas | UB 4.000; UO 2.300; RF −300; OR 20; UAI 2.020; UN 1.415 | Correcto | APROBADO | — |
| F05 | Balance | Pasivo > activo, patrimonio negativo | A 100, P 300, Pat. −200 | Pat. −200, cuadra | Correcto | APROBADO | — |
| F06 | Vertical | ER incluye ingresos y utilidades | I 1.000, CV 600 | Fila 4001 y utilidades | Solo fila 5001 | APROBADO (fase 3; antes FALLIDO) | M-03 |
| F07 | Vertical | Balance incluye subtotales | AC 300, ANC 700 | Subtotales con % | Solo filas por cuenta | APROBADO (fase 3; antes FALLIDO) | M-03 |
| F08 | Balance | Ausencia frente a cero | Solo 1001 = 100 | Indicador de incompleto | No existe; pasivo = 0,00 | APROBADO (fase 2; antes FALLIDO) | M-04 |
| G01 | Excel | Balance sin grupo ANC | AC 100, PC 40, Pat. 60 | Sin circulares | `C12 =C10+C12`, `C20 =C18+C20`, `C28 =C26+C28+…` | APROBADO (fase 3; antes FALLIDO) | A-06 |
| G02 | Excel | ER sin gastos ni ISR | I 1.000, CV 600 | Sin circulares | `C18`, `C20`, `C22 =C20-C22` circulares | APROBADO (fase 3; antes FALLIDO) | A-06 |
| G03 | PDF | Nombre con "&" | "Acero & Aluminio, S. A. de C. V." | PDF válido | Válido | APROBADO | — |
| G04 | Exportación | No modifica la BD | Exportar los 4 archivos | Hash igual | Igual | APROBADO | — |
| H01 | Restauración | Archivo corrupto (`app.py` real con AppTest) | Bytes no SQLite | BD intacta | **BD sobrescrita**; `DatabaseError: file is not a database` | APROBADO (fase 1; antes FALLIDO) | C-01 |
| H02 | Restauración | SQLite ajena | BD con tabla `x` | Rechazada | "Base de datos restaurada correctamente."; **empresa = None** | APROBADO (fase 1; antes FALLIDO) | C-01 |
| I01 | Captura | Guardar el formulario sin completar | Formulario Balance 2021 | Sin registros fantasma | 19 registros 0,00; "tiene datos" y "cuadra" | APROBADO (fase 1; antes FALLIDO) | A-03 |
| I02 | Edición | Vaciar una celda | 1001 = 100 → NaN | Error controlado | **IntegrityError no controlado** | APROBADO (fase 1; antes FALLIDO) | A-07 |
| I03 | Persistencia | Tipo almacenado | 1.234,56 | Decimal exacto (text/integer) | `real` | APROBADO (fase 1; antes FALLIDO) | M-02 |

**Simulaciones usadas:**
- D01, D02, D04, D10, D11: `st.file_uploader`, `st.button` y `st.checkbox`.
- I01: `st.form_submit_button` y `st.rerun`.
- I02: `st.data_editor`, `st.button` y `st.rerun`.
- H01, H02: solo se redirige `DB_PATH` a una BD temporal.

En todos los casos se ejecutó el código real del módulo (`render`, `_render_grupos`, `_tabla_editable`, `app.py`).

---

## 3. Verificaciones no ejecutadas

| ID | Módulo | Escenario | Motivo | Procedimiento para ejecutarla | Estado |
|---|---|---|---|---|---|
| N-01 | Conciliación | Reportes de Alutech 2021–2025 contra los estados publicados | No hay datos de Alutech en la BD ni en `documentos/` | Cargar los estados 2020–2025; comparar totales, utilidades, % y ROE contra una hoja de cálculo independiente | NO EJECUTADO |
| N-02 | Interfaz | Navegación manual de las 16 páginas | No se levantó el servidor durante la auditoría | `streamlit run app.py` sobre una copia de la BD; recorrer cada página con un ejercicio completo, uno incompleto y uno aproximado | NO EJECUTADO |
| N-03 | Restauración | Restaurar con varias pestañas abiertas (bloqueo de archivo en Windows) | Requiere una sesión real con varios navegadores | Abrir 2 pestañas, restaurar desde una y verificar el error o el éxito y el estado de la otra | NO EJECUTADO |
| N-04 | Excel | Abrir los archivos en Excel o LibreOffice | No hay una hoja de cálculo en el entorno de la auditoría | Abrir el archivo de G01 y confirmar la advertencia de circularidad y los totales | NO EJECUTADO |
| N-05 | PDF | Revisión visual (maquetación, saltos, acentos) | Solo se verificó la firma `%PDF` | Generar con datos de Alutech e inspeccionar | NO EJECUTADO |
| N-06 | Persistencia | Cerrar el proceso Streamlit real y reabrir | Solo se probó a nivel de engine (T-08, E01) | Capturar, cerrar el proceso, reabrir y comparar | NO EJECUTADO |
| N-07 | Entorno | Compatibilidad con las versiones mínimas (Streamlit 1.38, pandas 2.2, etc.) | Solo están instaladas las versiones actuales | Crear un venv con las versiones mínimas y ejecutar pytest y la aplicación | NO EJECUTADO |
| N-08 | Seguridad | Acceso desde otra máquina de la red | Requiere una segunda máquina | Desde otro equipo, abrir `http://<IP>:8501` con la aplicación en ejecución | NO EJECUTADO |

---

## 4. Cobertura de escenarios requeridos

| # | Escenario | Prueba original | Prueba de auditoría | Estado |
|---|---|---|---|---|
| 1 | Balance equilibrado | T-12 | — | APROBADO |
| 2 | Balance descuadrado | T-13 | — | APROBADO |
| 3 | Activos negativos | — | F02 (correctora), F01 | APROBADO / FALLIDO (F01) |
| 4 | Pasivos negativos | — | F05 (suma algebraica) | APROBADO |
| 5 | Patrimonio negativo | — | F05, A02 | APROBADO (balance) / FALLIDO (DuPont) |
| 6 | Cuentas correctoras | — | F01, F02 | FALLIDO (sin validación de signo) |
| 7 | Ingresos financieros | — | F04 | APROBADO |
| 8 | Gastos financieros | T-24 | F04 | APROBADO |
| 9 | Otros ingresos operativos | T-25 | F04, B02 | APROBADO (cálculo) / FALLIDO (retroactividad) |
| 10 | Otros gastos operativos | T-25 | F04 | APROBADO |
| 11 | Utilidad neta negativa | — | A09 | APROBADO |
| 12 | Ingresos netos = 0 | T-30 | A07 | APROBADO |
| 13 | Activos promedio = 0 | — | A08 | APROBADO |
| 14 | Patrimonio promedio = 0 | T-19 | — | APROBADO |
| 15 | Patrimonio promedio negativo | — | A02 | FALLIDO |
| 16 | Saldo inicial inexistente | T-18 | A03, A04 | APROBADO (aprox.) / FALLIDO (ceros, parcial) |
| 17 | Ejercicios discontinuos | — | A01 | FALLIDO |
| 18 | Modificación de ejercicios anteriores | — | B06 | APROBADO (aislamiento); trazabilidad FALLIDA (C01) |
| 19 | Importaciones Excel duplicadas | T-20 | D09, D11 | APROBADO |
| 20 | Cancelación de importación | — | D01, D02 | FALLIDO |
| 21 | Importación con errores parciales | T-20 | D10, D03, D04 | APROBADO (filas inválidas) / FALLIDO (vacíos) |
| 22 | Restauración de BD dañada | — | H01, H02 | FALLIDO |
| 23 | Cambios de clasificación de cuentas históricas | — | B01, B02, B03 | FALLIDO |
| 24 | Persistencia tras cerrar y abrir la aplicación | T-08 (engine) | E01 (engine) | APROBADO a nivel de engine; app real NO EJECUTADO (N-06) |
