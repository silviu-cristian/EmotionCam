import json
from datetime import date

from app.core.statistics import read_expression_history, summarize_day, supportive_message, weekly_balance


def test_statistics_parser_skips_corruption_and_old_fields(tmp_path):
    path = tmp_path / "history.jsonl"
    path.write_text(
        "\n".join(
            [
                json.dumps({"timestamp": "2026-06-15T09:00:00", "expression_label": "smile", "expression_group": "positive"}),
                "{broken",
                json.dumps({"timestamp": "2026-06-15T10:00:00", "label": "neutral", "group": "neutral"}),
                json.dumps({"timestamp": "bad", "expression_group": "negative"}),
                json.dumps({"timestamp": "2026-06-15T11:00:00", "expression_label": "mystery", "expression_group": "unexpected"}),
                json.dumps({"timestamp": "2026-06-15T12:00:00+03:00", "expression_label": "focused", "expression_group": "neutral"}),
            ]
        ),
        encoding="utf-8",
    )
    entries = read_expression_history(path)
    assert len(entries) == 4
    assert entries[-1]["group"] == "neutral"
    summary = summarize_day(entries, date(2026, 6, 15))
    assert summary.analyzed_entries == 4
    assert summary.most_frequent_expression in {"smile", "neutral", "mystery"}
    assert summary.group_counts == {"positive": 1, "neutral": 3, "negative": 0}
    assert summary.label_counts["smile"] == 1
    assert round(sum(summary.group_percentages.values())) == 100
    assert "expression" in supportive_message(summary).lower() or "today" in supportive_message(summary).lower()


def test_weekly_balance_includes_seven_days():
    week = weekly_balance([], date(2026, 6, 15))
    assert len(week) == 7
    assert all(item["positive"] == 0 for item in week)


def test_empty_log_is_safe(tmp_path):
    assert read_expression_history(tmp_path / "missing.jsonl") == []
    assert summarize_day([], date(2026, 6, 15)).analyzed_entries == 0
