from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DetectionIngest(BaseModel):
    vehicle_id: str
    latitude: float
    longitude: float
    speed_kmh: Optional[float] = 0.0
    class_name: str = "Pothole"
    confidence: float
    severity: str = "MEDIUM"
    bbox: Optional[List[float]] = None
    image_base64: Optional[str] = None
    detected_at: Optional[str] = None

class PotholeResponse(BaseModel):
    id: int
    vehicle_id: str
    latitude: float
    longitude: float
    speed_kmh: float
    class_name: str
    confidence: float
    severity: str
    bbox_json: Optional[str]
    image_base64: Optional[str]
    status: str
    scan_count: int
    first_detected_at: datetime
    last_scanned_at: datetime
    assigned_contractor: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True

class StatusUpdate(BaseModel):
    status: str
    assigned_contractor: Optional[str] = None
    notes: Optional[str] = None

class AnalyticsSummary(BaseModel):
    total_potholes: int
    critical_high_count: int
    medium_count: int
    low_count: int
    repaired_count: int
    in_repair_count: int
    active_vehicles_count: int
    repair_rate_percentage: float
