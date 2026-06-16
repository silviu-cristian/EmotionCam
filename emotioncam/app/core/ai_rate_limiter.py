"""Small rate limiter for optional external AI requests."""

from __future__ import annotations

import time


class AIRateLimiter:
    def __init__(self, interval_seconds: float = 10.0, minimum_seconds: float = 5.0) -> None:
        self.interval_seconds = max(float(minimum_seconds), float(interval_seconds))
        self._last_request = float("-inf")

    def due(self, now: float | None = None) -> bool:
        current = time.monotonic() if now is None else now
        return current - self._last_request >= self.interval_seconds

    def mark_sent(self, now: float | None = None) -> None:
        self._last_request = time.monotonic() if now is None else now
