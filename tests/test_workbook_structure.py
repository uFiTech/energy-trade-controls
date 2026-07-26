"""Tests for workbook structure validation."""

from src.validation.workbook_structure import (
    REQUIRED_SHEETS,
    find_missing_sheets,
)


def test_find_missing_sheets_returns_empty_when_all_exit() -> None:
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

