"""
Upload pending incidents to the central backend when the network is available.
"""
import json
import logging
from typing import Optional
from urllib.parse import urljoin

import requests

from config import (
    DEFAULT_BACKEND_URL,
    DEFAULT_DB_PATH,
    DETECTIONS_ENDPOINT,
    SYNC_BATCH_SIZE,
    SYNC_REQUEST_TIMEOUT_SEC,
)
from network import NetworkMonitor
from storage import IncidentStorage

logger = logging.getLogger(__name__)


class IncidentSync:
    """Syncs locally stored incidents to the FastAPI backend."""

    def __init__(
        self,
        storage: IncidentStorage,
        network: NetworkMonitor,
        backend_url: str = DEFAULT_BACKEND_URL,
    ):
        self.storage = storage
        self.network = network
        self.backend_url = backend_url.rstrip("/")
        self.upload_url = urljoin(self.backend_url + "/", DETECTIONS_ENDPOINT.lstrip("/"))

    def sync_pending(self) -> int:
        """
        Upload pending incidents when the backend is reachable.
        Returns the number of incidents successfully synced.
        """
        if not self.network.is_backend_reachable():
            return 0

        rows = self.storage.get_pending_incidents(limit=SYNC_BATCH_SIZE)
        if not rows:
            return 0

        synced_count = 0
        for row in rows:
            payload = {
                "vehicle_id": row["vehicle_id"],
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "speed_kmh": row["speed_kmh"],
                "class_name": row["class_name"],
                "confidence": row["confidence"],
                "severity": row["severity"],
                "bbox": json.loads(row["bbox_json"]) if row["bbox_json"] else None,
                "image_base64": row["image_base64"],
                "detected_at": row["detected_at"],
            }

            logger.info("[SYNC] Uploading pending incident (db_id=%s)", row["id"])
            try:
                response = requests.post(
                    self.upload_url,
                    json=payload,
                    timeout=SYNC_REQUEST_TIMEOUT_SEC,
                )
                if response.status_code in (200, 201):
                    self.storage.mark_synced(row["id"])
                    synced_count += 1
                    logger.info("[SYNC] Incident synchronized successfully (db_id=%s)", row["id"])
                else:
                    error = f"HTTP {response.status_code}: {response.text[:200]}"
                    self.storage.record_sync_failure(row["id"], error)
                    logger.warning("[SYNC] Upload failed for db_id=%s — %s", row["id"], error)
                    break
            except requests.RequestException as exc:
                self.storage.record_sync_failure(row["id"], str(exc))
                logger.warning("[SYNC] Upload error for db_id=%s — %s", row["id"], exc)
                break

        return synced_count


class OfflineBufferSync:
    """
    Backward-compatible facade used by main.py.
    Combines local storage, network checks, and upload retries.
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        backend_url: str = DEFAULT_BACKEND_URL,
        mock_offline: bool = False,
    ):
        resolved_db = DEFAULT_DB_PATH if db_path is None else db_path
        self.storage = IncidentStorage(db_path=resolved_db)
        self.network = NetworkMonitor(backend_url=backend_url, mock_offline=mock_offline)
        self.sync = IncidentSync(self.storage, self.network, backend_url=backend_url)

    def add_detection(self, vehicle_id, gps_data, detection, frame=None):
        import base64

        import cv2

        image_b64 = ""
        if frame is not None:
            ok, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            if ok:
                image_b64 = base64.b64encode(buffer).decode("utf-8")

        return self.storage.save_incident(vehicle_id, gps_data, detection, image_b64)

    def sync_pending(self) -> int:
        return self.sync.sync_pending()

    def is_online(self) -> bool:
        return self.network.is_backend_reachable()

    @property
    def pending_count(self) -> int:
        return self.storage.count_pending()
