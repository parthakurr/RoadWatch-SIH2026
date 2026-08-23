import logging
import time

import cv2
import numpy as np
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)


class CameraManager:
    """
    Handles camera capture on Raspberry Pi (OpenCV / picamera2) or synthetic mock frames.
    """

    def __init__(self, mock=False, camera_id=0):
        self.mock = mock
        self.camera_id = camera_id
        self.cap = None

        if mock:
            logger.info("[CAMERA] Mock camera enabled")
        else:
            try:
                self.cap = cv2.VideoCapture(camera_id)
                if not self.cap.isOpened():
                    logger.warning("[CAMERA] Physical camera not found — switching to mock mode")
                    self.mock = True
                    logger.info("[CAMERA] Mock camera enabled")
                else:
                    logger.info("[CAMERA] OpenCV camera opened (device %s)", camera_id)
            except Exception as exc:
                logger.warning("[CAMERA] Camera init failed (%s) — switching to mock mode", exc)
                self.mock = True
                logger.info("[CAMERA] Mock camera enabled")

    def capture_frame(self):
        """Return an OpenCV BGR frame (numpy ndarray)."""
        if not self.mock and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret and frame is not None:
                return frame
            logger.debug("[CAMERA] Empty frame from hardware camera — using mock fallback")

        return self._generate_mock_frame()

    def _generate_mock_frame(self):
        img = Image.new("RGB", (640, 480), color=(60, 64, 67))
        draw = ImageDraw.Draw(img)

        t = int(time.time() * 2) % 40
        for y in range(-40 + t, 480, 60):
            draw.rectangle([315, y, 325, y + 30], fill=(240, 240, 240))

        if int(time.time()) % 6 in (0, 1):
            draw.ellipse([240, 200, 400, 310], fill=(20, 20, 22), outline=(40, 42, 45), width=4)
            draw.ellipse([250, 210, 390, 300], fill=(10, 10, 12))
            draw.line([240, 250, 210, 270], fill=(15, 15, 15), width=3)
            draw.line([400, 240, 430, 230], fill=(15, 15, 15), width=3)

        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
