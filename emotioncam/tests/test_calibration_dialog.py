from PySide6.QtWidgets import QApplication, QMessageBox

from app.core.config import DEFAULT_CONFIG
from app.core.expression_profile import ExpressionProfile
from app.ui.calibration_dialog import CalibrationDialog


def dialog_without_camera(tmp_path, monkeypatch):
    application = QApplication.instance() or QApplication([])
    monkeypatch.setattr(CalibrationDialog, "_open_camera", lambda self: self._show_ready_state())
    monkeypatch.setattr(
        "app.ui.calibration_dialog.ExpressionProfile",
        lambda: ExpressionProfile(tmp_path / "profile.json"),
    )
    return application, CalibrationDialog(dict(DEFAULT_CONFIG))


def test_manual_capture_does_not_start_automatically(tmp_path, monkeypatch):
    _, dialog = dialog_without_camera(tmp_path, monkeypatch)
    assert dialog.state == "ready"
    assert dialog.current_samples == []
    dialog.start_capture()
    assert dialog.state == "capturing"
    assert dialog.start_button.isEnabled() is False
    dialog.close()


def test_recapture_discards_pending_batch(tmp_path, monkeypatch):
    _, dialog = dialog_without_camera(tmp_path, monkeypatch)
    dialog.state = "review"
    dialog.current_samples = [[1.0] * 14]
    dialog.rejected = 3
    dialog.retake()
    assert dialog.state == "ready"
    assert dialog.current_samples == []
    assert dialog.rejected == 0
    assert dialog.start_button.isEnabled() is True
    dialog.close()


def test_too_few_samples_are_not_saved(tmp_path, monkeypatch):
    _, dialog = dialog_without_camera(tmp_path, monkeypatch)
    dialog.settings["minimum_samples_per_expression"] = 2
    dialog.current_samples = [[1.0] * 14]
    dialog._complete_capture()
    assert not dialog.profile.exists
    dialog.close()


def test_standard_save_replaces_and_add_more_appends(tmp_path, monkeypatch):
    _, dialog = dialog_without_camera(tmp_path, monkeypatch)
    dialog.settings["minimum_samples_per_expression"] = 1
    dialog.current_samples = [[1.0] * 14]
    dialog._complete_capture()
    assert dialog.profile.counts()["neutral"] == 1
    dialog.retake()
    dialog.current_samples = [[2.0] * 14]
    dialog._complete_capture()
    assert dialog.profile.counts()["neutral"] == 1
    dialog.close()

    application = QApplication.instance() or QApplication([])
    monkeypatch.setattr(CalibrationDialog, "_open_camera", lambda self: self._show_ready_state())
    monkeypatch.setattr(
        "app.ui.calibration_dialog.ExpressionProfile",
        lambda: ExpressionProfile(tmp_path / "profile.json"),
    )
    add_more = CalibrationDialog(dict(DEFAULT_CONFIG), add_more=True)
    add_more.settings["minimum_samples_per_expression"] = 1
    add_more.current_samples = [[3.0] * 14]
    add_more._complete_capture()
    assert add_more.profile.counts()["neutral"] == 2
    add_more.retake()
    assert add_more.profile.counts()["neutral"] == 1
    add_more.close()
    assert application is not None


def test_previous_next_and_dropdown_change_target(tmp_path, monkeypatch):
    _, dialog = dialog_without_camera(tmp_path, monkeypatch)
    first_key = dialog.example.pixmap().cacheKey()
    dialog.next_expression()
    assert dialog.index == 1
    assert dialog.previous_button.isEnabled()
    assert dialog.example.pixmap().cacheKey() != first_key
    dialog.previous_expression()
    assert dialog.index == 0
    dialog.target_selector.setCurrentIndex(6)
    assert dialog.selected_label == "surprised"
    assert "surprised" in dialog.prompt.text().lower()
    dialog.close()


def test_skip_button_removed(tmp_path, monkeypatch):
    _, dialog = dialog_without_camera(tmp_path, monkeypatch)
    labels = {button.text() for button in dialog.findChildren(type(dialog.next_button))}
    assert "Skip" not in labels
    assert {"Previous", "Start Capture", "Re-capture", "Next", "Finish"} <= labels
    dialog.close()
