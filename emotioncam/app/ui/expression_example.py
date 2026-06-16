"""Render bundled expression-example specs as local vector graphics."""

from __future__ import annotations

import json
import sys
from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen, QPixmap


@lru_cache(maxsize=1)
def _specs() -> dict:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return json.loads((root / "app" / "assets" / "expression_examples.json").read_text(encoding="utf-8"))


def expression_example_pixmap(label: str, size: int = 220) -> QPixmap:
    spec = _specs().get(label, _specs()["neutral"])
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor("#111620"))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    accent = {"blue": "#3d9cff", "orange": "#ff9b3d", "gray": "#9aa5b5"}[spec["accent"]]
    painter.setPen(QPen(QColor(accent), 5, Qt.SolidLine, Qt.RoundCap))
    painter.setBrush(QColor("#202938"))
    painter.drawEllipse(QRectF(20, 20, size - 40, size - 40))
    painter.setBrush(Qt.NoBrush)

    eye_y = 88
    for x in (72, 148):
        if spec["eyes"] == "wide":
            painter.drawEllipse(QPointF(x, eye_y), 12, 17)
        elif spec["eyes"] in {"happy", "squint", "tired", "soft"}:
            offset = 4 if spec["eyes"] in {"tired", "soft"} else 0
            painter.drawArc(QRectF(x - 15, eye_y - 5 + offset, 30, 18), 0, 180 * 16)
        elif spec["eyes"] == "side":
            painter.drawEllipse(QPointF(x + 5, eye_y), 7, 9)
        else:
            painter.drawEllipse(QPointF(x, eye_y), 8, 11)

    brow_y = 60
    if spec["brows"] == "raised":
        painter.drawArc(QRectF(52, brow_y - 12, 40, 20), 0, 180 * 16)
        painter.drawArc(QRectF(128, brow_y - 12, 40, 20), 0, 180 * 16)
    elif spec["brows"] == "furrow":
        painter.drawLine(55, brow_y, 90, brow_y + 10)
        painter.drawLine(130, brow_y + 10, 165, brow_y)
    elif spec["brows"] in {"asymmetric", "inner_up"}:
        painter.drawLine(55, brow_y + 5, 90, brow_y - 5)
        painter.drawLine(130, brow_y - 5, 165, brow_y + 5)
    else:
        painter.drawLine(55, brow_y, 90, brow_y)
        painter.drawLine(130, brow_y, 165, brow_y)

    mouth = spec["mouth"]
    if mouth == "open":
        painter.drawEllipse(QPointF(110, 148), 16, 24)
    elif mouth == "open_smile":
        painter.drawArc(QRectF(65, 120, 90, 65), 180 * 16, 180 * 16)
        painter.drawLine(70, 151, 150, 151)
    elif mouth in {"smile_small", "smile_big"}:
        width = 70 if mouth == "smile_big" else 52
        painter.drawArc(QRectF(110 - width / 2, 125, width, 45), 180 * 16, 180 * 16)
    elif mouth == "frown":
        painter.drawArc(QRectF(80, 145, 60, 35), 0, 180 * 16)
    elif mouth == "asymmetric":
        painter.drawLine(80, 154, 115, 145)
        painter.drawLine(115, 145, 145, 150)
    else:
        painter.drawLine(82, 150, 138, 150)
    painter.end()
    return pixmap


def expressions_match(target: str, detected: str) -> bool:
    if target == detected:
        return True
    families = [
        {"smile_small", "smile_big", "smile", "happy", "laughing", "amused"},
        {"focused", "thinking"},
        {"concerned", "sad"},
        {"tired", "bored"},
    ]
    return any(target in family and detected in family for family in families)
