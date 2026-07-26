# Energy Trade Controls

A Python automation and controls project for a fictional physical-energy trading portfolio.

## Project objectives

- Read controlled Excel tables from the portfolio workbook.
- Validate workbook structure and data quality.
- Reconcile trades, movements, invoices, payments, accruals, and claims.
- Identify settlement and month-end exceptions.
- Produce auditable reports and execution logs.

## Project structure

- `config/` — validation rules and configurable thresholds
- `data/input/` — source workbooks, excluded from Git
- `data/output/` — generated reports, excluded from Git
- `docs/` — project and control documentation
- `logs/` — execution logs
- `src/` — Python source code
- `tests/` — automated tests

## Workbook baseline

The initial automation baseline is Version 23 of the Houston Energy Trade Operations and Demurrage Portfolio.

## Environment

- Python 3.13
- pandas
- openpyxl
- PyYAML
- pytest
