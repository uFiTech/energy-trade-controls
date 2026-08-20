# Energy Trade Controls

A Python-based settlement-control framework for a fictional physical-energy trading portfolio.

The project ingests governed Excel data, reconciles payments and invoices, identifies settlement exceptions, distinguishes active issues from controlled exclusions, links related observations into settlement cases, and produces a formatted Excel exception report.

A fully synthetic demo is included so the workflow can be cloned, tested, and run without access to the larger portfolio workbook.

## Contents

- [Business problem](#business-problem)
- [Control workflow](#control-workflow)
- [Key controls](#key-controls)
  - [Payment allocation reconciliation](#1-payment-allocation-reconciliation)
  - [Invoice allocation reconciliation](#2-invoice-allocation-reconciliation)
  - [Invoice exception classification](#3-invoice-exception-classification)
  - [Consolidated exception reporting](#4-consolidated-exception-reporting)
  - [Settlement case linkage](#5-settlement-case-linkage)
- [Quick-start demo](#quick-start-demo)
- [Expected demo result](#expected-demo-result)
- [Generated Excel report](#generated-excel-report)
- [Synthetic demo scenarios](#synthetic-demo-scenarios)
- [Testing](#testing)
- [Project structure](#project-structure)
- [Technical design](#technical-design)
- [Design principles](#design-principles)
- [Full portfolio context](#full-portfolio-context)
- [Technology](#technology)
- [Development approach](#development-approach)
- [Current scope](#current-scope)
- [Potential future enhancements](#potential-future-enhancements)
- [Portfolio objective](#portfolio-objective)

---

## Business problem

Physical commodity settlements rarely behave like a simple one-invoice / one-payment process.

Operational scenarios can include:

- one payment allocated across multiple invoices;
- multiple payments applied to one invoice;
- partial cash receipts;
- unapplied cash;
- open invoice balances;
- overallocations;
- cancelled or rejected invoices;
- reported balances that disagree with an independently re-performed transaction-level calculation;
- multiple control observations relating to the same economic issue.

The framework therefore answers two distinct control questions.

### Payment side

> Has the full payment amount been allocated to invoices, or is cash still unallocated or overallocated?

### Invoice side

> Do recorded payment allocations support the invoice's reported outstanding balance?

The calculations are performed before operational statuses are used to interpret the result.

---

## Control workflow

```text
Structured Excel Tables
        |
        v
Workbook Ingestion
        |
        v
Structural / Data Validation
        |
        +-----------------------------+
        |                             |
        v                             v
Payment Reconciliation        Invoice Reconciliation
        |                             |
        |                             v
        |                   Exception Classification
        |                             |
        +--------------+--------------+
                       |
                       v
              Consolidated Exceptions
                       |
                       v
              Settlement Case Linkage
                       |
                       v
               Formatted Excel Report
```

Settlement cases are linked using actual payment-allocation records rather than matching exception amounts.

Matching amounts may be a useful clue, but they are not treated as authoritative evidence of a relationship.

---

## Key controls

### 1. Payment allocation reconciliation

Each payment is reconciled to the total amount allocated across invoices.

```text
Payment Amount - Allocated Amount = Unallocated Amount
```

Status logic:

```text
Within +/- $0.01 tolerance  -> PASS
Positive residual           -> REVIEW
Negative residual           -> FAIL
```

A positive residual represents cash that has not yet been fully allocated.

A negative residual represents invoice allocations exceeding the recorded payment amount.

---

### 2. Invoice allocation reconciliation

For each invoice, the application re-performs expected outstanding balance from Invoice Total and Payment Allocation detail, then compares that result with the source-system reported balance.

```text
Invoice Total - Allocated Amount = Calculated Outstanding Amount
```

The calculated balance is then compared with the balance reported in the invoice data.

```text
Calculated Outstanding Amount
-
Reported Outstanding Amount
=
Outstanding Variance
```

Settlement position:

```text
Within +/- $0.01             -> SETTLED
Positive outstanding amount  -> OPEN BALANCE
Negative outstanding amount  -> OVERPAID
```

Balance reconciliation status:

```text
Variance within +/- $0.01   -> PASS
Variance outside tolerance  -> REVIEW
```

This separates two different questions:

1. Settlement Position asks what the invoice's economic balance is:
   settled, still open, or overpaid.

2. Balance Reconciliation Status asks whether the source-system
   reported balance agrees with the balance independently re-performed
   from Invoice Total and Payment Allocation detail.

Reported Outstanding Amount is the source-system reported balance snapshot.

Calculated Outstanding Amount is independently re-performed from Invoice Total and payment-allocation detail.

This provides an independent re-performance of the balance calculation. Full data-source independence depends on the architecture of the originating systems.

---

### 3. Invoice exception classification

Reconciliation mathematics and operational interpretation are deliberately separated.

```text
Active balance mismatch
    -> ACTION REQUIRED

Cancelled invoice with retained variance
    -> CONTROLLED EXCLUSION

No balance mismatch
    -> CLEAR
```

Cancelled records remain visible rather than being filtered out before reconciliation.

This preserves the control evidence while distinguishing active settlement exposure from intentionally retained historical records.

---

### 4. Consolidated exception reporting

Payment-side and invoice-side findings are normalized into a common exception structure.

Core fields include:

```text
Control Area
Record ID
Exception Type
Exception Amount
Source Status
Severity
Classification
```

Examples include:

```text
UNALLOCATED PAYMENT
OVERALLOCATED PAYMENT
BALANCE MISMATCH
```

A control observation is not automatically the same thing as an economic issue.

For example, a payment exception and an invoice exception may represent two sides of the same settlement problem.

---

### 5. Settlement case linkage

Related observations are grouped into settlement cases using the payment-allocation ledger.

```text
PAYMENT PAY-xxxx
        |
        | Payment Allocation Record
        |
        v
INVOICE INV-xxxx
```

The linkage supports:

```text
one payment -> one invoice

one payment -> many invoices

many payments -> one invoice

connected settlement chains
```

Each linked observation receives:

```text
Settlement Case ID
Related Records
Link Basis
```

Records without a direct exception-to-exception allocation relationship remain visible as standalone cases.

---

## Quick-start demo

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

Generate the synthetic demo workbook:

```powershell
python scripts/generate_demo_workbook.py
```

The generator writes:

```text
data/output/generated_demo_portfolio.xlsx
```

Run the controls:

```powershell
python -m src.main `
    --input data/output/generated_demo_portfolio.xlsx `
    --output data/output/demo_settlement_exceptions.xlsx
```

The repository also includes a committed reference workbook:

```text
data/demo/demo_portfolio.xlsx
```

The generator writes a separate disposable copy under `data/output/`, so running the documented workflow does not modify tracked files.

---

## Expected demo result

A successful demo run produces:

```text
Energy Trade Controls Run
-------------------------
Payments tested:                 3
Invoices tested:                 5
Control observations:            5
Settlement cases:                3
Action-required cases:           2
Controlled-exclusion cases:      1
Overall status: REVIEW
```

`REVIEW` does not mean the application failed.

It means:

```text
Technical execution: SUCCESS
Control result:       REVIEW
```

The application completed successfully and identified settlement conditions requiring operational attention.

---

## Generated Excel report

The runner produces a formatted Excel workbook with two worksheets.

### Run Summary

Includes:

```text
Overall Status
Payments Tested
Invoices Tested
Control Observations
Settlement Cases
Action-Required Cases
Controlled-Exclusion Cases
```

Presentation features include:

- formatted headers;
- frozen panes;
- readable column widths;
- status highlighting.

### Settlement Exceptions

Includes:

```text
Control Area
Record ID
Exception Type
Exception Amount
Source Status
Severity
Classification
Settlement Case ID
Related Records
Link Basis
```

Presentation features include:

- Excel table filters;
- frozen headers;
- currency formatting;
- readable column widths;
- severity highlighting;
- action-required and controlled-exclusion highlighting.

Formatting is applied only after control calculations have completed.

The presentation layer does not alter reconciliation values, statuses, classifications, or settlement-case relationships.

---

## Synthetic demo scenarios

| Scenario | Purpose |
| --- | --- |
| Fully settled payment and invoice | Clean PASS result |
| Partially allocated payment | Demonstrates unallocated cash |
| Incorrectly reported zero invoice balance | Demonstrates a balance mismatch |
| Overallocated payment | Demonstrates allocations exceeding the recorded payment amount |
| Cancelled invoice with retained discrepancy | Demonstrates a controlled exclusion |
| Legitimate open invoice with correct balance | Shows that an open invoice is not automatically an exception |

The demo is intentionally small so each control path can be understood quickly.

---

## Testing

The project contains **71 automated pytest tests**.

Coverage includes:

```text
Workbook sheet discovery
Structured Excel table discovery
Required sheet and table validation
Expected table locations
Structured table DataFrame ingestion
Required-column validation
Primary-key validation
Foreign-key validation
Payment allocation reconciliation
Invoice allocation reconciliation
Invoice exception classification
Consolidated exception reporting
Settlement case linkage
Excel report formatting
Empty-exception reporting
End-to-end orchestration
Generated Excel output
```

Run the suite with:

```powershell
python -m pytest -q
```

Expected result:

```text
71 passed
```

Tests use synthetic DataFrames and disposable temporary workbooks so source workbooks are not modified.

The repository has also passed a clean-clone validation using a fresh Git clone, new virtual environment, dependency installation from `requirements.txt`, the full regression suite, synthetic workbook generation, end-to-end execution, and formatted report generation.

---

## Project structure

```text
energy-trade-controls/
|
├── data/
│   ├── demo/
│   │   └── demo_portfolio.xlsx
│   ├── input/
│   └── output/
|
├── scripts/
│   └── generate_demo_workbook.py
|
├── src/
│   ├── controls/
│   │   ├── invoice_exception_classification.py
│   │   ├── invoice_reconciliation.py
│   │   ├── payment_reconciliation.py
│   │   └── settlement_case_linkage.py
│   │
│   ├── ingestion/
│   │   └── workbook_reader.py
│   │
│   ├── reporting/
│   │   ├── excel_formatter.py
│   │   └── exception_report.py
│   │
│   ├── validation/
│   │   ├── data_contract.py
│   │   └── workbook_structure.py
│   │
│   └── main.py
|
├── tests/
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Technical design

### Structured Excel ingestion

The ingestion layer reads genuine Excel structured tables rather than relying on fixed cell ranges.

Examples include:

```text
tblPayments
tblPaymentAllocations
tblInvoices
```

The reader validates the workbook and requested table, reads the table's defined range, returns a pandas DataFrame, and closes the workbook without saving it.

The ingestion functions treat source workbooks as read-only inputs.

### Workbook governance

Reusable validation controls cover:

```text
Required worksheets
Required Excel tables
Expected table-to-sheet locations
Required DataFrame columns
Primary-key blanks and duplicates
Foreign-key orphans
```

Structural integrity and financial reconciliation are intentionally separate concerns.

### Source immutability

Input workbooks are not saved by the ingestion layer.

Generated reports are written separately under:

```text
data/output/
```

The source workbook is treated as evidence; the generated workbook is a reporting artifact.

### Presentation separation

The Excel formatter runs downstream from the control calculations.

It may change presentation properties such as fills, column widths, number formats, filters, and freeze panes, but it does not change business-control values.

---

## Design principles

1. **Calculate first, interpret second**

   Reconciliation mathematics are performed before operational status is used for classification.

2. **Preserve exceptions rather than hiding them**

   Cancelled or excluded records remain visible when they contain a variance.

3. **Use transactional relationships instead of inference**

   Settlement cases are linked using payment-allocation records rather than amount matching.

4. **Separate observations from economic cases**

   Multiple control findings can belong to one underlying settlement issue.

5. **Keep source workbooks immutable**

   Inputs are read without being rewritten.

6. **Test controls independently before orchestration**

   Reconciliation, validation, classification, linkage, and reporting functions are tested individually before being combined.

7. **Separate presentation from control logic**

   Workbook formatting occurs only after control results have been produced.

---

## Full portfolio context

The public synthetic demo is intentionally small.

The broader project was developed alongside a larger fictional workbook:

```text
Houston Energy Trade Operations and Demurrage Portfolio
Version 25
```

That workbook contains a wider operational model covering areas including:

```text
Trades
Movements
Invoices
Payments
Invoice Charges
Service Commitments
Invoice-Service Allocations
Payment Allocations
Claim Allocations
Change Control
Exception Register
Baseline Reconciliation
Regression Tests
```

The larger workbook is maintained separately for portfolio and interview walkthrough purposes.

The public Python repository uses separately generated synthetic data so it can be reviewed and reproduced without requiring that workbook.

---

## Technology

The project uses:

```text
Python 3.13
pandas
openpyxl
pytest
PyYAML
Git
```

`pandas` handles tabular transformation, grouping, joining, and reconciliation.

`openpyxl` handles workbook-level Excel features such as structured tables, formatting, freeze panes, and column widths.

---

## Development approach

The project was developed control by control:

```text
Business rule
    ->
Pseudocode
    ->
Python implementation
    ->
Unit tests
    ->
Debugging
    ->
Workbook integration
    ->
End-to-end orchestration
```

Testing exposed and helped resolve issues involving exact table and column names, Excel cell-value handling, status spelling, graph traversal scope, and Excel file lifecycle management.

---

## Current scope

The implemented Python application focuses on:

```text
Payments
Payment allocations
Invoices
Reported invoice balances
Exception classification
Settlement case linkage
Excel exception reporting
```

It should therefore be viewed as a focused settlement-control application rather than a complete commodity trading platform.

---

## Potential future enhancements

Possible extensions include:

```text
Additional foreign-key validation in the main runtime pipeline
Trade-to-movement reconciliation
Service commitment and accrual controls
Demurrage and claims controls
Configuration-driven tolerances and business rules
Exception aging and ownership
Structured application logging
Historical exception trend reporting
Dashboard or visualization layers
```

These are future enhancements and are not represented as currently implemented functionality.

---

## Portfolio objective

This project demonstrates the combination of:

```text
Physical-energy trade operations concepts
Settlement and reconciliation reasoning
Control design
Excel data governance
Python automation
Testing discipline
Exception management
Auditability
Operational reporting
```

The objective is not simply to automate spreadsheet calculations.

It is to show how operational settlement questions can be translated into explicit business rules, independently tested controls, and reproducible reporting.