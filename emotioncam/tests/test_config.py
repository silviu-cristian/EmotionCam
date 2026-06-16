import json

from app.core.config import ConfigManager, DEFAULT_CONFIG


def test_defaults_and_save(tmp_path):
    path = tmp_path / "config.json"
    manager = ConfigManager(path)
    assert manager.data["local_logging_enabled"] is True
    manager.update({"camera_index": 2, "unexpected": "ignored"})
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["camera_index"] == 2
    assert "unexpected" not in saved


def test_invalid_config_uses_defaults(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{broken", encoding="utf-8")
    assert ConfigManager(path).data == DEFAULT_CONFIG


def test_existing_config_migrates_new_defaults(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"camera_index": 3}', encoding="utf-8")
    data = ConfigManager(path).data
    assert data["camera_index"] == 3
    assert data["face_missing_grace_seconds"] == 1.0
    assert data["debug_panel_enabled"] is False
    assert data["expression_detection_mode"] == "heuristic"
    assert data["store_raw_calibration_images"] is False
    assert data["theme"] == "dark"
    assert data["statistics_enabled"] is True
    assert data["daily_email_summary_enabled"] is False
    assert data["summary_send_time"] == "20:00"
    assert data["email_summary_use_tls"] is True
    assert data["email_summary_method"] == "smtp"
    assert data["external_ai_enabled"] is False
    assert data["external_ai_consent_accepted"] is False
    assert data["external_ai_request_interval_seconds"] == 10.0
    assert data["external_ai_timeout_seconds"] == 20.0
    assert data["external_ai_send_cropped_face_only"] is True


def test_api_key_is_not_saved_in_plain_config(tmp_path):
    path = tmp_path / "config.json"
    manager = ConfigManager(path)
    manager.update({"external_ai_api_key": "sk-test-secret", "external_ai_enabled": True})
    saved = path.read_text(encoding="utf-8")
    assert "sk-test-secret" not in saved
    assert "external_ai_api_key" not in saved


def test_enabled_external_ai_migrates_hybrid_mode_to_hybrid_ai(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(
        json.dumps(
            {
                "expression_detection_mode": "hybrid",
                "external_ai_enabled": True,
                "external_ai_consent_accepted": True,
            }
        ),
        encoding="utf-8",
    )
    assert ConfigManager(path).data["expression_detection_mode"] == "hybrid_ai"


def test_invalid_theme_falls_back_to_dark(tmp_path):
    path = tmp_path / "config.json"
    path.write_text('{"theme": "invisible"}', encoding="utf-8")
    assert ConfigManager(path).data["theme"] == "dark"
