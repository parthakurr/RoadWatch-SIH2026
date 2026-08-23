from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from datetime import datetime
from db import Base

class PotholeDetection(Base):
    __tablename__ = "pothole_detections"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(String(50), index=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    speed_kmh = Column(Float, default=0.0)
    class_name = Column(String(50), default="Pothole")
    confidence = Column(Float, nullable=False)
    severity = Column(String(20), default="MEDIUM") # HIGH, MEDIUM, LOW
    bbox_json = Column(Text, nullable=True)
    image_base64 = Column(Text, nullable=True)
    status = Column(String(30), default="PENDING") # PENDING, ASSIGNED, IN_REPAIR, VERIFIED_FIXED, RE_SCAN_NEEDED
    scan_count = Column(Integer, default=1)
    first_detected_at = Column(DateTime, default=datetime.utcnow)
    last_scanned_at = Column(DateTime, default=datetime.utcnow)
    assigned_contractor = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
