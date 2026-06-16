"""Resilient local statistics derived from metadata-only expression logs."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from .paths import history_path


GROUPS = ("positive", "neutral", "negative")
VALID_GROUPS = set(GROUPS)


@dataclass(frozen=True)
class StatisticsSummary:
    selected_date: date
    entries: list[dict[str, Any]]
    group_counts: dict[str, int]
    group_percentages: dict[str, float]
    label_counts: dict[str, int]
    most_frequent_expression: str
    most_positive_period: str
    most_serious_period: str
    analyzed_entries: int
    estimated_minutes: float


def _parse_timestamp(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed.astimezone().replace(tzinfo=None) if parsed.tzinfo else parsed
    except (ValueError, TypeError):
        return None


def _normalize_entry(raw: dict[str, Any]) -> dict[str, Any] | None:
    timestamp = _parse_timestamp(raw.get("timestamp"))
    if timestamp is None:
        return None
    group = str(raw.get("expression_group", raw.get("group", "neutral"))).lower()
    if group not in VALID_GROUPS:
        group = "neutral"
    label = str(raw.get("expression_label", raw.get("label", "unknown"))).strip() or "unknown"
    try:
        confidence = max(0.0, min(1.0, float(raw.get("confidence", 0.0))))
    except (TypeError, ValueError):
        confidence = 0.0
    return {"timestamp": timestamp, "group": group, "label": label, "confidence": confidence}


def read_expression_history(path: Path | None = None) -> list[dict[str, Any]]:
    source = path or history_path()
    if not source.exists():
        return []
    entries: list[dict[str, Any]] = []
    if source.suffix.lower() == ".csv":
        try:
            with source.open("r", encoding="utf-8-sig", newline="") as stream:
                records = list(csv.DictReader(stream))
        except (OSError, csv.Error):
            return []
    else:
        records = []
        try:
            with source.open("r", encoding="utf-8") as stream:
                for line in stream:
                    try:
                        value = json.loads(line)
                    except (json.JSONDecodeError, TypeError):
                        continue
                    if isinstance(value, dict):
                        records.append(value)
        except OSError:
            return []
    for record in records:
        normalized = _normalize_entry(record)
        if normalized:
            entries.append(normalized)
    return sorted(entries, key=lambda item: item["timestamp"])


def _period(entries: list[dict[str, Any]], group: str) -> str:
    hours = Counter(item["timestamp"].strftime("%H:00") for item in entries if item["group"] == group)
    return hours.most_common(1)[0][0] if hours else "Not available"


def summarize_day(entries: list[dict[str, Any]], selected: date) -> StatisticsSummary:
    chosen = [item for item in entries if item["timestamp"].date() == selected]
    group_counts = Counter(item["group"] for item in chosen)
    total = len(chosen)
    percentages = {
        group: (group_counts[group] * 100.0 / total if total else 0.0) for group in GROUPS
    }
    labels = Counter(item["label"] for item in chosen)
    return StatisticsSummary(
        selected,
        chosen,
        {group: group_counts[group] for group in GROUPS},
        percentages,
        dict(labels),
        labels.most_common(1)[0][0] if labels else "No data",
        _period(chosen, "positive"),
        _period(chosen, "negative"),
        total,
        round(total * 5.0 / 60.0, 1),
    )


def weekly_balance(entries: list[dict[str, Any]], end_date: date) -> list[dict[str, Any]]:
    result = []
    for offset in range(6, -1, -1):
        day = end_date - timedelta(days=offset)
        summary = summarize_day(entries, day)
        result.append({"date": day, **summary.group_percentages})
    return result


def supportive_message(summary: StatisticsSummary) -> str:
    if not summary.analyzed_entries:
        return "No visible-expression metadata was recorded for this day."
    percentages = summary.group_percentages
    if percentages["positive"] >= 50:
        return "You had many positive-expression moments today. Nice work keeping that energy."
    if percentages["negative"] >= 40:
        return (
            "There were more serious-expression moments today. Consider taking a short break, "
            "stretching, or doing something relaxing."
        )
    if len(summary.label_counts) >= 6:
        return "Your expression patterns varied throughout the day, which is normal during active work."
    return "Most of today looked steady and neutral. That can reflect visible focus or calm."


def export_summary(summary: StatisticsSummary, destination: Path, name: str = "") -> None:
    greeting = f"{name}, " if name else ""
    text = [
        f"EmotionCam visible-expression summary for {summary.selected_date.isoformat()}",
        "",
        f"{greeting}this summary was generated from local expression metadata.",
        f"Positive: {summary.group_percentages['positive']:.1f}%",
        f"Neutral: {summary.group_percentages['neutral']:.1f}%",
        f"Negative / serious: {summary.group_percentages['negative']:.1f}%",
        f"Most frequent expression: {summary.most_frequent_expression}",
        f"Most positive period: {summary.most_positive_period}",
        f"Most serious-expression period: {summary.most_serious_period}",
        f"Valid log entries: {summary.analyzed_entries}",
        "",
        supportive_message(summary),
        "",
        "Privacy note: This summary was generated locally from expression metadata logs. "
        "No images were included.",
    ]
    destination.write_text("\n".join(text), encoding="utf-8")
