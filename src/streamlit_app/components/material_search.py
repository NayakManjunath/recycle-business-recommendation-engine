"""
Material search interface.

Module 7.2
----------
Provides the Streamlit presentation layer for material search.
All filtering and search behavior is delegated to the FastAPI API.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from src.streamlit_app.api_client import (
    APIClient,
    APIClientError,
)


def _extract_material_rows(
    response: dict[str, Any],
) -> list[dict[str, Any]]:
    """Extract material records from the API response."""
    materials = response.get("materials", [])

    if not isinstance(materials, list):
        return []

    return materials


def _extract_units(
    response: dict[str, Any],
) -> list[str]:
    """Extract unique units from API material records."""
    materials = _extract_material_rows(response)

    units = {
        str(material["unit"])
        for material in materials
        if material.get("unit")
    }

    return sorted(units)


def render_material_search(client: APIClient) -> None:
    """Render the material search interface."""
    st.subheader("Material Search")

    st.write(
        "Search industrial material byproduct records "
        "using the FastAPI backend."
    )

    # Load all materials to populate the unit filter.
    try:
        initial_response = client.search_materials()
    except APIClientError as exc:
        st.error("Unable to load material search data.")
        st.caption(str(exc))
        return

    units = _extract_units(initial_response)

    col1, col2 = st.columns(2)

    with col1:
        material_name = st.text_input(
            "Material Name",
            placeholder="e.g. Steel",
            help="Enter a material name or partial material name.",
        )

    with col2:
        unit_options = ["All"] + units

        selected_unit = st.selectbox(
            "Unit",
            options=unit_options,
            index=0,
        )

    search_clicked = st.button(
        "🔎 Search Materials",
        type="primary",
        use_container_width=True,
    )

    if search_clicked:
        unit_filter = (
            None
            if selected_unit == "All"
            else selected_unit
        )

        try:
            with st.spinner("Searching materials..."):
                response = client.search_materials(
                    material_name=material_name or None,
                    unit=unit_filter,
                )
        except APIClientError as exc:
            st.error("Material search failed.")
            st.caption(str(exc))
            return

        materials = _extract_material_rows(response)
        count = response.get("count", len(materials))

        st.divider()

        st.metric(
            label="Matching Materials",
            value=count,
        )

        if not materials:
            st.info(
                "No materials matched the selected search criteria."
            )
            return

        st.dataframe(
            materials,
            use_container_width=True,
            hide_index=True,
        )

    else:
        st.divider()

        st.caption(
            "Enter search criteria and select "
            "'Search Materials' to view matching records."
        )