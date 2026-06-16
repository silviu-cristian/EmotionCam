"""Safe, cooldown-controlled interaction messages."""

from __future__ import annotations

import time


MESSAGES = {
    "happy": ("Smile detected :)", "Positive expression detected."),
    "smile": ("Smile detected :)", "Positive visible expression detected."),
    "laughing": ("Laughing expression detected :)",),
    "surprised": ("That looked like surprise!",),
    "neutral": ("Neutral expression detected.", "All calm. Processing stays local."),
    "negative": (
        "A more serious expression was detected.",
        "Expression changed. Remember, this is only an estimate.",
    ),
}


class InteractionEngine:
    def __init__(self, cooldown_seconds: float = 8.0, enabled: bool = True, name: str = "") -> None:
        self.cooldown_seconds = max(0.0, cooldown_seconds)
        self.enabled = enabled
        self.name = name.strip()
        self._last_time = float("-inf")
        self._last_label = ""
        self._message_index = 0

    def message_for(self, label: str, group: str, now: float | None = None) -> str:
        if not self.enabled or label in {"unknown", "low_confidence", "no_face"}:
            return ""
        current = time.monotonic() if now is None else now
        if current - self._last_time < self.cooldown_seconds:
            return ""
        key = "negative" if group == "negative" else label
        options = MESSAGES.get(key)
        if not options:
            return ""
        if label != self._last_label:
            self._message_index = 0
        message = options[self._message_index % len(options)]
        self._message_index += 1
        self._last_label = label
        self._last_time = current
        return f"{self.name}, {message[0].lower()}{message[1:]}" if self.name else message
