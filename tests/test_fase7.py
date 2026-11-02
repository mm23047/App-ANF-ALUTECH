"""Fase 7: correcciones de la validacion operativa (O-1 a O-5)."""
import io
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
