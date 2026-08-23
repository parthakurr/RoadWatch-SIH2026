# RoadWatch Hardware Build & Hardware Integration Guide

This guide provides the complete hardware wiring, OS setup, and deployment workflow for the **RoadWatch Edge AI Unit** mounted on municipal/garbage vehicles.

---

## 🛠️ Bill of Materials (BOM)

| Component | Recommended Model | Approx. Price | Purpose |
| :--- | :--- | :--- | :--- |
| **SBC (Single Board Computer)** | Raspberry Pi 4 Model B (4GB RAM) | ₹5,200 | Runs TFLite INT8 inference & GPS parsing |
| **Camera Module** | RPi Camera Module 2 (8MP Sony IMX219) or Arducam | ₹1,400 | Captures front road video stream |
| **GPS Receiver** | Neo-6M GPS Module (with ceramic antenna) | ₹350 | Real-time UTC & geotagging coordinates |
| **Power Supply** | 20,000mAh Power Bank (5V/3A USB-C) | ₹1,200 | Continuous 8+ hour vehicle vehicle power |
| **Enclosure** | Weatherproof IP65 Plastic Box + Suction Mount | ₹600 | Mounts unit on vehicle windshield/dash |
| **Storage** | 32GB MicroSD Card (Class 10 / A1) | ₹400 | Raspberry Pi OS 64-bit + SQLite buffer |

---

## 🔌 Hardware Wiring Diagram

### 1. Camera Module Connection
- Insert the CSI ribbon cable into the Raspberry Pi 4 CSI Camera Port (between HDMI and Audio jack).
- Ensure the blue tab faces the Ethernet/USB ports.

### 2. Neo-6M GPS Module Wiring (UART Serial)

Connect the Neo-6M pins to Raspberry Pi 4 GPIO header pins as follows:

```
Neo-6M GPS Pin         Raspberry Pi 4 GPIO Pin
--------------         -----------------------
VCC             -----> Pin 2  (5V) or Pin 1 (3.3V)
GND             -----> Pin 6  (Ground)
TX  (Transmit)  -----> Pin 10 (GPIO 15 / RXD)
RX  (Receive)   -----> Pin 8  (GPIO 14 / TXD)
```

---

## ⚡ Step-by-Step Raspberry Pi OS Setup (Modern Bookworm / Bullseye OS)

> [!IMPORTANT]
> **Modern `rpicam` Command Note**: Recent 64-bit Raspberry Pi OS releases use `rpicam-hello` and `rpicam-still` (instead of legacy `libcamera-hello` or `raspistill`).

### Step 1: Headless OS Setup
1. Download **Raspberry Pi Imager** on your computer.
2. Select **Raspberry Pi OS (64-bit)**.
3. Click gear icon to set: Hostname (`roadwatch-edge`), SSH password, and Wi-Fi credentials.
4. Flash MicroSD card and insert into Pi 4.

### Step 2: SSH & System Upgrade
```bash
ssh pi@roadwatch-edge.local
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-opencv python3-serial libatlas-base-dev
```

### Step 3: Enable Hardware Interfaces (Camera & UART GPS)
1. Launch configuration tool:
   ```bash
   sudo raspi-config
   ```
2. Navigate to `Interface Options`:
   - Enable **Legacy/Camera Support** or ensure `rpicam` is active.
   - Enable **Serial Port**: Select `NO` for login shell over serial, but `YES` for hardware serial port enabled (`/dev/ttyS0`).
3. Reboot: `sudo reboot`.

### Step 4: Verify Camera & GPS Hardware
```bash
# Test Camera Capture
rpicam-still -o test_road.jpg

# Test GPS NMEA Stream
sudo cat /dev/ttyS0
```

---

## 🚀 Running the RoadWatch Edge Daemon

### Option A: Test Mode on Mac/PC (Mock Mode)
```bash
cd edge
python3 main.py --mock --backend-url http://localhost:8000
```

### Option B: Production Hardware Deployment on Raspberry Pi 4
```bash
cd edge
pip3 install -r requirements.txt
python3 main.py --backend-url http://192.168.1.100:8000 --vehicle-id MUNI-VEH-01
```

### Option C: Auto-Start Daemon on Vehicle Ignition (systemd Service)
Create service file `/etc/systemd/system/roadwatch.service`:
```ini
[Unit]
Description=RoadWatch Edge AI Vehicle Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/roadwatch/edge
ExecStart=/usr/bin/python3 main.py --backend-url http://<YOUR_SERVER_IP>:8000 --vehicle-id MUNI-GARBAGE-01
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable auto-start:
```bash
sudo systemctl enable roadwatch.service
sudo systemctl start roadwatch.service
```
