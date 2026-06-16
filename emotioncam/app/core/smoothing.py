"""Temporal prediction smoothing."""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass


EXPRESSION_GROUPS = {
    "happy": "positive",
    "smile": "positive",
    "smile_small": "positive",
    "smile_big": "positive",
    "laughing": "positive",
    "amused": "positive",
    "surprised": "positive",
    "sad": "negative",
    "angry": "negative",
    "fearful": "negative",
    "disgusted": "negative",
    "tired": "negative",
    "bored": "negative",
    "frustrated": "negative",
    "concerned": "negative",
    "neutral": "neutral",
    "focused": "neutral",
    "confused": "neutral",
    "skeptical": "neutral",
    "thinking": "neutral",
    "relaxed": "neutral",
    "unknown": "neutral",
    "low_confidence": "neutral",
    "no_face": "neutral",
}


@dataclass(frozen=True)
class SmoothedPrediction:
    label: str
    group: str
    confidence: float
    face_detected: bool


class ExpressionSmoother:
    def __init__(self, window_seconds: float = 1.5, stable_seconds: float = 0.8) -> None:
        self.window_seconds = max(0.2, window_seconds)
        self.stable_seconds = max(0.0, stable_seconds)
        self._samples: deque[tuple[float, str, float, bool]] = deque()
        self._candidate = "unknown"
        self._candidate_since = 0.0
        self._stable = "unknown"

    def reset(self) -> None:
        self._samples.clear()
        self._candidate = "unknown"
        self._candidate_since = 0.0
        self._stable = "unknown"

    def add(
        self,
        label: str,
        confidence: float,
        face_detected: bool,
        now: float | None = None,
    ) -> SmoothedPrediction:
        current = time.monotonic() if now is None else now
        normalized = label.replace(" ", "_") or "unknown"
        self._samples.append((current, normalized, max(0.0, min(1.0, confidence)), face_detected))
        cutoff = current - self.window_seconds
        while self._samples and self._samples[0][0] < cutoff:
            self._samples.popleft()

        weights: dict[str, float] = {}
        confidences: dict[str, list[float]] = {}
        for _, sample_label, sample_confidence, detected in self._samples:
            effective = sample_label if detected else "no_face"
            weights[effective] = weights.get(effective, 0.0) + max(0.05, sample_confidence)
            confidences.setdefault(effective, []).append(sample_confidence)
        winner = max(weights, key=weights.get, default="unknown")

        if winner != self._candidate:
            self._candidate = winner
            self._candidate_since = current
        if winner == self._stable or current - self._candidate_since >= self.stable_seconds:
            self._stable = winner

        values = confidences.get(self._stable, [0.0])
        confidence_out = sum(values) / len(values)
        face_out = self._stable != "no_face"
        return SmoothedPrediction(
            self._stable,
            EXPRESSION_GROUPS.get(self._stable, "neutral"),
            confidence_out,
            face_out,
        )
