import argparse
import logging
import sys
import time

from camera import CameraManager
from config import DEFAULT_BACKEND_URL, DEFAULT_SCAN_INTERVAL_SEC, DEFAULT_VEHICLE_ID
from detector import RoadDamageDetector
from duplicate_filter import DuplicateFilter
from gps import GPSManager
from sync import OfflineBufferSync


def configure_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="RoadWatch Edge AI Daemon (Raspberry Pi 4)")
    parser.add_argument("--mock", action="store_true", help="Run with mock camera & GPS generators")
    parser.add_argument("--mock-offline", action="store_true", help="Simulate no backend connectivity")
    parser.add_argument("--backend-url", default=DEFAULT_BACKEND_URL, help="FastAPI Backend URL")
    parser.add_argument("--vehicle-id", default=DEFAULT_VEHICLE_ID, help="Vehicle registration tag")
    parser.add_argument("--interval", type=float, default=DEFAULT_SCAN_INTERVAL_SEC, help="Scan loop interval (seconds)")
    parser.add_argument("--verbose", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    configure_logging(verbose=args.verbose)

    logger = logging.getLogger("edge")
    logger.info("[EDGE] Starting RoadWatch Edge Daemon")
    logger.info("[EDGE] Vehicle tag: %s", args.vehicle_id)
    logger.info("[EDGE] Backend URL: %s", args.backend_url)
    logger.info("[EDGE] Mode: %s", "MOCK SIMULATION" if args.mock else "HARDWARE (Pi 4)")

    camera = CameraManager(mock=args.mock)
    gps = GPSManager(mock=args.mock)
    detector = RoadDamageDetector()
    buffer_sync = OfflineBufferSync(
        backend_url=args.backend_url,
        mock_offline=args.mock_offline,
    )
    duplicate_filter = DuplicateFilter()

    try:
        while True:
            try:
                frame = camera.capture_frame()
            except Exception as exc:
                logging.getLogger("camera").warning("[CAMERA] Frame capture failed: %s", exc)
                time.sleep(args.interval)
                continue

            try:
                gps_data = gps.get_coordinates()
            except Exception as exc:
                logging.getLogger("gps").warning("[GPS] Location unavailable: %s", exc)
                gps_data = {
                    "latitude": 0.0,
                    "longitude": 0.0,
                    "speed_kmh": 0.0,
                    "valid": False,
                }

            if gps_data.get("valid", True):
                logging.getLogger("gps").debug(
                    "[GPS] Location acquired (%.6f, %.6f)",
                    gps_data["latitude"],
                    gps_data["longitude"],
                )

            try:
                detections = detector.detect(frame)
            except Exception as exc:
                logging.getLogger("detection").warning("[DETECTION] Inference failed: %s", exc)
                detections = []

            for det in detections:
                logging.getLogger("detection").info("[DETECTION] %s detected", det["class_name"])
                logging.getLogger("detection").info("[DETECTION] Confidence: %s", det["confidence"])

                if not gps_data.get("valid", True):
                    logging.getLogger("gps").warning("[GPS] Skipping incident — GPS not valid")
                    continue

                if not duplicate_filter.should_create_incident(gps_data):
                    continue

                buffer_sync.add_detection(args.vehicle_id, gps_data, det, frame)

            synced_count = buffer_sync.sync_pending()
            if synced_count > 0:
                logging.getLogger("sync").info("[SYNC] Synced %d incident(s) this cycle", synced_count)

            time.sleep(args.interval)

    except KeyboardInterrupt:
        logging.getLogger("edge").info("[EDGE] Shutting down cleanly")
        camera.release()
        gps.close()
        sys.exit(0)


if __name__ == "__main__":
    main()
