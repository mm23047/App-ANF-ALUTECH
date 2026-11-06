# Informe de recuperación de la carpeta `calculations/` (Fase 1)

Proyecto: `C:\Users\estua\Documents\ANF\appfinanciera` · Rama `correcciones-auditoria` · HEAD `92115b6` (sin cambios) · Fecha: 2026-11-03, 11:47–11:56 · Autorización: Fase 1 (recuperación mediante copia, sin commit).

## 1. Objetivo

Restituir los 14 módulos de cálculo en `calculations/`, en la raíz del proyecto, copiándolos desde `.venv/calculations/` sin mover ni borrar los originales, sin alterar su contenido y sin modificar fórmulas, datos, interfaz ni git (salvo el efecto natural en el árbol de trabajo).

## 2. Estado inicial del repositorio

Comandos: `git rev-parse --abbrev-ref HEAD`, `git rev-parse HEAD`, `git status --short`, `git status --short --ignored`.

| Concepto | Resultado (11:47) |
|---|---|
| Rama / HEAD | `correcciones-auditoria` / `92115b64471b3d03e6bbbbdadb02d2a7846b2a49` |
| Modificados (` M`) | 16 (README, app.py, navigation, migrations, models, repositories, accounts, dashboard, data_entry y 7 pruebas) |
| Eliminados (` D`) | 7: `calculations/{balance_sheet, banderas, controls, dupont, income_statement, validation, vertical_analysis}.py` |
| Sin seguimiento (`??`) | 18: los 17 de la auditoría más `AUDITORIA_FORENSE_ERRORES_ANF.md`, creado después |
| Ignorados relevantes | `.venv/`, `data/financiera.db`, `data/backups/`, `documentos/`, `__pycache__/`, `.pytest_cache/`, `streamlit_run*` |
| `calculations/` en la raíz | **No existía** |
| `.venv/calculations/` | 14 `.py` más `__pycache__/` (28 archivos); carpeta movida el 2026-11-03 a las 10:50:17 |
| Otros módulos de cálculo | Ninguno fuera de `.venv/calculations/` (`find` excluyendo `.venv` y `.git`) |
| Procesos | Ningún `python.exe` ni `streamlit.exe` en ejecución; la otra sesión de Claude estaba inactiva |
| Base de datos | SHA-256 `48bb729ffe5f5ba9b24bb337933adc5d0c6d7bba62b1fad629384b04af4dd269` |

**Incidencia detectada antes de restaurar**, que corrige `AUDITORIA_FORENSE_ERRORES_ANF.md` §2: con los módulos en `.venv/calculations/`, `wacc.py` (línea 33) y `comparacion_anf.py` (línea 40) calculan la ruta de sus datos como `Path(__file__).resolve().parent.parent / "fuentes" / "anf"`. Eso apuntaba a `.venv\fuentes\anf\`, que no existe: `SUPUESTOS.exists() = False` y `DIR_ANF.exists() = False`. Las páginas de WACC y de comparación con el trabajo **fallaban** en el árbol real, aunque las importaciones funcionaran. La auditoría forense solo había comprobado las importaciones.

## 3. Inventario de los 14 módulos

| Módulo | Bytes | Fecha de modificación | Estado en git | Función | Lo usan |
|---|---:|---|---|---|---|
| `balance_sheet.py` | 4,603 | 2026-11-01 11:24 | Con seguimiento (en HEAD) | Balance General | rubros, reportes, pruebas |
| `banderas.py` | 3,397 | 2026-11-01 11:49 | Con seguimiento | Banderas de datos | módulos y avisos |
| `controls.py` | 2,935 | 2026-11-01 11:25 | Con seguimiento | Conciliación | dupont, reportes |
| `dupont.py` | 14,248 | 2026-11-01 11:49 | Con seguimiento | DuPont (saldos promedio) | reports/dupont_report |
| `income_statement.py` | 6,570 | 2026-11-01 11:24 | Con seguimiento | Estado de Resultados | rubros, reportes |
| `validation.py` | 4,685 | 2026-11-01 11:24 | Con seguimiento | Validaciones | módulos de captura |
| `vertical_analysis.py` | 8,357 | 2026-11-01 11:49 | Con seguimiento | Vertical por ejercicio | reports/vertical_report |
| `comparacion_anf.py` | 10,625 | 2026-11-02 22:06 | **Sin seguimiento** (nunca confirmado: 0 commits) | Comparación con el trabajo ANF | reports/analisis_alutech, informe_integral, secciones; scripts/generar_informe_validacion; tests/test_alutech |
| `comparativo.py` | 14,837 | 2026-11-02 21:28 | Sin seguimiento | Horizontal y vertical comparativo | comparacion_anf, reports/secciones, pruebas |
| `controles_carga.py` | 4,143 | 2026-11-02 21:30 | Sin seguimiento | Controles de trazabilidad | modules/trazabilidad, reports/secciones, scripts/cargar_alutech, pruebas |
| `fuentes_usos.py` | 5,029 | 2026-11-02 21:29 | Sin seguimiento | Origen y aplicación de fondos | comparacion_anf, reportes, pruebas |
| `indicadores.py` | 26,728 | 2026-11-02 21:27 | Sin seguimiento | 39 indicadores | comparacion_anf, modules/dashboard, reportes, scripts, pruebas |
| `rubros.py` | 17,522 | 2026-11-02 21:25 | Sin seguimiento | Grupos de análisis y `DatosEjercicio` | 6 módulos de cálculo, accounts, dashboard, trazabilidad, reportes, scripts y pruebas |
| `wacc.py` | 7,427 | 2026-11-02 21:29 | Sin seguimiento | WACC | comparacion_anf, reportes, pruebas |

Los 7 sin seguimiento son **necesarios**: la app, los reportes, los scripts y las pruebas los importan. Fuera de `.venv/calculations/`, solo existían en el respaldo de esta fase y en copias temporales de auditoría.

## 4. Respaldo completo

Comando: `cp -a "C:/Users/estua/Documents/ANF/appfinanciera" "<respaldo>/"`, que conserva fechas y permisos e incluye `.git`, `.venv`, `data`, `documentos` y todo lo ignorado.

**Ubicación:** `C:\Users\estua\Documents\ANF\respaldos_appfinanciera\fase1_recuperacion_calculations_20261103_114753\appfinanciera\`

| Verificación | Original | Respaldo |
|---|---:|---:|
| Archivos | 44,129 | 44,129 |
| Bytes (`du -sb`) | 539,526,539 | 539,526,539 |
| Manifiesto SHA-256 de todos los archivos (`find -type f \| sort \| xargs sha256sum`) | — | **Idéntico** |
| `.venv/calculations/*.py` | 14 | 14 |
| `data/financiera.db` | `48bb729f…` | `48bb729f…` |
| `git status --short` (desde el respaldo) | — | Idéntico al original |

## 5. Comparación de archivos con y sin seguimiento

Para los 7 con seguimiento se usó `git hash-object --path=calculations/<f>.py .venv/calculations/<f>.py`, que aplica los filtros de fin de línea del repositorio (`core.autocrlf=true`), frente a `git rev-parse HEAD:calculations/<f>.py`.

| Archivo | Estado git | Existía en la raíz | Existe en `.venv/calculations` | Diferencias frente a HEAD | Acción |
|---|---|---|---|---|---|
| balance_sheet.py | Eliminado (` D`) | No | Sí | Ninguna (blob `d7fd1cab89a2`); solo CRLF en disco (122/122 líneas) | Copiar |
| banderas.py | Eliminado | No | Sí | Ninguna (`1176f52bfedc`); CRLF | Copiar |
| controls.py | Eliminado | No | Sí | Ninguna (`075fee88fcb0`); CRLF | Copiar |
| dupont.py | Eliminado | No | Sí | Ninguna (`81fe83201426`); CRLF | Copiar |
| income_statement.py | Eliminado | No | Sí | Ninguna (`9a3d6e2b4b42`); CRLF | Copiar |
| validation.py | Eliminado | No | Sí | Ninguna (`b2265b36a5f7`); CRLF | Copiar |
| vertical_analysis.py | Eliminado | No | Sí | Ninguna (`4c8904c0c620`); CRLF | Copiar |
| comparacion_anf.py | No existía para git | No | Sí | Sin versión en git (0 commits) | Copiar |
| comparativo.py | No existía para git | No | Sí | Sin versión en git | Copiar |
| controles_carga.py | No existía para git | No | Sí | Sin versión en git | Copiar |
| fuentes_usos.py | No existía para git | No | Sí | Sin versión en git | Copiar |
| indicadores.py | No existía para git | No | Sí | Sin versión en git | Copiar |
| rubros.py | No existía para git | No | Sí | Sin versión en git | Copiar |
| wacc.py | No existía para git | No | Sí | Sin versión en git | Copiar |

Las diferencias de hash que mostraban `sha256sum` frente a `git show` en dos archivos se deben solo a los finales de línea; los blobs normalizados por git son idénticos. No se restauró ninguna versión desde git.

## 6. Archivos copiados a la raíz

Comandos:

```
[ -e calculations ] && exit 1      # sin sobrescribir: no existía
mkdir calculations
cp -n -p .venv/calculations/*.py calculations/   # -n: nunca sobrescribe; -p: conserva fechas
```

Se copiaron los 14 `.py`. No se copió `__pycache__/` (se regenera solo y no forma parte del código). `.venv/calculations/` no se movió ni se modificó.

## 7. Verificación mediante hashes

| Módulo | SHA-256 (16 primeros) | Raíz = `.venv` = respaldo |
|---|---|---|
| balance_sheet.py | c58955b616684384 | Sí |
| banderas.py | 8970fdc4d78a1a45 | Sí |
| comparacion_anf.py | a3e8cf5632169bc6 | Sí |
| comparativo.py | 1e1b239958fb31d8 | Sí |
| controles_carga.py | a4b9d58ca2d56c1c | Sí |
| controls.py | 805093287e5f652f | Sí |
| dupont.py | d8d0ba34a8123829 | Sí |
| fuentes_usos.py | 0e1b0398c5f0a7c1 | Sí |
| income_statement.py | f5bd0a54f4c135c1 | Sí |
| indicadores.py | e1e7b10121a786b1 | Sí |
| rubros.py | a7703bf1bf298772 | Sí |
| validation.py | 861a654676e05ad9 | Sí |
| vertical_analysis.py | bf3180bbf8193f65 | Sí |
| wacc.py | a185d359f99b5a1d | Sí |

Resultado: **14/14 idénticos**. Los 28 archivos de `.venv/calculations/` (incluido `__pycache__`) tienen los mismos hashes que antes de la intervención.

## 8. Verificación de importaciones

Comprobación ejecutada desde la raíz con `.venv\Scripts\python.exe -B` (sin escribir caché):

- `calculations.__path__` = `[…\appfinanciera\calculations, …\appfinanciera\.venv\calculations]`. La raíz va primero.
- **14/14 módulos se cargan desde la raíz** (`calculations/`).
- `wacc.SUPUESTOS` = `…\fuentes\anf\supuestos_wacc.json`: **existe**. `comparacion_anf.DIR_ANF` = `…\fuentes\anf`: **existe**. `cargar_supuestos()` funciona y se cargan 261 referencias ANF. Queda resuelta la incidencia del §2.
- Con el Python global, `calculations` ya se resuelve desde la raíz. El error que aparece después (`No module named 'sqlalchemy'`) se debe a que esa dependencia solo está instalada en el venv; no tiene relación con la ubicación de los módulos.
- Ningún archivo `.py`, `.toml`, `.cfg` ni `.ini` del proyecto hace referencia explícita a `.venv/calculations`. Las dos menciones a `.venv` en `tests/test_fase4.py` (líneas 112 y 249) solo excluyen esa carpeta al recorrer archivos.

## 9. Pruebas en copia aislada

Copia: `…\scratchpad\app3`, construida desde el árbol restaurado (`app.py`, `calculations` de la raíz, `components`, `database`, `modules`, `reports`, `scripts`, `fuentes`, `assets`, `.streamlit`, `tests`) más una copia de `data/financiera.db`, sin `__pycache__` y sin `.venv/calculations`.

Comando: `.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider` (directorio de trabajo: la copia).

Resultado: **525 aprobadas de 525** (145.9 s). La base de la copia y la original siguen con el hash `48bb729f…` después de las pruebas. No se modificó código para que pasaran.

## 10. Estado final de git

| Concepto | Inicial | Final |
|---|---|---|
| Rama / HEAD | `correcciones-auditoria` / `92115b6` | Sin cambios |
| Modificados | 16 | 16 (los mismos) |
| Eliminados | 7 | **0**: los 7 módulos con seguimiento vuelven a estar en su sitio y git los ve sin cambios frente a HEAD |
| Sin seguimiento | 18 | 25: los mismos 18 más los 7 módulos `calculations/{comparacion_anf, comparativo, controles_carga, fuentes_usos, indicadores, rubros, wacc}.py`, ahora fuera de la carpeta ignorada |
| Preparado para commit (`git diff --cached`) | Nada | Nada |
| Commits / stash | — | Ninguno creado |

Archivos que cambiaron fuera de `calculations/` (comparación del manifiesto SHA-256 completo antes y después): solo `.git/index`. Ese cambio es la actualización de la caché de metadatos que `git status` hace al volver a encontrar los archivos. `git ls-files -s` es idéntico al del respaldo (74 rutas, mismos blobs) y no hay nada preparado. No se modificó ningún archivo fuera del alcance autorizado: ni la base de datos, ni el código, ni la interfaz, ni los documentos.

## 11. Incidencias encontradas

1. **Antes de la intervención fallaban las páginas de WACC y de comparación con el trabajo** (§2): resuelto con la restauración.
2. Corrección a `AUDITORIA_FORENSE_ERRORES_ANF.md` §2: la afirmación de que la app «funciona por accidente» era incompleta. Importaba, pero esas dos funciones fallaban. Ese informe no se modificó.
3. La primera comprobación de importaciones falló por un error de comillas en el comando de prueba. Se repitió con un script; no tuvo efecto en el proyecto.

## 12. Riesgos pendientes (requieren autorización para actuar)

1. **Copia duplicada en `.venv/calculations/`.** Sigue formando parte del paquete de espacio de nombres `calculations` (segunda posición). La raíz tiene prioridad, pero:
   - un módulo que exista solo en `.venv/calculations/` seguiría siendo importable;
   - si en el futuro se edita uno de los dos lados, las copias divergirán sin aviso.

   Por la regla de esta fase, se conservó. Cuando se autorice, puede retirarse **después** de confirmar otra vez los hashes; el respaldo de esta fase lo contiene.
2. **Los 7 módulos sin seguimiento siguen fuera de git.** Ya no están en una carpeta ignorada, pero solo existen en disco (y en el respaldo). Protegerlos requiere un commit autorizado.
3. **El origen del movimiento no se ha determinado.** Ocurrió a las 10:50 con otra sesión de Claude abierta en la misma carpeta; conviene confirmar que no se repita.
4. Los paquetes del proyecto no tienen `__init__.py`: siguen siendo paquetes de espacio de nombres, como antes. Es un tema pendiente de fases anteriores (O‑6) que no se tocó.

## 13. Conclusión

**Recuperación satisfactoria.** Se cumplen todos los criterios de finalización:

- Hay un respaldo completo y verificado (44,129 archivos, manifiesto SHA-256 idéntico).
- Los 14 módulos están en `calculations/`, en la raíz, y 14/14 se cargan desde ahí.
- Los 14 originales (y su `__pycache__`) siguen intactos en `.venv/calculations/`.
- Los hashes de las copias coinciden 14/14 con los originales.
- No se perdieron modificaciones ni archivos sin seguimiento: los 7 eliminados de git vuelven a coincidir con HEAD.
- La base de datos no cambió (`48bb729f…`).
- No se modificó ninguna fórmula, indicador ni lógica.
- El estado de git está documentado y no hay nada preparado para commit ni ningún commit nuevo.

Quedan pendientes los riesgos del §12. No se inició ninguna otra fase.
