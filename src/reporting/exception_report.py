"""Build consolidated operational exception reports."""

import pandas as pd


REPORT_COLUMNS: list[str] = [
    "Control Area",
    "Record ID",
    "Exception Type",
    "Exception Amount",
    "Source Status",
    "Severity",
    "Classification",
]


def build_consolidated_exception_report(
        payment_reconciliation: pd.DataFrame,
        invoice_classification: pd.DataFrame,
) -> pd.DataFrame:
    """Combine payment and invoice exceptions into one operational report.

    Args:
        payment_reconciliation: Payment reconciliation results.
        invoice_classification: Classified invoice reconciliation results.

    Returns:
        A standardized DataFrame containing actionable exceptions and
        controlled exclusions.

    Raises:
        KeyError: If required input columns are missing.
    """
    required_payment_columns = {
        "Payment ID",
        "Unallocated Amount",
        "Reconciliation Status",
    }

    required_invoice_columns = {
        "Invoice ID",
        "Outstanding Variance",
        "Balance Reconciliation Status",
        "Exception Classification",
    }

    missing_payment_columns = (
        required_payment_columns
        - set(payment_reconciliation.columns)
    )

    if missing_payment_columns:
        raise KeyError(
            "Missing payment reconciliation columns: "
            f"{sorted(missing_payment_columns)}"
        )

    missing_invoice_columns = (
        required_invoice_columns
        - set(invoice_classification.columns)
    )

    if missing_invoice_columns:
        raise KeyError(
            "Missing invoice classification columns: "
            f"{sorted(missing_invoice_columns)}"
        )

    payment_exceptions = payment_reconciliation[
        payment_reconciliation["Reconciliation Status"].ne("PASS")
    ].copy()

    payment_report = pd.DataFrame(
        {
            "Control Area": "PAYMENT",
            "Record ID": payment_exceptions["Payment ID"],
            "Exception Amount": (
                payment_exceptions["Unallocated Amount"].abs()
            ),
            "Source Status": (
                payment_exceptions["Reconciliation Status"]
            ),
            "Classification": "ACTION REQUIRED",
        }
    )

    payment_report["Exception Type"] = "UNALLOCATED PAYMENT"
    payment_report["Severity"] = "MEDIUM"

    payment_fail_mask = (
        payment_report["Source Status"].eq("FAIL")
    )

    payment_report.loc[
        payment_fail_mask,
        "Exception Type",
    ] = "OVERALLOCATED PAYMENT"

    payment_report.loc[
        payment_fail_mask,
        "Severity",
    ] = "HIGH"

    invoice_exceptions = invoice_classification[
        invoice_classification[
            "Exception Classification"
        ].ne("CLEAR")
    ].copy()

    invoice_report = pd.DataFrame(
        {
            "Control Area": "INVOICE",
            "Record ID": invoice_exceptions["Invoice ID"],
            "Exception Type": "BALANCE MISMATCH",
            "Exception Amount": (
                invoice_exceptions["Outstanding Variance"].abs()
            ),
            "Source Status": (
                invoice_exceptions["Balance Reconciliation Status"]
            ),
            "Classification": (
                invoice_exceptions["Exception Classification"]
            ),
        }
    )

    invoice_report["Severity"] = "INFO"

    invoice_action_mask = (
        invoice_report["Classification"].eq("ACTION REQUIRED")
    )

    invoice_report.loc[
        invoice_action_mask,
        "Severity",
    ] = "HIGH"

    consolidated = pd.concat(
        [
            payment_report,
            invoice_report,
        ],
        ignore_index=True,
    )

    return consolidated[REPORT_COLUMNS]




    

