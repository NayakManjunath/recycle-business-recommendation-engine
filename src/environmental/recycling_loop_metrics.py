"""
Recycling-loop environmental metrics.

Module 5.2:
    Calculate carbon footprint associated with the recycling loop
    from validated baseline environmental metrics.

Design principles:
- Consume 5.1 baseline metrics rather than recalculating them.
- Keep calculations deterministic and traceable.
- Validate inputs at the module boundary.
- Reject invalid recycling ratios and environmental values.
- Preserve material-level records.
- Provide aggregate recycling-loop metrics for downstream savings
  calculations.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


REQUIRED_COLUMNS = {
    "material_id",
    "material_name",
    "quantity",
    "unit",
    "emission_factor",
    "baseline_carbon_footprint_kg_co2e",
}

OUTPUT_COLUMNS = [
    "material_id",
    "material_name",
    "quantity",
    "unit",
    "emission_factor",
    "baseline_carbon_footprint_kg_co2e",
    "recycling_emission_ratio",
    "recycling_loop_footprint_kg_co2e",
]


def _validate_recycling_ratio(recycling_emission_ratio: float) -> None:
    """Validate the recycling-loop emission ratio."""

    if not isinstance(recycling_emission_ratio, (int, float)):
        raise TypeError(
            "recycling_emission_ratio must be a numeric value."
        )

    if pd.isna(recycling_emission_ratio):
        raise ValueError(
            "recycling_emission_ratio must not be null."
        )

    if recycling_emission_ratio < 0 or recycling_emission_ratio > 1:
        raise ValueError(
            "recycling_emission_ratio must be between 0 and 1."
        )


def _validate_input(baseline_metrics: pd.DataFrame) -> None:
    """Validate baseline environmental metrics."""

    if not isinstance(baseline_metrics, pd.DataFrame):
        raise TypeError(
            "baseline_metrics must be a pandas DataFrame."
        )

    if baseline_metrics.empty:
        raise ValueError(
            "baseline_metrics must contain at least one row."
        )

    missing_columns = REQUIRED_COLUMNS.difference(
        baseline_metrics.columns
    )

    if missing_columns:
        raise ValueError(
            "baseline_metrics is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    if baseline_metrics["material_id"].isna().any():
        raise ValueError(
            "material_id must not contain null values."
        )

    if baseline_metrics["material_name"].isna().any():
        raise ValueError(
            "material_name must not contain null values."
        )

    if baseline_metrics["unit"].isna().any():
        raise ValueError(
            "unit must not contain null values."
        )

    if baseline_metrics["material_id"].duplicated().any():
        raise ValueError(
            "material_id must be unique."
        )

    numeric_columns = [
        "quantity",
        "emission_factor",
        "baseline_carbon_footprint_kg_co2e",
    ]

    for column in numeric_columns:
        if not pd.api.types.is_numeric_dtype(
            baseline_metrics[column]
        ):
            raise TypeError(
                f"{column} must be numeric."
            )

        if baseline_metrics[column].isna().any():
            raise ValueError(
                f"{column} must not contain null values."
            )

        if not baseline_metrics[column].map(
            lambda value: pd.notna(value)
            and pd.api.types.is_number(value)
        ).all():
            raise TypeError(
                f"{column} contains non-numeric values."
            )

    if (baseline_metrics["quantity"] < 0).any():
        raise ValueError(
            "quantity must be non-negative."
        )

    if (baseline_metrics["emission_factor"] < 0).any():
        raise ValueError(
            "emission_factor must be non-negative."
        )

    if (
        baseline_metrics["baseline_carbon_footprint_kg_co2e"] < 0
    ).any():
        raise ValueError(
            "baseline_carbon_footprint_kg_co2e must be non-negative."
        )


def calculate_recycling_loop_metrics(
    baseline_metrics: pd.DataFrame,
    recycling_emission_ratio: float = 0.30,
) -> pd.DataFrame:
    """
    Calculate recycling-loop carbon footprint metrics.

    Parameters
    ----------
    baseline_metrics:
        Validated output from 5.1 baseline environmental metrics.

    recycling_emission_ratio:
        Fraction of the baseline carbon footprint attributed to
        the recycling loop.

        Example:
            0.30 means the recycling loop produces 30% of the
            baseline carbon footprint.

    Returns
    -------
    pd.DataFrame
        Material-level recycling-loop environmental metrics.

    Formula
    -------
    recycling_loop_footprint =
        baseline_carbon_footprint * recycling_emission_ratio
    """

    _validate_recycling_ratio(recycling_emission_ratio)
    _validate_input(baseline_metrics)

    result = baseline_metrics.copy()

    result["recycling_emission_ratio"] = float(
        recycling_emission_ratio
    )

    result["recycling_loop_footprint_kg_co2e"] = (
        result["baseline_carbon_footprint_kg_co2e"]
        * result["recycling_emission_ratio"]
    )

    return result[OUTPUT_COLUMNS].copy()


def get_recycling_loop_environmental_summary(
    baseline_metrics: pd.DataFrame,
    recycling_emission_ratio: float = 0.30,
) -> dict[str, Any]:
    """
    Return aggregate recycling-loop environmental metrics.

    The summary is calculated from the same material-level metrics
    returned by calculate_recycling_loop_metrics().
    """

    recycling_metrics = calculate_recycling_loop_metrics(
        baseline_metrics=baseline_metrics,
        recycling_emission_ratio=recycling_emission_ratio,
    )

    total_quantity = float(
        recycling_metrics["quantity"].sum()
    )

    total_baseline_footprint = float(
        recycling_metrics[
            "baseline_carbon_footprint_kg_co2e"
        ].sum()
    )

    total_recycling_loop_footprint = float(
        recycling_metrics[
            "recycling_loop_footprint_kg_co2e"
        ].sum()
    )

    return {
        "material_count": int(len(recycling_metrics)),
        "total_quantity": total_quantity,
        "recycling_emission_ratio": float(
            recycling_emission_ratio
        ),
        "total_baseline_carbon_footprint_kg_co2e": (
            total_baseline_footprint
        ),
        "total_recycling_loop_footprint_kg_co2e": (
            total_recycling_loop_footprint
        ),
    }