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

EXPECTED_TABLE_LOCATIONS: dict[str, str] = {
    "tblTrades": "Trades",
    "tblMovements": "Movements",
    "tblInvoices": "Invoices",
    "tblPayments": "Payments",
    "tblInvoiceCharges": "Invoice Charges",
    "tblServiceCommitments": "Service Commitments",
}


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


def find_misplaced_tables(
        discovered_tables: Mapping[str, str],
        expected_locations: Mapping[str, str] =  EXPECTED_TABLE_LOCATIONS,
) -> dict[str, dict[str, str]]:
    """Returns required tables located on wrong worksheets.
    
    Missing tables are ignored because they are handled by
    find_missing_tables.
    
    Args:
        discovered_tables: Mapping of table names to actual worksheets.
        expected_locations: Mapping of table names to expected worksheets.
        
    Returns:
        A mapping describing the expected and actual worksheet for each
        misplaced table.
    """
    misplaced_tables: dict[str, dict[str, str]] = {}

    for table_name, expected_worksheet in expected_locations.items():
        if table_name not in discovered_tables:
            continue

        actual_worksheet = discovered_tables[table_name]

        if actual_worksheet != expected_worksheet:
            misplaced_tables[table_name] = {
                "expected": expected_worksheet,
                "actual": actual_worksheet,
            }

    return misplaced_tables