"""
FaceDatabase – persists face encodings and identity metadata to disk.

Storage layout (pickled dict):
  {
    "Alice": {
      "encodings": [np.ndarray, ...],
      "metadata":  {"created_at": str, "updated_at": str, "sample_count": int}
    },
    ...
  }
"""

import pickle
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


class FaceDatabase:
    """Thread-safe (read) face encoding store backed by a pickle file."""

    def __init__(self, data_dir: Path, encodings_file: str) -> None:
        self._data_dir = data_dir
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._path = data_dir / encodings_file
        self._db: Dict = {}
        self._load()

    # ── Persistence ──────────────────────────────────────────────────────────

    def _load(self) -> None:
        if self._path.exists():
            try:
                with open(self._path, "rb") as fh:
                    self._db = pickle.load(fh)
                logger.info("Loaded %d identity/ies from %s", len(self._db), self._path)
            except Exception as exc:
                logger.error("Could not load database (%s). Starting empty.", exc)
                self._db = {}
        else:
            logger.info("No existing database – starting fresh.")

    def save(self) -> bool:
        """Flush in-memory database to disk. Returns True on success."""
        try:
            with open(self._path, "wb") as fh:
                pickle.dump(self._db, fh)
            logger.info("Database saved → %s", self._path)
            return True
        except Exception as exc:
            logger.error("Database save failed: %s", exc)
            return False

    # ── Write Operations ─────────────────────────────────────────────────────

    def add_encoding(self, name: str, encoding: np.ndarray) -> None:
        """Append one encoding to an identity (creates the identity if needed)."""
        now = datetime.now().isoformat(timespec="seconds")
        if name not in self._db:
            self._db[name] = {
                "encodings": [],
                "metadata": {"created_at": now, "updated_at": now, "sample_count": 0},
            }
        entry = self._db[name]
        entry["encodings"].append(encoding)
        entry["metadata"]["sample_count"] += 1
        entry["metadata"]["updated_at"] = now

    def remove(self, name: str) -> bool:
        """Delete an identity entirely. Returns True if it existed."""
        if name in self._db:
            del self._db[name]
            logger.info("Removed '%s' from database.", name)
            return True
        logger.warning("'%s' not found in database.", name)
        return False

    # ── Read Operations ───────────────────────────────────────────────────────

    def get_all(self) -> Tuple[List[np.ndarray], List[str]]:
        """Return (encodings_list, parallel_names_list) for recognition."""
        encodings: List[np.ndarray] = []
        names: List[str] = []
        for name, data in self._db.items():
            for enc in data["encodings"]:
                encodings.append(enc)
                names.append(name)
        return encodings, names

    def list_identities(self) -> List[Dict]:
        """Return a list of identity summary dicts (for display)."""
        return [
            {
                "name": name,
                "sample_count": data["metadata"]["sample_count"],
                "created_at": data["metadata"]["created_at"],
                "updated_at": data["metadata"]["updated_at"],
            }
            for name, data in self._db.items()
        ]

    # ── Properties ───────────────────────────────────────────────────────────

    @property
    def identity_count(self) -> int:
        return len(self._db)

    @property
    def total_encodings(self) -> int:
        return sum(len(d["encodings"]) for d in self._db.values())