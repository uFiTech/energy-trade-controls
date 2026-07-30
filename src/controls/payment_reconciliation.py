"""Controls for reconciling payments to invoice allocations."""

import pandas as pd

def reconcile_payment_allocations(
        payments: pd.DataFrame,
        payment_allocations: pd.DataFrame,
        tolerance: float = 0.01,
) -> pd.DataFrame:
    """Reconcile each payment amount to its total applied allocations.
    
    Args:
        payments: Payment records containing Payment ID and Payment Amount.
        payment_allocations: Allocation records containing Payment ID and
            Applied Amount.
        tolerance: Permitted absolute allocation difference.

    Returns: 
        A DataFrame containing payment, allocation, difference and status 
        results.

    Raises:
        ValueError: If payment or allocation amounts are not numeric. 
    """
    payment_data = payments[
        ["Payment ID", "Payment Amount"]
    ].copy()

    allocation_data = payment_allocations[
        ["Payment ID", "Applied Amount"]
    ].copy()

    payment_data["Payment Amount"] = pd.to_numeric(
        payment_data["Payment Amount"], 
        errors="raise",
    )

    allocation_data["Applied Amount"] = pd.to_numeric(
        allocation_data["Applied Amount"],
        errors="raise",
    )

    allocation_totals = (
        allocation_data
        .groupby("Payment ID", as_index=False)["Applied Amount"]
        .sum()
        .rename(
            columns={
                "Applied Amount": "Allocated Amount",
            }
        )
    )

    reconciliation = payment_data.merge(
        allocation_totals,
        on="Payment ID",
        how="left",
        validate="one_to_one",
    )

    reconciliation["Allocated Amount"] = (
        reconciliation["Allocated Amount"].fillna(0.0)
    )

    reconciliation["Unallocated Amount"] = (
        reconciliation["Payment Amount"]
        - reconciliation["Allocated Amount"]
    )

    reconciliation["Reconciliation Status"] = "PASS"

    review_mask = (
        reconciliation["Unallocated Amount"] > tolerance
    )

    fail_mask = (
        reconciliation["Unallocated Amount"] < -tolerance
    )

    reconciliation.loc[
        review_mask,
        "Reconciliation Status",
    ] = "REVIEW"

    reconciliation.loc[
        fail_mask,
        "Reconciliation Status"
    ] = "FAIL"

    return reconciliation