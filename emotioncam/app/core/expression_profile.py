"""Local personalized visible-expression profile storage."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from shutil import copy2, rmtree

from .expression_features import FEATURE_NAMES, centroid
from .paths import profile_path


class ExpressionProfile:
    VERSION = 1

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or profile_path()
        self.samples: dict[str, list[list[float]]] = {}
        self.load()

    @property
    def exists(self) -> bool:
        return bool(self.samples)

    def load(self) -> bool:
        self.samples = {}
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            if data.get("version") == self.VERSION and data.get("feature_names") == list(FEATURE_NAMES):
                self.samples = {
                    str(label): [list(map(float, sample)) for sample in samples]
                    for label, samples in data.get("samples", {}).items()
                    if isinstance(samples, list)
                }
        except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError, ValueError):
            pass
        return self.exists

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": self.VERSION,
            "updated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
            "feature_names": list(FEATURE_NAMES),
            "samples": self.samples,
            "centroids": {label: centroid(samples) for label, samples in self.samples.items() if samples},
        }
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temporary.replace(self.path)

    def add_samples(self, label: str, samples: list[list[float]]) -> None:
        if samples:
            self.samples.setdefault(label, []).extend(samples)
            self.save()

    def delete(self) -> None:
        self.samples = {}
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass
        debug_images = self.path.parent / "debug_images"
        if debug_images.exists():
            rmtree(debug_images)

    def export_to(self, destination: Path) -> None:
        if not self.exists:
            raise FileNotFoundError("No personalized expression profile exists.")
        copy2(self.path, destination)

    def import_from(self, source: Path) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        copy2(source, self.path)
        if not self.load():
            raise ValueError("The selected file is not a valid EmotionCam expression profile.")

    def counts(self) -> dict[str, int]:
        return {label: len(samples) for label, samples in self.samples.items()}
