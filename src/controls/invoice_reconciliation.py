"""Controls for reconciling invoices ro payment allocations."""

import pandas as pd

def reconcile_invoice_allocations(
        invoices: pd.DataFrame,
        payment_allocations: pd.DataFrame,
        tolerance: float = 0.01,
) -> pd.DataFrame:
    """Reconcile invoice totals to payment allocations and reported balances.
    Args:
        invoices: Invoice records containing Invoice ID, Invoice Total,
            and Outstanding Amount.
        payment_allocations: Allocation records containing Invoice ID
            and Applied Amount.
        tolerance: Permitted absolute reconciliation difference.
        
    Returns:
        A DataFrame containing calculated outstanding amounts,
        settlement statuses, and reported-balance comparison results.

    Raises:
        ValueError: If invoice or allocation amounts are not numeric.
    """

    invoice_data = invoices[
        [
            "Invoice ID",
            "Invoice Total",
            "Outstanding Amount",
        ]
    ].copy()

    allocation_data = payment_allocations[
        [
            "Invoice ID",
            "Applied Amount",
        ]
    ].copy()

    invoice_data["Invoice Total"] = pd.to_numeric(
        invoice_data["Invoice Total"],
        errors="raise",
    )

    invoice_data["Outstanding Amount"] = pd.to_numeric(
        invoice_data["Outstanding Amount"],
        errors="raise",
    )

    allocation_data["Applied Amount"] = pd.to_numeric(
        allocation_data["Applied Amount"],
        errors="raise",
    )

    allocation_totals = (
        allocation_data
        .groupby("Invoice ID", as_index=False)["Applied Amount"]
        .sum()
        .rename(
            columns={
                "Applied Amount": "Allocated Amount",
            }
        )
    )

    reconciliation = invoice_data.merge(
        allocation_totals,
        on="Invoice ID",
        how="left",
        validate="one_to_one",
    )

    reconciliation["Allocated Amount"] = (
        reconciliation["Allocated Amount"].fillna(0.0)
    )

    reconciliation["Calculated Outstanding Amount"] = (
        reconciliation["Invoice Total"]
        - reconciliation["Allocated Amount"]
    )

    reconciliation["Settlement Status"] = "PASS"

    review_mask = (
        reconciliation["Calculated Outstanding Amount"] > tolerance
    )

    fail_mask = (
        reconciliation["Calculated Outstanding Amount"] < -tolerance
    )

    reconciliation.loc[
        review_mask,
        "Settlement Status",
    ] = "REVIEW"

    reconciliation.loc[
        fail_mask,
        "Settlement Status",
    ] = "FAIL"

    reconciliation["Outstanding Variance"] = (
        reconciliation["Calculated Outstanding Amount"]
        - reconciliation["Outstanding Amount"]
    )

    reconciliation["Reported Balance Status"] = "PASS"

    balance_review_mask = (
        reconciliation["Outstanding Variance"].abs() > tolerance
    )

    reconciliation.loc[
        balance_review_mask,
        "Reported Balance Status",
    ] = "REVIEW"

    return reconciliation