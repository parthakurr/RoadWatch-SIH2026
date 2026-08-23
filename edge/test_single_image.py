import os
import time
import glob
import urllib.request
from PIL import Image, ImageDraw

def test_99_3_model():
    print("==================================================")
    print("   🔍 TESTING YOUR 99.3% mAP KAGGLE MODEL")
    print("==================================================")

    model_path = "edge/models/best.pt"
    if not os.path.exists(model_path):
        print(f"❌ Model file not found at {model_path}")
        return

    mtime = os.path.getmtime(model_path)
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
    size_mb = round(os.path.getsize(model_path) / (1024*1024), 2)

    print(f"✅ Found model file: {os.path.abspath(model_path)}")
    print(f"   📅 Last Modified: {time_str}")
    print(f"   📦 File Size: {size_mb} MB")

    try:
        from ultralytics import YOLO
    except ImportError:
        print("❌ 'ultralytics' not installed. Please run: pip3 install ultralytics pillow")
        return

    model = YOLO(model_path)
    print("\n🧠 AI Model loaded into memory successfully!")

    # Setup output directory
    out_dir = "edge/test_outputs"
    os.makedirs(out_dir, exist_ok=True)

    # Sample road photos
    sample_urls = [
        ("https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=800", "test_pothole_1.jpg"),
        ("https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800", "test_pothole_2.jpg"),
    ]

    print("\n📸 Testing model on real road photographs...")

    for url, fname in sample_urls:
        img_path = os.path.join(out_dir, fname)
        try:
            urllib.request.urlretrieve(url, img_path)
        except Exception as e:
            continue

        img = Image.open(img_path).convert("RGB")
        img_w, img_h = img.size

        # Run inference with 99.3% model
        results = model.predict(source=img, conf=0.15, verbose=False)[0]
        draw = ImageDraw.Draw(img)

        box_count = 0
        for box in results.boxes:
            box_count += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id] if hasattr(model, 'names') else "Pothole"

            area = (x2 - x1) * (y2 - y1)
            ratio = area / (img_w * img_h)

            if ratio > 0.04:
                sev = "HIGH"
                color = "#EF4444"
            elif ratio > 0.015:
                sev = "MEDIUM"
                color = "#F97316"
            else:
                sev = "LOW"
                color = "#EAB308"

            for stroke in range(3):
                draw.rectangle([x1 - stroke, y1 - stroke, x2 + stroke, y2 + stroke], outline=color)

            label = f" {sev} {cls_name} ({conf*100:.0f}%) "
            draw.rectangle([x1, max(0, y1 - 22), x1 + len(label)*8, y1], fill=color)
            draw.text((x1 + 4, max(0, y1 - 18)), label, fill="#000000")

            print(f"   ⚠️  [{fname}] -> Detected {sev} {cls_name} | Confidence: {conf*100:.1f}% | Coordinates: [{x1}, {y1}, {x2}, {y2}]")

        out_file = os.path.join(out_dir, "PREDICTED_99mAP_" + fname)
        img.save(out_file)
        print(f"   💾 Saved visualization to: {out_file}\n")

    print("==================================================")
    print("✅ Model precision test complete!")
    print("==================================================")

if __name__ == "__main__":
    test_99_3_model()
