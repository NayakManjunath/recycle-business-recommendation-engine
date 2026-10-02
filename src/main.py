"""
Application entry point for the Recycle Business Recommendation Engine.

Module 6
--------
Provides the authoritative FastAPI application for the project.

All production API routes are registered here so that this module
remains the single application entry point for the API.
"""

from fastapi import FastAPI, HTTPException

from src.api.materials import router as materials_router
from src.api.recommendations import (
    environmental_impact_endpoint,
    recommendations_endpoint,
)
from src.api.schemas import (
    EnvironmentalSavingsResponse,
    RecommendationResponse,
)
from fastapi.exceptions import RequestValidationError

from src.api.error_handlers import (
    http_exception_handler,
    unexpected_exception_handler,
    validation_exception_handler,
)


# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Recycle Business Recommendation Engine",
    description=(
        "AI/ML-powered recommendation engine for "
        "reuse, recycling, and remanufacturing of industrial materials."
    ),
    version="1.0.0",
)
# ---------------------------------------------------------------------------
# Centralized error handling
# ---------------------------------------------------------------------------

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)

app.add_exception_handler(
    HTTPException,
    http_exception_handler,
)

app.add_exception_handler(
    Exception,
    unexpected_exception_handler,
)

# ---------------------------------------------------------------------------
# System endpoints
# ---------------------------------------------------------------------------

@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    """Return basic API information."""

    return {
        "service": "recycle-business-recommendation-engine",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health", tags=["System"])
def health() -> dict[str, str]:
    """Return API health status."""

    return {
        "status": "healthy",
        "service": "recycle-business-recommendation-engine",
    }


# ---------------------------------------------------------------------------
# Material API
# ---------------------------------------------------------------------------

app.include_router(materials_router)


# ---------------------------------------------------------------------------
# Recommendation API
# ---------------------------------------------------------------------------

app.add_api_route(
    "/recommendations",
    recommendations_endpoint,
    methods=["GET"],
    tags=["Recommendations"],
    response_model=RecommendationResponse,
)


# ---------------------------------------------------------------------------
# Environmental Impact API
# ---------------------------------------------------------------------------

app.add_api_route(
    "/environmental-impact",
    environmental_impact_endpoint,
    methods=["GET"],
    tags=["Environmental Impact"],
    response_model=EnvironmentalSavingsResponse,
)
