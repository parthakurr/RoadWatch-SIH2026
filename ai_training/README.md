# RoadWatch AI Model Training Guide (RDD2022 + YOLOv8)

This guide provides everything needed to train the RoadWatch pothole & road damage detection model using **YOLOv8** on **Google Colab** (free T4 GPU).

---

## 📌 Dataset Overview: RDD2022 (Road Damage Dataset)
RDD2022 contains ~47,000 road damage images across multiple countries (Japan, India, Czech Republic, Norway, USA) with 4 main damage categories:
- **D00**: Longitudinal Crack
- **D10**: Transverse Crack
- **D20**: Aligator Crack
- **D40**: **Pothole** (Primary target for RoadWatch)

---

## 🚀 Quick Start on Google Colab

### Step 1: Open Google Colab
1. Upload `train_yolov8_rdd2022.ipynb` or run the notebook on [Google Colab](https://colab.research.google.com/).
2. Change Runtime to **GPU**: `Runtime -> Change runtime type -> Hardware accelerator -> GPU (T4)`.

### Step 2: Key Code Steps in Colab

```python
# 1. Install Ultralytics YOLOv8 & Roboflow/Kaggle API
!pip install -q ultralytics roboflow opencv-python

# 2. Import YOLO
from ultralytics import YOLO

# 3. Load lightweight YOLOv8 Nano model (ideal for Raspberry Pi 4 edge inference)
model = YOLO('yolov8n.pt')

# 4. Download RDD2022 Pothole Dataset via Roboflow (Pre-converted to YOLO format)
from roboflow import Roboflow
rf = Roboflow(api_key="YOUR_ROBOFLOW_KEY") # Or use public Kaggle RDD2022 download
project = rf.workspace("road-damage-detection").project("rdd2022-pothole")
dataset = project.download("yolov8")

# 5. Train for 50 epochs
results = model.train(
    data=f"{dataset.location}/data.yaml",
    epochs=50,
    imgsz=640,
    batch=16,
    device=0,
    name='roadwatch_yolov8n'
)

# 6. Evaluate Performance
metrics = model.val()
print(f"mAP50-95: {metrics.box.map}")

# 7. Export to TFLite (TensorFlow Lite) for Raspberry Pi 4
model.export(format='tflite', int8=True) # INT8 Quantization for max edge FPS speed
print("Model exported successfully to best_float32.tflite / best_int8.tflite")
```

---

## 📦 Model Export Outputs
After training finishes, download these files from Colab to `edge/models/`:
- `best.pt` (PyTorch model for desktop testing)
- `best_saved_model/best_int8.tflite` (Quantized TFLite model for Raspberry Pi 4 Edge Unit)
- `labels.txt` (Class names: Pothole, Longitudinal Crack, Transverse Crack, Alligator Crack)
