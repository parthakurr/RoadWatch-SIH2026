# RoadWatch — AI-Powered Pothole Detection & Municipal Road Governance System

[![SIH 2026](https://img.shields.io/badge/SIH-2026-amber)](https://sih.gov.in)
[![Edge AI](https://img.shields.io/badge/Edge%20AI-Raspberry%20Pi%204-red)](#)
[![Stack](https://img.shields.io/badge/Stack-FastAPI%20%7C%20React%20%7C%20YOLOv8%20%7C%20Leaflet-blue)](#)

RoadWatch mounts a camera + Neo-6M GPS unit on municipal garbage/public vehicles. Using on-device Edge AI, it automatically detects road defects (potholes, cracks), auto geo-tags them, deduplicates occurrences within 10 meters, and streams actionable alerts to municipal road departments — eliminating reliance on citizen complaints.

---

## 📁 Repository Structure

```
roadwatch/
├── backend/            # FastAPI central server, SQLite DB, Spatial Deduplication API
│   ├── app/
│   │   ├── main.py     # API entry point & CORS
│   │   ├── db.py       # Haversine spatial distance calculation
│   │   ├── models.py   # PotholeDetection & Repair database schema
│   │   └── routers/    # Ingestion, Pothole management, and Municipal Analytics
│   ├── seed_sqlite.py  # Pure-Python database seeder (No extra dependencies needed)
│   └── requirements.txt
├── frontend/           # React GIS Command Center Dashboard (Leaflet + Tailwind)
│   ├── src/App.jsx     # Live Map Pins, Work Orders, & Analytics Dashboard
│   ├── index.html
│   └── package.json
├── edge/               # Raspberry Pi 4 Edge Service (Python Daemon)
│   ├── main.py         # Main daemon loop (--mock mode for testing without Pi)
│   ├── camera.py       # Picamera2 / OpenCV / Mock frame generator
│   ├── gps.py          # Neo-6M UART parser / Mock vehicle route generator
│   ├── detector.py     # TFLite INT8 / Computer vision defect classifier
│   └── sync.py         # Offline SQLite buffer & automatic server sync
├── ai_training/        # RDD2022 Pothole Dataset YOLOv8 Training Setup
│   └── README.md       # Google Colab T4 GPU step-by-step training guide
└── docs/               # Technical Documentation
    ├── RoadWatch-Hardware-Build-Guide.md  # Pi 4 wiring & modern rpicam OS setup
    └── Team-Role-Distribution.md          # 3-person team responsibility matrix
```

---

## 🚀 Quick Start Instructions

### 1. Central Backend Server (`/backend`)
```bash
cd backend
pip install -r requirements.txt
python3 seed_sqlite.py    # Pre-populate sample municipal road damage data
python3 app/main.py       # Starts API at http://localhost:8000
```

### 2. Department GIS Dashboard (`/frontend`)
```bash
cd frontend
npm install
npm run dev               # Starts dashboard at http://localhost:3000
```

### 3. Edge AI Vehicle Daemon (`/edge`)

#### A. Test Mode on PC/Mac (Simulated Vehicle & Camera):
```bash
cd edge
python3 main.py --mock --backend-url http://localhost:8000
```

#### B. Production Deployment on Raspberry Pi 4:
```bash
cd edge
python3 main.py --backend-url http://<YOUR_SERVER_IP>:8000 --vehicle-id MUNI-VEH-01
```

---

## 🔥 Key Differentiators for SIH 2026 Judging
1. **On-Device Edge AI**: Runs inference locally on Raspberry Pi 4 — works without reliable 4G internet.
2. **Spatial Deduplication**: 10-meter radius Haversine algorithm merges multiple vehicle scans of the same pothole, tracking scan count and severity progression.
3. **Offline Buffer**: Detections in connectivity dead-zones are saved to local SQLite buffer and synced automatically when back online.
4. **Auto-Verification**: Re-scanning a fixed road segment auto-verifies contractor repairs without manual inspection.
