"""
Validate the Module 6.1 FastAPI foundation.

Checks:
- FastAPI application imports successfully
- Application metadata is correct
- Required foundation routes are registered
- Health endpoint returns the expected response
- Root endpoint returns the expected application metadata
"""

from __future__ import annotations

from pathlib import Path
import sys

# Add the project root to Python's import path.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastapi.testclient import TestClient

from src.main import app


EXPECTED_TITLE = "Recycle Business Recommendation Engine"
EXPECTED_VERSION = "1.0.0"
EXPECTED_SERVICE = "recycle-business-recommendation-engine"

REQUIRED_ROUTES = {
    "/",
    "/health",
    "/recommendations",
    "/environmental-impact",
}


def validate_application_metadata() -> None:
    """Validate FastAPI application metadata."""
    assert app.title == EXPECTED_TITLE
    assert app.version == EXPECTED_VERSION


def validate_routes() -> None:
    """Validate required API routes are registered."""
    registered_routes = {
        route.path
        for route in app.routes
        if hasattr(route, "path")
    }

    missing_routes = REQUIRED_ROUTES - registered_routes

    assert not missing_routes, (
        f"Missing required routes: {sorted(missing_routes)}"
    )


def validate_health_endpoint(client: TestClient) -> None:
    """Validate the health endpoint."""
    response = client.get("/health")

    assert response.status_code == 200

    payload = response.json()

    assert payload["status"] == "healthy"
    assert payload["service"] == EXPECTED_SERVICE


def validate_root_endpoint(client: TestClient) -> None:
    """Validate the root endpoint."""
    response = client.get("/")

    assert response.status_code == 200

    payload = response.json()

    assert payload["service"] == EXPECTED_SERVICE
    assert payload["status"] == "running"
    assert payload["version"] == EXPECTED_VERSION


def main() -> None:
    """Run all Module 6.1 validation checks."""
    validate_application_metadata()
    validate_routes()

    with TestClient(app) as client:
        validate_health_endpoint(client)
        validate_root_endpoint(client)

    print("Application metadata validation: PASSED")
    print("Route registration validation: PASSED")
    print("Health endpoint validation: PASSED")
    print("Root endpoint validation: PASSED")
    print()
    print("MODULE 6.1 FASTAPI FOUNDATION VALIDATION PASSED")


if __name__ == "__main__":
    main()