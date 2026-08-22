"""
SQLite storage for pothole incidents captured while offline or awaiting sync.
"""
import json
import logging
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import DEFAULT_DB_PATH

logger = logging.getLogger(__name__)

SYNC_STATUS_PENDING = "PENDING"
SYNC_STATUS_SYNCED = "SYNCED"


def ensure_data_directory(db_path: Path) -> None:
    """Create the parent folder for the SQLite file if it does not exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)


class IncidentStorage:
    """Persistent local store for edge pothole incidents."""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path or DEFAULT_DB_PATH)
        ensure_data_directory(self.db_path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        ensure_data_directory(self.db_path)
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS buffered_detections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    incident_id TEXT UNIQUE NOT NULL,
                    vehicle_id TEXT NOT NULL,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    speed_kmh REAL,
                    class_name TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    severity TEXT NOT NULL,
                    bbox_json TEXT,
                    image_base64 TEXT,
                    detected_at TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    sync_status TEXT NOT NULL DEFAULT 'PENDING',
                    synced INTEGER NOT NULL DEFAULT 0,
                    last_sync_attempt_at TEXT,
                    sync_error TEXT
                )
                """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_buffered_sync_status
                ON buffered_detections(sync_status)
                """
            )
            conn.commit()
            logger.info("[STORAGE] SQLite ready at %s", self.db_path)
        finally:
            conn.close()

    def save_incident(
        self,
        vehicle_id: str,
        gps_data: Dict[str, Any],
        detection: Dict[str, Any],
        image_base64: str = "",
    ) -> str:
        """Save a new incident locally. Returns the unique incident_id."""
        incident_id = str(uuid.uuid4())
        detected_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        created_at = detected_at

        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO buffered_detections (
                    incident_id, vehicle_id, latitude, longitude, speed_kmh,
                    class_name, confidence, severity, bbox_json, image_base64,
                    detected_at, created_at, sync_status, synced
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    incident_id,
                    vehicle_id,
                    gps_data["latitude"],
                    gps_data["longitude"],
                    gps_data.get("speed_kmh", 0.0),
                    detection["class_name"],
                    detection["confidence"],
                    detection["severity"],
                    json.dumps(detection.get("bbox_normalized") or detection.get("bbox")),
                    image_base64,
                    detected_at,
                    created_at,
                    SYNC_STATUS_PENDING,
                    0,
                ),
            )
            conn.commit()
            logger.info("[STORAGE] Incident saved locally (id=%s, status=PENDING)", incident_id)
            return incident_id
        finally:
            conn.close()

    def get_pending_incidents(self, limit: int = 20) -> List[sqlite3.Row]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM buffered_detections
                WHERE sync_status = ? OR synced = 0
                ORDER BY id ASC
                LIMIT ?
                """,
                (SYNC_STATUS_PENDING, limit),
            )
            return cursor.fetchall()
        finally:
            conn.close()

    def mark_synced(self, row_id: int) -> None:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE buffered_detections
                SET sync_status = ?, synced = 1, sync_error = NULL,
                    last_sync_attempt_at = datetime('now')
                WHERE id = ?
                """,
                (SYNC_STATUS_SYNCED, row_id),
            )
            conn.commit()
        finally:
            conn.close()

    def record_sync_failure(self, row_id: int, error_message: str) -> None:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE buffered_detections
                SET last_sync_attempt_at = datetime('now'), sync_error = ?
                WHERE id = ?
                """,
                (error_message[:500], row_id),
            )
            conn.commit()
        finally:
            conn.close()

    def count_pending(self) -> int:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT COUNT(*) FROM buffered_detections
                WHERE sync_status = ? OR synced = 0
                """,
                (SYNC_STATUS_PENDING,),
            )
            return int(cursor.fetchone()[0])
        finally:
            conn.close()

    def get_incident_by_id(self, incident_id: str) -> Optional[sqlite3.Row]:
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM buffered_detections WHERE incident_id = ?",
                (incident_id,),
            )
            return cursor.fetchone()
        finally:
            conn.close()
