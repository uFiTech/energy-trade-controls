"""Tests for settlement-case linkage."""

import pandas as pd
import pytest

from src.controls.settlement_case_linkage import (
    assign_settlement_cases,
)


def test_links_payment_and_invoice_exception_through_allocation() -> None:
    """An allocation should put related payment and invoice exceptions together."""
    report = pd.DataFrame(
        {
            "Control Area": ["PAYMENT", "INVOICE"],
            "Record ID": ["PAY-1001", "INV-1001"],
        }
    )

    allocations = pd.DataFrame(
        {
            "Payment ID": ["PAY-1001"],
            "Invoice ID": ["INV-1001"],
        }
    )

    result = assign_settlement_cases(report, allocations)

    assert result.loc[0, "Settlement Case ID"] == result.loc[
        1,
        "Settlement Case ID",
    ]
    assert result.loc[0, "Related Records"] == "INV-1001"
    assert result.loc[1, "Related Records"] == "PAY-1001"
    assert result.loc[0, "Link Basis"] == "PAYMENT ALLOCATION RECORD"
    assert result.loc[1, "Link Basis"] == "PAYMENT ALLOCATION RECORD"


def test_unlinked_exception_receives_its_own_case() -> None:
    """An exception without another exception link should remain its own case."""
    report = pd.DataFrame(
        {
            "Control Area": ["INVOICE"],
            "Record ID": ["INV-1002"],
        }
    )

    allocations = pd.DataFrame(
        columns=[
            "Payment ID",
            "Invoice ID",
        ]
    )

    result = assign_settlement_cases(report, allocations)

    assert result.loc[0, "Settlement Case ID"] == "CASE-001"
    assert result.loc[0, "Related Records"] == ""
    assert result.loc[0, "Link Basis"] == "NO DIRECT EXCEPTION LINK"


def test_one_payment_can_link_to_multiple_invoice_exceptions() -> None:
    """One payment allocated across several exception invoices should form one case."""
    report = pd.DataFrame(
        {
            "Control Area": [
                "PAYMENT",
                "INVOICE",
                "INVOICE",
            ],
            "Record ID": [
                "PAY-1003",
                "INV-1003",
                "INV-1004",
            ],
        }
    )

    allocations = pd.DataFrame(
        {
            "Payment ID": [
                "PAY-1003",
                "PAY-1003",
            ],
            "Invoice ID": [
                "INV-1003",
                "INV-1004",
            ],
        }
    )

    result = assign_settlement_cases(report, allocations)

    assert result["Settlement Case ID"].nunique() == 1

    payment_related = set(
        result.loc[0, "Related Records"].split(", ")
    )

    assert payment_related == {
        "INV-1003",
        "INV-1004",
    }


def test_connected_chain_forms_one_settlement_case() -> None:
    """Indirect allocation connections should remain one economic case."""
    report = pd.DataFrame(
        {
            "Control Area": [
                "PAYMENT",
                "INVOICE",
                "PAYMENT",
            ],
            "Record ID": [
                "PAY-1004",
                "INV-1005",
                "PAY-1005",
            ],
        }
    )

    allocations = pd.DataFrame(
        {
            "Payment ID": [
                "PAY-1004",
                "PAY-1005",
            ],
            "Invoice ID": [
                "INV-1005",
                "INV-1005",
            ],
        }
    )

    result = assign_settlement_cases(report, allocations)

    assert result["Settlement Case ID"].nunique() == 1


def test_matching_amounts_do_not_create_a_link() -> None:
    """Exceptions must not be linked merely because their amounts match."""
    report = pd.DataFrame(
        {
            "Control Area": [
                "PAYMENT",
                "INVOICE",
            ],
            "Record ID": [
                "PAY-1006",
                "INV-1006",
            ],
            "Exception Amount": [
                5_000.00,
                5_000.00,
            ],
        }
    )

    allocations = pd.DataFrame(
        columns=[
            "Payment ID",
            "Invoice ID",
        ]
    )

    result = assign_settlement_cases(report, allocations)

    assert result["Settlement Case ID"].nunique() == 2
    assert result["Related Records"].tolist() == ["", ""]


def test_raises_when_report_column_is_missing() -> None:
    """Missing exception-report identifiers should raise a clear error."""
    report = pd.DataFrame(
        {
            "Record ID": ["PAY-1007"],
        }
    )

    allocations = pd.DataFrame(
        columns=[
            "Payment ID",
            "Invoice ID",
        ]
    )

    with pytest.raises(
        KeyError,
        match="Missing exception report columns",
    ):
        assign_settlement_cases(report, allocations)


def test_raises_when_allocation_column_is_missing() -> None:
    """Missing allocation relationship fields should raise a clear error."""
    report = pd.DataFrame(
        {
            "Control Area": ["PAYMENT"],
            "Record ID": ["PAY-1008"],
        }
    )

    allocations = pd.DataFrame(
        {
            "Payment ID": ["PAY-1008"],
        }
    )

    with pytest.raises(
        KeyError,
        match="Missing payment allocation columns",
    ):
        assign_settlement_cases(report, allocations)
