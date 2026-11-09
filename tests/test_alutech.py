"""Adaptacion Alutech 2021-2025: datos originales, calculos, comparacion con el
trabajo ANF, exportaciones, migracion v4 y carga reproducible.

Las bases de datos son temporales y reproducen la BD real (2021 con las 19
cuentas del catalogo estandar en cero). Los calculos "a mano" usan las cifras
de los estados financieros originales, no los resultados del trabajo ANF.
"""
import json
import sqlite3
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

import pytest
from openpyxl import load_workbook

from calculations import indicadores as ind
from calculations.comparacion_anf import (
    COINCIDE,
    DIFERENCIA,
    NO_APLICA,
    NO_VERIFICABLE,
    REDONDEO,
    clasificar,
    comparar,
    metricas_desconocidas,
    resumen,
)
from calculations.comparativo import horizontal_conceptos, variacion
from calculations.controles_carga import MODIFICADO, OK, controles_fuentes
from calculations.fuentes_usos import calcular_fuentes_usos
from calculations.rubros import GRUPOS, datos_todos
from calculations.wacc import calcular_wacc
from database import connection
from database.backup_utils import sha256_archivo
from database.connection import init_db, session_scope
from database.enums import TipoEstadoFinanciero as Tipo
from database.migrations import PASOS, migrar, version_esquema
from database.repositories import (
    get_account_by_codigo,
    get_entries_map,
    get_fiscal_period,
    get_or_create_fiscal_period,
    list_accounts,
    save_company,
    upsert_entry,
)
from database.seed import seed_default_accounts
from reports.exportar_secciones import secciones_a_excel, secciones_a_pdf
from reports.informe_integral import hojas_informe
from scripts.cargar_alutech import ARCHIVO_DATOS, CargaError, cargar, importe_impreso

PROYECTO = Path(__file__).resolve().parent.parent
DATOS = json.loads(ARCHIVO_DATOS.read_text(encoding="utf-8"))
D = Decimal


def construir_bd_como_la_real(ruta: Path) -> Path:
    """BD vigente con la empresa y el ejercicio 2021 con 19 importes en cero."""
    init_db(db_path=ruta)
    with session_scope() as s:
        seed_default_accounts(s)
        save_company(s, nombre_legal="Alutech", nombre_comercial="Alutech SV", actividad_economica="metal",
                     pais="El Salvador", moneda="USD", anio_inicial_analisis=2021)
        periodo, _ = get_or_create_fiscal_period(s, 2021)
        for cuenta in list_accounts(s):
            if cuenta.categoria_principal.value in ("ACTIVO", "PASIVO", "PATRIMONIO"):
                upsert_entry(s, fiscal_period_id=periodo.id, account_id=cuenta.id, valor="0", tipo=Tipo.BALANCE)
    connection.dispose_engine()
    return ruta


@pytest.fixture(scope="module")
def bd_cargada(tmp_path_factory):
    ruta = construir_bd_como_la_real(tmp_path_factory.mktemp("alutech") / "financiera.db")
    informe = cargar(db_path=ruta)
    return ruta, informe


@pytest.fixture()
def datos(bd_cargada):
    init_db(db_path=bd_cargada[0])
    with session_scope() as s:
        yield {d.anio: d for d in datos_todos(s) if d.tiene_datos}, s
    connection.dispose_engine()


# --------------------------------------------------------------- carga
def test_carga_crea_todo_y_cuadra_los_61_totales_impresos(bd_cargada):
    _, informe = bd_cargada
    assert informe.cuentas_creadas == len(DATOS["cuentas"]) == 106
    assert informe.ejercicios_creados == [2022, 2023, 2024, 2025]
    assert informe.importes_creados == informe.fuentes_creadas == 247
    assert len(informe.controles) == 61 and informe.controles_ok
    assert informe.respaldo is not None and informe.respaldo.exists()


def test_cada_importe_registrado_es_el_del_documento(datos):
    _, s = datos
    for anio, ejercicio in DATOS["ejercicios"].items():
        periodo = get_fiscal_period(s, int(anio))
        for tipo in ("BALANCE", "RESULTADOS"):
            vigentes = get_entries_map(s, periodo.id, Tipo(tipo))
            for codigo, _, impreso, _ in ejercicio[tipo]:
                esperado = importe_impreso(impreso)
                if tipo == "RESULTADOS":
                    esperado = abs(esperado)  # convencion: costos y gastos en positivo
                assert vigentes[get_account_by_codigo(s, codigo).id] == esperado, (anio, codigo)


def test_los_19_ceros_de_2021_se_conservan(datos):
    _, s = datos
    periodo = get_fiscal_period(s, 2021)
    vigentes = get_entries_map(s, periodo.id, Tipo.BALANCE)
    estandar = [c for c in list_accounts(s) if not c.codigo.startswith(("CB", "CN"))
                and c.categoria_principal.value in ("ACTIVO", "PASIVO", "PATRIMONIO")]
    assert len(estandar) == 19
    assert all(vigentes[c.id] == 0 for c in estandar)


def test_la_carga_es_idempotente(bd_cargada):
    ruta, _ = bd_cargada
    informe = cargar(db_path=ruta, respaldar=False)
    assert informe.cuentas_creadas == informe.importes_creados == informe.fuentes_creadas == informe.datos_creados == 0
    assert informe.importes_existentes == 247 and informe.controles_ok


def test_la_carga_no_sobrescribe_un_importe_distinto_y_no_cambia_nada(tmp_path):
    ruta = construir_bd_como_la_real(tmp_path / "financiera.db")
    cargar(db_path=ruta, respaldar=False)
    init_db(db_path=ruta)
    with session_scope() as s:
        periodo = get_fiscal_period(s, 2025)
        upsert_entry(s, fiscal_period_id=periodo.id, account_id=get_account_by_codigo(s, "CN1101").id, valor="1", tipo=Tipo.BALANCE)
    connection.dispose_engine()
    antes = sha256_archivo(ruta)
    with pytest.raises(CargaError, match="CN1101"):
        cargar(db_path=ruta, respaldar=False)
    assert sha256_archivo(ruta) == antes


def test_la_simulacion_no_modifica_la_bd(tmp_path):
    ruta = construir_bd_como_la_real(tmp_path / "financiera.db")
    antes = sha256_archivo(ruta)
    informe = cargar(db_path=ruta, simular=True)
    assert informe.simulado and informe.controles_ok and informe.importes_creados == 247
    assert sha256_archivo(ruta) == antes
    assert not (tmp_path / "backups").exists()


def test_un_signo_impreso_incoherente_detiene_la_carga(tmp_path):
    datos = json.loads(ARCHIVO_DATOS.read_text(encoding="utf-8"))
    datos["ejercicios"]["2025"]["RESULTADOS"][1][2] = "331,430,173"  # costo de ventas sin parentesis
    archivo = tmp_path / "datos.json"
    archivo.write_text(json.dumps(datos), encoding="utf-8")
    ruta = construir_bd_como_la_real(tmp_path / "financiera.db")
    antes = sha256_archivo(ruta)
    with pytest.raises(CargaError, match="signo incoherente"):
        cargar(archivo, ruta, respaldar=False)
    assert sha256_archivo(ruta) == antes


def test_control_de_fuente_detecta_un_importe_editado(tmp_path):
    ruta = construir_bd_como_la_real(tmp_path / "financiera.db")
    cargar(db_path=ruta, respaldar=False)
    init_db(db_path=ruta)
    with session_scope() as s:
        periodo = get_fiscal_period(s, 2024)
        upsert_entry(s, fiscal_period_id=periodo.id, account_id=get_account_by_codigo(s, "CN1105").id, valor="1", tipo=Tipo.BALANCE)
    with session_scope() as s:
        estados = {c.codigo: c.estado for c in controles_fuentes(s, get_fiscal_period(s, 2024))}
    connection.dispose_engine()
    assert estados["CN1105"] == MODIFICADO
    assert sum(e == OK for e in estados.values()) == len(estados) - 1


def test_todas_las_cuentas_tienen_un_grupo_valido():
    assert all(c["grupo"] in GRUPOS for c in DATOS["cuentas"])
    # «Otras cuentas por cobrar a LP» 2024 no se presume relacionada (revision final).
    assert next(c for c in DATOS["cuentas"] if c["codigo"] == "CN1202")["grupo"] == "OTRAS_CXC_LP"
    assert len({c["codigo"] for c in DATOS["cuentas"]}) == len(DATOS["cuentas"])


# -------------------------------------------------------- calculos a mano
@pytest.mark.parametrize("anio, clave, esperado", [
    (2021, "razon_corriente", D(383881547) / D(205973230)),
    (2021, "ctn", D(383881547) - D(205973230)),
    (2022, "ctn", D(448672401) - D(231944180)),
    (2023, "prueba_acida", (D(429794544) - D(141491319)) / D(333120685)),
    (2023, "razon_tesoreria", (D(12130206) + D(7400000)) / D(333120685) * 100),
    (2024, "ppp", D(225126517) / D(377459424) * 365),
    (2024, "cobertura_intereses", D(35193918) / (D(43089283) - D(15024973))),
    (2025, "roe", D(11898987) / D(231160198) * 100),
    # 9.3: operandos a 2 decimales, 76.89 + 58.25 − 190.66.
    (2025, "cce", D("76.89") + D("58.25") - D("190.66")),
    (2022, "margen_operativo", D(31200977) / D(499653494) * 100),
    (2023, "roe_controladora", D(12309102) / D(227673394) * 100),
    (2021, "maf_controladora", D(553955185) / D(142057829)),
    (2025, "ebitda", D(54665644) + D(7167799)),
    (2021, "ebitda", D(103578903) + D(8610532)),
    (2023, "fondo_maniobra_lp", D(227673394) + D(248306867) - D(379306402)),
])
def test_indicador_calculado_a_mano(datos, anio, clave, esperado):
    por_anio, _ = datos
    valor = ind.calcular(por_anio[anio], clave).valor
    assert abs(valor - esperado) < D("1e-12"), (clave, anio, valor, esperado)


def test_utilidad_operativa_2022_es_un_subtotal_derivado(datos):
    por_anio, _ = datos
    assert por_anio[2022].inc.utilidad_operativa == D(89322338) - D(18344656) - D(39712552) - D(397016) + D(332863)


def test_wacc_2021_a_mano(datos):
    por_anio, _ = datos
    v = D(553955185)
    deuda = [(25039997, "7.50"), (114626074, "7.50"), (4872937, "8.00"), (24556484, "8.00"), (1652870, "6.90"),
             (10847273, "6.90"), (80133, "6.75"), (186964, "6.75"), (32758231, "7.25"), (18271064, "7.34")]
    aporte_deuda = sum(D(i) * D(t) / 100 * D("0.70") for i, t in deuda) / v * 100
    aporte_patrimonio = D(68602739) / v * 100  # (E/V) * (NI/E)
    resultado = calcular_wacc(por_anio[2021])
    assert abs(resultado.wacc_pct - (aporte_deuda + aporte_patrimonio)) < D("1e-12")
    assert abs(resultado.pct_deuda_financiera - D(sum(i for i, _ in deuda)) / v * 100) < D("1e-12")


def test_wacc_sin_tasa_supuesta_no_se_calcula(datos):
    por_anio, _ = datos
    resultado = calcular_wacc(por_anio[2025], {"ejercicios": {"2025": {"tasa_isr": "30.00", "tasas": {}}}})
    assert not resultado.disponible and resultado.wacc_pct is None and "Falta la tasa" in resultado.motivo


def test_indicadores_de_mercado_no_calculables(datos):
    por_anio, _ = datos
    for clave in ("eps", "per", "ml"):
        assert ind.calcular(por_anio[2025], clave).valor is None
    # 8.3 C del trabajo: sin desglose, el indice de pagos fijos iguala a la razon de cargos de interes fijo.
    assert ind.calcular(por_anio[2025], "cobertura_pagos_fijos").valor == ind.calcular(por_anio[2025], "cobertura_intereses").valor


def test_fuentes_y_usos_cuadran_y_reproducen_los_totales_del_trabajo(datos):
    por_anio, _ = datos
    for anio in (2022, 2023, 2024, 2025):
        resultado = calcular_fuentes_usos(por_anio[anio - 1], por_anio[anio])
        assert resultado.cuadra, anio
    assert calcular_fuentes_usos(por_anio[2022], por_anio[2023]).total_fuentes == D(209290574)
    # 2025 vs 2024: el trabajo obtiene 289,762,626 al tratar «Otras cuentas por cobrar a LP» 2024 como relacionadas;
    # sin esa equivalencia (no respaldada por los documentos) el total es 408,447,177 = 289,762,626 + 118,684,551.
    assert calcular_fuentes_usos(por_anio[2024], por_anio[2025]).total_fuentes == D(289762626) + D(118684551)


def test_balance_cuadra_y_totales_coinciden_con_los_impresos(datos):
    por_anio, _ = datos
    impresos = {int(a): {c: importe_impreso(v) for c, _, v, _ in e["totales_declarados"]} for a, e in DATOS["ejercicios"].items()}
    for anio, d in por_anio.items():
        assert d.bs.cuadra, anio
        assert d.bs.total_activo == impresos[anio]["total_activo"]
        assert d.inc.utilidad_neta == impresos[anio]["utilidad_neta"]


# ------------------------------------------------------------- horizontal
@pytest.mark.parametrize("actual, anterior, abs_, pct", [
    (D(120), D(100), D(20), D(20)),
    (D(50), D(0), D(50), None),
    (D(-50), D(-100), D(50), None),
    (None, D(10), None, None),
])
def test_variacion_controla_base_cero_y_negativa(actual, anterior, abs_, pct):
    absoluta, relativa, nota = variacion(actual, anterior)
    assert absoluta == abs_ and relativa == pct
    if anterior is not None and anterior <= 0 and actual is not None:
        assert "Base" in nota


def test_horizontal_ctn_2025_con_base_positiva(datos):
    por_anio, _ = datos
    fila = next(f for f in horizontal_conceptos(list(por_anio.values()), ("activo_corriente",)))
    assert fila.var_abs[2025] == D(247705981) - D(432771678)


# ------------------------------------------------------------ comparacion
@pytest.mark.parametrize("app, anf, decimales, estado", [
    (D("1.8637"), D("1.86"), 2, COINCIDE),
    (D("3.8745"), D("3.88"), 2, REDONDEO),
    (D("135.138"), D("135.2"), 1, REDONDEO),
    (D("1.2902"), D("1.58"), 2, DIFERENCIA),
    (D("216728221"), D("216758221"), 0, DIFERENCIA),
    (D("68602739"), D("68602739"), 0, COINCIDE),
    (None, None, 2, NO_APLICA),
    (None, D("1"), 2, NO_VERIFICABLE),
    (D("1"), None, 2, DIFERENCIA),
])
def test_clasificacion_de_la_comparacion(app, anf, decimales, estado):
    assert clasificar(app, anf, decimales)[0] == estado


def test_comparacion_completa_con_el_trabajo(datos):
    por_anio, _ = datos
    comparaciones = comparar(list(por_anio.values()))
    assert metricas_desconocidas() == []
    conteo = resumen(comparaciones)
    # 5 de E-CPF son resultados derivados: 8.3 C no publica cifras propias.
    assert conteo.pop("Resultado derivado") == 5
    assert conteo == {COINCIDE: 711, REDONDEO: 4, DIFERENCIA: 6, NO_VERIFICABLE: 0, NO_APLICA: 15}
    # Toda discrepancia tiene una causa investigada y documentada.
    sin_causa = [(c.referencia.id, c.anio) for c in comparaciones if c.estado in (DIFERENCIA, REDONDEO) and not c.causa]
    assert sin_causa == []
    # Cada causa pertenece a una de las seis categorias de la revision; ninguna es un error de extraccion.
    from calculations.comparacion_anf import CATEGORIAS_CAUSA

    assert {c.categoria for c in comparaciones if c.causa} <= set(CATEGORIAS_CAUSA)
    assert not any(c.categoria == "Error de extracción" for c in comparaciones)
    # Las coincidencias del WACC dependen de supuestos no verificables y lo indican.
    assert all(c.categoria == "Supuesto no verificable" for c in comparaciones
               if c.referencia.id == "W-WACC" and c.estado == COINCIDE)
    # Las diferencias se concentran en las cifras del trabajo que no corresponden a los documentos.
    ids = {c.referencia.id.split("-")[0] for c in comparaciones if c.estado == DIFERENCIA}
    assert ids <= {"T3", "T4", "T5", "T6", "T7", "B", "FU25"}


def test_los_valores_del_trabajo_no_entran_en_los_calculos():
    """Ningun modulo de calculo, de reporte ni la carga de datos lee los
    resultados del trabajo, salvo el comparador. (El generador del informe de
    validacion solo los muestra a traves del comparador.)"""
    for carpeta in ("calculations", "reports", "modules", "components"):
        for archivo in (PROYECTO / carpeta).glob("*.py"):
            if archivo.name == "comparacion_anf.py":
                continue
            assert "resultados_referencia" not in archivo.read_text(encoding="utf-8"), archivo
    assert "resultados_referencia" not in (PROYECTO / "scripts" / "cargar_alutech.py").read_text(encoding="utf-8")


# ----------------------------------------------------------- exportaciones
def test_informe_integral_excel_y_pdf(datos, tmp_path):
    _, s = datos

    class Empresa:
        nombre_legal = "=Alutech, S. A. de C. V."  # un texto con "=" no debe exportarse como formula (B-10)
        moneda = "USD"

    hojas = hojas_informe(s)
    nombres = [n for n, _ in hojas]
    assert nombres == ["Estados originales", "Horizontal", "Vertical", "Indicadores", "Capital de trabajo", "DuPont", "WACC",
                       "Origen y aplicación", "Trazabilidad"]
    archivo = tmp_path / "informe.xlsx"
    archivo.write_bytes(secciones_a_excel(Empresa, "Informe", hojas))
    wb = load_workbook(archivo)
    assert len(wb.sheetnames) == len(hojas)
    formulas = [c.coordinate for ws in wb for fila in ws.iter_rows() for c in fila if c.data_type == "f"]
    assert formulas == []
    pdf = secciones_a_pdf(Empresa, "Informe", [sc for _, lista in hojas for sc in lista])
    assert pdf.startswith(b"%PDF") and len(pdf) > 20000


def test_excel_conserva_el_valor_sin_redondear(datos, tmp_path):
    _, s = datos
    from reports.secciones import indicadores as seccion_indicadores

    class Empresa:
        nombre_legal = "Alutech"
        moneda = "USD"

    seccion = seccion_indicadores(datos_todos(s), ind.LIQUIDEZ)
    archivo = tmp_path / "liq.xlsx"
    archivo.write_bytes(secciones_a_excel(Empresa, "Liquidez", [("Liquidez", [seccion])]))
    ws = load_workbook(archivo).active
    valores = [c.value for fila in ws.iter_rows() for c in fila if isinstance(c.value, float)]
    assert any(abs(v - 383881547 / 205973230) < 1e-9 for v in valores)


# ---------------------------------------------------------------- migracion
def test_migracion_v3_a_v4_conserva_todo(tmp_path, monkeypatch):
    from conftest import construir_bd_v0

    from database import migrations

    bd = construir_bd_v0(tmp_path / "financiera.db")
    monkeypatch.setattr(migrations, "VERSION_ACTUAL", 3)
    monkeypatch.setattr(migrations, "PASOS", PASOS[:3])
    migrar(bd)
    assert version_esquema(bd) == 3
    monkeypatch.undo()
    antes = tmp_path / "v3.db"
    antes.write_bytes(bd.read_bytes())
    registro = migrar(bd)
    assert version_esquema(bd) == 4
    assert any("Copia previa" in r for r in registro)
    # Cada fila de cada tabla v3 sigue igual en v4 (columnas de v3); el registro
    # de migraciones solo agrega la fila de la version 4.
    con_a, con = sqlite3.connect(antes), sqlite3.connect(bd)
    try:
        for (tabla,) in con_a.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
            columnas = ", ".join(r[1] for r in con_a.execute(f'PRAGMA table_info("{tabla}")'))
            filas_a = con_a.execute(f'SELECT {columnas} FROM "{tabla}" ORDER BY rowid').fetchall()
            filas_d = con.execute(f'SELECT {columnas} FROM "{tabla}" ORDER BY rowid').fetchall()
            if tabla == "schema_migration":
                assert filas_d[:len(filas_a)] == filas_a and len(filas_d) == len(filas_a) + 1
            else:
                assert filas_d == filas_a, tabla
        assert con.execute("SELECT COUNT(*) FROM account WHERE grupo_analisis IS NOT NULL").fetchone()[0] == 0
    finally:
        con_a.close()
        con.close()
    con = sqlite3.connect(bd)
    try:
        tablas = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        disparadores = {r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='trigger'")}
        grupos = con.execute("SELECT COUNT(*) FROM account WHERE grupo_analisis IS NOT NULL").fetchone()[0]
    finally:
        con.close()
    assert {"fuente_importe", "dato_complementario"} <= tablas
    assert "trg_fuente_importe_cerrado_insert" in disparadores
    assert grupos == 0  # la migracion no clasifica nada por su cuenta
    assert migrar(bd) == []  # idempotente


# ------------------------------------------------------------- paginas reales
def test_paginas_con_los_datos_de_alutech(bd_cargada, tmp_path):
    """Todas las paginas se renderizan sin excepciones con los cinco ejercicios
    cargados (AppTest en subproceso, ver tests/humo_paginas.py)."""
    copia = tmp_path / "financiera.db"
    copia.write_bytes(bd_cargada[0].read_bytes())
    proceso = subprocess.run([sys.executable, str(PROYECTO / "tests" / "humo_paginas.py"), str(copia)], capture_output=True,
                             text=True, encoding="utf-8", timeout=900)
    assert proceso.returncode == 0, proceso.stderr[-3000:]
    resultados = json.loads(proceso.stdout.strip().splitlines()[-1])
    errores = {k: v["excepciones"] for k, v in resultados.items() if k != "_menu" and (v["excepciones"] or v["pagina"] != k)}
    assert errores == {}
    validacion = resultados["Validación › Contraste de resultados"]["tablas"][0]
    assert {f["Estado"] for f in validacion} == {"Coincidencia por redondeo", "Diferencia", "No aplica", "Resultado derivado"}


def test_los_indicadores_y_analisis_se_actualizan_al_cambiar_el_mapeo(tmp_path):
    """El grupo de analisis es configurable: al cambiarlo, los rubros e
    indicadores que lo usan se recalculan; los totales del estado no cambian."""
    from database.repositories import update_account

    ruta = construir_bd_como_la_real(tmp_path / "financiera.db")
    cargar(db_path=ruta, respaldar=False)
    init_db(db_path=ruta)
    with session_scope() as s:
        d = {x.anio: x for x in datos_todos(s)}[2025]
        antes = ind.calcular(d, "prueba_acida").valor
        total_antes = d.bs.total_activo
        update_account(s, get_account_by_codigo(s, "CN1105").id, grupo_analisis=None)  # inventario 2025 sin grupo
    with session_scope() as s:
        d = {x.anio: x for x in datos_todos(s)}[2025]
        despues = ind.calcular(d, "prueba_acida").valor
        assert d.bs.total_activo == total_antes
        # La denominacion identifica la cuenta como inventario: sigue excluida del activo liquido (Decision 1, escenario A).
        # Antes se exigia AC / PC, es decir, contar el inventario como activo liquido.
        assert despues == antes == (D(247705981) - D(69818060)) / D(371274007)
        assert any(c.codigo == "CN1105" for c, _, _ in d.sin_grupo)  # y se advierte
    connection.dispose_engine()
