from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select

from ..database import get_db
from ..models import FloodReport, User
from ..schemas import ReportStatusUpdate
from geoalchemy2.shape import to_shape
from .dependencies import require_admin

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/status")
def admin_status(user: User = Depends(require_admin)) -> dict:
    return {"ok": True, "role": user.role, "message": "Admin access confirmed"}


@router.get("/reports", response_model=list[dict])
def moderation_reports(user: User = Depends(require_admin), db=Depends(get_db)) -> list[dict]:
    reports = db.scalars(select(FloodReport).order_by(FloodReport.updated_at.desc()).limit(500)).all()
    return [{"id": r.id, "latitude": to_shape(r.geometry).y, "longitude": to_shape(r.geometry).x, "water_depth_category": r.water_depth_category, "road_status": r.road_status, "verification_status": r.verification_status, "status": r.status, "admin_note": r.admin_note, "photo_url": r.photo_url, "confidence": r.confidence, "observed_at": r.observed_at, "user_id": r.user_id} for r in reports]


@router.patch("/reports/{report_id}", response_model=dict)
def update_report_status(report_id: int, payload: ReportStatusUpdate, user: User = Depends(require_admin), db=Depends(get_db)) -> dict:
    report = db.get(FloodReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    report.status = payload.status
    report.verification_status = "verified" if payload.status in {"ACKNOWLEDGED", "COMPLETED"} else ("rejected" if payload.status == "REJECTED" else "under_review")
    report.admin_note = payload.admin_note
    db.commit()
    db.refresh(report)
    return {"id": report.id, "status": report.status, "verification_status": report.verification_status, "admin_note": report.admin_note}


@router.delete("/reports/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report(report_id: int, user: User = Depends(require_admin), db=Depends(get_db)) -> Response:
    report = db.get(FloodReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    db.delete(report)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
