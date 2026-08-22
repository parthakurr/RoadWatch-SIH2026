import time
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

class CameraManager:
    """
    Handles camera capture on Raspberry Pi (picamera2 / OpenCV) or synthetic mock frames.
    """
    def __init__(self, mock=False, camera_id=0):
        self.mock = mock
        self.camera_id = camera_id
        self.cap = None
        
        if not self.mock:
            try:
                # Try opening OpenCV camera device
                self.cap = cv2.VideoCapture(camera_id)
                if not self.cap.isOpened():
                    print("[CameraManager] Warning: Physical camera device not found. Switching to Mock mode.")
                    self.mock = True
            except Exception as e:
                print(f"[CameraManager] Camera init failed ({e}). Switching to Mock mode.")
                self.mock = True

    def capture_frame(self):
        """
        Returns an OpenCV BGR frame (numpy ndarray).
        """
        if not self.mock and self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        
        # Synthetic frame generator for mock testing
        return self._generate_mock_frame()

    def _generate_mock_frame(self):
        # Create a synthetic 640x480 road surface frame
        img = Image.new('RGB', (640, 480), color=(60, 64, 67)) # Asphalt grey
        draw = ImageDraw.Draw(img)
        
        # Draw road lane markings (white dashed line)
        t = int(time.time() * 2) % 40
        for y in range(-40 + t, 480, 60):
            draw.rectangle([315, y, 325, y + 30], fill=(240, 240, 240))
        
        # Periodically draw a simulated pothole
        if int(time.time()) % 6 in [0, 1]:
            # Pothole dark ellipse with rough texture
            draw.ellipse([240, 200, 400, 310], fill=(20, 20, 22), outline=(40, 42, 45), width=4)
            draw.ellipse([250, 210, 390, 300], fill=(10, 10, 12))
            
            # Additional crack lines
            draw.line([240, 250, 210, 270], fill=(15, 15, 15), width=3)
            draw.line([400, 240, 430, 230], fill=(15, 15, 15), width=3)

        # Convert PIL to OpenCV BGR format
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return frame

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
