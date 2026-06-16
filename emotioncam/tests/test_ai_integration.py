import json

import numpy as np

from app.core.ai_agent_classifier import ExternalAIExpressionClassifier, merge_ai_with_local
from app.core.ai_client import crop_frame_for_ai, parse_ai_response_json
from app.core.ai_rate_limiter import AIRateLimiter
from app.core.config import DEFAULT_CONFIG
from app.core.expression_backends import ExpressionResult


class FakeAIClient:
    def __init__(self, result=None, error=None):
        self.result = result or ExpressionResult(
            "smile_small", "positive", 0.82, {"smile_small": 0.82}, "external_ai", {}
        )
        self.error = error
        self.calls = 0

    def analyze_frame(self, *args, **kwargs):
        self.calls += 1
        if self.error:
            raise self.error
        return self.result


def ai_settings(**overrides):
    data = dict(DEFAULT_CONFIG)
    data.update(
        {
            "external_ai_enabled": True,
            "external_ai_consent_accepted": True,
            "expression_detection_mode": "hybrid_ai",
        }
    )
    data.update(overrides)
    return data


def test_consent_required_before_ai_sends_requests():
    client = FakeAIClient()
    classifier = ExternalAIExpressionClassifier(
        ai_settings(external_ai_consent_accepted=False),
        api_key="sk-test",
        client=client,
    )
    result = classifier.classify(np.zeros((40, 40, 3), dtype=np.uint8), (0, 0, 20, 20))
    assert result.label == "unknown"
    assert result.debug["reason"] == "consent_required"
    assert client.calls == 0


def test_no_request_when_ai_disabled_or_key_missing():
    client = FakeAIClient()
    disabled = ExternalAIExpressionClassifier(
        ai_settings(external_ai_enabled=False), api_key="sk-test", client=client
    )
    missing_key = ExternalAIExpressionClassifier(ai_settings(), api_key="", client=client)
    assert disabled.classify(None, (0, 0, 20, 20)).debug["reason"] == "external_ai_disabled"
    assert missing_key.classify(None, (0, 0, 20, 20)).debug["reason"] == "missing_api_key"
    assert client.calls == 0


def test_no_request_when_cropped_face_mode_has_no_face():
    client = FakeAIClient()
    classifier = ExternalAIExpressionClassifier(ai_settings(), api_key="sk-test", client=client)
    result = classifier.classify(np.zeros((40, 40, 3), dtype=np.uint8), None)
    assert result.label == "no_face"
    assert result.debug["reason"] == "face_not_found"
    assert client.calls == 0


def test_cropped_face_only_selection():
    frame = np.zeros((100, 120, 3), dtype=np.uint8)
    cropped, debug = crop_frame_for_ai(frame, (40, 30, 20, 20), True)
    assert debug["cropped"] is True
    assert cropped.shape[0] > 20
    full, full_debug = crop_frame_for_ai(frame, None, False)
    assert full_debug["cropped"] is False
    assert full.shape == frame.shape


def test_ai_response_json_validation_accepts_known_labels():
    payload = {
        "label": "smile_small",
        "group": "positive",
        "confidence": 0.78,
        "reason": "Visible slight smile.",
        "alternatives": [{"label": "neutral", "confidence": 0.18}],
    }
    result = parse_ai_response_json(json.dumps(payload), 0.55)
    assert result.label == "smile_small"
    assert result.group == "positive"
    assert result.source == "external_ai"


def test_invalid_label_and_low_confidence_fallback():
    invalid = parse_ai_response_json(
        json.dumps({"label": "identity_guess", "group": "positive", "confidence": 0.9}),
        0.55,
    )
    low = parse_ai_response_json(
        json.dumps({"label": "happy", "group": "positive", "confidence": 0.2}),
        0.55,
    )
    assert invalid.label == "unknown"
    assert low.label == "unknown"


def test_timeout_fallback_does_not_crash():
    classifier = ExternalAIExpressionClassifier(
        ai_settings(),
        api_key="sk-test",
        client=FakeAIClient(error=TimeoutError("slow")),
    )
    result = classifier.classify(np.zeros((40, 40, 3), dtype=np.uint8), (0, 0, 20, 20))
    assert result.label == "unknown"
    assert result.debug["reason"] == "timeout"


def test_hybrid_ai_falls_back_to_local_when_ai_uncertain():
    local = ExpressionResult("neutral", "neutral", 0.7, {"neutral": 0.7}, "heuristic", {})
    uncertain_ai = ExpressionResult("unknown", "neutral", 0.2, {}, "external_ai", {})
    assert merge_ai_with_local("hybrid_ai", local, uncertain_ai).label == "neutral"


def test_ai_rate_limiter_waits_between_requests():
    limiter = AIRateLimiter(10.0)
    assert limiter.due(100.0)
    limiter.mark_sent(100.0)
    assert not limiter.due(104.9)
    assert limiter.due(110.0)
