"""
Validate Module 6.4 Environmental Savings API.

Checks:
- Environmental savings route registration
- Runtime response structure
- Environmental recommendation fields
- Environmental summary fields
- Expected environmental calculations
- OpenAPI response contract
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from src.main import app

EXPECTED_RECOMMENDATION_FIELDS = {
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

EXPECTED_SUMMARY_FIELDS = {
    "recommendation_count",
    "total_available_quantity",
    "total_carbon_footprint_kg_co2e",
    "total_recycling_footprint_kg_co2e",
    "total_carbon_savings_kg_co2e",
    "overall_carbon_savings_percentage",
}


client = TestClient(app)


# ---------------------------------------------------------------------------
# Route validation
# ---------------------------------------------------------------------------

routes = {
    route.path
    for route in app.routes
    if hasattr(route, "path")
}

assert "/environmental-impact" in routes
print("Environmental savings route validation: PASSED")


# ---------------------------------------------------------------------------
# Runtime response validation
# ---------------------------------------------------------------------------

response = client.get("/environmental-impact")

assert response.status_code == 200
payload = response.json()

assert "count" in payload
assert "recommendations" in payload
assert "environmental_summary" in payload

assert payload["count"] == len(payload["recommendations"])
assert payload["count"] == 3

print("Environmental savings response validation: PASSED")


# ---------------------------------------------------------------------------
# Recommendation schema validation
# ---------------------------------------------------------------------------

recommendations = payload["recommendations"]

assert recommendations

for recommendation in recommendations:
    assert EXPECTED_RECOMMENDATION_FIELDS.issubset(
        recommendation.keys()
    )

    assert recommendation["rank"] >= 1
    assert 0 <= recommendation["compatibility_score"] <= 100
    assert recommendation["quantity_coverage_ratio"] >= 0
    assert recommendation["emission_factor"] >= 0
    assert recommendation["carbon_footprint_kg_co2e"] >= 0
    assert recommendation["recycling_footprint_kg_co2e"] >= 0
    assert recommendation["carbon_savings_kg_co2e"] >= 0
    assert 0 <= recommendation["carbon_savings_percentage"] <= 100

print("Environmental recommendation field validation: PASSED")


# ---------------------------------------------------------------------------
# Environmental calculation validation
# ---------------------------------------------------------------------------

total_baseline = sum(
    item["carbon_footprint_kg_co2e"]
    for item in recommendations
)

total_recycling = sum(
    item["recycling_footprint_kg_co2e"]
    for item in recommendations
)

total_savings = sum(
    item["carbon_savings_kg_co2e"]
    for item in recommendations
)

assert round(total_baseline, 2) == 7550.00
assert round(total_recycling, 2) == 2265.00
assert round(total_savings, 2) == 5285.00

assert all(
    round(item["carbon_savings_percentage"], 2) == 70.00
    for item in recommendations
)

print("Environmental calculation validation: PASSED")


# ---------------------------------------------------------------------------
# Summary validation
# ---------------------------------------------------------------------------

summary = payload["environmental_summary"]

assert EXPECTED_SUMMARY_FIELDS.issubset(summary.keys())

assert summary["recommendation_count"] == 3
assert summary["total_available_quantity"] == 2200.0
assert summary["total_carbon_footprint_kg_co2e"] == 7550.0
assert summary["total_recycling_footprint_kg_co2e"] == 2265.0
assert summary["total_carbon_savings_kg_co2e"] == 5285.0
assert summary["overall_carbon_savings_percentage"] == 70.0

print("Environmental summary validation: PASSED")


# ---------------------------------------------------------------------------
# OpenAPI contract validation
# ---------------------------------------------------------------------------

openapi_response = client.get("/openapi.json")

assert openapi_response.status_code == 200

openapi = openapi_response.json()

environmental_schema = (
    openapi["paths"]["/environmental-impact"]["get"]
    ["responses"]["200"]["content"]["application/json"]["schema"]
)

assert (
    environmental_schema["$ref"]
    == "#/components/schemas/EnvironmentalSavingsResponse"
)

schemas = openapi["components"]["schemas"]

assert "EnvironmentalSavingsResponse" in schemas
assert "EnvironmentalRecommendation" in schemas
assert "EnvironmentalSummary" in schemas

print("OpenAPI response contract validation: PASSED")


print()
print("MODULE 6.4 ENVIRONMENTAL SAVINGS VALIDATION PASSED")