"""Test for consolidated operational exception report."""

import pandas as pd
import pytest

from src.reporting.exception_report import (
    REPORT_COLUMNS,
    build_consolidated_exception_report,
)


def test_payment_review_becomes_medium_unallocated_exception() -> None:
    """A partially allocated payment should become a medium action item."""
    payments = pd.DataFrame(
        {
            "Payment ID": ["PAY-1001"],
            "Unallocated Amount": [2_000.00],
            "Reconciliation Status": ["REVIEW"],
        }
    )

    invoices = pd.DataFrame(
        columns=[
            "Invoice ID",
            "Outstanding Variance",
            "Balance Reconciliation Status",
            "Exception Classification",
        ]
    )

    result = build_consolidated_exception_report(
        payments, 
        invoices,
    )

    assert result.loc[0, "Control Area"] == "PAYMENT"
    assert result.loc[0, "Record ID"] == "PAY-1001"
    assert result.loc[0, "Exception Type"] == "UNALLOCATED PAYMENT"
    assert result.loc[0, "Exception Amount"] == 2_000.00
    assert result.loc[0, "Source Status"] == "REVIEW"
    assert result.loc[0, "Severity"] == "MEDIUM"
    assert result.loc[0, "Classification"] == "ACTION REQUIRED"


def test_payment_fail_becomes_high_overallocated_exception() -> None:
    """An overallocated payment should become a high-severity action item."""
    payments = pd.DataFrame(
        {
            "Payment ID": ["PAY-1002"],
            "Unallocated Amount": [-500.00],
            "Reconciliation Status": ["FAIL"],
        }
    )

    invoices = pd.DataFrame(
        columns=[
            "Invoice ID",
            "Outstanding Variance",
            "Balance Reconciliation Status",
            "Exception Classification",
        ]
    )

    result = build_consolidated_exception_report(
        payments,
        invoices,
    )

    assert result.loc[0, "Exception Type"] == "OVERALLOCATED PAYMENT"
    assert result.loc[0, "Exception Amount"] == 500.00
    assert result.loc[0, "Severity"] == "HIGH"
    assert result.loc[0, "Classification"] == "ACTION REQUIRED"


def test_active_invoice_exception_becomes_high_action_item() -> None:
    """An active invoice balance mismatch should be high severity."""
    payments = pd.DataFrame(
        columns=[
            "Payment ID",
            "Unallocated Amount",
            "Reconciliation Status",
        ]
    )

    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1001"],
            "Outstanding Variance": [7_500.00],
            "Balance Reconciliation Status": ["REVIEW"],
            "Exception Classification": ["ACTION REQUIRED"],
        }
    )

    result = build_consolidated_exception_report(
        payments,
        invoices,
    )

    assert result.loc[0, "Control Area"] == "INVOICE"
    assert result.loc[0, "Record ID"] == "INV-1001"
    assert result.loc[0, "Exception Type"] == "BALANCE MISMATCH"
    assert result.loc[0, "Exception Amount"] == 7_500.00
    assert result.loc[0, "Severity"] == "HIGH"
    assert result.loc[0, "Classification"] == "ACTION REQUIRED"


def test_controlled_exclusion_remains_visible_with_info_severity() -> None:
    """A controlled exclusion should remain visible without active severity."""
    payments = pd.DataFrame(
        columns=[
            "Payment ID",
            "Unallocated Amount",
            "Reconciliation Status",
        ]
    )

    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1002"],
            "Outstanding Variance": [1_500.00],
            "Balance Reconciliation Status": ["REVIEW"],
            "Exception Classification": ["CONTROLLED EXCLUSION"],
        }
    )

    result = build_consolidated_exception_report(
        payments,
        invoices,
    )

    assert len(result) == 1
    assert result.loc[0, "Exception Amount"] == 1_500.00
    assert result.loc[0, "Severity"] == "INFO"
    assert (
        result.loc[0, "Classification"]
        == "CONTROLLED EXCLUSION"
    )


def test_clear_records_are_excluded_from_exception_report() -> None:
    """Clean payment and invoice records should not enter the exception queue."""
    payments = pd.DataFrame(
        {
            "Payment ID": ["PAY-1003"],
            "Unallocated Amount": [0.00],
            "Reconciliation Status": ["PASS"],
        }
    )

    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1003"],
            "Outstanding Variance": [0.00],
            "Balance Reconciliation Status": ["PASS"],
            "Exception Classification": ["CLEAR"],
        }
    )

    result = build_consolidated_exception_report(
        payments,
        invoices,
    )

    assert result.empty
    assert result.columns.tolist() == REPORT_COLUMNS


def test_raises_when_payment_column_is_missing() -> None:
    """Missing payment reconciliation inputs should raise a clear error."""
    payments = pd.DataFrame(
        {
            "Payment ID": ["PAY-1004"],
        }
    )

    invoices = pd.DataFrame(
        columns=[
            "Invoice ID",
            "Outstanding Variance",
            "Balance Reconciliation Status",
            "Exception Classification",
        ]
    )

    with pytest.raises(
        KeyError,
        match="Missing payment reconciliation columns",
    ):
        build_consolidated_exception_report(
            payments,
            invoices,
        )


def test_raises_when_invoice_column_is_missing() -> None:
    """Missing invoice classification inputs should raise a clear error."""
    payments = pd.DataFrame(
        columns=[
            "Payment ID",
            "Unallocated Amount",
            "Reconciliation Status",
        ]
    )

    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1004"],
        }
    )

    with pytest.raises(
        KeyError,
        match="Missing invoice classification columns",
    ):
        build_consolidated_exception_report(
            payments,
            invoices,
        )




