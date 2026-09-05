"""
Reusable Streamlit components.

Module 7.1
----------
Contains shared presentation components used across the portal.
"""

from __future__ import annotations

from typing import Any

import streamlit as st


def render_header() -> None:
    """Render the main application header."""
    st.title("Recycle Business Recommendation Engine")
    st.caption(
        "AI/ML-powered recommendations for industrial "
        "reuse, recycling, and remanufacturing."
    )


def render_api_status(
    health_response: dict[str, Any] | None,
    error_message: str | None = None,
) -> None:
    """Render the current FastAPI backend status."""
    st.subheader("System Status")

    if error_message:
        st.error(
            "Unable to connect to the FastAPI backend."
        )
        st.caption(error_message)
        return

    if health_response and health_response.get("status") == "healthy":
        st.success("FastAPI backend is healthy.")
        return

    st.warning("FastAPI backend status is unavailable.")


def render_footer() -> None:
    """Render a small application footer."""
    st.divider()
    st.caption(
        "Recycle Business Recommendation Engine • "
        "Streamlit Presentation Layer"
    )
