"""
Environmental impact integration.

Module 4.3
----------
Integrates the carbon-footprint results produced by Module 4.2
into the compatibility recommendation pipeline.
"""

from __future__ import annotations

from typing import Final

import pandas as pd

from src.environmental.carbon_footprint import calculate_carbon_footprint


REQUIRED_RECOMMENDATION_COLUMNS: Final[tuple[str, ...]] = (
    "material_id",
    "source_material_name",
    "available_quantity",
)

CARBON_COLUMNS: Final[tuple[str, ...]] = (
    "material_id",
    "emission_factor",
    "carbon_footprint_kg_co2e",
)

OUTPUT_COLUMNS: Final[tuple[str, ...]] = (
    "emission_factor",
    "carbon_footprint_kg_co2e",
)


def _validate_recommendations(
    recommendations: pd.DataFrame,
) -> None:
    """Validate the recommendation DataFrame."""
    if not isinstance(recommendations, pd.DataFrame):
        raise TypeError(
            "recommendations must be a pandas DataFrame."
        )

    missing_columns = [
        column
        for column in REQUIRED_RECOMMENDATION_COLUMNS
        if column not in recommendations.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required recommendation columns: "
            f"{missing_columns}"
        )

    if recommendations["material_id"].isna().any():
        raise ValueError(
            "material_id must not contain null values."
        )

    if recommendations["source_material_name"].isna().any():
        raise ValueError(
            "source_material_name must not contain null values."
        )

    if not pd.api.types.is_numeric_dtype(
        recommendations["available_quantity"]
    ):
        raise ValueError(
            "available_quantity must be numeric."
        )

    if recommendations["available_quantity"].isna().any():
        raise ValueError(
            "available_quantity must not contain null values."
        )

    if (recommendations["available_quantity"] < 0).any():
        raise ValueError(
            "available_quantity must be non-negative."
        )


def _validate_carbon_data(
    carbon_data: pd.DataFrame,
) -> None:
    """Validate carbon-footprint output from Module 4.2."""
    if not isinstance(carbon_data, pd.DataFrame):
        raise TypeError(
            "carbon_data must be a pandas DataFrame."
        )

    missing_columns = [
        column
        for column in CARBON_COLUMNS
        if column not in carbon_data.columns
    ]

    if missing_columns:
        raise ValueError(
            "Missing required carbon-footprint columns: "
            f"{missing_columns}"
        )

    if carbon_data["material_id"].duplicated().any():
        raise ValueError(
            "carbon_data must contain one row per material_id."
        )

    if carbon_data["emission_factor"].isna().any():
        raise ValueError(
            "emission_factor must not contain null values."
        )

    if carbon_data["carbon_footprint_kg_co2e"].isna().any():
        raise ValueError(
            "carbon_footprint_kg_co2e must not contain null values."
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

    if (carbon_data["carbon_footprint_kg_co2e"] < 0).any():
        raise ValueError(
            "carbon_footprint_kg_co2e must be non-negative."
        )


def integrate_environmental_impact(
    recommendations: pd.DataFrame,
) -> pd.DataFrame:
    """
    Enrich recommendations with carbon-footprint information.

    The function uses the existing Module 4.2 carbon-footprint
    implementation as the single source of truth.

    Parameters
    ----------
    recommendations:
        Filtered compatibility recommendations.

    Returns
    -------
    pandas.DataFrame
        Recommendations enriched with emission factor and
        carbon-footprint metrics.

    Raises
    ------
    TypeError
        If recommendations is not a pandas DataFrame.
    ValueError
        If input validation or carbon-data integration fails.
    """
    _validate_recommendations(recommendations)

    # Calculate environmental metrics using the existing
    # Module 4.2 implementation.
    material_input = recommendations[
        ["material_id", "source_material_name", "available_quantity"]
    ].copy()

    material_input = material_input.rename(
        columns={
            "source_material_name": "material_name",
            "available_quantity": "quantity",
        }
    )

    material_input["unit"] = "kg"

    carbon_data = calculate_carbon_footprint(material_input)

    _validate_carbon_data(carbon_data)

    # Keep only the environmental metrics needed by the
    # recommendation layer.
    carbon_data = carbon_data[
        [
            "material_id",
            "emission_factor",
            "carbon_footprint_kg_co2e",
        ]
    ].copy()

    # Merge environmental metrics back into recommendations.
    result = recommendations.merge(
        carbon_data,
        on="material_id",
        how="left",
        validate="many_to_one",
    )

    # Fail explicitly rather than silently returning incomplete
    # environmental information.
    if result["emission_factor"].isna().any():
        missing_materials = (
            result.loc[
                result["emission_factor"].isna(),
                "material_id",
            ]
            .drop_duplicates()
            .tolist()
        )

        raise ValueError(
            "Environmental impact data missing for material_id(s): "
            f"{missing_materials}"
        )

    if result["carbon_footprint_kg_co2e"].isna().any():
        raise ValueError(
            "Carbon footprint calculation produced null values."
        )

    return result


def get_environmental_summary(
    recommendations: pd.DataFrame,
) -> dict[str, float | int]:
    """
    Generate aggregate environmental metrics.

    Parameters
    ----------
    recommendations:
        Filtered compatibility recommendations.

    Returns
    -------
    dict
        Aggregate environmental summary.
    """
    enriched = integrate_environmental_impact(recommendations)

    return {
        "recommendation_count": int(len(enriched)),
        "total_available_quantity": float(
            enriched["available_quantity"].sum()
        ),
        "total_carbon_footprint_kg_co2e": float(
            enriched["carbon_footprint_kg_co2e"].sum()
        ),
    }