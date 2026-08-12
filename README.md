# Energy Trade Controls

A Python-based settlement-control framework for a fictional physical-energy trading portfolio.

The project ingests governed Excel data, independently reconciles payments and invoices, identifies settlement exceptions, distinguishes active issues from controlled exclusions, links related control observations into settlement cases, and produces a formatted Excel exception report.

A fully synthetic demo workbook is included so the workflow can be reproduced without access to the larger portfolio workbook.

---

## Business problem

Physical commodity settlement data rarely behaves like a simple one-invoice / one-payment process.

Operational scenarios can include:

- one payment allocated across multiple invoices;
- multiple payments applied to one invoice;
- partial cash receipts;
- unapplied cash;
- open invoice balances;
- overallocations;
- cancelled or rejected invoices;
- reported balances that disagree with independently calculated balances;
- multiple control observations relating to the same underlying settlement issue.

A useful settlement-control process therefore needs to answer two separate questions.

### Payment-side question

For each payment:

> Has the full payment amount been allocated to invoices, or is cash still unallocated or overallocated?

### Invoice-side question

For each invoice:

> Do recorded payment allocations support the invoice's reported outstanding balance?

The framework calculates those questions independently before applying operational classification.

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
        |                    Balance Classification
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

That distinction is important: two observations having the same dollar amount may be a useful clue, but it is not authoritative evidence that they belong to the same settlement event.

---

## Key controls

### 1. Payment allocation reconciliation

Each payment is independently reconciled to the total amount allocated across invoices.

```text
Payment Amount - Allocated Amount = Unallocated Amount
```

Control status:

```text
Within ±$0.01 tolerance      -> PASS
Positive residual            -> REVIEW
Negative residual            -> FAIL
```

A positive residual represents cash that has not yet been fully allocated.

A negative residual represents allocations exceeding the recorded payment amount.

The calculation does not rely on workbook-level summary fields.

---

### 2. Invoice allocation reconciliation

Each invoice is independently reconciled to payment-allocation records.

```text
Invoice Total - Allocated Amount = Calculated Outstanding Amount
```

The independently calculated balance is then compared with the balance reported in the invoice data.

```text
Calculated Outstanding Amount
-
Reported Outstanding Amount
=
Outstanding Variance
```

Settlement status:

```text
Within tolerance             -> PASS
Positive outstanding amount  -> REVIEW
Negative outstanding amount  -> FAIL
```

Reported-balance status:

```text
Variance within ±$0.01       -> PASS
Variance outside tolerance   -> REVIEW
```

This separates two questions:

1. Has the invoice actually been settled?
2. Does the reported balance agree with the transaction-level allocation evidence?

---

### 3. Invoice exception classification

Reconciliation mathematics and operational interpretation are deliberately kept separate.

The framework first calculates the variance and only then considers invoice status.

Examples:

```text
Active balance mismatch
    -> ACTION REQUIRED

Cancelled invoice with retained variance
    -> CONTROLLED EXCLUSION

No balance mismatch
    -> CLEAR
```

Cancelled records remain visible rather than being filtered out before reconciliation.

This preserves the audit trail while distinguishing genuine active exposure from intentionally retained historical records.

---

### 4. Consolidated exception reporting

Payment-side and invoice-side exceptions are normalized into a common report structure.

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

Examples of exception types include:

```text
UNALLOCATED PAYMENT
OVERALLOCATED PAYMENT
BALANCE MISMATCH
```

The consolidated report intentionally distinguishes a **control observation** from an underlying economic issue.

A payment exception and an invoice exception can describe two sides of the same settlement problem.

---

### 5. Settlement case linkage

Related exception observations are grouped into settlement cases using the payment-allocation ledger.

For example:

```text
PAYMENT PAY-xxxx
        |
        | Payment Allocation Record
        |
        v
INVOICE INV-xxxx
```

The linkage logic models exception observations as connected records.

This supports:

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

This prevents amount matching from being used as a substitute for transactional evidence.

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

The generator writes a disposable workbook to:

```text
data/output/generated_demo_portfolio.xlsx
```

Run the settlement controls:

```powershell
python -m src.main `
    --input data/output/generated_demo_portfolio.xlsx `
    --output data/output/demo_settlement_exceptions.xlsx
```

The repository also includes:

```text
data/demo/demo_portfolio.xlsx
```

as a committed reference copy.

The generator writes a separate workbook under `data/output/` so running the documented demo workflow does not modify tracked files.

---

## Expected demo result

The synthetic demo is designed to exercise both clean and exception scenarios.

A successful run produces approximately:

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

`REVIEW` does **not** mean the Python application failed.

It means:

```text
Technical execution: SUCCESS
Control result:       REVIEW
```

The application completed successfully and identified settlement conditions requiring operational attention.

---

## Generated Excel report

The control runner produces a formatted Excel workbook containing two worksheets.

### Run Summary

Provides high-level execution and control metrics including:

```text
Overall Status
Payments Tested
Invoices Tested
Control Observations
Settlement Cases
Action-Required Cases
Controlled-Exclusion Cases
```

The worksheet includes generated presentation formatting such as:

- formatted headers;
- frozen panes;
- readable column widths;
- visual status highlighting.

### Settlement Exceptions

Provides record-level settlement observations including:

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

The generated worksheet includes:

- Excel table filters;
- frozen headers;
- currency formatting;
- readable column widths;
- severity highlighting;
- action-required versus controlled-exclusion highlighting.

Formatting is applied only after the control calculations have completed.

The presentation layer does not change reconciliation values, statuses, classifications, or settlement-case relationships.

---

## Synthetic demo scenarios

The generated demo contains deliberately designed settlement conditions.

| Scenario | Purpose |
|---|---|
| Fully settled payment and invoice | Demonstrates a clean PASS result |
| Partially allocated payment | Demonstrates unallocated cash |
| Invoice with incorrectly reported zero balance | Demonstrates a reported-balance mismatch |
| Overallocated payment | Demonstrates allocations exceeding cash received |
| Cancelled invoice with retained discrepancy | Demonstrates a controlled exclusion |
| Legitimate open invoice with correctly reported balance | Demonstrates that an open invoice is not automatically an exception |

The purpose of the demo is not to mimic production transaction volume.

It is to provide a small, understandable dataset that exercises the major control paths.

---

## Testing

The project currently contains **71 automated pytest tests**.

The test suite covers:

```text
Workbook sheet discovery
Structured Excel table discovery
Required sheet validation
Required table validation
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
End-to-end control orchestration
Generated Excel output
```

Run the complete suite with:

```powershell
python -m pytest -q
```

Expected result:

```text
71 passed
```

Tests use synthetic DataFrames and disposable temporary workbooks so the source portfolio workbook is not modified.

---

## Clean-clone validation

The project has also been tested from a fresh Git clone and a newly created Python virtual environment.

The validation process included:

```text
Fresh repository clone
Fresh virtual environment
Dependency installation from requirements.txt
71-test regression suite
Synthetic workbook regeneration
End-to-end application execution
Formatted Excel report generation
```

This verifies that the committed repository is sufficient to reproduce the public demo workflow without relying on the development environment or the larger portfolio workbook.

---

## Project structure

```text
energy-trade-controls/
|
├── config/
|
├── data/
│   ├── demo/
│   │   └── demo_portfolio.xlsx
│   ├── input/
│   └── output/
|
├── docs/
|
├── logs/
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
│   ├── utils/
│   │
│   ├── validation/
│   │   ├── data_contract.py
│   │   └── workbook_structure.py
│   │
│   └── main.py
|
├── tests/
|
├── .gitignore
├── README.md
└── requirements.txt
```

---

## Excel ingestion design

The ingestion layer reads genuine Excel structured tables rather than relying on fixed cell ranges.

Examples include:

```text
tblPayments
tblPaymentAllocations
tblInvoices
```

Structured-table ingestion provides a stronger contract than hard-coded worksheet coordinates because table names represent governed business objects.

The reader:

1. validates that the workbook exists;
2. locates the requested structured table;
3. reads the table's defined Excel range;
4. uses the first row as column headers;
5. returns the table as a pandas DataFrame;
6. closes the workbook without saving it.

Financial values are read using Excel's saved calculation results where appropriate.

The production ingestion functions do not save the source workbook.

---

## Workbook governance controls

The project also contains reusable structural-validation functions.

These include checks for:

```text
Required worksheets
Required Excel tables
Expected table-to-sheet locations
Required DataFrame columns
Primary-key blanks
Primary-key duplicates
Foreign-key orphans
```

The validation functions are intentionally separated from business reconciliation controls.

Structural integrity answers:

> Is the dataset shaped correctly enough to process?

Settlement reconciliation answers:

> Do the financial relationships reconcile?

Those are related but distinct control questions.

---

## Source workbook immutability

The Python controls treat source workbooks as read-only inputs.

Production ingestion functions never save the input workbook.

Generated reports are written separately under:

```text
data/output/
```

This distinction is deliberate.

The source workbook is evidence.

The generated output workbook is a reporting artifact and can safely be formatted and saved by Python.

---

## Full portfolio workbook

The public synthetic demo is intentionally small.

The broader project was developed alongside a substantially larger fictional workbook:

```text
Houston Energy Trade Operations and Demurrage Portfolio
Version 23
```

That workbook contains a wider operational model covering areas such as:

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

The public Python repository uses independently generated synthetic data so the application can be cloned, tested, and reviewed without requiring that workbook.

---

## Design principles

### 1. Calculate first, interpret second

Financial relationships are reconciled before operational statuses are used to classify the resulting exception.

This prevents status fields from hiding mathematical discrepancies.

### 2. Preserve exceptions rather than hiding them

Cancelled or excluded records remain visible when they contain a reconciliation variance.

Their classification changes, but the underlying control evidence remains available.

### 3. Use transactional relationships instead of inference

Settlement cases are linked through actual payment-allocation records.

Matching dollar amounts alone are not treated as sufficient evidence of a relationship.

### 4. Separate control observations from economic cases

A payment exception and an invoice exception may describe two sides of one settlement event.

The report preserves both observations while settlement-case linkage groups the related records.

### 5. Keep source workbooks immutable

The application reads source workbooks without saving them.

Generated outputs are written to separate locations.

### 6. Test controls independently before orchestration

Core reconciliation, validation, classification, linkage, and reporting functions are tested individually before being combined in the end-to-end runner.

### 7. Separate presentation from control logic

Excel formatting is applied downstream from the reconciliation process.

Formatting may change presentation properties such as fills, widths, number formats, filters, or freeze panes, but it does not alter business-control values.

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

`pandas` is used primarily for tabular transformation, reconciliation, grouping, and joining.

`openpyxl` is used where workbook-level Excel features are required, including:

```text
Structured Excel table discovery
Structured table creation
Workbook formatting
Freeze panes
Column widths
Excel table styles
```

---

## Development approach

The project was developed control by control rather than as one large script.

The general implementation sequence was:

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

This made it possible to validate both the financial reasoning and the software behavior independently.

---

## Example debugging lessons

Several implementation issues were deliberately resolved through tests rather than hidden.

Examples included:

```text
Incorrect Excel table name
Incorrect pandas column name
Cell objects accidentally used instead of cell values
Capitalization / spelling mismatches in status columns
Graph traversal state placed at the wrong indentation level
Attempting to reopen an Excel file before ExcelWriter had closed it
```

These failures helped reinforce the role of:

```text
Exact data contracts
Scope and indentation
File lifecycle management
Focused unit tests
Diagnostic inspection before changing algorithms
```

---

## Current scope

The implemented application currently focuses on settlement-control logic around:

```text
Payments
Payment allocations
Invoices
Reported invoice balances
Exception classification
Settlement case linkage
Excel exception reporting
```

The repository should therefore be viewed as a focused settlement-control application rather than a complete commodity trading platform.

---

## Potential future enhancements

Possible extensions include:

```text
Integrating additional foreign-key validation into the main runtime pipeline
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

This project is intended to demonstrate the combination of:

```text
Physical-energy trade operations knowledge
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