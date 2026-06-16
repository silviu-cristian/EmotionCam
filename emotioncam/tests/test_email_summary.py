from datetime import date, datetime

from app.core.email_summary import build_email, due_summary_date
from app.core.statistics import summarize_day


def test_email_text_is_safe_and_image_free():
    summary = summarize_day([], date(2026, 6, 15))
    subject, body = build_email(summary, "Silviu")
    assert "2026-06-15" in subject
    assert "Silviu" in body
    assert "No images were included" in body
    assert "depressed" not in body.lower()


def test_daily_summary_due_once_after_send_time():
    profile = {
        "daily_email_summary_enabled": True,
        "summary_send_time": "20:00",
        "last_summary_sent_date": None,
    }
    assert due_summary_date(profile, datetime(2026, 6, 15, 20, 1)) == date(2026, 6, 15)
    profile["last_summary_sent_date"] = "2026-06-15"
    assert due_summary_date(profile, datetime(2026, 6, 15, 20, 2)) is None
