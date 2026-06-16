from PySide6.QtCore import QPoint, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QDoubleSpinBox, QLineEdit, QSpinBox

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


def test_external_ai_controls_exist_and_do_not_expose_key():
    application = QApplication.instance() or QApplication([])
    dialog = SettingsDialog(DEFAULT_CONFIG)
    modes = [dialog.detection_mode.itemData(index) for index in range(dialog.detection_mode.count())]
    assert "external_ai" in modes
    assert "hybrid_ai" in modes
    assert dialog.ai_key.echoMode() == QLineEdit.Password
    values = dialog.values()
    ai_values = dialog.ai_values()
    assert "external_ai_api_key" not in values
    assert "external_ai_api_key" in ai_values
    dialog.close()
    assert application is not None


def test_enabling_external_ai_selects_hybrid_ai_mode():
    application = QApplication.instance() or QApplication([])
    dialog = SettingsDialog(DEFAULT_CONFIG)
    dialog.external_ai_enabled.setChecked(True)
    assert dialog.detection_mode.currentData() == "hybrid_ai"
    assert dialog.values()["expression_detection_mode"] == "hybrid_ai"
    dialog.close()
    assert application is not None


def test_local_mode_disables_external_ai_checkbox():
    application = QApplication.instance() or QApplication([])
    dialog = SettingsDialog({**DEFAULT_CONFIG, "external_ai_enabled": True, "expression_detection_mode": "hybrid_ai"})
    dialog.detection_mode.setCurrentIndex(dialog.detection_mode.findData("hybrid"))
    assert dialog.external_ai_enabled.isChecked() is False
    assert dialog.values()["expression_detection_mode"] == "hybrid"
    dialog.close()
    assert application is not None
