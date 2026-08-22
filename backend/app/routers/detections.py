from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import json

from db import get_db, haversine_distance
from models import PotholeDetection
from schemas import DetectionIngest, PotholeResponse

router = APIRouter(prefix="/api/v1/detections", tags=["Edge Ingestion"])

DEDUPLICATION_RADIUS_METERS = 10.0

@router.post("", response_model=PotholeResponse, status_code=status.HTTP_201_CREATED)
def ingest_detection(payload: DetectionIngest, db: Session = Depends(get_db)):
    """
    Ingests detection from Edge AI unit.
    Applies spatial deduplication (10-meter radius):
    - If a pothole already exists nearby, updates scan_count, last_scanned_at timestamp, and image.
    - If the pothole was previously marked IN_REPAIR or VERIFIED_FIXED, triggers re-scan flag.
    - Otherwise creates a new pothole entry.
    """
    # 1. Fetch recent active/pending potholes
    candidates = db.query(PotholeDetection).filter(
        PotholeDetection.status.in_(["PENDING", "ASSIGNED", "IN_REPAIR", "VERIFIED_FIXED"])
    ).all()

    existing_pothole = None
    for cand in candidates:
        dist = haversine_distance(payload.latitude, payload.longitude, cand.latitude, cand.longitude)
        if dist <= DEDUPLICATION_RADIUS_METERS:
            existing_pothole = cand
            break

    if existing_pothole:
        # Spatial Deduplication Match Found!
        existing_pothole.scan_count += 1
        existing_pothole.last_scanned_at = datetime.utcnow()
        
        # Upgrade severity if higher
        severity_order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
        if severity_order.get(payload.severity, 2) > severity_order.get(existing_pothole.severity, 2):
            existing_pothole.severity = payload.severity

        # Update snapshot if confidence is higher
        if payload.confidence > existing_pothole.confidence and payload.image_base64:
            existing_pothole.confidence = payload.confidence
            existing_pothole.image_base64 = payload.image_base64

        # If vehicle re-scanned a pothole marked IN_REPAIR but defect is still detected -> flag RE_SCAN_NEEDED
        if existing_pothole.status == "IN_REPAIR":
            existing_pothole.notes = (existing_pothole.notes or "") + " [Re-scan detected remaining road defect]"
            existing_pothole.status = "RE_SCAN_NEEDED"

        db.commit()
        db.refresh(existing_pothole)
        return existing_pothole

    # 2. Create new Pothole Record
    bbox_str = json.dumps(payload.bbox) if payload.bbox else None
    new_pothole = PotholeDetection(
        vehicle_id=payload.vehicle_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        speed_kmh=payload.speed_kmh or 0.0,
        class_name=payload.class_name,
        confidence=payload.confidence,
        severity=payload.severity,
        bbox_json=bbox_str,
        image_base64=payload.image_base64,
        status="PENDING",
        scan_count=1,
        first_detected_at=datetime.utcnow(),
        last_scanned_at=datetime.utcnow()
    )
    db.add(new_pothole)
    db.commit()
    db.refresh(new_pothole)
    return new_pothole
