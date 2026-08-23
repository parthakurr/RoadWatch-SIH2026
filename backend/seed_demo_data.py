import os
import sys
from datetime import datetime, timedelta
import random

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from db import SessionLocal, Base, engine
from models import PotholeDetection

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing demo data
    db.query(PotholeDetection).delete()
    db.commit()

    print("[Seed] Populating sample municipal road damage data (New Delhi area)...")

    # Center coords around New Delhi
    center_lat = 28.6139
    center_lng = 77.2090

    vehicles = ["MUNI-GARBAGE-VEH-01", "MUNI-GARBAGE-VEH-02", "MUNI-GARBAGE-VEH-04", "MUNI-ROAD-INSPECT-09"]
    severities = ["HIGH", "HIGH", "MEDIUM", "MEDIUM", "LOW"]
    statuses = ["PENDING", "PENDING", "ASSIGNED", "IN_REPAIR", "VERIFIED_FIXED"]
    
    sample_records = [
        # High severity critical potholes
        {"lat_offset": 0.0042, "lng_offset": 0.0031, "sev": "HIGH", "status": "PENDING", "class": "Pothole", "scans": 4, "conf": 0.94, "veh": vehicles[0]},
        {"lat_offset": -0.0031, "lng_offset": 0.0062, "sev": "HIGH", "status": "IN_REPAIR", "class": "Pothole", "scans": 7, "conf": 0.91, "veh": vehicles[2]},
        {"lat_offset": 0.0085, "lng_offset": -0.0041, "sev": "HIGH", "status": "PENDING", "class": "Pothole", "scans": 3, "conf": 0.89, "veh": vehicles[1]},
        
        # Medium severity potholes & alligator cracks
        {"lat_offset": -0.0051, "lng_offset": -0.0022, "sev": "MEDIUM", "status": "ASSIGNED", "class": "Alligator Crack", "scans": 2, "conf": 0.83, "veh": vehicles[0]},
        {"lat_offset": 0.0019, "lng_offset": 0.0088, "sev": "MEDIUM", "status": "PENDING", "class": "Pothole", "scans": 2, "conf": 0.78, "veh": vehicles[3]},
        {"lat_offset": -0.0072, "lng_offset": 0.0035, "sev": "MEDIUM", "status": "PENDING", "class": "Transverse Crack", "scans": 1, "conf": 0.81, "veh": vehicles[2]},

        # Low severity longitudinal cracks
        {"lat_offset": 0.0061, "lng_offset": 0.0012, "sev": "LOW", "status": "PENDING", "class": "Longitudinal Crack", "scans": 1, "conf": 0.76, "veh": vehicles[1]},
        {"lat_offset": -0.0021, "lng_offset": -0.0081, "sev": "LOW", "status": "PENDING", "class": "Pothole", "scans": 1, "conf": 0.74, "veh": vehicles[3]},

        # Verified Fixed repairs
        {"lat_offset": 0.0032, "lng_offset": -0.0065, "sev": "HIGH", "status": "VERIFIED_FIXED", "class": "Pothole", "scans": 12, "conf": 0.96, "veh": vehicles[0]},
        {"lat_offset": -0.0088, "lng_offset": -0.0042, "sev": "MEDIUM", "status": "VERIFIED_FIXED", "class": "Pothole", "scans": 6, "conf": 0.88, "veh": vehicles[2]},
    ]

    for item in sample_records:
        rec = PotholeDetection(
            vehicle_id=item["veh"],
            latitude=round(center_lat + item["lat_offset"], 6),
            longitude=round(center_lng + item["lng_offset"], 6),
            speed_kmh=round(random.uniform(15.0, 24.0), 1),
            class_name=item["class"],
            confidence=item["conf"],
            severity=item["sev"],
            status=item["status"],
            scan_count=item["scans"],
            first_detected_at=datetime.utcnow() - timedelta(hours=random.randint(4, 72)),
            last_scanned_at=datetime.utcnow() - timedelta(minutes=random.randint(10, 240)),
            assigned_contractor="PWD Contractor Zone 4" if item["status"] in ["ASSIGNED", "IN_REPAIR"] else None
        )
        db.add(rec)

    db.commit()
    db.close()
    print("✅ [Seed] Successfully added 10 sample road damage records with coordinates & statuses.")

if __name__ == "__main__":
    seed()
