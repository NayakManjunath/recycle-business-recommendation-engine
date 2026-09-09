"""
Module 8.1
----------
End-to-end integration tests for the complete Recycle Business
Recommendation Engine.

Validation flow:

Sample Data
    ↓
Business Logic
    ↓
FastAPI
    ↓
Real HTTP
    ↓
APIClient
    ↓
Streamlit
    ↓
User-facing application
"""

from __future__ import annotations

import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

from src.main import app
from src.streamlit_app.api_client import APIClient, APIClientError


PROJECT_ROOT = Path(__file__).resolve().parents[2]

API_HOST = "127.0.0.1"
API_PORT = 8765
STREAMLIT_PORT = 8766

API_BASE_URL = f"http://{API_HOST}:{API_PORT}"
STREAMLIT_BASE_URL = f"http://{API_HOST}:{STREAMLIT_PORT}"

EXPECTED_MATERIAL_IDS = {
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


def _is_port_available(host: str, port: int) -> bool:
    """Return True when the specified TCP port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) != 0


def _wait_for_http(
    url: str,
    *,
    timeout: float = 30.0,
    expected_status: int = 200,
) -> httpx.Response:
    """Wait until an HTTP endpoint becomes available."""
    deadline = time.time() + timeout
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            response = httpx.get(url, timeout=2.0)

            if response.status_code == expected_status:
                return response

        except httpx.HTTPError as exc:
            last_error = exc

        time.sleep(0.5)

    raise RuntimeError(
        f"Timed out waiting for {url}. "
        f"Last error: {last_error}"
    )


@pytest.fixture(scope="session")
def live_api_server():
    """Start a real FastAPI/Uvicorn process for integration testing."""
    if not _is_port_available(API_HOST, API_PORT):
        raise RuntimeError(
            f"Port {API_PORT} is already in use. "
            "Stop the existing API service and rerun the integration suite."
        )

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "src.main:app",
        "--host",
        API_HOST,
        "--port",
        str(API_PORT),
    ]

    process = subprocess.Popen(
        command,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        _wait_for_http(f"{API_BASE_URL}/health")
        yield process

    finally:
        process.terminate()

        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


@pytest.fixture(scope="session")
def live_streamlit_server(live_api_server):
    """Start the real Streamlit presentation layer."""
    del live_api_server

    if not _is_port_available(API_HOST, STREAMLIT_PORT):
        raise RuntimeError(
            f"Port {STREAMLIT_PORT} is already in use. "
            "Stop the existing Streamlit service and rerun the integration suite."
        )

    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "src/streamlit_app/app.py",
        "--server.headless",
        "true",
        "--server.address",
        API_HOST,
        "--server.port",
        str(STREAMLIT_PORT),
    ]

    process = subprocess.Popen(
        command,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        _wait_for_http(
            f"{STREAMLIT_BASE_URL}/_stcore/health"
        )
        yield process

    finally:
        process.terminate()

        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


@pytest.fixture
def api_client(live_api_server) -> APIClient:
    """Return an APIClient connected to the live FastAPI server."""
    del live_api_server
    return APIClient(base_url=API_BASE_URL)


def test_fastapi_application_metadata() -> None:
    """Verify the authoritative FastAPI application."""
    assert app.title == "Recycle Business Recommendation Engine"
    assert app.version == "1.0.0"


def test_fastapi_live_root_endpoint(
    api_client: APIClient,
) -> None:
    """Validate the live root endpoint."""
    response = api_client.get_root()

    assert response["service"] == (
        "recycle-business-recommendation-engine"
    )
    assert response["status"] == "running"
    assert response["version"] == "1.0.0"


def test_fastapi_live_health_endpoint(
    api_client: APIClient,
) -> None:
    """Validate the live health endpoint."""
    response = api_client.get_health()

    assert response["status"] == "healthy"
    assert response["service"] == (
        "recycle-business-recommendation-engine"
    )


def test_material_search_real_http(
    api_client: APIClient,
) -> None:
    """Validate material search through real HTTP."""
    response = api_client.search_materials()

    assert response["count"] == 3
    assert len(response["materials"]) == 3

    material_ids = {
        material["material_id"]
        for material in response["materials"]
    }

    assert material_ids == EXPECTED_MATERIAL_IDS


def test_material_search_filter_real_http(
    api_client: APIClient,
) -> None:
    """Validate filtered material search through real HTTP."""
    response = api_client.search_materials(
        material_name="steel",
    )

    assert response["count"] == 1
    assert response["materials"][0]["material_id"] == "MAT-001"


def test_recommendations_real_http(
    api_client: APIClient,
) -> None:
    """Validate recommendations through real HTTP."""
    response = api_client.get_recommendations()

    assert response["count"] == 3
    assert len(response["recommendations"]) == 3

    recommendations = response["recommendations"]

    assert [item["rank"] for item in recommendations] == [1, 2, 3]

    for recommendation in recommendations:
        assert recommendation["compatibility_score"] == 100.0
        assert recommendation["quantity_coverage_ratio"] > 0
        assert recommendation["material_id"] in EXPECTED_MATERIAL_IDS


def test_environmental_impact_real_http(
    api_client: APIClient,
) -> None:
    """Validate environmental impact through APIClient."""
    response = api_client.get_environmental_impact()

    assert response["count"] == 3
    assert len(response["recommendations"]) == 3

    summary = response["environmental_summary"]

    for field, expected_value in EXPECTED_ENVIRONMENTAL_SUMMARY.items():
        assert summary[field] == pytest.approx(expected_value)


def test_cross_endpoint_material_consistency(
    api_client: APIClient,
) -> None:
    """
    Verify material IDs remain consistent between material search
    and recommendation endpoints.
    """
    materials_response = api_client.search_materials()
    recommendations_response = api_client.get_recommendations()

    material_ids = {
        material["material_id"]
        for material in materials_response["materials"]
    }

    recommendation_ids = {
        recommendation["material_id"]
        for recommendation in recommendations_response[
            "recommendations"
        ]
    }

    assert recommendation_ids == material_ids


def test_cross_endpoint_environmental_consistency(
    api_client: APIClient,
) -> None:
    """
    Verify environmental recommendations preserve compatibility
    recommendation fields.
    """
    recommendations_response = api_client.get_recommendations()
    environmental_response = api_client.get_environmental_impact()

    recommendations = recommendations_response["recommendations"]
    environmental = environmental_response["recommendations"]

    assert len(recommendations) == len(environmental)

    for recommendation, environmental_record in zip(
        recommendations,
        environmental,
    ):
        assert environmental_record["rank"] == recommendation["rank"]
        assert (
            environmental_record["material_id"]
            == recommendation["material_id"]
        )
        assert (
            environmental_record["process_id"]
            == recommendation["process_id"]
        )
        assert (
            environmental_record["demand_id"]
            == recommendation["demand_id"]
        )
        assert (
            environmental_record["compatibility_score"]
            == recommendation["compatibility_score"]
        )
        assert (
            environmental_record["quantity_coverage_ratio"]
            == recommendation["quantity_coverage_ratio"]
        )


def test_environmental_calculation_consistency(
    api_client: APIClient,
) -> None:
    """Verify environmental totals against recommendation-level values."""
    response = api_client.get_environmental_impact()

    recommendations = response["recommendations"]
    summary = response["environmental_summary"]

    total_footprint = sum(
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

    assert total_footprint == pytest.approx(
        summary["total_carbon_footprint_kg_co2e"]
    )

    assert total_recycling == pytest.approx(
        summary["total_recycling_footprint_kg_co2e"]
    )

    assert total_savings == pytest.approx(
        summary["total_carbon_savings_kg_co2e"]
    )


def test_no_result_material_search(
    api_client: APIClient,
) -> None:
    """Validate the no-result search path."""
    response = api_client.search_materials(
        material_name="definitely-not-a-material",
    )

    assert response["count"] == 0
    assert response["materials"] == []


def test_api_client_connection_error() -> None:
    """Validate APIClient error handling."""
    client = APIClient(
        base_url="http://127.0.0.1:8799",
        timeout=0.5,
    )

    with pytest.raises(APIClientError):
        client.get_health()


def test_streamlit_server_startup(
    live_streamlit_server,
) -> None:
    """Verify the real Streamlit server starts successfully."""
    del live_streamlit_server

    response = httpx.get(
        f"{STREAMLIT_BASE_URL}/_stcore/health",
        timeout=5.0,
    )

    assert response.status_code == 200
    assert response.text.strip().lower() == "ok"


def test_streamlit_application_import() -> None:
    """Verify the Streamlit application exposes its main entry point."""
    from src.streamlit_app import app as streamlit_app

    assert hasattr(streamlit_app, "main")


def test_complete_end_to_end_workflow(
    api_client: APIClient,
    live_streamlit_server,
) -> None:
    """
    Execute the representative business workflow from backend
    availability through material discovery, recommendations,
    and environmental impact analysis.
    """
    del live_streamlit_server

    health = api_client.get_health()

    assert health["status"] == "healthy"

    materials = api_client.search_materials(
        material_name="Steel",
    )

    assert materials["count"] == 1
    assert materials["materials"][0]["material_id"] == "MAT-001"

    recommendations = api_client.get_recommendations()

    assert recommendations["count"] == 3

    environmental = api_client.get_environmental_impact()

    assert environmental["count"] == 3

    summary = environmental["environmental_summary"]

    assert summary["total_carbon_savings_kg_co2e"] == pytest.approx(
        5285.0
    )

    assert summary["overall_carbon_savings_percentage"] == pytest.approx(
        70.0
    )
    