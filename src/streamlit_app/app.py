"""
Streamlit application entry point.

Module 7.2
----------
Provides the user-facing material search portal while
delegating business logic to the FastAPI backend.
"""

from __future__ import annotations

import streamlit as st

from src.streamlit_app.api_client import (
    APIClient,
    APIClientError,
)
from src.streamlit_app.components.common import (
    render_api_status,
    render_footer,
    render_header,
)
from src.streamlit_app.components.material_search import (
    render_material_search,
)
from src.streamlit_app.config import get_api_base_url


st.set_page_config(
    page_title="Recycle Business Recommendation Engine",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    """Render the Streamlit portal."""
    render_header()

    api_base_url = get_api_base_url()

    st.sidebar.header("Application")
    st.sidebar.caption(
        f"API Backend: {api_base_url}"
    )

    client = APIClient()

    health_response = None
    error_message = None

    try:
        health_response = client.get_health()
    except APIClientError as exc:
        error_message = str(exc)

    render_api_status(
        health_response=health_response,
        error_message=error_message,
    )

    st.divider()

    render_material_search(client)

    render_footer()


if __name__ == "__main__":
    main()