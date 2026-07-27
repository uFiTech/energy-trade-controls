"""Functions for safely reading the source portfolio workbook."""

from pathlib import Path

from openpyxl import load_workbook


def list_workbook_sheets(workbook_path: str | Path) -> list[str]:
    """Rturn the workbook names contained in an Excel workbook.

    Args:
        workbook_path: Location of the source Excel workbook.

    Returns:
        The workbook's worksheet names.

    Raises:
        FileNotFoundError: If the workbook does not exist.
    """

    path = Path(workbook_path)

    if not path.is_file():
        raise FileNotFoundError(f"Workbook not found: {path}")

    workbook = load_workbook(
        filename=path,
        read_only=True,
        data_only=True,
    )

    try:
        return workbook.sheetnames
    finally:
        workbook.close()


def map_workbook_tables(workbook_path: str | Path) -> dict[str, str]:
    """Return structured Excel table names and their worksheets.

    Args:
        workbook_path: Location of the source Excel workbook.

    Returns:
        A mapping whose keys are Excel table names and whose values are
        worksheet names.

    Raises:
        FileNotFoundError: If the supplied workbook does not exist.
        ValueError: If the same table name is found more than once.
     """

    path = Path(workbook_path)

    if not path.is_file():
        raise FileNotFoundError(f"Workbook not found: {path}")

    workbook = load_workbook(
        filename=path,
        read_only=False,
        data_only=False,
    )

    try:
        table_locations: dict[str, str] = {}

        for worksheet in workbook.worksheets:
            for table in worksheet.tables.values():
                if table.name in table_locations:
                    raise ValueError(
                        f"Duplicate Excel table names found: {table.name}"
                    )

                table_locations[table.name] = worksheet.title

        return table_locations

    finally:
        workbook.close()
