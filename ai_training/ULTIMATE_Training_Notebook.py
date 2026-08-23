# ============================================================
# 🔥 ROADWATCH ULTIMATE AI MODEL TRAINING
# ============================================================
# SIH 2026 | YOLOv8s | Maximum Dataset | Zero Compromises
#
# INSTRUCTIONS:
# 1. Open Google Colab → New Notebook → Runtime → T4 GPU
# 2. Copy each cell below into Colab cells (separated by # === CELL markers)
# 3. Run cells 1→2→3→4→5 in order
# ============================================================


# === CELL 1: INSTALL EVERYTHING ===

# !pip install -q ultralytics kagglehub opencv-python matplotlib pyyaml


# === CELL 2: DOWNLOAD EVERY POTHOLE DATASET AVAILABLE ===

import kagglehub, os

datasets = {}
sources = [
    ("chitholian/annotated-potholes-dataset", "chitholian"),
    ("atulyakumar98/pothole-detection-dataset", "atulyakumar"),
    ("sovitrath/road-pothole-images-for-pothole-detection", "sovitrath"),
    ("sachinpatel21/pothole-image-dataset", "sachinpatel"),
    ("s6hemant/potholes-detection", "hemant"),
    ("nikhilroxtomar/pothole-detection-dataset", "nikhil"),
    ("debasisdotcom/pothole-detection", "debasis"),
    ("zfrfrk/road-damage-dataset-yolo-format", "rdd_yolo"),
    ("warrantyvoid/potholes-and-road-damage", "warranty"),
]

for kaggle_id, label in sources:
    try:
        path = kagglehub.dataset_download(kaggle_id)
        datasets[label] = path
        print(f"✅ {label}: {path}")
    except Exception as e:
        print(f"❌ {label}: Skipped ({str(e)[:60]})")

print(f"\n🔥 Successfully downloaded {len(datasets)} out of {len(sources)} datasets!")


# === CELL 3: MEGA MERGE — USE ALL DATA, NO CAPS ===

import os, shutil, glob, random, yaml
import xml.etree.ElementTree as ET

random.seed(42)
MERGED = "/content/mega_dataset"
for split in ['train', 'val']:
    os.makedirs(f"{MERGED}/{split}/images", exist_ok=True)
    os.makedirs(f"{MERGED}/{split}/labels", exist_ok=True)

total = 0
stats = {}

def add_voc_annotated(src_path, prefix, label):
    """Add images with Pascal VOC XML bounding box annotations"""
    global total
    count = 0
    xmls = glob.glob(f"{src_path}/**/*.xml", recursive=True)
    for xml_path in xmls:
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            size = root.find('size')
            if size is None: continue
            w = int(size.find('width').text)
            h = int(size.find('height').text)
            if w == 0 or h == 0: continue

            base = os.path.splitext(xml_path)[0]
            img_path = None
            for ext in ['.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG']:
                if os.path.exists(base + ext):
                    img_path = base + ext
                    break
            if not img_path: continue

            # Check if any objects exist
            objects = root.findall('object')
            if not objects: continue

            split = 'train' if random.random() < 0.85 else 'val'
            name = f"{prefix}_{count:05d}.jpg"
            shutil.copy2(img_path, f"{MERGED}/{split}/images/{name}")

            with open(f"{MERGED}/{split}/labels/{name.replace('.jpg', '.txt')}", 'w') as f:
                for obj in objects:
                    bb = obj.find('bndbox')
                    xmin = max(0, int(float(bb.find('xmin').text)))
                    ymin = max(0, int(float(bb.find('ymin').text)))
                    xmax = min(w, int(float(bb.find('xmax').text)))
                    ymax = min(h, int(float(bb.find('ymax').text)))
                    if xmax <= xmin or ymax <= ymin: continue
                    x_c = ((xmin + xmax) / 2.0) / w
                    y_c = ((ymin + ymax) / 2.0) / h
                    bw = (xmax - xmin) / w
                    bh = (ymax - ymin) / h
                    # Clamp values to [0, 1]
                    x_c = max(0, min(1, x_c))
                    y_c = max(0, min(1, y_c))
                    bw = max(0.001, min(1, bw))
                    bh = max(0.001, min(1, bh))
                    f.write(f"0 {x_c:.6f} {y_c:.6f} {bw:.6f} {bh:.6f}\n")
            count += 1
        except:
            continue
    total += count
    stats[label] = count
    print(f"  ✅ {label}: {count} annotated images")
    return count

def add_yolo_formatted(src_path, prefix, label):
    """Add images that already have YOLO .txt label files"""
    global total
    count = 0
    # Find all images
    all_imgs = glob.glob(f"{src_path}/**/*.jpg", recursive=True) + \
               glob.glob(f"{src_path}/**/*.jpeg", recursive=True) + \
               glob.glob(f"{src_path}/**/*.png", recursive=True)
    
    for img_path in all_imgs:
        base = os.path.splitext(img_path)[0]
        txt_path = base + '.txt'
        if not os.path.exists(txt_path): continue
        # Verify label file is not empty and has valid YOLO format
        try:
            with open(txt_path, 'r') as f:
                content = f.read().strip()
            if not content: continue
            # Quick validation
            parts = content.split('\n')[0].split()
            if len(parts) < 5: continue
        except:
            continue
        
        split = 'train' if random.random() < 0.85 else 'val'
        name = f"{prefix}_{count:05d}.jpg"
        shutil.copy2(img_path, f"{MERGED}/{split}/images/{name}")
        shutil.copy2(txt_path, f"{MERGED}/{split}/labels/{name.replace('.jpg', '.txt')}")
        count += 1
    
    total += count
    stats[label] = count
    print(f"  ✅ {label}: {count} YOLO-formatted images")
    return count

def add_classification_images(src_path, prefix, label, is_pothole=True):
    """Add classification-only images (no bounding boxes) with approximate labels"""
    global total
    count = 0
    all_imgs = glob.glob(f"{src_path}/**/*.jpg", recursive=True) + \
               glob.glob(f"{src_path}/**/*.jpeg", recursive=True) + \
               glob.glob(f"{src_path}/**/*.png", recursive=True)
    random.shuffle(all_imgs)
    
    for img_path in all_imgs:
        split = 'train' if random.random() < 0.85 else 'val'
        name = f"{prefix}_{count:05d}.jpg"
        shutil.copy2(img_path, f"{MERGED}/{split}/images/{name}")
        
        lbl_path = f"{MERGED}/{split}/labels/{name.replace('.jpg', '.txt')}"
        if is_pothole:
            # Approximate center bounding box for pothole images
            with open(lbl_path, 'w') as f:
                f.write("0 0.5 0.5 0.55 0.45\n")
        else:
            # Empty label = negative sample (clean road)
            open(lbl_path, 'w').close()
        count += 1
    
    total += count
    stats[label] = count
    print(f"  ✅ {label}: {count} images ({'pothole' if is_pothole else 'negative/clean road'})")
    return count


print("=" * 60)
print("🔥 MEGA MERGE — PROCESSING ALL DATASETS")
print("=" * 60)

# --- Process each downloaded dataset ---

# 1. Chitholian (XML annotated - BEST quality)
if 'chitholian' in datasets:
    add_voc_annotated(datasets['chitholian'], "chi", "Chitholian Annotated")

# 2. Atulyakumar (classification: potholes/ and normal/ folders)
if 'atulyakumar' in datasets:
    pot_dir = None
    norm_dir = None
    for d in glob.glob(f"{datasets['atulyakumar']}/**/potholes", recursive=True):
        pot_dir = d; break
    for d in glob.glob(f"{datasets['atulyakumar']}/**/normal", recursive=True):
        norm_dir = d; break
    if pot_dir:
        add_classification_images(pot_dir, "atul_pot", "Atulyakumar Potholes", is_pothole=True)
    if norm_dir:
        add_classification_images(norm_dir, "atul_norm", "Atulyakumar Normal Roads", is_pothole=False)

# 3. Sovit Rath (8.82GB - MASSIVE - check for XML or YOLO annotations)
if 'sovitrath' in datasets:
    sovit_xmls = glob.glob(f"{datasets['sovitrath']}/**/*.xml", recursive=True)
    sovit_txts = glob.glob(f"{datasets['sovitrath']}/**/*.txt", recursive=True)
    if sovit_xmls:
        add_voc_annotated(datasets['sovitrath'], "sov", "Sovit Rath Annotated")
    elif sovit_txts:
        add_yolo_formatted(datasets['sovitrath'], "sov", "Sovit Rath YOLO")
    else:
        add_classification_images(datasets['sovitrath'], "sov", "Sovit Rath Images", is_pothole=True)

# 4. Sachin Patel
if 'sachinpatel' in datasets:
    sp_xmls = glob.glob(f"{datasets['sachinpatel']}/**/*.xml", recursive=True)
    if sp_xmls:
        add_voc_annotated(datasets['sachinpatel'], "sp", "Sachin Patel Annotated")
    else:
        add_classification_images(datasets['sachinpatel'], "sp", "Sachin Patel Images", is_pothole=True)

# 5. Hemant
if 'hemant' in datasets:
    h_xmls = glob.glob(f"{datasets['hemant']}/**/*.xml", recursive=True)
    if h_xmls:
        add_voc_annotated(datasets['hemant'], "hem", "Hemant Annotated")
    else:
        add_classification_images(datasets['hemant'], "hem", "Hemant Images", is_pothole=True)

# 6. Nikhil
if 'nikhil' in datasets:
    n_xmls = glob.glob(f"{datasets['nikhil']}/**/*.xml", recursive=True)
    n_txts = glob.glob(f"{datasets['nikhil']}/**/*.txt", recursive=True)
    if n_xmls:
        add_voc_annotated(datasets['nikhil'], "nik", "Nikhil Annotated")
    elif n_txts:
        add_yolo_formatted(datasets['nikhil'], "nik", "Nikhil YOLO")
    else:
        add_classification_images(datasets['nikhil'], "nik", "Nikhil Images", is_pothole=True)

# 7. Debasis
if 'debasis' in datasets:
    d_xmls = glob.glob(f"{datasets['debasis']}/**/*.xml", recursive=True)
    if d_xmls:
        add_voc_annotated(datasets['debasis'], "deb", "Debasis Annotated")
    else:
        add_classification_images(datasets['debasis'], "deb", "Debasis Images", is_pothole=True)

# 8. RDD YOLO format
if 'rdd_yolo' in datasets:
    # Check for data.yaml first
    rdd_yamls = glob.glob(f"{datasets['rdd_yolo']}/**/*.yaml", recursive=True)
    if rdd_yamls:
        print(f"  📄 Found YAML configs: {rdd_yamls[:3]}")
    add_yolo_formatted(datasets['rdd_yolo'], "rdd", "RDD YOLO Format")

# 9. Warranty Void
if 'warranty' in datasets:
    w_xmls = glob.glob(f"{datasets['warranty']}/**/*.xml", recursive=True)
    if w_xmls:
        add_voc_annotated(datasets['warranty'], "wrn", "WarrantyVoid Annotated")
    else:
        add_classification_images(datasets['warranty'], "wrn", "WarrantyVoid Images", is_pothole=True)

# --- Create data.yaml ---
train_count = len(glob.glob(f"{MERGED}/train/images/*"))
val_count = len(glob.glob(f"{MERGED}/val/images/*"))

with open(f"{MERGED}/data.yaml", 'w') as f:
    yaml.dump({
        'path': MERGED,
        'train': 'train/images',
        'val': 'val/images',
        'names': {0: 'Pothole'}
    }, f)

print(f"\n{'=' * 60}")
print(f"🔥🔥🔥 MEGA DATASET READY — NO ROOM FOR IMPROVEMENT 🔥🔥🔥")
print(f"{'=' * 60}")
print(f"   Train: {train_count} images")
print(f"   Val:   {val_count} images")
print(f"   TOTAL: {train_count + val_count} images")
print(f"{'=' * 60}")
print(f"\n📊 Breakdown by source:")
for src, cnt in sorted(stats.items(), key=lambda x: -x[1]):
    bar = "█" * min(50, cnt // 20)
    print(f"   {src:30s} | {cnt:5d} | {bar}")


# === CELL 4: TRAIN THE ABSOLUTE BEST MODEL ===

from ultralytics import YOLO

# YOLOv8s — 11.2M params, best balance of accuracy + Pi 4 deployability
model = YOLO('yolov8s.pt')

results = model.train(
    data='/content/mega_dataset/data.yaml',
    epochs=150,           # Maximum epochs
    imgsz=640,            # Standard YOLO input resolution
    batch=8,              # Fits T4 GPU memory with YOLOv8s
    device=0,
    name='roadwatch_BEST',
    
    # --- Learning Rate ---
    lr0=0.01,             # Initial learning rate
    lrf=0.01,             # Final LR = lr0 * lrf (cosine decay)
    warmup_epochs=5,      # Gradual warmup prevents early divergence
    
    # --- Early Stopping ---
    patience=30,          # Wait 30 epochs before stopping (max patience)
    
    # --- Augmentation (MAXIMUM) ---
    augment=True,
    mosaic=1.0,           # Mosaic: stitches 4 images together
    mixup=0.2,            # Mixup: blends 2 images
    copy_paste=0.15,      # Copy-paste augmentation
    degrees=20.0,         # Random rotation ±20°
    translate=0.2,        # Random translation ±20%
    scale=0.5,            # Random zoom 50%-150%
    shear=5.0,            # Random shear ±5°
    perspective=0.001,    # Random perspective warp
    fliplr=0.5,           # Horizontal flip 50%
    flipud=0.05,          # Vertical flip 5% (rare for roads but adds variety)
    hsv_h=0.015,          # Hue jitter (color shift)
    hsv_s=0.7,            # Saturation jitter (vivid ↔ faded)
    hsv_v=0.4,            # Brightness jitter (daylight ↔ shadow)
    erasing=0.3,          # Random erasing (occlusion simulation)
)

print("\n" + "=" * 60)
print("🏆🏆🏆 ULTIMATE MODEL TRAINING COMPLETE 🏆🏆🏆")
print("=" * 60)

metrics = model.val()
print(f"📊 Precision:  {metrics.box.p[0]:.3f}")
print(f"📊 Recall:     {metrics.box.r[0]:.3f}")  
print(f"📊 mAP50:      {metrics.box.map50:.3f}")
print(f"📊 mAP50-95:   {metrics.box.map:.3f}")


# === CELL 5: EXPORT & DOWNLOAD ===

from ultralytics import YOLO
from google.colab import files

# Load best weights
model = YOLO('/content/runs/detect/roadwatch_BEST/weights/best.pt')

# Export TFLite for Raspberry Pi 4
model.export(format='tflite')

print("✅ Models ready!")
print("📁 Downloading best.pt to your laptop...")
files.download('/content/runs/detect/roadwatch_BEST/weights/best.pt')
