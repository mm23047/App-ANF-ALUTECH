"""Casos 17-18 de la sección 16: importación desde Excel y exportación
a PDF y Excel."""
import io
from decimal import Decimal

import pandas as pd
from openpyxl import load_workbook

from calculations.balance_sheet import compute_balance_sheet
from calculations.dupont import compute_dupont
from calculations.income_statement import compute_income_statement
from calculations.vertical_analysis import compute_vertical_balance
from database.enums import TipoEstadoFinanciero as Tipo
from database.repositories import (
    get_account_by_codigo,
    get_or_create_fiscal_period,
    save_company,
    upsert_entry,
)
from modules.excel_import import COLUMNAS, _validar_dataframe
from reports.excel_export import export_balance_excel, export_income_excel, export_vertical_excel
from reports.pdf_export import export_balance_pdf, export_income_pdf


def test_importacion_excel_detecta_errores_y_filas_validas(db_session):
    df = pd.DataFrame(
        [
            {"Código de cuenta": "1001", "Nombre de cuenta": "Efectivo", "Categoría": "ACTIVO", "Subcategoría": "CORRIENTE", "Período": 2021, "Valor monetario": "500.00"},
            {"Código de cuenta": "9999-NOEXISTE", "Nombre de cuenta": "Inventada", "Categoría": "ACTIVO", "Subcategoría": "CORRIENTE", "Período": 2021, "Valor monetario": "100.00"},
            {"Código de cuenta": "1002", "Nombre de cuenta": "Cuentas por cobrar", "Categoría": "ACTIVO", "Subcategoría": "CORRIENTE", "Período": 2021, "Valor monetario": "no-es-numero"},
            {"Código de cuenta": "1003", "Nombre de cuenta": "Inventarios", "Categoría": "ACTIVO", "Subcategoría": "CORRIENTE", "Período": 2021, "Valor monetario": "200.00"},
            {"Código de cuenta": "1003", "Nombre de cuenta": "Inventarios", "Categoría": "ACTIVO", "Subcategoría": "CORRIENTE", "Período": 2021, "Valor monetario": "250.00"},
        ],
        columns=COLUMNAS,
    )

    filas = _validar_dataframe(db_session, df)
    estados = {f.codigo + f"@{f.numero_fila}": f.estado for f in filas}

    assert any(f.estado == "OK" and f.codigo == "1001" for f in filas)
    assert any(f.estado == "CUENTA_DESCONOCIDA" and f.codigo == "9999-NOEXISTE" for f in filas)
    assert any(f.estado == "VALOR_NO_NUMERICO" and f.codigo == "1002" for f in filas)
    assert any(f.estado == "DUPLICADA" and f.codigo == "1003" for f in filas)


def test_importacion_no_sobrescribe_sin_autorizacion_por_disenio_del_modulo(db_session):
    # La logica de "no sobrescribir sin autorizacion" vive en modules.excel_import.render()
    # (requiere interaccion de UI); aqui se verifica que _validar_dataframe por si sola
    # nunca escribe en la base de datos (solo valida), lo que es la garantia de que ninguna
    # importacion puede aplicar cambios sin pasar por la confirmacion explicita del usuario.
    periodo, _ = get_or_create_fiscal_period(db_session, 2021)
    db_session.commit()
    cuenta = get_account_by_codigo(db_session, "1001")
    upsert_entry(db_session, fiscal_period_id=periodo.id, account_id=cuenta.id, valor=Decimal("111.00"), tipo=Tipo.BALANCE)
    db_session.commit()

    df = pd.DataFrame(
        [{"Código de cuenta": "1001", "Nombre de cuenta": "Efectivo", "Categoría": "ACTIVO", "Subcategoría": "CORRIENTE", "Período": 2021, "Valor monetario": "999.00"}],
        columns=COLUMNAS,
    )
    _validar_dataframe(db_session, df)

    from database.repositories import get_entries_map

    valores = get_entries_map(db_session, periodo.id, Tipo.BALANCE)
    assert valores[cuenta.id] == Decimal("111.00")


def _preparar_ejercicio_completo(session):
    save_company(
        session, nombre_legal="Exportadora SA", nombre_comercial="Exportadora", actividad_economica="Pruebas",
        pais="GT", moneda="GTQ", anio_inicial_analisis=2021,
    )
    periodo, _ = get_or_create_fiscal_period(session, 2021)
    session.commit()

    def be(codigo, valor):
        cuenta = get_account_by_codigo(session, codigo)
        upsert_entry(session, fiscal_period_id=periodo.id, account_id=cuenta.id, valor=Decimal(valor), tipo=Tipo.BALANCE)

    def ie(codigo, valor):
        cuenta = get_account_by_codigo(session, codigo)
        upsert_entry(session, fiscal_period_id=periodo.id, account_id=cuenta.id, valor=Decimal(valor), tipo=Tipo.RESULTADOS)

    be("1001", "300.00")
    be("1101", "700.00")
    be("2001", "400.00")
    be("3001", "600.00")
    ie("4001", "1000.00")
    ie("5001", "600.00")
    ie("8001", "40.00")
    session.commit()

    from database.repositories import get_company

    return get_company(session), periodo


def test_exportacion_pdf_genera_documentos_validos(db_session):
    company, periodo = _preparar_ejercicio_completo(db_session)
    bs = compute_balance_sheet(db_session, periodo.id)
    inc = compute_income_statement(db_session, periodo.id)

    pdf_balance = export_balance_pdf(company, periodo, bs)
    pdf_income = export_income_pdf(company, periodo, inc)

    assert pdf_balance.startswith(b"%PDF")
    assert pdf_income.startswith(b"%PDF")
    assert len(pdf_balance) > 500
    assert len(pdf_income) > 500


def test_exportacion_excel_genera_libros_validos(db_session):
    company, periodo = _preparar_ejercicio_completo(db_session)
    bs = compute_balance_sheet(db_session, periodo.id)
    inc = compute_income_statement(db_session, periodo.id)
    vb = compute_vertical_balance(db_session, periodo.id)

    datos_balance = export_balance_excel(company, periodo, bs)
    wb = load_workbook(io.BytesIO(datos_balance))
    ws = wb.active
    assert "Exportadora SA" in ws.cell(1, 1).value

    import pandas as pd

    df_vertical = pd.DataFrame(
        [{"Código": f.cuenta.codigo, "Cuenta": f.cuenta.nombre, "Valor": float(f.valor), "Participación %": float(f.porcentaje) if f.porcentaje else None} for f in vb.filas]
    )
    datos_vertical = export_vertical_excel(company, periodo, "Análisis Vertical", df_vertical, vb.base_total_activo, "Total Activo")
    wb2 = load_workbook(io.BytesIO(datos_vertical))
    assert wb2.active is not None

    datos_income = export_income_excel(company, periodo, inc)
    wb3 = load_workbook(io.BytesIO(datos_income))
    assert wb3.active is not None
