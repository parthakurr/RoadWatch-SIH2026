from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from db import get_db
from models import PotholeDetection
from schemas import PotholeResponse, StatusUpdate

router = APIRouter(prefix="/api/v1/potholes", tags=["Pothole Management"])

@router.get("", response_model=List[PotholeResponse])
def get_potholes(
    severity: Optional[str] = Query(None, description="Filter by HIGH, MEDIUM, LOW"),
    status: Optional[str] = Query(None, description="Filter by PENDING, ASSIGNED, IN_REPAIR, VERIFIED_FIXED"),
    vehicle_id: Optional[str] = Query(None),
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(PotholeDetection)
    if severity:
        query = query.filter(PotholeDetection.severity == severity.upper())
    if status:
        query = query.filter(PotholeDetection.status == status.upper())
    if vehicle_id:
        query = query.filter(PotholeDetection.vehicle_id == vehicle_id)
    
    return query.order_by(PotholeDetection.last_scanned_at.desc()).limit(limit).all()

@router.get("/{pothole_id}", response_model=PotholeResponse)
def get_pothole_by_id(pothole_id: int, db: Session = Depends(get_db)):
    pothole = db.query(PotholeDetection).filter(PotholeDetection.id == pothole_id).first()
    if not pothole:
        raise HTTPException(status_code=404, detail="Pothole record not found")
    return pothole

@router.patch("/{pothole_id}/status", response_model=PotholeResponse)
def update_pothole_status(pothole_id: int, payload: StatusUpdate, db: Session = Depends(get_db)):
    pothole = db.query(PotholeDetection).filter(PotholeDetection.id == pothole_id).first()
    if not pothole:
        raise HTTPException(status_code=404, detail="Pothole record not found")
    
    pothole.status = payload.status.upper()
    if payload.assigned_contractor:
        pothole.assigned_contractor = payload.assigned_contractor
    if payload.notes:
        pothole.notes = payload.notes

    db.commit()
    db.refresh(pothole)
    return pothole

@router.post("/{pothole_id}/verify-repair", response_model=PotholeResponse)
def verify_repair(pothole_id: int, db: Session = Depends(get_db)):
    """
    Manually or automatically marks a pothole repair as VERIFIED_FIXED after successful vehicle re-scan.
    """
    pothole = db.query(PotholeDetection).filter(PotholeDetection.id == pothole_id).first()
    if not pothole:
        raise HTTPException(status_code=404, detail="Pothole record not found")

    pothole.status = "VERIFIED_FIXED"
    pothole.notes = (pothole.notes or "") + f" [Repair verified by auto-rescan at {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}]"
    
    db.commit()
    db.refresh(pothole)
    return pothole
