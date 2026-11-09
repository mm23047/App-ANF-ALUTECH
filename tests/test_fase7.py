"""Fase 7: correcciones de la validacion operativa (O-1 a O-5)."""
import io
import sys
import shutil
import sqlite3
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pytest
import streamlit
from openpyxl import Workbook

from components import confirmacion
from database import connection
from database.backup_utils import crear_respaldo, restaurar, sha256_archivo
from database.connection import init_db, render_scope, session_scope
from database.enums import TipoEstadoFinanciero as Tipo
from database.repositories import (
    get_account_by_codigo,
    get_company,
    get_entries_map,
    get_fiscal_period,
    get_or_create_fiscal_period,
    save_company,
    upsert_entry,
)
from database.seed import seed_default_accounts


@pytest.fixture()
def bd(tmp_path):
    ruta = tmp_path / "data" / "financiera.db"
    ruta.parent.mkdir()
    init_db(db_path=ruta)
    with session_scope() as s:
        seed_default_accounts(s)
        save_company(s, nombre_legal="Empresa Prueba", nombre_comercial="EP", actividad_economica="x",
                     pais="SV", moneda="USD", anio_inicial_analisis=2021)
        p, _ = get_or_create_fiscal_period(s, 2021)
        upsert_entry(s, fiscal_period_id=p.id, account_id=get_account_by_codigo(s, "1001").id, valor="100",
                     tipo=Tipo.BALANCE)
    yield ruta
    connection.dispose_engine()


def _id(s, codigo):
    return get_account_by_codigo(s, codigo).id


def _importes(s, tipo=Tipo.RESULTADOS):
    return {s.get(type(get_account_by_codigo(s, "1001")), i).codigo: v
            for i, v in get_entries_map(s, get_fiscal_period(s, 2021).id, tipo).items()}


def _botones(monkeypatch, *pulsados):
    monkeypatch.setattr(streamlit, "button", lambda label, *a, **k: label in pulsados)


def _capturar(monkeypatch, valores, *botones, tipo=Tipo.RESULTADOS, errores=None):
    """Pagina real de captura con widgets simulados (una 'pestana')."""
    from modules import data_entry

    monkeypatch.setattr(streamlit, "number_input",
                        lambda label, *a, value=None, **k: valores.get(label.split(" — ")[0], value))
    monkeypatch.setattr(streamlit, "form_submit_button", lambda *a, **k: "Guardar" in botones)
    monkeypatch.setattr(streamlit, "rerun", lambda *a, **k: None)
    if errores is not None:
        monkeypatch.setattr(streamlit, "error", lambda m, *a, **k: errores.append(m))
    _botones(monkeypatch, *botones)
    grupos = data_entry.GRUPOS_RESULTADOS if tipo == Tipo.RESULTADOS else data_entry.GRUPOS_BALANCE
    with render_scope() as s:
        data_entry._render_grupos(s, get_fiscal_period(s, 2021), tipo, grupos, "USD", "form")


def _restaurar_desde_otra_pestana(copia: Path, ruta: Path):
    """Lo que hace app.py cuando otra pestana confirma una restauracion."""
    connection.dispose_engine()
    resultado = restaurar(copia, ruta, dir_respaldos=ruta.parent / "backups")
    init_db(db_path=ruta)
    return resultado


def _estado(ruta: Path) -> dict:
    con = sqlite3.connect(f"file:{ruta}?mode=ro", uri=True)
    datos = {t: con.execute(f"select * from {t} order by rowid").fetchall()
             for t in ("balance_entry", "income_entry", "change_history", "company", "fiscal_period")}
    con.close()
    return datos


# =================================================================== O-1

def test_o1_restaurar_entre_preparar_y_confirmar_invalida_la_confirmacion(bd, monkeypatch):
    """Escenario O-1 exacto: B prepara 4001 = 999; A restaura una copia en la
    que 4001 sigue 'Sin dato' (el valor que mostro el resumen); B confirma."""
    copia = crear_respaldo(bd, bd.parent / "backups" / "financiera_previa.db")
    _capturar(monkeypatch, {"4001": 999.0}, "Guardar")                      # pestana B
    assert confirmacion.pendiente("captura_form") is not None
    _restaurar_desde_otra_pestana(copia, bd)                                 # pestana A
    antes = sha256_archivo(bd)
    errores = []
    _capturar(monkeypatch, {"4001": 999.0}, confirmacion.ETIQUETA_CONFIRMAR, errores=errores)  # B confirma
    assert sha256_archivo(bd) == antes                                       # nada escrito
    with session_scope() as s:
        assert _importes(s) == {}
    assert errores and "la base de datos cambió" in errores[0] and "vuelva a pulsar Guardar" in errores[0]
    assert confirmacion.pendiente("captura_form") is None                    # la confirmacion obsoleta se descarto
    # Una confirmacion nueva sobre la base restaurada si funciona.
    _capturar(monkeypatch, {"4001": 999.0}, "Guardar")
    _capturar(monkeypatch, {"4001": 999.0}, confirmacion.ETIQUETA_CONFIRMAR)
    with session_scope() as s:
        assert _importes(s) == {"4001": Decimal("999.00")}


def test_o1_restaurar_copia_identica_tambien_invalida(bd, monkeypatch):
    """La copia restaurada tiene exactamente los mismos datos (se hizo despues
    de preparar): cambia el archivo, asi que la confirmacion se invalida."""
    _capturar(monkeypatch, {"4001": 999.0}, "Guardar")
    copia = crear_respaldo(bd, bd.parent / "backups" / "financiera_identica.db")
    _restaurar_desde_otra_pestana(copia, bd)
    antes = _estado(bd)
    _capturar(monkeypatch, {"4001": 999.0}, confirmacion.ETIQUETA_CONFIRMAR, errores=[])
    assert _estado(bd) == antes


def test_o1_sustitucion_del_contenido_en_el_mismo_archivo(bd, monkeypatch):
    """Otra base copiada sobre el mismo archivo (mismo id de archivo): el
    ultimo registro del historial ya no existe y la confirmacion se invalida."""
    copia = crear_respaldo(bd, bd.parent / "backups" / "financiera_vieja.db")
    with session_scope() as s:  # un cambio posterior a la copia: nuevo registro en el historial
        upsert_entry(s, fiscal_period_id=get_fiscal_period(s, 2021).id, account_id=_id(s, "1002"), valor="5",
                     tipo=Tipo.BALANCE)
    _capturar(monkeypatch, {"4001": 999.0}, "Guardar")
    connection.dispose_engine()
    id_archivo = Path(bd).stat().st_ino
    src, dst = sqlite3.connect(copia), sqlite3.connect(bd)
    src.backup(dst)  # reescribe el contenido en el mismo archivo
    src.close()
    dst.close()
    assert Path(bd).stat().st_ino == id_archivo
    init_db(db_path=bd)
    antes = _estado(bd)
    errores = []
    _capturar(monkeypatch, {"4001": 999.0}, confirmacion.ETIQUETA_CONFIRMAR, errores=errores)
    assert _estado(bd) == antes and "la base de datos cambió" in errores[0]


def test_o1_escrituras_normales_no_invalidan_la_confirmacion(bd, monkeypatch):
    """Otra pestana guarda otra cuenta en la misma base: la confirmacion de B
    sigue siendo valida (las escrituras normales no cambian el archivo ni
    borran el historial)."""
    _capturar(monkeypatch, {"4001": 999.0}, "Guardar")
    base = confirmacion.pendiente("captura_form").base
    with session_scope() as s:
        upsert_entry(s, fiscal_period_id=get_fiscal_period(s, 2021).id, account_id=_id(s, "5001"), valor="300",
                     tipo=Tipo.RESULTADOS)
        assert confirmacion.misma_base(base, s)
    _capturar(monkeypatch, {"4001": 999.0}, confirmacion.ETIQUETA_CONFIRMAR)
    with session_scope() as s:
        assert _importes(s) == {"4001": Decimal("999.00"), "5001": Decimal("300.00")}


def test_o1_la_comprobacion_tambien_ocurre_dentro_de_la_transaccion(bd, monkeypatch):
    """Si la base cambia justo entre la comprobacion previa y la escritura,
    la comprobacion dentro de la transaccion revierte todo."""
    _capturar(monkeypatch, {"4001": 999.0, "5001": 100.0}, "Guardar")
    llamadas = []
    original = confirmacion.misma_base

    def cambia_en_la_segunda(base, session):
        llamadas.append(1)
        return original(base, session) and len(llamadas) < 2

    monkeypatch.setattr(confirmacion, "misma_base", cambia_en_la_segunda)
    antes = _estado(bd)
    errores = []
    _capturar(monkeypatch, {}, confirmacion.ETIQUETA_CONFIRMAR, errores=errores)
    assert len(llamadas) == 2 and _estado(bd) == antes
    assert "la base de datos cambió" in errores[0] and "No se guardó ningún cambio" in errores[0]


def test_o1_edicion_tras_restaurar_no_escribe(bd, monkeypatch):
    from modules import data_edit

    copia = crear_respaldo(bd, bd.parent / "backups" / "financiera_previa.db")

    def editar(*botones):
        def editor(df, **k):
            df = df.copy()
            df.loc[df["Código"] == "1001", "Valor"] = 150.0
            return df

        monkeypatch.setattr(streamlit, "data_editor", editor)
        monkeypatch.setattr(streamlit, "checkbox", lambda *a, **k: False)
        monkeypatch.setattr(streamlit, "rerun", lambda *a, **k: None)
        _botones(monkeypatch, *botones)
        with render_scope() as s:
            data_edit._tabla_editable(s, get_fiscal_period(s, 2021).id, Tipo.BALANCE, "USD", key="k")

    editar("Guardar cambios")
    _restaurar_desde_otra_pestana(copia, bd)
    antes = _estado(bd)
    errores = []
    monkeypatch.setattr(streamlit, "error", lambda m, *a, **k: errores.append(m))
    editar(confirmacion.ETIQUETA_CONFIRMAR)
    assert _estado(bd) == antes and "la base de datos cambió" in errores[0]
    editar("Guardar cambios")
    editar(confirmacion.ETIQUETA_CONFIRMAR)
    with session_scope() as s:
        assert _importes(s, Tipo.BALANCE) == {"1001": Decimal("150.00")}


def test_o1_importacion_tras_restaurar_exige_revisar_la_vista_previa(bd, monkeypatch):
    from modules import excel_import
    from modules.excel_import import COLUMNAS

    wb = Workbook()
    wb.active.append(COLUMNAS)
    wb.active.append(["4001", "Ingresos", "", "", 2021, 500])
    archivo = io.BytesIO()
    wb.save(archivo)
    avisos = []
    monkeypatch.setattr(streamlit, "warning", lambda m, *a, **k: avisos.append(m))
    monkeypatch.setattr(streamlit, "checkbox", lambda *a, **k: False)
    monkeypatch.setattr(streamlit, "file_uploader", lambda *a, **k: (archivo.seek(0), archivo)[1])

    def pagina(*botones):
        _botones(monkeypatch, *botones)
        with render_scope() as s:
            excel_import.render(s, get_company(s))

    pagina()  # vista previa
    copia = crear_respaldo(bd, bd.parent / "backups" / "financiera_identica.db")
    _restaurar_desde_otra_pestana(copia, bd)  # mismos datos, otra base
    antes = _estado(bd)
    pagina("Confirmar importación")
    assert _estado(bd) == antes and any("La vista previa cambió" in a for a in avisos)
    pagina("Confirmar importación")  # con la vista previa actual, si importa
    with session_scope() as s:
        assert _importes(s) == {"4001": Decimal("500.00")}


def test_o1_estado_base_estable_con_escrituras_y_distinto_tras_restaurar(bd):
    copia = crear_respaldo(bd, bd.parent / "backups" / "financiera_copia.db")
    with session_scope() as s:
        inicial = confirmacion.estado_base(s)
        upsert_entry(s, fiscal_period_id=get_fiscal_period(s, 2021).id, account_id=_id(s, "1003"), valor="7",
                     tipo=Tipo.BALANCE)
    with session_scope() as s:
        tras_escribir = confirmacion.estado_base(s)
        assert tras_escribir.archivo == inicial.archivo and confirmacion.misma_base(inicial, s)
        assert not confirmacion.misma_base(None, s)  # una operacion sin base registrada nunca se acepta
    _restaurar_desde_otra_pestana(copia, bd)
    with session_scope() as s:
        assert confirmacion.estado_base(s).archivo != inicial.archivo
        assert not confirmacion.misma_base(tras_escribir, s)


# =================================================================== O-2

from database import backup_utils  # noqa: E402
from database.backup_utils import RespaldoInvalido, RestauracionError  # noqa: E402


@pytest.fixture()
def escenario_restauracion(tmp_path):
    """BD actual, una copia a restaurar y respaldos historicos que no deben tocarse."""
    actual = tmp_path / "data" / "financiera.db"
    actual.parent.mkdir()
    init_db(db_path=actual)
    with session_scope() as s:
        seed_default_accounts(s)
        save_company(s, nombre_legal="Actual", nombre_comercial="A", actividad_economica="x", pais="SV", moneda="USD",
                     anio_inicial_analisis=2021)
    connection.dispose_engine()
    backups = actual.parent / "backups"
    origen = crear_respaldo(actual, backups / "financiera_20260101_000000_000000.db")
    con = sqlite3.connect(origen)  # la copia a restaurar tiene otra empresa
    con.execute("update company set nombre_legal = 'Copia'")
    con.commit()
    con.close()
    historicos = {}
    for nombre in ("financiera_20250101_000000_000000.db", "financiera_pre_restauracion_20250101_000000_000000.db"):
        shutil.copy2(origen, backups / nombre)
        historicos[nombre] = sha256_archivo(backups / nombre)
    historicos[origen.name] = sha256_archivo(origen)
    yield actual, origen, backups, historicos
    connection.dispose_engine()


def _previas(backups, historicos):
    return sorted(p.name for p in backups.glob("financiera_pre_restauracion_*.db") if p.name not in historicos)


def _temporales(actual):
    return sorted(p.name for p in actual.parent.glob("financiera.db.*"))


def _historicos_intactos(backups, historicos):
    return all(sha256_archivo(backups / n) == h for n, h in historicos.items())


def _lanza(exc):
    def f(*_a, **_k):
        raise exc
    return f


def test_o2_restauracion_exitosa_conserva_la_copia_previa(escenario_restauracion):
    actual, origen, backups, historicos = escenario_restauracion
    hash_antes = sha256_archivo(actual)
    resultado = restaurar(origen, actual, dir_respaldos=backups)
    assert sha256_archivo(resultado.respaldo_previo) == hash_antes  # copia de recuperacion de la base anterior
    assert _previas(backups, historicos) == [resultado.respaldo_previo.name]
    assert _temporales(actual) == [] and _historicos_intactos(backups, historicos)


def test_o2_restauracion_rechazada_por_archivo_en_uso_no_deja_copia(escenario_restauracion, monkeypatch):
    actual, origen, backups, historicos = escenario_restauracion
    hash_antes = sha256_archivo(actual)
    monkeypatch.setattr(backup_utils.time, "sleep", lambda _: None)
    monkeypatch.setattr(backup_utils.os, "replace", _lanza(PermissionError("en uso")))
    with pytest.raises(RestauracionError, match="en uso"):
        restaurar(origen, actual, dir_respaldos=backups)
    assert sha256_archivo(actual) == hash_antes
    assert _previas(backups, historicos) == [] and _temporales(actual) == []
    assert _historicos_intactos(backups, historicos)


@pytest.mark.skipif(sys.platform != "win32", reason="bloqueo de archivos propio de Windows")
def test_o2_bloqueo_real_de_otra_pestana_no_deja_copia(escenario_restauracion, monkeypatch):
    actual, origen, backups, historicos = escenario_restauracion
    hash_antes = sha256_archivo(actual)
    monkeypatch.setattr(backup_utils.time, "sleep", lambda _: None)
    otra_pestana = sqlite3.connect(actual)
    otra_pestana.execute("SELECT COUNT(*) FROM company").fetchone()
    try:
        with pytest.raises(RestauracionError, match="en uso"):
            restaurar(origen, actual, dir_respaldos=backups)
    finally:
        otra_pestana.close()
    assert sha256_archivo(actual) == hash_antes
    assert _previas(backups, historicos) == [] and _temporales(actual) == []
    assert _historicos_intactos(backups, historicos)


def test_o2_error_durante_el_reemplazo_no_deja_copia(escenario_restauracion, monkeypatch):
    actual, origen, backups, historicos = escenario_restauracion
    hash_antes = sha256_archivo(actual)
    monkeypatch.setattr(backup_utils.os, "replace", _lanza(OSError(28, "disco lleno")))
    with pytest.raises(RestauracionError, match="No se pudo preparar"):
        restaurar(origen, actual, dir_respaldos=backups)
    assert sha256_archivo(actual) == hash_antes
    assert _previas(backups, historicos) == [] and _temporales(actual) == []
    assert _historicos_intactos(backups, historicos)


def test_o2_copia_previa_no_verificable_se_descarta(escenario_restauracion, monkeypatch):
    """Antes quedaban la copia previa y el .restaurando (RestauracionError no se limpiaba)."""
    actual, origen, backups, historicos = escenario_restauracion
    hash_antes = sha256_archivo(actual)
    copiar = shutil.copy2

    def copia_corrupta(src, dst, *a, **k):
        resultado = copiar(src, dst, *a, **k)
        if "pre_restauracion" in str(dst):
            Path(dst).write_bytes(b"danada")
        return resultado

    monkeypatch.setattr(backup_utils.shutil, "copy2", copia_corrupta)
    with pytest.raises(RestauracionError, match="copia previa"):
        restaurar(origen, actual, dir_respaldos=backups)
    assert sha256_archivo(actual) == hash_antes
    assert _previas(backups, historicos) == [] and _temporales(actual) == []


def test_o2_reversion_conserva_la_copia_previa(escenario_restauracion, monkeypatch):
    """Rollback: falla la verificacion despues de reemplazar. La base vuelve al
    original y la copia previa se conserva (es la referencia de recuperacion)."""
    actual, origen, backups, historicos = escenario_restauracion
    hash_antes = sha256_archivo(actual)
    inspeccion_real = backup_utils.inspeccionar_bd

    def falla_en_destino(ruta):
        if Path(ruta) == actual and sha256_archivo(actual) != hash_antes:
            raise RespaldoInvalido("verificación posterior simulada")
        return inspeccion_real(ruta)

    monkeypatch.setattr(backup_utils, "inspeccionar_bd", falla_en_destino)
    with pytest.raises(RestauracionError, match="se restableció"):
        restaurar(origen, actual, dir_respaldos=backups)
    assert sha256_archivo(actual) == hash_antes
    previas = _previas(backups, historicos)
    assert len(previas) == 1 and sha256_archivo(backups / previas[0]) == hash_antes
    assert _temporales(actual) == [] and _historicos_intactos(backups, historicos)


def test_o2_reversion_fallida_conserva_la_copia_y_limpia_el_temporal(escenario_restauracion, monkeypatch):
    actual, origen, backups, historicos = escenario_restauracion
    inspeccion_real = backup_utils.inspeccionar_bd
    reemplazar_real = backup_utils._reemplazar
    hash_antes = sha256_archivo(actual)

    def falla_en_destino(ruta):
        if Path(ruta) == actual and sha256_archivo(actual) != hash_antes:
            raise RespaldoInvalido("verificación posterior simulada")
        return inspeccion_real(ruta)

    def reemplazo(origen_, destino_, *a, **k):
        if str(origen_).endswith(".revertir"):
            raise PermissionError("en uso durante la reversión")
        return reemplazar_real(origen_, destino_, *a, **k)

    monkeypatch.setattr(backup_utils, "inspeccionar_bd", falla_en_destino)
    monkeypatch.setattr(backup_utils, "_reemplazar", reemplazo)
    with pytest.raises(RestauracionError, match="Copia previa conservada"):
        restaurar(origen, actual, dir_respaldos=backups)
    previas = _previas(backups, historicos)
    assert len(previas) == 1 and sha256_archivo(backups / previas[0]) == hash_antes
    assert _temporales(actual) == []


def test_o2_situacion_ambigua_conserva_la_copia(escenario_restauracion, monkeypatch):
    """Si la base actual cambio durante el intento (no se puede demostrar que
    sigue intacta), la copia previa no se borra."""
    actual, origen, backups, historicos = escenario_restauracion

    def cambia_y_falla(origen_, destino_, *a, **k):
        con = sqlite3.connect(destino_)
        con.execute("update company set pais = 'GT'")
        con.commit()
        con.close()
        raise PermissionError("en uso")

    monkeypatch.setattr(backup_utils, "_reemplazar", cambia_y_falla)
    with pytest.raises(RestauracionError):
        restaurar(origen, actual, dir_respaldos=backups)
    assert len(_previas(backups, historicos)) == 1 and _temporales(actual) == []


# =================================================================== O-3 y O-4 (Excel)

from openpyxl import load_workbook  # noqa: E402


@pytest.fixture()
def libros_excel(bd):
    """Reportes Excel de 2021 con las mismas banderas que pasan las paginas, y un
    DuPont descuadrado de 2022 para comprobar los textos largos de las banderas."""
    from calculations.balance_sheet import compute_balance_sheet
    from calculations.banderas import banderas_balance, banderas_resultados
    from calculations.controls import conciliar_resultado
    from calculations.dupont import compute_dupont
    from calculations.income_statement import compute_income_statement
    from calculations.vertical_analysis import compute_vertical_balance, compute_vertical_income
    from reports.excel_export import (export_balance_excel, export_dupont_excel, export_income_excel,
                                      export_vertical_excel)

    with session_scope() as s:
        p = get_fiscal_period(s, 2021)
        for codigo, valor, tipo in (("1101", "900", Tipo.BALANCE), ("2001", "400", Tipo.BALANCE),
                                    ("3001", "500", Tipo.BALANCE), ("4001", "1000", Tipo.RESULTADOS),
                                    ("5001", "600", Tipo.RESULTADOS), ("6001", "100", Tipo.RESULTADOS),
                                    ("8001", "50", Tipo.RESULTADOS)):
            upsert_entry(s, fiscal_period_id=p.id, account_id=_id(s, codigo), valor=valor, tipo=tipo)
    with session_scope() as s:
        c, p = get_company(s), get_fiscal_period(s, 2021)
        bs, inc = compute_balance_sheet(s, p.id), compute_income_statement(s, p.id)
        conc = conciliar_resultado(bs, inc)
        vb, vi = compute_vertical_balance(s, p.id), compute_vertical_income(s, p.id)
        datos = {
            "balance": export_balance_excel(c, p, bs, banderas_balance(bs, conc)),
            "resultados": export_income_excel(c, p, inc, banderas_resultados(inc, conc)),
            "vertical": export_vertical_excel(c, p, "V", None, vb.base_total_activo, "Total Activo", vb.lineas,
                                              banderas_balance(bs, conc)),
            "vertical_df": export_vertical_excel(c, p, "V", pd.DataFrame(
                [{"Código": "1101", "Cuenta": "PPE", "Valor": 900.0, "Participación %": 100.0}]),
                vb.base_total_activo, "Total Activo"),
            "dupont": export_dupont_excel(c, p, compute_dupont(s, p)),
        }
        p22, _ = get_or_create_fiscal_period(s, 2022)
        for codigo, valor, tipo in (("1101", "900", Tipo.BALANCE), ("2001", "100", Tipo.BALANCE), ("3001", "500", Tipo.BALANCE),
                                    ("4001", "1000", Tipo.RESULTADOS), ("8001", "50", Tipo.RESULTADOS)):
            upsert_entry(s, fiscal_period_id=p22.id, account_id=_id(s, codigo), valor=valor, tipo=tipo)
        datos["dupont_con_banderas"] = export_dupont_excel(c, p22, compute_dupont(s, p22))
    return {k: load_workbook(io.BytesIO(v)).active for k, v in datos.items()}


@pytest.mark.parametrize("reporte", ["balance", "resultados", "vertical", "vertical_df", "dupont"])
def test_o4_impresion_horizontal_en_una_pagina_de_ancho(libros_excel, reporte):
    ws = libros_excel[reporte]
    assert ws.page_setup.orientation == "landscape"
    assert ws.sheet_properties.pageSetUpPr.fitToPage is True
    assert ws.page_setup.fitToWidth == 1 and ws.page_setup.fitToHeight == 0
    assert ws.page_margins.left == ws.page_margins.right == 0.5
    if reporte != "dupont":  # el encabezado de la tabla se repite en cada pagina impresa
        fila = int(ws.print_title_rows.split(":")[0].lstrip("$"))
        assert ws.cell(fila, 1).value == "Código"


@pytest.mark.parametrize("reporte, ancho_maximo", [("balance", 140), ("resultados", 140), ("vertical", 160),
                                                    ("dupont", 140)])
def test_o4_ancho_total_no_obliga_a_reducir_demasiado(libros_excel, reporte, ancho_maximo):
    """Una pagina horizontal Carta con margenes de 0,5" admite unos 130
    caracteres a 100 %: el ancho total no debe exigir una reduccion fuerte."""
    ws = libros_excel[reporte]
    total = sum(d.width for d in ws.column_dimensions.values() if d.width)
    assert total <= ancho_maximo


def test_o3_etiqueta_de_la_diferencia_cabe_en_la_columna_b(libros_excel):
    ws = libros_excel["balance"]
    etiqueta = next(c for c in ws["B"] if isinstance(c.value, str) and c.value.startswith("Diferencia:"))
    assert etiqueta.font.b
    assert ws.column_dimensions["B"].width >= len(etiqueta.value) * 1.1  # negrita: algo mas ancha


def test_o3_textos_largos_se_ajustan_sin_perder_informacion(libros_excel):
    ws = libros_excel["dupont"]
    fuente = next(c for c in ws["A"] if c.value == "Base de saldos:")
    valor = ws.cell(fuente.row, 2)
    from calculations.dupont import BASE_SALDOS
    assert valor.value == BASE_SALDOS  # texto completo, sin recortes
    assert f"B{fuente.row}:C{fuente.row}" in {str(r) for r in ws.merged_cells.ranges}
    assert valor.alignment.wrap_text and ws.row_dimensions[fuente.row].height >= 30
    assert fuente.alignment.vertical == "top"  # la etiqueta queda junto al inicio del texto
    ws = libros_excel["dupont_con_banderas"]
    banderas = [c for c in ws["A"] if isinstance(c.value, str) and c.value.startswith("DESCUADRADO:")]
    assert banderas and all(f"A{b.row}:C{b.row}" in {str(r) for r in ws.merged_cells.ranges} for b in banderas)
    assert all(b.alignment.wrap_text for b in banderas)


def test_o3_detalle_de_controles_en_varias_lineas_y_alineado(libros_excel):
    ws = libros_excel["dupont"]
    fila = next(c.row for c in ws["A"] if c.value == "Resultado del ejercicio conciliado con la utilidad neta")
    detalle = ws.cell(fila, 3)
    assert detalle.alignment.wrap_text and len(detalle.value) > 60
    assert ws.row_dimensions[fila].height >= 30
    assert ws.cell(fila, 1).alignment.vertical == ws.cell(fila, 2).alignment.vertical == "top"


@pytest.mark.parametrize("reporte", ["balance", "resultados", "vertical", "dupont"])
def test_o3_formatos_fuentes_y_formulas_se_conservan(libros_excel, reporte):
    ws = libros_excel[reporte]
    numeros = [c for fila in ws.iter_rows() for c in fila if c.data_type == "n" and c.value is not None]
    assert numeros and all(c.number_format in ("#,##0.00", "0.00", "0.0000") for c in numeros)
    assert all((c.font.sz or 11) >= 9 for fila in ws.iter_rows() for c in fila if c.value is not None)
    formulas = [c for fila in ws.iter_rows() for c in fila if c.data_type == "f"]
    assert (len(formulas) > 0) is (reporte != "dupont")


# =================================================================== O-5 (interfaz)

def _datos_varios_anios():
    """2020-2022 completos y cuadrados (datos sinteticos)."""
    with session_scope() as s:
        for i, anio in enumerate((2020, 2021, 2022)):
            p, _ = get_or_create_fiscal_period(s, anio)
            un = 300 + 100 * i
            for codigo, valor, tipo in (("1001", 2000 + 500 * i, Tipo.BALANCE), ("1102", -100, Tipo.BALANCE),
                                        ("1101", 1000, Tipo.BALANCE), ("2001", 800, Tipo.BALANCE),
                                        ("3001", 1500 + 500 * i - un - 100, Tipo.BALANCE), ("3004", un, Tipo.BALANCE),
                                        ("4001", 5000, Tipo.RESULTADOS), ("5001", 3000, Tipo.RESULTADOS),
                                        ("6001", 1700 - un, Tipo.RESULTADOS), ("8001", 0, Tipo.RESULTADOS)):
                upsert_entry(s, fiscal_period_id=p.id, account_id=_id(s, codigo), valor=str(valor), tipo=tipo)


def _render_dupont(monkeypatch, anio):
    from reports import dupont_report

    llamadas = {"dataframe": [], "table": []}
    monkeypatch.setattr(streamlit, "dataframe", lambda df, *a, **k: llamadas["dataframe"].append((df, k)))
    monkeypatch.setattr(streamlit, "table", lambda df, *a, **k: llamadas["table"].append((df, k)))
    monkeypatch.setattr(streamlit, "selectbox", lambda label, opciones, *a, **k: next(o for o in opciones if o == anio))
    monkeypatch.setattr(streamlit, "plotly_chart", lambda *a, **k: None)
    monkeypatch.setattr(streamlit, "download_button", lambda *a, **k: None)
    with render_scope() as s:
        dupont_report.render(s, get_company(s))
    return llamadas


@pytest.mark.parametrize("anio", [2020, 2021, 2022])
def test_o5_tabla_de_resultados_muestra_todas_las_filas_incluido_el_roe(bd, monkeypatch, anio):
    _datos_varios_anios()
    llamadas = _render_dupont(monkeypatch, anio)
    tabla, opciones = next((df, k) for df, k in llamadas["dataframe"] if "Componente" in df.columns)
    assert opciones.get("height") == "content"  # sin desplazamiento interno
    assert len(tabla) == 11 and tabla["Componente"].iloc[-3] == "RSP / ROE DuPont"
    controladora = [df for df, _ in llamadas["dataframe"] if "Componente" in df.columns][1]
    assert len(controladora) == 8 and controladora["Componente"].iloc[-2] == "RSP / ROE (controladora)"


@pytest.mark.parametrize("anio", [2020, 2022])
def test_o5_controles_dupont_con_el_detalle_completo(bd, monkeypatch, anio):
    _datos_varios_anios()
    llamadas = _render_dupont(monkeypatch, anio)
    controles, opciones = next((df, k) for df, k in llamadas["table"] if "Detalle" in df.columns)
    assert opciones.get("hide_index") is True and len(controles) == 6
    detalles = list(controles["Detalle"])
    assert any(len(d) > 60 for d in detalles)  # textos largos completos (st.table los ajusta)
    assert not any("APROXIMADO" in d for d in detalles)  # tampoco el primer ejercicio (2020)


def test_o5_modificacion_de_datos_oculta_account_id_y_sigue_guardando(bd, monkeypatch):
    from modules import data_edit

    vistos = {}

    def editor(df, **k):
        vistos["columnas"], vistos["config"] = list(df.columns), k.get("column_config", {})
        df = df.copy()
        df.loc[df["Código"] == "1001", "Valor"] = 175.0
        return df

    monkeypatch.setattr(streamlit, "data_editor", editor)
    monkeypatch.setattr(streamlit, "checkbox", lambda *a, **k: False)
    monkeypatch.setattr(streamlit, "rerun", lambda *a, **k: None)
    for botones in (("Guardar cambios",), (confirmacion.ETIQUETA_CONFIRMAR,)):
        _botones(monkeypatch, *botones)
        with render_scope() as s:
            data_edit._tabla_editable(s, get_fiscal_period(s, 2021).id, Tipo.BALANCE, "USD", key="k")
    assert "account_id" in vistos["columnas"]            # el identificador sigue en los datos
    assert vistos["config"].get("account_id", "falta") is None  # pero no se muestra
    with session_scope() as s:
        assert _importes(s, Tipo.BALANCE) == {"1001": Decimal("175.00")}
