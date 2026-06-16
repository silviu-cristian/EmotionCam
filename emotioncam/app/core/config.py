"""Local JSON configuration."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from .paths import config_path, profile_path


EXPRESSION_DETECTION_MODES = {"heuristic", "personalized", "hybrid", "external_ai", "hybrid_ai"}


DEFAULT_CONFIG: dict[str, Any] = {
    "first_launch_complete": False,
    "theme": "dark",
    "statistics_enabled": True,
    "daily_email_summary_enabled": False,
    "summary_send_time": "20:00",
    "email_summary_use_tls": True,
    "email_summary_method": "smtp",
    "local_logging_enabled": True,
    "camera_index": 0,
    "detection_confidence_threshold": 0.45,
    "expression_confidence_threshold": 0.45,
    "smoothing_window_seconds": 1.5,
    "stable_expression_seconds": 0.8,
    "message_cooldown_seconds": 8.0,
    "show_face_rectangle": True,
    "show_confidence_values": True,
    "interaction_messages_enabled": True,
    "background_mode_enabled": False,
    "background_popups_enabled": True,
    "negative_popup_cooldown_seconds": 600,
    "positive_recovery_popup_cooldown_seconds": 300,
    "face_missing_grace_seconds": 1.0,
    "negative_expression_min_confidence": 0.65,
    "positive_expression_min_confidence": 0.5,
    "debug_panel_enabled": False,
    "expression_detection_mode": "heuristic",
    "personalized_profile_enabled": True,
    "calibration_samples_per_expression": 45,
    "calibration_capture_seconds": 4.0,
    "calibration_prepare_seconds": 2.0,
    "store_raw_calibration_images": False,
    "minimum_samples_per_expression": 15,
    "external_ai_backend_enabled": False,
    "external_ai_enabled": False,
    "external_ai_consent_accepted": False,
    "external_ai_provider": "openai",
    "external_ai_request_interval_seconds": 10.0,
    "external_ai_timeout_seconds": 20.0,
    "external_ai_send_cropped_face_only": True,
    "external_ai_show_debug_info": False,
    "external_ai_model": "gpt-4.1-mini",
    "external_ai_min_confidence": 0.55,
}


class ConfigManager:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or config_path()
        self.data = deepcopy(DEFAULT_CONFIG)
        self.load()

    def load(self) -> dict[str, Any]:
        self.data = deepcopy(DEFAULT_CONFIG)
        loaded_keys: set[str] = set()
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                loaded_keys = set(loaded)
                for key in DEFAULT_CONFIG:
                    if key in loaded:
                        value = self._compatible_value(key, loaded[key])
                        if value is not None:
                            self.data[key] = value
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass
        if (
            self.path == config_path()
            and "expression_detection_mode" not in loaded_keys
            and profile_path().exists()
        ):
            self.data["expression_detection_mode"] = "hybrid"
        if "external_ai_enabled" not in loaded_keys and "external_ai_backend_enabled" in loaded_keys:
            self.data["external_ai_enabled"] = bool(self.data["external_ai_backend_enabled"])
        if (
            self.data.get("external_ai_enabled")
            and self.data.get("external_ai_consent_accepted")
            and self.data.get("expression_detection_mode") == "hybrid"
        ):
            self.data["expression_detection_mode"] = "hybrid_ai"
        return deepcopy(self.data)

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(
            json.dumps(self.data, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        temporary.replace(self.path)

    def update(self, values: dict[str, Any]) -> None:
        for key, value in values.items():
            if key in DEFAULT_CONFIG:
                compatible = self._compatible_value(key, value)
                if compatible is not None:
                    self.data[key] = compatible
        self.save()

    def reset(self) -> None:
        self.data = deepcopy(DEFAULT_CONFIG)
        self.save()

    @staticmethod
    def _compatible_value(key: str, value: Any) -> Any | None:
        default = DEFAULT_CONFIG[key]
        if key == "theme":
            return value if value in {"dark", "light"} else None
        if key == "expression_detection_mode":
            return value if value in EXPRESSION_DETECTION_MODES else None
        if key == "external_ai_provider":
            return value if value == "openai" else None
        if key == "external_ai_model":
            return value.strip() if isinstance(value, str) and value.strip() else None
        if isinstance(default, bool):
            return value if isinstance(value, bool) else None
        if isinstance(default, (int, float)) and isinstance(value, (int, float)) and not isinstance(value, bool):
            return type(default)(value)
        return value if type(value) is type(default) else None
