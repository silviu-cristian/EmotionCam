"""Minimal local user profile and optional email-summary preferences."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from .paths import user_profile_path


DEFAULT_USER_PROFILE: dict[str, Any] = {
    "name": "",
    "email": "",
    "daily_email_summary_enabled": False,
    "summary_send_time": "20:00",
    "last_summary_sent_date": None,
    "email_delivery_mode": "mail_client",
    "smtp_server": "",
    "smtp_port": 587,
    "smtp_username": "",
    "smtp_use_tls": True,
}


def normalize_name(value: str) -> str:
    name = " ".join(str(value).strip().split())
    if len(name) > 80:
        raise ValueError("User name must be 80 characters or fewer.")
    if name and not re.fullmatch(r"[^\W\d_]+(?:[ '\-][^\W\d_]+)*", name, re.UNICODE):
        raise ValueError("User name may contain letters, spaces, apostrophes, and hyphens.")
    return name


def normalize_email(value: str, required: bool = False) -> str:
    email = str(value).strip()
    if not email and not required:
        return ""
    if (
        len(email) > 254
        or email.count("@") != 1
        or "." not in email.rsplit("@", 1)[1]
        or any(character.isspace() for character in email)
    ):
        raise ValueError("Enter a valid email address.")
    return email


def normalize_time(value: str) -> str:
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", str(value)):
        raise ValueError("Send time must use 24-hour HH:MM format.")
    return str(value)


class UserProfile:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or user_profile_path()
        self.data = deepcopy(DEFAULT_USER_PROFILE)
        self.load()

    def load(self) -> dict[str, Any]:
        self.data = deepcopy(DEFAULT_USER_PROFILE)
        try:
            loaded = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                for key, default in DEFAULT_USER_PROFILE.items():
                    value = loaded.get(key, default)
                    if key == "last_summary_sent_date" and (value is None or isinstance(value, str)):
                        self.data[key] = value
                    elif isinstance(value, type(default)):
                        self.data[key] = value
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            pass
        return deepcopy(self.data)

    def update(self, values: dict[str, Any]) -> None:
        updated = deepcopy(self.data)
        updated["name"] = normalize_name(values.get("name", updated["name"]))
        enabled = bool(values.get("daily_email_summary_enabled", updated["daily_email_summary_enabled"]))
        updated["email"] = normalize_email(values.get("email", updated["email"]), required=enabled)
        updated["summary_send_time"] = normalize_time(
            values.get("summary_send_time", updated["summary_send_time"])
        )
        mode = values.get("email_delivery_mode", updated["email_delivery_mode"])
        if mode not in {"mail_client", "smtp"}:
            raise ValueError("Email delivery mode must be SMTP or default mail client.")
        updated["email_delivery_mode"] = mode
        updated["daily_email_summary_enabled"] = enabled
        updated["smtp_server"] = str(values.get("smtp_server", updated["smtp_server"])).strip()
        updated["smtp_port"] = max(1, min(65535, int(values.get("smtp_port", updated["smtp_port"]))))
        updated["smtp_username"] = str(values.get("smtp_username", updated["smtp_username"])).strip()
        updated["smtp_use_tls"] = bool(values.get("smtp_use_tls", updated["smtp_use_tls"]))
        if "last_summary_sent_date" in values:
            updated["last_summary_sent_date"] = values["last_summary_sent_date"]
        self.data = updated
        self.save()

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(self.data, indent=2, sort_keys=True), encoding="utf-8")
        temporary.replace(self.path)
