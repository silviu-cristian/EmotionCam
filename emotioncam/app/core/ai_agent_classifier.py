"""Optional AI classifier wrapper with consent and fallback safety."""

from __future__ import annotations

from typing import Any

from .ai_client import OpenAIExpressionClient, unknown_result
from .ai_privacy import AI_PRIVACY_WARNING
from .ai_settings import load_api_key, normalize_api_key
from .expression_backends import BaseExpressionClassifier, ExpressionResult
from .local_ai_client import LocalOllamaExpressionClient, LOCAL_AI_SOURCE


AI_RESULT_SOURCES = {"external_ai", LOCAL_AI_SOURCE}


class ExternalAIExpressionClassifier(BaseExpressionClassifier):
    """Classify a selected frame through an explicitly enabled AI provider."""

    PRIVACY_WARNING = AI_PRIVACY_WARNING

    def __init__(
        self,
        settings: dict[str, Any],
        api_key: str = "",
        client: OpenAIExpressionClient | LocalOllamaExpressionClient | None = None,
    ) -> None:
        self.settings = settings
        self.provider = str(settings.get("external_ai_provider", "openai")).strip().lower()
        if self.provider not in {"openai", "ollama"}:
            self.provider = "openai"
        self.api_key = normalize_api_key(api_key) or (load_api_key() if self.provider == "openai" else "")
        self.client = client or self._create_client()

    def _create_client(self) -> OpenAIExpressionClient | LocalOllamaExpressionClient:
        if self.provider == "ollama":
            return LocalOllamaExpressionClient(
                self.settings.get("local_ai_ollama_endpoint", "http://localhost:11434"),
                self.settings.get("local_ai_ollama_model", "llava:7b"),
            )
        return OpenAIExpressionClient(self.settings.get("external_ai_model", "gpt-4.1-mini"))

    def ready_to_send(self, face_box: tuple[int, int, int, int] | None = None) -> tuple[bool, str]:
        if not self.settings.get("external_ai_enabled", False):
            return False, "external_ai_disabled"
        if not self.settings.get("external_ai_consent_accepted", False):
            return False, "consent_required"
        if self.provider == "openai" and not self.api_key:
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
                LOCAL_AI_SOURCE if self.provider == "ollama" else "external_ai",
                {
                    "ai_status": "not_sent",
                    "reason": reason,
                    "provider": self.provider,
                    "privacy_warning": AI_PRIVACY_WARNING,
                },
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
            return unknown_result("timeout", source=LOCAL_AI_SOURCE if self.provider == "ollama" else "external_ai")
        except Exception as exc:
            return unknown_result(
                str(exc)[:180] or type(exc).__name__,
                source=LOCAL_AI_SOURCE if self.provider == "ollama" else "external_ai",
            )


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
        if ai and ai.source in AI_RESULT_SOURCES and ai.confidence >= min_confidence and ai.label != "unknown":
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
    if mode == "hybrid_ai" and ai and ai.source in AI_RESULT_SOURCES:
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
