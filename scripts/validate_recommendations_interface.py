"""
Validate Module 7.3 compatibility recommendation interface.

Checks:
1. Recommendation component structure
2. API client recommendation method
3. Backend recommendation integration
4. Recommendation response structure
5. Ranking and scoring preservation
6. Quantity coverage preservation
7. Empty-result handling
8. API error handling
9. Streamlit component import
10. Presentation-layer separation
"""

from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

from src.streamlit_app.api_client import (
    APIClient,
    APIClientError,
)
from src.streamlit_app.components.recommendations import (
    _extract_recommendations,
    _format_recommendations,
)


COMPONENT_PATH = (
    PROJECT_ROOT
    / "src"
    / "streamlit_app"
    / "components"
    / "recommendations.py"
)

API_CLIENT_PATH = (
    PROJECT_ROOT
    / "src"
    / "streamlit_app"
    / "api_client.py"
)


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


def validate_component_structure() -> None:
    assert COMPONENT_PATH.exists(), (
        "Recommendation component file is missing."
    )

    source = COMPONENT_PATH.read_text(
        encoding="utf-8"
    )

    required_symbols = {
        "_extract_recommendations",
        "_format_recommendations",
        "render_recommendations",
    }

    tree = ast.parse(source)

    function_names = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    missing = required_symbols - function_names

    assert not missing, (
        f"Missing recommendation component functions: {missing}"
    )

    print(
        "Recommendation component structure validation: PASSED"
    )


def validate_api_client_method() -> None:
    assert API_CLIENT_PATH.exists(), (
        "API client file is missing."
    )

    source = API_CLIENT_PATH.read_text(
        encoding="utf-8"
    )

    assert "def get_recommendations(" in source, (
        "APIClient.get_recommendations() is missing."
    )

    tree = ast.parse(source)

    methods = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    }

    assert "get_recommendations" in methods, (
        "get_recommendations() is not defined correctly."
    )

    print(
        "API client recommendation method validation: PASSED"
    )


def validate_backend_recommendations() -> dict:
    client = APIClient()

    response = client.get_recommendations()

    assert isinstance(response, dict), (
        "Recommendation response must be a dictionary."
    )

    assert response.get("count") == 3, (
        "Expected 3 sample recommendations."
    )

    recommendations = response.get(
        "recommendations"
    )

    assert isinstance(recommendations, list), (
        "Recommendations must be returned as a list."
    )

    assert len(recommendations) == 3, (
        "Expected 3 recommendation records."
    )

    print(
        "Backend recommendation integration validation: PASSED"
    )

    return response


def validate_response_fields(
    response: dict,
) -> None:
    recommendations = response["recommendations"]

    for recommendation in recommendations:
        missing = EXPECTED_FIELDS - recommendation.keys()

        assert not missing, (
            f"Missing recommendation fields: {missing}"
        )

    print(
        "Recommendation response field validation: PASSED"
    )


def validate_ranking_and_scores(
    response: dict,
) -> None:
    recommendations = response["recommendations"]

    ranks = [
        recommendation["rank"]
        for recommendation in recommendations
    ]

    assert ranks == [1, 2, 3], (
        f"Unexpected recommendation ranking: {ranks}"
    )

    scores = [
        recommendation["compatibility_score"]
        for recommendation in recommendations
    ]

    assert scores == [100.0, 100.0, 100.0], (
        f"Unexpected compatibility scores: {scores}"
    )

    print(
        "Ranking and compatibility-score validation: PASSED"
    )


def validate_quantity_coverage(
    response: dict,
) -> None:
    recommendations = response["recommendations"]

    coverage = [
        recommendation["quantity_coverage_ratio"]
        for recommendation in recommendations
    ]

    assert coverage[0] == 1.25
    assert coverage[1] == 1.25
    assert abs(coverage[2] - 1.1666666666666667) < 1e-9

    print(
        "Quantity coverage validation: PASSED"
    )


def validate_presentation_helpers(
    response: dict,
) -> None:
    recommendations = _extract_recommendations(
        response
    )

    assert len(recommendations) == 3

    rows = _format_recommendations(
        recommendations
    )

    assert len(rows) == 3

    expected_display_fields = {
        "Rank",
        "Source Material",
        "Process",
        "Target Material",
        "Demand",
        "Compatibility Score",
        "Quantity Coverage",
    }

    assert set(rows[0].keys()) == expected_display_fields

    assert rows[0]["Rank"] == 1
    assert rows[0]["Source Material"] == "Steel Scrap"
    assert rows[0]["Compatibility Score"] == 100.0

    print(
        "Presentation helper validation: PASSED"
    )


def validate_empty_result_handling() -> None:
    empty_response = {
        "count": 0,
        "recommendations": [],
    }

    recommendations = _extract_recommendations(
        empty_response
    )

    assert recommendations == []

    rows = _format_recommendations(
        recommendations
    )

    assert rows == []

    print(
        "Empty-result handling validation: PASSED"
    )


def validate_api_error_handling() -> None:
    client = APIClient(
        base_url="http://127.0.0.1:1",
        timeout=0.5,
    )

    try:
        client.get_recommendations()
    except APIClientError:
        print(
            "API error handling validation: PASSED"
        )
        return

    raise AssertionError(
        "APIClientError was not raised for an unavailable backend."
    )


def validate_presentation_layer_separation() -> None:
    """Validate that recommendation logic remains backend-owned."""
    source = COMPONENT_PATH.read_text(
        encoding="utf-8"
    )

    forbidden_terms = {
        "compatibility_score =",
        "quantity_coverage_ratio =",
        "sorted(",
        "max(",
        "min(",
    }

    violations = [
        term
        for term in forbidden_terms
        if term in source
    ]

    assert not violations, (
        "Recommendation business logic detected in "
        f"presentation layer: {violations}"
    )

    architecture_terms = {
        "recommendation",
        "backend",
        "scoring",
        "ranking",
    }

    source_lower = source.lower()

    missing_architecture_terms = [
        term
        for term in architecture_terms
        if term not in source_lower
    ]

    assert not missing_architecture_terms, (
        "Presentation layer does not clearly document "
        "backend ownership of recommendation logic: "
        f"{missing_architecture_terms}"
    )

    assert "compatibility_score" in source
    assert "quantity_coverage_ratio" in source

    print(
        "Presentation-layer separation validation: PASSED"
    )

def main() -> None:
    print(
        "\nMODULE 7.3 RECOMMENDATION INTERFACE VALIDATION\n"
    )

    validate_component_structure()
    validate_api_client_method()

    response = validate_backend_recommendations()

    validate_response_fields(response)
    validate_ranking_and_scores(response)
    validate_quantity_coverage(response)
    validate_presentation_helpers(response)
    validate_empty_result_handling()
    validate_api_error_handling()
    validate_presentation_layer_separation()

    print(
        "\nMODULE 7.3 RECOMMENDATION INTERFACE "
        "VALIDATION PASSED"
    )


if __name__ == "__main__":
    main()