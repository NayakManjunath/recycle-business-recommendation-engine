"""
Carbon footprint calculation utilities.

This module calculates the baseline carbon footprint associated
with available waste materials using emission factors.

Formula:
    carbon_footprint = quantity * emission_factor

Units:
    quantity: kg
    emission_factor: kg CO2e per kg
    carbon_footprint: kg CO2e
"""

from __future__ import annotations

from typing import Final

import pandas as pd

from src.environmental.emission_factors import get_emission_factor


REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "material_id",
    "material_name",
    "quantity",
)


def _validate_columns(
    df: pd.DataFrame,
    required_columns: tuple[str, ...],
) -> None:
    """Validate that all required columns exist."""
    missing_columns = [
        column for column in required_columns if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns for carbon footprint calculation: "
            f"{missing_columns}"
        )


def _validate_input_dataframe(df: pd.DataFrame) -> None:
    """Validate the material input DataFrame."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("materials_df must be a pandas DataFrame.")

    _validate_columns(df, REQUIRED_COLUMNS)

    if df.empty:
        raise ValueError("materials_df must not be empty.")

    if df["material_id"].isna().any():
        raise ValueError("material_id must not contain null values.")

    if df["material_name"].isna().any():
        raise ValueError("material_name must not contain null values.")

    if not pd.api.types.is_numeric_dtype(df["quantity"]):
        raise ValueError("quantity must be numeric.")

    if df["quantity"].isna().any():
        raise ValueError("quantity must not contain null values.")

    if (df["quantity"] < 0).any():
        raise ValueError("quantity must be non-negative.")


def calculate_carbon_footprint(
    materials_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate baseline carbon footprint for each material.

    Parameters
    ----------
    materials_df:
        DataFrame containing:
        - material_id
        - material_name
        - quantity

    Returns
    -------
    pd.DataFrame
        Copy of the input DataFrame with:
        - emission_factor
        - carbon_footprint_kg_co2e

    Notes
    -----
    Carbon footprint is calculated as:

        quantity * emission_factor

    The emission factor is retrieved using the centralized
    emission-factor lookup layer.
    """
    _validate_input_dataframe(materials_df)

    result = materials_df.copy()

    result["emission_factor"] = result["material_name"].apply(
        get_emission_factor
    )

    result["carbon_footprint_kg_co2e"] = (
        result["quantity"] * result["emission_factor"]
    )

    return result