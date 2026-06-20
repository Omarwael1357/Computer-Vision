from __future__ import annotations

from datetime import datetime
from pathlib import Path

import cv2


class Camera:
    def __init__(self, index: int = 0, width: int = 1280, height: int = 720, fps: int = 30) -> None:
        self.index = index
        self.width = width
        self.height = height
        self.fps = fps
        self.capture = None

    def __enter__(self) -> "Camera":
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.release()

    def open(self) -> bool:
        self.capture = cv2.VideoCapture(self.index)
        if not self.capture.isOpened():
            return False
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.capture.set(cv2.CAP_PROP_FPS, self.fps)
        return self.capture.isOpened()

    def read(self):
        if self.capture is None:
            return False, None
        return self.capture.read()

    def release(self) -> None:
        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def screenshot(self, frame, screenshots: Path):
        screenshots = Path(screenshots)
        screenshots.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = screenshots / f"screenshot_{timestamp}.png"
        success = cv2.imwrite(str(filename), frame)
        return str(filename) if success else None
