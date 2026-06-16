"""Optional external AI classifier wrapper with consent and fallback safety."""

from __future__ import annotations

from typing import Any

from .ai_client import OpenAIExpressionClient, unknown_result
from .ai_privacy import AI_PRIVACY_WARNING
from .ai_settings import load_api_key, normalize_api_key
from .expression_backends import BaseExpressionClassifier, ExpressionResult


class ExternalAIExpressionClassifier(BaseExpressionClassifier):
    """Classify a selected frame through an explicitly enabled external AI provider."""

    PRIVACY_WARNING = AI_PRIVACY_WARNING

    def __init__(
        self,
        settings: dict[str, Any],
        api_key: str = "",
        client: OpenAIExpressionClient | None = None,
    ) -> None:
        self.settings = settings
        self.api_key = normalize_api_key(api_key) or load_api_key()
        self.client = client or OpenAIExpressionClient(settings.get("external_ai_model", "gpt-4.1-mini"))

    def ready_to_send(self, face_box: tuple[int, int, int, int] | None = None) -> tuple[bool, str]:
        if not self.settings.get("external_ai_enabled", False):
            return False, "external_ai_disabled"
        if not self.settings.get("external_ai_consent_accepted", False):
            return False, "consent_required"
        if not self.api_key:
            return False, "missing_api_key"
        if self.settings.get("external_ai_send_cropped_face_only", True) and face_box is None:
            return False, "face_not_found"
        return True, "ready"

    def classify(self, frame: Any, face_box=None, landmarks=None) -> ExpressionResult:
        ready, reason = self.ready_to_send(face_box)
        if not ready:
            label = "no_face" if reason == "face_not_found" else "unknown"
            return ExpressionResult(
                label,
                "neutral",
                0.0,
                {},
                "external_ai",
                {"ai_status": "not_sent", "reason": reason, "privacy_warning": AI_PRIVACY_WARNING},
                label != "no_face",
            )
        try:
            return self.client.analyze_frame(
                frame,
                self.api_key,
                face_box=face_box,
                send_cropped_face_only=self.settings.get("external_ai_send_cropped_face_only", True),
                timeout_seconds=self.settings.get("external_ai_timeout_seconds", 20.0),
                min_confidence=self.settings.get("external_ai_min_confidence", 0.55),
            )
        except TimeoutError:
            return unknown_result("timeout")
        except Exception as exc:
            return unknown_result(type(exc).__name__)


ExternalAIAgentExpressionClassifier = ExternalAIExpressionClassifier


def merge_ai_with_local(
    mode: str,
    local: ExpressionResult,
    ai: ExpressionResult | None,
    min_confidence: float = 0.55,
) -> ExpressionResult:
    """Choose a final result without forcing low-confidence AI outputs."""
    if mode == "external_ai":
        if local.label == "no_face":
            return local
        if ai and ai.source == "external_ai" and ai.confidence >= min_confidence and ai.label != "unknown":
            return ai
        return ExpressionResult(
            "unknown",
            "neutral",
            0.0,
            {},
            "external_ai_fallback",
            {"ai_fallback": True, "local_label": local.label},
            local.face_detected,
        )
    if mode == "hybrid_ai" and ai and ai.source == "external_ai":
        if local.label == "no_face":
            return local
        if ai.confidence >= min_confidence and ai.label not in {"unknown", "no_face"}:
            return ExpressionResult(
                ai.label,
                ai.group,
                ai.confidence,
                ai.probabilities,
                "external_ai",
                {"hybrid_ai_choice": "external_ai", **ai.debug},
                ai.face_detected,
            )
    return local
