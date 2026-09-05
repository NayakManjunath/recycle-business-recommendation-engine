"""
FastAPI client for the Streamlit portal.

Module 7.2
----------
Provides centralized communication between the Streamlit
presentation layer and the FastAPI backend.
"""

from __future__ import annotations

from typing import Any

import httpx

from src.streamlit_app.config import get_api_base_url


class APIClientError(Exception):
    """Raised when communication with the FastAPI backend fails."""


class APIClient:
    """Client for communicating with the FastAPI backend."""

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = (
            base_url.rstrip("/")
            if base_url
            else get_api_base_url()
        )
        self.timeout = timeout

    def _get(
        self,
        path: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Execute a GET request and return the JSON response."""
        url = f"{self.base_url}{path}"

        try:
            response = httpx.get(
                url,
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise APIClientError(
                f"API request failed: {exc}"
            ) from exc

        try:
            return response.json()
        except ValueError as exc:
            raise APIClientError(
                "API returned an invalid JSON response."
            ) from exc

    def get_root(self) -> dict[str, Any]:
        """Return API root information."""
        return self._get("/")

    def get_health(self) -> dict[str, Any]:
        """Return API health information."""
        return self._get("/health")

    def search_materials(
        self,
        material_name: str | None = None,
        unit: str | None = None,
    ) -> dict[str, Any]:
        """
        Search materials through the FastAPI material-search endpoint.

        The Streamlit layer does not perform material filtering itself.
        All search behavior remains owned by the FastAPI backend.
        """
        params: dict[str, str] = {}

        if material_name:
            params["material_name"] = material_name.strip()

        if unit:
            params["unit"] = unit.strip()

        return self._get(
            "/materials/search",
            params=params or None,
        )