import logging
import random
import time

logger = logging.getLogger(__name__)


class GPSManager:
    """
    Handles Neo-6M GPS serial reading or simulated municipal vehicle route telemetry.
    """

    def __init__(self, mock=False, port="/dev/ttyS0", baudrate=9600):
        self.mock = mock
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None

        self.current_lat = 28.6139
        self.current_lng = 77.2090

        if mock:
            logger.info("[GPS] Mock GPS enabled")
        else:
            try:
                import serial

                self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
                logger.info("[GPS] Connected to serial GPS at %s", self.port)
            except Exception as exc:
                logger.warning("[GPS] Serial GPS connection failed (%s) — switching to mock GPS", exc)
                self.mock = True
                logger.info("[GPS] Mock GPS enabled")

    def get_coordinates(self):
        """
        Returns dict:
        {'latitude': float, 'longitude': float, 'speed_kmh': float, 'valid': bool, 'timestamp': float}
        """
        if not self.mock and self.serial_conn:
            try:
                import pynmea2

                line = self.serial_conn.readline().decode("ascii", errors="replace")
                if line.startswith("$GPRMC") or line.startswith("$GPGGA"):
                    msg = pynmea2.parse(line)
                    if hasattr(msg, "latitude") and msg.latitude != 0.0:
                        return {
                            "latitude": round(msg.latitude, 6),
                            "longitude": round(msg.longitude, 6),
                            "speed_kmh": round(getattr(msg, "spd_over_grnd", 0.0) * 1.852, 1),
                            "valid": True,
                            "timestamp": time.time(),
                        }
            except Exception as exc:
                logger.debug("[GPS] Serial read failed: %s", exc)

        return self._get_mock_coordinates()

    def _get_mock_coordinates(self):
        self.current_lat += (random.random() - 0.48) * 0.0003
        self.current_lng += (random.random() - 0.48) * 0.0003

        return {
            "latitude": round(self.current_lat, 6),
            "longitude": round(self.current_lng, 6),
            "speed_kmh": round(18.5 + random.uniform(-3.0, 4.0), 1),
            "valid": True,
            "timestamp": time.time(),
        }

    def close(self):
        if self.serial_conn:
            self.serial_conn.close()
