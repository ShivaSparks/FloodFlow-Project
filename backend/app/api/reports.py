from fastapi import APIRouter, Depends, status
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import FloodReport, User
from ..schemas import FloodReportCreate, FloodReportPublic
from .dependencies import current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/flood", response_model=FloodReportPublic, status_code=status.HTTP_201_CREATED)
def create_flood_report(
    payload: FloodReportCreate,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
) -> dict:
    report = FloodReport(
        user_id=user.id,
        water_depth_category=payload.water_depth_category,
        road_status=payload.road_status,
        comment=payload.comment,
        photo_url=payload.photo_url,
        observed_at=payload.observed_at,
        geometry=from_shape(Point(payload.longitude, payload.latitude), srid=4326),
        verification_status="unverified",
        status="SUBMITTED",
        confidence=0.35,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return {
        "id": report.id,
        "latitude": payload.latitude,
        "longitude": payload.longitude,
        "water_depth_category": report.water_depth_category,
        "road_status": report.road_status,
        "verification_status": report.verification_status,
        "confidence": report.confidence,
        "observed_at": report.observed_at,
        "status": report.status,
        "admin_note": report.admin_note,
        "photo_url": report.photo_url,
        "user_id": report.user_id,
    }


def report_payload(report: FloodReport) -> dict:
    point = getattr(report, "geometry", None)
    latitude = longitude = None
    if point is not None:
        shaped = to_shape(point)
        longitude, latitude = shaped.x, shaped.y
    return {"id": report.id, "latitude": latitude, "longitude": longitude, "water_depth_category": report.water_depth_category, "road_status": report.road_status, "verification_status": report.verification_status, "status": report.status, "admin_note": report.admin_note, "photo_url": report.photo_url, "confidence": report.confidence, "observed_at": report.observed_at, "user_id": report.user_id}


@router.get("/flood", response_model=list[dict])
def list_flood_reports(db: Session = Depends(get_db)) -> list[dict]:
    reports = db.scalars(select(FloodReport).order_by(FloodReport.observed_at.desc()).limit(200)).all()
    return [report_payload(report) for report in reports]


@router.get("/mine", response_model=list[dict])
def list_my_reports(user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[dict]:
    reports = db.scalars(select(FloodReport).where(FloodReport.user_id == user.id).order_by(FloodReport.observed_at.desc())).all()
    return [report_payload(report) for report in reports]
