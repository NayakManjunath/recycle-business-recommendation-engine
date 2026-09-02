"""
Environmental Savings Integration
----------------------------------

Module 5.4

Integrates the outputs produced by the carbon savings engine
into a consolidated environmental savings view.

This module intentionally does not recalculate:
- baseline carbon footprint
- recycling-loop footprint
- carbon savings
- carbon savings percentage

Those calculations belong to Modules 5.1, 5.2, and 5.3 respectively.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


REQUIRED_COLUMNS = [
    "material_id",
    "material_name",
    "quantity",
    "unit",
    "baseline_carbon_footprint_kg_co2e",
    "recycling_loop_footprint_kg_co2e",
    "carbon_savings_kg_co2e",
    "carbon_savings_percentage",
]


OUTPUT_COLUMNS = [
    "material_id",
    "material_name",
    "quantity",
    "unit",
    "baseline_carbon_footprint_kg_co2e",
    "recycling_loop_footprint_kg_co2e",
    "carbon_savings_kg_co2e",
    "carbon_savings_percentage",
]


def _validate_input(carbon_savings_metrics: pd.DataFrame) -> None:
    """Validate the carbon savings metrics before integration."""

    if not isinstance(carbon_savings_metrics, pd.DataFrame):
        raise TypeError("carbon_savings_metrics must be a pandas DataFrame.")

    if carbon_savings_metrics.empty:
        raise ValueError(
            "carbon_savings_metrics must contain at least one row."
        )

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in carbon_savings_metrics.columns
    ]

    if missing_columns:
        raise ValueError(
            "carbon_savings_metrics is missing required columns: "
            f"{missing_columns}"
        )

    # Identifier validation
    if carbon_savings_metrics["material_id"].isna().any():
        raise ValueError("material_id cannot contain null values.")

    if carbon_savings_metrics["material_name"].isna().any():
        raise ValueError("material_name cannot contain null values.")

    if carbon_savings_metrics["unit"].isna().any():
        raise ValueError("unit cannot contain null values.")

    if carbon_savings_metrics["material_id"].duplicated().any():
        raise ValueError("material_id values must be unique.")

    # Numeric validation
    numeric_columns = [
        "quantity",
        "baseline_carbon_footprint_kg_co2e",
        "recycling_loop_footprint_kg_co2e",
        "carbon_savings_kg_co2e",
        "carbon_savings_percentage",
    ]

    for column in numeric_columns:
        if not pd.api.types.is_numeric_dtype(
            carbon_savings_metrics[column]
        ):
            raise ValueError(f"{column} must be numeric.")

        if carbon_savings_metrics[column].isna().any():
            raise ValueError(f"{column} cannot contain null values.")

    # Environmental metrics must be non-negative.
    non_negative_columns = [
        "quantity",
        "baseline_carbon_footprint_kg_co2e",
        "recycling_loop_footprint_kg_co2e",
        "carbon_savings_kg_co2e",
        "carbon_savings_percentage",
    ]

    for column in non_negative_columns:
        if (carbon_savings_metrics[column] < 0).any():
            raise ValueError(
                f"{column} must be non-negative."
            )

    # Savings percentage cannot exceed 100%.
    if (carbon_savings_metrics["carbon_savings_percentage"] > 100).any():
        raise ValueError(
            "carbon_savings_percentage cannot exceed 100."
        )

    # Integration consistency checks.
    calculated_savings = (
        carbon_savings_metrics["baseline_carbon_footprint_kg_co2e"]
        - carbon_savings_metrics["recycling_loop_footprint_kg_co2e"]
    )

    if not calculated_savings.round(10).equals(
        carbon_savings_metrics["carbon_savings_kg_co2e"].round(10)
    ):
        raise ValueError(
            "carbon_savings_kg_co2e is inconsistent with baseline and "
            "recycling-loop footprints."
        )

    non_zero_baseline = (
        carbon_savings_metrics["baseline_carbon_footprint_kg_co2e"] > 0
    )

    expected_percentage = pd.Series(
        0.0,
        index=carbon_savings_metrics.index,
    )

    expected_percentage.loc[non_zero_baseline] = (
        carbon_savings_metrics.loc[
            non_zero_baseline,
            "carbon_savings_kg_co2e",
        ]
        / carbon_savings_metrics.loc[
            non_zero_baseline,
            "baseline_carbon_footprint_kg_co2e",
        ]
        * 100
    )

    if not expected_percentage.round(10).equals(
        carbon_savings_metrics["carbon_savings_percentage"].round(10)
    ):
        raise ValueError(
            "carbon_savings_percentage is inconsistent with carbon savings "
            "and baseline footprint."
        )


def integrate_environmental_savings(
    carbon_savings_metrics: pd.DataFrame,
) -> pd.DataFrame:
    """
    Integrate carbon savings metrics into a consolidated environmental view.

    Parameters
    ----------
    carbon_savings_metrics:
        Output DataFrame produced by calculate_carbon_savings().

    Returns
    -------
    pd.DataFrame
        Consolidated environmental savings metrics.
    """

    _validate_input(carbon_savings_metrics)

    integrated = carbon_savings_metrics.loc[:, OUTPUT_COLUMNS].copy()

    return integrated


def get_environmental_savings_summary(
    carbon_savings_metrics: pd.DataFrame,
) -> dict[str, Any]:
    """
    Return an aggregated environmental savings summary.

    Parameters
    ----------
    carbon_savings_metrics:
        Output DataFrame produced by calculate_carbon_savings().

    Returns
    -------
    dict[str, Any]
        Aggregated environmental savings metrics.
    """

    integrated = integrate_environmental_savings(
        carbon_savings_metrics
    )

    total_baseline = float(
        integrated["baseline_carbon_footprint_kg_co2e"].sum()
    )

    total_savings = float(
        integrated["carbon_savings_kg_co2e"].sum()
    )

    if total_baseline == 0:
        overall_percentage = 0.0
    else:
        overall_percentage = (
            total_savings / total_baseline
        ) * 100

    return {
        "material_count": int(len(integrated)),
        "total_quantity": float(
            integrated["quantity"].sum()
        ),
        "total_baseline_carbon_footprint_kg_co2e": total_baseline,
        "total_recycling_loop_footprint_kg_co2e": float(
            integrated["recycling_loop_footprint_kg_co2e"].sum()
        ),
        "total_carbon_savings_kg_co2e": total_savings,
        "overall_carbon_savings_percentage": float(
            overall_percentage
        ),
    }