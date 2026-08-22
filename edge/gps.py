import time
import random

class GPSManager:
    """
    Handles Neo-6M GPS serial reading or simulated municipal vehicle route telemetry.
    """
    def __init__(self, mock=False, port="/dev/ttyS0", baudrate=9600):
        self.mock = mock
        self.port = port
        self.baudrate = baudrate
        self.serial_conn = None
        
        # Default mock starting coordinates (New Delhi / Municipal Ward area)
        self.current_lat = 28.6139
        self.current_lng = 77.2090
        
        if not self.mock:
            try:
                import serial
                self.serial_conn = serial.Serial(self.port, self.baudrate, timeout=1)
                print(f"[GPSManager] Connected to serial GPS at {self.port}")
            except Exception as e:
                print(f"[GPSManager] Serial GPS connection failed ({e}). Switching to Mock GPS.")
                self.mock = True

    def get_coordinates(self):
        """
        Returns dict: {'latitude': float, 'longitude': float, 'speed_kmh': float, 'valid': bool}
        """
        if not self.mock and self.serial_conn:
            try:
                import pynmea2
                line = self.serial_conn.readline().decode('ascii', errors='replace')
                if line.startswith('$GPRMC') or line.startswith('$GPGGA'):
                    msg = pynmea2.parse(line)
                    if hasattr(msg, 'latitude') and msg.latitude != 0.0:
                        return {
                            'latitude': round(msg.latitude, 6),
                            'longitude': round(msg.longitude, 6),
                            'speed_kmh': round(getattr(msg, 'spd_over_grnd', 0.0) * 1.852, 1),
                            'valid': True
                        }
            except Exception:
                pass

        # Return simulated municipal vehicle trajectory
        return self._get_mock_coordinates()

    def _get_mock_coordinates(self):
        # Simulate slight vehicle motion along a city route
        self.current_lat += (random.random() - 0.48) * 0.0003
        self.current_lng += (random.random() - 0.48) * 0.0003
        
        return {
            'latitude': round(self.current_lat, 6),
            'longitude': round(self.current_lng, 6),
            'speed_kmh': round(18.5 + random.uniform(-3.0, 4.0), 1),
            'valid': True
        }

    def close(self):
        if self.serial_conn:
            self.serial_conn.close()
