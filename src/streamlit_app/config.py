"""
Streamlit portal configuration.

Module 7.1
----------
Centralizes configuration for the Streamlit presentation layer.
"""

from __future__ import annotations

import os


DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"


def get_api_base_url() -> str:
    """
    Return the FastAPI backend base URL.

    The API_BASE_URL environment variable can be used to override
    the local-development default.
    """
    configured_url = os.getenv(
        "API_BASE_URL",
        DEFAULT_API_BASE_URL,
    )

    return configured_url.rstrip("/")
