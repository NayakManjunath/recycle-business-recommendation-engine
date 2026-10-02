"""
Validate centralized API error handling for Module 8.2.
"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient
from fastapi import HTTPException

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.main import app


def validate_validation_error() -> None:
    """Validate FastAPI request validation handling."""

    client = TestClient(app)

    response = client.get(
        "/materials/search",
        params={"material_name": ""},
    )

    assert response.status_code == 422

    body = response.json()

    assert "error" in body
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message"] == "Request validation failed."
    assert "details" in body["error"]

    print("Request validation error handling: PASSED")


def validate_http_exception() -> None:
    """Validate explicit HTTP exception handling."""

    route_path = "/_validation/http-error"

    def test_http_error() -> None:
        raise HTTPException(
            status_code=400,
            detail="Invalid test request.",
        )

    app.add_api_route(
        route_path,
        test_http_error,
        methods=["GET"],
    )

    client = TestClient(app)

    response = client.get(route_path)

    assert response.status_code == 400

    body = response.json()

    assert body["error"]["code"] == "HTTP_ERROR"
    assert body["error"]["message"] == "Invalid test request."

    print("HTTP exception handling: PASSED")


def validate_unexpected_exception() -> None:
    """Validate safe handling of unexpected internal failures."""

    route_path = "/_validation/internal-error"

    def test_internal_error() -> None:
        raise RuntimeError(
            "SECRET_INTERNAL_PATH_OR_TRACEBACK"
        )

    app.add_api_route(
        route_path,
        test_internal_error,
        methods=["GET"],
    )

    client = TestClient(
        app,
        raise_server_exceptions=False,
    )

    response = client.get(route_path)

    assert response.status_code == 500

    body = response.json()

    assert body["error"]["code"] == "INTERNAL_SERVER_ERROR"
    assert (
        body["error"]["message"]
        == "An unexpected internal server error occurred."
    )

    response_text = response.text

    assert "SECRET_INTERNAL_PATH_OR_TRACEBACK" not in response_text
    assert "Traceback" not in response_text

    print("Unexpected exception handling: PASSED")


def validate_normal_endpoints() -> None:
    """Ensure existing successful endpoints remain unaffected."""

    client = TestClient(app)

    root_response = client.get("/")
    health_response = client.get("/health")
    materials_response = client.get("/materials/search")
    recommendations_response = client.get("/recommendations")
    environmental_response = client.get("/environmental-impact")

    assert root_response.status_code == 200
    assert health_response.status_code == 200
    assert materials_response.status_code == 200
    assert recommendations_response.status_code == 200
    assert environmental_response.status_code == 200

    print("Existing successful endpoints regression: PASSED")


def main() -> None:
    validate_validation_error()
    validate_http_exception()
    validate_unexpected_exception()
    validate_normal_endpoints()

    print()
    print("MODULE 8.2 ERROR HANDLING VALIDATION PASSED")


if __name__ == "__main__":
    main()