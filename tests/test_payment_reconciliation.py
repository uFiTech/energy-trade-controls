"""Tests for payment-allocation roconciliation."""

import pandas as pd
import pytest

from src.controls.payment_reconciliation import (
    reconcile_payment_allocations,
)


def test_reconcile_payment_allocations_returns_pass_when_fully_allocated() -> None:
    """A fully allocated payment should receive PASS."""
    payments = pd.DataFrame(
        {
            "Payment ID": ["PAY-1001"],
            "Payment Amount": [10_000.00],
        }
    )

    allocations = pd.DataFrame(
        {
            "Payment ID": ["PAY-1001"],
            "Applied Amount": [10_000.00],
        }
    )

    result = reconcile_payment_allocations(payments, allocations)

    assert result.loc[0, "Allocated Amount"] == 10_000.00
    assert result.loc[0, "Unallocated Amount"] == 0.00
    assert result.loc[0, "Reconciliation Status"] == "PASS"


def test_reconcile_payment_allocations_sums_multiple_allocations() -> None:
    """Multiple applications against one payment should be summed."""
    payments = pd.DataFrame(
        {
            "Payment ID": ["PAY-1001"],
            "Payment Amount": [10_000.00]
        }
    )

    allocations = pd.DataFrame(
        {
            "Payment ID": [
                "PAY-1001",
                "PAY-1001",
            ],
            "Applied Amount": [
                6_000.00,
                4_000.00,
            ],
        }
    )

    result = reconcile_payment_allocations(payments, allocations)

    assert result.loc[0, "Allocated Amount"] == 10_000.00
    assert result.loc[0, "Reconciliation Status"] == "PASS"


def test_reconcile_payment_allocations_returns_review_when_partial() -> None:
    """A positive unallocated balance should receive REVIEW."""
    payments = pd.DataFrame(
        {
            "Payment ID": ["PAY-1002"],
            "Payment Amount": [8_000.00],
        }
    )

    allocations = pd.DataFrame(
        {
            "Payment ID": ["PAY-1002"],
            "Applied Amount": [6_500.00],
        }
    )

    result = reconcile_payment_allocations(payments, allocations)

    assert result.loc[0, "Unallocated Amount"] == 1_500.00
    assert result.loc[0, "Reconciliation Status"] == "REVIEW"


def test_reconcile_payment_allocations_treats_missing_allocation_as_zero() -> None:
    """A payment without an allocation should remain in the results."""
    payments = pd.DataFrame(
        {
            "Payment ID": ["PAY-1003"],
            "Payment Amount": [5_000.00],
        }
    )

    allocations = pd.DataFrame(
        columns=[
            "Payment ID",
            "Applied Amount",
        ]
    )

    result = reconcile_payment_allocations(payments, allocations)

    assert result.loc[0, "Allocated Amount"] == 0.00
    assert result.loc[0, "Unallocated Amount"] == 5_000.00
    assert result.loc[0, "Reconciliation Status"] == "REVIEW"


def test_reconcile_payment_allocations_returns_fail_when_overallocated() -> None:
    """Allocations exceeding the payment should receive FAIL."""
    payments = pd.DataFrame(
        {
            "Payment ID": ["PAY-1004"],
            "Payment Amount": [5_000.00],
        }
    )

    allocations = pd.DataFrame(
        {
            "Payment ID": ["PAY-1004"],
            "Applied Amount": [5_250.00],
        }
    )

    result = reconcile_payment_allocations(payments, allocations)

    assert result.loc[0, "Unallocated Amount"] == -250.00
    assert result.loc[0, "Reconciliation Status"] == "FAIL"


def test_reconcile_payment_allocations_accepts_difference_within_tolerance() -> None:
    """An immaterial difference within tolerance should receive PASS."""
    payments = pd.DataFrame(
        {
            "Payment ID": ["PAY-1005"],
            "Payment Amount": [100.00],
        }
    )

    allocations = pd.DataFrame(
        {
            "Payment ID": ["PAY-1005"],
            "Applied Amount": [99.995],
        }
    )

    result = reconcile_payment_allocations(
        payments,
        allocations,
        tolerance=0.01,
    )

    assert result.loc[0, "Unallocated Amount"] == pytest.approx(0.005)
    assert result.loc[0, "Reconciliation Status"] == "PASS"


def test_reconcile_payment_allocations_raises_for_nonnumeric_amount() -> None:
    """Invalid financial amounts should not be silently converted."""
    payments = pd.DataFrame(
        {
            "Payment ID": ["PAY-1006"],
            "Payment Amount": ["invalid"],
        }
    )

    allocations = pd.DataFrame(
        {
            "Payment ID": ["PAY-1006"],
            "Applied Amount": [1_000.00],
        }
    )

    with pytest.raises(ValueError):
        reconcile_payment_allocations(payments, allocations)