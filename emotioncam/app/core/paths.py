"""Windows-local application paths."""

from __future__ import annotations

import os
from pathlib import Path


APP_NAME = "EmotionCam"


def app_data_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if not base:
        base = str(Path.home() / "AppData" / "Local")
    return Path(base) / APP_NAME


def config_path() -> Path:
    return app_data_dir() / "config.json"


def logs_dir() -> Path:
    return app_data_dir() / "logs"


def history_path() -> Path:
    return logs_dir() / "expression_history.jsonl"


def profile_dir() -> Path:
    return app_data_dir() / "profile"


def profile_path() -> Path:
    return profile_dir() / "expression_profile.json"


def expression_labels_path() -> Path:
    return profile_dir() / "expression_labels.json"


def user_profile_path() -> Path:
    return profile_dir() / "user_profile.json"


def ensure_app_dirs() -> None:
    app_data_dir().mkdir(parents=True, exist_ok=True)
    logs_dir().mkdir(parents=True, exist_ok=True)
    profile_dir().mkdir(parents=True, exist_ok=True)
