"""Validation functions for workbook structure."""

from collections.abc import Mapping, Sequence


REQUIRED_SHEETS: tuple[str, ...] = (
    "Trades",
    "Movements",
    "Invoices",
    "Payments",
    "Invoice Charges",
    "Service Commitments",
)

REQUIRED_TABLES: tuple[str, ...] = (
    "tblTrades",
    "tblMovements",
    "tblInvoices",
    "tblPayments",
    "tblInvoiceCharges",
    "tblServiceCommitments",
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


def find_missing_tables(
        discovered_tables: Mapping[str, str],
        required_tables: Sequence[str] = REQUIRED_TABLES,
) -> list[str]:
    """Return required Excel table names that are missing.
    
    Args:
        discovered_tables: Mapping of Excel table names to worksheet names.
        required_tables: Excel table names required by the automation.
        
    Returns:
        Missing table names in required-table-order.
    """
    return [
        table
        for table in required_tables
        if table not in discovered_tables
    ]