"""
Validate the Module 6.2 material search endpoint.

Checks:
- Material search route availability
- All-material search
- Material-name filtering
- Case-insensitive material search
- Unit filtering
- Combined filtering
- Zero-result behavior
- Response structure
"""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.main import app


EXPECTED_ROUTE = "/materials/search"

EXPECTED_MATERIAL_FIELDS = {
    "material_id",
    "material_name",
    "quantity",
    "unit",
}


def validate_response_structure(response) -> None:
    """Validate the common material-search response structure."""
    assert response.status_code == 200

    payload = response.json()

    assert "count" in payload
    assert "materials" in payload
    assert isinstance(payload["count"], int)
    assert isinstance(payload["materials"], list)
    assert payload["count"] == len(payload["materials"])

    for material in payload["materials"]:
        assert set(material.keys()) == EXPECTED_MATERIAL_FIELDS


def validate_route_availability(client: TestClient) -> None:
    """Validate that the material search route is reachable."""
    response = client.get(EXPECTED_ROUTE)

    assert response.status_code == 200, (
        f"{EXPECTED_ROUTE} returned HTTP {response.status_code}"
    )

    validate_response_structure(response)


def validate_all_materials(client: TestClient) -> None:
    """Validate search without filters."""
    response = client.get(EXPECTED_ROUTE)

    validate_response_structure(response)

    payload = response.json()

    assert payload["count"] == 3


def validate_material_name_filter(client: TestClient) -> None:
    """Validate material-name filtering."""
    response = client.get(
        EXPECTED_ROUTE,
        params={"material_name": "steel"},
    )

    validate_response_structure(response)

    payload = response.json()

    assert payload["count"] == 1
    assert payload["materials"][0]["material_id"] == "MAT-001"
    assert payload["materials"][0]["material_name"] == "Steel Scrap"


def validate_case_insensitive_search(client: TestClient) -> None:
    """Validate case-insensitive material-name search."""
    response = client.get(
        EXPECTED_ROUTE,
        params={"material_name": "STEEL"},
    )

    validate_response_structure(response)

    payload = response.json()

    assert payload["count"] == 1
    assert payload["materials"][0]["material_id"] == "MAT-001"


def validate_unit_filter(client: TestClient) -> None:
    """Validate unit filtering."""
    response = client.get(
        EXPECTED_ROUTE,
        params={"unit": "kg"},
    )

    validate_response_structure(response)

    payload = response.json()

    assert payload["count"] == 3

    assert all(
        material["unit"].lower() == "kg"
        for material in payload["materials"]
    )


def validate_combined_filter(client: TestClient) -> None:
    """Validate combined material-name and unit filtering."""
    response = client.get(
        EXPECTED_ROUTE,
        params={
            "material_name": "steel",
            "unit": "kg",
        },
    )

    validate_response_structure(response)

    payload = response.json()

    assert payload["count"] == 1
    assert payload["materials"][0]["material_id"] == "MAT-001"


def validate_zero_result(client: TestClient) -> None:
    """Validate a valid search with no matching materials."""
    response = client.get(
        EXPECTED_ROUTE,
        params={"material_name": "nonexistent-material"},
    )

    validate_response_structure(response)

    payload = response.json()

    assert payload["count"] == 0
    assert payload["materials"] == []


def validate_query_validation(client: TestClient) -> None:
    """Validate FastAPI query parameter validation."""
    response = client.get(
        EXPECTED_ROUTE,
        params={"material_name": ""},
    )

    assert response.status_code == 422


def main() -> None:
    """Run all Module 6.2 validation checks."""

    with TestClient(app) as client:
        validate_route_availability(client)
        print("Material search route validation: PASSED")

        validate_all_materials(client)
        print("All-material search validation: PASSED")

        validate_material_name_filter(client)
        print("Material-name filter validation: PASSED")

        validate_case_insensitive_search(client)
        print("Case-insensitive search validation: PASSED")

        validate_unit_filter(client)
        print("Unit filter validation: PASSED")

        validate_combined_filter(client)
        print("Combined filter validation: PASSED")

        validate_zero_result(client)
        print("Zero-result validation: PASSED")

        validate_query_validation(client)
        print("Query parameter validation: PASSED")

    print()
    print("MODULE 6.2 MATERIAL SEARCH VALIDATION PASSED")


if __name__ == "__main__":
    main()
