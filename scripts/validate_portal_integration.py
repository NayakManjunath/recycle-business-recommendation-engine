"""
Module 7.5 - End-to-End Portal Validation.

Validates the complete Streamlit portal integration with the
authoritative FastAPI backend.

The validator verifies:
- Streamlit portal structure
- API client integration
- all backend endpoints
- material search flow
- recommendation flow
- environmental savings flow
- cross-feature consistency
- error handling
- presentation/business-logic separation
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.main import app
from src.streamlit_app.api_client import (
    APIClient,
    APIClientError,
)
from src.streamlit_app.components.common import (
    render_api_status,
    render_footer,
    render_header,
)
from src.streamlit_app.components.environmental_savings import (
    render_environmental_savings,
)
from src.streamlit_app.components.material_search import (
    render_material_search,
)
from src.streamlit_app.components.recommendations import (
    render_recommendations,
)


STREAMLIT_APP_PATH = (
    PROJECT_ROOT
    / "src"
    / "streamlit_app"
    / "app.py"
)

API_CLIENT_PATH = (
    PROJECT_ROOT
    / "src"
    / "streamlit_app"
    / "api_client.py"
)

COMPONENTS_DIR = (
    PROJECT_ROOT
    / "src"
    / "streamlit_app"
    / "components"
)


EXPECTED_ROUTES = {
    ("/", "GET"),
    ("/health", "GET"),
    ("/materials/search", "GET"),
    ("/recommendations", "GET"),
    ("/environmental-impact", "GET"),
}


EXPECTED_MATERIAL_IDS = {
    "MAT-001",
    "MAT-002",
    "MAT-003",
}


EXPECTED_RECOMMENDATION_IDS = {
    "MAT-001",
    "MAT-002",
    "MAT-003",
}


EXPECTED_ENVIRONMENTAL_SUMMARY = {
    "recommendation_count": 3,
    "total_available_quantity": 2200.0,
    "total_carbon_footprint_kg_co2e": 7550.0,
    "total_recycling_footprint_kg_co2e": 2265.0,
    "total_carbon_savings_kg_co2e": 5285.0,
    "overall_carbon_savings_percentage": 70.0,
}


def assert_close(
    actual: float,
    expected: float,
    tolerance: float = 1e-9,
) -> None:
    """Validate floating-point values within tolerance."""
    assert abs(actual - expected) <= tolerance, (
        f"Expected {expected}, got {actual}"
    )


def validate_portal_structure() -> None:
    """Validate the Streamlit application structure."""
    assert STREAMLIT_APP_PATH.exists(), (
        "Streamlit application file does not exist."
    )

    required_components = [
        "src/streamlit_app/components/common.py",
        "src/streamlit_app/components/material_search.py",
        "src/streamlit_app/components/recommendations.py",
        "src/streamlit_app/components/environmental_savings.py",
    ]

    for component in required_components:
        path = PROJECT_ROOT / component

        assert path.exists(), (
            f"Required portal component is missing: {component}"
        )

    source = STREAMLIT_APP_PATH.read_text(
        encoding="utf-8"
    )

    required_renderers = [
        "render_header",
        "render_api_status",
        "render_material_search",
        "render_recommendations",
        "render_environmental_savings",
        "render_footer",
    ]

    missing = [
        renderer
        for renderer in required_renderers
        if renderer not in source
    ]

    assert not missing, (
        "Streamlit application is missing required "
        f"portal integrations: {missing}"
    )

    print(
        "Portal structure validation: PASSED"
    )


def validate_portal_metadata() -> None:
    """Validate application metadata and corrected portal identity."""
    source = STREAMLIT_APP_PATH.read_text(
        encoding="utf-8"
    )

    assert (
        "Recycle Business Recommendation Engine"
        in source
    )

    assert 'page_title="Recycle Business Recommendation Engine"' in source

    assert 'page_icon="♻️"' in source, (
        "Streamlit page icon is not configured correctly."
    )

    assert "Module 7" in source
    assert "Module 7.2" not in source

    print(
        "Portal metadata validation: PASSED"
    )


def validate_api_client_contract() -> None:
    """Validate all API client methods required by the portal."""
    assert API_CLIENT_PATH.exists()

    source = API_CLIENT_PATH.read_text(
        encoding="utf-8"
    )

    required_methods = [
        "get_root",
        "get_health",
        "search_materials",
        "get_recommendations",
        "get_environmental_impact",
    ]

    for method_name in required_methods:
        assert (
            f"def {method_name}("
            in source
        ), (
            f"API client method missing: {method_name}"
        )

        method = getattr(
            APIClient,
            method_name,
            None,
        )

        assert callable(method), (
            f"API client method is not callable: {method_name}"
        )

    assert '"/materials/search"' in source
    assert '"/recommendations"' in source
    assert '"/environmental-impact"' in source

    print(
        "API client contract validation: PASSED"
    )


def validate_component_callables() -> None:
    """Validate all portal renderers are callable."""
    renderers = {
        "header": render_header,
        "API status": render_api_status,
        "material search": render_material_search,
        "recommendations": render_recommendations,
        "environmental savings": render_environmental_savings,
        "footer": render_footer,
    }

    for name, renderer in renderers.items():
        assert callable(renderer), (
            f"{name} renderer is not callable."
        )

    print(
        "Portal component callable validation: PASSED"
    )


def get_route_pairs() -> set[tuple[str, str]]:
    """Return routes exposed by the authoritative FastAPI app."""
    route_pairs: set[tuple[str, str]] = set()

    openapi = app.openapi()

    for path, operations in openapi.get(
        "paths",
        {},
    ).items():
        for method in operations:
            route_pairs.add(
                (path, method.upper())
            )

    return route_pairs


def validate_backend_routes() -> None:
    """Validate all required FastAPI routes."""
    route_pairs = get_route_pairs()

    missing = EXPECTED_ROUTES - route_pairs

    assert not missing, (
        "Required FastAPI routes are missing: "
        f"{sorted(missing)}"
    )

    print(
        "Backend route validation: PASSED"
    )


def validate_system_endpoints(
    client: TestClient,
) -> None:
    """Validate root and health endpoints."""
    root_response = client.get("/")

    assert root_response.status_code == 200
    root_payload = root_response.json()

    assert root_payload.get("status") == "running"

    health_response = client.get("/health")

    assert health_response.status_code == 200
    health_payload = health_response.json()

    assert health_payload.get("status") == "healthy"

    print(
        "System endpoint validation: PASSED"
    )


def validate_material_search(
    client: TestClient,
) -> dict[str, Any]:
    """Validate the complete material search API flow."""
    response = client.get(
        "/materials/search"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload.get("count") == 3

    materials = payload.get("materials")

    assert isinstance(materials, list)
    assert len(materials) == 3

    material_ids = {
        material["material_id"]
        for material in materials
    }

    assert material_ids == EXPECTED_MATERIAL_IDS

    steel_response = client.get(
        "/materials/search",
        params={"material_name": "steel"},
    )

    assert steel_response.status_code == 200

    steel_payload = steel_response.json()

    assert steel_payload["count"] == 1
    assert (
        steel_payload["materials"][0]["material_id"]
        == "MAT-001"
    )

    print(
        "Material search end-to-end validation: PASSED"
    )

    return payload


def validate_recommendations(
    client: TestClient,
) -> dict[str, Any]:
    """Validate the complete recommendation API flow."""
    response = client.get(
        "/recommendations"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload.get("count") == 3

    recommendations = payload.get(
        "recommendations"
    )

    assert isinstance(recommendations, list)
    assert len(recommendations) == 3

    recommendation_ids = {
        recommendation["material_id"]
        for recommendation in recommendations
    }

    assert (
        recommendation_ids
        == EXPECTED_RECOMMENDATION_IDS
    )

    ranks = [
        recommendation["rank"]
        for recommendation in recommendations
    ]

    assert ranks == [1, 2, 3]

    for recommendation in recommendations:
        assert (
            0
            <= recommendation["compatibility_score"]
            <= 100
        )

        assert (
            recommendation["quantity_coverage_ratio"]
            >= 0
        )

    print(
        "Recommendation end-to-end validation: PASSED"
    )

    return payload


def validate_environmental_savings(
    client: TestClient,
) -> dict[str, Any]:
    """Validate the complete environmental savings API flow."""
    response = client.get(
        "/environmental-impact"
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload.get("count") == 3

    recommendations = payload.get(
        "recommendations"
    )

    assert isinstance(recommendations, list)
    assert len(recommendations) == 3

    summary = payload.get(
        "environmental_summary"
    )

    assert isinstance(summary, dict)

    for field, expected in (
        EXPECTED_ENVIRONMENTAL_SUMMARY.items()
    ):
        actual = summary[field]

        if isinstance(expected, float):
            assert_close(
                actual,
                expected,
            )
        else:
            assert actual == expected

    required_environmental_fields = [
        "emission_factor",
        "carbon_footprint_kg_co2e",
        "recycling_footprint_kg_co2e",
        "carbon_savings_kg_co2e",
        "carbon_savings_percentage",
    ]

    for recommendation in recommendations:
        for field in required_environmental_fields:
            assert field in recommendation

    print(
        "Environmental savings end-to-end validation: PASSED"
    )

    return payload


def validate_cross_feature_consistency(
    materials_payload: dict[str, Any],
    recommendations_payload: dict[str, Any],
    environmental_payload: dict[str, Any],
) -> None:
    """Validate consistency across all three portal features."""
    material_ids = {
        material["material_id"]
        for material in materials_payload[
            "materials"
        ]
    }

    recommendation_ids = {
        recommendation["material_id"]
        for recommendation in recommendations_payload[
            "recommendations"
        ]
    }

    environmental_ids = {
        recommendation["material_id"]
        for recommendation in environmental_payload[
            "recommendations"
        ]
    }

    assert material_ids == recommendation_ids, (
        "Material and recommendation IDs are inconsistent."
    )

    assert (
        recommendation_ids
        == environmental_ids
    ), (
        "Recommendation and environmental IDs "
        "are inconsistent."
    )

    assert (
        environmental_payload[
            "environmental_summary"
        ]["recommendation_count"]
        == recommendations_payload["count"]
    )

    print(
        "Cross-feature consistency validation: PASSED"
    )


def validate_api_error_handling() -> None:
    """Validate graceful API client failure behavior."""
    failing_client = APIClient(
        base_url="http://127.0.0.1:1",
        timeout=0.1,
    )

    methods = [
        failing_client.get_root,
        failing_client.get_health,
        failing_client.search_materials,
        failing_client.get_recommendations,
        failing_client.get_environmental_impact,
    ]

    for method in methods:
        try:
            method()
        except APIClientError:
            continue

        raise AssertionError(
            "API client did not raise APIClientError "
            "for an unreachable backend."
        )

    print(
        "API error handling validation: PASSED"
    )


def validate_presentation_layer_separation() -> None:
    """Ensure Streamlit does not duplicate backend business logic."""
    component_files = [
        COMPONENTS_DIR / "material_search.py",
        COMPONENTS_DIR / "recommendations.py",
        COMPONENTS_DIR / "environmental_savings.py",
    ]

    forbidden_calculations = [
        "compatibility_score =",
        "quantity_coverage_ratio =",
        "carbon_savings =",
        "carbon_savings_percentage =",
        "carbon_footprint =",
        "recycling_footprint =",
        "emission_factor *",
        "carbon_footprint -",
        "carbon_savings /",
    ]

    for component_path in component_files:
        source = component_path.read_text(
            encoding="utf-8"
        ).lower()

        violations = [
            expression
            for expression in forbidden_calculations
            if expression in source
        ]

        assert not violations, (
            f"Business logic detected in "
            f"{component_path.name}: {violations}"
        )

    print(
        "Presentation-layer separation validation: PASSED"
    )


def validate_api_client_live_flow() -> None:
    """Validate Streamlit API client against the live backend."""
    api_client = APIClient()

    root = api_client.get_root()
    health = api_client.get_health()
    materials = api_client.search_materials()
    recommendations = api_client.get_recommendations()
    environmental = (
        api_client.get_environmental_impact()
    )

    assert root.get("status") == "running"
    assert health.get("status") == "healthy"

    assert materials.get("count") == 3
    assert recommendations.get("count") == 3
    assert environmental.get("count") == 3

    print(
        "API client live-flow validation: PASSED"
    )


def main() -> None:
    """Run the complete Module 7.5 validation suite."""
    print()
    print(
        "MODULE 7.5 END-TO-END PORTAL VALIDATION"
    )
    print()

    validate_portal_structure()
    validate_portal_metadata()
    validate_api_client_contract()
    validate_component_callables()
    validate_backend_routes()

    backend_client = TestClient(app)

    validate_system_endpoints(
        backend_client
    )

    materials_payload = validate_material_search(
        backend_client
    )

    recommendations_payload = (
        validate_recommendations(
            backend_client
        )
    )

    environmental_payload = (
        validate_environmental_savings(
            backend_client
        )
    )

    validate_cross_feature_consistency(
        materials_payload,
        recommendations_payload,
        environmental_payload,
    )

    validate_api_error_handling()
    validate_presentation_layer_separation()
    validate_api_client_live_flow()

    print()
    print(
        "MODULE 7.5 END-TO-END PORTAL VALIDATION PASSED"
    )
    print()


if __name__ == "__main__":
    main()