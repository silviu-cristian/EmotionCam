"""Reusable local expression labels for manual calibration."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

from .paths import expression_labels_path


DEFAULT_EXPRESSION_LABELS = [
    "neutral", "smile_small", "smile_big", "happy", "laughing", "amused",
    "surprised", "sad", "angry", "fearful", "disgusted", "tired", "bored",
    "frustrated", "concerned", "focused", "confused", "skeptical", "thinking",
    "relaxed",
]


def normalize_expression_label(value: str) -> str:
    normalized = re.sub(r"\s+", "_", value.strip().lower())
    normalized = re.sub(r"[^a-z0-9_]", "", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    if not normalized:
        raise ValueError("Expression label cannot be empty.")
    return normalized


class ExpressionLabelRegistry:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or expression_labels_path()
        self.custom_labels: list[str] = []
        self.load()
        if not self.path.exists():
            self.save()

    @property
    def labels(self) -> list[str]:
        return DEFAULT_EXPRESSION_LABELS + [
            label for label in self.custom_labels if label not in DEFAULT_EXPRESSION_LABELS
        ]

    def load(self) -> None:
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.custom_labels = [
                normalize_expression_label(label) for label in data.get("custom_labels", [])
                if isinstance(label, str)
            ]
        except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
            self.custom_labels = []

    def add_custom(self, value: str) -> str:
        label = normalize_expression_label(value)
        if label in self.labels:
            raise ValueError(f"Expression label '{label}' already exists.")
        self.custom_labels.append(label)
        if not self.save():
            self.custom_labels.remove(label)
            raise ValueError("Could not save the custom expression label locally.")
        return label

    def save(self) -> bool:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "default_labels": DEFAULT_EXPRESSION_LABELS,
                "custom_labels": self.custom_labels,
                "last_updated": datetime.now().astimezone().isoformat(timespec="seconds"),
            }
            self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
            return True
        except OSError:
            return False
