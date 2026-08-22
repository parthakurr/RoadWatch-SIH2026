import argparse
import time
import os
import sys

from camera import CameraManager
from gps import GPSManager
from detector import RoadDamageDetector
from sync import OfflineBufferSync

def main():
    parser = argparse.ArgumentParser(description="RoadWatch Edge AI Daemon (Raspberry Pi 4)")
    parser.add_argument("--mock", action="store_true", help="Run with mock camera & GPS generators")
    parser.add_argument("--backend-url", default="http://localhost:8000", help="FastAPI Backend URL")
    parser.add_argument("--vehicle-id", default="MUNI-GARBAGE-VEH-04", help="Vehicle Registration Tag")
    parser.add_argument("--interval", type=float, default=2.0, help="Scan loop interval in seconds")
    args = parser.parse_args()

    print("==================================================")
    print("      🚀 ROADWATCH EDGE AI UNIT INITIALIZING       ")
    print("==================================================")
    print(f" Vehicle Tag : {args.vehicle_id}")
    print(f" Backend URL : {args.backend_url}")
    print(f" Mode        : {'MOCK SIMULATION' if args.mock else 'HARDWARE (Pi 4)'}")
    print("==================================================")

    camera = CameraManager(mock=args.mock)
    gps = GPSManager(mock=args.mock)
    detector = RoadDamageDetector()
    buffer_sync = OfflineBufferSync(backend_url=args.backend_url)

    try:
        scan_count = 0
        while True:
            scan_count += 1
            # 1. Capture frame from camera module
            frame = camera.capture_frame()
            
            # 2. Get current GPS telemetry
            gps_data = gps.get_coordinates()

            # 3. Perform Edge AI road damage detection
            detections = detector.detect(frame)

            if detections:
                for det in detections:
                    print(f"⚠️ [{time.strftime('%H:%M:%S')}] {det['severity']} {det['class_name']} detected! "
                          f"Conf: {det['confidence']} | GPS: ({gps_data['latitude']}, {gps_data['longitude']})")
                    
                    # Store in offline DB buffer
                    buffer_sync.add_detection(args.vehicle_id, gps_data, det, frame)

            # 4. Sync buffered records to central backend if online
            synced_count = buffer_sync.sync_pending()
            if synced_count > 0:
                print(f"✅ [{time.strftime('%H:%M:%S')}] Synced {synced_count} detection(s) to central server.")

            time.sleep(args.interval)

    except KeyboardInterrupt:
        print("\n[Edge Daemon] Shutting down cleanly.")
        camera.release()
        gps.close()
        sys.exit(0)

if __name__ == "__main__":
    main()
