"""Run the end-to-end energy trade settlement control workflow."""

import argparse
from pathlib import Path

import pandas as pd

from src.controls.invoice_exception_classification import (
    classify_invoice_balance_exceptions,
)
from src.controls.invoice_reconciliation import (
    reconcile_invoice_allocations,
)
from src.controls.payment_reconciliation import (
    reconcile_payment_allocations,
)
from src.controls.settlement_case_linkage import (
    assign_settlement_cases,
)
from src.ingestion.workbook_reader import read_excel_table
from src.reporting.exception_report import (
    build_consolidated_exception_report,
)
from src.reporting.excel_formatter import (
    format_control_report,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_INPUT_PATH = (
    PROJECT_ROOT
    /"data"
    /"input"
    /"portfolio.xlsx"
)

DEFAULT_OUTPUT_PATH = (
    PROJECT_ROOT
    /"data"
    /"output"
   /"settlement_exceptions.xlsx"
)


def run_controls(
        workbook_path: str | Path  = DEFAULT_INPUT_PATH,
        output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> tuple[dict[str, int | str], pd.DataFrame]:
    """Run settlement controls and write the exception report.
    
    Args:
        workbook_path: Source workbook containing governed Excel tables.
        output_path: Destination for the generated exception workbook.
        
    Returns:
        A tuple containing the run summary and linked exception report.
    """
    workbook_path = Path(workbook_path)
    output_path = Path(output_path)

    payments = read_excel_table(
        workbook_path,
        "tblPayments",
    )

    allocations = read_excel_table(
        workbook_path,
        "tblPaymentAllocations",
    )

    invoices = read_excel_table(
        workbook_path,
        "tblInvoices",
    )

    payment_reconciliation = reconcile_payment_allocations(
        payments,
        allocations,
    )

    invoice_reconciliation = reconcile_invoice_allocations(
        invoices,
        allocations,
    )

    invoice_classification = classify_invoice_balance_exceptions(
        invoice_reconciliation,
        invoices,
    )

    exception_report = build_consolidated_exception_report(
        payment_reconciliation,
        invoice_classification,
    )

    linked_report = assign_settlement_cases(
        exception_report,
        allocations,
    )

    action_required_cases = linked_report.loc[
        linked_report["Classification"].eq("ACTION REQUIRED"),
        "Settlement Case ID",
    ].nunique()

    controlled_exclusion_cases = linked_report.loc[
        linked_report["Classification"].eq(
            "CONTROLLED EXCLUSION"
        ),
        "Settlement Case ID",
    ].nunique()

    overall_status = (
        "REVIEW"
        if action_required_cases > 0
        else "PASS"
    )

    summary: dict[str, int | str] = {
        "Overall Status": overall_status,
        "Payments Tested": len(payments),
        "Invoices Tested": len(invoices),
        "Control Observations": len(linked_report),
        "Settlement Cases": (
            linked_report["Settlement Case ID"].nunique()
        ),
        "Action-Required Cases": action_required_cases,
        "Controlled-Exclusion Cases": controlled_exclusion_cases,
    }

    summary_dataframe = pd.DataFrame(
        {
            "Metric": list(summary.keys()),
            "Value": list(summary.values()),
        }
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        output_path,
        engine="openpyxl",
    ) as writer:
        summary_dataframe.to_excel(
            writer,
            sheet_name="Run Summary",
            index=False,
        )

        linked_report.to_excel(
            writer,
            sheet_name="Settlement Exceptions",
            index=False,
        )

    format_control_report(output_path)

    return summary, linked_report


def main() -> None:
    """Parse command-line arguments and run the controls."""
    parser = argparse.ArgumentParser(
        description=(
            "Run energy-trade settlement controls and generate "
            "an Excel exception report."
        )   
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help=(
            "Path to the source workbook. "
            "Defaults to data/input/portfolio.xlsx."
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help=(
            "Path for the generated exception report. "
            "Defaults to data/output/settlement_exceptions.xlsx."
        ),
    )

    args = parser.parse_args()

    summary, _ = run_controls(
        workbook_path=args.input,
        output_path=args.output,
    )

    print()
    print("Energy Trade Controls Run")
    print("-------------------------")
    print(
        f"Payments tested:                 "
        f"{summary['Payments Tested']}"
    )
    print(
        f"Invoices tested:                 "
        f"{summary['Invoices Tested']}"
    )
    print(
        f"Control observations:            "
        f"{summary['Control Observations']}"
    )
    print(
        f"Settlement cases:                "
        f"{summary['Settlement Cases']}"
    )
    print(
        f"Action-required cases:           "
        f"{summary['Action-Required Cases']}"
    )
    print(
        f"Controlled-exclusion cases:      "
        f"{summary['Controlled-Exclusion Cases']}"
    )
    print()
    print(
        f"Overall status: "
        f"{summary['Overall Status']}"
    )
    print()
    print("Report written to:")
    print(args.output.resolve())


if __name__ == "__main__":
    main()

