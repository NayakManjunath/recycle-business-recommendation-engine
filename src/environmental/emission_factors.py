from pathlib import Path

import pandas as pd


DEFAULT_EMISSION_FACTOR_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "sample"
    / "emission_factors.csv"
)

REQUIRED_COLUMNS = {
    "material_name",
    "emission_factor",
    "unit",
}


def load_emission_factors(
    path: str | Path = DEFAULT_EMISSION_FACTOR_PATH,
) -> pd.DataFrame:
    """
    Load and validate material-level carbon emission factors.

    Expected unit:
        kg_co2e_per_kg
    """
    csv_path = Path(path)

    if not csv_path.exists():
        raise FileNotFoundError(
            f"Emission factor file not found: {csv_path}"
        )

    df = pd.read_csv(csv_path)

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            "Missing required columns in emission factor data: "
            f"{sorted(missing_columns)}"
        )

    if df.empty:
        raise ValueError("Emission factor data cannot be empty.")

    df["emission_factor"] = pd.to_numeric(
        df["emission_factor"],
        errors="coerce",
    )

    if df["emission_factor"].isna().any():
        raise ValueError(
            "emission_factor must contain only numeric values."
        )

    if (df["emission_factor"] < 0).any():
        raise ValueError(
            "emission_factor must contain non-negative values."
        )

    if df["material_name"].isna().any():
        raise ValueError(
            "material_name cannot contain missing values."
        )

    if df["material_name"].duplicated().any():
        duplicates = (
            df.loc[
                df["material_name"].duplicated(),
                "material_name",
            ]
            .tolist()
        )

        raise ValueError(
            f"Duplicate material emission factors found: {duplicates}"
        )

    return df


def get_emission_factor(
    material_name: str,
    path: str | Path = DEFAULT_EMISSION_FACTOR_PATH,
) -> float:
    """
    Return the emission factor for a material.

    The returned value represents:
        kg CO2e per kg material
    """
    if not isinstance(material_name, str) or not material_name.strip():
        raise ValueError(
            "material_name must be a non-empty string."
        )

    df = load_emission_factors(path)

    matches = df[
        df["material_name"].str.casefold()
        == material_name.strip().casefold()
    ]

    if matches.empty:
        raise ValueError(
            f"No emission factor found for material: {material_name}"
        )

    return float(matches.iloc[0]["emission_factor"])