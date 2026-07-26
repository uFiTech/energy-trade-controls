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
