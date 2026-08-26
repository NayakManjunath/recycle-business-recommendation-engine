"""Recommendation filtering for compatibility results."""

from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = [
    "compatibility_score",
    "quantity_coverage_ratio",
]


def filter_recommendations(
    df: pd.DataFrame,
    min_score: float = 70.0,
    min_coverage_ratio: float = 1.0,
) -> pd.DataFrame:
    """
    Filter compatibility results using business thresholds.

    Parameters
    ----------
    df : pd.DataFrame
        Ranked compatibility results.

    min_score : float, default=70.0
        Minimum compatibility score required.

    min_coverage_ratio : float, default=1.0
        Minimum quantity coverage ratio required.

    Returns
    -------
    pd.DataFrame
        Filtered recommendations while preserving the
        original ranking/order.

    Raises
    ------
    ValueError
        If required columns are missing, thresholds are invalid,
        or score/coverage values are non-numeric.
    """

    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame.")

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns for recommendation filtering: "
            f"{missing_columns}"
        )

    if not isinstance(min_score, (int, float)):
        raise ValueError("min_score must be numeric.")

    if not isinstance(min_coverage_ratio, (int, float)):
        raise ValueError("min_coverage_ratio must be numeric.")

    if min_score < 0 or min_score > 100:
        raise ValueError("min_score must be between 0 and 100.")

    if min_coverage_ratio < 0:
        raise ValueError("min_coverage_ratio must be non-negative.")

    if not pd.api.types.is_numeric_dtype(df["compatibility_score"]):
        raise ValueError("compatibility_score must be numeric.")

    if not pd.api.types.is_numeric_dtype(
        df["quantity_coverage_ratio"]
    ):
        raise ValueError("quantity_coverage_ratio must be numeric.")

    filtered = df[
        (df["compatibility_score"] >= min_score)
        & (df["quantity_coverage_ratio"] >= min_coverage_ratio)
    ].copy()

    return filtered.reset_index(drop=True)