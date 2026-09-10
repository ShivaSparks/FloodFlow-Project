from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.model.ml_correction import save_model, train_demo_model


def main() -> int:
    result = train_demo_model()
    model_path = ROOT / "data" / "generated" / "xgboost_demo_model.joblib"
    metrics_path = ROOT / "data" / "generated" / "xgboost_demo_metrics.json"
    save_model(result, model_path)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(
        json.dumps(
            {
                "metrics": result.metrics,
                "training_source": result.training_source,
                "warning": "Synthetic demo labels; not real-world accuracy.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Trained demo XGBoost model: {model_path.relative_to(ROOT)}")
    print(f"Metrics: {result.metrics}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
