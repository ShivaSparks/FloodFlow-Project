from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.model.ml_correction import (
    combine_physics_and_ml,
    load_model,
    predict_probability,
)


def main() -> int:
    generated = ROOT / "data" / "generated"
    model = load_model(generated / "xgboost_demo_model.joblib")
    simulation_path = generated / "stage3_demo_predictions.json"
    steps = json.loads(simulation_path.read_text(encoding="utf-8"))
    enriched = []
    for step in steps:
        rows = []
        for prediction in step["predictions"]:
            rows.append(
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
            )
        features = pd.DataFrame(rows)
        probabilities = predict_probability(model, features)
        enriched_predictions = []
        for prediction, probability in zip(step["predictions"], probabilities):
            item = dict(prediction)
            item["ml_flood_probability"] = round(float(probability), 3)
            item["final_risk_level"] = combine_physics_and_ml(
                item["predicted_depth_cm"], float(probability)
            )
            item["ml_source"] = "synthetic_demo"
            enriched_predictions.append(item)
        enriched.append({**step, "predictions": enriched_predictions})
    output = generated / "hybrid_demo_predictions.json"
    output.write_text(json.dumps(enriched, indent=2), encoding="utf-8")
    print(f"Generated hybrid outputs: {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
