"""
Module 7.4 - Environmental Savings Interface Validator.

Validates the Streamlit environmental savings presentation layer,
its FastAPI integration, response contract, error handling, and
separation of business logic.

The validator does not modify application data or business logic.
"""

from __future__ import annotations
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import inspect
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.streamlit_app.api_client import (
    APIClient,
    APIClientError,
)
from src.streamlit_app.components.environmental_savings import (
    _extract_recommendations,
    _extract_summary,
    _format_recommendations,
)
from src.streamlit_app.components.environmental_savings import (
    render_environmental_savings,
)
from src.main import app


PROJECT_ROOT = Path(__file__).resolve().parents[1]

COMPONENT_PATH = (
    PROJECT_ROOT
    / "src"
    / "streamlit_app"
    / "components"
    / "environmental_savings.py"
)

API_CLIENT_PATH = (
    PROJECT_ROOT
    / "src"
    / "streamlit_app"
    / "api_client.py"
)

APP_PATH = (
    PROJECT_ROOT
    / "src"
    / "streamlit_app"
    / "app.py"
)


EXPECTED_SUMMARY = {
    "recommendation_count": 3,
    "total_available_quantity": 2200.0,
    "total_carbon_footprint_kg_co2e": 7550.0,
    "total_recycling_footprint_kg_co2e": 2265.0,
    "total_carbon_savings_kg_co2e": 5285.0,
    "overall_carbon_savings_percentage": 70.0,
}


EXPECTED_RECOMMENDATIONS = {
    "MAT-001": {
        "rank": 1,
        "source_material_name": "Steel Scrap",
        "process_name": "Steel Scrap Recycling",
        "target_material": "Steel Scrap",
        "demand_material_name": "Steel Scrap",
        "carbon_footprint_kg_co2e": 1800.0,
        "recycling_footprint_kg_co2e": 540.0,
        "carbon_savings_kg_co2e": 1260.0,
        "carbon_savings_percentage": 70.0,
    },
    "MAT-002": {
        "rank": 2,
        "source_material_name": "Aluminum Scrap",
        "process_name": "Aluminum Scrap Recycling",
        "target_material": "Aluminum Scrap",
        "demand_material_name": "Aluminum Scrap",
        "carbon_footprint_kg_co2e": 4000.0,
        "recycling_footprint_kg_co2e": 1200.0,
        "carbon_savings_kg_co2e": 2800.0,
        "carbon_savings_percentage": 70.0,
    },
    "MAT-003": {
        "rank": 3,
        "source_material_name": "Plastic Waste",
        "process_name": "Plastic Reprocessing",
        "target_material": "Plastic Waste",
        "demand_material_name": "Plastic Waste",
        "carbon_footprint_kg_co2e": 1750.0,
        "recycling_footprint_kg_co2e": 525.0,
        "carbon_savings_kg_co2e": 1225.0,
        "carbon_savings_percentage": 70.0,
    },
}


def assert_close(
    actual: float,
    expected: float,
    tolerance: float = 1e-9,
) -> None:
    """Validate floating-point values within a small tolerance."""
    assert abs(actual - expected) <= tolerance, (
        f"Expected {expected}, got {actual}"
    )


def validate_component_structure() -> None:
    """Validate the environmental savings component structure."""
    assert COMPONENT_PATH.exists(), (
        "Environmental savings component does not exist."
    )

    source = COMPONENT_PATH.read_text(encoding="utf-8")

    required_symbols = [
        "render_environmental_savings",
        "_extract_recommendations",
        "_extract_summary",
        "_format_recommendations",
        "get_environmental_impact",
        "Environmental Savings",
        "Overall Environmental Impact",
        "Environmental Impact by Recommendation",
    ]

    missing = [
        symbol
        for symbol in required_symbols
        if symbol not in source
    ]

    assert not missing, (
        "Environmental savings component is missing required "
        f"elements: {missing}"
    )

    print(
        "Environmental savings component structure validation: PASSED"
    )


def validate_api_client_method() -> None:
    """Validate the API client environmental-impact method."""
    assert API_CLIENT_PATH.exists(), (
        "API client file does not exist."
    )

    source = API_CLIENT_PATH.read_text(encoding="utf-8")

    assert "def get_environmental_impact(" in source, (
        "APIClient.get_environmental_impact() is missing."
    )

    assert 'self._get("/environmental-impact")' in source, (
        "Environmental API client method does not call "
        '"/environmental-impact".'
    )

    method = getattr(APIClient, "get_environmental_impact", None)

    assert callable(method), (
        "APIClient.get_environmental_impact is not callable."
    )

    print(
        "API client environmental-impact method validation: PASSED"
    )


def validate_backend_environmental_endpoint() -> None:
    """Validate the authoritative FastAPI environmental endpoint."""
    route_pairs = set()

    for route in app.routes:
        methods = getattr(route, "methods", set())

        for method in methods:
            route_pairs.add(
                (route.path, method.upper())
            )

    assert (
        "/environmental-impact",
        "GET",
    ) in route_pairs, (
        "GET /environmental-impact is not registered "
        "on the authoritative FastAPI application."
    )

    print(
        "Backend environmental endpoint validation: PASSED"
    )


def validate_environmental_response() -> dict[str, Any]:
    """Validate the live environmental API response."""
    client = TestClient(app)

    response = client.get("/environmental-impact")

    assert response.status_code == 200, (
        "Environmental endpoint returned "
        f"HTTP {response.status_code}."
    )

    payload = response.json()

    assert isinstance(payload, dict), (
        "Environmental endpoint must return a JSON object."
    )

    assert payload.get("count") == 3, (
        f"Expected count=3, got {payload.get('count')}."
    )

    recommendations = payload.get("recommendations")

    assert isinstance(recommendations, list), (
        "recommendations must be a list."
    )

    assert len(recommendations) == 3, (
        "Expected exactly 3 environmental recommendations."
    )

    summary = payload.get("environmental_summary")

    assert isinstance(summary, dict), (
        "environmental_summary must be an object."
    )

    print(
        "Environmental API response validation: PASSED"
    )

    return payload


def validate_summary_fields(
    payload: dict[str, Any],
) -> None:
    """Validate environmental summary fields and values."""
    summary = payload["environmental_summary"]

    required_fields = [
        "recommendation_count",
        "total_available_quantity",
        "total_carbon_footprint_kg_co2e",
        "total_recycling_footprint_kg_co2e",
        "total_carbon_savings_kg_co2e",
        "overall_carbon_savings_percentage",
    ]

    missing = [
        field
        for field in required_fields
        if field not in summary
    ]

    assert not missing, (
        f"Environmental summary fields missing: {missing}"
    )

    for field, expected in EXPECTED_SUMMARY.items():
        actual = summary[field]

        if isinstance(expected, float):
            assert_close(actual, expected)
        else:
            assert actual == expected, (
                f"{field}: expected {expected}, got {actual}"
            )

    print(
        "Environmental summary validation: PASSED"
    )


def validate_recommendation_fields(
    payload: dict[str, Any],
) -> None:
    """Validate recommendation-level environmental fields."""
    recommendations = payload["recommendations"]

    required_fields = [
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
    ]

    for recommendation in recommendations:
        missing = [
            field
            for field in required_fields
            if field not in recommendation
        ]

        assert not missing, (
            "Recommendation is missing fields: "
            f"{missing}"
        )

    print(
        "Environmental recommendation field validation: PASSED"
    )


def validate_environmental_values(
    payload: dict[str, Any],
) -> None:
    """Validate expected environmental values from the backend."""
    recommendations = payload["recommendations"]

    actual_by_material = {
        recommendation["material_id"]: recommendation
        for recommendation in recommendations
    }

    assert set(actual_by_material) == set(
        EXPECTED_RECOMMENDATIONS
    ), (
        "Unexpected recommendation material IDs: "
        f"{set(actual_by_material)}"
    )

    for material_id, expected in EXPECTED_RECOMMENDATIONS.items():
        actual = actual_by_material[material_id]

        for field, expected_value in expected.items():
            actual_value = actual[field]

            if isinstance(expected_value, float):
                assert_close(
                    actual_value,
                    expected_value,
                )
            else:
                assert actual_value == expected_value, (
                    f"{material_id}.{field}: expected "
                    f"{expected_value}, got {actual_value}"
                )

    print(
        "Environmental recommendation value validation: PASSED"
    )


def validate_helper_functions() -> None:
    """Validate Streamlit presentation helper functions."""
    sample_response = {
        "count": 1,
        "recommendations": [
            {
                "rank": 1,
                "source_material_name": "Steel Scrap",
                "process_name": "Steel Scrap Recycling",
                "target_material": "Steel Scrap",
                "demand_material_name": "Steel Scrap",
                "carbon_footprint_kg_co2e": 1800.0,
                "recycling_footprint_kg_co2e": 540.0,
                "carbon_savings_kg_co2e": 1260.0,
                "carbon_savings_percentage": 70.0,
            }
        ],
        "environmental_summary": {
            "recommendation_count": 1,
            "total_available_quantity": 1000.0,
            "total_carbon_footprint_kg_co2e": 1800.0,
            "total_recycling_footprint_kg_co2e": 540.0,
            "total_carbon_savings_kg_co2e": 1260.0,
            "overall_carbon_savings_percentage": 70.0,
        },
    }

    recommendations = _extract_recommendations(
        sample_response
    )

    assert len(recommendations) == 1
    assert recommendations[0]["rank"] == 1

    summary = _extract_summary(sample_response)

    assert summary["recommendation_count"] == 1
    assert (
        summary["total_carbon_savings_kg_co2e"]
        == 1260.0
    )

    rows = _format_recommendations(
        recommendations
    )

    assert len(rows) == 1

    expected_columns = {
        "Rank",
        "Source Material",
        "Process",
        "Target Material",
        "Demand",
        "Carbon Footprint (kg CO2e)",
        "Recycling Footprint (kg CO2e)",
        "Carbon Savings (kg CO2e)",
        "Savings (%)",
    }

    assert set(rows[0]) == expected_columns

    assert rows[0]["Carbon Savings (kg CO2e)"] == 1260.0
    assert rows[0]["Savings (%)"] == 70.0

    print(
        "Environmental presentation helper validation: PASSED"
    )


def validate_empty_result_handling() -> None:
    """Validate safe handling of empty or malformed API data."""
    assert _extract_recommendations({}) == []
    assert _extract_recommendations(
        {"recommendations": None}
    ) == []
    assert _extract_recommendations(
        {"recommendations": "invalid"}
    ) == []

    assert _extract_summary({}) == {}
    assert _extract_summary(
        {"environmental_summary": None}
    ) == {}
    assert _extract_summary(
        {"environmental_summary": "invalid"}
    ) == {}

    rows = _format_recommendations([])

    assert rows == []

    print(
        "Empty-result handling validation: PASSED"
    )


def validate_api_error_handling() -> None:
    """Validate API client error handling remains available."""
    assert issubclass(
        APIClientError,
        Exception,
    )

    failing_client = APIClient(
        base_url="http://127.0.0.1:1",
        timeout=0.1,
    )

    try:
        failing_client.get_environmental_impact()
    except APIClientError:
        pass
    else:
        raise AssertionError(
            "APIClient did not raise APIClientError "
            "for an unreachable backend."
        )

    print(
        "API error handling validation: PASSED"
    )


def validate_presentation_layer_separation() -> None:
    """
    Validate that Streamlit displays environmental metrics
    without implementing environmental calculations.
    """
    source = COMPONENT_PATH.read_text(
        encoding="utf-8"
    )

    source_lower = source.lower()

    forbidden_logic = [
        "carbon_savings =",
        "carbon_savings_percentage =",
        "total_carbon_savings =",
        "savings_percentage =",
        "carbon_footprint =",
        "recycling_footprint =",
    ]

    violations = [
        expression
        for expression in forbidden_logic
        if expression in source_lower
    ]

    assert not violations, (
        "Environmental calculation logic detected in "
        f"Streamlit presentation layer: {violations}"
    )

    forbidden_operations = [
        "emission_factor *",
        "emission_factor*",
        "carbon_footprint -",
        "carbon_footprint-",
        "carbon_savings /",
        "carbon_savings/",
    ]

    operation_violations = [
        expression
        for expression in forbidden_operations
        if expression in source_lower
    ]

    assert not operation_violations, (
        "Environmental calculation operation detected in "
        f"presentation layer: {operation_violations}"
    )

    required_backend_terms = [
        "backend",
        "environmental calculations",
        "environmental savings engine",
        "get_environmental_impact",
    ]

    missing_terms = [
        term
        for term in required_backend_terms
        if term not in source_lower
    ]

    assert not missing_terms, (
        "Component does not clearly document backend "
        f"ownership of environmental calculations: {missing_terms}"
    )

    required_display_fields = [
        "carbon_footprint_kg_co2e",
        "recycling_footprint_kg_co2e",
        "carbon_savings_kg_co2e",
        "carbon_savings_percentage",
    ]

    missing_display_fields = [
        field
        for field in required_display_fields
        if field not in source
    ]

    assert not missing_display_fields, (
        "Required backend environmental fields are not "
        f"displayed: {missing_display_fields}"
    )

    print(
        "Presentation-layer separation validation: PASSED"
    )


def validate_streamlit_integration() -> None:
    """Validate environmental component integration into the portal."""
    assert APP_PATH.exists(), (
        "Streamlit application file does not exist."
    )

    source = APP_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        "render_environmental_savings"
        in source
    ), (
        "Environmental savings component is not imported "
        "or rendered by the Streamlit application."
    )

    assert (
        "render_environmental_savings(client)"
        in source
    ), (
        "Streamlit application does not render the "
        "environmental savings component with the API client."
    )

    print(
        "Streamlit integration validation: PASSED"
    )


def validate_component_callable() -> None:
    """Validate that the main component renderer is callable."""
    assert callable(
        render_environmental_savings
    )

    signature = inspect.signature(
        render_environmental_savings
    )

    assert "client" in signature.parameters, (
        "render_environmental_savings() must accept "
        "an API client."
    )

    print(
        "Environmental renderer validation: PASSED"
    )


def main() -> None:
    """Run the complete Module 7.4 validation suite."""
    print()
    print(
        "MODULE 7.4 ENVIRONMENTAL SAVINGS "
        "INTERFACE VALIDATION"
    )
    print()

    validate_component_structure()
    validate_api_client_method()
    validate_backend_environmental_endpoint()

    payload = validate_environmental_response()

    validate_summary_fields(payload)
    validate_recommendation_fields(payload)
    validate_environmental_values(payload)

    validate_helper_functions()
    validate_empty_result_handling()
    validate_api_error_handling()
    validate_presentation_layer_separation()
    validate_streamlit_integration()
    validate_component_callable()

    print()
    print(
        "MODULE 7.4 ENVIRONMENTAL SAVINGS "
        "INTERFACE VALIDATION PASSED"
    )
    print()


if __name__ == "__main__":
    main()