"""
API response schemas.

Module 6.3
----------
Defines typed Pydantic models for compatibility recommendation responses.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class Recommendation(BaseModel):
    """Single compatibility recommendation."""

    rank: int = Field(ge=1)
    material_id: str
    source_material_name: str
    process_id: str
    process_name: str
    target_material: str
    demand_id: str
    demand_material_name: str
    compatibility_score: float = Field(ge=0, le=100)
    quantity_coverage_ratio: float = Field(ge=0)


class RecommendationResponse(BaseModel):
    """Compatibility recommendation API response."""

    count: int = Field(ge=0)
    recommendations: list[Recommendation]

class EnvironmentalRecommendation(BaseModel):
    """Single recommendation with environmental savings metrics."""

    rank: int = Field(ge=1)
    material_id: str
    source_material_name: str
    process_id: str
    process_name: str
    target_material: str
    demand_id: str
    demand_material_name: str

    compatibility_score: float = Field(ge=0, le=100)
    quantity_coverage_ratio: float = Field(ge=0)

    emission_factor: float = Field(ge=0)
    carbon_footprint_kg_co2e: float = Field(ge=0)
    recycling_footprint_kg_co2e: float = Field(ge=0)
    carbon_savings_kg_co2e: float = Field(ge=0)
    carbon_savings_percentage: float = Field(ge=0, le=100)


class EnvironmentalSummary(BaseModel):
    """Aggregate environmental impact and carbon savings metrics."""

    recommendation_count: int = Field(ge=0)
    total_available_quantity: float = Field(ge=0)
    total_carbon_footprint_kg_co2e: float = Field(ge=0)
    total_recycling_footprint_kg_co2e: float = Field(ge=0)
    total_carbon_savings_kg_co2e: float = Field(ge=0)
    overall_carbon_savings_percentage: float = Field(ge=0, le=100)


class EnvironmentalSavingsResponse(BaseModel):
    """Environmental savings API response."""

    count: int = Field(ge=0)
    recommendations: list[EnvironmentalRecommendation]
    environmental_summary: EnvironmentalSummary