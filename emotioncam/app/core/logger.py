"""Metadata-only expression history logger."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from .paths import ensure_app_dirs, history_path, logs_dir


ALLOWED_FIELDS = (
    "timestamp",
    "expression_label",
    "expression_group",
    "confidence",
    "detection_mode",
    "classifier_source",
    "personalized_profile_active",
    "face_detected",
    "message_displayed",
    "popup_displayed",
    "fps",
)


class ExpressionLogger:
    def __init__(self, path: Path | None = None, enabled: bool = True) -> None:
        self.path = path or history_path()
        self.enabled = enabled

    def log(
        self, result: dict[str, Any], message: str = "", fps: float = 0.0, popup: str = ""
    ) -> bool:
        if not self.enabled:
            return False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
            "expression_label": str(result.get("label", "unknown")),
            "expression_group": str(result.get("group", "neutral")),
            "confidence": round(float(result.get("confidence", 0.0)), 3),
            "detection_mode": str(result.get("detection_mode", "heuristic")),
            "classifier_source": str(result.get("classifier_source", "heuristic")),
            "personalized_profile_active": bool(result.get("personalized_profile_active", False)),
            "face_detected": bool(result.get("face_detected", False)),
            "message_displayed": str(message),
            "popup_displayed": str(popup),
            "fps": round(float(fps), 1),
        }
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return True

    def clear(self) -> None:
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass

    @staticmethod
    def folder() -> Path:
        ensure_app_dirs()
        return logs_dir()
