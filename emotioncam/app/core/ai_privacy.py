"""Privacy and validation constants for optional AI analysis."""

from __future__ import annotations

from .smoothing import EXPRESSION_GROUPS


AI_PRIVACY_WARNING = (
    "AI analysis is disabled by default. OpenAI mode sends selected camera frames "
    "or cropped face images to an external AI service. Local Ollama mode sends "
    "selected images only to an Ollama service running on this computer. No AI "
    "images are sent unless you explicitly enable AI analysis and accept consent."
)

OPENAI_AI_PRIVACY_WARNING = (
    "External AI analysis sends selected camera frames or cropped face images to an "
    "external AI service for expression estimation. This is disabled by default. "
    "No images are sent unless you explicitly enable it."
)

LOCAL_AI_PRIVACY_WARNING = (
    "Local Ollama analysis sends selected cropped face images or frames only to the "
    "Ollama service running on this computer. It does not use OpenAI credits and "
    "does not upload images to the cloud."
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
