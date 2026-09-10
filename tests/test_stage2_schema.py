from backend.app.database import Base
from backend.app.models import (
    DrainageEdge,
    DrainageNode,
    EmergencyFacility,
    FloodPrediction,
    FloodReport,
    ForecastRun,
    KnownHotspot,
    RainfallForecast,
    RainfallObservation,
    Road,
    SessionRecord,
    User,
    UserPreference,
    Ward,
)


def test_stage2_declares_required_tables():
    expected = {
        "users",
        "user_preferences",
        "sessions",
        "roads",
        "wards",
        "drainage_nodes",
        "drainage_edges",
        "rainfall_observations",
        "rainfall_forecasts",
        "forecast_runs",
        "flood_predictions",
        "known_hotspots",
        "emergency_facilities",
        "flood_reports",
        "audit_logs",
    }
    assert expected.issubset(Base.metadata.tables)


def test_models_are_bound_to_expected_tables():
    assert User.__tablename__ == "users"
    assert UserPreference.__tablename__ == "user_preferences"
    assert Road.__tablename__ == "roads"
    assert DrainageNode.__tablename__ == "drainage_nodes"
    assert DrainageEdge.__tablename__ == "drainage_edges"
    assert RainfallObservation.__tablename__ == "rainfall_observations"
    assert RainfallForecast.__tablename__ == "rainfall_forecasts"
    assert ForecastRun.__tablename__ == "forecast_runs"
    assert FloodPrediction.__tablename__ == "flood_predictions"
    assert KnownHotspot.__tablename__ == "known_hotspots"
    assert EmergencyFacility.__tablename__ == "emergency_facilities"
    assert FloodReport.__tablename__ == "flood_reports"
    assert SessionRecord.__tablename__ == "sessions"
    assert Ward.__tablename__ == "wards"
