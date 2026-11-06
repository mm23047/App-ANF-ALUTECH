"""Correcciones autorizadas del analisis horizontal (R-1, R-3, R-4, R-5, D-1, D-2 y D-4).

Comprueba: grupos sin cuentas, saldo cero explicito, cambios de denominacion, agrupaciones no
verificadas, cambios de signo, observacion del capital social y nivel de las exportaciones.
Las reglas se comprueban tambien con ejercicios ficticios de otros anios: no dependen del anio.
"""
from __future__ import annotations

import io
import json
import shutil
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest
from openpyxl import load_workbook

from calculations.comparativo import (
    ADVERTENCIA_ANALITICA,
    AGRUPADA,
    ANALITICA,
    NO_COMPARABLE,
    PRESENTACION_AGRUPADA,
    SIN_COMPARAR,
    FilaHorizontal,
    comparabilidad_agregado,
    comparabilidad_grupo,
    dos_ejercicios,
    horizontal_de_estado,
    horizontal_grupos,
    presentacion_cambia,
)
from calculations.rubros import FAMILIA_DE_GRUPO, GRUPOS, RUBROS, datos_todos
from components.secciones_ui import a_dataframe
from database.connection import init_db, session_scope
from reports import secciones as sec
from reports.analisis_alutech import _hojas_dos_ejercicios
from reports.exportar_secciones import secciones_a_excel, secciones_a_pdf
from scripts.cargar_alutech import cargar
from test_fase8_vertical_dupont import _guardar_empresa

PROYECTO = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def ruta_bd(tmp_path_factory):
    ruta = tmp_path_factory.mktemp("fase11") / "financiera.db"
    cargar(db_path=ruta, respaldar=False)
    init_db(db_path=ruta)
    with session_scope() as s:
        _guardar_empresa(s)  # sin empresa, la aplicacion no abre las paginas de reportes
    return ruta


@pytest.fixture
def lista(ruta_bd):
    init_db(db_path=ruta_bd)
    with session_scope() as s:
        return [d for d in datos_todos(s) if d.tiene_datos]


def _dos(lista, anio, estado, nivel):
    return {f.clave: f for f in dos_ejercicios(horizontal_de_estado(lista, estado, nivel), anio, anio - 1)}


def _ejercicio(anio: int, grupos: dict[str, list[tuple[int, str]]]):
    """Ejercicio ficticio: {grupo: [(id de cuenta, importe)]}. Sirve para probar la regla con cualquier anio."""
    lineas = {g: [(SimpleNamespace(id=i, grupo_analisis=g), Decimal(v)) for i, v in cuentas] for g, cuentas in grupos.items()}
    return SimpleNamespace(anio=anio, lineas_por_grupo=lineas, tiene=lambda g: g in lineas)


# ------------------------------------------------------------ grupos sin cuentas (R-1)
def test_un_grupo_sin_cuentas_queda_sin_dato_y_no_en_cero(lista):
    fila = next(f for f in horizontal_grupos(lista, "BG") if f.clave == "grupo:CXP_COMERCIALES")
    assert fila.valores[2023] == Decimal("195599671")
    assert fila.valores[2024] is None and fila.valores[2025] is None
    assert fila.var_abs[2024] is None and fila.var_pct[2024] is None


@pytest.mark.parametrize("estado", ["BG", "ER"])
def test_ningun_grupo_ausente_muestra_menos_cien_ni_base_cero(lista, estado):
    por_anio = {d.anio: d for d in lista}
    for fila in horizontal_grupos(lista, estado):
        if not fila.clave.startswith("grupo:"):
            continue
        codigo = fila.clave[6:]
        for anio in fila.var_abs:
            if por_anio[anio].tiene(codigo) != por_anio[anio - 1].tiene(codigo):
                assert fila.var_abs[anio] is None and fila.var_pct[anio] is None, (codigo, anio)


def test_un_saldo_cero_explicito_sigue_siendo_cero(lista):
    fila = next(f for f in horizontal_grupos(lista, "BG") if f.clave == "grupo:NO_CONTROLADORAS")
    assert fila.valores[2023] == Decimal("0")  # el estado imprime «-» en 2023
    assert fila.valores[2024] is None  # en 2024 la linea no se presenta
    assert fila.var_pct[2023] == Decimal(-100)  # la caida a cero informada por el estado es real


def test_ausencia_sin_relacion_conocida_aparece_o_desaparece_sin_advertencia_analitica(lista):
    filas = _dos(lista, 2024, "BG", "grupos")
    fila = filas["grupo:BENEFICIOS_POST_EMPLEO"]
    assert fila.tendencia == "Desaparece" and fila.var_abs is None and ADVERTENCIA_ANALITICA not in fila.nota
    assert "No se presenta en 2024" in fila.nota


def test_el_mismo_conjunto_de_estados_no_se_marca_si_solo_aparece_una_linea(lista):
    filas = _dos(lista, 2023, "BG", "grupos")
    assert filas["grupo:BONOS_CP"].tendencia == "Aparece" and ADVERTENCIA_ANALITICA not in filas["grupo:BONOS_CP"].nota
    assert filas["grupo:TITULARIZACION_CP"].var_pct is not None  # sigue la misma cuenta: se compara


def test_los_totales_no_cambian_y_siguen_cuadrando(lista):
    filas = _dos(lista, 2024, "BG", "grupos")
    assert filas["activo_corriente"].actual == Decimal("432771678") and filas["activo_corriente"].var_abs == Decimal("2977134")
    assert filas["pasivo_corriente"].actual == Decimal("362966215") and filas["pasivo_corriente"].var_abs == Decimal("29845530")
    corrientes = [f.valores[2024] for f in horizontal_grupos(lista, "BG") if f.clave.startswith("grupo:")
                  and GRUPOS[f.clave[6:]].clase == "AC" and f.valores[2024] is not None]
    assert sum(corrientes) == Decimal("432771678")


# ----------------------------------------------------- agrupaciones no verificadas (D-1)
@pytest.mark.parametrize("grupo", ["CXC_COMERCIALES", "OTRAS_CXC_CP", "DEUDORES_COMERCIALES_OTRAS", "CXP_COMERCIALES", "ACREEDORES_COMERCIALES_OTRAS",
                                   "PLUSVALIA", "BONOS_LP", "TITULOS_VALORES_LP", "GASTOS_PERSONAL", "GASTOS_FINANCIEROS_NETOS"])
def test_agrupacion_en_otro_rubro_no_calcula_y_advierte(lista, grupo):
    estado = "ER" if GRUPOS[grupo].clase == "ER" else "BG"
    fila = _dos(lista, 2024, estado, "grupos")[f"grupo:{grupo}"]
    assert fila.tendencia == PRESENTACION_AGRUPADA and fila.var_abs is None and fila.var_pct is None
    assert ADVERTENCIA_ANALITICA in fila.nota


@pytest.mark.parametrize("grupo, estado", [("INTANGIBLES", "BG"), ("RESULTADOS_ACUMULADOS", "BG"), ("GASTOS_ADMINISTRACION", "ER"), ("GASTOS_VENTA", "ER")])
def test_misma_linea_con_contenido_distinto_no_es_comparable(lista, grupo, estado):
    fila = _dos(lista, 2024, estado, "grupos")[f"grupo:{grupo}"]
    assert fila.actual is not None and fila.anterior is not None  # los saldos si se muestran
    assert fila.tendencia == SIN_COMPARAR and fila.var_abs is None and fila.var_pct is None
    assert ADVERTENCIA_ANALITICA in fila.nota


def test_agrupacion_analitica_calcula_con_advertencia_y_no_afirma_homogeneidad(lista):
    fila = _dos(lista, 2024, "BG", "rubros")["rubro:CXC_COMERCIALES_Y_OTRAS"]
    assert fila.var_abs == Decimal("1106932") and ADVERTENCIA_ANALITICA in fila.nota
    assert "homog" not in fila.nota.lower()
    assert "sin conceptos adicionales" in fila.nota


def test_linea_presentada_no_se_compara_con_la_linea_unificada(lista):
    fila = _dos(lista, 2024, "BG", "rubros")["rubro:CXC_COMERCIALES_PRESENTADA"]
    assert fila.tendencia == SIN_COMPARAR and fila.var_pct is None and fila.anterior == Decimal("41272525")
    assert _dos(lista, 2025, "BG", "rubros")["rubro:CXC_COMERCIALES_PRESENTADA"].var_abs == Decimal("-27034533")


def test_la_regla_no_depende_del_anio():
    familia = FAMILIA_DE_GRUPO["CXC_COMERCIALES"]
    a = _ejercicio(1999, {"CXC_COMERCIALES": [(1, "10")], "OTRAS_CXC_CP": [(2, "5")]})
    b = _ejercicio(2000, {"DEUDORES_COMERCIALES_OTRAS": [(3, "16")]})
    assert presentacion_cambia(familia, a, b)
    assert comparabilidad_grupo("CXC_COMERCIALES", a, b).estado == AGRUPADA
    assert comparabilidad_agregado(RUBROS["CXC_COMERCIALES_Y_OTRAS"].grupos, a, b).estado == ANALITICA
    assert comparabilidad_agregado(RUBROS["CXC_COMERCIALES_PRESENTADA"].grupos, a, b).estado == NO_COMPARABLE
    igual = _ejercicio(2000, {"CXC_COMERCIALES": [(1, "11")], "OTRAS_CXC_CP": [(2, "6")]})
    assert not presentacion_cambia(familia, a, igual) and comparabilidad_grupo("CXC_COMERCIALES", a, igual) is None


def test_no_hay_excepciones_por_anio_en_las_reglas():
    import calculations.comparativo as modulo

    fuente = Path(modulo.__file__).read_text(encoding="utf-8")
    inicio, fin = fuente.index("def _grupos_presentes"), fuente.index("_GRUPOS_DE_CONCEPTO =")
    regla = fuente[inicio:fin]
    assert not any(str(anio) in regla for anio in range(2021, 2026))


# --------------------------------------------------------- cambios de denominacion
def test_cambio_de_denominacion_cxc_largo_plazo_entre_2024_y_2025(lista):
    grupos = _dos(lista, 2025, "BG", "grupos")
    assert grupos["grupo:OTRAS_CXC_LP"].tendencia == PRESENTACION_AGRUPADA and grupos["grupo:OTRAS_CXC_LP"].var_pct is None
    assert grupos["grupo:CXC_RELACIONADAS_LP"].tendencia == PRESENTACION_AGRUPADA and grupos["grupo:CXC_RELACIONADAS_LP"].var_pct is None
    assert grupos["grupo:CXC_LP"].var_abs == Decimal("1561607")  # la misma cuenta en ambos ejercicios sigue comparandose
    cuentas = _dos(lista, 2025, "BG", "cuentas")
    assert cuentas["CN1202"].tendencia == "Desaparece" and "otra denominación" in cuentas["CN1202"].nota
    assert cuentas["CN1203"].tendencia == "Aparece" and ADVERTENCIA_ANALITICA in cuentas["CN1203"].nota


def test_otras_cxc_no_corrientes_no_muestra_el_porcentaje_anterior(lista):
    fila = _dos(lista, 2024, "BG", "grupos")["grupo:OTRAS_CXC_LP"]
    assert fila.tendencia == SIN_COMPARAR and fila.var_pct is None


# ------------------------------------------------------- advertencia en la fila (R-4)
def test_tablas_marcan_la_fila_y_explican_la_marca_sin_cambiar_cifras(lista):
    tabla_4 = sec.horizontal_balance_tablas(lista)[1]
    df = a_dataframe(tabla_4)
    fila = df[df["Cuenta financiera"].str.contains("†")]
    assert fila["Cuenta financiera"].tolist() == ["Cuentas por cobrar comerciales y otras (corrientes) †"]
    assert fila["Var. rel. 23–24"].tolist() == ["+1.15%"]
    assert any(n.startswith("† ") and ADVERTENCIA_ANALITICA in n for n in tabla_4.notas)
    tabla_3 = a_dataframe(sec.horizontal_balance_tablas(lista)[0])
    assert not tabla_3["Cuenta financiera"].str.contains("†").any()  # 2021-2023 no tiene cambios de presentacion


def test_tabla_5_conserva_cifras_y_marca_las_filas_analiticas(lista):
    seccion = sec.horizontal_resultados_tabla(lista)
    df = a_dataframe(seccion).set_index("Rubro del estado de resultados")
    gastos = next(i for i in df.index if i.startswith("Gastos operativos"))
    financieros = next(i for i in df.index if i.startswith("Gastos financieros netos"))
    assert gastos.endswith("†") and financieros.endswith("†")
    assert df.loc[gastos, "Var. rel. 23–24"] == "+4.33%" and df.loc[financieros, "Var. rel. 23–24"] == "+27.47%"


# ------------------------------------------------------------- cambios de signo (R-5)
def _fila_dos(actual, anterior):
    fila = FilaHorizontal("x", "x", "cuenta", {2001: Decimal(actual), 2000: Decimal(anterior)})
    return dos_ejercicios([fila], 2001, 2000)[0]


@pytest.mark.parametrize("seccion_fn, columna, etiqueta", [(sec.capital_trabajo, "Var. relativa CTN", "2025 †"),
                                                           (sec.capital_trabajo_interanual, "Variación relativa CTN", "2024 vs 2025 †")])
def test_tablas_6_y_7_advierten_el_cambio_de_signo_solo_donde_ocurre(lista, seccion_fn, columna, etiqueta):
    seccion = seccion_fn(lista)
    df = a_dataframe(seccion)
    marcadas = df[df.iloc[:, 0].str.contains("†")]
    assert marcadas.iloc[:, 0].tolist() == [etiqueta] and marcadas[columna].tolist() == ["-277.02%"]
    notas = [n for n in seccion.notas if "cambia de signo" in n]
    assert len(notas) == 1 and "variación absoluta" in notas[0] and "+69,805,463" in notas[0] and "-123,568,026" in notas[0]


def test_de_positivo_a_negativo_calcula_y_advierte():
    fila = _fila_dos("-50", "100")
    assert fila.var_pct == Decimal(-150) and "Cambia de signo" in fila.nota and "variación absoluta" in fila.nota


def test_de_negativo_a_positivo_no_menciona_un_porcentaje_inexistente():
    fila = _fila_dos("50", "-100")
    assert fila.var_pct is None and fila.var_abs == Decimal(150)
    assert "no se calcula" in fila.nota and "porcentaje" not in fila.nota


def test_signo_igual_no_advierte():
    assert "signo" not in _fila_dos("-50", "-100").nota and "signo" not in _fila_dos("50", "100").nota


# ------------------------------------------------------------- capital social (D-4)
def test_capital_social_conserva_el_importe_y_pide_confirmacion(lista):
    for anio, signo in ((2024, "2000"), (2025, "-2000")):
        fila = _dos(lista, anio, "BG", "grupos")["grupo:CAPITAL_SOCIAL"]
        assert fila.var_abs == Decimal(signo) and "USD 2,000" in fila.nota and "confirmación documental" in fila.nota
    assert _dos(lista, 2024, "BG", "grupos")["grupo:CAPITAL_SOCIAL"].actual == Decimal("119391833")
    assert "confirmación" not in _dos(lista, 2022, "BG", "grupos")["grupo:CAPITAL_SOCIAL"].nota  # un aumento real no se senala


# ---------------------------------------------------- nivel de las exportaciones (R-3)
@pytest.mark.parametrize("nivel, detalle", [("rubros", "rubros y totales"), ("grupos", "grupos de análisis"), ("cuentas", "cuentas")])
@pytest.mark.parametrize("estado", ["BG", "ER"])
def test_hojas_interanuales_usan_el_nivel_pedido(lista, estado, nivel, detalle):
    hojas = _hojas_dos_ejercicios(lista, estado, nivel)
    assert [h for h, _ in hojas] == ["2022 vs 2021", "2023 vs 2022", "2024 vs 2023", "2025 vs 2024"]
    assert all(s.titulo.endswith(f"{detalle} [USD]") for _, secciones in hojas for s in secciones)


@pytest.mark.parametrize("nivel", ["rubros", "grupos", "cuentas"])
def test_excel_y_pdf_contienen_las_mismas_filas_que_la_pantalla(lista, nivel):
    hojas = _hojas_dos_ejercicios(lista, "BG", nivel)
    empresa = SimpleNamespace(nombre_legal="Empresa", moneda="USD")
    libro = load_workbook(io.BytesIO(secciones_a_excel(empresa, "T", hojas)))
    assert secciones_a_pdf(empresa, "T", [s for _, l in hojas for s in l]).startswith(b"%PDF")
    for nombre, secciones in hojas:
        seccion = secciones[0]
        df = a_dataframe(seccion)
        ws = libro[nombre]
        filas_xl = list(ws.iter_rows(values_only=True))
        inicio = next(i for i, f in enumerate(filas_xl) if f[0] == seccion.titulo) + 2
        for i, (_, fila) in enumerate(df.iterrows()):
            assert filas_xl[inicio + i][0] == fila.iloc[0]
            assert (filas_xl[inicio + i][5] or "") == fila["Sentido"]
            assert (filas_xl[inicio + i][6] or "") == fila["Observación"]


def test_pagina_entrega_a_las_descargas_el_nivel_elegido(ruta_bd, tmp_path):
    copia = tmp_path / "financiera.db"
    shutil.copy2(ruta_bd, copia)
    proceso = subprocess.run([sys.executable, str(PROYECTO / "tests" / "humo_exportes_nivel.py"), str(copia)],
                             capture_output=True, text=True, encoding="utf-8", timeout=280, cwd=str(PROYECTO))
    assert proceso.returncode == 0, proceso.stderr[-1500:]
    datos = json.loads(proceso.stdout.strip().splitlines()[-1])
    for clave, nivel, detalle in (("balance_defecto", "rubros", "rubros y totales"), ("balance_cuentas", "cuentas", "cuentas"),
                                  ("balance_grupos", "grupos", "grupos de análisis"), ("resultados_cuentas", "cuentas", "cuentas")):
        assert datos[clave]["archivo"].endswith(f"_{nivel}"), clave
        assert all(t.endswith(f"{detalle} [USD]") for t in datos[clave]["interanuales"]) and len(datos[clave]["interanuales"]) == 4, clave
