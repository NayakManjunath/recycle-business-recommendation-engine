"""
Streamlit portal configuration.

Module 8.2.1
------------
Centralizes runtime configuration for the Streamlit presentation
layer and provides validation for the FastAPI backend URL.
"""

from __future__ import annotations

import os
from urllib.parse import urlparse


DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"


class ConfigurationError(ValueError):
    """Raised when application configuration is invalid."""


def _validate_api_base_url(value: str) -> str:
    """
    Validate and normalize the FastAPI backend base URL.

    Parameters
    ----------
    value:
        API base URL supplied through configuration.

    Returns
    -------
    str
        Normalized API base URL without a trailing slash.

    Raises
    ------
    ConfigurationError
        If the configured URL is empty or malformed.
    """

    normalized_url = value.strip().rstrip("/")

    if not normalized_url:
        raise ConfigurationError(
            "API_BASE_URL cannot be empty."
        )

    parsed = urlparse(normalized_url)

    if parsed.scheme not in {"http", "https"}:
        raise ConfigurationError(
            "API_BASE_URL must use the http or https scheme."
        )

    if not parsed.netloc:
        raise ConfigurationError(
            "API_BASE_URL must include a valid host."
        )

    return normalized_url


def get_api_base_url() -> str:
    """
    Return the validated FastAPI backend base URL.

    API_BASE_URL can be used to override the local-development
    default.
    """

    configured_url = os.getenv(
        "API_BASE_URL",
        DEFAULT_API_BASE_URL,
    )

    return _validate_api_base_url(configured_url)
