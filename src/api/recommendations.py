from pathlib import Path

from fastapi import FastAPI

from src.data_pipeline.loader import load_csv
from src.compatibility.features import build_compatibility_features
from src.compatibility.scoring import calculate_compatibility_score
from src.compatibility.ranking import rank_compatibility_results
from src.compatibility.filtering import filter_recommendations


app = FastAPI(
    title="Recycle Business Recommendation Engine",
    description="API for industrial waste reuse and recycling recommendations.",
    version="1.0.0",
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MATERIALS_PATH = PROJECT_ROOT / "data" / "sample" / "material_byproducts.csv"
PROCESSES_PATH = PROJECT_ROOT / "data" / "sample" / "recycling_processes.csv"
DEMAND_PATH = PROJECT_ROOT / "data" / "sample" / "secondary_market_demand.csv"


def generate_recommendations():
    """Run the complete recommendation pipeline."""

    materials = load_csv(str(MATERIALS_PATH))
    processes = load_csv(str(PROCESSES_PATH))
    demand = load_csv(str(DEMAND_PATH))

    features = build_compatibility_features(
        materials,
        processes,
        demand,
    )

    scored = calculate_compatibility_score(features)

    ranked = rank_compatibility_results(scored)

    filtered = filter_recommendations(ranked)

    return filtered


@app.get("/health")
def health_check():
    """Return API health status."""

    return {
        "status": "healthy",
        "service": "recycle-business-recommendation-engine",
    }


@app.get("/recommendations")
def get_recommendations():
    """Return filtered compatibility recommendations."""

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

    result = recommendations[columns].to_dict(orient="records")

    return {
        "count": len(result),
        "recommendations": result,
    }