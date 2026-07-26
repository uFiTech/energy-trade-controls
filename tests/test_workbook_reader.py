"""Tests for workbook ingestion functions."""

from pathlib import Path 

import pytest
from openpyxl import Workbook

from src.ingestion.workbook_reader import list_workbook_sheets


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