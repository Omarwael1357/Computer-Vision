from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any, Dict, List


class FaceDatabase:
    def __init__(self, data_dir: Path, encodings_file: Path) -> None:
        self.data_dir = Path(data_dir)
        self.encodings_file = Path(encodings_file)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._encodings: Dict[str, List[Any]] = {}
        self._load()

    def _load(self) -> None:
        if self.encodings_file.exists():
            try:
                with open(self.encodings_file, "rb") as handle:
                    self._encodings = pickle.load(handle)
            except Exception:
                self._encodings = {}

    @property
    def identity_count(self) -> int:
        return len(self._encodings)

    @property
    def total_encodings(self) -> int:
        return sum(len(encs) for encs in self._encodings.values())

    def list_identities(self) -> List[str]:
        return sorted(self._encodings.keys())

    def add_encoding(self, name: str, encoding: Any) -> None:
        self._encodings.setdefault(name, []).append(encoding)

    def remove(self, name: str) -> bool:
        if name in self._encodings:
            del self._encodings[name]
            return True
        return False

    def save(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.encodings_file, "wb") as handle:
            pickle.dump(self._encodings, handle)
