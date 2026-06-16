from PySide6.QtWidgets import QApplication

from app.ui.style import DARK_STYLE, LIGHT_STYLE, apply_theme


def test_dark_and_light_themes_apply_app_wide():
    application = QApplication.instance() or QApplication([])
    assert apply_theme("light") == "light"
    assert application.property("emotioncamTheme") == "light"
    assert application.styleSheet() == LIGHT_STYLE
    assert apply_theme("dark") == "dark"
    assert application.styleSheet() == DARK_STYLE


def test_unknown_theme_falls_back_to_dark():
    application = QApplication.instance() or QApplication([])
    assert apply_theme("unsupported") == "dark"
    assert application.property("emotioncamTheme") == "dark"
