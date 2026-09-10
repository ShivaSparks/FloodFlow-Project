from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: str
    avatar_url: str | None = None


class ProfileUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    avatar_url: str | None = Field(default=None, max_length=2_000_000)


class FloodReportCreate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    water_depth_category: str = Field(min_length=2, max_length=40)
    road_status: str = Field(min_length=2, max_length=40)
    comment: str | None = Field(default=None, max_length=1000)
    photo_url: str | None = Field(default=None, max_length=2_000_000)
    observed_at: datetime


class FloodReportPublic(BaseModel):
    id: int
    latitude: float
    longitude: float
    water_depth_category: str
    road_status: str
    verification_status: str
    confidence: float | None
    observed_at: datetime
    latitude: float | None = None
    longitude: float | None = None
    status: str = "SUBMITTED"
    admin_note: str | None = None
    photo_url: str | None = None
    user_id: int | None = None


class ReportStatusUpdate(BaseModel):
    status: str = Field(pattern="^(SUBMITTED|UNDER_REVIEW|ACKNOWLEDGED|COMPLETED|REJECTED)$")
    admin_note: str | None = Field(default=None, max_length=1000)


class RouteRequest(BaseModel):
    start_latitude: float = Field(ge=-90, le=90)
    start_longitude: float = Field(ge=-180, le=180)
    end_latitude: float = Field(ge=-90, le=90)
    end_longitude: float = Field(ge=-180, le=180)
    transport: str = Field(default="driving", max_length=30)
    forecast_lead_minutes: int = Field(default=0, ge=0, le=180)
