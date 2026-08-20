"""Controls for reconciling invoices to payment allocations."""

import pandas as pd

def reconcile_invoice_allocations(
        invoices: pd.DataFrame,
        payment_allocations: pd.DataFrame,
        tolerance: float = 0.01,
) -> pd.DataFrame:
    """Reconcile invoice totals to payment allocations and reported balances.
    Args:
        invoices: Invoice records containing Invoice ID, Invoice Total,
            and Reported Outstanding Amount.
        payment_allocations: Allocation records containing Invoice ID
            and Applied Amount.
        tolerance: Permitted absolute reconciliation difference.
        
    Returns:
        A DataFrame containing calculated outstanding amounts,
        settlement positions, and reported-balance comparison results.

    Raises:
        ValueError: If invoice or allocation amounts are not numeric.
    """

    invoice_data = invoices[
        [
            "Invoice ID",
            "Invoice Total",
            "Reported Outstanding Amount",
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

    invoice_data["Reported Outstanding Amount"] = pd.to_numeric(
        invoice_data["Reported Outstanding Amount"],
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

    reconciliation["Settlement Position"] = "SETTLED"

    open_balance_mask = (
        reconciliation["Calculated Outstanding Amount"] > tolerance
    )

    overpaid_mask = (
        reconciliation["Calculated Outstanding Amount"] < -tolerance
    )

    reconciliation.loc[
        open_balance_mask,
        "Settlement Position",
    ] = "OPEN BALANCE"

    reconciliation.loc[
        overpaid_mask,
        "Settlement Position",
    ] = "OVERPAID"

    reconciliation["Outstanding Variance"] = (
        reconciliation["Calculated Outstanding Amount"]
        - reconciliation["Reported Outstanding Amount"]
    )

    reconciliation["Balance Reconciliation Status"] = "PASS"

    balance_review_mask = (
        reconciliation["Outstanding Variance"].abs() > tolerance
    )

    reconciliation.loc[
        balance_review_mask,
        "Balance Reconciliation Status",
    ] = "REVIEW"

    return reconciliation