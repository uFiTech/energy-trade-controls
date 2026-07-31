"""Classification of invoice balance-reconciliation exceptions."""

import pandas as pd


def classify_invoice_balance_exceptions(
        reconciliation: pd.DataFrame,
        invoices: pd.DataFrame,
) -> pd.DataFrame:
    """Classify invoice balance mismatches by active settlement scope.

    Cancelled invoices remain visible but are treated as controlled
    exclusions rather than active settlement exposure.

    Args:
        reconciliation: Invoice reconciliation results containing Invoice ID
            and Reported Balance Status.
        invoices: Invoice records containing Invoice ID and Invoice Status.

    Returns:
        Reconciliation results with Invoice Status, Settlement Scope,
        and Exception Classification added.

    Raises:
        KeyError: If a required column is missing.
    """

    reconciliation_required = {
        "Invoice ID",
        "Reported Balance Status",
    }

    invoice_required = {
        "Invoice ID",
        "Invoice Status",
    }

    missing_reconciliation_columns = (
        reconciliation_required - set(reconciliation.columns)
    )

    if missing_reconciliation_columns:
        raise KeyError(
            "Missing reconciliation columns: "
            f"{sorted(missing_reconciliation_columns)}"
        )

    missing_invoice_columns = (
        invoice_required - set(invoices.columns)
    )

    if missing_invoice_columns:
        raise KeyError(
            "Missing invoice columns: "
            f"{sorted(missing_invoice_columns)}"
        )

    invoice_statuses = invoices[
        [
            "Invoice ID",
            "Invoice Status",
        ]
    ].copy()

    classified = reconciliation.merge(
        invoice_statuses,
        on="Invoice ID",
        how="left",
        validate="one_to_one",
    )

    normalized_status = (
        classified["Invoice Status"]
        .astype("string")
        .fillna("")
        .str.strip()
        .str.upper()
    )

    classified["Settlement Scope"] = "ACTIVE"

    cancelled_mask = normalized_status.eq("CANCELLED")

    classified.loc[
        cancelled_mask,
        "Settlement Scope",
    ] = "OUT OF SCOPE"


    classified["Exception Classification"] = "CLEAR"

    active_exception_mask = (
        classified["Reported Balance Status"].eq("REVIEW")
        & classified["Settlement Scope"].eq("ACTIVE")
    )

    controlled_exclusion_mask = (
        classified["Reported Balance Status"].eq("REVIEW")
        & classified["Settlement Scope"].eq("OUT OF SCOPE")
    )

    classified.loc[
        active_exception_mask,
        "Exception Classification",
    ] = "ACTION REQUIRED"

    classified.loc[
        controlled_exclusion_mask,
        "Exception Classification",
    ] = "CONTROLLED EXCLUSION"

    return classified

    

    

    

