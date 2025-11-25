import numpy as np
import cv2
from ultralytics import YOLO
from application.port.outbound.image_analysis_port import ImageAnalysisPort

class YoloService(ImageAnalysisPort):

    def __init__(self, model_path: str):
        self.model = YOLO(model_path)

    def analyze_image(self, image_bytes: bytes) -> str:
        if not self.model:
            return "YOLO model not loaded."
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        results = self.model(img)
        if len(results) == 0 or len(results[0].boxes) == 0:
            return "No object detected"

        boxes = results[0].boxes
        candidates = []
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = self.model.names[cls]
            area = (x2 - x1) * (y2 - y1)
            candidates.append((label, conf, area))

        candidates.sort(key=lambda x: (x[2], x[1]), reverse=True)
        best_label, _, _ = candidates[0]
        return best_label
