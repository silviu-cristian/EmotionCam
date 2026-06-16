"""Interchangeable local expression-classification backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import Any

from .expression_classifier import ExpressionClassifier, NEGATIVE_LABELS
from .expression_features import extract_expression_features, feature_distance
from .expression_profile import ExpressionProfile
from .face_detector import FaceDetection
from .smoothing import EXPRESSION_GROUPS


@dataclass(frozen=True)
class ExpressionResult:
    label: str
    group: str
    confidence: float
    probabilities: dict[str, float]
    source: str
    debug: dict[str, Any]
    face_detected: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class BaseExpressionClassifier(ABC):
    @abstractmethod
    def classify(
        self,
        frame: Any,
        face_box: tuple[int, int, int, int] | None = None,
        landmarks: FaceDetection | None = None,
    ) -> ExpressionResult:
        raise NotImplementedError


class HeuristicExpressionClassifier(BaseExpressionClassifier):
    def __init__(self, threshold: float, negative_min: float, positive_min: float) -> None:
        self.classifier = ExpressionClassifier(threshold, negative_min, positive_min)

    def classify(self, frame: Any, face_box=None, landmarks=None) -> ExpressionResult:
        detection = landmarks or FaceDetection(face_box or (0, 0, 0, 0), 0.0)
        result = self.classifier.classify(frame, detection)
        return ExpressionResult(
            result["label"], result["group"], result["confidence"], result["probabilities"],
            "heuristic", {"backend": detection.backend}
        )


class PersonalizedExpressionClassifier(BaseExpressionClassifier):
    def __init__(self, profile: ExpressionProfile, confidence_threshold: float = 0.55) -> None:
        self.profile = profile
        self.threshold = confidence_threshold

    def classify(self, frame: Any, face_box=None, landmarks=None) -> ExpressionResult:
        sample = extract_expression_features(landmarks) if landmarks else None
        if not sample or not self.profile.exists:
            return self._unknown("profile_or_landmarks_unavailable")
        distances = {
            label: min(feature_distance(sample.values, candidate) for candidate in samples)
            for label, samples in self.profile.samples.items()
            if samples
        }
        if not distances:
            return self._unknown("profile_empty")
        probabilities = {label: 1.0 / (1.0 + distance * 4.0) for label, distance in distances.items()}
        label, confidence = max(probabilities.items(), key=lambda item: item[1])
        confidence *= sample.quality
        if confidence < self.threshold or (label in NEGATIVE_LABELS and confidence < 0.65):
            label = "unknown"
        return ExpressionResult(
            label,
            EXPRESSION_GROUPS.get(label, "neutral"),
            confidence,
            dict(sorted(probabilities.items(), key=lambda item: item[1], reverse=True)[:5]),
            "personalized",
            {"feature_quality": sample.quality, **sample.debug},
        )

    @staticmethod
    def _unknown(reason: str) -> ExpressionResult:
        return ExpressionResult("unknown", "neutral", 0.0, {}, "personalized", {"reason": reason})


class HybridExpressionClassifier(BaseExpressionClassifier):
    def __init__(self, heuristic: HeuristicExpressionClassifier, personalized: PersonalizedExpressionClassifier):
        self.heuristic = heuristic
        self.personalized = personalized

    def classify(self, frame: Any, face_box=None, landmarks=None) -> ExpressionResult:
        personal = self.personalized.classify(frame, face_box, landmarks)
        if personal.label != "unknown" and personal.confidence >= self.personalized.threshold:
            return ExpressionResult(
                personal.label, personal.group, personal.confidence, personal.probabilities,
                "personalized", {"hybrid_choice": "personalized", **personal.debug}
            )
        heuristic = self.heuristic.classify(frame, face_box, landmarks)
        if heuristic.confidence < 0.45:
            return ExpressionResult("unknown", "neutral", heuristic.confidence, heuristic.probabilities,
                                    "hybrid", {"hybrid_choice": "uncertain"})
        return ExpressionResult(
            heuristic.label, heuristic.group, heuristic.confidence, heuristic.probabilities,
            "heuristic_fallback", {"hybrid_choice": "heuristic_fallback", **heuristic.debug}
        )


class ExternalAIAgentExpressionClassifier(BaseExpressionClassifier):
    PRIVACY_WARNING = (
        "External AI agent analysis is not enabled. This would require explicitly sending "
        "images outside the app, so it is disabled by default."
    )

    def classify(self, frame: Any, face_box=None, landmarks=None) -> ExpressionResult:
        return ExpressionResult("unknown", "neutral", 0.0, {}, "external_ai_disabled",
                                {"privacy_warning": self.PRIVACY_WARNING})


def create_expression_classifier(
    settings: dict[str, Any], profile: ExpressionProfile | None = None
) -> BaseExpressionClassifier:
    profile = profile or ExpressionProfile()
    heuristic = HeuristicExpressionClassifier(
        settings["expression_confidence_threshold"],
        settings["negative_expression_min_confidence"],
        settings["positive_expression_min_confidence"],
    )
    personalized = PersonalizedExpressionClassifier(profile)
    mode = settings.get("expression_detection_mode", "heuristic")
    if mode == "personalized":
        return personalized
    if mode == "hybrid" and settings.get("personalized_profile_enabled", True) and profile.exists:
        return HybridExpressionClassifier(heuristic, personalized)
    return heuristic
