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


def test_disabled_logger_creates_nothing(tmp_path):
    path = tmp_path / "history.jsonl"
    assert ExpressionLogger(path, enabled=False).log({}) is False
    assert not path.exists()


def test_logger_never_writes_image_fields(tmp_path):
    path = tmp_path / "history.jsonl"
    ExpressionLogger(path).log({"label": "neutral", "frame": b"pixels", "image": "face"})
    text = path.read_text(encoding="utf-8")
    assert "pixels" not in text
    assert '"image"' not in text
