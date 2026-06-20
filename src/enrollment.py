from __future__ import annotations

from typing import List


class EnrollmentSession:
    def __init__(self, name: str, samples: int = 5, countdown: int = 3) -> None:
        self.name = name
        self.samples = samples
        self.countdown = countdown
        self.captured_frames: List[object] = []
        self.is_done = False

    def process_frame(self, frame: object) -> object:
        if len(self.captured_frames) < self.samples:
            self.captured_frames.append(frame.copy())
            if len(self.captured_frames) >= self.samples:
                self.is_done = True
        return frame
