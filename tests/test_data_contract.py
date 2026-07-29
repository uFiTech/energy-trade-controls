"""Tests for tabular data-contract validation."""

import pandas as pd

from src.validation.data_contract import (
    REQUIRED_TRADE_COLUMNS,
    find_missing_columns,
)


def test_find_missing_columns_returns_empty_when_all_exist() -> None:
     """No columns should be reported when the full schema exists."""
     dataframe = pd.DataFrame(
          columns=[
            "Trade ID",
            "Counterparty ID",
            "Product Code",
            "Trade Date",
          ]
     )

     result = find_missing_columns(
          dataframe, 
          REQUIRED_TRADE_COLUMNS
          )

     assert result == []


def test_find_missing_columns_returns_names_in_required_order() -> None:
     """Missing columns should follow the configured contract order."""
     dtatframe = pd.DataFrame(
          columns=[
            "Trade ID",
            "Trade Date",
          ]
     )

     result = find_missing_columns(
          dtatframe,
          REQUIRED_TRADE_COLUMNS,
     )

     assert result == [
          "Counterparty ID",
          "Product Code",
     ]


def test_find_missing_columns_allows_extra_columns() -> None:
     """Additional workbook columns should not fail the data contract."""
     dataframe = pd.DataFrame(
          {
            "Trade ID": ["TRD-1001"],
            "Counterparty ID": ["CP-002"],
            "Product Code": ["ULSD-US"],
            "Optional Notes": ["Test record"],
          }
     )

     result = find_missing_columns(
          dataframe,
          REQUIRED_TRADE_COLUMNS,
     )

     assert result == []