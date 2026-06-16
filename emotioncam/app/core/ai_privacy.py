"""Privacy and validation constants for optional external AI analysis."""

from __future__ import annotations

from .smoothing import EXPRESSION_GROUPS


AI_PRIVACY_WARNING = (
    "External AI analysis sends selected camera frames or cropped face images to an "
    "external AI service for expression estimation. This is disabled by default. "
    "No images are sent unless you explicitly enable it."
)

AI_FULL_FRAME_WARNING = (
    "Full-frame analysis may include background details. Cropped-face-only mode is "
    "recommended for better privacy."
)

AI_SUPPORTED_LABELS = {
    "neutral",
    "smile_small",
    "smile_big",
    "happy",
    "laughing",
    "amused",
    "surprised",
    "sad",
    "angry",
    "fearful",
    "disgusted",
    "tired",
    "bored",
    "frustrated",
    "concerned",
    "focused",
    "confused",
    "skeptical",
    "thinking",
    "relaxed",
    "unknown",
    "no_face",
}

AI_SUPPORTED_GROUPS = {"positive", "neutral", "negative"}


def group_for_label(label: str) -> str:
    """Return EmotionCam's safe display group for a known expression label."""
    return EXPRESSION_GROUPS.get(label, "neutral")
