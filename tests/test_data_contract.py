"""Tests for tabular data-contract validation."""
import pytest
import pandas as pd

from src.validation.data_contract import (
    REQUIRED_TRADE_COLUMNS,
    find_missing_columns,
    find_primary_key_issues,
    find_foreign_key_issues,
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


def test_find_primary_key_issues_returns_empty_when_keys_valid() -> None:
     """Unique, nonblank keys should produce no issues."""
     dataframe = pd.DataFrame(
          {
               "Trade ID": [
                    "TRD-1001",
                    "TRD-1002",
                    "TRD-1003",
               ]
          }
     )

     result = find_primary_key_issues(dataframe,"Trade ID")

     assert result == {
         "blank_row_indexes": [],
         "duplicate_values": [],
     }


def test_find_primary_key_issues_identifies_blank_keys() -> None:
    """Missing, empty and whitespace-only keys should all be blank."""
    dataframe = pd.DataFrame(
         {
              "Trade ID": [
                   "TRD-1001",
                   None,
                   "",
                   "   ",
              ]
         }
    )

    result = find_primary_key_issues(dataframe, "Trade ID")

    assert result == {
         "blank_row_indexes": [1, 2, 3],
         "duplicate_values": [],
    }


def test_find_primary_key_issues_normalizes_duplicate_keys() -> None:
    """Surrounding spaces should not hide duplicate identifiers."""
    dataframe = pd.DataFrame(
        {
            "Trade ID": [
                "TRD-1001",
                " TRD-1001 ",
                "TRD-1002",
            ]
        }
    )

    result = find_primary_key_issues(dataframe, "Trade ID")

    assert result == {
        "blank_row_indexes": [],
        "duplicate_values": ["TRD-1001"],
    }


def test_find_primary_key_issues_raises_when_column_missing() -> None:
    """A missing primary-key column should raise a clear error."""
    dataframe = pd.DataFrame(
        {
            "Product Code": ["ULSD-US"],
        }
     )

    with pytest.raises(
         KeyError,
         match="Primary key column not found",

     ):
         find_primary_key_issues(dataframe, "Trade ID")


def test_find_foreign_key_issues_returns_empty_when_links_valid() -> None:
     """Valid foreign keys and blank optional keys should not be orphans."""
     trades = pd.DataFrame(
          {
               "Counterparty ID": [
                    "CP-001",
                    "CP-002",
                    None,
                    "",
               ]
          }
     )

     counterparties = pd.DataFrame(
          {
               "Counterparty ID": [
                    "CP-001",
                    "CP-002",
                    "CP-003",
               ]
          }
     )

     result = find_foreign_key_issues(
          trades,
          "Counterparty ID",
          counterparties,
          "Counterparty ID",
     )

     assert result == {
        "orphan_row_indexes": [],
        "orphan_values": [],
     }


def test_find_foreign_key_issues_identifies_orphans() -> None:
     """Unknown foreign keys should report their rows and values."""
     trades = pd.DataFrame(
        {
            "Counterparty ID": [
                "CP-001",
                "CP-999",
                "CP-002",
                "CP-999",
                "CP-888",
            ]
        }
    )

     counterparties = pd.DataFrame(
        {
            "Counterparty ID": [
                "CP-001",
                "CP-002",
            ]
        }
    )

     result = find_foreign_key_issues(
          trades,
          "Counterparty ID",
          counterparties,
          "Counterparty ID",
     )

     assert result == {
        "orphan_row_indexes": [1, 3, 4],
        "orphan_values": ["CP-999", "CP-888"],
    }


def test_find_foreign_key_issues_normalizes_spaces() -> None:
    """Surrounding spaces should not create false orphan records."""
    trades = pd.DataFrame(
        {
            "Counterparty ID": [
                " CP-002 ",
            ]
        }
    )

    counterparties = pd.DataFrame(
        {
            "Counterparty ID": [
                "CP-002",
            ]
        }
    )

    result = find_foreign_key_issues(
        trades,
        "Counterparty ID",
        counterparties,
        "Counterparty ID",
    )

    assert result == {
        "orphan_row_indexes": [],
        "orphan_values": [],
    }


def test_find_foreign_key_issues_raises_when_child_column_missing() -> None:
    """A missing child foreign-key column should raise a clear error."""
    trades = pd.DataFrame(
        {
            "Trade ID": ["TRD-1001"],
        }
    )

    counterparties = pd.DataFrame(
        {
            "Counterparty ID": ["CP-001"],
        }
    )

    with pytest.raises(
         KeyError,
         match="Foreign key column not found",
    ):
         find_foreign_key_issues(
              trades,
              "Counterparty ID",
              counterparties,
              "Counterparty ID",
         )


def test_find_foreign_key_issues_raises_when_parent_column_missing() -> None:
    """A missing parent-key column should raise a clear error."""
    trades = pd.DataFrame(
        {
            "Counterparty ID": ["CP-001"],
        }
    )

    counterparties = pd.DataFrame(
        {
            "Counterparty Name": ["Example Energy"],
        }
    )

    with pytest.raises(
        KeyError,
        match="Parent key column not found",
    ):
        find_foreign_key_issues(
            trades,
            "Counterparty ID",
            counterparties,
            "Counterparty ID",
        )


     

     