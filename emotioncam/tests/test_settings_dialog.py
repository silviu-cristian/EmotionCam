from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDoubleSpinBox, QSpinBox

from app.core.config import DEFAULT_CONFIG
from app.ui.settings_dialog import SettingsDialog


def test_all_numeric_settings_step_with_arrows():
    application = QApplication.instance() or QApplication([])
    dialog = SettingsDialog(DEFAULT_CONFIG)
    controls = dialog.findChildren(QSpinBox) + dialog.findChildren(QDoubleSpinBox)
    assert controls
    for control in controls:
        original = control.value()
        control.stepUp()
        assert control.value() > original
        control.stepDown()
        assert control.value() == original
        original = control.value()
        QTest.mouseClick(control, Qt.LeftButton, pos=QPoint(control.width() - 16, 5))
        assert control.value() > original
        QTest.mouseClick(
            control, Qt.LeftButton, pos=QPoint(control.width() - 16, control.height() - 5)
        )
        assert control.value() == original
    dialog.close()
    assert application is not None


def test_theme_setting_round_trips():
    application = QApplication.instance() or QApplication([])
    dialog = SettingsDialog({**DEFAULT_CONFIG, "theme": "light"})
    assert dialog.theme.currentData() == "light"
    assert dialog.values()["theme"] == "light"
    dialog.close()
    assert application is not None
