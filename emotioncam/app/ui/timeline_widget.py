"""Recent expression timeline."""

from collections import deque

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPalette
from PySide6.QtWidgets import QWidget


COLORS = {
    "positive": QColor("#3d8ee6"),
    "negative": QColor("#e68a3d"),
    "neutral": QColor("#777f8d"),
}


class TimelineWidget(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setMinimumHeight(72)
        self.items: deque[tuple[str, str]] = deque(maxlen=30)

    def add_expression(self, label: str, group: str) -> None:
        self.items.append((label, group))
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), self.palette().color(QPalette.Base))
        if not self.items:
            painter.setPen(self.palette().color(QPalette.Text))
            painter.drawText(self.rect(), Qt.AlignCenter, "Recent expression timeline")
            return
        width = max(5.0, self.width() / max(30, len(self.items)))
        for index, (label, group) in enumerate(self.items):
            painter.setBrush(COLORS.get(group, COLORS["neutral"]))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(index * width + 1, 12, width - 2, 45, 2, 2)
        painter.setPen(self.palette().color(QPalette.Text))
        painter.drawText(8, self.height() - 3, self.items[-1][0].title())
