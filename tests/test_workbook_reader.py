"""Tests for workbook ingestion functions."""

from pathlib import Path 

import pytest
from openpyxl import Workbook
from openpyxl.worksheet.table import Table

from src.ingestion.workbook_reader import (
    list_workbook_sheets,
    map_workbook_tables,
    )


def test_list_workbook_sheets_returns_sheet_names(tmp_path: Path) -> None:
    """A valid workbook should return its worksheet names in order."""
    workbook_path = tmp_path / "test_portfolio.xlsx"

    workbook = Workbook()
    workbook.active.title = "Trades"
    workbook.create_sheet("Invoices")
    workbook.save(workbook_path)
    workbook.close()

    result = list_workbook_sheets(workbook_path)

    assert result == ["Trades", "Invoices"]


def test_list_workbook_sheets_raises_when_file_missing(
        tmp_path: Path,
) -> None:
    """A missing workbook should raise a clear file-not-found error."""
    missing_path = tmp_path / "missing_portfolio.xlsx"

    with pytest.raises(FileNotFoundError, match="Workbook not found"):
        list_workbook_sheets(missing_path)


def test_map_workbook_tables_returns_table_locations(
        tmp_path: Path,
) -> None:
    """Structured table names should map to their worksheet names."""
    workbook_path = tmp_path / "test_portfolio.xlsx"

    workbook = Workbook()

    trades_sheet = workbook.active
    trades_sheet.title = "Trades"
    trades_sheet.append(["Trade ID", "Quantity"])
    trades_sheet.append(["TRD-1001", 100_000])
    trades_sheet.add_table(
        Table(
            displayName="tblTrades",
            ref="A1:B2",
        )
    )

    invoices_sheet = workbook.create_sheet("Invoices")
    invoices_sheet.append(["Invoice ID", "Invoice Total"])
    invoices_sheet.append(["INV-2001", 1_500_000])
    invoices_sheet.add_table(
        Table(
            displayName="tblInvoices",
            ref="A1:B2",
        )
    )

    workbook.save(workbook_path)
    workbook.close()

    result = map_workbook_tables(workbook_path)

    assert result == {
        "tblTrades": "Trades",
        "tblInvoices": "Invoices",
    }


def test_map_workbook_tables_returns_empty_mapping_when_no_tables(
        tmp_path: Path,
) -> None:
    """A workbook without structured tables should return an empty mapping."""
    workbook_path = tmp_path / "empty_tables.xlsx"

    workbook = Workbook()
    workbook.save(workbook_path)
    workbook.close()

    result = map_workbook_tables(workbook_path)

    assert result == {}


def test_map_workbook_tables_raises_when_file_missing(
        tmp_path: Path,
) -> None:
    """A missing workbook should raise a clear file-not-found error."""
    missing_path = tmp_path / "missing_portfolio.xlsx"

    with pytest.raises(FileNotFoundError, match="Workbook not found"):
        map_workbook_tables(missing_path)

