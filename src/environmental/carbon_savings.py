"""
Carbon savings calculation.

Module 4.4
----------
Calculates carbon savings by comparing the baseline carbon footprint
with the estimated recycling/reuse footprint.
"""

from __future__ import annotations

from typing import Final

import pandas as pd


REQUIRED_COLUMNS: Final[tuple[str, ...]] = (
    "material_id",
    "carbon_footprint_kg_co2e",
)

DEFAULT_RECYCLING_EMISSION_RATIO: Final[float] = 0.30


def _validate_input(
    recommendations: pd.DataFrame,
) -> None:
    """Validate the environmental recommendation DataFrame."""

    if not isinstance(recommendations, pd.DataFrame):
        raise TypeError(
            "recommendations must be a pandas DataFrame."
        )

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in recommendations.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required columns for carbon savings calculation: "
            f"{missing_columns}"
        )

    if recommendations["material_id"].isna().any():
        raise ValueError(
            "material_id must not contain null values."
        )

    if not pd.api.types.is_numeric_dtype(
        recommendations["carbon_footprint_kg_co2e"]
    ):
        raise ValueError(
            "carbon_footprint_kg_co2e must be numeric."
        )

    if recommendations["carbon_footprint_kg_co2e"].isna().any():
        raise ValueError(
            "carbon_footprint_kg_co2e must not contain null values."
        )

    if (
        recommendations["carbon_footprint_kg_co2e"] < 0
    ).any():
        raise ValueError(
            "carbon_footprint_kg_co2e must be non-negative."
        )


def _validate_recycling_emission_ratio(
    recycling_emission_ratio: float,
) -> None:
    """Validate the recycling emission ratio."""

    if not isinstance(
        recycling_emission_ratio,
        (int, float),
    ):
        raise TypeError(
            "recycling_emission_ratio must be numeric."
        )

    if not 0 <= recycling_emission_ratio <= 1:
        raise ValueError(
            "recycling_emission_ratio must be between 0 and 1."
        )


def calculate_carbon_savings(
    recommendations: pd.DataFrame,
    recycling_emission_ratio: float = DEFAULT_RECYCLING_EMISSION_RATIO,
) -> pd.DataFrame:
    """
    Calculate carbon savings for each recommendation.

    Parameters
    ----------
    recommendations:
        DataFrame containing baseline carbon footprint values.

    recycling_emission_ratio:
        Estimated recycling/reuse emissions as a fraction of
        the baseline footprint.

        Example:
            0.30 means the recycling/reuse process produces
            30% of the baseline emissions.

    Returns
    -------
    pandas.DataFrame
        Input DataFrame enriched with:

        - recycling_footprint_kg_co2e
        - carbon_savings_kg_co2e
        - carbon_savings_percentage
    """

    _validate_input(recommendations)
    _validate_recycling_emission_ratio(
        recycling_emission_ratio
    )

    result = recommendations.copy()

    # Baseline carbon footprint comes from Module 4.3.
    result["recycling_footprint_kg_co2e"] = (
        result["carbon_footprint_kg_co2e"]
        * recycling_emission_ratio
    )

    # Carbon savings are the emissions avoided by recycling/reuse.
    result["carbon_savings_kg_co2e"] = (
        result["carbon_footprint_kg_co2e"]
        - result["recycling_footprint_kg_co2e"]
    )

    result["carbon_savings_percentage"] = 0.0

    baseline_mask = (
        result["carbon_footprint_kg_co2e"] != 0
    )

    result.loc[
        baseline_mask,
        "carbon_savings_percentage",
    ] = (
        result.loc[
            baseline_mask,
            "carbon_savings_kg_co2e",
        ]
        / result.loc[
            baseline_mask,
            "carbon_footprint_kg_co2e",
        ]
        * 100.0
    )

    result[
        [
            "recycling_footprint_kg_co2e",
            "carbon_savings_kg_co2e",
            "carbon_savings_percentage",
        ]
    ] = result[
        [
            "recycling_footprint_kg_co2e",
            "carbon_savings_kg_co2e",
            "carbon_savings_percentage",
        ]
    ].round(6)

    return result


def get_carbon_savings_summary(
    recommendations: pd.DataFrame,
    recycling_emission_ratio: float = DEFAULT_RECYCLING_EMISSION_RATIO,
) -> dict[str, float | int]:
    """
    Generate aggregate carbon-savings metrics.

    Returns
    -------
    dict
        Aggregate environmental metrics.
    """

    result = calculate_carbon_savings(
        recommendations,
        recycling_emission_ratio=recycling_emission_ratio,
    )

    total_baseline = float(
        result["carbon_footprint_kg_co2e"].sum()
    )

    total_recycling = float(
        result["recycling_footprint_kg_co2e"].sum()
    )

    total_savings = float(
        result["carbon_savings_kg_co2e"].sum()
    )

    savings_percentage = (
        total_savings / total_baseline * 100.0
        if total_baseline != 0
        else 0.0
    )

    return {
        "recommendation_count": int(len(result)),
        "total_baseline_carbon_kg_co2e": total_baseline,
        "total_recycling_carbon_kg_co2e": total_recycling,
        "total_carbon_savings_kg_co2e": total_savings,
        "carbon_savings_percentage": round(
            savings_percentage,
            6,
        ),
    }