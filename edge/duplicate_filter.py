"""
Simple duplicate suppression so consecutive frames do not spam incidents.
"""
import logging
import math
import time
from typing import Any, Dict, Optional

from config import DUPLICATE_COOLDOWN_SEC, DUPLICATE_RADIUS_METERS

logger = logging.getLogger(__name__)


def haversine_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distance between two GPS points in meters."""
    radius = 6371000.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius * math.atan2(math.sqrt(a), math.sqrt(1 - a))


class DuplicateFilter:
    """
    Suppresses repeated detections of the same pothole using GPS proximity
    and a time cooldown window.
    """

    def __init__(
        self,
        cooldown_sec: float = DUPLICATE_COOLDOWN_SEC,
        radius_meters: float = DUPLICATE_RADIUS_METERS,
    ):
        self.cooldown_sec = cooldown_sec
        self.radius_meters = radius_meters
        self._last_lat: Optional[float] = None
        self._last_lng: Optional[float] = None
        self._last_time: float = 0.0

    def should_create_incident(self, gps_data: Dict[str, Any]) -> bool:
        now = time.time()
        lat = gps_data["latitude"]
        lng = gps_data["longitude"]

        if self._last_lat is not None and self._last_lng is not None:
            distance = haversine_meters(self._last_lat, self._last_lng, lat, lng)
            elapsed = now - self._last_time
            if distance <= self.radius_meters and elapsed < self.cooldown_sec:
                logger.info(
                    "[DETECTION] Duplicate suppressed (%.1fm away, %.0fs since last incident)",
                    distance,
                    elapsed,
                )
                return False

        self._last_lat = lat
        self._last_lng = lng
        self._last_time = now
        return True
