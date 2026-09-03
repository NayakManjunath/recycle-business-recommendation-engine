"""
Application entry point for the Recycle Business Recommendation Engine.

Module 6.1
----------
Provides the FastAPI application foundation and registers
the existing recommendation API routes.
"""

from fastapi import FastAPI

from src.api.materials import router as materials_router
from src.api.schemas import (
    EnvironmentalSavingsResponse,
    RecommendationResponse,
)
from src.api.recommendations import (
    environmental_impact_endpoint,
    recommendations_endpoint,
    health,
)


app = FastAPI(
    title="Recycle Business Recommendation Engine",
    description=(
        "AI/ML-powered recommendation engine for "
        "reuse, recycling, and remanufacturing of industrial materials."
    ),
    version="1.0.0",
)

app.add_api_route(
    "/environmental-impact",
    environmental_impact_endpoint,
    methods=["GET"],
    tags=["Environmental Impact"],
    response_model=EnvironmentalSavingsResponse,
)

app.include_router(materials_router)


@app.get("/", tags=["System"])
def root() -> dict[str, str]:
    """Return basic API information."""
    return {
        "service": "recycle-business-recommendation-engine",
        "status": "running",
        "version": "1.0.0",
    }
