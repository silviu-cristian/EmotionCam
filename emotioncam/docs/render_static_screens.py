"""Render camera-free documentation screens for visual verification."""

from pathlib import Path
import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.core.config import DEFAULT_CONFIG
from app.ui.settings_dialog import SettingsDialog
from app.ui.spinbox_style import SpinBoxArrowStyle
from app.ui.startup_screen import StartupScreen
from app.ui.style import apply_theme


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "screenshots"


def render(widget, filename: str) -> None:
    widget.show()
    application.processEvents()
    pixmap = QPixmap(widget.size())
    pixmap.fill(Qt.transparent)
    widget.render(pixmap)
    pixmap.save(str(OUTPUT / filename))
    widget.close()


application = QApplication.instance() or QApplication([])
application.setStyle(SpinBoxArrowStyle(application.style()))
OUTPUT.mkdir(parents=True, exist_ok=True)

apply_theme("dark")
render(StartupScreen(True), "01_startup_screen.png")
dark = SettingsDialog(DEFAULT_CONFIG)
dark.resize(1280, 800)
render(dark, "04_settings_numeric_arrows_dark.png")

apply_theme("light")
light_settings = {**DEFAULT_CONFIG, "theme": "light"}
light = SettingsDialog(light_settings)
light.resize(1280, 800)
render(light, "05_settings_numeric_arrows_light.png")
theme = SettingsDialog(light_settings)
theme.resize(1280, 800)
render(theme, "06_settings_theme_toggle.png")
