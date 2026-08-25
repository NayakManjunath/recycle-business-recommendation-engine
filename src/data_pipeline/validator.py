from pathlib import Path
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONTRACTS_PATH = PROJECT_ROOT / "configs" / "data_contracts.json"


def load_data_contracts() -> dict:
    """Load the project's data contracts."""
    with CONTRACTS_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


def validate_dataframe(
    dataframe: pd.DataFrame,
    contract_name: str,
) -> None:
    """
    Validate a DataFrame against a configured data contract.

    Parameters
    ----------
    dataframe:
        DataFrame to validate.

    contract_name:
        Name of the data contract.

    Raises
    ------
    ValueError
        If the contract does not exist, the DataFrame is empty,
        required columns are missing, or column data types are invalid.
    """
    contracts = load_data_contracts()

    if contract_name not in contracts:
        raise ValueError(
            f"Unknown data contract: {contract_name}"
        )

    if dataframe.empty:
        raise ValueError(
            f"DataFrame is empty for contract: {contract_name}"
        )

    required_fields = contracts[contract_name]["required_fields"]

    missing_fields = [
        field
        for field in required_fields
        if field not in dataframe.columns
    ]

    if missing_fields:
        raise ValueError(
            f"Missing required fields for "
            f"{contract_name}: {missing_fields}"
        )

    for field, expected_type in required_fields.items():
        series = dataframe[field]

        if expected_type == "string":
            if not (
                pd.api.types.is_string_dtype(series)
                or series.dtype == object
            ):
                raise ValueError(
                    f"Field '{field}' must be a string."
                )

        elif expected_type == "number":
            if not pd.api.types.is_numeric_dtype(series):
                raise ValueError(
                    f"Field '{field}' must be numeric."
                )

        else:
            raise ValueError(
                f"Unsupported contract type '{expected_type}' "
                f"for field '{field}'."
            )