import sqlite3
import requests
import json
import time
import os
import base64
import cv2

class OfflineBufferSync:
    """
    Buffers detections locally when offline and syncs payload to FastAPI backend when connected.
    """
    def __init__(self, db_path="edge/edge_buffer.db", backend_url="http://localhost:8000"):
        self.db_path = db_path
        self.backend_url = backend_url.rstrip('/')
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS buffered_detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vehicle_id TEXT,
                latitude REAL,
                longitude REAL,
                speed_kmh REAL,
                class_name TEXT,
                confidence REAL,
                severity TEXT,
                bbox_json TEXT,
                image_base64 TEXT,
                detected_at TEXT,
                synced INTEGER DEFAULT 0
            )
        ''')
        conn.commit()
        conn.close()

    def add_detection(self, vehicle_id, gps_data, detection, frame=None):
        """
        Stores detection event in local SQLite buffer.
        """
        image_b64 = ""
        if frame is not None:
            # Encode frame to JPEG Base64 for transmission
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if ret:
                image_b64 = base64.b64encode(buffer).decode('utf-8')

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO buffered_detections 
            (vehicle_id, latitude, longitude, speed_kmh, class_name, confidence, severity, bbox_json, image_base64, detected_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        ''', (
            vehicle_id,
            gps_data['latitude'],
            gps_data['longitude'],
            gps_data.get('speed_kmh', 0.0),
            detection['class_name'],
            detection['confidence'],
            detection['severity'],
            json.dumps(detection['bbox_normalized']),
            image_b64
        ))
        conn.commit()
        conn.close()

    def sync_pending(self):
        """
        Tries sending un-synced detections to FastAPI backend API.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM buffered_detections WHERE synced = 0 LIMIT 20')
        rows = cursor.fetchall()
        
        if not rows:
            conn.close()
            return 0

        synced_ids = []
        for row in rows:
            payload = {
                "vehicle_id": row["vehicle_id"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "speed_kmh": row["speed_kmh"],
                "class_name": row["class_name"],
                "confidence": row["confidence"],
                "severity": row["severity"],
                "bbox": json.loads(row["bbox_json"]),
                "image_base64": row["image_base64"],
                "detected_at": row["detected_at"]
            }
            
            try:
                res = requests.post(f"{self.backend_url}/api/v1/detections", json=payload, timeout=4)
                if res.status_code in [200, 201]:
                    synced_ids.append(row["id"])
            except Exception:
                # Backend currently offline, stop attempt until next loop
                break

        if synced_ids:
            cursor.execute(f'UPDATE buffered_detections SET synced = 1 WHERE id IN ({",".join("?" * len(synced_ids))})', synced_ids)
            conn.commit()

        conn.close()
        return len(synced_ids)
