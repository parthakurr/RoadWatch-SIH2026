import sqlite3
from datetime import datetime, timedelta
import random
import os

db_path = os.path.join(os.path.dirname(__file__), 'roadwatch.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create table matching SQLAlchemy model
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pothole_detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vehicle_id TEXT,
        latitude REAL NOT NULL,
        longitude REAL NOT NULL,
        speed_kmh REAL DEFAULT 0.0,
        class_name TEXT DEFAULT 'Pothole',
        confidence REAL NOT NULL,
        severity TEXT DEFAULT 'MEDIUM',
        bbox_json TEXT,
        image_base64 TEXT,
        status TEXT DEFAULT 'PENDING',
        scan_count INTEGER DEFAULT 1,
        first_detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        assigned_contractor TEXT,
        notes TEXT
    )
''')

# Clear existing rows for fresh seed
cursor.execute('DELETE FROM pothole_detections')

print("[Seed SQLite] Populating sample municipal road damage data (New Delhi area)...")

center_lat = 28.6139
center_lng = 77.2090

vehicles = ["MUNI-GARBAGE-VEH-01", "MUNI-GARBAGE-VEH-02", "MUNI-GARBAGE-VEH-04", "MUNI-ROAD-INSPECT-09"]

sample_records = [
    {"lat_offset": 0.0042, "lng_offset": 0.0031, "sev": "HIGH", "status": "PENDING", "class": "Pothole", "scans": 4, "conf": 0.94, "veh": vehicles[0]},
    {"lat_offset": -0.0031, "lng_offset": 0.0062, "sev": "HIGH", "status": "IN_REPAIR", "class": "Pothole", "scans": 7, "conf": 0.91, "veh": vehicles[2]},
    {"lat_offset": 0.0085, "lng_offset": -0.0041, "sev": "HIGH", "status": "PENDING", "class": "Pothole", "scans": 3, "conf": 0.89, "veh": vehicles[1]},
    
    {"lat_offset": -0.0051, "lng_offset": -0.0022, "sev": "MEDIUM", "status": "ASSIGNED", "class": "Alligator Crack", "scans": 2, "conf": 0.83, "veh": vehicles[0]},
    {"lat_offset": 0.0019, "lng_offset": 0.0088, "sev": "MEDIUM", "status": "PENDING", "class": "Pothole", "scans": 2, "conf": 0.78, "veh": vehicles[3]},
    {"lat_offset": -0.0072, "lng_offset": 0.0035, "sev": "MEDIUM", "status": "PENDING", "class": "Transverse Crack", "scans": 1, "conf": 0.81, "veh": vehicles[2]},

    {"lat_offset": 0.0061, "lng_offset": 0.0012, "sev": "LOW", "status": "PENDING", "class": "Longitudinal Crack", "scans": 1, "conf": 0.76, "veh": vehicles[1]},
    {"lat_offset": -0.0021, "lng_offset": -0.0081, "sev": "LOW", "status": "PENDING", "class": "Pothole", "scans": 1, "conf": 0.74, "veh": vehicles[3]},

    {"lat_offset": 0.0032, "lng_offset": -0.0065, "sev": "HIGH", "status": "VERIFIED_FIXED", "class": "Pothole", "scans": 12, "conf": 0.96, "veh": vehicles[0]},
    {"lat_offset": -0.0088, "lng_offset": -0.0042, "sev": "MEDIUM", "status": "VERIFIED_FIXED", "class": "Pothole", "scans": 6, "conf": 0.88, "veh": vehicles[2]},
]

for item in sample_records:
    now = datetime.utcnow()
    cursor.execute('''
        INSERT INTO pothole_detections 
        (vehicle_id, latitude, longitude, speed_kmh, class_name, confidence, severity, status, scan_count, first_detected_at, last_scanned_at, assigned_contractor)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        item["veh"],
        round(center_lat + item["lat_offset"], 6),
        round(center_lng + item["lng_offset"], 6),
        round(random.uniform(15.0, 24.0), 1),
        item["class"],
        item["conf"],
        item["sev"],
        item["status"],
        item["scans"],
        (now - timedelta(hours=random.randint(4, 72))).strftime('%Y-%m-%d %H:%M:%S'),
        (now - timedelta(minutes=random.randint(10, 240))).strftime('%Y-%m-%d %H:%M:%S'),
        "PWD Contractor Zone 4" if item["status"] in ["ASSIGNED", "IN_REPAIR"] else None
    ))

conn.commit()
conn.close()
print("✅ [Seed SQLite] Database successfully initialized and seeded with 10 sample road damage records.")
