"""
Recommendation API.

Module 4.5
----------
Extends the recommendation API with environmental impact metrics.
"""

from __future__ import annotations

from src.api.schemas import RecommendationResponse
from typing import Any

from fastapi import FastAPI

from src.compatibility.features import build_compatibility_features
from src.compatibility.filtering import filter_recommendations
from src.compatibility.ranking import rank_compatibility_results
from src.compatibility.scoring import calculate_compatibility_score
from src.data_pipeline.loader import load_csv
from src.environmental.carbon_savings import calculate_carbon_savings
from src.environmental.impact_integration import (
    get_environmental_summary,
    integrate_environmental_impact,
)


app = FastAPI(
    title="Recycle Business Recommendation Engine",
    description=(
        "Recommendation API with environmental impact "
        "and carbon savings analysis."
    ),
    version="1.0.0",
)


MATERIALS_PATH = "data/sample/material_byproducts.csv"
PROCESSES_PATH = "data/sample/recycling_processes.csv"
DEMAND_PATH = "data/sample/secondary_market_demand.csv"


def generate_recommendations():
    """
    Generate filtered compatibility recommendations.

    Returns
    -------
    pandas.DataFrame
        Ranked and filtered recommendations.
    """
    materials = load_csv(MATERIALS_PATH)
    processes = load_csv(PROCESSES_PATH)
    demand = load_csv(DEMAND_PATH)

    features = build_compatibility_features(
        materials,
        processes,
        demand,
    )

    scored = calculate_compatibility_score(features)

    ranked = rank_compatibility_results(scored)

    filtered = filter_recommendations(ranked)

    return filtered


def get_recommendations() -> dict[str, Any]:
    """
    Return recommendations in API-friendly JSON structure.
    """
    recommendations = generate_recommendations()

    columns = [
        "rank",
        "material_id",
        "source_material_name",
        "process_id",
        "process_name",
        "target_material",
        "demand_id",
        "demand_material_name",
        "compatibility_score",
        "quantity_coverage_ratio",
    ]

    records = recommendations[columns].to_dict(
        orient="records"
    )

    return {
        "count": len(records),
        "recommendations": records,
    }


def get_environmental_impact() -> dict[str, Any]:
    """
    Generate recommendations enriched with environmental metrics.

    Returns
    -------
    dict
        Environmental impact response containing detailed
        recommendation-level metrics and aggregate summary.
    """
    recommendations = generate_recommendations()

    environmental = integrate_environmental_impact(
        recommendations
    )

    environmental = calculate_carbon_savings(
        environmental
    )

    columns = [
        "rank",
        "material_id",
        "source_material_name",
        "process_id",
        "process_name",
        "target_material",
        "demand_id",
        "demand_material_name",
        "compatibility_score",
        "quantity_coverage_ratio",
        "emission_factor",
        "carbon_footprint_kg_co2e",
        "recycling_footprint_kg_co2e",
        "carbon_savings_kg_co2e",
        "carbon_savings_percentage",
    ]

    records = environmental[columns].to_dict(
        orient="records"
    )

    summary = get_environmental_summary(
        recommendations
    )

    total_savings = float(
        environmental["carbon_savings_kg_co2e"].sum()
    )

    total_recycling_footprint = float(
        environmental["recycling_footprint_kg_co2e"].sum()
    )

    total_baseline = float(
        environmental["carbon_footprint_kg_co2e"].sum()
    )

    overall_savings_percentage = (
        (total_savings / total_baseline) * 100.0
        if total_baseline > 0
        else 0.0
    )

    summary.update(
        {
            "total_recycling_footprint_kg_co2e":
                total_recycling_footprint,
            "total_carbon_savings_kg_co2e":
                total_savings,
            "overall_carbon_savings_percentage":
                overall_savings_percentage,
        }
    )

    return {
        "count": len(records),
        "recommendations": records,
        "environmental_summary": summary,
    }


@app.get("/health")
def health() -> dict[str, str]:
    """Return API health status."""
    return {
        "status": "healthy",
        "service": "recycle-business-recommendation-engine",
    }


@app.get(
    "/recommendations",
    response_model=RecommendationResponse,
)
def recommendations_endpoint() -> dict[str, Any]:
    """Return compatibility recommendations."""
    return get_recommendations()


def environmental_impact_endpoint() -> dict[str, Any]:
    """Return recommendations with environmental impact metrics."""
    return get_environmental_impact()
