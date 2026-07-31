import os
import csv
import pandas as pd
from pathlib import Path
from ultralytics import YOLO

model = YOLO("yolov8n.pt")  # load pretrained nano

image_dir = Path("data/raw/images")
output_csv = Path("data/processed/yolo_results.csv")

results = []
for img_path in image_dir.glob("**/*.jpg"):
    try:
        detections = model(img_path)[0]
        detected_classes = [model.names[int(cls)] for cls in detections.boxes.cls]
        # Simple classification
        if "person" in detected_classes and any(c in ["bottle", "cup"] for c in detected_classes):
            category = "promotional"
        elif any(c in ["bottle", "cup", "packaging"] for c in detected_classes):
            category = "product_display"
        elif "person" in detected_classes:
            category = "lifestyle"
        else:
            category = "other"
        
        results.append({
            "image_path": str(img_path),
            "detected_classes": detected_classes,
            "category": category,
            # You can store confidence scores as JSON
        })
    except Exception as e:
        print(f"Error processing {img_path}: {e}")

pd.DataFrame(results).to_csv(output_csv, index=False)
print(f"YOLO results saved to {output_csv}")
