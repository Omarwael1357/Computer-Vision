from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    camera_index: int = 0
    detection_model: str = "hog"
    tolerance: float = 0.50
    frame_width: int = 1280
    frame_height: int = 720
    target_fps: int = 30
    data_dir: Path = Path("data")
    encodings_file: Path = Path("data") / "encodings.pkl"
    screenshots_dir: Path = Path("screenshots")
    enrollment_samples: int = 5
    enrollment_countdown: int = 3

    def __post_init__(self):
        self.data_dir = Path(self.data_dir)
        self.screenshots_dir = Path(self.screenshots_dir)
        if not isinstance(self.encodings_file, Path):
            self.encodings_file = Path(self.encodings_file)
        if self.encodings_file.parent == Path("."):
            self.encodings_file = self.data_dir / self.encodings_file.name
