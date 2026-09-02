"""
Carbon savings metrics.

Module 5.3:
    Calculate carbon savings achieved by replacing the baseline
    environmental footprint with the recycling-loop footprint.

Design principles:
- Consume validated 5.2 recycling-loop metrics.
- Preserve baseline and recycling-loop values for traceability.
- Calculate material-level carbon savings.
- Calculate material-level savings percentage.
- Provide aggregate savings metrics.
- Validate all inputs at the module boundary.
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
    "recycling_emission_ratio",
    "recycling_loop_footprint_kg_co2e",
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
    "carbon_savings_kg_co2e",
    "carbon_savings_percentage",
]


def _validate_input(
    recycling_loop_metrics: pd.DataFrame,
) -> None:
    """Validate 5.2 recycling-loop metrics."""

    if not isinstance(recycling_loop_metrics, pd.DataFrame):
        raise TypeError(
            "recycling_loop_metrics must be a pandas DataFrame."
        )

    if recycling_loop_metrics.empty:
        raise ValueError(
            "recycling_loop_metrics must contain at least one row."
        )

    missing_columns = REQUIRED_COLUMNS.difference(
        recycling_loop_metrics.columns
    )

    if missing_columns:
        raise ValueError(
            "recycling_loop_metrics is missing required columns: "
            f"{sorted(missing_columns)}"
        )

    if recycling_loop_metrics["material_id"].isna().any():
        raise ValueError(
            "material_id must not contain null values."
        )

    if recycling_loop_metrics["material_name"].isna().any():
        raise ValueError(
            "material_name must not contain null values."
        )

    if recycling_loop_metrics["unit"].isna().any():
        raise ValueError(
            "unit must not contain null values."
        )

    if recycling_loop_metrics["material_id"].duplicated().any():
        raise ValueError(
            "material_id must be unique."
        )

    numeric_columns = [
        "quantity",
        "emission_factor",
        "baseline_carbon_footprint_kg_co2e",
        "recycling_emission_ratio",
        "recycling_loop_footprint_kg_co2e",
    ]

    for column in numeric_columns:
        if not pd.api.types.is_numeric_dtype(
            recycling_loop_metrics[column]
        ):
            raise TypeError(
                f"{column} must be numeric."
            )

        if recycling_loop_metrics[column].isna().any():
            raise ValueError(
                f"{column} must not contain null values."
            )

        if not recycling_loop_metrics[column].map(
            lambda value: pd.notna(value)
            and pd.api.types.is_number(value)
        ).all():
            raise TypeError(
                f"{column} contains non-numeric values."
            )

    if (recycling_loop_metrics["quantity"] < 0).any():
        raise ValueError(
            "quantity must be non-negative."
        )

    if (recycling_loop_metrics["emission_factor"] < 0).any():
        raise ValueError(
            "emission_factor must be non-negative."
        )

    if (
        recycling_loop_metrics[
            "baseline_carbon_footprint_kg_co2e"
        ] < 0
    ).any():
        raise ValueError(
            "baseline_carbon_footprint_kg_co2e must be non-negative."
        )

    if (
        recycling_loop_metrics["recycling_emission_ratio"] < 0
    ).any() or (
        recycling_loop_metrics["recycling_emission_ratio"] > 1
    ).any():
        raise ValueError(
            "recycling_emission_ratio must be between 0 and 1."
        )

    if (
        recycling_loop_metrics[
            "recycling_loop_footprint_kg_co2e"
        ] < 0
    ).any():
        raise ValueError(
            "recycling_loop_footprint_kg_co2e must be non-negative."
        )


def calculate_carbon_savings(
    recycling_loop_metrics: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate material-level carbon savings.

    Parameters
    ----------
    recycling_loop_metrics:
        Validated output from Module 5.2.

    Returns
    -------
    pd.DataFrame
        Material-level carbon savings metrics.

    Formulas
    --------
    carbon_savings =
        baseline_carbon_footprint
        - recycling_loop_footprint

    carbon_savings_percentage =
        carbon_savings / baseline_carbon_footprint * 100
    """

    _validate_input(recycling_loop_metrics)

    result = recycling_loop_metrics.copy()

    result["carbon_savings_kg_co2e"] = (
        result["baseline_carbon_footprint_kg_co2e"]
        - result["recycling_loop_footprint_kg_co2e"]
    )

    if (result["carbon_savings_kg_co2e"] < 0).any():
        raise ValueError(
            "carbon savings cannot be negative."
        )

    zero_baseline = (
        result["baseline_carbon_footprint_kg_co2e"] == 0
    )

    if zero_baseline.any():
        if (
            result.loc[
                zero_baseline,
                "recycling_loop_footprint_kg_co2e",
            ]
            != 0
        ).any():
            raise ValueError(
                "recycling_loop_footprint must be zero when "
                "baseline carbon footprint is zero."
            )

        result["carbon_savings_percentage"] = 0.0

        non_zero_baseline = ~zero_baseline

        result.loc[
            non_zero_baseline,
            "carbon_savings_percentage",
        ] = (
            result.loc[
                non_zero_baseline,
                "carbon_savings_kg_co2e",
            ]
            / result.loc[
                non_zero_baseline,
                "baseline_carbon_footprint_kg_co2e",
            ]
            * 100.0
        )
    else:
        result["carbon_savings_percentage"] = (
            result["carbon_savings_kg_co2e"]
            / result["baseline_carbon_footprint_kg_co2e"]
            * 100.0
        )

    return result[OUTPUT_COLUMNS].copy()


def get_carbon_savings_summary(
    recycling_loop_metrics: pd.DataFrame,
) -> dict[str, Any]:
    """
    Return aggregate carbon savings metrics.

    The summary is calculated from the same material-level
    output returned by calculate_carbon_savings().
    """

    savings_metrics = calculate_carbon_savings(
        recycling_loop_metrics
    )

    total_quantity = float(
        savings_metrics["quantity"].sum()
    )

    total_baseline = float(
        savings_metrics[
            "baseline_carbon_footprint_kg_co2e"
        ].sum()
    )

    total_recycling_loop = float(
        savings_metrics[
            "recycling_loop_footprint_kg_co2e"
        ].sum()
    )

    total_savings = float(
        savings_metrics[
            "carbon_savings_kg_co2e"
        ].sum()
    )

    if total_baseline == 0:
        overall_savings_percentage = 0.0
    else:
        overall_savings_percentage = (
            total_savings / total_baseline
        ) * 100.0

    return {
        "material_count": int(len(savings_metrics)),
        "total_quantity": total_quantity,
        "total_baseline_carbon_footprint_kg_co2e": (
            total_baseline
        ),
        "total_recycling_loop_footprint_kg_co2e": (
            total_recycling_loop
        ),
        "total_carbon_savings_kg_co2e": (
            total_savings
        ),
        "overall_carbon_savings_percentage": (
            overall_savings_percentage
        ),
    }