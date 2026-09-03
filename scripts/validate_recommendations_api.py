"""
Validate the Module 6.3 compatibility recommendation endpoint.

Checks:
- Recommendation endpoint availability
- HTTP response status
- Response structure
- Recommendation fields
- Recommendation count
- Ranking order
- Compatibility score bounds
- Quantity coverage values
- Expected sample recommendations
- OpenAPI response schema
"""

from __future__ import annotations

from pathlib import Path
import sys

from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.main import app


EXPECTED_ROUTE = "/recommendations"

EXPECTED_FIELDS = {
    "rank",
    "material_id",
    "source_material_name",
    "process_id",
    "process_name",
    "target_material",
    "demand_id",
    "demand_material_name",
    "compatibility_score",
    "quantity_coverage_ratio",
}

EXPECTED_MATERIAL_IDS = [
    "MAT-001",
    "MAT-002",
    "MAT-003",
]


def validate_response_structure(response) -> dict:
    """Validate the top-level recommendation response."""
    assert response.status_code == 200, (
        f"{EXPECTED_ROUTE} returned HTTP {response.status_code}"
    )

    payload = response.json()

    assert isinstance(payload, dict)
    assert "count" in payload
    assert "recommendations" in payload

    assert isinstance(payload["count"], int)
    assert payload["count"] >= 0

    assert isinstance(payload["recommendations"], list)
    assert payload["count"] == len(payload["recommendations"])

    return payload


def validate_recommendation_fields(payload: dict) -> None:
    """Validate fields and basic value constraints."""
    for recommendation in payload["recommendations"]:
        assert set(recommendation.keys()) == EXPECTED_FIELDS

        assert isinstance(recommendation["rank"], int)
        assert recommendation["rank"] >= 1

        assert isinstance(recommendation["material_id"], str)
        assert recommendation["material_id"]

        assert isinstance(recommendation["source_material_name"], str)
        assert recommendation["source_material_name"]

        assert isinstance(recommendation["process_id"], str)
        assert recommendation["process_id"]

        assert isinstance(recommendation["process_name"], str)
        assert recommendation["process_name"]

        assert isinstance(recommendation["target_material"], str)
        assert recommendation["target_material"]

        assert isinstance(recommendation["demand_id"], str)
        assert recommendation["demand_id"]

        assert isinstance(recommendation["demand_material_name"], str)
        assert recommendation["demand_material_name"]

        assert 0 <= recommendation["compatibility_score"] <= 100

        assert recommendation["quantity_coverage_ratio"] >= 0


def validate_ranking(payload: dict) -> None:
    """Validate sequential recommendation ranking."""
    ranks = [
        recommendation["rank"]
        for recommendation in payload["recommendations"]
    ]

    expected_ranks = list(range(1, len(ranks) + 1))

    assert ranks == expected_ranks, (
        f"Invalid ranking sequence: {ranks}"
    )


def validate_expected_sample_data(payload: dict) -> None:
    """Validate the expected sample recommendation results."""
    material_ids = [
        recommendation["material_id"]
        for recommendation in payload["recommendations"]
    ]

    assert material_ids == EXPECTED_MATERIAL_IDS

    assert payload["recommendations"][0]["source_material_name"] == (
        "Steel Scrap"
    )

    assert payload["recommendations"][1]["source_material_name"] == (
        "Aluminum Scrap"
    )

    assert payload["recommendations"][2]["source_material_name"] == (
        "Plastic Waste"
    )

    assert all(
        recommendation["compatibility_score"] == 100.0
        for recommendation in payload["recommendations"]
    )


def validate_openapi_contract(client: TestClient) -> None:
    """Validate the documented response schema."""
    response = client.get("/openapi.json")

    assert response.status_code == 200

    openapi = response.json()

    recommendation_schema = (
        openapi["paths"]
        [EXPECTED_ROUTE]
        ["get"]
        ["responses"]
        ["200"]
        ["content"]
        ["application/json"]
        ["schema"]
    )

    assert recommendation_schema == {
        "$ref": "#/components/schemas/RecommendationResponse"
    }

    assert "RecommendationResponse" in (
        openapi["components"]["schemas"]
    )

    assert "Recommendation" in (
        openapi["components"]["schemas"]
    )


def main() -> None:
    with TestClient(app) as client:
        payload = validate_response_structure(
            client.get(EXPECTED_ROUTE)
        )
        print("Recommendation endpoint validation: PASSED")

        validate_recommendation_fields(payload)
        print("Recommendation field validation: PASSED")

        validate_ranking(payload)
        print("Recommendation ranking validation: PASSED")

        validate_expected_sample_data(payload)
        print("Expected sample recommendation validation: PASSED")

        validate_openapi_contract(client)
        print("OpenAPI response contract validation: PASSED")

    print()
    print("MODULE 6.3 COMPATIBILITY RECOMMENDATION VALIDATION PASSED")


if __name__ == "__main__":
    main()
