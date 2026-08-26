"""Compatibility ranking utilities."""

from __future__ import annotations

import pandas as pd


REQUIRED_COLUMNS = [
    "compatibility_score",
    "quantity_coverage_ratio",
]


def rank_compatibility_results(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rank compatibility candidates from best to worst.

    Primary ranking criterion:
        compatibility_score descending

    Secondary ranking criterion:
        quantity_coverage_ratio descending

    Returns:
        A new DataFrame containing the original columns plus `rank`.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Cannot rank an empty DataFrame.")

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns for ranking: {missing_columns}"
        )

    if df["compatibility_score"].isna().any():
        raise ValueError(
            "compatibility_score must not contain null values."
        )

    if df["quantity_coverage_ratio"].isna().any():
        raise ValueError(
            "quantity_coverage_ratio must not contain null values."
        )

    if not pd.api.types.is_numeric_dtype(df["compatibility_score"]):
        raise ValueError(
            "compatibility_score must be numeric."
        )

    if not pd.api.types.is_numeric_dtype(
        df["quantity_coverage_ratio"]
    ):
        raise ValueError(
            "quantity_coverage_ratio must be numeric."
        )

    ranked = (
        df.copy()
        .sort_values(
            by=[
                "compatibility_score",
                "quantity_coverage_ratio",
            ],
            ascending=[
                False,
                False,
            ],
            kind="stable",
        )
        .reset_index(drop=True)
    )

    ranked.insert(0, "rank", range(1, len(ranked) + 1))

    return ranked