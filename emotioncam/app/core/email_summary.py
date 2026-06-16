"""Opt-in daily email summaries built only from local statistics text."""

from __future__ import annotations

import os
import smtplib
from datetime import date, datetime, timedelta
from email.message import EmailMessage
from pathlib import Path
from urllib.parse import quote

from .statistics import StatisticsSummary, supportive_message


SERVICE_NAME = "EmotionCam SMTP"


def build_email(summary: StatisticsSummary, name: str = "") -> tuple[str, str]:
    greeting = f"Hi {name}," if name else "Hello,"
    subject = f"Your EmotionCam summary for {summary.selected_date.isoformat()}"
    body = "\n".join(
        [
            greeting,
            "",
            "Here is your local visible-expression estimate summary:",
            f"Positive expression balance: {summary.group_percentages['positive']:.1f}%",
            f"Neutral expression balance: {summary.group_percentages['neutral']:.1f}%",
            f"More serious expression balance: {summary.group_percentages['negative']:.1f}%",
            f"Most frequent expression: {summary.most_frequent_expression}",
            f"Most positive period: {summary.most_positive_period}",
            f"Most serious-expression period: {summary.most_serious_period}",
            "",
            supportive_message(summary),
            "",
            "This summary was generated locally from expression metadata logs. No images were included.",
        ]
    )
    return subject, body


def store_password(username: str, password: str) -> bool:
    try:
        import keyring
        keyring.set_password(SERVICE_NAME, username, password)
        return True
    except (ImportError, Exception):
        return False


def load_password(username: str) -> str:
    try:
        import keyring
        return keyring.get_password(SERVICE_NAME, username) or ""
    except (ImportError, Exception):
        return ""


def send_smtp(profile: dict, summary: StatisticsSummary, password: str = "") -> None:
    recipient = profile["email"]
    username = profile.get("smtp_username", "")
    secret = password or load_password(username)
    if not profile.get("smtp_server") or not username or not secret:
        raise ValueError("SMTP server, username, and password are required.")
    subject, body = build_email(summary, profile.get("name", ""))
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = username
    message["To"] = recipient
    message.set_content(body)
    with smtplib.SMTP(profile["smtp_server"], int(profile["smtp_port"]), timeout=20) as client:
        if profile.get("smtp_use_tls", True):
            client.starttls()
        client.login(username, secret)
        client.send_message(message)


def open_mail_client(profile: dict, summary: StatisticsSummary) -> None:
    subject, body = build_email(summary, profile.get("name", ""))
    uri = f"mailto:{quote(profile['email'])}?subject={quote(subject)}&body={quote(body)}"
    os.startfile(uri)


def due_summary_date(profile: dict, now: datetime | None = None) -> date | None:
    current = now or datetime.now().astimezone()
    if not profile.get("daily_email_summary_enabled"):
        return None
    hour, minute = map(int, profile.get("summary_send_time", "20:00").split(":"))
    candidate = current.date() if (current.hour, current.minute) >= (hour, minute) else current.date() - timedelta(days=1)
    return None if profile.get("last_summary_sent_date") == candidate.isoformat() else candidate
