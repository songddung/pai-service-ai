import numpy as np
import cv2
from ultralytics import YOLO

yolo_model: YOLO = None

def load_yolo_model(model_path: str):
    global yolo_model
    yolo_model = YOLO(model_path)

def analyze_image(image_bytes: bytes) -> str:
    if not yolo_model:
        return "YOLO model not loaded."
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    results = yolo_model(img)
    if len(results) == 0 or len(results[0].boxes) == 0:
        return "No object detected"

    boxes = results[0].boxes
    candidates = []
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        cls = int(box.cls[0])
        label = yolo_model.names[cls]
        area = (x2 - x1) * (y2 - y1)
        candidates.append((label, conf, area))

    candidates.sort(key=lambda x: (x[2], x[1]), reverse=True)
    best_label, _, _ = candidates[0]
    return best_label
