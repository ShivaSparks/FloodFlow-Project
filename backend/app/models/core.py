from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func, Index
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(30), default="USER", nullable=False, index=True)
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class SessionRecord(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class UserPreference(Base):
    __tablename__ = "user_preferences"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    home_label: Mapped[str | None] = mapped_column(String(120))
    home_location = mapped_column(Geometry("POINT", srid=4326, spatial_index=True), nullable=True)
    work_label: Mapped[str | None] = mapped_column(String(120))
    work_location = mapped_column(Geometry("POINT", srid=4326, spatial_index=True), nullable=True)
    default_transport: Mapped[str] = mapped_column(String(30), default="car", nullable=False)
    alert_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(20), default="en", nullable=False)


class Road(TimestampMixin, Base):
    __tablename__ = "roads"
    id: Mapped[int] = mapped_column(primary_key=True)
    road_id: Mapped[str] = mapped_column(String(80), unique=True, nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String(255))
    road_class: Mapped[str | None] = mapped_column(String(50))
    speed_kph: Mapped[float | None] = mapped_column(Float)
    source_type: Mapped[str] = mapped_column(String(20), default="unknown", nullable=False)
    geometry = mapped_column(Geometry("LINESTRING", srid=4326, spatial_index=True), nullable=False)


class Ward(Base):
    __tablename__ = "wards"
    id: Mapped[int] = mapped_column(primary_key=True)
    ward_no: Mapped[str | None] = mapped_column(String(30), index=True)
    zone_name: Mapped[str | None] = mapped_column(String(120))
    zone_no: Mapped[str | None] = mapped_column(String(50))
    source_type: Mapped[str] = mapped_column(String(20), default="real", nullable=False)
    geometry = mapped_column(Geometry("MULTIPOLYGON", srid=4326, spatial_index=True), nullable=False)


class DrainageNode(Base):
    __tablename__ = "drainage_nodes"
    id: Mapped[int] = mapped_column(primary_key=True)
    node_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    node_type: Mapped[str] = mapped_column(String(40), nullable=False)
    ward: Mapped[str | None] = mapped_column(String(30))
    ground_level_m: Mapped[float | None] = mapped_column(Float)
    invert_level_m: Mapped[float | None] = mapped_column(Float)
    manhole_depth_m: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    source_type: Mapped[str] = mapped_column(String(20), default="synthetic", nullable=False)
    geometry = mapped_column(Geometry("POINT", srid=4326, spatial_index=True), nullable=False)


class DrainageEdge(Base):
    __tablename__ = "drainage_edges"
    id: Mapped[int] = mapped_column(primary_key=True)
    edge_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    from_node: Mapped[str] = mapped_column(ForeignKey("drainage_nodes.node_id"), nullable=False)
    to_node: Mapped[str] = mapped_column(ForeignKey("drainage_nodes.node_id"), nullable=False)
    pipe_type: Mapped[str] = mapped_column(String(50), nullable=False)
    diameter_or_width_m: Mapped[float | None] = mapped_column(Float)
    length_m: Mapped[float | None] = mapped_column(Float)
    slope_percent: Mapped[float | None] = mapped_column(Float)
    material: Mapped[str | None] = mapped_column(String(50))
    condition: Mapped[str | None] = mapped_column(String(30))
    design_capacity_cumecs: Mapped[float | None] = mapped_column(Float)
    source_type: Mapped[str] = mapped_column(String(20), default="synthetic", nullable=False)
    geometry = mapped_column(Geometry("LINESTRING", srid=4326, spatial_index=True), nullable=True)


class RainfallObservation(Base):
    __tablename__ = "rainfall_observations"
    id: Mapped[int] = mapped_column(primary_key=True)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    zone_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    rainfall_mm_15min: Mapped[float] = mapped_column(Float, nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float)


class RainfallForecast(Base):
    __tablename__ = "rainfall_forecasts"
    id: Mapped[int] = mapped_column(primary_key=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    valid_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    lead_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    zone_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    forecast_mm_15min: Mapped[float] = mapped_column(Float, nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float)


class ForecastRun(Base):
    __tablename__ = "forecast_runs"
    id: Mapped[int] = mapped_column(primary_key=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    mode: Mapped[str] = mapped_column(String(30), nullable=False)
    model_version: Mapped[str] = mapped_column(String(80), nullable=False)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text)


class FloodPrediction(Base):
    __tablename__ = "flood_predictions"
    id: Mapped[int] = mapped_column(primary_key=True)
    forecast_run_id: Mapped[int] = mapped_column(ForeignKey("forecast_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    road_id: Mapped[str | None] = mapped_column(ForeignKey("roads.road_id"), index=True)
    valid_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    lead_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_depth_cm: Mapped[float] = mapped_column(Float, nullable=False)
    flood_probability: Mapped[float | None] = mapped_column(Float)
    risk_level: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    drainage_utilization: Mapped[float | None] = mapped_column(Float)
    confidence: Mapped[float | None] = mapped_column(Float)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    geometry = mapped_column(Geometry("LINESTRING", srid=4326, spatial_index=True), nullable=True)


class KnownHotspot(Base):
    __tablename__ = "known_hotspots"
    id: Mapped[int] = mapped_column(primary_key=True)
    location_name: Mapped[str] = mapped_column(String(255), nullable=False)
    area: Mapped[str | None] = mapped_column(String(120))
    event: Mapped[str | None] = mapped_column(String(160))
    severity_note: Mapped[str | None] = mapped_column(Text)
    source: Mapped[str | None] = mapped_column(String(255))
    source_type: Mapped[str] = mapped_column(String(20), default="real", nullable=False)
    geometry = mapped_column(Geometry("POINT", srid=4326, spatial_index=True), nullable=False)


class EmergencyFacility(Base):
    __tablename__ = "emergency_facilities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    facility_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(80))
    source_type: Mapped[str] = mapped_column(String(20), default="synthetic", nullable=False)
    geometry = mapped_column(Geometry("POINT", srid=4326, spatial_index=True), nullable=False)


class FloodReport(TimestampMixin, Base):
    __tablename__ = "flood_reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    water_depth_category: Mapped[str] = mapped_column(String(40), nullable=False)
    road_status: Mapped[str] = mapped_column(String(40), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column(Text)
    verification_status: Mapped[str] = mapped_column(String(30), default="unverified", nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default="SUBMITTED", nullable=False, index=True)
    admin_note: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[float | None] = mapped_column(Float)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    geometry = mapped_column(Geometry("POINT", srid=4326, spatial_index=True), nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    resource_type: Mapped[str | None] = mapped_column(String(80))
    resource_id: Mapped[str | None] = mapped_column(String(80))
    details_json: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


Index("ix_predictions_run_time_road", FloodPrediction.forecast_run_id, FloodPrediction.valid_time, FloodPrediction.road_id)
Index("ix_rainfall_forecast_zone_time", RainfallForecast.zone_id, RainfallForecast.valid_time)
