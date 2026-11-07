"""Reconocimiento de cuentas en la prueba acida: falsos positivos y negativos de la auditoria de activos liquidos.
La formula residual del trabajo (5.6 c) no cambia. Las bases son temporales y se cargan desde los estados originales;
nunca data/financiera.db. Las cuentas ficticias existen solo en esas bases."""
from __future__ import annotations

import io
import json
import subprocess
import sys
from decimal import Decimal as D
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import pytest
from openpyxl import load_workbook

from calculations import indicadores as ind
from calculations.rubros import (
    AVISO_AMBIGUA,
    AVISO_CONTRADICCION,
    AVISO_INVENTARIO,
    AVISO_NO_INVENTARIO,
    AVISO_SALDO,
    INVENTARIO,
    NO_INVENTARIO,
    contradiccion_nombre_grupo,
    datos_todos,
    naturaleza_activo_corriente,
)
from database import connection
from database.connection import init_db, session_scope
from database.enums import CategoriaPrincipal as Cat
from database.enums import NaturalezaSaldo as Nat
from database.enums import Subcategoria as Sub
from database.enums import TipoEstadoFinanciero as Tipo
from database.repositories import (
    create_account,
    deactivate_account,
    delete_entry,
    get_account_by_codigo,
    get_fiscal_period,
    get_or_create_fiscal_period,
    list_accounts,
    save_company,
    update_account,
    upsert_entry,
)
from database.seed import seed_default_accounts
from reports import secciones as sec
from reports.exportar_secciones import secciones_a_excel, secciones_a_pdf
from reports.informe_integral import hojas_informe
from scripts.cargar_alutech import cargar

PROYECTO = Path(__file__).resolve().parent.parent
MILLON = D("1000000")
EMPRESA = SimpleNamespace(nombre_legal="Prueba", moneda="USD")


@pytest.fixture()
def bd(tmp_path):
    ruta = tmp_path / "financiera.db"
    init_db(db_path=ruta)
    with session_scope() as s:
        seed_default_accounts(s)
        save_company(s, nombre_legal="Prueba", nombre_comercial="Prueba", actividad_economica="x", pais="x", moneda="USD",
                     anio_inicial_analisis=2021)
        periodo, _ = get_or_create_fiscal_period(s, 2021)
        for c in list_accounts(s):
            if c.categoria_principal.value in ("ACTIVO", "PASIVO", "PATRIMONIO"):
                upsert_entry(s, fiscal_period_id=periodo.id, account_id=c.id, valor="0", tipo=Tipo.BALANCE)
    connection.dispose_engine()
    cargar(db_path=ruta, respaldar=False)
    init_db(db_path=ruta)
    yield ruta
    connection.dispose_engine()


def ejercicios(s) -> dict:
    return {d.anio: d for d in datos_todos(s) if d.tiene_datos}


def valor(d, clave):
    return ind.calcular(d, clave).valor


def _nueva_activo(codigo: str, nombre: str, importe=1000000, naturaleza: str = "DEUDORA", grupo: str | None = None) -> None:
    with session_scope() as s:
        c = create_account(s, codigo=codigo, nombre=nombre, categoria_principal=Cat.ACTIVO, subcategoria=Sub.CORRIENTE,
                           naturaleza_saldo=Nat(naturaleza), orden_presentacion=9999, grupo_analisis=grupo)
        upsert_entry(s, fiscal_period_id=get_fiscal_period(s, 2025).id, account_id=c.id, valor=D(str(importe)), tipo=Tipo.BALANCE)


def quitar_cuenta(codigo: str, anio: int) -> None:
    with session_scope() as s:
        c = get_account_by_codigo(s, codigo)
        delete_entry(s, fiscal_period_id=get_fiscal_period(s, anio).id, account_id=c.id, tipo=Tipo.BALANCE)
        deactivate_account(s, c.id)


def celdas_excel(hojas) -> list:
    libro = load_workbook(io.BytesIO(secciones_a_excel(EMPRESA, "Prueba", hojas)))
    return [c for ws in libro.worksheets for fila in ws.iter_rows(values_only=True) for c in fila if c is not None]


def cuenta(nombre="Inventarios", **k):
    return SimpleNamespace(**({"grupo_analisis": None, "categoria_principal": Cat.ACTIVO, "subcategoria": Sub.CORRIENTE,
                               "naturaleza_saldo": Nat.DEUDORA, "nombre": nombre} | k))


def foto(s, anio=2025):
    d = ejercicios(s)[anio]
    return SimpleNamespace(pa=valor(d, "prueba_acida"), ac=d.bs.activo_corriente.subtotal, inv=d.rubro("INVENTARIOS"), pc=d.bs.pasivo_corriente.subtotal)


def base():
    with session_scope() as s:
        return foto(s)


# ---------------------------------------------------------------- 1. listas cerradas, sin base de datos
INVENTARIOS = ["Inventarios", "Inventario", "Materias primas", "Materia prima", "Productos en proceso", "Productos terminados", "Mercaderías",
               "Inventario en tránsito", "Existencias", "Inventario de materias primas", "Inventario (Materiales, Suministros, etc.)", "Inventarios - neto"]
NO_INVENTARIOS = ["Efectivo en caja", "Caja general", "Bancos", "Cuentas por cobrar comerciales", "Cuentas por cobrar relacionadas", "Gastos pagados por anticipado",
                  "Pagos anticipados", "Inversiones", "Efectivo y equivalentes", "Caja y bancos", "Deudores comerciales", "Cuentas comerciales por cobrar",
                  "Cuentas por cobrar a partes relacionadas (corriente)", "Inversiones en bonos", "Caja", "Banco", "Caja chica", "Documentos por cobrar",
                  "Clientes", "Otras cuentas por cobrar", "Cuentas por cobrar"]
FALSOS_POSITIVOS = ["Banco de materiales", "Bancos de alimentos", "Cuentas por cobrar y materias primas", "Impuestos y productos terminados", "Caja de herramientas",
                    "Cajas de embalaje", "Caja fuerte (equipo)", "Caja y terrenos", "Inversiones en maquinaria", "Inversiones en terrenos",
                    "Inventario de terrenos", "Inventario de oficina", "Inventario de maquinaria", "Inventario de edificios", "Inventario de activos fijos",
                    "Inventario físico de caja", "Existencias de terrenos", "Inventarios de terceros en consignación", "Inversiones en edificios",
                    "Cuentas por cobrar a largo plazo", "Documentos por cobrar a largo plazo", "Caja chica de maquinaria", "Clientes y materias primas", "Banco y terrenos"]
AMBIGUAS = ["Otras cuentas por cobrar (corriente)", "Otros activos corrientes", "Depósitos bancarios", "Disponibilidades",
            "Activos por impuestos", "Depósitos en garantía", "Activos varios", "Cuenta genérica", "Terrenos", "Edificios", "Maquinaria", "Maquinaria y equipo",
            "Depreciación acumulada", "Provisión de inventario", "Inventarios y otros", "Materias primas y otros", "Materiales", "Productos",
            "Efectivo restringido", "Impuesto diferido", "Deudores incobrables"]


@pytest.mark.parametrize("nombre", INVENTARIOS)
def test_inventario_por_denominacion_completa(nombre):
    assert naturaleza_activo_corriente(cuenta(nombre)) == INVENTARIO


@pytest.mark.parametrize("nombre", NO_INVENTARIOS)
def test_no_inventario_por_denominacion_completa(nombre):
    assert naturaleza_activo_corriente(cuenta(nombre)) == NO_INVENTARIO


@pytest.mark.parametrize("nombre", FALSOS_POSITIVOS + AMBIGUAS)
def test_lo_demas_no_se_clasifica(nombre):
    assert naturaleza_activo_corriente(cuenta(nombre)) is None


@pytest.mark.parametrize("nombre,esperado", [("MATERIAS PRIMAS", INVENTARIO), ("materias primas", INVENTARIO), ("  Materias   primas ", INVENTARIO), ("Matérias Prímas", INVENTARIO),
                                             ("MERCADERIAS", INVENTARIO), ("inventario en transito", INVENTARIO), ("BANCOS", NO_INVENTARIO), ("  caja   GENERAL ", NO_INVENTARIO),
                                             # la normalizacion no quita palabras ni signos: no amplia las coincidencias
                                             ("Materias primas.", None), ("Mis materias primas", None), ("Materias primas 2", None), ("Inventarios-neto", None),
                                             ("Bancos locales", None), ("Bancos y otros", None), ("Caja general de maquinaria", None)])
def test_normalizacion_controlada(nombre, esperado):
    assert naturaleza_activo_corriente(cuenta(nombre)) == esperado


@pytest.mark.parametrize("nombre", ["Inventarios", "Caja general"])
def test_el_saldo_debe_ser_deudor(nombre):
    assert naturaleza_activo_corriente(cuenta(nombre, naturaleza_saldo=Nat.ACREEDORA)) is None
    assert naturaleza_activo_corriente(cuenta(nombre), D("-1")) is None
    assert naturaleza_activo_corriente(cuenta(nombre), D("1")) is not None
    assert naturaleza_activo_corriente(cuenta(nombre), D("0")) is None  # sin saldo deudor no hay reconocimiento


@pytest.mark.parametrize("nombre", ["Inventarios", "Caja general"])
def test_solo_reconoce_el_activo_corriente_sin_grupo(nombre):
    assert naturaleza_activo_corriente(cuenta(nombre, subcategoria=Sub.NO_CORRIENTE)) is None
    assert naturaleza_activo_corriente(cuenta(nombre, categoria_principal=Cat.PASIVO)) is None
    assert naturaleza_activo_corriente(cuenta(nombre, grupo_analisis="EFECTIVO")) is None
    assert naturaleza_activo_corriente(cuenta(nombre, grupo_analisis="INVENTARIOS")) is None  # lo decide el grupo, no el nombre


@pytest.mark.parametrize("nombre,grupo,bloquea", [("Inventarios", "EFECTIVO", True), ("Materias primas", "PAGOS_ANTICIPADOS", True), ("Caja general", "INVENTARIOS", True),
                                                  ("Terrenos", "EFECTIVO", True), ("Inversiones en maquinaria", "INVERSIONES_CP", True), ("Inventario de terrenos", "INVENTARIOS", True),
                                                  ("Bancos", "PAGOS_ANTICIPADOS", False), ("Gastos pagados por anticipado", "EFECTIVO", False)])
def test_contradiccion_de_nombre_y_grupo(nombre, grupo, bloquea):
    contradiccion = contradiccion_nombre_grupo(cuenta(nombre, grupo_analisis=grupo))
    assert contradiccion is not None and contradiccion[1] is bloquea


@pytest.mark.parametrize("nombre,grupo", [("Inventarios", "INVENTARIOS"), ("Materias primas", "INVENTARIOS"), ("Bancos", "EFECTIVO"), ("Cuentas por cobrar", "CXC_RELACIONADAS_CP"),
                                          ("Banco de materiales", "INVENTARIOS"), ("Cuenta genérica", "EFECTIVO")])
def test_sin_contradiccion(nombre, grupo):
    assert contradiccion_nombre_grupo(cuenta(nombre, grupo_analisis=grupo)) is None


def test_contradiccion_solo_examina_el_activo_corriente():
    assert contradiccion_nombre_grupo(cuenta("Inventarios")) is None  # sin grupo
    assert contradiccion_nombre_grupo(cuenta("Terrenos", subcategoria=Sub.NO_CORRIENTE, grupo_analisis="PPE")) is None
    assert contradiccion_nombre_grupo(cuenta("Inventarios", grupo_analisis="NO_EXISTE")) is None  # lo trata grupo_incongruente


# ---------------------------------------------------------------- 2. efecto en la prueba acida
@pytest.mark.parametrize("nombre", ["Banco de materiales", "Cuentas por cobrar y materias primas", "Caja de herramientas", "Caja y terrenos", "Inversiones en maquinaria",
                                    "Inventario de terrenos", "Inventario de oficina", "Inversiones en terrenos", "Documentos por cobrar a largo plazo", "Otros activos corrientes"])
def test_falso_positivo_o_ambigua_da_no_calculable(bd, nombre):
    b = base()
    _nueva_activo("ZP1", nombre)
    with session_scope() as s:
        lista = ejercicios(s)
        d = lista[2025]
        r = ind.calcular(d, "prueba_acida")
        assert r.valor is None and "ZP1" in r.motivo and "grupo de análisis" in r.motivo and "No se sabe" in r.motivo
        assert d.rubro("INVENTARIOS") == b.inv  # no se supone inventario ni se resta como cero
        assert ind.formatear(r.indicador.unidad, r.valor) == "No calculable"
        assert ind.es_provisional(ind.calcular(d, "ppi"))  # el resto de lo que usa inventarios queda avisado
        assert valor(d, "ctn") is not None and valor(d, "razon_corriente") is not None  # los totales son ciertos
        assert valor(lista[2024], "prueba_acida") is not None


@pytest.mark.parametrize("nombre", ["Materias primas", "Productos en proceso", "Productos terminados", "Mercaderías", "Inventario en tránsito"])
def test_falso_negativo_se_reconoce_como_inventario(bd, nombre):
    b = base()
    _nueva_activo("ZN1", nombre)
    with session_scope() as s:
        d = ejercicios(s)[2025]
        r = ind.calcular(d, "prueba_acida")
        assert d.rubro("INVENTARIOS") == b.inv + MILLON and d.bs.activo_corriente.subtotal == b.ac + MILLON
        assert abs(r.valor - b.pa) < D("1E-20")  # entra al activo corriente y a los inventarios: el numerador no cambia
        assert "ZN1" in r.nota and "reconocido por su denominación" in r.nota
        assert ind.tiene_aviso_de_clasificacion(r) and not ind.es_provisional(r)
        assert [a.tipo for a in d.avisos_reconocimiento()] == [AVISO_INVENTARIO]


def test_no_inventario_entra_al_numerador_con_su_aviso(bd):
    b = base()
    _nueva_activo("ZR1", "Caja general")
    with session_scope() as s:
        d = ejercicios(s)[2025]
        r = ind.calcular(d, "prueba_acida")
        assert r.valor == (b.ac + MILLON - b.inv) / b.pc and "ZR1" in r.nota and "no inventario" in r.nota
        assert ind.tiene_aviso_de_clasificacion(r) and not ind.es_provisional(r)
        assert [a.tipo for a in d.avisos_reconocimiento()] == [AVISO_NO_INVENTARIO]
        assert "no inventario" not in (ind.calcular(d, "razon_corriente").nota or "")  # solo la prueba acida lleva este aviso


# ---------------------------------------------------------------- grupo con prioridad
@pytest.mark.parametrize("nombre,grupo", [("Inventarios", "EFECTIVO"), ("Materias primas", "PAGOS_ANTICIPADOS"), ("Terrenos", "EFECTIVO"), ("Caja general", "INVENTARIOS")])
def test_contradiccion_que_decide_la_formula_da_no_calculable(bd, nombre, grupo):
    b = base()
    _nueva_activo("ZC1", nombre, grupo=grupo)
    with session_scope() as s:
        d = ejercicios(s)[2025]
        r = ind.calcular(d, "prueba_acida")
        assert r.valor is None and "Contradicción" in r.motivo and "ZC1" in r.motivo
        assert get_account_by_codigo(s, "ZC1").grupo_analisis == grupo  # el grupo no se cambia
        assert d.rubro("INVENTARIOS") == b.inv + (MILLON if grupo == "INVENTARIOS" else 0)  # el nombre no se impone al grupo
        assert not d.sin_grupo and valor(d, "ctn") is not None and valor(d, "razon_corriente") is not None
        assert [a.tipo for a in d.avisos_reconocimiento()] == [AVISO_CONTRADICCION]


def test_inventarios_en_efectivo_no_se_trata_como_inventario(bd):
    with session_scope() as s:
        efectivo = ejercicios(s)[2025].g("EFECTIVO")
    _nueva_activo("ZC2", "Inventarios", grupo="EFECTIVO")
    with session_scope() as s:
        d = ejercicios(s)[2025]
        assert d.g("EFECTIVO") == efectivo + MILLON and not d.inventario_identificado()


def test_contradiccion_entre_grupos_no_inventario_solo_avisa(bd):
    b = base()
    _nueva_activo("ZC3", "Bancos", grupo="PAGOS_ANTICIPADOS")
    with session_scope() as s:
        r = ind.calcular(ejercicios(s)[2025], "prueba_acida")
        assert r.valor == (b.ac + MILLON - b.inv) / b.pc  # con cualquiera de los dos, entra al numerador
        assert "Contradicción" in r.nota and "ZC3" in r.nota and ind.tiene_aviso_de_clasificacion(r) and not ind.es_provisional(r)


def test_contradiccion_con_saldo_cero_no_afecta(bd):
    b = base()
    _nueva_activo("ZC4", "Inventarios", importe=0, grupo="EFECTIVO")
    with session_scope() as s:
        r = ind.calcular(ejercicios(s)[2025], "prueba_acida")
        assert r.valor == b.pa and r.nota is None


@pytest.mark.parametrize("nombre,grupo", [("Materias primas", "INVENTARIOS"), ("Banco de materiales", "INVENTARIOS"), ("Bancos", "EFECTIVO"), ("Cuenta genérica", "EFECTIVO")])
def test_grupo_valido_y_coherente_se_usa_sin_avisos(bd, nombre, grupo):
    b = base()
    _nueva_activo("ZG1", nombre, grupo=grupo)
    with session_scope() as s:
        r = ind.calcular(ejercicios(s)[2025], "prueba_acida")
        esperado = (b.ac + MILLON - b.inv - (MILLON if grupo == "INVENTARIOS" else 0)) / b.pc
        assert abs(r.valor - esperado) < D("1E-20") and r.nota is None


def test_grupo_de_otra_clase_es_contradiccion(bd):
    _nueva_activo("ZG2", "Inventarios", grupo="PRESTAMOS_CP")
    with session_scope() as s:
        r = ind.calcular(ejercicios(s)[2025], "prueba_acida")
        assert r.valor is None and "Contradicción" in r.motivo and "ZG2" in r.motivo and ".." not in r.motivo


# ---------------------------------------------------------------- saldos
@pytest.mark.parametrize("nombre,kw,texto", [("Caja general", {"naturaleza": "ACREEDORA"}, "saldo acreedor"), ("Inventarios", {"naturaleza": "ACREEDORA"}, "saldo acreedor"),
                                             ("Caja general", {"importe": -500}, "saldo negativo"), ("Inventarios", {"importe": -500}, "saldo negativo")])
def test_saldo_incompatible_da_no_calculable_y_lo_explica(bd, nombre, kw, texto):
    b = base()
    _nueva_activo("ZS1", nombre, **kw)
    with session_scope() as s:
        d = ejercicios(s)[2025]
        r = ind.calcular(d, "prueba_acida")
        assert r.valor is None and "ZS1" in r.motivo and texto in r.motivo and "No se sabe" not in r.motivo
        assert d.rubro("INVENTARIOS") == b.inv and not d.inventario_identificado()  # un inventario negativo no se resta
        assert [a.tipo for a in d.avisos_reconocimiento()] == [AVISO_SALDO]


@pytest.mark.parametrize("nombre", ["Banco de materiales", "Materias primas", "Caja general"])
def test_saldo_cero_no_altera_el_resultado(bd, nombre):
    b = base()
    _nueva_activo("ZS2", nombre, importe=0)
    with session_scope() as s:
        d = ejercicios(s)[2025]
        r = ind.calcular(d, "prueba_acida")
        assert r.valor == b.pa and r.nota is None and not d.sin_grupo and not d.avisos_reconocimiento()


def test_saldo_negativo_de_nombre_desconocido_sigue_ambiguo(bd):
    _nueva_activo("ZS3", "Cuenta genérica", importe=-500)
    with session_scope() as s:
        d = ejercicios(s)[2025]
        assert valor(d, "prueba_acida") is None and [a.tipo for a in d.avisos_reconocimiento()] == [AVISO_AMBIGUA]


# ---------------------------------------------------------------- combinaciones y reversion
def test_varias_cuentas_problematicas_a_la_vez(bd):
    _nueva_activo("ZV1", "Banco de materiales")
    _nueva_activo("ZV2", "Caja y terrenos")
    _nueva_activo("ZV3", "Materias primas")
    _nueva_activo("ZV4", "Caja general", importe=-1)
    _nueva_activo("ZV5", "Inventarios", grupo="EFECTIVO")
    with session_scope() as s:
        r = ind.calcular(ejercicios(s)[2025], "prueba_acida")
        assert r.valor is None
        for codigo in ("ZV1", "ZV2", "ZV4", "ZV5"):
            assert codigo in r.motivo
        assert "ZV3" not in r.motivo  # esta si se reconocio: no es la causa
    for codigo in ("ZV1", "ZV2", "ZV4", "ZV5"):
        quitar_cuenta(codigo, 2025)
    with session_scope() as s:
        r = ind.calcular(ejercicios(s)[2025], "prueba_acida")
        assert r.valor is not None and "ZV3" in r.nota


def test_el_aviso_solo_afecta_al_ejercicio_con_importe(bd):
    _nueva_activo("ZV6", "Banco de materiales")
    with session_scope() as s:
        lista = ejercicios(s)
        assert valor(lista[2025], "prueba_acida") is None
        for anio in (2021, 2022, 2023, 2024):
            r = ind.calcular(lista[anio], "prueba_acida")
            assert r.valor is not None and r.nota is None


def test_modificacion_y_reversion_recuperan_el_resultado_exacto(bd):
    b = base()
    _nueva_activo("ZM1", "Banco de materiales")
    with session_scope() as s:
        assert valor(ejercicios(s)[2025], "prueba_acida") is None
    with session_scope() as s:  # se clasifica
        update_account(s, get_account_by_codigo(s, "ZM1").id, grupo_analisis="INVENTARIOS")
    with session_scope() as s:
        r = ind.calcular(ejercicios(s)[2025], "prueba_acida")
        assert abs(r.valor - b.pa) < D("1E-20") and r.nota is None
    with session_scope() as s:  # el nombre pasa a contradecir el grupo
        update_account(s, get_account_by_codigo(s, "ZM1").id, nombre="Bancos")
    with session_scope() as s:
        assert valor(ejercicios(s)[2025], "prueba_acida") is None
    quitar_cuenta("ZM1", 2025)  # eliminacion de la cuenta
    with session_scope() as s:
        f = foto(s)
        assert (f.pa, f.ac, f.inv, f.pc) == (b.pa, b.ac, b.inv, b.pc)


def test_modificar_el_saldo_cambia_el_reconocimiento(bd):
    b = base()
    _nueva_activo("ZM2", "Caja general")
    with session_scope() as s:
        c = get_account_by_codigo(s, "ZM2")
        upsert_entry(s, fiscal_period_id=get_fiscal_period(s, 2025).id, account_id=c.id, valor=D("-1"), tipo=Tipo.BALANCE)
    with session_scope() as s:
        assert valor(ejercicios(s)[2025], "prueba_acida") is None
    with session_scope() as s:
        c = get_account_by_codigo(s, "ZM2")
        delete_entry(s, fiscal_period_id=get_fiscal_period(s, 2025).id, account_id=c.id, tipo=Tipo.BALANCE)
    with session_scope() as s:
        assert valor(ejercicios(s)[2025], "prueba_acida") == b.pa


# ---------------------------------------------------------------- pantalla, PDF y Excel
def _escenario_calculado():
    _nueva_activo("ZI1", "Materias primas")
    _nueva_activo("ZI2", "Caja general")
    _nueva_activo("ZI3", "Bancos", grupo="PAGOS_ANTICIPADOS")


def _textos_de_la_pagina(ruta) -> str:
    connection.dispose_engine()
    proceso = subprocess.run([sys.executable, str(PROYECTO / "tests" / "humo_prueba_acida.py"), str(ruta)],
                             capture_output=True, text=True, encoding="utf-8", timeout=280, cwd=str(PROYECTO))
    assert proceso.returncode == 0, proceso.stderr[-1500:]
    return " ".join(json.loads(proceso.stdout.strip().splitlines()[-1])["textos"])


def test_reportes_llevan_los_avisos_de_un_resultado_calculado(bd):
    _escenario_calculado()
    with session_scope() as s:
        lista = list(ejercicios(s).values())
        for seccion in (sec.indicadores(lista, ind.LIQUIDEZ), sec.capital_trabajo(lista)):
            notas = " ".join(seccion.notas)
            assert all(c in notas for c in ("ZI1", "ZI2", "ZI3")) and "no inventario" in notas and "Contradicción" in notas
        tabla = {f[1]: f[5] for f in sec.clasificacion(lista).filas}
        assert "Inventario reconocido" in tabla["ZI1"] and "No inventario reconocido" in tabla["ZI2"] and "ZI3" not in tabla
        hojas = hojas_informe(s, lista)
        assert any("ZI2" in str(c) and "no inventario" in str(c) for c in celdas_excel(hojas))
        assert secciones_a_pdf(EMPRESA, "Prueba", [x for _, l in hojas for x in l]).startswith(b"%PDF")


@pytest.mark.parametrize("nombre,kw,texto", [("Banco de materiales", {}, "No se sabe"), ("Inventarios", {"grupo": "EFECTIVO"}, "Contradicción"), ("Caja general", {"importe": -500}, "saldo negativo")])
def test_reportes_explican_el_no_calculable(bd, nombre, kw, texto):
    _nueva_activo("ZI4", nombre, **kw)
    with session_scope() as s:
        lista = list(ejercicios(s).values())
        for seccion in (sec.indicadores(lista, ind.LIQUIDEZ), sec.capital_trabajo(lista)):
            assert any("ZI4" in n and texto in n for n in seccion.notas)
        fila = next(f for f in sec.capital_trabajo(lista).filas if str(f[0]).startswith("2025"))
        assert fila[7] == "No calculable"
        celdas = celdas_excel(hojas_informe(s, lista))
        assert any("ZI4" in str(c) and texto in str(c) for c in celdas) and "No calculable" in celdas


def test_cuenta_nueva_participa_en_el_informe(bd):
    _nueva_activo("ZI5", "Mercaderías")
    with session_scope() as s:
        lista = list(ejercicios(s).values())
        assert "Cuentas sin clasificar" in dict(hojas_informe(s, lista))
        fila = next(f for f in sec.capital_trabajo(lista).filas if str(f[0]).startswith("2025"))
        assert fila[7] != "No calculable"


def test_la_pagina_explica_el_no_calculable(bd):
    _nueva_activo("ZI6", "Banco de materiales")
    textos = _textos_de_la_pagina(bd)
    assert "Prueba ácida" in textos and "No se sabe si" in textos and "ZI6" in textos


def test_la_pagina_muestra_el_aviso_de_un_resultado_calculado(bd):
    _escenario_calculado()
    textos = _textos_de_la_pagina(bd)
    for parte in ("ZI1", "ZI2", "ZI3", "reconocido por su denominación", "no inventario", "Contradicción"):
        assert parte in textos


# ---------------------------------------------------------------- matriz final de cierre (decisiones 1 a 4 del usuario)
MATRIZ_A_INVENTARIO = ["Inventarios", "Inventario", "Existencias", "Materias primas", "Productos en proceso", "Productos terminados", "Mercaderías",
                       "Inventario en tránsito", "Inventario de materias primas", "Inventario de productos en proceso", "Inventario de productos terminados"]
MATRIZ_A_NO_CLASIFICABLE = ["Inventario de terrenos", "Inventario de oficina", "Inventario de maquinaria", "Inventario de edificios"]
MATRIZ_B_NO_INVENTARIO = ["Efectivo", "Caja", "Banco", "Caja chica", "Clientes", "Cuentas por cobrar", "Cuentas comerciales por cobrar", "Otras cuentas por cobrar",
                          "Documentos por cobrar", "Inversiones", "Pagos anticipados", "Anticipos al impuesto sobre la renta", "Certificados de depósitos a plazo fijo (corriente)"]
MATRIZ_C_NO_CALCULABLE = [("Banco de materiales", None), ("Caja de herramientas", None), ("Caja y terrenos", None), ("Cuentas por cobrar y materias primas", None),
                          ("Inversiones en maquinaria", None), ("Inversiones en terrenos", None), ("Otros activos corrientes", None), ("Inversiones en edificios", None),
                          ("Cuentas por cobrar a largo plazo", None), ("Documentos por cobrar a largo plazo", None), ("Inventarios", "EFECTIVO"), ("Materias primas", "EFECTIVO"), ("Banco", "INVENTARIOS")]


def _sin_cambios(b) -> None:
    """Paso 4 de la reversibilidad: el resultado original se recupera exactamente."""
    with session_scope() as s:
        f = foto(s)
    assert (f.pa, f.ac, f.inv, f.pc) == (b.pa, b.ac, b.inv, b.pc)


@pytest.mark.parametrize("nombre", MATRIZ_A_INVENTARIO)
def test_matriz_a_inventario_y_reversion(bd, nombre):
    b = base()
    _nueva_activo("ZF1", nombre)
    with session_scope() as s:
        d = ejercicios(s)[2025]
        assert naturaleza_activo_corriente(get_account_by_codigo(s, "ZF1"), MILLON) == INVENTARIO
        r = ind.calcular(d, "prueba_acida")
        assert abs(r.valor - b.pa) < D("1E-20") and d.rubro("INVENTARIOS") == b.inv + MILLON and "ZF1" in r.nota
    quitar_cuenta("ZF1", 2025)
    _sin_cambios(b)


@pytest.mark.parametrize("nombre", MATRIZ_B_NO_INVENTARIO)
def test_matriz_b_no_inventario_y_reversion(bd, nombre):
    b = base()
    _nueva_activo("ZF2", nombre)
    with session_scope() as s:
        d = ejercicios(s)[2025]
        assert naturaleza_activo_corriente(get_account_by_codigo(s, "ZF2"), MILLON) == NO_INVENTARIO
        r = ind.calcular(d, "prueba_acida")
        assert r.valor == (b.ac + MILLON - b.inv) / b.pc and d.rubro("INVENTARIOS") == b.inv
        assert "ZF2" in r.nota and nombre in r.nota and "no inventario" in r.nota and "denominación" in r.nota  # nombre, clasificacion y motivo
        assert ind.tiene_aviso_de_clasificacion(r) and not ind.es_provisional(r)
    quitar_cuenta("ZF2", 2025)
    _sin_cambios(b)


@pytest.mark.parametrize("nombre", MATRIZ_A_INVENTARIO + MATRIZ_B_NO_INVENTARIO)
@pytest.mark.parametrize("kw", [{"naturaleza_saldo": Nat.ACREEDORA}, {"subcategoria": Sub.NO_CORRIENTE}, {"grupo_analisis": "EFECTIVO"}], ids=["acreedor", "no_corriente", "con_grupo"])
def test_matriz_exige_activo_corriente_saldo_deudor_y_sin_grupo(nombre, kw):
    assert naturaleza_activo_corriente(cuenta(nombre, **kw)) is None


@pytest.mark.parametrize("nombre", MATRIZ_A_INVENTARIO + MATRIZ_B_NO_INVENTARIO)
def test_matriz_saldo_cero_o_negativo_no_se_acepta(nombre):
    assert naturaleza_activo_corriente(cuenta(nombre), D("0")) is None
    assert naturaleza_activo_corriente(cuenta(nombre), D("-1")) is None


@pytest.mark.parametrize("nombre", MATRIZ_A_NO_CLASIFICABLE)
def test_matriz_a_no_clasificable_y_reversion(bd, nombre):
    b = base()
    _nueva_activo("ZF3", nombre)
    with session_scope() as s:
        d = ejercicios(s)[2025]
        assert naturaleza_activo_corriente(get_account_by_codigo(s, "ZF3"), MILLON) is None
        r = ind.calcular(d, "prueba_acida")
        assert r.valor is None and "ZF3" in r.motivo and d.rubro("INVENTARIOS") == b.inv
    quitar_cuenta("ZF3", 2025)
    _sin_cambios(b)


@pytest.mark.parametrize("nombre,grupo", MATRIZ_C_NO_CALCULABLE)
def test_matriz_c_no_calculable_y_reversion(bd, nombre, grupo):
    b = base()
    _nueva_activo("ZF4", nombre, grupo=grupo)
    with session_scope() as s:
        d = ejercicios(s)[2025]
        r = ind.calcular(d, "prueba_acida")
        assert r.valor is None and "ZF4" in r.motivo and nombre in r.motivo
        assert ("Contradicción" in r.motivo) is (grupo is not None)
        assert ind.formatear(r.indicador.unidad, r.valor) == "No calculable"
        assert get_account_by_codigo(s, "ZF4").grupo_analisis == grupo  # el reconocimiento nunca sobrescribe el grupo
    quitar_cuenta("ZF4", 2025)
    _sin_cambios(b)


@pytest.mark.parametrize("nombre,esperado", [("CAJA", NO_INVENTARIO), ("caja chica", NO_INVENTARIO), ("  Caja   Chica ", NO_INVENTARIO), ("BANCO", NO_INVENTARIO), ("Documentos  por cobrar", NO_INVENTARIO),
                                             ("CLIENTES", NO_INVENTARIO), ("Inversiónes", NO_INVENTARIO), ("EXISTENCIAS", INVENTARIO), ("Inventario de Productos Terminados", INVENTARIO),
                                             ("Cajas", None), ("Cajachica", None), ("Caja-chica", None), ("Banco.", None), ("Banco central", None), ("Cliente", None), ("Clientes varios", None),
                                             ("Otras cuentas por cobrar (corriente)", None), ("Documento por cobrar", None), ("Inversión", None), ("Cuenta por cobrar", None)])
def test_matriz_normalizacion_de_los_nombres_autorizados(nombre, esperado):
    assert naturaleza_activo_corriente(cuenta(nombre)) == esperado


def test_saldo_cero_no_bloquea_ni_altera_con_nombre_autorizado(bd):
    b = base()
    _nueva_activo("ZF5", "Caja", importe=0)
    with session_scope() as s:
        d = ejercicios(s)[2025]
        assert valor(d, "prueba_acida") == b.pa and not d.avisos_reconocimiento() and not d.sin_grupo
    quitar_cuenta("ZF5", 2025)
    _sin_cambios(b)


def test_banco_con_efectivo_es_coherente_y_con_pagos_anticipados_solo_avisa(bd):
    b = base()
    _nueva_activo("ZF6", "Banco", grupo="EFECTIVO")
    with session_scope() as s:
        r = ind.calcular(ejercicios(s)[2025], "prueba_acida")
        assert r.valor == (b.ac + MILLON - b.inv) / b.pc and r.nota is None
    with session_scope() as s:
        update_account(s, get_account_by_codigo(s, "ZF6").id, grupo_analisis="PAGOS_ANTICIPADOS")
    with session_scope() as s:
        r = ind.calcular(ejercicios(s)[2025], "prueba_acida")
        assert r.valor == (b.ac + MILLON - b.inv) / b.pc and "Contradicción" in r.nota  # el numerador no cambia: se calcula con advertencia
    quitar_cuenta("ZF6", 2025)
    _sin_cambios(b)


def test_otra_incertidumbre_invalida_el_calculo_con_contradiccion_solo_informativa(bd):
    _nueva_activo("ZF7", "Banco", grupo="PAGOS_ANTICIPADOS")
    _nueva_activo("ZF8", "Cuenta genérica")
    with session_scope() as s:
        r = ind.calcular(ejercicios(s)[2025], "prueba_acida")
        assert r.valor is None and "ZF8" in r.motivo


def test_la_celda_del_reporte_coincide_con_la_pantalla(bd):
    """Hallado en la verificacion en navegador: la celda salia como «—» en PDF y Excel y la pantalla decia «No calculable»."""
    _nueva_activo("ZH1", "Banco de materiales")
    with session_scope() as s:
        lista = list(ejercicios(s).values())
        seccion = sec.indicadores(lista, ind.LIQUIDEZ)
        fila = next(f for f in seccion.filas if f[0] == "Prueba ácida")
        assert fila[8] == "No calculable" and all(isinstance(v, D) for v in fila[4:8])
        libro = load_workbook(io.BytesIO(secciones_a_excel(EMPRESA, "Prueba", [("Liquidez", [seccion])])))
        filas = [f for f in libro.worksheets[0].iter_rows(values_only=True) if f[0] == "Prueba ácida"]
        assert filas[0][8] == "No calculable"
        otra = next(f for f in seccion.filas if f[0].startswith("Razón corriente"))  # los demas indicadores no cambian
        assert all(isinstance(v, D) for v in otra[4:9])


def test_los_avisos_no_se_duplican(bd):
    _nueva_activo("ZF9", "Caja chica")
    _nueva_activo("ZG9", "Banco de materiales")
    with session_scope() as s:
        lista = list(ejercicios(s).values())
        for seccion in (sec.indicadores(lista, ind.LIQUIDEZ), sec.capital_trabajo(lista)):
            assert sum("ZG9" in n and "No se sabe" in n for n in seccion.notas) == 1
            assert len(seccion.notas) == len(set(seccion.notas))


# ---------------------------------------------------------------- Alutech
REFERENCIA = {2021: (235441043, 205973230, "1.1431"), 2022: (307602959, 231944180, "1.3262"), 2023: (288303225, 333120685, "0.8655"),
              2024: (316010367, 362966215, "0.8706"), 2025: (177887921, 371274007, "0.4791")}


def test_alutech_conserva_los_cinco_resultados_sin_avisos(bd):
    with session_scope() as s:
        lista = ejercicios(s)
        assert set(lista) == set(REFERENCIA)
        for anio, (numerador, denominador, redondeado) in REFERENCIA.items():
            d = lista[anio]
            r = ind.calcular(d, "prueba_acida")
            assert d.activo_corriente - d.rubro_registrado("INVENTARIOS") == numerador and d.pasivo_corriente == denominador
            assert Fraction(r.valor).limit_denominator(10**12) == Fraction(numerador, denominador)
            assert f"{r.valor:.4f}" == redondeado
            assert r.nota is None and r.motivo is None and not d.sin_grupo and not d.avisos_reconocimiento()


def test_ninguna_cuenta_real_de_activo_corriente_se_contradice(bd):
    with session_scope() as s:
        for c in list_accounts(s):
            if c.grupo_analisis:
                assert contradiccion_nombre_grupo(c) is None, c.nombre


@pytest.mark.parametrize("codigo,esperado", [("CB1101", NO_INVENTARIO), ("CB1102", NO_INVENTARIO), ("CB1103", NO_INVENTARIO), ("CB1104", NO_INVENTARIO), ("CB1105", NO_INVENTARIO),
                                             ("CB1106", None), ("CB1107", INVENTARIO), ("CB1108", NO_INVENTARIO), ("CB1109", NO_INVENTARIO), ("CN1101", NO_INVENTARIO),
                                             ("CN1102", NO_INVENTARIO), ("CN1103", NO_INVENTARIO), ("CN1104", NO_INVENTARIO), ("CN1105", INVENTARIO), ("CN1106", NO_INVENTARIO), ("CN1107", NO_INVENTARIO)])
def test_cuenta_real_sin_su_grupo(bd, codigo, esperado):
    with session_scope() as s:
        original = {a: valor(d, "prueba_acida") for a, d in ejercicios(s).items()}
        c = get_account_by_codigo(s, codigo)
        grupo = c.grupo_analisis
        assert grupo
        update_account(s, c.id, grupo_analisis=None)
    with session_scope() as s:
        c = get_account_by_codigo(s, codigo)
        assert naturaleza_activo_corriente(c) == esperado
        for anio, d in ejercicios(s).items():
            if esperado is None and any(x.codigo == codigo for x, _, _ in d.sin_grupo):
                assert valor(d, "prueba_acida") is None  # «Otras cuentas por cobrar» sin grupo: No calculable
            else:
                assert valor(d, "prueba_acida") == original[anio]
        update_account(s, c.id, grupo_analisis=grupo)
    with session_scope() as s:
        assert {a: valor(d, "prueba_acida") for a, d in ejercicios(s).items()} == original
