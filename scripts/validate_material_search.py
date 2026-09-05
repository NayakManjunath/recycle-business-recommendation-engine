"""
Validate Module 7.2 Material Search Interface.

Checks:
- material-search component structure
- API client search functionality
- search/filter behavior
- case-insensitive behavior
- zero-result behavior
- combined filters
- API error handling
- Streamlit component imports
- presentation-layer separation
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.streamlit_app.api_client import (  # noqa: E402
    APIClient,
    APIClientError,
)
from src.streamlit_app.components.material_search import (  # noqa: E402
    _extract_material_rows,
    _extract_units,
    render_material_search,
)


PORTAL_ROOT = PROJECT_ROOT / "src" / "streamlit_app"
COMPONENT_PATH = (
    PORTAL_ROOT / "components" / "material_search.py"
)


def validate_component_structure() -> None:
    """Validate required 7.2 files and component entry point."""
    assert COMPONENT_PATH.exists(), (
        f"Missing material-search component: {COMPONENT_PATH}"
    )

    source = COMPONENT_PATH.read_text(encoding="utf-8")

    assert "def render_material_search" in source
    assert "APIClient" in source
    assert "search_materials" in source
    assert "st.text_input" in source
    assert "st.selectbox" in source
    assert "st.button" in source
    assert "st.dataframe" in source
    assert "st.metric" in source

    print("Material search component structure validation: PASSED")


def validate_component_helpers() -> None:
    """Validate material-search response helper behavior."""
    response = {
        "count": 3,
        "materials": [
            {
                "material_id": "MAT-001",
                "material_name": "Steel Scrap",
                "quantity": 1000,
                "unit": "kg",
            },
            {
                "material_id": "MAT-002",
                "material_name": "Aluminum Scrap",
                "quantity": 500,
                "unit": "kg",
            },
            {
                "material_id": "MAT-003",
                "material_name": "Plastic Waste",
                "quantity": 700,
                "unit": "kg",
            },
        ],
    }

    rows = _extract_material_rows(response)

    assert len(rows) == 3
    assert rows[0]["material_id"] == "MAT-001"

    units = _extract_units(response)

    assert units == ["kg"]

    assert _extract_material_rows({"materials": "invalid"}) == []
    assert _extract_material_rows({}) == []

    print("Material search helper validation: PASSED")


def validate_all_material_search() -> None:
    """Validate the unfiltered material search."""
    client = APIClient()

    response = client.search_materials()

    assert response["count"] == 3
    assert len(response["materials"]) == 3

    material_ids = {
        material["material_id"]
        for material in response["materials"]
    }

    assert material_ids == {
        "MAT-001",
        "MAT-002",
        "MAT-003",
    }

    print("All-material search validation: PASSED")


def validate_material_name_search() -> None:
    """Validate material-name search behavior."""
    client = APIClient()

    response = client.search_materials(
        material_name="steel",
    )

    assert response["count"] == 1
    assert response["materials"][0]["material_id"] == "MAT-001"

    print("Material-name search validation: PASSED")


def validate_case_insensitive_search() -> None:
    """Validate case-insensitive material-name search."""
    client = APIClient()

    lowercase = client.search_materials(
        material_name="steel",
    )

    uppercase = client.search_materials(
        material_name="STEEL",
    )

    mixed_case = client.search_materials(
        material_name="StEeL",
    )

    assert lowercase == uppercase
    assert lowercase == mixed_case

    print("Case-insensitive search validation: PASSED")


def validate_unit_filter() -> None:
    """Validate unit filtering."""
    client = APIClient()

    response = client.search_materials(
        unit="kg",
    )

    assert response["count"] == 3

    for material in response["materials"]:
        assert material["unit"].lower() == "kg"

    print("Unit filter validation: PASSED")


def validate_combined_filter() -> None:
    """Validate material-name and unit filtering together."""
    client = APIClient()

    response = client.search_materials(
        material_name="steel",
        unit="kg",
    )

    assert response["count"] == 1

    material = response["materials"][0]

    assert material["material_id"] == "MAT-001"
    assert material["material_name"] == "Steel Scrap"
    assert material["unit"] == "kg"

    print("Combined filter validation: PASSED")


def validate_zero_result() -> None:
    """Validate graceful handling of zero matching records."""
    client = APIClient()

    response = client.search_materials(
        material_name="xyz",
    )

    assert response["count"] == 0
    assert response["materials"] == []

    print("Zero-result validation: PASSED")


def validate_api_error_handling() -> None:
    """Validate that backend failures become APIClientError."""
    client = APIClient(
        base_url="http://127.0.0.1:59999",
        timeout=1.0,
    )

    try:
        client.search_materials()
    except APIClientError:
        print("API error handling validation: PASSED")
        return

    raise AssertionError(
        "APIClientError was not raised for unavailable backend."
    )


def validate_component_import() -> None:
    """Validate the Streamlit component entry point."""
    assert callable(render_material_search)

    print("Material search component import validation: PASSED")


def validate_presentation_layer_separation() -> None:
    """
    Ensure the Streamlit component does not duplicate backend
    data-loading or recommendation/environmental business logic.
    """
    source = COMPONENT_PATH.read_text(encoding="utf-8")

    tree = ast.parse(source)

    forbidden_calls = {
        "load_csv",
        "validate_dataframe",
        "validate_data_quality",
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                assert node.func.id not in forbidden_calls, (
                    f"Backend data-pipeline logic duplicated in "
                    f"Streamlit component: {node.func.id}"
                )

            if isinstance(node.func, ast.Attribute):
                assert node.func.attr not in forbidden_calls, (
                    f"Backend data-pipeline logic duplicated in "
                    f"Streamlit component: {node.func.attr}"
                )

    forbidden_terms = [
        "carbon_savings_kg_co2e",
        "compatibility_score",
        "calculate_carbon",
    ]

    for term in forbidden_terms:
        assert term not in source, (
            f"Backend business logic detected in Streamlit "
            f"component: {term}"
        )

    print("Presentation-layer separation validation: PASSED")


def main() -> None:
    """Run the complete Module 7.2 validation suite."""
    validate_component_structure()
    validate_component_helpers()
    validate_all_material_search()
    validate_material_name_search()
    validate_case_insensitive_search()
    validate_unit_filter()
    validate_combined_filter()
    validate_zero_result()
    validate_api_error_handling()
    validate_component_import()
    validate_presentation_layer_separation()

    print()
    print("MODULE 7.2 MATERIAL SEARCH VALIDATION PASSED")


if __name__ == "__main__":
    main()