# Matriz de pruebas

**Fecha de ejecución:** 2026-11-01 · **Entorno:** Windows 11, Python 3.12.10 (`.venv`), pytest 8.4.2, Streamlit 1.66.1, SQLAlchemy 2.0.55
**Base de datos:** todas las pruebas usan SQLite temporales. El hash de `data/financiera.db` fue el mismo antes y después (`f026863d…630a82d`).

## Resumen

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
| T-15 | DuPont | Factores | A 1.000, P 600, I 1.000, UN 100 | 0,10 / 1,00 / 1,67 | Correcto | APROBADO |
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
| A01 | DuPont | Ejercicio no consecutivo | 2021 (A 1.000) y 2023 (A 2.000), sin 2022 | No usar 2021 como saldo inicial sin marcarlo | Activo inicial 1.000; fuente "Balance final del ejercicio 2021"; `aproximado=False` | FALLIDO | A-01 |
| A02 | DuPont | Patrimonio promedio negativo | A 1.000, P −200, UN −100 | No disponible o con advertencia | ROE **+50,00%**, mult. −5,00, sin advertencia | FALLIDO | A-04 |
| A03 | DuPont | Ejercicio anterior guardado en ceros | 2022 en ceros; 2023 A 2.000, P 1.000, UN 200 | Activo inicial ≠ 0 o aproximado | Activo inicial 0 → prom. 1.000 → **ROE 40%** (real 20%); `aproximado=False` | FALLIDO | A-02 |
| A04 | DuPont | Saldos manuales parciales | Solo patrimonio inicial 500 | Activo inicial ≠ 0 o aproximado | Activo inicial 0; **rotación 2,00** (real 1,00) | FALLIDO | A-02 |
| A05 | DuPont | Identidad con datos válidos | 2021 → 2022, I 1.234,56, UN 98,76 | ROE 15,19% en ambos | 15,19% = 15,19% | APROBADO | — |
| A06 | DuPont | Factores mostrados reproducen el ROE | A 3.333, P 1.111, I 7.777, UN 123 | Producto ≈ ROE ± 0,01 | 1,58% × 2,33 × 3,00 = 11,04% frente a ROE 11,07% | FALLIDO | B-01 |
| A07 | DuPont | Ingresos = 0 | I 0 | No disponible | No disponible | APROBADO | — |
| A08 | DuPont | Activo promedio = 0 | A 0 | No disponible | No disponible | APROBADO | — |
| A09 | DuPont | Utilidad negativa | A 1.000, P 500, UN −100 | ROE −20%, margen −10% | Correcto | APROBADO | — |
| B01 | Catálogo | Reclasificar ACTIVO → INGRESOS con saldo | 1001 = 500 en 2021 | Bloqueado o importe conservado | Activo 500 → 0; ingresos 0: **el importe desaparece** | FALLIDO | C-03 |
| B02 | Catálogo | Cambiar efecto INGRESO → GASTO | 6003 = 100 en 2021 | UN 2021 sin cambio | UN 1.100 → 900 | FALLIDO | C-03 |
| B03 | Catálogo | CORRIENTE → NO_CORRIENTE | 1003 = 400 | AC 2021 sin cambio | AC 400 → 0 | FALLIDO | C-03 |
| B04 | BD | Importe con ejercicio inexistente | `fiscal_period_id=999` | IntegrityError | IntegrityError | APROBADO | — |
| B05 | BD | Importe duplicado cuenta/ejercicio | 2 filas iguales | IntegrityError | IntegrityError | APROBADO | — |
| B06 | BD | Modificar 2022 no altera 2021 | 2022: 1001 = 1.500 | Activo 2021 = 1.000 | 1.000 | APROBADO | — |
| C01 | Historial | CREAR identifica registro y ejercicio | 1002 = 10 | `registro_id` = id del registro; columna de ejercicio | `registro_id=2` (id de cuenta) y entry.id=1; sin columna de ejercicio | FALLIDO | A-08 |
| D01 | Importación | Solo vista previa (sin confirmar) | XLSX período 2024 | No se crea 2024 | **Ejercicio 2024 creado** + 1 registro en el historial | FALLIDO | C-02 |
| D02 | Importación | Cancelar | XLSX período 2025 + "Cancelar" | No se crea 2025 | **Ejercicio 2025 creado** | FALLIDO | C-02 |
| D03 | Importación | Valor vacío | Celda vacía | Estado ≠ OK | Estado **OK**, valor `NaN` | FALLIDO | A-07 |
| D04 | Importación | Confirmar con valor vacío | Igual + Confirmar | Error controlado, nada guardado | **IntegrityError no controlado** (NOT NULL) | FALLIDO | A-07 |
| D05 | Importación | Período decimal | 2021.9 | Rechazado | OK, período 2021 | FALLIDO | M-01 |
| D06 | Importación | Período fuera de rango | 21 | Rechazado | OK | FALLIDO | M-01 |
| D07 | Importación | Más de 2 decimales | 0,1 + 0,2 | Rechazado o cuantizado | 0.30000000000000004, OK | FALLIDO | M-02 |
| D08 | Importación | Código numérico | 1001.0 | OK | CUENTA_DESCONOCIDA | FALLIDO | B-06 |
| D09 | Importación | Duplicado dentro del archivo | 1001/2021 × 2 | OK + DUPLICADA | Correcto | APROBADO | — |
| D10 | Importación | Errores parciales | 1 válida + 1 inexistente | Solo se importa la válida | {1001: 100,00} | APROBADO | — |
| D11 | Importación | Reimportar el mismo archivo | 2 veces | 1 registro | 1 | APROBADO | — |
| E01 | Precisión | Importe grande | 123.456.789.012.345,67 | Exacto tras reabrir | Exacto | APROBADO | — |
| E02 | Precisión | Importes típicos | 0,10; 0,20; 1.234.567,89; −98.765,43; 99.999.999,99 | Suma exacta | 101.135.802,75 exacto | APROBADO | — |
| E03 | Precisión | Conversión de float en la captura | 2,675 | 2,68 (HALF_UP) | 2,67 | FALLIDO | B-08 |
| F01 | Balance | Depreciación positiva | PPE 1.000, dep. +300 | ANC 700 o rechazo | ANC **1.300** | FALLIDO | A-05 |
| F02 | Balance | Depreciación negativa | PPE 1.000, dep. −300 | ANC 700 | 700 | APROBADO | — |
| F03 | ER | Costo capturado negativo | I 1.000, CV −600 | UB 400 o rechazo | UB **1.600** | FALLIDO | A-05 |
| F04 | ER | Estado completo (todas las categorías) | 11 cuentas | UB 4.000; UO 2.300; RF −300; OR 20; UAI 2.020; UN 1.415 | Correcto | APROBADO | — |
| F05 | Balance | Pasivo > activo, patrimonio negativo | A 100, P 300, Pat. −200 | Pat. −200, cuadra | Correcto | APROBADO | — |
| F06 | Vertical | ER incluye ingresos y utilidades | I 1.000, CV 600 | Fila 4001 y utilidades | Solo fila 5001 | FALLIDO | M-03 |
| F07 | Vertical | Balance incluye subtotales | AC 300, ANC 700 | Subtotales con % | Solo filas por cuenta | FALLIDO | M-03 |
| F08 | Balance | Ausencia frente a cero | Solo 1001 = 100 | Indicador de incompleto | No existe; pasivo = 0,00 | FALLIDO | M-04 |
| G01 | Excel | Balance sin grupo ANC | AC 100, PC 40, Pat. 60 | Sin circulares | `C12 =C10+C12`, `C20 =C18+C20`, `C28 =C26+C28+…` | FALLIDO | A-06 |
| G02 | Excel | ER sin gastos ni ISR | I 1.000, CV 600 | Sin circulares | `C18`, `C20`, `C22 =C20-C22` circulares | FALLIDO | A-06 |
| G03 | PDF | Nombre con "&" | "Acero & Aluminio, S. A. de C. V." | PDF válido | Válido | APROBADO | — |
| G04 | Exportación | No modifica la BD | Exportar los 4 archivos | Hash igual | Igual | APROBADO | — |
| H01 | Restauración | Archivo corrupto (`app.py` real con AppTest) | Bytes no SQLite | BD intacta | **BD sobrescrita**; `DatabaseError: file is not a database` | FALLIDO | C-01 |
| H02 | Restauración | SQLite ajena | BD con tabla `x` | Rechazada | "Base de datos restaurada correctamente."; **empresa = None** | FALLIDO | C-01 |
| I01 | Captura | Guardar el formulario sin completar | Formulario Balance 2021 | Sin registros fantasma | 19 registros 0,00; "tiene datos" y "cuadra" | FALLIDO | A-03 |
| I02 | Edición | Vaciar una celda | 1001 = 100 → NaN | Error controlado | **IntegrityError no controlado** | FALLIDO | A-07 |
| I03 | Persistencia | Tipo almacenado | 1.234,56 | Decimal exacto (text/integer) | `real` | FALLIDO | M-02 |

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
