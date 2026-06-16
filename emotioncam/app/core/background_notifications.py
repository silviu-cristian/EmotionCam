"""Cooldown and recovery state for safe background notifications."""

from __future__ import annotations

import time


NEGATIVE_MESSAGES = (
    "I noticed a more serious visible expression. Take a breath - you're doing okay.",
    "Tough expression estimate detected. Quick reset: relax your shoulders and breathe slowly.",
    "Visible expression changed. Small pause? You've got this.",
)
RECOVERY_MESSAGES = (
    "Glad I could cheer you up!",
    "Nice, a more positive visible expression appeared :)",
    "Positive visible expression detected - good to see that shift.",
)


class BackgroundNotificationEngine:
    def __init__(
        self, negative_cooldown: float = 600, recovery_cooldown: float = 300, name: str = ""
    ) -> None:
        self.negative_cooldown = max(0.0, negative_cooldown)
        self.recovery_cooldown = max(0.0, recovery_cooldown)
        self.name = name.strip()
        self._last_negative = float("-inf")
        self._last_recovery = float("-inf")
        self._negative_seen = False
        self._negative_index = 0
        self._recovery_index = 0

    def message_for(self, group: str, now: float | None = None) -> str:
        current = time.monotonic() if now is None else now
        if group == "negative":
            self._negative_seen = True
            if current - self._last_negative >= self.negative_cooldown:
                message = NEGATIVE_MESSAGES[self._negative_index % len(NEGATIVE_MESSAGES)]
                self._negative_index += 1
                self._last_negative = current
                return f"{self.name}, {message[0].lower()}{message[1:]}" if self.name else message
        elif group == "positive" and self._negative_seen:
            self._negative_seen = False
            if current - self._last_recovery >= self.recovery_cooldown:
                message = RECOVERY_MESSAGES[self._recovery_index % len(RECOVERY_MESSAGES)]
                self._recovery_index += 1
                self._last_recovery = current
                return f"Nice shift, {self.name} - {message[0].lower()}{message[1:]}" if self.name else message
        return ""
