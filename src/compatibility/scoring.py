"""Compatibility scoring utilities."""

from __future__ import annotations

import pandas as pd


PROCESS_MATCH_WEIGHT = 0.40
DEMAND_MATCH_WEIGHT = 0.40
QUANTITY_COVERAGE_WEIGHT = 0.20


REQUIRED_COLUMNS = [
    "material_process_match",
    "material_demand_match",
    "quantity_coverage_ratio",
]


def calculate_compatibility_score(
    features: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate a compatibility score from generated compatibility features.

    The score ranges from 0 to 100.

    Components:
    - Material-process match: 40%
    - Material-demand match: 40%
    - Quantity coverage: 20%
    """

    if not isinstance(features, pd.DataFrame):
        raise TypeError("features must be a pandas DataFrame.")

    if features.empty:
        raise ValueError("features DataFrame cannot be empty.")

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in features.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required scoring columns: {missing_columns}"
        )

    result = features.copy()

    process_score = (
        result["material_process_match"].astype(float)
    )

    demand_score = (
        result["material_demand_match"].astype(float)
    )

    quantity_score = (
        pd.to_numeric(
            result["quantity_coverage_ratio"],
            errors="raise",
        )
        .clip(lower=0, upper=1)
    )

    result["compatibility_score"] = (
        (
            PROCESS_MATCH_WEIGHT * process_score
            + DEMAND_MATCH_WEIGHT * demand_score
            + QUANTITY_COVERAGE_WEIGHT * quantity_score
        )
        * 100
    )

    result["compatibility_score"] = (
        result["compatibility_score"].round(2)
    )

    return result