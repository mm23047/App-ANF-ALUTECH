"""Regresion de los hallazgos P-01 (datos faltantes), P-02 (cuentas sin grupo) y P-03 (utilidad atribuible) de la
auditoria de dinamismo. Las bases son temporales y se cargan desde los estados originales; nunca data/financiera.db.
Las cuentas ZZ... y los ejercicios ficticios existen solo en esas bases."""
from __future__ import annotations

import io
from decimal import Decimal as D
from types import SimpleNamespace

import pytest
from openpyxl import load_workbook
from sqlalchemy import delete

from calculations import indicadores as ind
from calculations.comparacion_anf import comparar, resumen
from calculations.comparativo import CLAVES_TABLA_3, CONCEPTOS, horizontal_conceptos, vertical_comparativo
from calculations.rubros import (
    BASE_DOCUMENTO,
    BASE_INGRESADA,
    BASE_SIMULACION,
    BASE_SUPUESTO_IGUALDAD,
    INVENTARIO,
    NO_INVENTARIO,
    datos_todos,
    grupo_incongruente,
    naturaleza_activo_corriente,
)
from calculations.wacc import calcular_wacc
from database import connection
from database.connection import init_db, session_scope
from database.enums import CategoriaPrincipal as Cat
from database.enums import EfectoCuenta as Ef
from database.enums import NaturalezaSaldo as Nat
from database.enums import Subcategoria as Sub
from database.enums import TipoEstadoFinanciero as Tipo
from database.models import DatoComplementario
from database.repositories import (
    EjercicioCerradoError,
    actualizar_atribucion,
    actualizar_dato_complementario,
    close_fiscal_period,
    create_account,
    deactivate_account,
    delete_entry,
    get_account_by_codigo,
    get_company,
    get_entries_map,
    get_fiscal_period,
    get_or_create_fiscal_period,
    list_accounts,
    list_history,
    registrar_atribucion_documentada,
    save_company,
    upsert_entry,
)
from database.seed import seed_default_accounts
from reports import secciones as sec
from calculations.dupont import compute_dupont
from database.repositories import update_account
from reports.excel_export import export_dupont_excel
from reports.exportar_secciones import secciones_a_excel
from reports.informe_integral import hojas_informe
from scripts.cargar_alutech import cargar

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
        for cuenta in list_accounts(s):
            if cuenta.categoria_principal.value in ("ACTIVO", "PASIVO", "PATRIMONIO"):
                upsert_entry(s, fiscal_period_id=periodo.id, account_id=cuenta.id, valor="0", tipo=Tipo.BALANCE)
    connection.dispose_engine()
    cargar(db_path=ruta, respaldar=False)
    init_db(db_path=ruta)
    yield ruta
    connection.dispose_engine()


def _tipo(cuenta) -> Tipo:
    return Tipo.BALANCE if cuenta.categoria_principal.value in ("ACTIVO", "PASIVO", "PATRIMONIO") else Tipo.RESULTADOS


def poner(anio: int, codigo: str, valor) -> None:
    with session_scope() as s:
        cuenta = get_account_by_codigo(s, codigo)
        upsert_entry(s, fiscal_period_id=get_fiscal_period(s, anio).id, account_id=cuenta.id, valor=D(str(valor)), tipo=_tipo(cuenta))


def borrar(anio: int, codigo: str) -> D:
    with session_scope() as s:
        cuenta = get_account_by_codigo(s, codigo)
        periodo = get_fiscal_period(s, anio).id
        previo = get_entries_map(s, periodo, _tipo(cuenta))[cuenta.id]
        delete_entry(s, fiscal_period_id=periodo, account_id=cuenta.id, tipo=_tipo(cuenta))
    return previo


def ejercicios(s) -> dict:
    return {d.anio: d for d in datos_todos(s) if d.tiene_datos}


def valor(d, clave):
    return ind.calcular(d, clave).valor


def celdas_excel(hojas) -> list:
    libro = load_workbook(io.BytesIO(secciones_a_excel(EMPRESA, "Prueba", hojas)))
    return [c for ws in libro.worksheets for fila in ws.iter_rows(values_only=True) for c in fila if c is not None]


# ------------------------------------------------------------- A. datos faltantes (P-01)
def test_saldo_en_cero_es_un_dato_y_conserva_su_tratamiento(bd):
    poner(2023, "CB1107", 0)
    with session_scope() as s:
        d = ejercicios(s)[2023]
        assert d.rubro_registrado("INVENTARIOS") == D("0.00")
        assert valor(d, "ppi") == 0  # cero real: cero dias
        assert valor(d, "rotacion_inventarios") is None and "denominador" in ind.calcular(d, "rotacion_inventarios").motivo
        assert valor(d, "prueba_acida") == valor(d, "razon_corriente")
        fila = horizontal_conceptos(list(ejercicios(s).values()), ("rubro:INVENTARIOS",))[0]
        assert fila.valores[2023] == 0 and fila.var_pct[2023] == D(-100)  # 141,069,442 a cero es una caida real
        assert fila.var_abs[2024] == D("116761311.00") and fila.causas[2024] == "No calculable"  # base cero


def test_saldo_no_registrado_no_produce_resultados_aparentes(bd):
    borrar(2022, "CB1104")
    with session_scope() as s:
        lista = ejercicios(s)
        d = lista[2022]
        assert d.rubro_registrado("CXC_COMERCIALES_PRESENTADA") is None
        for clave in ("rotacion_cxc", "ppc", "ciclo_operativo", "cce", "rotacion_cxc_total", "ppc_total"):
            r = ind.calcular(d, clave)
            assert r.valor is None and r.motivo, clave
        # Lo que no depende de la cuenta sigue calculandose
        assert valor(d, "ppi") is not None and valor(d, "ppp") is not None and valor(d, "margen_neto") is not None
        fila = {f.clave: f for f in horizontal_conceptos(list(lista.values()), CLAVES_TABLA_3)}["rubro:CXC_COMERCIALES_PRESENTADA"]
        assert fila.valores[2022] is None
        assert fila.var_abs[2022] is None and fila.var_pct[2022] is None and fila.causas[2022] == "Sin dato"
        assert fila.var_abs[2023] is None and fila.causas[2023] == "Sin dato"
        tablas = sec.horizontal_balance_tablas(list(lista.values()))
        tabla = next(f for f in tablas[0].filas if str(f[0]).startswith("Cuentas por cobrar"))
        assert tabla[2:5] == ["Sin dato", "Sin dato", "Sin dato"]


def test_inventario_no_registrado_deja_sin_calcular_la_prueba_acida(bd):
    borrar(2024, "CN1105")
    with session_scope() as s:
        d = ejercicios(s)[2024]
        for clave in ("prueba_acida", "rotacion_inventarios", "ppi", "ciclo_operativo", "cce"):
            assert valor(d, clave) is None, clave
        assert valor(d, "razon_corriente") is not None  # el activo corriente sigue registrado


def test_cartera_con_una_sola_de_sus_lineas_no_se_presenta_como_completa(bd):
    borrar(2022, "CB1106")  # quedan las comerciales, faltan las otras
    with session_scope() as s:
        d = ejercicios(s)[2022]
        assert d.rubro_registrado("CXC_COMERCIALES_PRESENTADA") == D("32581092.00")
        assert d.rubro_registrado("CXC_COMERCIALES_Y_OTRAS") is None


def test_ejercicio_solo_con_resultados_no_muestra_balance_en_cero(bd):
    with session_scope() as s:
        p, _ = get_or_create_fiscal_period(s, 2026)
        for codigo in ("CN4101", "CN5101"):
            cuenta = get_account_by_codigo(s, codigo)
            upsert_entry(s, fiscal_period_id=p.id, account_id=cuenta.id, valor=D("1000.00"), tipo=Tipo.RESULTADOS)
    with session_scope() as s:
        lista = list(ejercicios(s).values())
        for f in horizontal_conceptos(lista, ("rubro:EFECTIVO", "rubro:INVENTARIOS", "total_activo")):
            assert f.valores[2026] is None and f.var_pct[2026] is None and f.causas[2026] == "Sin dato", f.clave
        d = lista[-1]
        assert valor(d, "margen_bruto") == 0  # ingresos y costo registrados: margen real
        for clave in ("margen_operativo", "margen_neto", "roa", "roe", "ebitda"):
            assert valor(d, clave) is None, clave  # faltan gastos o impuesto


def test_lineas_no_aplicables_siguen_en_cero_como_en_la_tabla_7_1(bd):
    with session_scope() as s:
        d = ejercicios(s)[2021]
        for clave in ("s_gastos_personal", "s_depreciacion_amortizacion", "s_ingresos_financieros"):
            assert CONCEPTOS[clave].obtener(d) == 0, clave
        assert ejercicios(s)[2024].g("DETERIORO_CXC") == 0 and CONCEPTOS["s_deterioro_cxc"].obtener(ejercicios(s)[2024]) == 0


def test_linea_obligatoria_faltante_no_se_presenta_como_cero_en_el_vertical(bd):
    borrar(2022, "CB5101")
    with session_scope() as s:
        lista = list(ejercicios(s).values())
        filas = {f.clave: f for f in vertical_comparativo(lista, "ER")}
        assert filas["s_costo_ventas"].porcentajes[2022] is None
        assert filas["s_utilidad_bruta"].porcentajes[2022] is None
        assert filas["s_utilidad_neta"].porcentajes[2022] is None
        assert filas["s_ingresos"].porcentajes[2022] == 100
        seccion = sec.vertical(lista, "ER")
        fila = next(f for f in seccion.filas if f[0] == "Costo de ventas")
        assert fila[2] == "Sin dato"


def test_wacc_y_dupont_no_calculan_sobre_un_estado_incompleto(bd):
    borrar(2025, "CN8101")
    with session_scope() as s:
        lista = ejercicios(s)
        d = lista[2025]
        w = calcular_wacc(d)
        assert w.wacc_pct is None and "Falta un dato" in w.motivo
        for clave in ("margen_neto", "roa", "roe", "roa_dupont", "roe_dupont", "margen_neto_controladora", "roe_controladora"):
            assert valor(d, clave) is None, clave
        total, _ = sec.dupont(list(lista.values()))
        roe = next(f for f in total.filas if f[0] == ind.POR_CLAVE["roe_dupont"].nombre)
        assert roe[5] == "Sin dato" and roe[1] != "Sin dato"


def test_exportaciones_muestran_sin_dato_y_no_un_cien_negativo(bd):
    borrar(2022, "CB1104")
    with session_scope() as s:
        lista = list(ejercicios(s).values())
        celdas = celdas_excel([("Tablas", sec.horizontal_balance_tablas(lista))])
    assert "Sin dato" in celdas
    assert not any(isinstance(c, float) and c == -100 for c in celdas)


def test_restaurar_el_saldo_recupera_los_resultados_iniciales(bd):
    claves = ("ppc", "ciclo_operativo", "cce", "rotacion_cxc")
    with session_scope() as s:
        antes = {k: valor(ejercicios(s)[2022], k) for k in claves}
        resumen_antes = resumen(comparar(list(ejercicios(s).values())))
    previo = borrar(2022, "CB1104")
    with session_scope() as s:
        assert all(valor(ejercicios(s)[2022], k) is None for k in claves)
    poner(2022, "CB1104", previo)
    with session_scope() as s:
        assert {k: valor(ejercicios(s)[2022], k) for k in claves} == antes
        assert resumen(comparar(list(ejercicios(s).values()))) == resumen_antes


def test_datos_reales_conservan_las_cifras_del_documento(bd):
    with session_scope() as s:
        lista = ejercicios(s)
        assert round(valor(lista[2023], "ppc"), 2) == D("31.47")
        assert valor(lista[2025], "ciclo_operativo") == D("135.14")
        assert valor(lista[2025], "cce") == D("-55.52")
        assert round(valor(lista[2021], "prueba_acida"), 2) == D("1.14")
        assert round(valor(lista[2021], "roe"), 2) == D("47.21")
        assert round(calcular_wacc(lista[2021]).wacc_pct, 2) == D("14.59")
        assert resumen(comparar(list(lista.values())))["Coincide"] == 711


# ------------------------------------------------------------- B. cuentas nuevas sin clasificar (P-02)
def nueva_cuenta(codigo: str, categoria: str, subcategoria: str | None, grupo: str | None, anio: int, importe,
                 naturaleza: str = "DEUDORA", efecto: str | None = None) -> None:
    with session_scope() as s:
        cuenta = create_account(s, codigo=codigo, nombre=f"FICTICIA {codigo}", categoria_principal=Cat(categoria),
                                subcategoria=Sub(subcategoria) if subcategoria else None, naturaleza_saldo=Nat(naturaleza),
                                efecto=Ef(efecto) if efecto else None, orden_presentacion=9999, grupo_analisis=grupo)
        upsert_entry(s, fiscal_period_id=get_fiscal_period(s, anio).id, account_id=cuenta.id, valor=D(str(importe)), tipo=_tipo(cuenta))


def quitar_cuenta(codigo: str, anio: int) -> None:
    with session_scope() as s:
        cuenta = get_account_by_codigo(s, codigo)
        delete_entry(s, fiscal_period_id=get_fiscal_period(s, anio).id, account_id=cuenta.id, tipo=_tipo(cuenta))
        deactivate_account(s, cuenta.id)


def test_cuenta_de_inventario_bien_clasificada_entra_en_todos_los_calculos(bd):
    with session_scope() as s:
        antes = ejercicios(s)[2025]
        pa, inv = valor(antes, "prueba_acida"), antes.rubro("INVENTARIOS")
        ppi = valor(antes, "ppi")
    nueva_cuenta("ZZ1", "ACTIVO", "CORRIENTE", "INVENTARIOS", 2025, 1000000)
    with session_scope() as s:
        d = ejercicios(s)[2025]
        assert d.rubro("INVENTARIOS") == inv + 1000000
        assert abs(valor(d, "prueba_acida") - pa) < D("1E-20")  # entra y sale: no cambia
        assert valor(d, "ppi") > ppi
        assert not d.sin_grupo and not ind.es_provisional(ind.calcular(d, "prueba_acida"))


def test_activo_corriente_sin_grupo_entra_en_totales_y_marca_lo_que_no_se_puede_afirmar(bd):
    with session_scope() as s:
        d0 = ejercicios(s)[2025]
        ac, inv, pc = d0.bs.activo_corriente.subtotal, d0.rubro("INVENTARIOS"), d0.bs.pasivo_corriente.subtotal
    nueva_cuenta("ZZ2", "ACTIVO", "CORRIENTE", None, 2025, 1000000)
    with session_scope() as s:
        lista = ejercicios(s)
        d = lista[2025]
        assert d.bs.activo_corriente.subtotal == ac + 1000000  # no queda fuera del total
        assert d.rubro("INVENTARIOS") == inv  # no se supone que sea inventario
        assert valor(d, "razon_corriente") == (ac + 1000000) / pc  # los totales son ciertos
        assert not ind.es_provisional(ind.calcular(d, "razon_corriente")) and not ind.es_provisional(ind.calcular(d, "ctn"))
        # Decision 1, escenario B: naturaleza desconocida. La prueba acida pasa de provisional a no calculable.
        acida = ind.calcular(d, "prueba_acida")
        assert acida.valor is None and "ZZ2" in acida.motivo and "grupo" in acida.motivo
        for clave in ("ppi", "ppc", "ciclo_operativo", "cce", "razon_efectivo", "razon_tesoreria"):
            r = ind.calcular(d, clave)
            assert ind.es_provisional(r) and "ZZ2" in r.nota, clave
        assert not ind.es_provisional(ind.calcular(lista[2024], "prueba_acida"))  # otro ejercicio no se afecta
        lista_ = list(lista.values())
        assert any("ZZ2" in n for n in sec.horizontal_balance_tablas(lista_)[0].notas)
        assert sec.clasificacion(lista_).filas[0][1] == "ZZ2"
        assert any("ZZ2" in str(c) for c in celdas_excel([("Tablas", sec.horizontal_balance_tablas(lista_))]))
        assert hojas_informe(s, lista_)[0][0] == "Cuentas sin clasificar"


def test_pasivo_sin_grupo_no_se_supone_sin_costo(bd):
    with session_scope() as s:
        d0 = ejercicios(s)[2025]
        pasivo, wacc0 = d0.bs.total_pasivo, calcular_wacc(d0).wacc_pct
    nueva_cuenta("ZZ3", "PASIVO", "CORRIENTE", None, 2025, 800000, naturaleza="ACREEDORA")
    with session_scope() as s:
        d = ejercicios(s)[2025]
        w = calcular_wacc(d)
        assert w.wacc_pct is None and "ZZ3" in w.motivo and not w.disponible
        assert any(l.tipo == "SIN CLASIFICAR" and l.codigo == "ZZ3" for l in w.lineas)
        assert d.bs.total_pasivo == pasivo + 800000
        assert valor(d, "endeudamiento") == (pasivo + 800000) / d.bs.total_activo * 100
        assert ind.es_provisional(ind.calcular(d, "ppp"))
    quitar_cuenta("ZZ3", 2025)
    with session_scope() as s:
        assert calcular_wacc(ejercicios(s)[2025]).wacc_pct == wacc0


def test_deuda_bien_clasificada_entra_en_el_wacc_y_sin_tasa_no_se_inventa(bd):
    with session_scope() as s:
        w0 = calcular_wacc(ejercicios(s)[2025])
    nueva_cuenta("ZZ4", "PASIVO", "CORRIENTE", "PRESTAMOS_CP", 2025, 800000, naturaleza="ACREEDORA")
    with session_scope() as s:
        w = calcular_wacc(ejercicios(s)[2025])
        assert w.disponible and w.pct_deuda_financiera > w0.pct_deuda_financiera
    nueva_cuenta("ZZ5", "PASIVO", "CORRIENTE", "BONOS_CP", 2025, 800000, naturaleza="ACREEDORA")
    with session_scope() as s:
        w = calcular_wacc(ejercicios(s)[2025])
        assert w.wacc_pct is None and "Falta la tasa" in w.motivo


def test_gasto_sin_grupo_se_muestra_para_que_el_vertical_sume(bd):
    with session_scope() as s:
        gop = ejercicios(s)[2025].rubro("GASTOS_OPERATIVOS_ANF")
    nueva_cuenta("ZZ6", "GASTOS_OPERATIVOS", "ADMINISTRACION", None, 2025, 500000)
    with session_scope() as s:
        lista = list(ejercicios(s).values())
        d = lista[-1]
        assert d.rubro("GASTOS_OPERATIVOS_ANF") == gop  # no se supone que sea un gasto de esa definicion
        filas = {f.clave: f for f in vertical_comparativo(lista, "ER")}
        assert filas["s_sin_clasificar_operativas"].valores[2025] == D("-500000.00")
        lineas = ("s_utilidad_bruta", "s_gastos_administracion", "s_gastos_venta", "s_deterioro_cxc", "s_gastos_personal",
                  "s_depreciacion_amortizacion", "s_sin_clasificar_operativas")
        # 2025 presenta los otros ingresos despues del resultado operativo
        assert sum(filas[c].valores[2025] for c in lineas) == filas["s_utilidad_operativa"].valores[2025]
        assert ind.es_provisional(ind.calcular(d, "ebitda"))


def test_patrimonio_sin_grupo_marca_el_enfoque_de_la_controladora(bd):
    nueva_cuenta("ZZ7", "PATRIMONIO", "RESERVAS", None, 2021, 100000, naturaleza="ACREEDORA")
    with session_scope() as s:
        d = ejercicios(s)[2021]
        assert ind.es_provisional(ind.calcular(d, "maf_controladora"))
        assert ind.es_provisional(ind.calcular(d, "roe_controladora"))
        assert not ind.es_provisional(ind.calcular(d, "roe"))


def test_grupo_de_otra_naturaleza_se_rechaza_y_no_altera_el_rubro(bd):
    assert grupo_incongruente(Cat.ACTIVO, Sub.CORRIENTE, "PRESTAMOS_CP")
    assert grupo_incongruente(Cat.ACTIVO, Sub.CORRIENTE, "PPE")  # no corriente
    assert grupo_incongruente(Cat.COSTOS, None, "IMPUESTO_RENTA")
    assert grupo_incongruente(Cat.ACTIVO, Sub.CORRIENTE, "NO_EXISTE")
    assert grupo_incongruente(Cat.ACTIVO, Sub.CORRIENTE, "INVENTARIOS") is None
    assert grupo_incongruente(Cat.ACTIVO, Sub.CORRIENTE, None) is None
    with session_scope() as s:
        deuda = ejercicios(s)[2025].rubro("DEUDA_FINANCIERA")
    nueva_cuenta("ZZ8", "ACTIVO", "CORRIENTE", "PRESTAMOS_CP", 2025, 1000)
    with session_scope() as s:
        d = ejercicios(s)[2025]
        assert d.rubro("DEUDA_FINANCIERA") == deuda and [c.codigo for c, _, _ in d.sin_grupo] == ["ZZ8"]


def test_catalogo_real_tiene_grupos_coherentes_y_cero_sin_grupo_no_avisa(bd):
    with session_scope() as s:
        for cuenta in list_accounts(s):
            assert grupo_incongruente(cuenta.categoria_principal, cuenta.subcategoria, cuenta.grupo_analisis) is None, cuenta.codigo
        lista = list(ejercicios(s).values())
        assert not any(d.sin_grupo for d in lista)  # los ceros de las cuentas estandar no son importes
        assert sec.clasificacion(lista) is None and sec.nota_sin_clasificar(lista) == []
        assert hojas_informe(s, lista)[0][0] == "Estados originales"


def test_retirar_la_cuenta_ficticia_recupera_los_resultados(bd):
    claves = ("prueba_acida", "razon_corriente", "ctn", "endeudamiento", "ppi", "roe")
    with session_scope() as s:
        antes = {k: valor(ejercicios(s)[2025], k) for k in claves}
    nueva_cuenta("ZZ9", "ACTIVO", "CORRIENTE", None, 2025, 1000)
    with session_scope() as s:
        assert {k: valor(ejercicios(s)[2025], k) for k in claves} != antes
    quitar_cuenta("ZZ9", 2025)
    with session_scope() as s:
        assert {k: valor(ejercicios(s)[2025], k) for k in claves} == antes
        assert not ejercicios(s)[2025].sin_grupo


# ------------------------------------------------------------- C. utilidad atribuible a la controladora (P-03)
UC = {2021: D("66407462.00"), 2022: D("8559346.00"), 2023: D("12309102.00")}
NCI = {2021: D("2195277.00"), 2022: D("1499964.00"), 2023: D("1021578.00")}


def test_con_los_datos_originales_se_reproducen_las_cifras_de_9_6(bd):
    with session_scope() as s:
        lista = ejercicios(s)
        for anio, esperado in UC.items():
            utilidad, fuente = lista[anio].utilidad_controladora()
            assert utilidad == esperado and fuente.startswith("Estado de cambios en el patrimonio"), anio
            assert utilidad + NCI[anio] == lista[anio].inc.utilidad_neta
        assert round(valor(lista[2021], "roe_controladora"), 2) == D("46.75")
        assert round(valor(lista[2022], "roe_controladora"), 2) == D("4.10")
        assert round(valor(lista[2023], "roe_controladora"), 2) == D("5.41")
        # 2024 y 2025: el trabajo iguala ambas utilidades porque no hay no controladoras ni atribucion impresa
        assert lista[2024].utilidad_controladora()[0] == D("3060981.00")
        assert "Supuesto" in lista[2025].utilidad_controladora()[1]


def test_2023_no_se_sustituye_por_la_utilidad_neta_ni_por_el_resultado_integral(bd):
    with session_scope() as s:
        d = ejercicios(s)[2023]
        utilidad = d.utilidad_controladora()[0]
        assert utilidad == D("12309102.00") and utilidad != d.inc.utilidad_neta
        assert utilidad != D("12542077.00")  # atribucion del resultado integral (13,796,630), otro concepto


@pytest.mark.parametrize("anio,cuenta", [(2021, "CB4101"), (2022, "CB4101"), (2023, "CB4101")])
def test_cambiar_la_utilidad_neta_actualiza_la_atribuible_y_lo_que_depende_de_ella(bd, anio, cuenta):
    with session_scope() as s:
        d = ejercicios(s)[anio]
        ingreso = d.g("INGRESOS_ORDINARIOS")
        roe_ctrl, margen_ctrl = valor(d, "roe_controladora"), valor(d, "margen_neto_controladora")
    poner(anio, cuenta, ingreso + 10000000)
    with session_scope() as s:
        lista = ejercicios(s)
        d = lista[anio]
        utilidad, fuente = d.utilidad_controladora()
        assert utilidad == UC[anio] + 10000000 and utilidad == d.inc.utilidad_neta - NCI[anio]
        assert fuente.startswith("Derivada") and "participación no controladora" in fuente
        assert valor(d, "roe_controladora") > roe_ctrl and valor(d, "margen_neto_controladora") > margen_ctrl
        assert CONCEPTOS["utilidad_controladora"].obtener(d) == utilidad
        _, ctrl = sec.dupont(list(lista.values()))
        fila = next(f for f in ctrl.filas if f[0] == "Utilidad atribuible a la controladora")
        assert fila[anio - 2020] == utilidad
        assert any("Derivada" in n for n in ctrl.notas)
        hoja = celdas_excel([("DuPont", [ctrl])])
        assert float(utilidad) in hoja
        for otro in set(UC) - {anio}:
            assert lista[otro].utilidad_controladora()[0] == UC[otro]  # otros ejercicios no cambian
    poner(anio, cuenta, ingreso)  # revertir
    with session_scope() as s:
        d = ejercicios(s)[anio]
        assert d.utilidad_controladora()[0] == UC[anio]
        assert d.utilidad_controladora()[1].startswith("Estado de cambios")
        assert valor(d, "roe_controladora") == roe_ctrl


def test_modificar_la_participacion_o_la_atribuible_mantiene_la_identidad(bd):
    with session_scope() as s:
        p = get_fiscal_period(s, 2022).id
        neta = ejercicios(s)[2022].inc.utilidad_neta
        roe_total = valor(ejercicios(s)[2022], "roe")
        actualizar_atribucion(s, fiscal_period_id=p, utilidad_neta=neta, participacion=D("2000000.00"))
    with session_scope() as s:
        d = ejercicios(s)[2022]
        assert d.utilidad_controladora()[0] == neta - D("2000000.00")
        assert d.complementarios["utilidad_no_controladora_ecp"].valor == D("2000000.00")
        assert valor(d, "roe") == roe_total  # el enfoque total no depende de la atribucion
        assert d.utilidad_controladora()[1].startswith("Estado de cambios")
        historia = [h for h in list_history(s, fiscal_period_id=p) if h.operacion == "EDITAR" and h.tabla_afectada == "dato_complementario"]
        assert {h.campo for h in historia} == {"utilidad_controladora_ecp", "utilidad_no_controladora_ecp"}
        assert any("utilidad_no_controladora_ecp" in n for n in sec.trazabilidad(s, list(ejercicios(s).values()))[2].notas)
        actualizar_atribucion(s, fiscal_period_id=p, utilidad_neta=neta, utilidad_controladora=D("8000000.00"))
    with session_scope() as s:
        d = ejercicios(s)[2022]
        assert d.utilidad_controladora()[0] == D("8000000.00")
        assert d.complementarios["utilidad_no_controladora_ecp"].valor == neta - D("8000000.00")
        actualizar_atribucion(s, fiscal_period_id=d.periodo.id, utilidad_neta=neta, utilidad_controladora=UC[2022])  # revertir
    with session_scope() as s:
        d = ejercicios(s)[2022]
        assert d.utilidad_controladora()[0] == UC[2022] and d.complementarios["utilidad_no_controladora_ecp"].valor == NCI[2022]
        assert not any("utilidad_no_controladora_ecp" in n for n in sec.trazabilidad(s, list(ejercicios(s).values()))[2].notas)


def test_atribucion_requiere_un_solo_dato_y_un_ejercicio_abierto(bd):
    with session_scope() as s:
        p = get_fiscal_period(s, 2022).id
        with pytest.raises(ValueError):
            actualizar_atribucion(s, fiscal_period_id=p, utilidad_neta=D("1.00"))
        with pytest.raises(ValueError):
            actualizar_atribucion(s, fiscal_period_id=p, utilidad_neta=D("1.00"), participacion=D("1.00"), utilidad_controladora=D("0.00"))
        with pytest.raises(ValueError):  # 2024 no tiene atribucion impresa
            actualizar_atribucion(s, fiscal_period_id=get_fiscal_period(s, 2024).id, utilidad_neta=D("1.00"), participacion=D("1.00"))
        close_fiscal_period(s, p)
    with session_scope() as s:
        with pytest.raises(EjercicioCerradoError):
            actualizar_atribucion(s, fiscal_period_id=get_fiscal_period(s, 2022).id, utilidad_neta=D("1.00"), participacion=D("1.00"))


def test_cifras_que_no_concilian_no_se_eligen_automaticamente(bd):
    with session_scope() as s:
        p = get_fiscal_period(s, 2023).id
        actualizar_dato_complementario(s, fiscal_period_id=p, clave="utilidad_controladora_ecp", valor=D("12542077.00"))
    with session_scope() as s:
        d = ejercicios(s)[2023]
        utilidad, motivo = d.utilidad_controladora()
        assert utilidad is None and "No concilia" in motivo
        r = ind.calcular(d, "margen_neto_controladora")
        assert r.valor is None and valor(d, "roe_controladora") is None
        assert valor(d, "roe") is not None  # el enfoque total sigue


def test_informacion_incompleta_no_produce_utilidad_atribuible(bd):
    borrar(2021, "CB8101")  # sin impuesto: no hay utilidad neta
    with session_scope() as s:
        d = ejercicios(s)[2021]
        assert d.utilidad_controladora()[0] is None
        assert valor(d, "margen_neto_controladora") is None
    with session_scope() as s:  # sin participacion registrada y con la utilidad cambiada no se puede actualizar
        p = get_fiscal_period(s, 2022).id
        s.execute(delete(DatoComplementario).where(DatoComplementario.fiscal_period_id == p,
                                                   DatoComplementario.clave == "utilidad_no_controladora_ecp"))
    with session_scope() as s:
        assert ejercicios(s)[2022].utilidad_controladora()[0] == UC[2022]  # la utilidad no cambio: dato del documento
    with session_scope() as s:
        d = ejercicios(s)[2022]
        poner(2022, "CB4101", d.g("INGRESOS_ORDINARIOS") + 5)
    with session_scope() as s:
        utilidad, motivo = ejercicios(s)[2022].utilidad_controladora()
        assert utilidad is None and "participación" in motivo


def test_sin_no_controladoras_y_sin_atribucion_sigue_a_la_utilidad_neta_como_el_trabajo(bd):
    with session_scope() as s:
        ingreso = ejercicios(s)[2025].g("INGRESOS_ORDINARIOS")
    poner(2025, "CN4101", ingreso + 1000)
    with session_scope() as s:
        d = ejercicios(s)[2025]
        assert d.utilidad_controladora()[0] == d.inc.utilidad_neta == D("11899987.00")


def test_no_controladoras_del_balance_actualizan_el_patrimonio_atribuible(bd):
    with session_scope() as s:
        d = ejercicios(s)[2021]
        pat, maf = d.patrimonio_controladora, valor(d, "maf_controladora")
        nci = d.g("NO_CONTROLADORAS")
    poner(2021, "CB3107", nci + 200000)
    with session_scope() as s:
        d = ejercicios(s)[2021]
        assert d.patrimonio_controladora == pat  # el total sube y las no controladoras tambien
        assert d.bs.total_patrimonio == pat + nci + 200000
        assert valor(d, "maf_controladora") == maf


# ------------------------------------------------------------- Decision 1: naturaleza de la cuenta y prueba acida
def _nueva_activo(codigo: str, nombre: str, importe=1000000, naturaleza: str = "DEUDORA", grupo: str | None = None) -> None:
    with session_scope() as s:
        cuenta = create_account(s, codigo=codigo, nombre=nombre, categoria_principal=Cat.ACTIVO, subcategoria=Sub.CORRIENTE,
                                naturaleza_saldo=Nat(naturaleza), orden_presentacion=9999, grupo_analisis=grupo)
        upsert_entry(s, fiscal_period_id=get_fiscal_period(s, 2025).id, account_id=cuenta.id, valor=D(str(importe)), tipo=Tipo.BALANCE)


def test_escenario_a_inventario_identificado_se_excluye_del_activo_liquido(bd):
    with session_scope() as s:
        d0 = ejercicios(s)[2025]
        acida, inv, ppi = valor(d0, "prueba_acida"), d0.rubro("INVENTARIOS"), valor(d0, "ppi")
    _nueva_activo("ZA1", "Inventario en tránsito")
    with session_scope() as s:
        lista = ejercicios(s)
        d = lista[2025]
        assert d.rubro("INVENTARIOS") == inv + 1000000 == CONCEPTOS["rubro:INVENTARIOS"].obtener(d)
        r = ind.calcular(d, "prueba_acida")
        assert abs(r.valor - acida) < D("1E-20")  # sube el activo corriente y sube el inventario: lo liquido no cambia
        assert not ind.es_provisional(r) and "ZA1" in r.nota and "denominación" in r.nota
        assert valor(d, "ppi") > ppi and not ind.es_provisional(ind.calcular(d, "ppi"))
        assert not ind.es_provisional(ind.calcular(d, "ppc"))  # ya se sabe que no es una cuenta por cobrar
        assert [c.codigo for c, _, _ in d.sin_grupo] == ["ZA1"]  # sigue pendiente de configurar
        fila = sec.clasificacion(list(lista.values())).filas[0]
        assert fila[1] == "ZA1" and "reconocido" in fila[5]


@pytest.mark.parametrize("nombre", ["FICTICIA sin naturaleza", "Otros activos corrientes", "Inventario y otros activos",
                                    "Provisión de inventario", "Inventario - provisión de obsolescencia", "Anticipos de inventario",
                                    "Cuentas por cobrar por inventario"])
def test_escenario_b_naturaleza_desconocida_o_ambigua_no_se_supone(bd, nombre):
    with session_scope() as s:
        inv = ejercicios(s)[2025].rubro("INVENTARIOS")
    _nueva_activo("ZB1", nombre)
    with session_scope() as s:
        lista = ejercicios(s)
        d = lista[2025]
        assert d.rubro("INVENTARIOS") == inv
        r = ind.calcular(d, "prueba_acida")
        assert r.valor is None and "ZB1" in r.motivo and "grupo de análisis" in r.motivo
        assert valor(lista[2024], "prueba_acida") is not None  # otro ejercicio no se afecta
        assert valor(d, "razon_corriente") is not None and valor(d, "ctn") is not None  # los totales son ciertos
        seccion = sec.capital_trabajo(list(lista.values()))
        fila = next(f for f in seccion.filas if str(f[0]).startswith("2025"))
        assert fila[7] == "No calculable" and any("ZB1" in n for n in seccion.notas)
        celdas = celdas_excel([("Capital", [seccion]), ("Liquidez", [sec.indicadores(list(lista.values()), ind.LIQUIDEZ)])])
        assert "No calculable" in celdas and sum("ZB1" in str(c) for c in celdas) >= 2


def test_cuenta_que_no_es_inventario_cuenta_como_activo_liquido(bd):
    with session_scope() as s:
        d0 = ejercicios(s)[2025]
        ac, inv, pc = d0.bs.activo_corriente.subtotal, d0.rubro("INVENTARIOS"), d0.bs.pasivo_corriente.subtotal
    _nueva_activo("ZC1", "Efectivo en caja")
    with session_scope() as s:
        d = ejercicios(s)[2025]
        r = ind.calcular(d, "prueba_acida")
        assert r.valor == (ac + 1000000 - inv) / pc and not ind.es_provisional(r)
        assert ind.es_provisional(ind.calcular(d, "razon_efectivo"))  # falta saber en que rubro de liquidez va


def test_naturaleza_exige_cuenta_corriente_saldo_deudor_y_sin_grupo_contradictorio(bd):
    with session_scope() as s:
        acc = lambda **k: SimpleNamespace(**({"grupo_analisis": None, "categoria_principal": Cat.ACTIVO, "subcategoria": Sub.CORRIENTE,
                                              "naturaleza_saldo": Nat.DEUDORA, "nombre": "Inventarios"} | k))
        assert naturaleza_activo_corriente(acc()) == INVENTARIO
        assert naturaleza_activo_corriente(acc(nombre="Inventario (Materiales, Suministros, etc.)")) == INVENTARIO
        assert naturaleza_activo_corriente(acc(naturaleza_saldo=Nat.ACREEDORA)) is None  # correctora
        assert naturaleza_activo_corriente(acc(subcategoria=Sub.NO_CORRIENTE)) is None
        assert naturaleza_activo_corriente(acc(categoria_principal=Cat.PASIVO)) is None
        assert naturaleza_activo_corriente(acc(grupo_analisis="PRESTAMOS_CP")) is None
        assert naturaleza_activo_corriente(acc(nombre="Efectivo y equivalentes")) == NO_INVENTARIO
    _nueva_activo("ZD1", "Inventarios", grupo="PRESTAMOS_CP")  # grupo contradictorio: no se reconoce
    with session_scope() as s:
        assert valor(ejercicios(s)[2025], "prueba_acida") is None


def test_cuenta_bien_clasificada_y_reversion_recuperan_la_prueba_acida(bd):
    with session_scope() as s:
        acida = valor(ejercicios(s)[2025], "prueba_acida")
    _nueva_activo("ZE1", "FICTICIA sin naturaleza")
    with session_scope() as s:
        assert valor(ejercicios(s)[2025], "prueba_acida") is None
    with session_scope() as s:  # al asignarle el grupo se completa el calculo
        update_account(s, get_account_by_codigo(s, "ZE1").id, grupo_analisis="INVENTARIOS")
    with session_scope() as s:
        r = ind.calcular(ejercicios(s)[2025], "prueba_acida")
        assert abs(r.valor - acida) < D("1E-20") and r.nota is None
    quitar_cuenta("ZE1", 2025)
    with session_scope() as s:
        assert valor(ejercicios(s)[2025], "prueba_acida") == acida


# ------------------------------------------------------------- Decision 2: atribucion de 2023
def test_2023_mantiene_la_pagina_11_conciliada_y_deja_a_la_vista_la_pagina_9(bd):
    with session_scope() as s:
        lista = ejercicios(s)
        d = lista[2023]
        assert D("12309102.00") + D("1021578.00") == D("13330680.00") == d.inc.utilidad_neta
        utilidad, fuente = d.utilidad_controladora()
        assert utilidad == D("12309102.00") and d.base_atribucion() == BASE_DOCUMENTO
        assert "pág. 11" in fuente and "pág. 9" in fuente and "pendiente editorial" in fuente and "13,330,680" in fuente
        assert "13,796,630" not in fuente and "12,542,077" not in fuente
        assert "pág. 9" not in lista[2021].utilidad_controladora()[1]  # 2021: ambas fuentes coinciden
        _, ctrl = sec.dupont(list(lista.values()))
        assert any("pendiente editorial" in n for n in ctrl.notas)


# ------------------------------------------------------------- Decision 3: supuesto de simulacion
@pytest.mark.parametrize("anio", [2021, 2022, 2023])
def test_cambio_de_utilidad_se_identifica_como_supuesto_de_simulacion(bd, anio):
    with session_scope() as s:
        d = ejercicios(s)[anio]
        ingreso, roe = d.g("INGRESOS_ORDINARIOS"), valor(d, "roe_controladora")
        assert d.base_atribucion() == BASE_DOCUMENTO
    poner(anio, "CB4101", ingreso - 3000000)
    with session_scope() as s:
        lista = ejercicios(s)
        d = lista[anio]
        utilidad, fuente = d.utilidad_controladora()
        assert utilidad == UC[anio] - 3000000  # tambien cuando baja
        assert d.base_atribucion() == BASE_SIMULACION
        assert "supuesto de simulación" in fuente and "No es una distribución contable comprobada" in fuente
        assert "información actualizada" in fuente and f"{NCI[anio]:,.2f}" in fuente
        participacion = next(v.valor for k, v in d.complementarios.items() if k.startswith("utilidad_no_controladora") and v.valor == NCI[anio])
        assert participacion == NCI[anio]  # no se modifica sola
        assert valor(d, "roe_controladora") < roe
        _, ctrl = sec.dupont(list(lista.values()))
        base = next(f for f in ctrl.filas if f[0] == "Base de la utilidad atribuible")
        assert base[anio - 2020] == BASE_SIMULACION
        assert any("supuesto de simulación" in n for n in ctrl.notas)
        assert any("supuesto de simulación" in str(c) for c in celdas_excel([("DuPont", [ctrl])]))
        libro = load_workbook(io.BytesIO(export_dupont_excel(get_company(s), d.periodo, compute_dupont(s, d.periodo))))
        assert any("supuesto de simulación" in str(c) for ws in libro.worksheets for f in ws.iter_rows(values_only=True) for c in f if c)
    poner(anio, "CB4101", ingreso)
    with session_scope() as s:
        d = ejercicios(s)[anio]
        assert d.utilidad_controladora()[0] == UC[anio] and d.base_atribucion() == BASE_DOCUMENTO
        assert valor(d, "roe_controladora") == roe


def test_datos_expresos_que_concilian_prevalecen_sobre_el_supuesto(bd):
    with session_scope() as s:
        ingreso = ejercicios(s)[2021].g("INGRESOS_ORDINARIOS")
    poner(2021, "CB4101", ingreso + 1000000)
    with session_scope() as s:
        d = ejercicios(s)[2021]
        assert d.base_atribucion() == BASE_SIMULACION
        actualizar_atribucion(s, fiscal_period_id=d.periodo.id, utilidad_neta=d.inc.utilidad_neta, participacion=D("2500000.00"))
    with session_scope() as s:
        d = ejercicios(s)[2021]
        assert d.utilidad_controladora()[0] == d.inc.utilidad_neta - D("2500000.00")
        assert d.base_atribucion() == BASE_INGRESADA and "cifra impresa 66,407,462" in d.utilidad_controladora()[1]


# ------------------------------------------------------------- Decision 4: 2024 y 2025
@pytest.mark.parametrize("anio,neta", [(2024, D("3060981.00")), (2025, D("11898987.00"))])
def test_igualdad_con_la_utilidad_neta_es_un_supuesto_identificado(bd, anio, neta):
    with session_scope() as s:
        lista = ejercicios(s)
        d = lista[anio]
        utilidad, fuente = d.utilidad_controladora()
        assert utilidad == neta and d.base_atribucion() == BASE_SUPUESTO_IGUALDAD
        assert fuente.startswith("Supuesto: utilidad atribuible igual a utilidad neta total")
        assert "no es un dato comprobado" in fuente and f"{neta:,.2f}" in fuente and "12_EEFF" in fuente
        _, ctrl = sec.dupont(list(lista.values()))
        base = next(f for f in ctrl.filas if f[0] == "Base de la utilidad atribuible")
        assert base[anio - 2020] == BASE_SUPUESTO_IGUALDAD and base[1] == BASE_DOCUMENTO  # se distingue de un dato documentado
        libro = load_workbook(io.BytesIO(export_dupont_excel(get_company(s), d.periodo, compute_dupont(s, d.periodo))))
        assert any("Supuesto: utilidad atribuible" in str(c) for ws in libro.worksheets for f in ws.iter_rows(values_only=True) for c in f if c)
        ingreso = d.g("INGRESOS_ORDINARIOS")
    poner(anio, "CN4101", ingreso + 1000)
    with session_scope() as s:
        d = ejercicios(s)[anio]
        assert d.utilidad_controladora()[0] == neta + 1000 and d.base_atribucion() == BASE_SUPUESTO_IGUALDAD
    poner(anio, "CN4101", ingreso)
    with session_scope() as s:
        assert ejercicios(s)[anio].utilidad_controladora()[0] == neta


def test_atribucion_documentada_sustituye_al_supuesto_si_concilia(bd):
    neta = D("11898987.00")
    with session_scope() as s:
        p = get_fiscal_period(s, 2025).id
        with pytest.raises(ValueError, match="no concilia"):
            registrar_atribucion_documentada(s, fiscal_period_id=p, utilidad_neta=neta, utilidad_controladora=D("11000000.00"),
                                             participacion=D("1.00"), documento="Nota", pagina=1)
        with pytest.raises(ValueError, match="documento"):
            registrar_atribucion_documentada(s, fiscal_period_id=p, utilidad_neta=neta, utilidad_controladora=neta,
                                             participacion=D("0.00"), documento=" ", pagina=1)
    with session_scope() as s:
        assert ejercicios(s)[2025].base_atribucion() == BASE_SUPUESTO_IGUALDAD
        registrar_atribucion_documentada(s, fiscal_period_id=get_fiscal_period(s, 2025).id, utilidad_neta=neta,
                                         utilidad_controladora=D("11000000.00"), participacion=D("898987.00"),
                                         documento="Notas 2025 (ficticio)", pagina=7)
    with session_scope() as s:
        d = ejercicios(s)[2025]
        assert d.utilidad_controladora()[0] == D("11000000.00") and d.base_atribucion() == BASE_DOCUMENTO
        assert "Notas 2025 (ficticio)" in d.utilidad_controladora()[1]
        with pytest.raises(ValueError, match="ya tiene"):
            registrar_atribucion_documentada(s, fiscal_period_id=d.periodo.id, utilidad_neta=neta, utilidad_controladora=neta,
                                             participacion=D("0.00"), documento="Otro", pagina=1)


def test_las_etiquetas_no_alteran_los_importes_del_documento(bd):
    esperado = {2021: "46.75", 2022: "4.10", 2023: "5.41", 2024: "1.35", 2025: "5.15"}
    with session_scope() as s:
        lista = ejercicios(s)
        for anio, roe in esperado.items():
            assert round(valor(lista[anio], "roe_controladora"), 2) == D(roe)
        assert resumen(comparar(list(lista.values()))) == {"Coincide": 711, "Coincidencia por redondeo": 4, "Resultado derivado": 5,
                                                           "Diferencia": 6, "No verificable": 0, "No aplica": 15}
