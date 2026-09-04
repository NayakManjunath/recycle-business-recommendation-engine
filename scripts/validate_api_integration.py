"""
API Integration Validation.

Module 6.5
----------
Validates the complete FastAPI application as an integrated system.

This validator covers:
- application and route registration
- root and health endpoints
- material search
- compatibility recommendations
- environmental savings
- cross-endpoint consistency
- validation/error handling
- OpenAPI response contracts
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Project root
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.main import app  # noqa: E402


# ---------------------------------------------------------------------------
# Test client
# ---------------------------------------------------------------------------

client = TestClient(app)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EXPECTED_ROUTES = {
    ("/", "GET"),
    ("/health", "GET"),
    ("/materials/search", "GET"),
    ("/recommendations", "GET"),
    ("/environmental-impact", "GET"),
}


def get_route_pairs():
    """
    Collect HTTP method/path pairs from the application's OpenAPI contract.

    OpenAPI represents the fully resolved API surface, including routes
    registered through included FastAPI routers.
    """
    openapi = app.openapi()
    route_pairs = set()

    for path, operations in openapi.get("paths", {}).items():
        for method in operations:
            route_pairs.add((path, method.upper()))

    return route_pairs

def validate_application_contract() -> None:
    """Validate application metadata and expected route registration."""

    assert app.title == "Recycle Business Recommendation Engine"
    assert app.version == "1.0.0"

    route_pairs = get_route_pairs()

    for expected_route in EXPECTED_ROUTES:
        assert expected_route in route_pairs, (
            f"Missing expected route: {expected_route}"
        )

    # Ensure no duplicate path/method registrations exist.
    assert len(route_pairs) == len(set(route_pairs)), (
        "Duplicate path/method registrations detected."
    )

    print("Application and route validation: PASSED")


def validate_system_endpoints() -> None:
    """Validate root and health endpoints."""

    root_response = client.get("/")
    assert root_response.status_code == 200

    root_payload = root_response.json()

    assert isinstance(root_payload, dict)
    assert root_payload.get("service") == (
        "recycle-business-recommendation-engine"
    )

    health_response = client.get("/health")
    assert health_response.status_code == 200

    health_payload = health_response.json()

    assert health_payload.get("status") == "healthy"
    assert health_payload.get("service") == (
        "recycle-business-recommendation-engine"
    )

    print("System endpoint validation: PASSED")


def validate_material_search() -> dict[str, Any]:
    """Validate material search and return its payload."""

    response = client.get("/materials/search")

    assert response.status_code == 200

    payload = response.json()

    assert payload["count"] == 3
    assert len(payload["materials"]) == payload["count"]

    required_fields = {
        "material_id",
        "material_name",
        "quantity",
        "unit",
    }

    for material in payload["materials"]:
        assert required_fields.issubset(material.keys())

    print("Material search integration validation: PASSED")

    return payload


def validate_recommendations() -> dict[str, Any]:
    """Validate compatibility recommendation endpoint."""

    response = client.get("/recommendations")

    assert response.status_code == 200

    payload = response.json()

    assert payload["count"] == 3
    assert len(payload["recommendations"]) == payload["count"]

    required_fields = {
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

    recommendations = payload["recommendations"]

    for recommendation in recommendations:
        assert required_fields.issubset(recommendation.keys())
        assert recommendation["rank"] >= 1
        assert 0 <= recommendation["compatibility_score"] <= 100
        assert recommendation["quantity_coverage_ratio"] >= 0

    ranks = [item["rank"] for item in recommendations]

    assert ranks == sorted(ranks)
    assert ranks == [1, 2, 3]

    print("Recommendation integration validation: PASSED")

    return payload


def validate_environmental_savings() -> dict[str, Any]:
    """Validate environmental savings endpoint."""

    response = client.get("/environmental-impact")

    assert response.status_code == 200

    payload = response.json()

    assert payload["count"] == 3
    assert len(payload["recommendations"]) == payload["count"]

    summary = payload["environmental_summary"]

    assert summary["recommendation_count"] == 3

    assert summary["total_available_quantity"] == 2200.0
    assert summary["total_carbon_footprint_kg_co2e"] == 7550.0
    assert summary["total_recycling_footprint_kg_co2e"] == 2265.0
    assert summary["total_carbon_savings_kg_co2e"] == 5285.0
    assert summary["overall_carbon_savings_percentage"] == 70.0

    required_fields = {
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
        "emission_factor",
        "carbon_footprint_kg_co2e",
        "recycling_footprint_kg_co2e",
        "carbon_savings_kg_co2e",
        "carbon_savings_percentage",
    }

    for recommendation in payload["recommendations"]:
        assert required_fields.issubset(recommendation.keys())

        baseline = recommendation["carbon_footprint_kg_co2e"]
        recycling = recommendation["recycling_footprint_kg_co2e"]
        savings = recommendation["carbon_savings_kg_co2e"]

        assert abs((baseline - recycling) - savings) < 1e-9

        assert 0 <= recommendation["carbon_savings_percentage"] <= 100

    print("Environmental savings integration validation: PASSED")

    return payload


def validate_cross_endpoint_consistency(
    materials_payload: dict[str, Any],
    recommendations_payload: dict[str, Any],
    environmental_payload: dict[str, Any],
) -> None:
    """Validate consistency across the API endpoints."""

    material_ids = {
        material["material_id"]
        for material in materials_payload["materials"]
    }

    recommendation_ids = {
        recommendation["material_id"]
        for recommendation in recommendations_payload["recommendations"]
    }

    environmental_ids = {
        recommendation["material_id"]
        for recommendation in environmental_payload["recommendations"]
    }

    assert material_ids == recommendation_ids
    assert recommendation_ids == environmental_ids

    material_names = {
        material["material_id"]: material["material_name"]
        for material in materials_payload["materials"]
    }

    for recommendation in recommendations_payload["recommendations"]:
        material_id = recommendation["material_id"]

        assert recommendation["source_material_name"] == material_names[
            material_id
        ]

    for recommendation in environmental_payload["recommendations"]:
        material_id = recommendation["material_id"]

        assert recommendation["source_material_name"] == material_names[
            material_id
        ]

    assert (
        recommendations_payload["count"]
        == environmental_payload["count"]
        == len(materials_payload["materials"])
    )

    print("Cross-endpoint consistency validation: PASSED")


def validate_error_handling() -> None:
    """Validate FastAPI request validation for invalid query parameters."""

    empty_material_name = client.get(
        "/materials/search?material_name="
    )

    assert empty_material_name.status_code == 422

    empty_unit = client.get("/materials/search?unit=")

    assert empty_unit.status_code == 422

    print("Error handling validation: PASSED")


def validate_openapi_contract() -> None:
    """Validate integrated OpenAPI response contracts."""

    response = client.get("/openapi.json")

    assert response.status_code == 200

    openapi = response.json()

    paths = openapi["paths"]

    assert "/materials/search" in paths
    assert "/recommendations" in paths
    assert "/environmental-impact" in paths

    recommendation_operation = paths["/recommendations"]["get"]

    environmental_operation = paths["/environmental-impact"]["get"]

    recommendation_schema = recommendation_operation["responses"]["200"][
        "content"
    ]["application/json"]["schema"]

    environmental_schema = environmental_operation["responses"]["200"][
        "content"
    ]["application/json"]["schema"]

    assert recommendation_schema["$ref"].endswith(
        "/RecommendationResponse"
    )

    assert environmental_schema["$ref"].endswith(
        "/EnvironmentalSavingsResponse"
    )

    schemas = openapi["components"]["schemas"]

    expected_schemas = {
        "Recommendation",
        "RecommendationResponse",
        "EnvironmentalRecommendation",
        "EnvironmentalSummary",
        "EnvironmentalSavingsResponse",
    }

    assert expected_schemas.issubset(schemas.keys())

    print("OpenAPI integration validation: PASSED")


# ---------------------------------------------------------------------------
# Main validation
# ---------------------------------------------------------------------------

def main() -> None:
    """Run the complete Module 6.5 integration validation."""

    validate_application_contract()

    validate_system_endpoints()

    materials_payload = validate_material_search()

    recommendations_payload = validate_recommendations()

    environmental_payload = validate_environmental_savings()

    validate_cross_endpoint_consistency(
        materials_payload,
        recommendations_payload,
        environmental_payload,
    )

    validate_error_handling()

    validate_openapi_contract()

    print()
    print("MODULE 6.5 API VALIDATION & INTEGRATION PASSED")


if __name__ == "__main__":
    main()