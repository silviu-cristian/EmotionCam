import json

import pytest

from app.core.user_profile import UserProfile, normalize_email, normalize_name


def test_profile_saves_only_expected_local_fields(tmp_path):
    path = tmp_path / "user_profile.json"
    profile = UserProfile(path)
    profile.update({"name": "  Silviu  Test ", "email": "person@example.com"})
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["name"] == "Silviu Test"
    assert saved["email"] == "person@example.com"
    assert "password" not in saved


def test_profile_validation():
    assert normalize_name("Anne-Marie O'Brien") == "Anne-Marie O'Brien"
    assert normalize_email(" person@example.com ") == "person@example.com"
    with pytest.raises(ValueError):
        normalize_name("123")
    with pytest.raises(ValueError):
        normalize_email("invalid", required=True)


def test_last_summary_date_round_trips(tmp_path):
    path = tmp_path / "user_profile.json"
    profile = UserProfile(path)
    profile.update({"last_summary_sent_date": "2026-06-15"})
    assert UserProfile(path).data["last_summary_sent_date"] == "2026-06-15"
