"""
Central configuration for the RoadWatch edge daemon.

Paths are resolved relative to this file so the daemon works whether you run
`python main.py` from inside `edge/` or from the repository root.
"""
from pathlib import Path

# Base directories (always absolute, independent of current working directory)
EDGE_DIR = Path(__file__).resolve().parent
DATA_DIR = EDGE_DIR / "data"
MODELS_DIR = EDGE_DIR / "models"

# SQLite offline buffer
DEFAULT_DB_PATH = DATA_DIR / "edge_buffer.db"

# ML model assets (Teammate 2 copies trained weights here)
DEFAULT_MODEL_PATH = MODELS_DIR / "best_int8.tflite"
DEFAULT_LABELS_PATH = MODELS_DIR / "labels.txt"

# Backend API (Teammate 3 owns the server; edge only posts to this endpoint)
DEFAULT_BACKEND_URL = "http://localhost:8000"
DETECTIONS_ENDPOINT = "/api/v1/detections"
HEALTH_ENDPOINT = "/"

# Edge behaviour defaults
DEFAULT_VEHICLE_ID = "MUNI-GARBAGE-VEH-04"
DEFAULT_SCAN_INTERVAL_SEC = 2.0
DEFAULT_CONFIDENCE_THRESHOLD = 0.5

# Duplicate suppression on the edge (backend also deduplicates within 10 m)
DUPLICATE_COOLDOWN_SEC = 45
DUPLICATE_RADIUS_METERS = 15.0

# Network checks
BACKEND_CHECK_TIMEOUT_SEC = 4.0
SYNC_BATCH_SIZE = 20
SYNC_REQUEST_TIMEOUT_SEC = 8.0
