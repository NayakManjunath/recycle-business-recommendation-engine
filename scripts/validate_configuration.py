"""
Validate Module 8.2.1 API configuration management.

Checks:
- default API URL
- environment override
- trailing slash normalization
- explicit APIClient configuration
- invalid configuration handling
- .env.example documentation
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_EXAMPLE = PROJECT_ROOT / ".env.example"

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.streamlit_app.api_client import APIClient
from src.streamlit_app.config import (
    ConfigurationError,
    DEFAULT_API_BASE_URL,
    get_api_base_url,
)




def assert_equal(actual, expected, message: str) -> None:
    if actual != expected:
        raise AssertionError(
            f"{message}: expected {expected!r}, got {actual!r}"
        )


def validate_default_configuration() -> None:
    previous_value = os.environ.pop("API_BASE_URL", None)

    try:
        assert_equal(
            get_api_base_url(),
            DEFAULT_API_BASE_URL,
            "Default API URL validation failed",
        )
    finally:
        if previous_value is not None:
            os.environ["API_BASE_URL"] = previous_value

    print("Default API configuration validation: PASSED")


def validate_environment_override() -> None:
    previous_value = os.environ.get("API_BASE_URL")

    try:
        os.environ["API_BASE_URL"] = (
            "https://example-api.internal/"
        )

        assert_equal(
            get_api_base_url(),
            "https://example-api.internal",
            "Environment override validation failed",
        )
    finally:
        if previous_value is None:
            os.environ.pop("API_BASE_URL", None)
        else:
            os.environ["API_BASE_URL"] = previous_value

    print("Environment override validation: PASSED")


def validate_trailing_slash_normalization() -> None:
    previous_value = os.environ.get("API_BASE_URL")

    try:
        os.environ["API_BASE_URL"] = (
            "http://127.0.0.1:8000///"
        )

        assert_equal(
            get_api_base_url(),
            "http://127.0.0.1:8000",
            "Trailing slash normalization failed",
        )
    finally:
        if previous_value is None:
            os.environ.pop("API_BASE_URL", None)
        else:
            os.environ["API_BASE_URL"] = previous_value

    print("Trailing slash normalization validation: PASSED")


def validate_invalid_configuration() -> None:
    previous_value = os.environ.get("API_BASE_URL")

    invalid_values = [
        "",
        "localhost:8000",
        "ftp://example.com",
        "http://",
    ]

    try:
        for invalid_value in invalid_values:
            os.environ["API_BASE_URL"] = invalid_value

            try:
                get_api_base_url()
            except ConfigurationError:
                continue

            raise AssertionError(
                f"Invalid API_BASE_URL was accepted: {invalid_value!r}"
            )
    finally:
        if previous_value is None:
            os.environ.pop("API_BASE_URL", None)
        else:
            os.environ["API_BASE_URL"] = previous_value

    print("Invalid configuration validation: PASSED")


def validate_explicit_api_client_configuration() -> None:
    client = APIClient(
        base_url="https://example-api.internal///"
    )

    assert_equal(
        client.base_url,
        "https://example-api.internal",
        "Explicit APIClient base URL validation failed",
    )

    print("Explicit APIClient configuration validation: PASSED")


def validate_env_example() -> None:
    if not ENV_EXAMPLE.exists():
        raise AssertionError(
            ".env.example is missing."
        )

    content = ENV_EXAMPLE.read_text(
        encoding="utf-8"
    )

    if "API_BASE_URL=" not in content:
        raise AssertionError(
            ".env.example does not document API_BASE_URL."
        )

    print(".env.example validation: PASSED")


def main() -> None:
    validate_default_configuration()
    validate_environment_override()
    validate_trailing_slash_normalization()
    validate_invalid_configuration()
    validate_explicit_api_client_configuration()
    validate_env_example()

    print()
    print(
        "MODULE 8.2.1 API CONFIGURATION MANAGEMENT "
        "VALIDATION PASSED"
    )


if __name__ == "__main__":
    main()
