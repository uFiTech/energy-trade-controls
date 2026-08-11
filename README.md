# Energy Trade Controls

A Python-based settlement-control framework for a fictional physical-energy trading portfolio.

The project ingests governed Excel tables, independently reconciles payments and invoices, identifies settlement exceptions, distinguishes active issues from controlled exclusions, links related payment and invoice findings into settlement cases, and produces an auditable Excel exception report.

The repository includes a fully synthetic demo workbook so the workflow can be reproduced without access to the larger portfolio workbook.

## Business problem

Physical-energy settlements can involve:

- one payment applied to multiple invoices;
- multiple payments applied to one invoice;
- partially allocated cash;
- open invoice balances;
- overallocations;
- cancelled or rejected records;
- differences between detailed settlement activity and reported balances.

A control process therefore needs to answer two different questions:

**Payment side**

> Has all cash associated with a payment been allocated?

**Invoice side**

> Has the invoice been fully settled, and does the reported outstanding balance agree with the detailed payment allocations?

The project evaluates both sides independently and then links related findings through actual payment-allocation records.

## Control workflow

```text
Excel tables
    |
    v
Payment reconciliation
    |
    +----> Unallocated / overallocated payment exceptions
    |
    v
Invoice reconciliation
    |
    +----> Calculated vs reported outstanding balances
    |
    v
Invoice exception classification
    |
    +----> Active exposure / controlled exclusion
    |
    v
Consolidated exception report
    |
    v
Settlement-case linkage
    |
    v
Management-facing Excel report
```

The linkage layer uses the payment-allocation table as the authoritative relationship between payments and invoices. Matching exception amounts alone are not treated as sufficient evidence that two findings belong to the same settlement situation.

## Key controls

### Payment allocation reconciliation

For each payment:

```text
Payment Amount
- Total Applied Amount
= Unallocated Amount
```

Results are classified as:

- `PASS` — difference is within tolerance;
- `REVIEW` — cash remains unallocated;
- `FAIL` — allocations exceed the payment amount.

### Invoice allocation reconciliation

For each invoice:

```text
Invoice Total
- Total Applied Amount
= Calculated Outstanding Amount
```

The calculated result is also compared with the workbook's reported `Outstanding Amount`.

This separates two questions:

- Is the invoice fully settled?
- Is the reported outstanding balance correct?

### Exception classification

Mathematical discrepancies are calculated first and business interpretation is applied afterward.

For example, a cancelled invoice remains visible in the reconciliation evidence but can be classified as:

```text
Settlement Scope: OUT OF SCOPE
Exception Classification: CONTROLLED EXCLUSION
```

This preserves the audit trail instead of deleting the record.

### Settlement-case linkage

Payment and invoice exceptions connected through payment-allocation records are grouped into the same settlement case.

This distinguishes:

```text
Control observations
```

from:

```text
Underlying settlement cases
```

and prevents management reporting from treating two views of the same economic situation as independent exposure.

## Quick-start demo

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

Generate the synthetic demo workbook:

```powershell
python scripts/generate_demo_workbook.py
```

Run the settlement controls:

```powershell
python -m src.main --input data/demo/demo_portfolio.xlsx
```

A custom output location can also be supplied:

```powershell
python -m src.main `
    --input data/demo/demo_portfolio.xlsx `
    --output data/output/demo_settlement_exceptions.xlsx
```

## Expected demo result

The synthetic dataset deliberately contains clean settlements, partial allocations, an overallocation, a cancelled record, and a legitimately open invoice.

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

`REVIEW` does not mean the Python application failed. It means the control process executed successfully and identified settlement situations requiring human investigation.

The generated Excel workbook contains:

```text
Run Summary
Settlement Exceptions
```

## Synthetic demo scenarios

The public demo deliberately exercises several control outcomes:

| Scenario | Expected control behavior |
|---|---|
| Clean payment and invoice | PASS |
| Partial allocation | ACTION REQUIRED |
| Overallocated payment | FAIL / ACTION REQUIRED |
| Cancelled invoice | CONTROLLED EXCLUSION |
| Legitimately open invoice with correct balance | No balance exception |

All demo records are synthetic and are generated programmatically by:

```text
scripts/generate_demo_workbook.py
```

## Testing

The project currently contains **67 automated pytest tests** covering:

- workbook sheet discovery;
- structured Excel table discovery;
- table location validation;
- table ingestion into pandas DataFrames;
- required-column validation;
- primary-key validation;
- foreign-key integrity;
- payment reconciliation;
- invoice reconciliation;
- invoice exception classification;
- consolidated exception reporting;
- one-to-one, one-to-many, and many-to-one settlement linkage;
- end-to-end orchestration and Excel report generation.

Run the full regression suite with:

```powershell
python -m pytest -v
```

## Project structure

```text
energy-trade-controls/
|
|-- data/
|   |-- demo/          Synthetic public demo workbook
|   |-- input/         Private source workbooks, excluded from Git
|   `-- output/        Generated reports, excluded from Git
|
|-- scripts/
|   `-- generate_demo_workbook.py
|
|-- src/
|   |-- controls/      Reconciliation and classification controls
|   |-- ingestion/     Excel workbook and table ingestion
|   |-- reporting/     Exception-report construction
|   |-- validation/    Data-contract and structural validation
|   `-- main.py        End-to-end application runner
|
|-- tests/             Automated pytest coverage
|-- docs/              Supporting project documentation
|-- config/            Configuration and control settings
|-- requirements.txt
`-- README.md
```

## Full portfolio workbook

The broader project was developed against Version 23 of the **Houston Energy Trade Operations and Demurrage Portfolio**, a larger fictional physical-energy trading workbook covering a wider trade-operations environment.

That workbook is kept separate from the public demo repository and is intended for deeper portfolio or interview walkthroughs.

The public synthetic workbook is not a reduced copy of that portfolio. It is generated independently from fictional records specifically designed to exercise the Python settlement controls.

## Design principles

The project follows several control-design principles:

1. **Calculate first, interpret second.**  
   Reconciliation mathematics is kept separate from business classification.

2. **Preserve exceptions rather than hiding them.**  
   Cancelled or excluded records remain visible for audit purposes.

3. **Use transactional relationships rather than inference.**  
   Payment and invoice exceptions are linked through payment-allocation records, not matching amounts.

4. **Separate control findings from economic cases.**  
   Multiple control observations can belong to one underlying settlement situation.

5. **Keep source workbooks immutable from Python.**  
   Input workbooks are read and closed; generated reports are written to separate output files.

6. **Test controls independently before orchestration.**  
   Individual business rules are unit tested before being incorporated into the end-to-end runner.

## Technology

- Python 3.13
- pandas
- openpyxl
- pytest
- PyYAML

## Future enhancements

Potential extensions include:

- invoice and payment foreign-key validation in the main execution pipeline;
- trade and movement reconciliation;
- service-commitment and accrual controls;
- demurrage and claims reconciliation;
- configurable tolerances and control rules;
- exception aging and ownership;
- execution logging;
- management dashboards and trend reporting.