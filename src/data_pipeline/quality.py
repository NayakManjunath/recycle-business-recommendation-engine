import pandas as pd


def validate_data_quality(
    dataframe: pd.DataFrame,
    id_column: str,
    quantity_columns: list[str] | None = None,
) -> None:
    """
    Validate basic data-quality rules for a DataFrame.

    Parameters
    ----------
    dataframe:
        DataFrame to validate.

    id_column:
        Column containing the record identifier.

    quantity_columns:
        Numeric quantity columns that must contain positive values.

    Raises
    ------
    ValueError
        If the DataFrame contains null values, duplicate IDs,
        or invalid quantity values.
    """
    if dataframe.empty:
        raise ValueError("Data quality validation failed: DataFrame is empty.")

    if id_column not in dataframe.columns:
        raise ValueError(
            f"Data quality validation failed: ID column '{id_column}' is missing."
        )

    if dataframe.isnull().any().any():
        null_columns = dataframe.columns[dataframe.isnull().any()].tolist()
        raise ValueError(
            f"Data quality validation failed: null values found in {null_columns}."
        )

    if dataframe[id_column].duplicated().any():
        duplicate_ids = (
            dataframe.loc[
                dataframe[id_column].duplicated(keep=False),
                id_column,
            ]
            .tolist()
        )

        raise ValueError(
            f"Data quality validation failed: duplicate IDs found: {duplicate_ids}."
        )

    if quantity_columns:
        for column in quantity_columns:
            if column not in dataframe.columns:
                raise ValueError(
                    f"Data quality validation failed: "
                    f"quantity column '{column}' is missing."
                )

            if not pd.api.types.is_numeric_dtype(dataframe[column]):
                raise ValueError(
                    f"Data quality validation failed: "
                    f"quantity column '{column}' must be numeric."
                )

            if (dataframe[column] <= 0).any():
                raise ValueError(
                    f"Data quality validation failed: "
                    f"quantity column '{column}' must contain positive values."
                )
