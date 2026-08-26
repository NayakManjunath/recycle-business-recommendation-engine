import pandas as pd


REQUIRED_MATERIAL_COLUMNS = {
    "material_id",
    "material_name",
    "quantity",
    "unit",
}

REQUIRED_PROCESS_COLUMNS = {
    "process_id",
    "process_name",
    "target_material",
}

REQUIRED_DEMAND_COLUMNS = {
    "demand_id",
    "material_name",
    "required_quantity",
    "unit",
}


def _validate_columns(
    dataframe: pd.DataFrame,
    required_columns: set[str],
    dataframe_name: str,
) -> None:
    missing = required_columns - set(dataframe.columns)

    if missing:
        raise ValueError(
            f"Missing required columns in {dataframe_name}: "
            f"{sorted(missing)}"
        )


def build_compatibility_features(
    material_df: pd.DataFrame,
    process_df: pd.DataFrame,
    demand_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Build compatibility features between material byproducts,
    recycling processes, and secondary market demand.
    """

    _validate_columns(
        material_df,
        REQUIRED_MATERIAL_COLUMNS,
        "material_df",
    )

    _validate_columns(
        process_df,
        REQUIRED_PROCESS_COLUMNS,
        "process_df",
    )

    _validate_columns(
        demand_df,
        REQUIRED_DEMAND_COLUMNS,
        "demand_df",
    )

    material = material_df.rename(
        columns={
            "material_name": "source_material_name",
            "quantity": "available_quantity",
            "unit": "source_unit",
        }
    ).copy()

    process = process_df.copy()

    demand = demand_df.rename(
        columns={
            "material_name": "demand_material_name",
            "required_quantity": "required_quantity",
            "unit": "demand_unit",
        }
    ).copy()

    material["_join_key"] = 1
    process["_join_key"] = 1
    demand["_join_key"] = 1

    candidates = material.merge(
        process,
        on="_join_key",
        how="inner",
    )

    candidates = candidates.merge(
        demand,
        on="_join_key",
        how="inner",
    )

    candidates.drop(columns="_join_key", inplace=True)

    candidates["material_process_match"] = (
        candidates["source_material_name"]
        .str.strip()
        .str.lower()
        == candidates["target_material"]
        .str.strip()
        .str.lower()
    )

    candidates["material_demand_match"] = (
        candidates["source_material_name"]
        .str.strip()
        .str.lower()
        == candidates["demand_material_name"]
        .str.strip()
        .str.lower()
    )

    candidates["quantity_coverage_ratio"] = (
        candidates["available_quantity"]
        / candidates["required_quantity"]
    )

    return candidates