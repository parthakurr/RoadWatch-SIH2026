"""
RoadWatch SIH 2026 — Live Edge AI Simulation Script
Simulates real-time defect detections streamed from Edge AI cameras mounted on municipal vehicles.
Demonstrates spatial deduplication, real-time map marker updates, and dynamic analytics.
"""

import time
import random
import requests
from datetime import datetime

API_ENDPOINT = "http://localhost:8000/api/v1/detections"

VEHICLES = [
    "MUNI-GARBAGE-VEH-01",
    "MUNI-GARBAGE-VEH-02",
    "MUNI-GARBAGE-VEH-04",
    "MUNI-ROAD-INSPECT-09",
    "MUNI-SWEEPER-VEH-07"
]

DEFECT_CLASSES = ["Pothole", "Alligator Crack", "Transverse Crack", "Longitudinal Crack"]
SEVERITIES = ["HIGH", "MEDIUM", "LOW"]

# Key locations in New Delhi
WAYPOINTS = [
    {"name": "Connaught Place Radial 3", "lat": 28.6295, "lng": 77.2185},
    {"name": "Janpath Road Junction", "lat": 28.6180, "lng": 77.2180},
    {"name": "Karol Bagh Market Road", "lat": 28.6510, "lng": 77.1900},
    {"name": "Lodhi Estate Road 2", "lat": 28.5920, "lng": 77.2210},
    {"name": "Paharganj Main Bazar", "lat": 28.6430, "lng": 77.2120},
    {"name": "India Gate Outer Ring", "lat": 28.6120, "lng": 77.2290},
]

def generate_detection():
    waypoint = random.choice(WAYPOINTS)
    # Slight GPS jitter within ~8 meters
    lat_jitter = random.uniform(-0.00007, 0.00007)
    lng_jitter = random.uniform(-0.00007, 0.00007)

    payload = {
        "vehicle_id": random.choice(VEHICLES),
        "latitude": round(waypoint["lat"] + lat_jitter, 6),
        "longitude": round(waypoint["lng"] + lng_jitter, 6),
        "speed_kmh": round(random.uniform(18.0, 38.0), 1),
        "class_name": random.choice(DEFECT_CLASSES),
        "confidence": round(random.uniform(0.75, 0.98), 2),
        "severity": random.choices(SEVERITIES, weights=[0.3, 0.5, 0.2])[0],
        "bbox": [
            round(random.uniform(100, 300), 1),
            round(random.uniform(150, 350), 1),
            round(random.uniform(80, 200), 1),
            round(random.uniform(60, 150), 1)
        ],
        "detected_at": datetime.utcnow().isoformat()
    }
    return payload, waypoint["name"]

def main():
    print("=" * 65)
    print("  🚀 RoadWatch SIH 2026 — Live Edge AI Fleet Stream Simulator")
    print("  📡 Streaming simulated road defects to FastAPI Backend...")
    print("  🌐 Target Endpoint:", API_ENDPOINT)
    print("=" * 65)
    print("Press Ctrl+C to stop simulation.\n")

    count = 1
    while True:
        try:
            payload, loc_name = generate_detection()
            res = requests.post(API_ENDPOINT, json=payload, timeout=5)

            if res.status_code == 201:
                data = res.json()
                scan_status = f"🔄 Re-scan (#{data.get('scan_count')}x)" if data.get('scan_count', 1) > 1 else "✨ New Defect"
                print(f"[{count:03d}] {datetime.now().strftime('%H:%M:%S')} | {payload['vehicle_id']} -> {payload['class_name']} ({payload['severity']}) @ {loc_name} | {scan_status} (ID: #{data.get('id')})")
            else:
                print(f"[{count:03d}] Server response status: {res.status_code}")

            count += 1
            time.sleep(random.uniform(2.5, 5.0))

        except requests.exceptions.ConnectionError:
            print("⚠️ Could not connect to FastAPI server. Make sure `python main.py` is running on port 8000.")
            time.sleep(4)
        except KeyboardInterrupt:
            print("\n🛑 Simulation stopped by user.")
            break
        except Exception as e:
            print("Error:", e)
            time.sleep(2)

if __name__ == "__main__":
    main()
