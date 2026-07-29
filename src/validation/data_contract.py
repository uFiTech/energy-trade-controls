"""Validation functions for tabular data contracts."""

from collections.abc import Sequence

import pandas as pd


REQUIRED_TRADE_COLUMNS: tuple[str, ...] = (
    "Trade ID",
    "Counterparty ID",
    "Product Code",
)


def find_missing_columns(
        dataframe: pd.DataFrame,
        required_columns: Sequence[str],
) -> list[str]:
    """Return required column names that are missing from a DataFrame.

    Args:
        dataframe: Dataset whose column labels will be validated.
        required_columns: Column names required by the data contract.

    Returns:
        Missing column names in configured order.
    """
    actual_columns = set(dataframe.columns)

    return [
        column
        for column in required_columns
        if column not in actual_columns
    ]