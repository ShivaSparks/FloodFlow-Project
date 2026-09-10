import pandas as pd

from backend.app.model.ml_correction import (
    FEATURE_COLUMNS,
    build_demo_training_frame,
    combine_physics_and_ml,
    predict_probability,
    train_demo_model,
)


def test_demo_training_frame_has_feature_contract():
    frame = build_demo_training_frame(rows=100)
    assert set(FEATURE_COLUMNS).issubset(frame.columns)
    assert "flooded_label" in frame.columns
    assert len(frame) == 100


def test_xgboost_demo_model_trains_and_predicts():
    result = train_demo_model(build_demo_training_frame(rows=160))
    probabilities = predict_probability(result.model, result.model.get_booster().feature_names and pd.DataFrame([{
        column: 1.0 for column in FEATURE_COLUMNS
    }]))
    assert 0 <= probabilities[0] <= 1
    assert 0 <= result.metrics["roc_auc"] <= 1


def test_hybrid_risk_uses_both_layers():
    assert combine_physics_and_ml(8, 0.99) == "watch"
    assert combine_physics_and_ml(35, 0.1) == "dangerous"
    assert combine_physics_and_ml(2, 0.1) == "safe"
