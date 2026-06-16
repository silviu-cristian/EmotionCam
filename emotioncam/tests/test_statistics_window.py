from PySide6.QtWidgets import QApplication

from app.ui.statistics_window import StatisticsWindow


def test_statistics_window_handles_empty_logs(monkeypatch):
    application = QApplication.instance() or QApplication([])
    monkeypatch.setattr("app.ui.statistics_window.read_expression_history", lambda: [])
    dialog = StatisticsWindow("dark")
    assert "No local expression metadata" in dialog.empty.text()
    assert dialog.cards["frequent"].text() == "No Data"
    dialog.close()
    assert application is not None
