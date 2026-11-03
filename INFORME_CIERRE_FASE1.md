# Informe de cierre — Fase 1.2: consolidación de `calculations/` y protección en git

Proyecto: `C:\Users\estua\Documents\ANF\appfinanciera` · Rama `correcciones-auditoria` · Fecha: 2026-11-03, 12:01–12:20 (hora local, UTC−6).

## 1. Resumen ejecutivo

| Tarea | Resultado |
|---|---|
| A. Eliminar la copia duplicada `.venv/calculations/` | **Hecho**, tras verificar que nada dependía de ella. Se eliminaron exactamente 28 archivos (14 `.py` + 14 `.pyc`); el resto de `.venv` y del proyecto no cambió. |
| B. Versionar los 7 módulos nuevos | **Hecho**: commit `9fb79f478374c5f355bf3e8eb9f3babb1a9a89f3`, que contiene exactamente los 7 archivos autorizados. |
| C. Investigar el origen del movimiento | **Origen no determinado.** Hay evidencia directa que excluye a esta sesión de Claude y ningún registro de otra sesión que ejecutara herramientas. Hay indicios de actividad en la interfaz de VS Code en el mismo segundo, pero no prueban la causa. |
| Pruebas | 525/525 en una copia aislada, después de eliminar el duplicado. |
| Base de datos | Sin cambios (`48bb729f…af4dd269`). |

**La Fase 1.2 terminó satisfactoriamente.**

## 2. Respaldo

| Concepto | Valor |
|---|---|
| Ubicación | `C:\Users\estua\Documents\ANF\respaldos_appfinanciera\fase1_2_cierre_20261103_120117\appfinanciera\` |
| Método | `cp -a` del proyecto completo: `.git`, `.venv` (con `.venv/calculations`), `calculations/`, `data/`, `fuentes/`, `documentos/`, código, archivos modificados, sin seguimiento e ignorados. |
| Archivos | 44,144 en el original y 44,144 en el respaldo. Por carpeta: `.git` 300, `.venv` 43,654, `calculations` 14, `data` 7, `fuentes` 4, `documentos` 9. |
| Tamaño | 539,671,576 bytes en ambos (`du -sb`). |
| Manifiesto SHA-256 de todos los archivos | **Idéntico** entre original y respaldo. |
| Respaldo de la Fase 1 | Sigue disponible: `…\fase1_recuperacion_calculations_20261103_114753\` (15 entradas en su `.venv/calculations`). |

## 3. Eliminación de duplicados

**Estado inicial verificado (12:01):** HEAD `92115b6`; 16 modificados, 0 eliminados, 26 sin seguimiento (los 25 de la Fase 1 más `INFORME_RECUPERACION_CALCULATIONS.md`); nada preparado para commit. `git diff --stat`: 16 archivos, +712/−53.

**Verificaciones previas:**

| Verificación | Resultado |
|---|---|
| Hashes raíz = `.venv/calculations` | 14/14 idénticos |
| Módulos en `.venv/calculations` que no estén en la raíz | Ninguno (solo `__pycache__/` con los 14 `.pyc`) |
| Importaciones explícitas de `.venv/calculations` | Ninguna (`grep` en `.py`, `.toml`, `.ini`, `.cfg`, `.json`, `.ps1`, `.bat`, `.cmd` y `.sh`) |
| `PYTHONPATH` (sesión, usuario y máquina) | Vacío |
| Archivos `.pth` en `.venv/Lib/site-packages` | No hay |
| `pyvenv.cfg` | Venv estándar de Python 3.12.10; `include-system-site-packages = false` |
| `sys.path.insert` en el proyecto | 6 casos (`scripts/cargar_alutech.py`, `scripts/generar_informe_validacion.py`, `tests/conftest.py`, `tests/humo_fase4.py`, `tests/humo_paginas.py`, `tests/test_auditoria.py`); **todos apuntan a la raíz del proyecto** |
| Importaciones dinámicas (`importlib`, `__import__`, `runpy`) | Ninguna sobre `calculations` (solo `importlib.metadata` en `tests/test_fase4.py`) |
| Streamlit (`.streamlit/config.toml`) | Solo `server.address = "localhost"` |
| Configuración de IDE y pruebas (`.vscode`, `.idea`, `pytest.ini`, `pyproject.toml`, `setup.cfg`, `tox.ini`) | No existen |
| Scripts de ejecución (`*.bat`, `*.ps1`, `*.sh`, `*.cmd`) | No existen |
| Resolución antes de eliminar | 14/14 módulos cargados desde la raíz |

La única vía por la que `.venv/calculations` era visible es que Windows incluye la raíz del venv en `sys.path`; no es una dependencia del proyecto.

**Eliminación:** `rm -r -- .venv/calculations`, con comprobación previa de la ruta real (`realpath`) y de que la raíz tenía 14 módulos. Se eliminaron 28 archivos. `.venv` pasó de 43,654 a 43,626 archivos, y la comparación del manifiesto SHA-256 completo confirma que **ningún otro archivo cambió** (ni en `.venv` ni en el proyecto).

**Verificación posterior (`.venv\Scripts\python.exe -B`, desde la raíz):**

- `calculations.__path__ = […\appfinanciera\calculations]`: una sola ubicación.
- 14/14 módulos se importan desde la raíz.
- `wacc.SUPUESTOS` → `fuentes\anf\supuestos_wacc.json`: existe; `cargar_supuestos()` funciona.
- `comparacion_anf.DIR_ANF` → `fuentes\anf`: existe; 261 referencias ANF cargadas (el mismo conjunto que en la Fase 1).
- `calculations/` conserva sus 14 módulos sin cambios.

## 4. Pruebas

| Concepto | Valor |
|---|---|
| Entorno | Copia aislada `…\scratchpad\app4`, construida desde el árbol actual (`app.py`, `calculations`, `components`, `database`, `modules`, `reports`, `scripts`, `fuentes`, `assets`, `.streamlit`, `tests`), sin `__pycache__`, con una copia de `data/financiera.db`. Intérprete: `.venv\Scripts\python.exe`. |
| Comando | `python -B -m pytest -q -p no:cacheprovider` |
| Resultado | **525 aprobadas de 525** (187.4 s) |
| Base de datos | Copia y original con SHA-256 `48bb729ffe5f5ba9…` después de las pruebas. La base original no cambió en ningún momento. |

## 5. Git

| Concepto | Valor |
|---|---|
| Rama | `correcciones-auditoria` (no cambió) |
| HEAD anterior | `92115b64471b3d03e6bbbbdadb02d2a7846b2a49` |
| Nuevo commit | `9fb79f478374c5f355bf3e8eb9f3babb1a9a89f3` (padre: `92115b6`) |
| Mensaje | `fix: restore and version ANF calculation modules`, más la línea de coautoría `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` |
| Autor | Estuardo (configuración local de git) |

**Inspección previa de los 7 archivos:**
- Los 7 son idénticos por SHA-256 a los recuperados en la Fase 1 (`.venv/calculations` del respaldo de la Fase 1).
- Seguían sin seguimiento y sin modificaciones.
- No contienen credenciales, contraseñas, tokens, claves, URLs, correos ni rutas a bases de datos.
- No contienen cifras de 6 o más dígitos (no hay datos financieros incrustados).
- Sus dependencias son solo `calculations.*`, `components.money`, `database.*`, `sqlalchemy.orm` y la biblioteca estándar.

**Preparación:** `git add -- calculations/comparacion_anf.py calculations/comparativo.py calculations/controles_carga.py calculations/fuentes_usos.py calculations/indicadores.py calculations/rubros.py calculations/wacc.py` (rutas explícitas; no se usó `git add .` ni `-A`).

- `git diff --cached --name-status`: exactamente 7 líneas `A` con los archivos autorizados; 7 archivos, +1,738.
- Los blobs del índice coinciden con `git hash-object --path=…` de cada archivo de trabajo.
- `git diff --cached --check` avisó de `new blank line at EOF` en `comparativo.py`, `fuentes_usos.py` y `wacc.py`. Es una propiedad del contenido original (los archivos terminan con una línea en blanco extra). No se modificaron, porque la autorización prohíbe alterar su contenido, y no es ninguna de las causas de bloqueo indicadas (archivos adicionales, diferencias inesperadas, información sensible o falta de coincidencia).
- Git avisó de que `controles_carga.py`, `indicadores.py` y `rubros.py` tienen finales LF en disco y que, con `core.autocrlf=true`, pasarían a CRLF «la próxima vez que git los toque». Es informativo: el contenido versionado está normalizado y los archivos de trabajo no cambiaron.

**Archivos incorporados** (`git diff-tree --no-commit-id --name-only -r HEAD`):

1. `calculations/comparacion_anf.py` (246 líneas)
2. `calculations/comparativo.py` (268)
3. `calculations/controles_carga.py` (101)
4. `calculations/fuentes_usos.py` (122)
5. `calculations/indicadores.py` (541)
6. `calculations/rubros.py` (301)
7. `calculations/wacc.py` (159)

**No se incluyó ningún otro archivo.** Después del commit:
- Siguen pendientes, sin preparar, los 16 modificados (README.md, app.py, navigation, migrations, models, repositories, accounts, dashboard, data_entry y 7 pruebas; `git diff --stat` igual que antes: +712/−53) y 19 archivos o carpetas sin seguimiento (documentos de auditoría, `fuentes/`, `scripts/`, `reports/secciones.py`, etc.).
- Hay 0 eliminados y nada preparado.
- Fuera de `.git` no cambió ningún archivo (manifiesto completo). Dentro de `.git` solo hay los 10 objetos nuevos del commit (7 blobs, 2 árboles y 1 commit) y las referencias de la rama.

## 6. Investigación del movimiento

### Registros consultados

| Registro | Resultado |
|---|---|
| Transcripciones de Claude Code (`C:\Users\estua\.claude\projects\*\*.jsonl`, 6 sesiones de este proyecto) | Solo esta sesión (`61cfa1cb`) tiene entradas entre 16:45Z y 16:55Z. Ninguna sesión contiene un comando que mueva o renombre `calculations` (búsqueda de `Move-Item`, `mv`, `move`, `Rename-Item`, `ren`, `robocopy /MOV`, `shutil.move`, `os.rename` y `git mv`). |
| Sesión anterior `50d0d7c0` | Su última entrada con hora es de 14:07:06Z (08:07 local). Su archivo se modificó a las 10:48:41 con entradas sin hora (`last-prompt`, `mode`, `cost-state`), escritas al abrirse la sesión, antes del movimiento. |
| Otra sesión activa (`appfinanciera-80`, iniciada hacia las 10:48) | **No tiene transcripción** en ninguna carpeta de proyectos de `.claude`, lo que indica que no procesó ningún mensaje ni ejecutó herramientas. Al consultarla figuraba como «idle». |
| Registro de la extensión Claude de VS Code (`…\Code\logs\20261103T104828\window1\exthost\Anthropic.claude-code\Claude VSCode.log`) | Inicio de las tareas de esta sesión a las 10:48:37; llamadas a herramientas con inicio y fin (ver la evidencia directa). |
| Otros registros de VS Code (`Git.log`, `GitHub Authentication.log`, `renderer.log`, `ptyhost.log`, `terminal.log`, `main.log`, `exthost.log`, `views.log`, `textModelChanges.log`) | Ver evidencias e indicios. |
| Estado del espacio de trabajo de VS Code (`workspaceStorage\071e5b2e…\state.vscdb` y `.backup`, consultados sobre copias en modo de solo lectura) | Árbol del Explorador y disposición de la terminal. |
| Historial de PowerShell (`PSReadLine\ConsoleHost_history.txt`) | Última modificación: 2026-11-02 20:45. No hubo actividad el día 3; no contiene movimientos de `calculations`. |
| Historial de bash (`~/.bash_history`) | No existe. |
| Diario USN de NTFS (`fsutil usn readjournal C:`) | `Error 5: Acceso denegado`. Requiere privilegios de administrador; no se intentó elevar. |
| Git (`reflog` y `stash`) | Git no registra movimientos del árbol de trabajo; el reflog no muestra operaciones ese día antes de este commit. |
| Marcas de tiempo | `.venv\` y la raíz del proyecto con mtime 2026-11-03 10:50:17.88; `.venv\calculations\` conservaba su mtime original (2026-11-02 21:35) y los archivos las suyas. |

### Evidencias directas

1. **Ventana del movimiento:** a las 16:49:35Z (10:49:35 local), `wc -l calculations/*.py` de esta sesión funcionó, así que la carpeta estaba en la raíz. A las 16:50:24Z, la lectura de `calculations/rubros.py` falló. El mtime de `.venv` y de la raíz (10:50:17.88) sitúa el movimiento a las **10:50:17**.
2. **Fue un movimiento, no una copia y borrado:** la carpeta y sus 14 archivos conservaron sus fechas originales y solo cambiaron las fechas de los directorios de origen y destino.
3. **Esta sesión no lo ejecutó:** sus tres comandos en la ventana (16:49:43, 16:49:51 y 16:50:13Z) solo consultan versiones, ejecutan `pdftotext` hacia el scratchpad, leen JSON y ejecutan `git status`. Según el registro de la extensión, el último terminó a las **10:50:14.141** y el siguiente empezó después de las 10:50:24. **A las 10:50:17 esta sesión no ejecutaba ninguna herramienta.**

### Indicios (compatibles con una acción en la interfaz de VS Code, sin probarla)

1. `GitHub Authentication.log` registra «Getting sessions for all scopes» a las **10:50:17.864 y 10:50:17.878**, en el mismo segundo del movimiento (10:50:17.882). Indica actividad en la ventana de VS Code, pero esa consulta también se produce por otros eventos (foco, menús).
2. `Git.log` registra `git check-ignore` y `git status` a las 10:50:18–19: VS Code reaccionó al cambio en disco. Es una consecuencia, no la causa.
3. Había una terminal integrada persistente (`cmd.exe`) reconectada a las 10:48:33 (`ptyhost.log`). `cmd` no conserva historial y su contenido no se recuperó.
4. El Explorador de VS Code tiene `.venv` expandida, pero ya lo estaba en la copia de estado de las 08:56, antes del movimiento. **No aporta evidencia.**

### Hipótesis (no verificadas)

Una acción manual en VS Code (arrastrar y soltar en el Explorador, que en el mismo volumen es un renombrado) o un comando escrito en la terminal `cmd`. Ninguna puede confirmarse con los registros accesibles.

### Información que no se pudo recuperar

Diario USN (requiere administrador), historial de `cmd.exe`, eventos de arrastrar y soltar del Explorador (VS Code no los registra) y auditoría de archivos de Windows (no hay evidencia de que esté habilitada; no se consultó con privilegios).

### Conclusión de la investigación

**El origen del movimiento no pudo determinarse.** Se puede afirmar con evidencia directa que no lo hizo esta sesión de Claude Code y que ninguna transcripción de Claude contiene la operación. No se atribuye a ninguna persona ni sesión.

## 7. Incidencias

1. **Corrección a `INFORME_RECUPERACION_CALCULATIONS.md` §5:** ese informe dijo que los 7 módulos con seguimiento estaban en CRLF («122/122 líneas»). El conteo con `grep` no era fiable. Un recuento por bytes muestra que solo `balance_sheet.py` e `income_statement.py` usan CRLF; `banderas`, `controls`, `dupont`, `validation` y `vertical_analysis` usan LF. **La conclusión de que eran idénticos a HEAD sigue siendo válida**, porque se basó en la comparación de blobs de git.
2. Un falso positivo similar (`grep -E '\r'`) señaló espacios finales en `indicadores.py`; la comprobación byte a byte lo descartó.
3. `git diff --cached --check`: línea en blanco final en 3 archivos (contenido original, no modificado). Avisos de conversión LF/CRLF en 3 archivos (informativos).
4. Ninguna operación falló, ni se detectaron dependencias de la copia eliminada.

## 8. Conclusión

**Fase 1.2 terminada satisfactoriamente:**

- Hay respaldo completo y verificado.
- La copia duplicada se eliminó sin dependencias y sin afectar a nada más.
- Los 14 módulos residen solo en `calculations/` y se importan desde ahí.
- Las pruebas pasan 525/525 en una copia aislada.
- La base de datos no cambió.
- Los 7 módulos nuevos quedaron versionados en el commit `9fb79f4`, que solo los contiene.
- El origen del movimiento quedó documentado como **no determinado**.

No se modificaron fórmulas, indicadores, WACC, DuPont, fuentes y usos, el ciclo de conversión del efectivo, la interfaz ni la base de datos. Este informe queda como archivo sin seguimiento (no se incluyó en ningún commit).
