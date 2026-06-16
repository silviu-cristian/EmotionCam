import json

from app.core.logger import ALLOWED_FIELDS, ExpressionLogger


def test_metadata_only_logging(tmp_path):
    path = tmp_path / "history.jsonl"
    logger = ExpressionLogger(path)
    logger.log(
        {
            "label": "happy",
            "group": "positive",
            "confidence": 0.72,
            "face_detected": True,
            "frame": "must never be logged",
            "detection_mode": "hybrid",
            "classifier_source": "personalized",
            "personalized_profile_active": True,
            "external_ai_enabled": True,
            "ai_request_sent": True,
            "ai_result_label": "happy",
            "ai_result_confidence": 0.8,
            "ai_error": "",
            "final_result_source": "external_ai",
        },
        "Smile detected :)",
        24.8,
        "Background popup shown",
    )
    entry = json.loads(path.read_text(encoding="utf-8"))
    assert set(entry) == set(ALLOWED_FIELDS)
    assert entry["expression_label"] == "happy"
    assert "frame" not in entry
    assert entry["popup_displayed"] == "Background popup shown"
    assert entry["detection_mode"] == "hybrid"
    assert entry["classifier_source"] == "personalized"
    assert entry["personalized_profile_active"] is True
    assert entry["external_ai_enabled"] is True
    assert entry["ai_request_sent"] is True
    assert entry["ai_result_label"] == "happy"
    assert entry["final_result_source"] == "external_ai"


def test_disabled_logger_creates_nothing(tmp_path):
    path = tmp_path / "history.jsonl"
    assert ExpressionLogger(path, enabled=False).log({}) is False
    assert not path.exists()


def test_logger_never_writes_image_fields(tmp_path):
    path = tmp_path / "history.jsonl"
    ExpressionLogger(path).log(
        {
            "label": "neutral",
            "frame": b"pixels",
            "image": "face",
            "base64": "data:image/jpeg;base64,secret",
            "external_ai_api_key": "sk-test-secret",
        }
    )
    text = path.read_text(encoding="utf-8")
    assert "pixels" not in text
    assert '"image"' not in text
    assert "data:image" not in text
    assert "sk-test-secret" not in text
