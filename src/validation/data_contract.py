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


def find_primary_key_issues(
        dataframe: pd.DataFrame,
        primary_key: str,
) -> dict[str, list[int] | list[str]]:
    """Return blank-row indexes and duplicate primary-key values.

    Primary-key values are converted to text and stripped of surrounding
    whitespace before validation.

    Args:
        dataframe: Dataset containing the primary-key column.
        primary_key: Column name that uniquely identifies each record.

    Returns:
        A mapping containing blank row indexes and normalized duplicate
        key values.

    Raises:
        KeyError: If the primary-key column does not exist.
    """
    if primary_key not in dataframe.columns:
        raise KeyError(f"Primary key column not found: {primary_key}")

    normalized_keys = (
        dataframe[primary_key]
        .astype("string")
        .fillna("")
        .str.strip()
    )

    blank_row_indexs = dataframe.index[
        normalized_keys.eq("")
    ].tolist()

    nonblank_keys = normalized_keys[normalized_keys.ne("")]

    duplicate_keys = nonblank_keys[
        nonblank_keys.duplicated(keep=False)
    ]

    duplicate_values = list(
        dict.fromkeys(duplicate_keys.tolist())
    )

    return {
        "blank_row_indexes": blank_row_indexs,
        "duplicate_values": duplicate_values,
    }