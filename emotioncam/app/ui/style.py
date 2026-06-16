"""Application-wide dark and light themes."""

from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QApplication


THEMES = {"dark", "light"}

_COMMON = """
QWidget { font-family: "Segoe UI"; font-size: 10pt; }
QLabel#title { font-size: 28pt; font-weight: 700; }
QLabel#subtitle { font-size: 12pt; }
QLabel#metric { font-size: 22pt; font-weight: 700; color: #2878d7; }
QLabel#message { font-size: 13pt; font-weight: 600; padding: 10px; }
QLabel#camera { background: #080a0f; color: #e9edf5; border-radius: 12px; }
QPushButton { border-radius: 7px; padding: 9px 16px; font-weight: 600; }
QPushButton#primary { background: #2878d7; border-color: #3f91ed; color: white; }
QPushButton#primary:hover { background: #3588e8; }
QPushButton#danger { background: #7b3843; border-color: #a55764; color: white; }
QPushButton:disabled { color: #8992a1; }
QCheckBox { spacing: 7px; padding: 4px; }
QComboBox { border-radius: 6px; padding: 6px 28px 6px 8px; min-height: 24px; }
QComboBox::drop-down { width: 26px; border: none; }
QGroupBox { border-radius: 8px; margin-top: 12px; padding: 12px; font-weight: 600; }
QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; }
QProgressBar { border-radius: 6px; text-align: center; min-height: 18px; }
QProgressBar::chunk { background: #2878d7; border-radius: 5px; }
QSpinBox, QDoubleSpinBox {
  border-radius: 6px; padding: 6px 36px 6px 8px; min-height: 26px;
}
QSpinBox::up-button, QDoubleSpinBox::up-button {
  subcontrol-origin: border; subcontrol-position: top right;
  width: 32px; height: 50%; border-top-right-radius: 5px;
}
QSpinBox::down-button, QDoubleSpinBox::down-button {
  subcontrol-origin: border; subcontrol-position: bottom right;
  width: 32px; height: 50%; border-bottom-right-radius: 5px;
}
QSpinBox::up-arrow, QDoubleSpinBox::up-arrow,
QSpinBox::down-arrow, QDoubleSpinBox::down-arrow { width: 10px; height: 7px; }
QLabel#matchIndicator[matchState="match"] {
  background: #dff7e8; color: #17633a; border: 1px solid #54a878;
  border-radius: 8px; font-weight: 700;
}
QLabel#matchIndicator[matchState="waiting"] { border-radius: 8px; }
"""

DARK_STYLE = _COMMON + """
QWidget { background: #11141b; color: #e9edf5; }
QMainWindow, QDialog { background: #11141b; }
QLabel#title { color: #f4f7ff; }
QLabel#subtitle { color: #a9b4c7; }
QLabel#message { color: #f2c879; }
QLabel#camera { border: 1px solid #303746; }
QFrame#card { background: #191e28; border: 1px solid #2b3342; border-radius: 12px; }
QPushButton { background: #283348; border: 1px solid #3b4963; }
QPushButton:hover { background: #33425d; }
QPushButton:pressed { background: #202a3b; }
QSpinBox, QDoubleSpinBox, QComboBox {
  background: #202633; color: #eef3fb; border: 1px solid #5f6f8d;
  selection-background-color: #2878d7;
}
QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
  background: #354158; border-left: 1px solid #7183a5;
}
QSpinBox::up-button, QDoubleSpinBox::up-button { border-bottom: 1px solid #596984; }
QSpinBox::down-button, QDoubleSpinBox::down-button { border-top: 1px solid #596984; }
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover { background: #4b6287; }
QSpinBox::up-button:pressed, QDoubleSpinBox::up-button:pressed,
QSpinBox::down-button:pressed, QDoubleSpinBox::down-button:pressed { background: #243047; }
QGroupBox { border: 1px solid #303848; }
QProgressBar { background: #202633; border: 1px solid #4c5a73; }
QScrollArea { border: 1px solid #303848; }
QMenuBar, QMenu, QStatusBar { background: #171c25; color: #e9edf5; }
QMenu::item:selected { background: #33425d; }
QToolTip { background: #222938; color: white; border: 1px solid #44516a; }
QLabel#matchIndicator[matchState="waiting"] {
  background: #252b37; color: #aeb8c8; border: 1px solid #465168;
}
"""

LIGHT_STYLE = _COMMON + """
QWidget { background: #f4f6fa; color: #202633; }
QMainWindow, QDialog { background: #f4f6fa; }
QLabel#title { color: #162033; }
QLabel#subtitle { color: #58677e; }
QLabel#message { color: #8a5a00; }
QLabel#camera { border: 1px solid #c7ceda; }
QFrame#card { background: #ffffff; border: 1px solid #d4dae4; border-radius: 12px; }
QPushButton { background: #ffffff; border: 1px solid #bac5d5; }
QPushButton:hover { background: #eaf2fc; border-color: #8ea9cc; }
QPushButton:pressed { background: #dce9f8; }
QPushButton:disabled { background: #eef1f5; }
QSpinBox, QDoubleSpinBox, QComboBox {
  background: #ffffff; color: #182236; border: 1px solid #9ba9bd;
  selection-background-color: #2878d7;
}
QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
  background: #e7edf5; border-left: 1px solid #9ba9bd;
}
QSpinBox::up-button, QDoubleSpinBox::up-button { border-bottom: 1px solid #b8c3d2; }
QSpinBox::down-button, QDoubleSpinBox::down-button { border-top: 1px solid #b8c3d2; }
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover { background: #d1e2f7; }
QSpinBox::up-button:pressed, QDoubleSpinBox::up-button:pressed,
QSpinBox::down-button:pressed, QDoubleSpinBox::down-button:pressed { background: #bcd2ee; }
QGroupBox { background: #ffffff; border: 1px solid #d1d8e3; }
QProgressBar { background: #e8edf4; border: 1px solid #b8c3d2; }
QScrollArea { border: 1px solid #d1d8e3; }
QMenuBar, QMenu, QStatusBar { background: #ffffff; color: #202633; }
QMenu::item:selected { background: #dce9f8; }
QToolTip { background: white; color: #202633; border: 1px solid #9ba9bd; }
QLabel#matchIndicator[matchState="waiting"] {
  background: #edf1f6; color: #536176; border: 1px solid #bdc7d5;
}
"""

APP_STYLE = DARK_STYLE


def apply_theme(theme: str) -> str:
    """Apply a supported theme to the entire current application."""
    selected = theme if theme in THEMES else "dark"
    application = QApplication.instance()
    if application is None:
        return selected
    application.setProperty("emotioncamTheme", selected)
    palette = QPalette()
    if selected == "light":
        values = ("#f4f6fa", "#202633", "#ffffff", "#182236", "#e7edf5")
    else:
        values = ("#11141b", "#e9edf5", "#121620", "#eef3fb", "#354158")
    window, window_text, base, text, button = map(QColor, values)
    palette.setColor(QPalette.Window, window)
    palette.setColor(QPalette.WindowText, window_text)
    palette.setColor(QPalette.Base, base)
    palette.setColor(QPalette.Text, text)
    palette.setColor(QPalette.Button, button)
    palette.setColor(QPalette.ButtonText, text)
    application.setPalette(palette)
    application.setStyleSheet(LIGHT_STYLE if selected == "light" else DARK_STYLE)
    return selected
