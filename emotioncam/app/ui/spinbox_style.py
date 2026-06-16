"""Reliable visible spin-box arrows for both EmotionCam themes."""

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPolygonF
from PySide6.QtWidgets import QApplication, QProxyStyle, QStyle


class SpinBoxArrowStyle(QProxyStyle):
    """Paint spinner triangles after the base style so QSS cannot hide them."""

    def drawComplexControl(self, control, option, painter: QPainter, widget=None) -> None:
        super().drawComplexControl(control, option, painter, widget)
        if control != QStyle.CC_SpinBox:
            return
        application = QApplication.instance()
        theme = application.property("emotioncamTheme") if application else "dark"
        color = QColor("#233149" if theme == "light" else "#f2f6ff")
        if not option.state & QStyle.State_Enabled:
            color.setAlpha(105)
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(color)
        for subcontrol, up in (
            (QStyle.SC_SpinBoxUp, True),
            (QStyle.SC_SpinBoxDown, False),
        ):
            center = self.subControlRect(control, option, subcontrol, widget).center()
            points = (
                [
                    QPointF(center.x() - 4.5, center.y() + 2.5),
                    QPointF(center.x() + 4.5, center.y() + 2.5),
                    QPointF(center.x(), center.y() - 3.0),
                ]
                if up
                else [
                    QPointF(center.x() - 4.5, center.y() - 2.5),
                    QPointF(center.x() + 4.5, center.y() - 2.5),
                    QPointF(center.x(), center.y() + 3.0),
                ]
            )
            painter.drawPolygon(QPolygonF(points))
        painter.restore()
