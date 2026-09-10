from __future__ import annotations

from pathlib import Path

import pandas as pd
from fastapi import APIRouter, HTTPException, Query

from ..model.ml_correction import combine_physics_and_ml, load_model, predict_probability
from .simulator import get_simulator

router = APIRouter(prefix="/flood", tags=["flood"])
ROOT = Path(__file__).resolve().parents[3]


@router.get("/timeline")
def timeline() -> dict:
    steps = get_simulator().preview_timeline()
    model_path = ROOT / "data" / "generated" / "xgboost_demo_model.joblib"
    if model_path.exists():
        model = load_model(model_path)
        for step in steps:
            frame = pd.DataFrame([
                {
                    "rainfall_mm": step["rainfall_mm_15min"],
                    "cumulative_rainfall_mm": step["cumulative_rainfall_mm"],
                    "physics_depth_cm": prediction["predicted_depth_cm"],
                    "drainage_utilization": prediction["drainage_utilization"],
                    "runoff_coefficient": 0.9,
                    "elevation_m": 5.0,
                    "historical_flood_frequency": 0.5,
                    "road_class_code": 1,
                }
                for prediction in step["predictions"]
            ])
            probabilities = predict_probability(model, frame)
            for prediction, probability in zip(step["predictions"], probabilities):
                prediction["ml_flood_probability"] = round(float(probability), 3)
                prediction["final_risk_level"] = combine_physics_and_ml(prediction["predicted_depth_cm"], float(probability))
                prediction["ml_source"] = "synthetic_demo_runtime"
    return {
        "data_mode": "synthetic",
        "is_simulation": True,
        "steps": steps,
    }


@router.get("/prediction")
def prediction(lead_minutes: int = Query(default=60, ge=0, le=180)) -> dict:
    payload = timeline()
    steps = payload["steps"]
    selected = min(steps, key=lambda step: abs(step["simulation_time_minutes"] - lead_minutes))
    return {**payload, "selected_lead_minutes": selected["simulation_time_minutes"], "predictions": selected["predictions"]}
