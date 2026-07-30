"""Tests for invoice-allocation reconciliation."""

import pandas as pd
import pytest

from src.controls.invoice_reconciliation import (
    reconcile_invoice_allocations,
)


def test_reconcile_invoice_allocations_returns_pass_when_fully_settled() -> None:
    "A fully allocated invoice with a correct reported balance should pass."
    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1001"],
            "Invoice Total": [100_000.00],
            "Outstanding Amount": [0.00],
        }
    )

    allocations = pd.DataFrame(
        {
            "Invoice ID": ["INV-1001"],
            "Applied Amount": [100_000.00],
        }
    )

    result = reconcile_invoice_allocations(invoices, allocations)

    assert result.loc[0, "Allocated Amount"] == 100_000.00
    assert result.loc[0, "Calculated Outstanding Amount"] == 0.00
    assert result.loc[0, "Settlement Status"] == "PASS"
    assert result.loc[0, "Outstanding Variance"] == 0.00
    assert result.loc[0, "Reported Balance Status"] == "PASS"


def test_reconcile_invoice_allocations_sums_multiple_payments() -> None:
    """Several payments applied to one invoice should be summed."""
    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1002"],
            "Invoice Total": [100_000.00],
            "Outstanding Amount": [15_000.00],
        }
    )

    allocations = pd.DataFrame(
        {
            "Invoice ID": [
                "INV-1002",
                "INV-1002",
            ],
            "Applied Amount": [
                60_000.00,
                25_000.00,
            ],
        }
    )

    result = reconcile_invoice_allocations(invoices, allocations)

    assert result.loc[0, "Allocated Amount"] == 85_000.00
    assert result.loc[0, "Calculated Outstanding Amount"] == 15_000.00
    assert result.loc[0, "Settlement Status"] == "REVIEW"
    assert result.loc[0, "Reported Balance Status"] == "PASS"


def test_reconcile_invoice_allocations_treats_missing_allocation_as_zero() -> None:
    """An invoice without allocations should remain visible and open."""
    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1003"],
            "Invoice Total": [50_000.00],
            "Outstanding Amount": [50_000.00],
        }
    )

    allocations = pd.DataFrame(
        columns=[
            "Invoice ID",
            "Applied Amount",
        ]
    )

    result = reconcile_invoice_allocations(invoices, allocations)

    assert result.loc[0, "Allocated Amount"] == 0.00
    assert result.loc[0, "Calculated Outstanding Amount"] == 50_000.00
    assert result.loc[0, "Settlement Status"] == "REVIEW"
    assert result.loc[0, "Reported Balance Status"] == "PASS"


def test_reconcile_invoice_allocations_returns_fail_when_overallocated() -> None:
    """Allocations exceeding the invoice total should fail."""
    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1004"],
            "Invoice Total": [50_000.00],
            "Outstanding Amount": [-250.00],
        }
    )

    allocations = pd.DataFrame(
        {
            "Invoice ID": ["INV-1004"],
            "Applied Amount": [50_250.00],
        }
    )

    result = reconcile_invoice_allocations(invoices, allocations)

    assert result.loc[0, "Calculated Outstanding Amount"] == -250.00
    assert result.loc[0, "Settlement Status"] == "FAIL"
    assert result.loc[0, "Reported Balance Status"] == "PASS"


def test_reconcile_invoice_allocations_flags_reported_balance_mismatch() -> None:
    """An incorrect workbook outstanding balance should require review."""
    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1005"],
            "Invoice Total": [80_000.00],
            "Outstanding Amount": [10_000.00],
        }
    )

    allocations = pd.DataFrame(
        {
            "Invoice ID": ["INV-1005"],
            "Applied Amount": [60_000.00],
        }
    )

    result = reconcile_invoice_allocations(invoices, allocations)

    assert result.loc[0, "Calculated Outstanding Amount"] == 20_000.00
    assert result.loc[0, "Outstanding Variance"] == 10_000.00
    assert result.loc[0, "Settlement Status"] == "REVIEW"
    assert result.loc[0, "Reported Balance Status"] == "REVIEW"


def test_reconcile_invoice_allocations_accepts_values_within_tolerance() -> None:
    """Immaterial settlement and balance differences should pass."""
    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1006"],
            "Invoice Total": [100.00],
            "Outstanding Amount": [0.00],
        }
    )

    allocations = pd.DataFrame(
        {
            "Invoice ID": ["INV-1006"],
            "Applied Amount": [99.995],
        }
    )

    result = reconcile_invoice_allocations(
        invoices,
        allocations,
        tolerance=0.01,
    )

    assert result.loc[0, "Calculated Outstanding Amount"] == pytest.approx(
        0.005
    )
    assert result.loc[0, "Settlement Status"] == "PASS"
    assert result.loc[0, "Outstanding Variance"] == pytest.approx(0.005)
    assert result.loc[0, "Reported Balance Status"] == "PASS"


def test_reconcile_invoice_allocations_raises_for_nonnumeric_amount() -> None:
    """Invalid financial amounts should not be silently accepted."""
    invoices = pd.DataFrame(
        {
            "Invoice ID": ["INV-1007"],
            "Invoice Total": ["invalid"],
            "Outstanding Amount": [0.00],
        }
    )

    allocations = pd.DataFrame(
        {
            "Invoice ID": ["INV-1007"],
            "Applied Amount": [1_000.00],
        }
    )

    with pytest.raises(ValueError):
        reconcile_invoice_allocations(invoices, allocations)


