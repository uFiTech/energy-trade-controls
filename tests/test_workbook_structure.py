"""Tests for workbook structure validation."""

from src.validation.workbook_structure import (
    REQUIRED_SHEETS,
    REQUIRED_TABLES,
    find_missing_sheets,
    find_missing_tables,
)


def test_find_missing_sheets_returns_empty_when_all_exist() -> None:
    """No sheets should be reported when every requirement is present."""
    actual_sheets = [*REQUIRED_SHEETS, "Dashboard", "Claims"]

    result = find_missing_sheets(actual_sheets)

    assert result == []


def test_find_missing_sheets_returns_missing_names_in_required_order() -> None:
    """Missing sheets should follow the configured requirement order."""
    actual_sheets = [
        "Trades",
        "Payments",
        "Dashboard",
    ]

    result = find_missing_sheets(actual_sheets)

    assert result == [
        "Movements",
        "Invoices",
        "Invoice Charges",
        "Service Commitments",
    ]


def test_find_missing_sheets_returns_all_when_workbook_is_empty() -> None:
    """An empty workbook sheet list should fail every requirement."""
    result = find_missing_sheets([])

    assert result == list(REQUIRED_SHEETS)


def test_find_missing_tables_returns_empty_when_all_exist() -> None:
    """No tables should be reported when every requirement exist."""
    discovered_tables = {
        table: f"Sheet for {table}"
        for table in REQUIRED_TABLES
    }
    discovered_tables["tblClaims"] = "Claims"

    result = find_missing_tables(discovered_tables)

    assert result == []


def test_find_missing_tables_returns_missing_names_in_required_order() -> None:
    """Missing tables should follow the configured requirement order."""
    discovered_tables = {
         "tblTrades": "Trades",
        "tblPayments": "Payments",
        "tblClaims": "Claims",
    }

    result = find_missing_tables(discovered_tables)

    assert result == [
        "tblMovements",
        "tblInvoices",
        "tblInvoiceCharges",
        "tblServiceCommitments",
    ]


def test_find_missing_tables_returns_all_when_mapping_is_empty() -> None:
    """An empty table mapping should fail every table requirement."""
    result = find_missing_tables({})

    assert result == list(REQUIRED_TABLES)

