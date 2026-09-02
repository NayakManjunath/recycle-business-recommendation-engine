"""
Baseline environmental metrics engine.

Module 5.1
----------
Provides a production-oriented baseline environmental metrics
layer for the Carbon Footprint Savings Engine.

The implementation reuses the validated Module 4 carbon-footprint
calculation rather than duplicating emission-factor logic.
"""

from __future__ import annotations

from typing import Final

import pandas as pd

from src.environmental.carbon_footprint import calculate_carbon_footprint


REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "material_id",
    "material_name",
    "quantity",
    "unit",
)


OUTPUT_COLUMNS: Final[tuple[str, ...]] = (
    "material_id",
    "material_name",
    "quantity",
    "unit",
    "emission_factor",
    "baseline_carbon_footprint_kg_co2e",
)


def _validate_input(materials: pd.DataFrame) -> None:
    """
    Validate material input data.

    Parameters
    ----------
    materials:
        Material-level environmental input data.

    Raises
    ------
    TypeError
        If materials is not a pandas DataFrame.

    ValueError
        If required columns are missing or contain invalid values.
    """
    if not isinstance(materials, pd.DataFrame):
        raise TypeError(
            "materials must be a pandas DataFrame."
        )

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in materials.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required material columns: "
            f"{missing_columns}"
        )

    if materials.empty:
        raise ValueError(
            "materials must contain at least one row."
        )

    if materials["material_id"].isna().any():
        raise ValueError(
            "material_id must not contain null values."
        )

    if materials["material_name"].isna().any():
        raise ValueError(
            "material_name must not contain null values."
        )

    if materials["unit"].isna().any():
        raise ValueError(
            "unit must not contain null values."
        )

    if not pd.api.types.is_numeric_dtype(
        materials["quantity"]
    ):
        raise ValueError(
            "quantity must be numeric."
        )

    if materials["quantity"].isna().any():
        raise ValueError(
            "quantity must not contain null values."
        )

    if not pd.api.types.is_numeric_dtype(
        materials["quantity"]
    ):
        raise ValueError(
            "quantity must be numeric."
        )

    if (materials["quantity"] < 0).any():
        raise ValueError(
            "quantity must be non-negative."
        )

    if materials["material_id"].duplicated().any():
        raise ValueError(
            "material_id must be unique."
        )


def calculate_baseline_metrics(
    materials: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate baseline environmental metrics.

    Parameters
    ----------
    materials:
        DataFrame containing:

        - material_id
        - material_name
        - quantity
        - unit

    Returns
    -------
    pandas.DataFrame
        Material-level baseline environmental metrics containing:

        - material_id
        - material_name
        - quantity
        - unit
        - emission_factor
        - baseline_carbon_footprint_kg_co2e

    Raises
    ------
    TypeError
        If materials is not a pandas DataFrame.

    ValueError
        If input data is invalid or environmental calculation
        produces invalid results.
    """
    _validate_input(materials)

    # Keep the input isolated from downstream transformations.
    material_input = materials[
        list(REQUIRED_COLUMNS)
    ].copy()

    # Reuse the existing Module 4 implementation as the
    # single source of truth for emission factors and
    # baseline carbon-footprint calculation.
    carbon_data = calculate_carbon_footprint(
        material_input
    )

    required_carbon_columns = (
        "material_id",
        "material_name",
        "quantity",
        "unit",
        "emission_factor",
        "carbon_footprint_kg_co2e",
    )

    missing_carbon_columns = [
        column
        for column in required_carbon_columns
        if column not in carbon_data.columns
    ]

    if missing_carbon_columns:
        raise ValueError(
            "Carbon-footprint calculation returned missing "
            "columns: "
            f"{missing_carbon_columns}"
        )

    if carbon_data["emission_factor"].isna().any():
        raise ValueError(
            "Baseline emission factors must not contain "
            "null values."
        )

    if carbon_data["carbon_footprint_kg_co2e"].isna().any():
        raise ValueError(
            "Baseline carbon footprint must not contain "
            "null values."
        )

    if not pd.api.types.is_numeric_dtype(
        carbon_data["emission_factor"]
    ):
        raise ValueError(
            "emission_factor must be numeric."
        )

    if not pd.api.types.is_numeric_dtype(
        carbon_data["carbon_footprint_kg_co2e"]
    ):
        raise ValueError(
            "carbon_footprint_kg_co2e must be numeric."
        )

    if (carbon_data["emission_factor"] < 0).any():
        raise ValueError(
            "emission_factor must be non-negative."
        )

    if (
        carbon_data["carbon_footprint_kg_co2e"] < 0
    ).any():
        raise ValueError(
            "carbon_footprint_kg_co2e must be non-negative."
        )

    result = carbon_data[
        [
            "material_id",
            "material_name",
            "quantity",
            "unit",
            "emission_factor",
            "carbon_footprint_kg_co2e",
        ]
    ].copy()

    result = result.rename(
        columns={
            "carbon_footprint_kg_co2e":
                "baseline_carbon_footprint_kg_co2e"
        }
    )

    # Guarantee the public output contract.
    result = result[
        list(OUTPUT_COLUMNS)
    ]

    return result


def get_baseline_environmental_summary(
    materials: pd.DataFrame,
) -> dict[str, float | int]:
    """
    Generate aggregate baseline environmental metrics.

    Parameters
    ----------
    materials:
        Material-level environmental input data.

    Returns
    -------
    dict
        Aggregate baseline metrics containing:

        - material_count
        - total_quantity
        - total_baseline_carbon_footprint_kg_co2e
    """
    baseline = calculate_baseline_metrics(materials)

    return {
        "material_count": int(len(baseline)),
        "total_quantity": float(
            baseline["quantity"].sum()
        ),
        "total_baseline_carbon_footprint_kg_co2e": float(
            baseline[
                "baseline_carbon_footprint_kg_co2e"
            ].sum()
        ),
    }