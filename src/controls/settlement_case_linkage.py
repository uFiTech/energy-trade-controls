"""Link related settlement exceptions into economic settlement case."""

import pandas as pd


def assign_settlement_cases(
        exception_report: pd.DataFrame,
        payment_allocations: pd.DataFrame,
) -> pd.DataFrame:
    """Assign related payment and invoice exceptions to settlement cases.

    Payment and invoice exceptions are linked only through actual
    payment-allocation records. Exception amounts are not used to infer
    relationships.

    Args:
        exception_report: Consolidated payment and invoice exception report.
        payment_allocations: Allocation records containing Payment ID and
            Invoice ID.

    Returns:
        The exception report with Settlement Case ID, Related Records,
        and Link Basis added.

    Raises:
        KeyError: If required columns are missing.
    """
    required_report_columns = {
        "Control Area",
        "Record ID",
    }

    required_allocation_columns = {
        "Payment ID",
        "Invoice ID",
    }

    missing_report_columns = (
        required_report_columns - set(exception_report.columns)
    )

    if missing_report_columns:
        raise KeyError(
            "Missing exception report columns: "
            f"{sorted(missing_report_columns)}"
        )

    missing_allocation_columns = (
        required_allocation_columns - set(payment_allocations.columns)
    )

    if missing_allocation_columns:
        raise KeyError(
            "Missing payment allocation columns: "
            f"{sorted(missing_allocation_columns)}"
        )

    result = exception_report.copy()

    nodes = [
        (row["Control Area"], row["Record ID"])
        for _, row in result.iterrows()
    ]

    adjacency: dict[tuple[str, str], set[tuple[str, str]]] = {
        node: set()
        for node in nodes
    }

    payment_nodes = {
        record_id: ("PAYMENT", record_id)
        for control_area, record_id in nodes
        if control_area == "PAYMENT"
    }

    invoice_nodes = {
        record_id: ("INVOICE", record_id)
        for control_area, record_id in nodes
        if control_area == "INVOICE"
    }

    for _, allocation in payment_allocations.iterrows():
        payment_id = allocation["Payment ID"]
        invoice_id = allocation["Invoice ID"]

        if (
            payment_id in payment_nodes
            and invoice_id in invoice_nodes
        ):
            payment_node = payment_nodes[payment_id]
            invoice_node = invoice_nodes[invoice_id]

            adjacency[payment_node].add(invoice_node)
            adjacency[invoice_node].add(payment_node)

    visited: set[tuple[str, str]] = set()
    case_members: dict[tuple[str, str], list[tuple[str, str]]] ={}
    case_number = 1

    for node in nodes:
        if node in visited:
            continue

        stack = [node]
        members: list[tuple[str, str]] = []

        while stack:
            current = stack.pop()

            if current in visited:
                continue

            visited.add(current)
            members.append(current)

            stack.extend(adjacency[current] - visited)

        case_id = f"CASE-{case_number:03d}"

        for member in members:
            case_members[member] = members

        for member in members:
            case_members[member] = members + [(case_id, "")]

        case_number += 1

    settlement_case_ids = []
    related_records = []
    link_bases = []

    for node in nodes:
        member_with_case = case_members[node]
        case_id = member_with_case[-1][0]
        members = member_with_case[:-1]

        related = [
            record_id
            for member_area, record_id in members
            if (member_area, record_id) != node
        ]

        settlement_case_ids.append(case_id)
        related_records.append(", ".join(related))

        if related:
            link_bases.append("PAYMENT ALLOCATION RECORD")
        else:
            link_bases.append("NO DIRECT EXCEPTION LINK")

    result["Settlement Case ID"] = settlement_case_ids
    result["Related Records"] = related_records
    result["Link Basis"] = link_bases

    return result
