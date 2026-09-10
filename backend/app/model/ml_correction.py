from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier

FEATURE_COLUMNS = [
    "rainfall_mm",
    "cumulative_rainfall_mm",
    "physics_depth_cm",
    "drainage_utilization",
    "runoff_coefficient",
    "elevation_m",
    "historical_flood_frequency",
    "road_class_code",
]


@dataclass(frozen=True)
class MLTrainingResult:
    model: XGBClassifier
    metrics: dict[str, float]
    training_source: str


def _sigmoid(value: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-value))


def build_demo_training_frame(rows: int = 800, seed: int = 42) -> pd.DataFrame:
    """Create labelled demo data; never use this as real accuracy evidence."""
    rng = np.random.default_rng(seed)
    frame = pd.DataFrame(
        {
            "rainfall_mm": rng.gamma(3.0, 4.0, rows),
            "cumulative_rainfall_mm": rng.gamma(4.0, 12.0, rows),
            "physics_depth_cm": rng.gamma(2.0, 12.0, rows),
            "drainage_utilization": rng.uniform(0.1, 1.5, rows),
            "runoff_coefficient": rng.uniform(0.25, 0.95, rows),
            "elevation_m": rng.uniform(3.0, 8.0, rows),
            "historical_flood_frequency": rng.uniform(0.0, 1.0, rows),
            "road_class_code": rng.integers(0, 3, rows),
        }
    )
    score = (
        -3.0
        + frame["rainfall_mm"] * 0.08
        + frame["cumulative_rainfall_mm"] * 0.025
        + frame["physics_depth_cm"] * 0.10
        + frame["drainage_utilization"] * 2.0
        - frame["elevation_m"] * 0.20
        + frame["historical_flood_frequency"] * 1.2
        + frame["runoff_coefficient"] * 1.2
    )
    probability = _sigmoid(score.to_numpy())
    frame["flooded_label"] = rng.binomial(1, probability)
    return frame


def train_demo_model(frame: pd.DataFrame | None = None, seed: int = 42) -> MLTrainingResult:
    frame = build_demo_training_frame(seed=seed) if frame is None else frame.copy()
    missing = set(FEATURE_COLUMNS + ["flooded_label"]) - set(frame.columns)
    if missing:
        raise ValueError(f"Missing ML columns: {sorted(missing)}")
    x_train, x_test, y_train, y_test = train_test_split(
        frame[FEATURE_COLUMNS],
        frame["flooded_label"],
        test_size=0.25,
        random_state=seed,
        stratify=frame["flooded_label"],
    )
    model = XGBClassifier(
        n_estimators=80,
        max_depth=4,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=seed,
        n_jobs=1,
    )
    model.fit(x_train, y_train)
    probability = model.predict_proba(x_test)[:, 1]
    predictions = (probability >= 0.5).astype(int)
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "roc_auc": float(roc_auc_score(y_test, probability)),
        "training_rows": float(len(frame)),
    }
    return MLTrainingResult(model=model, metrics=metrics, training_source="synthetic_demo")


def predict_probability(model: XGBClassifier, features: pd.DataFrame) -> np.ndarray:
    missing = set(FEATURE_COLUMNS) - set(features.columns)
    if missing:
        raise ValueError(f"Missing inference columns: {sorted(missing)}")
    return model.predict_proba(features[FEATURE_COLUMNS])[:, 1]


def combine_physics_and_ml(physics_depth_cm: float, flood_probability: float) -> str:
    # The physics depth remains the primary safety signal. The demo classifier
    # may indicate elevated likelihood, but it must not turn a 5 cm prediction
    # into a blocked road by itself.
    if physics_depth_cm >= 50:
        return "blocked"
    if physics_depth_cm >= 30:
        return "dangerous"
    if physics_depth_cm >= 10 or (physics_depth_cm >= 8 and flood_probability >= 0.98):
        return "watch"
    return "safe"


def save_model(result: MLTrainingResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": result.model,
            "metrics": result.metrics,
            "training_source": result.training_source,
            "feature_columns": FEATURE_COLUMNS,
        },
        path,
    )


def load_model(path: Path) -> XGBClassifier:
    payload = joblib.load(path)
    if payload.get("feature_columns") != FEATURE_COLUMNS:
        raise ValueError("Saved model feature contract does not match current code")
    return payload["model"]
