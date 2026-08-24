import logging
from pathlib import Path
from typing import Optional, Union

import cv2
import numpy as np

from config import DEFAULT_CONFIDENCE_THRESHOLD, DEFAULT_LABELS_PATH, DEFAULT_MODEL_PATH

logger = logging.getLogger(__name__)


class RoadDamageDetector:
    """
    Inference pipeline supporting TFLite models on Raspberry Pi or a heuristic fallback.
    """

    def __init__(
        self,
        model_path: Optional[Union[Path, str]] = None,
        labels_path: Optional[Union[Path, str]] = None,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
    ):
        self.model_path = Path(model_path or DEFAULT_MODEL_PATH)
        self.labels_path = Path(labels_path or DEFAULT_LABELS_PATH)
        self.confidence_threshold = confidence_threshold
        self.labels = self._load_labels(self.labels_path)
        self.interpreter = None
        self.use_tflite = False

        if self.model_path.exists():
            try:
                try:
                    import tflite_runtime.interpreter as tflite
                except ImportError:
                    import tensorflow.lite as tflite

                self.interpreter = tflite.Interpreter(model_path=str(self.model_path))
                self.interpreter.allocate_tensors()
                self.input_details = self.interpreter.get_input_details()
                self.output_details = self.interpreter.get_output_details()
                self.use_tflite = True
                logger.info("[DETECTION] Loaded TFLite model from %s", self.model_path)
            except Exception as exc:
                logger.warning("[DETECTION] TFLite load failed (%s) — using heuristic fallback", exc)
        else:
            logger.info(
                "[DETECTION] No TFLite model at '%s' — using heuristic fallback",
                self.model_path,
            )

    def _load_labels(self, path: Path):
        if path.exists():
            with open(path, "r", encoding="utf-8") as handle:
                return [line.strip() for line in handle.readlines() if line.strip()]
        return ["Pothole", "Longitudinal Crack", "Transverse Crack", "Alligator Crack"]

    def detect(self, frame):
        """
        Run inference on an OpenCV BGR frame.

        Returns a list of dicts with keys:
        class_name, confidence, severity, bbox, bbox_normalized
        """
        if self.use_tflite and self.interpreter:
            detections = self._detect_tflite(frame)
        else:
            detections = self._detect_heuristic(frame)

        return [d for d in detections if d["confidence"] >= self.confidence_threshold]

    def _detect_tflite(self, frame):
        try:
            input_shape = self.input_details[0]["shape"]
            if len(input_shape) == 4:
                input_h, input_w = input_shape[1], input_shape[2]
            else:
                input_h, input_w = 640, 640

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            resized = cv2.resize(rgb, (input_w, input_h))

            input_dtype = self.input_details[0]["dtype"]
            if input_dtype == np.uint8:
                input_data = np.expand_dims(resized, axis=0).astype(np.uint8)
            elif input_dtype == np.int8:
                input_data = np.expand_dims(resized.astype(np.float32) - 128, axis=0).astype(np.int8)
            else:
                input_data = np.expand_dims(resized, axis=0).astype(np.float32) / 255.0

            self.interpreter.set_tensor(self.input_details[0]["index"], input_data)
            self.interpreter.invoke()

            output_tensors = [
                self.interpreter.get_tensor(detail["index"])
                for detail in self.output_details
            ]

            frame_h, frame_w = frame.shape[:2]
            detections = []

            # Case A: Multi-tensor output (Boxes, Classes, Scores, Num)
            if len(output_tensors) >= 4:
                boxes = output_tensors[0][0]
                classes = output_tensors[1][0]
                scores = output_tensors[2][0]
                num_dets = int(output_tensors[3][0]) if output_tensors[3].ndim > 0 else len(scores)

                for i in range(num_dets):
                    score = float(scores[i])
                    if score >= self.confidence_threshold:
                        cls_idx = int(classes[i])
                        class_name = self.labels[cls_idx] if cls_idx < len(self.labels) else "Pothole"
                        ymin, xmin, ymax, xmax = boxes[i]
                        x = int(xmin * frame_w)
                        y = int(ymin * frame_h)
                        w = int((xmax - xmin) * frame_w)
                        h = int((ymax - ymin) * frame_h)

                        area_ratio = (w * h) / (frame_w * frame_h)
                        severity = "HIGH" if area_ratio > 0.04 else ("MEDIUM" if area_ratio > 0.02 else "LOW")

                        detections.append({
                            "class_name": class_name,
                            "confidence": round(score, 2),
                            "severity": severity,
                            "bbox": [x, y, w, h],
                            "bbox_normalized": [
                                round(x / frame_w, 4),
                                round(y / frame_h, 4),
                                round((x + w) / frame_w, 4),
                                round((y + h) / frame_h, 4),
                            ],
                        })
                return detections

            # Case B: Standard YOLOv8 single output tensor [1, 4 + C, N] or [1, N, 4 + C]
            output = output_tensors[0]
            if output.dtype in (np.int8, np.uint8):
                quant_params = self.output_details[0].get("quantization", (0.0, 0))
                scale, zero_point = quant_params
                if scale > 0:
                    output = (output.astype(np.float32) - zero_point) * scale

            if output.ndim == 3:
                output = output[0]
                if output.shape[0] < output.shape[1]:
                    output = output.T

                boxes = []
                confidences = []
                class_ids = []

                for row in output:
                    cx, cy, w, h = row[:4]
                    class_scores = row[4:]
                    cls_id = int(np.argmax(class_scores))
                    max_score = float(class_scores[cls_id])

                    if max_score >= self.confidence_threshold:
                        if cx <= 1.0 and cy <= 1.0:
                            box_x = int((cx - w / 2) * frame_w)
                            box_y = int((cy - h / 2) * frame_h)
                            box_w = int(w * frame_w)
                            box_h = int(h * frame_h)
                        else:
                            box_x = int((cx - w / 2) * (frame_w / input_w))
                            box_y = int((cy - h / 2) * (frame_h / input_h))
                            box_w = int(w * (frame_w / input_w))
                            box_h = int(h * (frame_h / input_h))

                        boxes.append([box_x, box_y, box_w, box_h])
                        confidences.append(max_score)
                        class_ids.append(cls_id)

                if boxes:
                    indices = cv2.dnn.NMSBoxes(boxes, confidences, self.confidence_threshold, 0.45)
                    if len(indices) > 0:
                        indices = indices.flatten() if isinstance(indices, np.ndarray) else indices
                        for idx in indices:
                            cls_id = class_ids[idx]
                            class_name = self.labels[cls_id] if cls_id < len(self.labels) else "Pothole"
                            bx, by, bw, bh = boxes[idx]
                            conf = confidences[idx]

                            area_ratio = (bw * bh) / (frame_w * frame_h)
                            severity = "HIGH" if area_ratio > 0.04 else ("MEDIUM" if area_ratio > 0.02 else "LOW")

                            detections.append({
                                "class_name": class_name,
                                "confidence": round(conf, 2),
                                "severity": severity,
                                "bbox": [bx, by, bw, bh],
                                "bbox_normalized": [
                                    round(max(0, bx) / frame_w, 4),
                                    round(max(0, by) / frame_h, 4),
                                    round(min(frame_w, bx + bw) / frame_w, 4),
                                    round(min(frame_h, by + bh) / frame_h, 4),
                                ],
                            })
                        return detections

            return self._detect_heuristic(frame)
        except Exception as exc:
            logger.warning("[DETECTION] TFLite parsing error (%s) — using heuristic fallback", exc)
            return self._detect_heuristic(frame)

    def _detect_heuristic(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        _, thresh = cv2.threshold(blur, 45, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections = []
        frame_h, frame_w = frame.shape[:2]

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if 1500 < area < 40000:
                x, y, w, h = cv2.boundingRect(cnt)
                aspect_ratio = float(w) / h
                if 0.4 < aspect_ratio < 2.5:
                    area_ratio = area / (frame_w * frame_h)
                    if area_ratio > 0.04:
                        severity = "HIGH"
                    elif area_ratio > 0.02:
                        severity = "MEDIUM"
                    else:
                        severity = "LOW"

                    confidence = min(0.96, 0.72 + (area / 50000.0))
                    detections.append(
                        {
                            "class_name": "Pothole",
                            "confidence": round(confidence, 2),
                            "severity": severity,
                            "bbox": [x, y, w, h],
                            "bbox_normalized": [
                                round(x / frame_w, 4),
                                round(y / frame_h, 4),
                                round((x + w) / frame_w, 4),
                                round((y + h) / frame_h, 4),
                            ],
                        }
                    )
                    break

        return detections
