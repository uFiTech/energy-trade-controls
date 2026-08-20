"""Tests for invoice balance-exception classification."""

import pandas as pd
import pytest

from src.controls.invoice_exception_classification import (
    classify_invoice_balance_exceptions,
)


def test_classifies_active_balance_mismatch_as_action_required() -> None:
    """An active invoice mismatch should require action."""
    reconciliation = pd.DataFrame(
        {
            "Invoice ID": ["INV-1001"],
            "Balance Reconciliation Status": ["REVIEW"],
            "Outstanding Variance": [5_000.00],
        }
    )

    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1001"],
            "Invoice Status": ["On Hold"],
        }
    )

    result = classify_invoice_balance_exceptions(
        reconciliation,
        invoices,
    )

    assert result.loc[0, "Settlement Scope"] == "ACTIVE"
    assert result.loc[0, "Exception Classification"] == "ACTION REQUIRED"


def test_classifies_cancelled_mismatch_as_controlled_exclusion() -> None:
    """A cancelled invoice mismatch should remain visible but excluded."""
    reconciliation = pd.DataFrame(
        {
            "Invoice ID": ["INV-1002"],
            "Balance Reconciliation Status": ["REVIEW"],
            "Outstanding Variance": [1_500.00],
        }
    )

    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1002"],
            "Invoice Status": ["Cancelled"],
        }
    )

    result = classify_invoice_balance_exceptions(
        reconciliation,
        invoices,
    )

    assert result.loc[0, "Outstanding Variance"] == 1_500.00
    assert result.loc[0, "Settlement Scope"] == "OUT OF SCOPE"
    assert (
        result.loc[0, "Exception Classification"]
        == "CONTROLLED EXCLUSION"
    )


def test_classifies_balanced_invoice_as_clear() -> None:
    """An invoice without a balance mismatch should be clear."""
    reconciliation = pd.DataFrame(
        {
            "Invoice ID": ["INV-1003"],
            "Balance Reconciliation Status": ["PASS"],
        }
    )

    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1003"],
            "Invoice Status": ["Open"],
        }
    )

    result = classify_invoice_balance_exceptions(
        reconciliation,
        invoices,
    )

    assert result.loc[0, "Settlement Scope"] == "ACTIVE"
    assert result.loc[0, "Exception Classification"] == "CLEAR"


def test_normalizes_cancelled_invoice_status() -> None:
    """Case and surrounding spaces should not affect classification."""
    reconciliation = pd.DataFrame(
        {
            "Invoice ID": ["INV-1004"],
            "Balance Reconciliation Status": ["REVIEW"],
        }
    )

    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1004"],
            "Invoice Status": ["  cancelled  "],
        }
    )

    result = classify_invoice_balance_exceptions(
        reconciliation,
        invoices,
    )

    assert result.loc[0, "Settlement Scope"] == "OUT OF SCOPE"
    assert (
        result.loc[0, "Exception Classification"]
        == "CONTROLLED EXCLUSION"
    )


def test_retains_reconciliation_row_when_invoice_status_is_missing() -> None:
    """A left join should retain a reconciliation row without status data."""
    reconciliation = pd.DataFrame(
        {
            "Invoice ID": ["INV-1005"],
            "Balance Reconciliation Status": ["REVIEW"],
        }
    )

    invoices = pd.DataFrame(
        columns=[
            "Invoice ID",
            "Invoice Status",
        ]
    )

    result = classify_invoice_balance_exceptions(
        reconciliation,
        invoices,
    )

    assert len(result) == 1
    assert result.loc[0, "Settlement Scope"] == "ACTIVE"
    assert result.loc[0, "Exception Classification"] == "ACTION REQUIRED"


def test_raises_when_reconciliation_column_is_missing() -> None:
    """Missing reconciliation inputs should raise a clear error."""
    reconciliation = pd.DataFrame(
        {
            "Invoice ID": ["INV-1006"],
        }
    )

    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1006"],
            "Invoice Status": ["Open"],
        }
    )

    with pytest.raises(
        KeyError,
        match="Missing reconciliation columns",
    ):
        classify_invoice_balance_exceptions(
            reconciliation,
            invoices,
        )


def test_raises_when_invoice_column_is_missing() -> None:
    """Missing invoice status inputs should raise a clear error."""
    reconciliation = pd.DataFrame(
        {
            "Invoice ID": ["INV-1007"],
            "Balance Reconciliation Status": ["PASS"],
        }
    )

    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1007"],
        }
    )

    with pytest.raises(
        KeyError,
        match="Missing invoice columns",
    ):
        classify_invoice_balance_exceptions(
            reconciliation,
            invoices,
        )