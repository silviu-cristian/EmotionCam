"""EmotionCam application entry point."""

from __future__ import annotations

import sys
import ctypes
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.ui.main_window import MainWindow
from app.ui.spinbox_style import SpinBoxArrowStyle
from app.ui.style import apply_theme
from app.core.config import ConfigManager


def main() -> int:
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("EmotionCam.Local.1")
    except (AttributeError, OSError):
        pass
    application = QApplication(sys.argv)
    application.setApplicationName("EmotionCam")
    application.setOrganizationName("EmotionCam")
    application.setStyle(SpinBoxArrowStyle(application.style()))
    config = ConfigManager()
    apply_theme(config.data["theme"])
    asset_root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    icon = asset_root / "app" / "assets" / "icon.ico"
    if not icon.exists():
        icon = Path(__file__).resolve().parent / "assets" / "icon.ico"
    application.setWindowIcon(QIcon(str(icon)))
    window = MainWindow(config)
    window.setWindowIcon(application.windowIcon())
    window.show()
    return application.exec()


if __name__ == "__main__":
    raise SystemExit(main())
