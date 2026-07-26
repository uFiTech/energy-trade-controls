"""Validation functions for workbook structure."""

from collections.abc import Sequence


REQUIRED_SHEETS: tuple[str, ...] = (
    "Trades",
    "Movements",
    "Invoices",
    "Payments",
    "Invoice Charges",
    "Service Commitments",
)


def find_missing_sheets(
        actual_sheets: Sequence[str],
        required_sheets: Sequence[str] = REQUIRED_SHEETS,
) -> list[str]:
    """Return required worksheet names that are missing from a workbook.

    Args:
        actual_sheets: Workbook names found in the workbook.
        required_sheets: Workbook names required by the automation.

    Returns:
        Missing workbook names in required-sheet order.
    """

    actual_sheet_names = set(actual_sheets)

    return [
        sheet
        for sheet in required_sheets
        if sheet not in actual_sheet_names
    ]