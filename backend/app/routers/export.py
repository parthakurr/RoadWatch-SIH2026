from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
import csv
import io

from db import get_db
from models import PotholeDetection

router = APIRouter(prefix="/api/v1/export", tags=["Export & Reports"])


@router.get("/csv")
def export_csv(
    severity: Optional[str] = Query(None, description="Filter by HIGH, MEDIUM, LOW"),
    status: Optional[str] = Query(None, description="Filter by PENDING, ASSIGNED, IN_REPAIR, VERIFIED_FIXED"),
    db: Session = Depends(get_db)
):
    """
    Exports pothole data as a CSV audit report for municipal contractors.
    Supports optional severity and status filters.
    """
    query = db.query(PotholeDetection)
    if severity:
        query = query.filter(PotholeDetection.severity == severity.upper())
    if status:
        query = query.filter(PotholeDetection.status == status.upper())

    records = query.order_by(PotholeDetection.last_scanned_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Defect Class", "Severity", "Latitude", "Longitude",
        "Status", "Scan Count", "Confidence %", "Assigned Contractor",
        "First Detected", "Last Scanned", "Vehicle ID", "Notes"
    ])

    for r in records:
        writer.writerow([
            r.id,
            r.class_name,
            r.severity,
            r.latitude,
            r.longitude,
            r.status,
            r.scan_count,
            round(r.confidence * 100, 1),
            r.assigned_contractor or "",
            r.first_detected_at.strftime("%Y-%m-%d %H:%M") if r.first_detected_at else "",
            r.last_scanned_at.strftime("%Y-%m-%d %H:%M") if r.last_scanned_at else "",
            r.vehicle_id,
            r.notes or ""
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=RoadEye_Audit_Report.csv"}
    )
