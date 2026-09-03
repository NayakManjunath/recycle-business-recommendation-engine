"""
Material Search API.

Module 6.2
----------
Provides material search functionality using the existing
material-byproduct data pipeline and data contracts.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Query

from src.data_pipeline.loader import load_csv
from src.data_pipeline.quality import validate_data_quality
from src.data_pipeline.validator import validate_dataframe


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MATERIALS_PATH = (
    PROJECT_ROOT
    / "data"
    / "sample"
    / "material_byproducts.csv"
)


router = APIRouter(
    prefix="/materials",
    tags=["Materials"],
)


def load_materials():
    """
    Load and validate material-byproduct data.

    Returns
    -------
    pandas.DataFrame
        Validated material records.
    """
    materials = load_csv(MATERIALS_PATH)

    validate_dataframe(
        materials,
        "material_byproduct",
    )

    validate_data_quality(
        materials,
        id_column="material_id",
        quantity_columns=["quantity"],
    )

    return materials


def search_materials(
    material_name: str | None = None,
    unit: str | None = None,
) -> dict[str, Any]:
    """
    Search material-byproduct records.

    Parameters
    ----------
    material_name:
        Optional case-insensitive material-name search term.

    unit:
        Optional case-insensitive unit filter.

    Returns
    -------
    dict
        API-friendly material search response.
    """
    materials = load_materials()

    results = materials.copy()

    if material_name:
        search_term = material_name.strip().lower()

        results = results[
            results["material_name"]
            .astype(str)
            .str.lower()
            .str.contains(
                search_term,
                regex=False,
                na=False,
            )
        ]

    if unit:
        requested_unit = unit.strip().lower()

        results = results[
            results["unit"]
            .astype(str)
            .str.lower()
            .eq(requested_unit)
        ]

    columns = [
        "material_id",
        "material_name",
        "quantity",
        "unit",
    ]

    records = results[columns].to_dict(
        orient="records"
    )

    return {
        "count": len(records),
        "materials": records,
    }


@router.get("/search")
def material_search_endpoint(
    material_name: str | None = Query(
        default=None,
        min_length=1,
        description="Case-insensitive material name search term.",
    ),
    unit: str | None = Query(
        default=None,
        min_length=1,
        description="Case-insensitive material unit filter.",
    ),
) -> dict[str, Any]:
    """Search material-byproduct records."""
    return search_materials(
        material_name=material_name,
        unit=unit,
    )
