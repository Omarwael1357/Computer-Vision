from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional, Tuple

import cv2
import numpy as np

from src.database import FaceDatabase
from src.config import Config


class FaceRecognizer:
    def __init__(self, cfg: Config, db: FaceDatabase) -> None:
        self.cfg = cfg
        self.db = db
        self.known_encodings = self._load_encodings()

    def _load_encodings(self) -> dict[str, List[Any]]:
        return {name: encs for name, encs in self.db._encodings.items()}  # type: ignore

    def encode_from_frame(self, frame: Any) -> List[Any]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
        encodings: List[Any] = []
        for (x, y, w, h) in faces:
            face = frame[y : y + h, x : x + w]
            encodings.append(face)
        return encodings

    def encode_from_file(self, path: str) -> List[Any]:
        img = cv2.imread(path)
        if img is None:
            return []
        return self.encode_from_frame(img)

    def process_frame(self, frame: Any) -> Tuple[Any, list[str]]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        return frame, ["Unknown" for _ in faces]
