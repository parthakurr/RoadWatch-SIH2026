from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from db import get_db
from models import PotholeDetection
from schemas import AnalyticsSummary

router = APIRouter(prefix="/api/v1/analytics", tags=["Municipal Analytics"])

@router.get("/summary", response_model=AnalyticsSummary)
def get_analytics_summary(db: Session = Depends(get_db)):
    total_potholes = db.query(PotholeDetection).count()
    high_count = db.query(PotholeDetection).filter(PotholeDetection.severity == "HIGH").count()
    med_count = db.query(PotholeDetection).filter(PotholeDetection.severity == "MEDIUM").count()
    low_count = db.query(PotholeDetection).filter(PotholeDetection.severity == "LOW").count()
    
    repaired_count = db.query(PotholeDetection).filter(PotholeDetection.status == "VERIFIED_FIXED").count()
    in_repair_count = db.query(PotholeDetection).filter(PotholeDetection.status.in_(["ASSIGNED", "IN_REPAIR"])).count()
    
    # Distinct active vehicle count
    active_vehicles = db.query(func.count(func.distinct(PotholeDetection.vehicle_id))).scalar() or 0
    
    repair_rate = round((repaired_count / total_potholes * 100.0), 1) if total_potholes > 0 else 0.0

    return AnalyticsSummary(
        total_potholes=total_potholes,
        critical_high_count=high_count,
        medium_count=med_count,
        low_count=low_count,
        repaired_count=repaired_count,
        in_repair_count=in_repair_count,
        active_vehicles_count=active_vehicles,
        repair_rate_percentage=repair_rate
    )
