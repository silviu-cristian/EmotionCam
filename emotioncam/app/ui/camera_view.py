"""Live camera preview widget."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel


class CameraView(QLabel):
    def __init__(self) -> None:
        super().__init__("Camera is stopped")
        self.setObjectName("camera")
        self.setAlignment(Qt.AlignCenter)
        self.setMinimumSize(640, 400)
        self._image: QImage | None = None

    def set_frame(self, image: QImage) -> None:
        self._image = image
        self._refresh()

    def clear_frame(self, text: str = "Camera stopped") -> None:
        self._image = None
        self.clear()
        self.setText(text)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._refresh()

    def _refresh(self) -> None:
        if self._image is None:
            return
        pixmap = QPixmap.fromImage(self._image).scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.setPixmap(pixmap)
