import os
import glob
import urllib.request
from PIL import Image, ImageDraw, ImageFont

def test_model_visual():
    print("==================================================")
    print("   🧪 ROADWATCH AI MODEL VISUAL PRECISION TEST   ")
    print("==================================================")

    # 1. Look for trained model weights
    possible_paths = [
        "edge/models/best.pt",
        "best.pt",
        os.path.expanduser("~/Downloads/best.pt"),
        os.path.expanduser("~/Downloads/best_roadwatch_india.pt")
    ]

    model_path = None
    for path in possible_paths:
        if os.path.exists(path):
            model_path = path
            break

    if not model_path:
        print("⚠️ Could not find 'best.pt' in edge/models/ or ~/Downloads/.")
        print("   If you downloaded 'best.pt' from Colab yesterday, please place it into:")
        print("   /Users/parththakur/.gemini/antigravity/scratch/roadwatch/edge/models/best.pt")
        print("==================================================")
        return

    print(f"✅ Loaded model weights from: {model_path}")
    
    try:
        from ultralytics import YOLO
    except ImportError:
        print("❌ 'ultralytics' package not found. Run: pip3 install ultralytics pillow")
        return

    model = YOLO(model_path)

    # 2. Setup output folder
    out_dir = "edge/test_outputs"
    os.makedirs(out_dir, exist_ok=True)

    # 3. Sample test road images
    sample_urls = [
        ("https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?w=800", "pothole_sample_1.jpg"),
        ("https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800", "pothole_sample_2.jpg"),
    ]

    print("\n⬇️ Downloading test road images for visual evaluation...")
    test_images = []
    for url, filename in sample_urls:
        target_path = os.path.join(out_dir, filename)
        try:
            urllib.request.urlretrieve(url, target_path)
            test_images.append(target_path)
        except Exception as e:
            print(f"   Warning: Could not download {filename}: {e}")

    # Also check if user placed any custom test images in edge/test_inputs/
    custom_inputs = glob.glob("edge/test_inputs/*.jpg") + glob.glob("edge/test_inputs/*.png")
    test_images.extend(custom_inputs)

    print(f"\n🔍 Running AI Detection on {len(test_images)} test images...")

    for img_path in test_images:
        try:
            img = Image.open(img_path).convert('RGB')
        except Exception:
            continue

        results = model.predict(source=img, conf=0.25, verbose=False)[0]
        draw = ImageDraw.Draw(img)

        detections_found = 0
        img_w, img_h = img.size

        for box in results.boxes:
            detections_found += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id] if hasattr(model, 'names') else "Pothole"

            # Severity calculation by bounding box area ratio
            area = (x2 - x1) * (y2 - y1)
            ratio = area / (img_w * img_h)

            if ratio > 0.04:
                severity = "HIGH"
                color = "#EF4444" # Red
            elif ratio > 0.015:
                severity = "MEDIUM"
                color = "#F97316" # Orange
            else:
                severity = "LOW"
                color = "#EAB308" # Yellow

            # Draw thick bounding box
            for offset in range(3):
                draw.rectangle([x1 - offset, y1 - offset, x2 + offset, y2 + offset], outline=color)

            # Draw label banner
            label = f" {severity} {cls_name} ({conf*100:.0f}%) "
            draw.rectangle([x1, max(0, y1 - 20), x1 + len(label)*8, y1], fill=color)
            draw.text((x1 + 2, max(0, y1 - 18)), label, fill="#000000")

        out_file = os.path.join(out_dir, "predicted_" + os.path.basename(img_path))
        img.save(out_file)
        print(f"  📸 [{os.path.basename(img_path)}] -> Detections: {detections_found} | Saved: {out_file}")

    print("\n==================================================")
    print(f"✅ Visual testing complete! Check output images in:\n   {os.path.abspath(out_dir)}")
    print("==================================================")

if __name__ == "__main__":
    test_model_visual()
