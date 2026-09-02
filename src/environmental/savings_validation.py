"""
Savings Validation
------------------

Module 5.5

Final validation layer for the Carbon Footprint Savings Engine.

This module validates the complete environmental savings pipeline:

5.1 Baseline Environmental Metrics
5.2 Recycling-Loop Metrics
5.3 Carbon Savings Calculation
5.4 Environmental Savings Integration

This module intentionally does not perform the calculations itself.
It validates the outputs produced by the previous stages.
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


def validate_savings_metrics(
    environmental_savings: pd.DataFrame,
) -> dict[str, Any]:
    """
    Validate the complete environmental savings dataset.

    Parameters
    ----------
    environmental_savings:
        Output produced by the environmental savings integration layer.

    Returns
    -------
    dict[str, Any]
        Validation result containing status and validation checks.
    """

    if not isinstance(environmental_savings, pd.DataFrame):
        raise TypeError(
            "environmental_savings must be a pandas DataFrame."
        )

    if environmental_savings.empty:
        raise ValueError(
            "environmental_savings must contain at least one row."
        )

    # ---------------------------------------------------------
    # 1. Structural validation
    # ---------------------------------------------------------

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in environmental_savings.columns
    ]

    if missing_columns:
        raise ValueError(
            "environmental_savings is missing required columns: "
            f"{missing_columns}"
        )

    if environmental_savings["material_id"].isna().any():
        raise ValueError(
            "material_id cannot contain null values."
        )

    if environmental_savings["material_name"].isna().any():
        raise ValueError(
            "material_name cannot contain null values."
        )

    if environmental_savings["unit"].isna().any():
        raise ValueError(
            "unit cannot contain null values."
        )

    if environmental_savings["material_id"].duplicated().any():
        raise ValueError(
            "material_id values must be unique."
        )

    # ---------------------------------------------------------
    # 2. Numeric validation
    # ---------------------------------------------------------

    numeric_columns = [
        "quantity",
        "baseline_carbon_footprint_kg_co2e",
        "recycling_loop_footprint_kg_co2e",
        "carbon_savings_kg_co2e",
        "carbon_savings_percentage",
    ]

    for column in numeric_columns:
        if not pd.api.types.is_numeric_dtype(
            environmental_savings[column]
        ):
            raise ValueError(
                f"{column} must be numeric."
            )

        if environmental_savings[column].isna().any():
            raise ValueError(
                f"{column} cannot contain null values."
            )

    # ---------------------------------------------------------
    # 3. Environmental sanity validation
    # ---------------------------------------------------------

    non_negative_columns = [
        "quantity",
        "baseline_carbon_footprint_kg_co2e",
        "recycling_loop_footprint_kg_co2e",
        "carbon_savings_kg_co2e",
        "carbon_savings_percentage",
    ]

    for column in non_negative_columns:
        if (environmental_savings[column] < 0).any():
            raise ValueError(
                f"{column} must be non-negative."
            )

    if (
        environmental_savings["carbon_savings_percentage"] > 100
    ).any():
        raise ValueError(
            "carbon_savings_percentage cannot exceed 100."
        )

    # Recycling footprint cannot exceed baseline footprint
    # when carbon savings are expected to be non-negative.
    if (
        environmental_savings[
            "recycling_loop_footprint_kg_co2e"
        ]
        > environmental_savings[
            "baseline_carbon_footprint_kg_co2e"
        ]
    ).any():
        raise ValueError(
            "recycling-loop footprint cannot exceed baseline "
            "footprint when savings are non-negative."
        )

    # ---------------------------------------------------------
    # 4. Calculation consistency
    # ---------------------------------------------------------

    expected_savings = (
        environmental_savings[
            "baseline_carbon_footprint_kg_co2e"
        ]
        - environmental_savings[
            "recycling_loop_footprint_kg_co2e"
        ]
    )

    if not expected_savings.round(10).equals(
        environmental_savings[
            "carbon_savings_kg_co2e"
        ].round(10)
    ):
        raise ValueError(
            "carbon_savings_kg_co2e is inconsistent with "
            "baseline and recycling-loop footprints."
        )

    expected_percentage = pd.Series(
        0.0,
        index=environmental_savings.index,
    )

    non_zero_baseline = (
        environmental_savings[
            "baseline_carbon_footprint_kg_co2e"
        ]
        > 0
    )

    expected_percentage.loc[non_zero_baseline] = (
        environmental_savings.loc[
            non_zero_baseline,
            "carbon_savings_kg_co2e",
        ]
        / environmental_savings.loc[
            non_zero_baseline,
            "baseline_carbon_footprint_kg_co2e",
        ]
        * 100
    )

    if not expected_percentage.round(10).equals(
        environmental_savings[
            "carbon_savings_percentage"
        ].round(10)
    ):
        raise ValueError(
            "carbon_savings_percentage is inconsistent "
            "with carbon savings and baseline footprint."
        )

    # ---------------------------------------------------------
    # 5. Validation result
    # ---------------------------------------------------------

    return {
        "status": "PASSED",
        "material_count": int(
            len(environmental_savings)
        ),
        "total_quantity": float(
            environmental_savings["quantity"].sum()
        ),
        "total_baseline_carbon_footprint_kg_co2e": float(
            environmental_savings[
                "baseline_carbon_footprint_kg_co2e"
            ].sum()
        ),
        "total_recycling_loop_footprint_kg_co2e": float(
            environmental_savings[
                "recycling_loop_footprint_kg_co2e"
            ].sum()
        ),
        "total_carbon_savings_kg_co2e": float(
            environmental_savings[
                "carbon_savings_kg_co2e"
            ].sum()
        ),
    }


def validate_savings_summary(
    environmental_savings: pd.DataFrame,
    summary: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate the aggregate environmental savings summary
    against the underlying material-level dataset.
    """

    if not isinstance(summary, dict):
        raise TypeError("summary must be a dictionary.")

    expected_material_count = int(
        len(environmental_savings)
    )

    expected_quantity = float(
        environmental_savings["quantity"].sum()
    )

    expected_baseline = float(
        environmental_savings[
            "baseline_carbon_footprint_kg_co2e"
        ].sum()
    )

    expected_recycling = float(
        environmental_savings[
            "recycling_loop_footprint_kg_co2e"
        ].sum()
    )

    expected_savings = float(
        environmental_savings[
            "carbon_savings_kg_co2e"
        ].sum()
    )

    if expected_baseline == 0:
        expected_percentage = 0.0
    else:
        expected_percentage = (
            expected_savings / expected_baseline
        ) * 100

    checks = {
        "material_count": (
            summary.get("material_count")
            == expected_material_count
        ),
        "total_quantity": (
            summary.get("total_quantity")
            == expected_quantity
        ),
        "baseline_footprint": (
            summary.get(
                "total_baseline_carbon_footprint_kg_co2e"
            )
            == expected_baseline
        ),
        "recycling_footprint": (
            summary.get(
                "total_recycling_loop_footprint_kg_co2e"
            )
            == expected_recycling
        ),
        "carbon_savings": (
            summary.get(
                "total_carbon_savings_kg_co2e"
            )
            == expected_savings
        ),
        "savings_percentage": (
            summary.get(
                "overall_carbon_savings_percentage"
            )
            == expected_percentage
        ),
    }

    failed_checks = [
        check
        for check, passed in checks.items()
        if not passed
    ]

    if failed_checks:
        raise ValueError(
            "Savings summary validation failed: "
            f"{failed_checks}"
        )

    return {
        "status": "PASSED",
        "checks": checks,
    }


def validate_environmental_savings_pipeline(
    environmental_savings: pd.DataFrame,
    summary: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute the final Module 5 validation gate.

    Returns a consolidated validation result.
    """

    metrics_result = validate_savings_metrics(
        environmental_savings
    )

    summary_result = validate_savings_summary(
        environmental_savings,
        summary,
    )

    return {
        "status": "PASSED",
        "metrics_validation": metrics_result,
        "summary_validation": summary_result,
    }