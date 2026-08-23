# RoadWatch — 3-Person Team Task Allocation Matrix (SIH 2026)

This document breaks down the responsibilities across all 3 team members so every team member has a clear domain during development, pitch preparation, and live hackathon judging.

---

## 👤 Member 1: Hardware & Edge AI Lead (Embedded / IoT)

### Core Tasks:
- **Raspberry Pi 4 Setup**: Flash 64-bit OS, configure SSH, UART serial for GPS (`/dev/ttyS0`), and camera CSI interface.
- **Hardware Assembly**: Wire Neo-6M GPS module, mount camera module in IP65 enclosure with 20,000mAh power bank.
- **Edge Daemon (`edge/`)**: Test `edge/main.py` with physical hardware, calibrate camera angle on windshield, test offline SQLite buffer sync.
- **Hackathon Demo Duty**: Demonstrate live hardware unit to judges — hold camera over simulated pothole picture, show instant LED/terminal detection, and unplug Wi-Fi to prove offline SQLite buffering.

---

## 👤 Member 2: AI Model & Training Specialist (Computer Vision)

### Core Tasks:
- **Model Training (`ai_training/`)**: Run `train_yolov8_rdd2022.ipynb` on Google Colab using free T4 GPU.
- **Dataset Preparation**: Filter RDD2022 dataset for pothole (D40) and crack classes.
- **Model Optimization**: Quantize PyTorch `best.pt` model to `best_int8.tflite` for fast FPS on Raspberry Pi 4 CPU.
- **Accuracy Evaluation**: Calculate mAP50-95 scores, fine-tune confidence threshold, and copy final `best_int8.tflite` weights to `edge/models/`.

---

## 👤 Member 3: Full-Stack Web & GIS Dashboard Lead (Backend & Frontend)

### Core Tasks:
- **Backend API (`backend/`)**: Launch FastAPI server (`backend/app/main.py`), maintain SQLite database schema, verify spatial deduplication logic (10m radius).
- **GIS Dashboard (`frontend/`)**: Launch React + Leaflet map dashboard (`frontend/src/App.jsx`), refine UI styling, test live marker updates, severity filters, and contractor repair assignment buttons.
- **Presentation & Pitch Script**: Prepare SIH presentation slides and manage live dashboard walkthrough for judges.
