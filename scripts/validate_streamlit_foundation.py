"""
Validate Module 7.1 Streamlit Portal Foundation.

Checks:
- required portal structure
- configuration
- API client
- reusable components
- Streamlit application entry point
- FastAPI connectivity
- API error handling
- separation of presentation and backend logic
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Ensure the project root is importable when this validator
# is executed directly from the scripts directory.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.streamlit_app.api_client import APIClient, APIClientError
from src.streamlit_app.config import (
    DEFAULT_API_BASE_URL,
    get_api_base_url,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PORTAL_ROOT = PROJECT_ROOT / "src" / "streamlit_app"


def validate_structure() -> None:
    required_paths = [
        PORTAL_ROOT,
        PORTAL_ROOT / "__init__.py",
        PORTAL_ROOT / "app.py",
        PORTAL_ROOT / "config.py",
        PORTAL_ROOT / "api_client.py",
        PORTAL_ROOT / "components",
        PORTAL_ROOT / "components" / "__init__.py",
        PORTAL_ROOT / "components" / "common.py",
    ]

    for path in required_paths:
        assert path.exists(), f"Missing required path: {path}"

    print("Portal structure validation: PASSED")


def validate_configuration() -> None:
    os.environ.pop("API_BASE_URL", None)

    assert get_api_base_url() == DEFAULT_API_BASE_URL

    os.environ["API_BASE_URL"] = "http://example.com/"
    assert get_api_base_url() == "http://example.com"

    os.environ.pop("API_BASE_URL", None)

    print("Portal configuration validation: PASSED")


def validate_api_client() -> None:
    client = APIClient(
        base_url="http://127.0.0.1:8000/",
    )

    assert client.base_url == "http://127.0.0.1:8000"
    assert client.timeout == 10.0

    root = client.get_root()
    health = client.get_health()

    assert root["service"] == "recycle-business-recommendation-engine"
    assert root["status"] == "running"
    assert root["version"] == "1.0.0"

    assert health["status"] == "healthy"
    assert health["service"] == "recycle-business-recommendation-engine"

    print("API client validation: PASSED")


def validate_api_error_handling() -> None:
    client = APIClient(
        base_url="http://127.0.0.1:59999",
        timeout=1.0,
    )

    try:
        client.get_health()
    except APIClientError:
        print("API error handling validation: PASSED")
        return

    raise AssertionError(
        "APIClientError was not raised for unavailable backend."
    )


def validate_application_imports() -> None:
    from src.streamlit_app.app import main
    from src.streamlit_app.components.common import (
        render_api_status,
        render_footer,
        render_header,
    )

    assert callable(main)
    assert callable(render_header)
    assert callable(render_api_status)
    assert callable(render_footer)

    print("Streamlit application import validation: PASSED")


def validate_presentation_layer_separation() -> None:
    source_files = [
        PORTAL_ROOT / "app.py",
        PORTAL_ROOT / "api_client.py",
        PORTAL_ROOT / "components" / "common.py",
    ]

    forbidden_backend_logic = [
        "load_csv(",
        "validate_dataframe(",
        "calculate_carbon",
        "compatibility_score",
        "carbon_savings_kg_co2e",
    ]

    for path in source_files:
        source = path.read_text(encoding="utf-8")

        for forbidden in forbidden_backend_logic:
            assert forbidden not in source, (
                f"Backend business logic detected in presentation layer: "
                f"{forbidden} in {path}"
            )

    print("Presentation-layer separation validation: PASSED")


def main() -> None:
    validate_structure()
    validate_configuration()
    validate_api_client()
    validate_api_error_handling()
    validate_application_imports()
    validate_presentation_layer_separation()

    print()
    print("MODULE 7.1 STREAMLIT PORTAL FOUNDATION VALIDATION PASSED")


if __name__ == "__main__":
    main()
