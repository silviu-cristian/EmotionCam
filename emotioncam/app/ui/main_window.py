"""Main EmotionCam window and dashboard orchestration."""

from __future__ import annotations

import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QMenu,
    QStackedWidget,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)

from app.core.camera_worker import CameraWorker
from app.core.ai_client import OpenAIExpressionClient
from app.core.ai_settings import load_api_key, normalize_api_key, store_api_key as store_openai_api_key
from app.core.background_notifications import BackgroundNotificationEngine
from app.core.config import ConfigManager
from app.core.interaction_engine import InteractionEngine
from app.core.logger import ExpressionLogger
from app.core.expression_profile import ExpressionProfile
from app.core.email_summary import due_summary_date, open_mail_client, send_smtp, store_password
from app.core.statistics import read_expression_history, summarize_day
from app.core.user_profile import UserProfile
from app.core.privacy import PRIVACY_NOTICE
from app.ui.camera_view import CameraView
from app.ui.calibration_dialog import CalibrationDialog
from app.ui.settings_dialog import SettingsDialog
from app.ui.startup_screen import StartupScreen
from app.ui.timeline_widget import TimelineWidget
from app.ui.style import apply_theme
from app.ui.statistics_window import StatisticsWindow


class MainWindow(QMainWindow):
    email_status_changed = Signal(str)
    ai_status_changed = Signal(str)
    ai_test_finished = Signal(bool, str)

    def __init__(self, config: ConfigManager | None = None) -> None:
        super().__init__()
        self.setWindowTitle("EmotionCam")
        self.resize(1280, 800)
        self.setMinimumSize(1000, 680)

        self.config = config or ConfigManager()
        self.user_profile = UserProfile()
        apply_theme(self.config.data["theme"])
        self.logger = ExpressionLogger(enabled=self.config.data["local_logging_enabled"])
        self.interaction = InteractionEngine(
            self.config.data["message_cooldown_seconds"],
            self.config.data["interaction_messages_enabled"],
            self.user_profile.data["name"],
        )
        self.notifications = BackgroundNotificationEngine(
            self.config.data["negative_popup_cooldown_seconds"],
            self.config.data["positive_recovery_popup_cooldown_seconds"],
            self.user_profile.data["name"],
        )
        self.worker: CameraWorker | None = None
        self.analysis_paused = False
        self.last_log_time = 0.0
        self.last_logged_label = ""
        self.last_timeline_time = 0.0
        self.background_active = False
        self._exiting = False
        self._summary_send_running = False
        self.session_ai_api_key = ""

        self.pages = QStackedWidget()
        self.setCentralWidget(self.pages)
        self.startup = StartupScreen(self.config.data["local_logging_enabled"])
        self.dashboard = self._build_dashboard()
        self.pages.addWidget(self.startup)
        self.pages.addWidget(self.dashboard)
        self.pages.setCurrentWidget(self.startup)

        self.startup.start_requested.connect(self._start_from_startup)
        self.startup.settings_requested.connect(self.open_settings)
        self.startup.exit_requested.connect(QApplication.quit)
        self.statusBar().showMessage("Ready - no camera frames are saved")
        self._create_tray()
        self._create_help_menu()
        self.summary_timer = QTimer(self)
        self.summary_timer.timeout.connect(self._check_daily_summary)
        self.summary_timer.start(60_000)
        self.email_status_changed.connect(self.statusBar().showMessage)
        self.ai_status_changed.connect(self.statusBar().showMessage)
        QTimer.singleShot(2_000, self._check_daily_summary)

    def _build_dashboard(self) -> QWidget:
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(18, 18, 18, 14)
        outer.setSpacing(12)

        heading = QHBoxLayout()
        title = QLabel("EmotionCam")
        title.setObjectName("title")
        self.privacy_mode_label = QLabel("LOCAL BY DEFAULT  |  EXTERNAL AI OFF  |  NO IMAGE SAVING")
        self.privacy_mode_label.setObjectName("subtitle")
        heading.addWidget(title)
        heading.addStretch()
        heading.addWidget(self.privacy_mode_label)
        outer.addLayout(heading)

        body = QHBoxLayout()
        body.setSpacing(14)
        self.camera_view = CameraView()
        body.addWidget(self.camera_view, 3)

        panel = QFrame()
        panel.setObjectName("card")
        panel.setMinimumWidth(330)
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(20, 18, 20, 18)
        panel_layout.addWidget(QLabel("Current likely expression"))
        self.expression_label = QLabel("Unknown")
        self.expression_label.setObjectName("metric")
        panel_layout.addWidget(self.expression_label)
        self.group_label = QLabel("Expression group: Neutral")
        self.confidence_label = QLabel("Confidence: --")
        self.mode_label = QLabel()
        self.profile_label = QLabel()
        self.ai_status_label = QLabel("External AI: off")
        self.ai_detail_label = QLabel("AI result: --")
        self.message_label = QLabel("Start the camera when you are ready.")
        self.message_label.setObjectName("message")
        self.message_label.setWordWrap(True)
        panel_layout.addWidget(self.group_label)
        panel_layout.addWidget(self.confidence_label)
        panel_layout.addWidget(self.mode_label)
        panel_layout.addWidget(self.profile_label)
        panel_layout.addWidget(self.ai_status_label)
        panel_layout.addWidget(self.ai_detail_label)
        panel_layout.addWidget(self.message_label)
        panel_layout.addWidget(QLabel("Recent expression timeline"))
        self.timeline = TimelineWidget()
        panel_layout.addWidget(self.timeline)
        self.debug_panel = QFrame()
        self.debug_panel.setObjectName("card")
        debug_layout = QVBoxLayout(self.debug_panel)
        debug_layout.setContentsMargins(10, 8, 10, 8)
        debug_layout.addWidget(QLabel("Expression debug"))
        self.debug_label = QLabel("Waiting for analysis")
        self.debug_label.setWordWrap(True)
        self.debug_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        debug_layout.addWidget(self.debug_label)
        self.debug_panel.setVisible(self.config.data["debug_panel_enabled"])
        panel_layout.addWidget(self.debug_panel)
        panel_layout.addStretch()
        self.logging_label = QLabel()
        self.background_label = QLabel("Background mode: inactive")
        self.privacy_label = QLabel(PRIVACY_NOTICE)
        self.privacy_label.setWordWrap(True)
        self.privacy_label.setObjectName("subtitle")
        panel_layout.addWidget(self.logging_label)
        panel_layout.addWidget(self.background_label)
        panel_layout.addWidget(self.privacy_label)
        body.addWidget(panel, 1)
        outer.addLayout(body, 1)

        controls = QHBoxLayout()
        self.start_button = QPushButton("Start Camera")
        self.start_button.setObjectName("primary")
        self.stop_button = QPushButton("Stop Camera")
        self.pause_button = QPushButton("Pause Analysis")
        settings = QPushButton("Settings")
        logs = QPushButton("Open Logs")
        statistics = QPushButton("Statistics")
        statistics.setEnabled(self.config.data["statistics_enabled"])
        background = QPushButton("Run in background")
        debug = QPushButton("Toggle Debug")
        calibrate = QPushButton("Improve detection with calibration")
        exit_button = QPushButton("Exit")
        exit_button.setObjectName("danger")
        self.start_button.clicked.connect(self.start_camera)
        self.stop_button.clicked.connect(self.stop_camera)
        self.pause_button.clicked.connect(self.toggle_pause)
        settings.clicked.connect(self.open_settings)
        logs.clicked.connect(self.open_logs)
        statistics.clicked.connect(self.open_statistics)
        background.clicked.connect(self.run_in_background)
        debug.clicked.connect(self.toggle_debug)
        calibrate.clicked.connect(lambda: self.open_calibration(True))
        exit_button.clicked.connect(self.exit_app)
        for button in (
            self.start_button, self.stop_button, self.pause_button, settings, logs, statistics, background,
            debug, calibrate
        ):
            controls.addWidget(button)
        controls.addStretch()
        controls.addWidget(exit_button)
        outer.addLayout(controls)
        self._refresh_logging_status()
        self._refresh_profile_status()
        self._set_camera_buttons(False)
        return page

    def _start_from_startup(self, logging_enabled: bool) -> None:
        self.config.update(
            {"local_logging_enabled": logging_enabled, "first_launch_complete": True}
        )
        self.logger.enabled = logging_enabled
        self._refresh_logging_status()
        self.pages.setCurrentWidget(self.dashboard)
        self.start_camera()

    def start_camera(self) -> None:
        if self.worker and self.worker.isRunning():
            return
        self.analysis_paused = False
        self.pause_button.setText("Pause Analysis")
        worker_settings = dict(self.config.data)
        if self.session_ai_api_key:
            worker_settings["_session_external_ai_api_key"] = self.session_ai_api_key
        self.worker = CameraWorker(worker_settings)
        self.worker.frame_ready.connect(self.camera_view.set_frame)
        self.worker.result_ready.connect(self._handle_result)
        self.worker.status_changed.connect(self.statusBar().showMessage)
        self.worker.camera_error.connect(self._handle_camera_error)
        self.worker.finished.connect(lambda: self._set_camera_buttons(False))
        self.worker.start()
        self._set_camera_buttons(True)

    def stop_camera(self) -> None:
        worker = self.worker
        if worker:
            worker.stop()
            worker.wait(2500)
            self.worker = None
        self.camera_view.clear_frame("Camera stopped")
        self._set_camera_buttons(False)
        self.statusBar().showMessage("Camera stopped - no frames saved")

    def toggle_pause(self) -> None:
        if not self.worker or not self.worker.isRunning():
            return
        self.analysis_paused = not self.analysis_paused
        self.worker.set_analysis_paused(self.analysis_paused)
        self.pause_button.setText("Resume Analysis" if self.analysis_paused else "Pause Analysis")
        self.statusBar().showMessage(
            "Analysis paused - camera preview remains active"
            if self.analysis_paused
            else "Analysis resumed - processing locally"
        )

    def _handle_result(self, result: dict) -> None:
        label = result["label"]
        group = result["group"]
        confidence = result["confidence"]
        self.expression_label.setText(label.replace("_", " ").title())
        self.group_label.setText(f"Expression group: {group.title()}")
        self.mode_label.setText(
            f"Detection mode: {self._detection_mode_text(result.get('detection_mode', self.config.data['expression_detection_mode']))}"
        )
        active = result.get("personalized_profile_active", ExpressionProfile().exists)
        self.profile_label.setText(f"Personalized profile: {'active' if active else 'inactive'}")
        mode = result.get("detection_mode", self.config.data["expression_detection_mode"])
        ai_enabled = bool(result.get("external_ai_enabled", self.config.data["external_ai_enabled"]))
        ai_status = result.get("ai_status", "Off")
        if ai_enabled and mode not in {"external_ai", "hybrid_ai"}:
            ai_status = "Enabled in settings, inactive in current detection mode"
        self.ai_status_label.setText(f"External AI: {'enabled' if ai_enabled else 'off'} | {ai_status}")
        ai_result = result.get("ai_result_label", "")
        ai_confidence = float(result.get("ai_result_confidence", 0.0) or 0.0)
        ai_time = result.get("last_ai_result_time", "")
        self.ai_detail_label.setText(
            f"AI result: {ai_result or '--'}"
            + (f" ({ai_confidence:.0%})" if ai_result else "")
            + (f" at {ai_time}" if ai_time else "")
        )
        self._refresh_ai_header()
        if self.config.data["show_confidence_values"]:
            self.confidence_label.setText(f"Confidence: {confidence:.0%}")
        else:
            self.confidence_label.setText("Confidence values hidden")

        message = ""
        if result.get("paused"):
            self.message_label.setText("Analysis paused. Preview remains local.")
        else:
            message = self.interaction.message_for(label, group)
            if message:
                self.message_label.setText(message)
            elif label == "no_face":
                self.message_label.setText("No face detected.")
            elif label == "low_confidence":
                self.message_label.setText("Low-confidence expression estimate.")

        probabilities = ", ".join(
            f"{key}: {value:.0%}" for key, value in result.get("probabilities", {}).items()
        )
        self.debug_label.setText(
            f"Raw: {result.get('raw_label', '--')}\n"
            f"Smoothed: {label} ({confidence:.0%})\n"
            f"Group: {group}\n"
            f"Face confidence: {result.get('face_detection_confidence', 0.0):.0%}\n"
            f"Grace tracking: {'yes' if result.get('using_face_grace') else 'no'}\n"
            f"Detector: {result.get('detector_backend', '--')}\n"
            f"Classifier source: {result.get('classifier_source', '--')}\n"
            f"Local result: {result.get('local_result_label', '--')} "
            f"({result.get('local_result_confidence', 0.0):.0%})\n"
            f"AI status: {ai_status}\n"
            f"AI result: {ai_result or '--'} ({ai_confidence:.0%})\n"
            f"Final source: {result.get('final_result_source', '--')}\n"
            f"Top estimates: {probabilities or '--'}"
        )

        popup = ""
        if (
            self.background_active
            and self.config.data["background_popups_enabled"]
            and not result.get("paused")
        ):
            popup = self.notifications.message_for(group)
            if popup:
                self.tray.showMessage("EmotionCam visible expression estimate", popup)

        now = time.monotonic()
        if now - self.last_timeline_time >= 0.5 and not result.get("paused"):
            self.timeline.add_expression(label, group)
            self.last_timeline_time = now
        if (
            self.logger.enabled
            and not result.get("paused")
            and (popup or label != self.last_logged_label or now - self.last_log_time >= 5.0)
        ):
            self.logger.log(result, message, result.get("fps", 0.0), popup)
            self.last_logged_label = label
            self.last_log_time = now

    def _handle_camera_error(self, message: str) -> None:
        self.camera_view.clear_frame("Camera unavailable")
        self._set_camera_buttons(False)
        self.statusBar().showMessage(message)
        QMessageBox.warning(self, "Camera Error", message)

    def open_settings(self) -> None:
        dialog = SettingsDialog(self.config.data, self, self.user_profile)
        dialog.clear_logs_requested.connect(self.clear_logs)
        dialog.open_logs_requested.connect(self.open_logs)
        dialog.calibrate_requested.connect(
            lambda add_more: (self.open_calibration(add_more), dialog._load(self.config.data))
        )
        dialog.delete_profile_requested.connect(
            lambda: (self.delete_profile(), dialog._load(self.config.data))
        )
        dialog.export_profile_requested.connect(self.export_profile)
        dialog.import_profile_requested.connect(
            lambda: (self.import_profile(), dialog._load(self.config.data))
        )
        dialog.test_email_requested.connect(self._send_test_email)
        dialog.test_ai_requested.connect(self._test_ai_connection)
        self.ai_test_finished.connect(dialog.set_ai_test_result)
        if dialog.exec():
            was_running = bool(self.worker and self.worker.isRunning())
            if was_running:
                self.stop_camera()
            self._handle_ai_key_from_settings(dialog.ai_values())
            self.config.update(dialog.values())
            self.user_profile.load()
            apply_theme(self.config.data["theme"])
            self.logger.enabled = self.config.data["local_logging_enabled"]
            self.startup.logging_checkbox.setChecked(self.logger.enabled)
            self.interaction = InteractionEngine(
                self.config.data["message_cooldown_seconds"],
                self.config.data["interaction_messages_enabled"],
                self.user_profile.data["name"],
            )
            self.notifications = BackgroundNotificationEngine(
                self.config.data["negative_popup_cooldown_seconds"],
                self.config.data["positive_recovery_popup_cooldown_seconds"],
                self.user_profile.data["name"],
            )
            self.debug_panel.setVisible(self.config.data["debug_panel_enabled"])
            self._refresh_logging_status()
            self._refresh_profile_status()
            self._refresh_ai_header()
            if was_running:
                self.start_camera()

    def open_statistics(self) -> None:
        StatisticsWindow(self.config.data["theme"], self).exec()

    def _send_test_email(self, values: dict) -> None:
        try:
            candidate = UserProfile(self.user_profile.path)
            candidate.update(values)
            summary = summarize_day(read_expression_history(), datetime.now().astimezone().date())
            if values.get("email_delivery_mode") == "smtp":
                password = values.get("smtp_password", "")
                if values.get("store_password_securely") and password:
                    if not store_password(values.get("smtp_username", ""), password):
                        QMessageBox.information(
                            self, "Email Summary",
                            "Secure credential storage is unavailable. The password was not saved."
                        )
                send_smtp(candidate.data, summary, password)
                QMessageBox.information(self, "Email Summary", "Test summary email sent.")
            else:
                open_mail_client(candidate.data, summary)
        except (ValueError, OSError, ConnectionError) as exc:
            QMessageBox.warning(self, "Email Summary", str(exc))
        except Exception as exc:
            QMessageBox.warning(self, "Email Summary", f"Could not send the test summary: {exc}")

    def _handle_ai_key_from_settings(self, values: dict) -> None:
        api_key = normalize_api_key(values.get("external_ai_api_key", ""))
        if not api_key:
            return
        if values.get("external_ai_store_key_securely", True):
            if store_openai_api_key(api_key):
                self.session_ai_api_key = ""
                self.statusBar().showMessage("OpenAI API key stored with secure credential storage")
                return
            self.session_ai_api_key = api_key
            QMessageBox.information(
                self,
                "External AI API Key",
                "Secure credential storage is unavailable. The API key will be used for this "
                "app session only and was not written to config.json.",
            )
            return
        self.session_ai_api_key = api_key
        QMessageBox.information(
            self,
            "External AI API Key",
            "The API key will be used for this app session only and was not saved.",
        )

    def _test_ai_connection(self, values: dict) -> None:
        api_key = normalize_api_key(values.get("external_ai_api_key", "")) or load_api_key()
        if not api_key:
            message = "Enter an OpenAI API key or store one securely before testing the connection."
            self.statusBar().showMessage(message)
            self.ai_test_finished.emit(False, message)
            return
        timeout = float(values.get("external_ai_timeout_seconds", 20.0))
        self.statusBar().showMessage("Testing OpenAI connection...")

        def worker() -> None:
            try:
                client = OpenAIExpressionClient(self.config.data.get("external_ai_model", "gpt-4.1-mini"))
                client.test_connection(api_key, timeout)
                message = "OpenAI connection test succeeded."
                self.ai_status_changed.emit(message)
                self.ai_test_finished.emit(True, message)
            except Exception as exc:
                message = f"OpenAI connection test failed: {exc}"
                self.ai_status_changed.emit(message)
                self.ai_test_finished.emit(False, message)

        threading.Thread(target=worker, daemon=True).start()

    def _check_daily_summary(self) -> None:
        self.user_profile.load()
        profile = self.user_profile.data
        selected = due_summary_date(profile)
        if selected is None or profile.get("email_delivery_mode") != "smtp":
            return
        summary = summarize_day(read_expression_history(), selected)
        if not summary.analyzed_entries:
            return
        if self._summary_send_running:
            return
        self._summary_send_running = True
        threading.Thread(
            target=self._send_due_summary_worker,
            args=(profile, selected, summary),
            daemon=True,
        ).start()

    def _send_due_summary_worker(self, profile: dict, selected, summary) -> None:
        try:
            send_smtp(profile, summary)
        except Exception as exc:
            self.email_status_changed.emit(f"Daily email summary not sent: {exc}")
            self._summary_send_running = False
            return
        self.user_profile.update({"last_summary_sent_date": selected.isoformat()})
        self.email_status_changed.emit(f"Daily statistics summary sent for {selected.isoformat()}")
        self._summary_send_running = False

    def _create_help_menu(self) -> None:
        help_menu = self.menuBar().addMenu("Help")
        demo_action = QAction("Start Demo Guide", self)
        demo_action.triggered.connect(self.open_demo_guide)
        help_menu.addAction(demo_action)

    def open_demo_guide(self) -> None:
        root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
        candidates = (
            root / "docs" / "START_DEMO_HERE.html",
            root / "docs" / "START_DEMO_HERE.md",
            root / "docs" / "demo_script.md",
        )
        guide = next((path for path in candidates if path.exists()), None)
        if guide is None:
            QMessageBox.warning(self, "Demo Guide", "The local demo guide could not be found.")
            return
        try:
            os.startfile(guide)
        except OSError as exc:
            QMessageBox.warning(self, "Demo Guide", f"Could not open the local demo guide: {exc}")

    def clear_logs(self) -> None:
        answer = QMessageBox.question(
            self,
            "Clear Local Logs",
            "Delete all locally saved expression metadata history?",
        )
        if answer == QMessageBox.Yes:
            self.logger.clear()
            self.statusBar().showMessage("Local expression metadata logs cleared")

    def open_logs(self) -> None:
        folder = self.logger.folder()
        try:
            os.startfile(folder)
        except OSError as exc:
            QMessageBox.warning(self, "Open Logs", f"Could not open logs folder: {exc}")

    def _refresh_logging_status(self) -> None:
        state = "enabled" if self.logger.enabled else "disabled"
        self.logging_label.setText(f"Local metadata logging: {state}")

    def _refresh_profile_status(self) -> None:
        profile = ExpressionProfile()
        exists = (
            profile.exists
            and self.config.data["personalized_profile_enabled"]
            and self.config.data["expression_detection_mode"] in {"personalized", "hybrid", "hybrid_ai"}
        )
        self.mode_label.setText(
            f"Detection mode: {self._detection_mode_text(self.config.data['expression_detection_mode'])}"
        )
        self.profile_label.setText(f"Personalized profile: {'active' if exists else 'inactive'}")
        self._refresh_ai_header()

    def _refresh_ai_header(self) -> None:
        if self.config.data.get("external_ai_enabled") and self.config.data.get("external_ai_consent_accepted"):
            self.privacy_mode_label.setText(
                "LOCAL BY DEFAULT  |  EXTERNAL AI ENABLED BY CONSENT  |  NO IMAGE SAVING"
            )
        else:
            self.privacy_mode_label.setText(
                "LOCAL BY DEFAULT  |  EXTERNAL AI OFF  |  NO IMAGE SAVING"
            )

    @staticmethod
    def _detection_mode_text(mode: str) -> str:
        return {
            "heuristic": "Local only",
            "personalized": "Personalized only",
            "hybrid": "Personalized / Hybrid local",
            "external_ai": "External AI only",
            "hybrid_ai": "Hybrid local + AI",
        }.get(mode, str(mode).replace("_", " ").title())

    def open_calibration(self, add_more: bool = True) -> None:
        was_running = bool(self.worker and self.worker.isRunning())
        if was_running:
            self.stop_camera()
        dialog = CalibrationDialog(self.config.data, self, add_more=add_more)
        dialog.profile_changed.connect(self._profile_trained)
        dialog.exec()
        self._refresh_profile_status()
        if was_running:
            self.start_camera()


    def _profile_trained(self) -> None:
        self.config.update(
            {"expression_detection_mode": "hybrid", "personalized_profile_enabled": True}
        )
        self._refresh_profile_status()

    def delete_profile(self) -> None:
        if QMessageBox.question(
            self, "Delete Personalized Profile",
            "Delete all local personalized expression calibration data?"
        ) == QMessageBox.Yes:
            was_running = bool(self.worker and self.worker.isRunning())
            if was_running:
                self.stop_camera()
            ExpressionProfile().delete()
            self.config.update({"expression_detection_mode": "heuristic"})
            self._refresh_profile_status()
            if was_running:
                self.start_camera()

    def export_profile(self) -> None:
        destination, _ = QFileDialog.getSaveFileName(
            self, "Export Expression Profile", "emotioncam-expression-profile.json", "JSON (*.json)"
        )
        if destination:
            try:
                ExpressionProfile().export_to(Path(destination))
                self.statusBar().showMessage("Personalized expression profile exported locally")
            except (OSError, FileNotFoundError) as exc:
                QMessageBox.warning(self, "Export Profile", str(exc))

    def import_profile(self) -> None:
        source, _ = QFileDialog.getOpenFileName(
            self, "Import Expression Profile", "", "JSON (*.json)"
        )
        if source:
            try:
                was_running = bool(self.worker and self.worker.isRunning())
                if was_running:
                    self.stop_camera()
                ExpressionProfile().import_from(Path(source))
                self.config.update(
                    {"expression_detection_mode": "hybrid", "personalized_profile_enabled": True}
                )
                self._refresh_profile_status()
                if was_running:
                    self.start_camera()
            except (OSError, ValueError) as exc:
                QMessageBox.warning(self, "Import Profile", str(exc))
                if "was_running" in locals() and was_running:
                    self.start_camera()

    def _create_tray(self) -> None:
        self.tray = QSystemTrayIcon(QApplication.windowIcon(), self)
        menu = QMenu(self)
        show_action = QAction("Show EmotionCam", self)
        stop_action = QAction("Stop Camera", self)
        exit_action = QAction("Exit", self)
        show_action.triggered.connect(self.show_from_background)
        stop_action.triggered.connect(self.stop_camera)
        exit_action.triggered.connect(self.exit_app)
        menu.addAction(show_action)
        menu.addAction(stop_action)
        menu.addSeparator()
        menu.addAction(exit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(
            lambda reason: self.show_from_background()
            if reason == QSystemTrayIcon.DoubleClick
            else None
        )

    def run_in_background(self) -> None:
        if not self.worker or not self.worker.isRunning():
            self.start_camera()
        self.background_active = True
        self.config.update({"background_mode_enabled": True})
        ai_active = (
            self.config.data.get("external_ai_enabled")
            and self.config.data.get("external_ai_consent_accepted")
            and self.config.data.get("expression_detection_mode") in {"external_ai", "hybrid_ai"}
        )
        self.background_label.setText(
            "Background mode: active, local-first with optional External AI"
            if ai_active
            else "Background mode: active, processing locally"
        )
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()
            self.tray.showMessage(
                "EmotionCam running in background",
                "Analysis continues with your current privacy and External AI settings.",
            )
            self.hide()
        else:
            self.showMinimized()

    def show_from_background(self) -> None:
        self.background_active = False
        self.config.update({"background_mode_enabled": False})
        self.background_label.setText("Background mode: inactive")
        self.showNormal()
        self.activateWindow()

    def toggle_debug(self) -> None:
        enabled = not self.debug_panel.isVisible()
        self.debug_panel.setVisible(enabled)
        self.config.update({"debug_panel_enabled": enabled})

    def exit_app(self) -> None:
        self._exiting = True
        self.stop_camera()
        self.tray.hide()
        QApplication.quit()

    def _set_camera_buttons(self, running: bool) -> None:
        self.start_button.setEnabled(not running)
        self.stop_button.setEnabled(running)
        self.pause_button.setEnabled(running)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.background_active and not self._exiting:
            event.ignore()
            self.hide()
            return
        self.stop_camera()
        self.tray.hide()
        event.accept()
