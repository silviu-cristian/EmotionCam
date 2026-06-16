"""Settings editor."""

from PySide6.QtCore import QPointF, QTime, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPolygonF
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTimeEdit,
    QLabel,
    QScrollArea,
    QWidget,
    QVBoxLayout,
)

from app.core.ai_privacy import AI_FULL_FRAME_WARNING, AI_PRIVACY_WARNING
from app.core.ai_settings import has_stored_api_key
from app.core.config import DEFAULT_CONFIG
from app.core.expression_profile import ExpressionProfile
from app.core.local_ai_client import DEFAULT_OLLAMA_ENDPOINT, DEFAULT_OLLAMA_MODEL
from app.core.email_summary import store_password
from app.core.user_profile import UserProfile


class _VisibleArrowMixin:
    """Draw high-contrast arrows while retaining native spin-box click handling."""

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        application = QApplication.instance()
        theme = application.property("emotioncamTheme") if application else "dark"
        painter.setBrush(QColor("#233149" if theme == "light" else "#f2f6ff"))
        x = self.width() - 16
        for y, up in ((self.height() * 0.25, True), (self.height() * 0.75, False)):
            points = (
                [QPointF(x - 5, y + 3), QPointF(x + 5, y + 3), QPointF(x, y - 3)]
                if up
                else [QPointF(x - 5, y - 3), QPointF(x + 5, y - 3), QPointF(x, y + 3)]
            )
            painter.drawPolygon(QPolygonF(points))

    def mousePressEvent(self, event) -> None:
        if event.position().x() >= self.width() - 32:
            if event.position().y() < self.height() / 2:
                self.stepUp()
            else:
                self.stepDown()
            event.accept()
            return
        super().mousePressEvent(event)


class VisibleSpinBox(_VisibleArrowMixin, QSpinBox):
    pass


class VisibleDoubleSpinBox(_VisibleArrowMixin, QDoubleSpinBox):
    pass


class SettingsDialog(QDialog):
    clear_logs_requested = Signal()
    open_logs_requested = Signal()
    calibrate_requested = Signal(bool)
    delete_profile_requested = Signal()
    export_profile_requested = Signal()
    import_profile_requested = Signal()
    test_email_requested = Signal(dict)
    test_ai_requested = Signal(dict)

    def __init__(self, settings: dict, parent=None, user_profile: UserProfile | None = None) -> None:
        super().__init__(parent)
        self.user_profile = user_profile or UserProfile()
        self.setWindowTitle("EmotionCam Settings")
        self.setMinimumWidth(540)
        layout = QVBoxLayout(self)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        scroll.setWidget(content)
        layout.addWidget(scroll)

        appearance = QGroupBox("Appearance")
        appearance_form = QFormLayout(appearance)
        self.theme = QComboBox()
        self.theme.addItem("Dark", "dark")
        self.theme.addItem("Light", "light")
        appearance_form.addRow("Theme", self.theme)
        content_layout.addWidget(appearance)

        user_group = QGroupBox("User Profile")
        user_form = QFormLayout(user_group)
        self.user_name = QLineEdit()
        self.user_name.setMaxLength(80)
        self.user_email = QLineEdit()
        self.user_email.setPlaceholderText("name@example.com")
        user_form.addRow("User name (optional)", self.user_name)
        user_form.addRow("Email address", self.user_email)
        content_layout.addWidget(user_group)

        email_group = QGroupBox("Daily Email Summary (optional network feature)")
        email_layout = QVBoxLayout(email_group)
        email_notice = QLabel(
            "Daily email summaries require sending summary text by email. No images or webcam "
            "frames are sent. Only local statistics text is used."
        )
        email_notice.setWordWrap(True)
        email_notice.setObjectName("subtitle")
        email_layout.addWidget(email_notice)
        self.daily_email_enabled = QCheckBox("Enable daily email summary")
        email_layout.addWidget(self.daily_email_enabled)
        email_form = QFormLayout()
        self.email_mode = QComboBox()
        self.email_mode.addItem("Default mail client draft (manual send)", "mail_client")
        self.email_mode.addItem("SMTP automatic sending", "smtp")
        self.summary_time = QTimeEdit()
        self.summary_time.setDisplayFormat("HH:mm")
        self.smtp_server = QLineEdit()
        self.smtp_port = VisibleSpinBox()
        self.smtp_port.setRange(1, 65535)
        self._prepare_integer(self.smtp_port)
        self.smtp_username = QLineEdit()
        self.smtp_password = QLineEdit()
        self.smtp_password.setEchoMode(QLineEdit.Password)
        self.smtp_password.setPlaceholderText("Stored securely only when keyring is available")
        self.smtp_tls = QCheckBox("Use TLS")
        self.store_password = QCheckBox("Store SMTP password securely with Windows credential storage")
        self.store_password.setChecked(True)
        email_form.addRow("Delivery method", self.email_mode)
        email_form.addRow("Send time", self.summary_time)
        email_form.addRow("SMTP server", self.smtp_server)
        email_form.addRow("SMTP port", self.smtp_port)
        email_form.addRow("SMTP username", self.smtp_username)
        email_form.addRow("SMTP password", self.smtp_password)
        email_form.addRow("", self.smtp_tls)
        email_form.addRow("", self.store_password)
        email_layout.addLayout(email_form)
        test_email = QPushButton("Send Test Email / Open Test Draft")
        test_email.clicked.connect(lambda: self.test_email_requested.emit(self.email_values()))
        email_layout.addWidget(test_email)
        content_layout.addWidget(email_group)

        detection = QGroupBox("Camera and detection")
        form = QFormLayout(detection)
        self.camera_index = VisibleSpinBox()
        self.camera_index.setRange(0, 9)
        self.camera_index.setSingleStep(1)
        self.camera_index.setButtonSymbols(QSpinBox.UpDownArrows)
        self.camera_index.setKeyboardTracking(True)
        self.camera_index.setFocusPolicy(Qt.StrongFocus)
        self._prepare_integer(self.camera_index)
        self.detection_confidence = self._decimal(0.1, 1.0, 0.05)
        self.expression_confidence = self._decimal(0.1, 1.0, 0.05)
        self.smoothing_window = self._decimal(0.2, 10.0, 0.1)
        self.stable_duration = self._decimal(0.0, 10.0, 0.1)
        self.message_cooldown = self._decimal(0.0, 120.0, 1.0)
        self.face_grace = self._decimal(0.0, 5.0, 0.1)
        self.negative_minimum = self._decimal(0.4, 1.0, 0.05)
        self.positive_minimum = self._decimal(0.3, 1.0, 0.05)
        form.addRow("Camera index", self.camera_index)
        form.addRow("Detection confidence threshold", self.detection_confidence)
        form.addRow("Expression confidence threshold", self.expression_confidence)
        form.addRow("Smoothing window duration (seconds)", self.smoothing_window)
        form.addRow("Stable expression duration (seconds)", self.stable_duration)
        form.addRow("Message cooldown duration (seconds)", self.message_cooldown)
        form.addRow("Keep tracking briefly when face is missed (seconds)", self.face_grace)
        form.addRow("Minimum confidence for negative estimates", self.negative_minimum)
        form.addRow("Minimum confidence for positive estimates", self.positive_minimum)
        content_layout.addWidget(detection)

        ai_group = QGroupBox("Expression Detection Mode and AI Analysis")
        ai_layout = QVBoxLayout(ai_group)
        ai_notice = QLabel(AI_PRIVACY_WARNING)
        ai_notice.setWordWrap(True)
        ai_notice.setObjectName("subtitle")
        ai_layout.addWidget(ai_notice)
        ai_form = QFormLayout()
        self.detection_mode = QComboBox()
        self.detection_mode.addItem("Local only", "heuristic")
        self.detection_mode.addItem("Personalized only", "personalized")
        self.detection_mode.addItem("Personalized / Hybrid local", "hybrid")
        self.detection_mode.addItem("AI only", "external_ai")
        self.detection_mode.addItem("Hybrid local + AI", "hybrid_ai")
        self.external_ai_enabled = QCheckBox("Enable AI Analysis")
        self.external_ai_consent = QCheckBox()
        self.ai_provider = QComboBox()
        self.ai_provider.addItem("OpenAI (cloud / uses API credits)", "openai")
        self.ai_provider.addItem("Local Ollama (runs on this computer)", "ollama")
        self.openai_model = QLineEdit()
        self.openai_model.setPlaceholderText("gpt-4.1-mini")
        self.ai_key = QLineEdit()
        self.ai_key.setEchoMode(QLineEdit.Password)
        self.ai_key.setPlaceholderText(
            "Stored securely; enter a new key to replace"
            if has_stored_api_key()
            else "Enter OpenAI API key"
        )
        self.ai_store_key = QCheckBox("Store API key securely with Windows credential storage")
        self.ai_store_key.setChecked(True)
        self.ollama_endpoint = QLineEdit()
        self.ollama_endpoint.setPlaceholderText(DEFAULT_OLLAMA_ENDPOINT)
        self.ollama_model = QLineEdit()
        self.ollama_model.setPlaceholderText(DEFAULT_OLLAMA_MODEL)
        self.ai_cropped = QCheckBox("Send cropped face only (recommended)")
        self.ai_interval = self._decimal(5.0, 3600.0, 1.0)
        self.ai_timeout = self._decimal(5.0, 60.0, 1.0)
        self.ai_debug = QCheckBox("Show AI debug info")
        ai_form.addRow("Detection mode", self.detection_mode)
        ai_form.addRow("", self.external_ai_enabled)
        ai_form.addRow("", self.external_ai_consent)
        ai_form.addRow("API provider", self.ai_provider)
        ai_form.addRow("OpenAI model", self.openai_model)
        ai_form.addRow("OpenAI API key", self.ai_key)
        ai_form.addRow("", self.ai_store_key)
        ai_form.addRow("Local Ollama endpoint", self.ollama_endpoint)
        ai_form.addRow("Local Ollama vision model", self.ollama_model)
        ai_form.addRow("", self.ai_cropped)
        ai_form.addRow("AI request interval (seconds)", self.ai_interval)
        ai_form.addRow("AI timeout (seconds)", self.ai_timeout)
        ai_form.addRow("", self.ai_debug)
        ai_layout.addLayout(ai_form)
        full_frame_warning = QLabel(AI_FULL_FRAME_WARNING)
        full_frame_warning.setWordWrap(True)
        full_frame_warning.setObjectName("subtitle")
        ai_layout.addWidget(full_frame_warning)
        self.ai_provider_help = QLabel()
        self.ai_provider_help.setWordWrap(True)
        self.ai_provider_help.setObjectName("subtitle")
        ai_layout.addWidget(self.ai_provider_help)
        self.test_ai_button = QPushButton("Test Connection")
        self.test_ai_button.clicked.connect(self._request_ai_test)
        ai_layout.addWidget(self.test_ai_button)
        self.ai_test_status = QLabel("Connection not tested yet.")
        self.ai_test_status.setWordWrap(True)
        self.ai_test_status.setObjectName("subtitle")
        ai_layout.addWidget(self.ai_test_status)
        content_layout.addWidget(ai_group)
        self.external_ai_enabled.toggled.connect(self._sync_external_ai_mode)
        self.detection_mode.currentIndexChanged.connect(self._sync_external_ai_checkbox)
        self.ai_provider.currentIndexChanged.connect(self._sync_ai_provider_fields)

        personalized = QGroupBox("Personalized expression calibration")
        personalized_layout = QVBoxLayout(personalized)
        mode_form = QFormLayout()
        self.profile_status = QLabel()
        mode_form.addRow("Personalized profile status", self.profile_status)
        self.samples_per_expression = VisibleSpinBox()
        self.samples_per_expression.setRange(15, 120)
        self.samples_per_expression.setSingleStep(5)
        self.samples_per_expression.setButtonSymbols(QSpinBox.UpDownArrows)
        self._prepare_integer(self.samples_per_expression)
        self.capture_seconds = self._decimal(2.0, 10.0, 0.5)
        self.prepare_seconds = self._decimal(0.5, 5.0, 0.5)
        self.minimum_samples = VisibleSpinBox()
        self.minimum_samples.setRange(5, 60)
        self.minimum_samples.setButtonSymbols(QSpinBox.UpDownArrows)
        self._prepare_integer(self.minimum_samples)
        mode_form.addRow("Target samples per expression", self.samples_per_expression)
        mode_form.addRow("Capture duration per expression (seconds)", self.capture_seconds)
        mode_form.addRow("Preparation countdown (seconds)", self.prepare_seconds)
        mode_form.addRow("Minimum good samples required", self.minimum_samples)
        personalized_layout.addLayout(mode_form)
        self.profile_enabled = QCheckBox("Use personalized expression profile when available")
        self.store_raw_images = QCheckBox("Store raw calibration images for debugging")
        self.store_raw_images.setToolTip("Off by default. Enabling saves calibration frames locally.")
        personalized_layout.addWidget(self.profile_enabled)
        personalized_layout.addWidget(self.store_raw_images)
        profile_actions = QHBoxLayout()
        profile_file_actions = QHBoxLayout()
        train = QPushButton("Train / Calibrate Expressions")
        retrain = QPushButton("Retrain Profile")
        add_samples = QPushButton("Add More Samples")
        delete = QPushButton("Delete Profile")
        export = QPushButton("Export Profile")
        import_button = QPushButton("Import Profile")
        train.clicked.connect(lambda: self.calibrate_requested.emit(False))
        retrain.clicked.connect(lambda: self.calibrate_requested.emit(False))
        add_samples.clicked.connect(lambda: self.calibrate_requested.emit(True))
        delete.clicked.connect(self.delete_profile_requested)
        export.clicked.connect(self.export_profile_requested)
        import_button.clicked.connect(self.import_profile_requested)
        for button in (train, retrain, add_samples):
            profile_actions.addWidget(button)
        for button in (delete, export, import_button):
            profile_file_actions.addWidget(button)
        personalized_layout.addLayout(profile_actions)
        personalized_layout.addLayout(profile_file_actions)
        content_layout.addWidget(personalized)

        display = QGroupBox("Display, messages, and local history")
        display_layout = QVBoxLayout(display)
        self.show_rectangle = QCheckBox("Show face rectangle")
        self.show_confidence = QCheckBox("Show confidence values")
        self.messages_enabled = QCheckBox("Enable interaction messages")
        self.logging_enabled = QCheckBox("Enable local expression metadata logging")
        self.background_popups = QCheckBox("Show helpful notifications while running in background")
        self.debug_panel = QCheckBox("Show expression debug panel")
        for widget in (
            self.show_rectangle,
            self.show_confidence,
            self.messages_enabled,
            self.logging_enabled,
            self.background_popups,
            self.debug_panel,
        ):
            display_layout.addWidget(widget)
        popup_form = QFormLayout()
        self.negative_popup_cooldown = self._decimal(0.0, 3600.0, 30.0)
        self.recovery_popup_cooldown = self._decimal(0.0, 3600.0, 30.0)
        popup_form.addRow("Serious-expression notification cooldown (seconds)", self.negative_popup_cooldown)
        popup_form.addRow("Positive-shift notification cooldown (seconds)", self.recovery_popup_cooldown)
        display_layout.addLayout(popup_form)
        content_layout.addWidget(display)

        actions = QHBoxLayout()
        clear_logs = QPushButton("Clear Logs")
        open_logs = QPushButton("Open Logs Folder")
        reset = QPushButton("Reset Settings to Default")
        clear_logs.clicked.connect(self.clear_logs_requested)
        open_logs.clicked.connect(self.open_logs_requested)
        reset.clicked.connect(self._reset_defaults)
        actions.addWidget(clear_logs)
        actions.addWidget(open_logs)
        actions.addWidget(reset)
        content_layout.addLayout(actions)
        content_layout.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self._load(settings)

    @staticmethod
    def _decimal(low: float, high: float, step: float) -> QDoubleSpinBox:
        box = VisibleDoubleSpinBox()
        box.setRange(low, high)
        box.setSingleStep(step)
        box.setDecimals(2)
        box.setButtonSymbols(QDoubleSpinBox.UpDownArrows)
        box.setKeyboardTracking(True)
        box.setFocusPolicy(Qt.StrongFocus)
        box.setMinimumWidth(150)
        box.setMaximumWidth(190)
        return box

    @staticmethod
    def _prepare_integer(box: QSpinBox) -> None:
        box.setButtonSymbols(QSpinBox.UpDownArrows)
        box.setKeyboardTracking(True)
        box.setFocusPolicy(Qt.StrongFocus)
        box.setMinimumWidth(150)
        box.setMaximumWidth(190)

    def _set_detection_mode(self, mode: str) -> None:
        index = self.detection_mode.findData(mode)
        if index < 0:
            return
        was_blocked = self.detection_mode.blockSignals(True)
        self.detection_mode.setCurrentIndex(index)
        self.detection_mode.blockSignals(was_blocked)

    def _set_external_ai_enabled(self, enabled: bool) -> None:
        was_blocked = self.external_ai_enabled.blockSignals(True)
        self.external_ai_enabled.setChecked(enabled)
        self.external_ai_enabled.blockSignals(was_blocked)

    def _sync_external_ai_mode(self, enabled: bool) -> None:
        mode = self.detection_mode.currentData()
        if enabled and mode not in {"external_ai", "hybrid_ai"}:
            self._set_detection_mode("hybrid_ai")
        elif not enabled and mode == "hybrid_ai":
            self._set_detection_mode("hybrid")
        elif not enabled and mode == "external_ai":
            self._set_detection_mode("heuristic")

    def _sync_external_ai_checkbox(self) -> None:
        mode = self.detection_mode.currentData()
        if mode in {"external_ai", "hybrid_ai"}:
            self._set_external_ai_enabled(True)
        elif self.external_ai_enabled.isChecked():
            self._set_external_ai_enabled(False)

    def _sync_ai_provider_fields(self) -> None:
        provider = self.ai_provider.currentData()
        is_ollama = provider == "ollama"
        self.external_ai_consent.setText(
            "I understand selected cropped face images or frames may be sent to OpenAI."
            if not is_ollama
            else "I understand selected cropped face images or frames may be sent to local Ollama on this computer."
        )
        self.openai_model.setEnabled(not is_ollama)
        self.ai_key.setEnabled(not is_ollama)
        self.ai_store_key.setEnabled(not is_ollama)
        self.ollama_endpoint.setEnabled(is_ollama)
        self.ollama_model.setEnabled(is_ollama)
        if is_ollama:
            self.ai_provider_help.setText(
                "Local Ollama mode uses a model running on this PC. Install Ollama, then run "
                f"`ollama pull {self.ollama_model.text() or DEFAULT_OLLAMA_MODEL}` in PowerShell. "
                "EmotionCam only allows localhost/127.0.0.1 endpoints for this local mode."
            )
            if self.ai_test_status.text() == "Connection not tested yet.":
                self.ai_test_status.setText("Local Ollama connection not tested yet.")
        else:
            self.ai_provider_help.setText(
                "OpenAI mode may send selected cropped face images or frames to OpenAI. It needs "
                "a valid API key, account quota, and internet access."
            )
            if self.ai_test_status.text() == "Local Ollama connection not tested yet.":
                self.ai_test_status.setText("Connection not tested yet.")

    def _request_ai_test(self) -> None:
        self.set_ai_test_running()
        self.test_ai_requested.emit(self.ai_values())

    def set_ai_test_running(self) -> None:
        provider = self.ai_provider.currentData()
        provider_name = "Local Ollama" if provider == "ollama" else "OpenAI"
        self.test_ai_button.setEnabled(False)
        self.test_ai_button.setText("Testing...")
        self.ai_test_status.setText(f"Testing {provider_name} connection. This can take a few seconds.")

    def set_ai_test_result(self, success: bool, message: str, show_popup: bool = True) -> None:
        clean_message = " ".join(str(message or "").split())
        if len(clean_message) > 600:
            clean_message = clean_message[:597] + "..."
        prefix = "Connection succeeded" if success else "Connection failed"
        text = f"{prefix}: {clean_message}"
        self.ai_test_status.setText(text)
        self.test_ai_button.setEnabled(True)
        self.test_ai_button.setText("Test Connection")
        if not show_popup:
            return
        if success:
            QMessageBox.information(self, "External AI Connection", text)
        else:
            QMessageBox.warning(self, "External AI Connection", text)

    def _load(self, data: dict) -> None:
        theme_index = self.theme.findData(data.get("theme", "dark"))
        self.theme.setCurrentIndex(max(0, theme_index))
        self.camera_index.setValue(data["camera_index"])
        self.detection_confidence.setValue(data["detection_confidence_threshold"])
        self.expression_confidence.setValue(data["expression_confidence_threshold"])
        self.smoothing_window.setValue(data["smoothing_window_seconds"])
        self.stable_duration.setValue(data["stable_expression_seconds"])
        self.message_cooldown.setValue(data["message_cooldown_seconds"])
        self.face_grace.setValue(data["face_missing_grace_seconds"])
        self.negative_minimum.setValue(data["negative_expression_min_confidence"])
        self.positive_minimum.setValue(data["positive_expression_min_confidence"])
        self.show_rectangle.setChecked(data["show_face_rectangle"])
        self.show_confidence.setChecked(data["show_confidence_values"])
        self.messages_enabled.setChecked(data["interaction_messages_enabled"])
        self.logging_enabled.setChecked(data["local_logging_enabled"])
        self.background_popups.setChecked(data["background_popups_enabled"])
        self.debug_panel.setChecked(data["debug_panel_enabled"])
        self.negative_popup_cooldown.setValue(data["negative_popup_cooldown_seconds"])
        self.recovery_popup_cooldown.setValue(data["positive_recovery_popup_cooldown_seconds"])
        index = self.detection_mode.findData(data["expression_detection_mode"])
        self.detection_mode.setCurrentIndex(max(0, index))
        self.external_ai_enabled.setChecked(data["external_ai_enabled"])
        self.external_ai_consent.setChecked(data["external_ai_consent_accepted"])
        provider_index = self.ai_provider.findData(data["external_ai_provider"])
        self.ai_provider.setCurrentIndex(max(0, provider_index))
        self.openai_model.setText(data.get("external_ai_model", "gpt-4.1-mini"))
        self.ollama_endpoint.setText(data.get("local_ai_ollama_endpoint", DEFAULT_OLLAMA_ENDPOINT))
        self.ollama_model.setText(data.get("local_ai_ollama_model", DEFAULT_OLLAMA_MODEL))
        self.ai_cropped.setChecked(data["external_ai_send_cropped_face_only"])
        self.ai_interval.setValue(data["external_ai_request_interval_seconds"])
        self.ai_timeout.setValue(data["external_ai_timeout_seconds"])
        self.ai_debug.setChecked(data["external_ai_show_debug_info"])
        profile = ExpressionProfile()
        self.profile_status.setText(
            f"Available locally ({len(profile.samples)} trained expressions)"
            if profile.exists else "No local profile"
        )
        self.profile_enabled.setChecked(data["personalized_profile_enabled"])
        self.store_raw_images.setChecked(data["store_raw_calibration_images"])
        self.samples_per_expression.setValue(data["calibration_samples_per_expression"])
        self.capture_seconds.setValue(data["calibration_capture_seconds"])
        self.prepare_seconds.setValue(data["calibration_prepare_seconds"])
        self.minimum_samples.setValue(data["minimum_samples_per_expression"])
        profile = self.user_profile.data
        self.user_name.setText(profile["name"])
        self.user_email.setText(profile["email"])
        self.daily_email_enabled.setChecked(profile["daily_email_summary_enabled"])
        mode_index = self.email_mode.findData(profile["email_delivery_mode"])
        self.email_mode.setCurrentIndex(max(0, mode_index))
        self.summary_time.setTime(QTime.fromString(profile["summary_send_time"], "HH:mm"))
        self.smtp_server.setText(profile["smtp_server"])
        self.smtp_port.setValue(profile["smtp_port"])
        self.smtp_username.setText(profile["smtp_username"])
        self.smtp_tls.setChecked(profile["smtp_use_tls"])
        self._sync_ai_provider_fields()

    def _reset_defaults(self) -> None:
        self._load(DEFAULT_CONFIG)

    def _accept(self) -> None:
        if self.external_ai_enabled.isChecked() and not self.external_ai_consent.isChecked():
            QMessageBox.warning(
                self,
                "External AI Consent Required",
                "External AI analysis cannot be enabled until you accept the consent checkbox.",
            )
            return
        try:
            candidate = UserProfile(self.user_profile.path)
            candidate.update(self.profile_values())
        except ValueError as exc:
            QMessageBox.warning(self, "User Profile", str(exc))
            return
        if self.store_password.isChecked() and self.smtp_password.text():
            if not store_password(self.smtp_username.text().strip(), self.smtp_password.text()):
                QMessageBox.information(
                    self,
                    "Secure Password Storage",
                    "Secure credential storage is unavailable. The SMTP password was not saved "
                    "and must be re-entered when needed.",
                )
        self.accept()

    def profile_values(self) -> dict:
        return {
            "name": self.user_name.text(),
            "email": self.user_email.text(),
            "daily_email_summary_enabled": self.daily_email_enabled.isChecked(),
            "summary_send_time": self.summary_time.time().toString("HH:mm"),
            "email_delivery_mode": self.email_mode.currentData(),
            "smtp_server": self.smtp_server.text(),
            "smtp_port": self.smtp_port.value(),
            "smtp_username": self.smtp_username.text(),
            "smtp_use_tls": self.smtp_tls.isChecked(),
        }

    def email_values(self) -> dict:
        return {
            **self.profile_values(),
            "smtp_password": self.smtp_password.text(),
            "store_password_securely": self.store_password.isChecked(),
        }

    def ai_values(self) -> dict:
        return {
            "external_ai_enabled": self.external_ai_enabled.isChecked(),
            "external_ai_consent_accepted": self.external_ai_consent.isChecked(),
            "external_ai_provider": self.ai_provider.currentData(),
            "external_ai_model": self.openai_model.text(),
            "external_ai_api_key": self.ai_key.text(),
            "external_ai_store_key_securely": self.ai_store_key.isChecked(),
            "local_ai_ollama_endpoint": self.ollama_endpoint.text(),
            "local_ai_ollama_model": self.ollama_model.text(),
            "external_ai_send_cropped_face_only": self.ai_cropped.isChecked(),
            "external_ai_request_interval_seconds": self.ai_interval.value(),
            "external_ai_timeout_seconds": self.ai_timeout.value(),
            "external_ai_show_debug_info": self.ai_debug.isChecked(),
            "expression_detection_mode": self.detection_mode.currentData(),
        }

    def values(self) -> dict:
        return {
            "theme": self.theme.currentData(),
            "camera_index": self.camera_index.value(),
            "detection_confidence_threshold": self.detection_confidence.value(),
            "expression_confidence_threshold": self.expression_confidence.value(),
            "smoothing_window_seconds": self.smoothing_window.value(),
            "stable_expression_seconds": self.stable_duration.value(),
            "message_cooldown_seconds": self.message_cooldown.value(),
            "face_missing_grace_seconds": self.face_grace.value(),
            "negative_expression_min_confidence": self.negative_minimum.value(),
            "positive_expression_min_confidence": self.positive_minimum.value(),
            "show_face_rectangle": self.show_rectangle.isChecked(),
            "show_confidence_values": self.show_confidence.isChecked(),
            "interaction_messages_enabled": self.messages_enabled.isChecked(),
            "local_logging_enabled": self.logging_enabled.isChecked(),
            "background_popups_enabled": self.background_popups.isChecked(),
            "debug_panel_enabled": self.debug_panel.isChecked(),
            "negative_popup_cooldown_seconds": self.negative_popup_cooldown.value(),
            "positive_recovery_popup_cooldown_seconds": self.recovery_popup_cooldown.value(),
            "expression_detection_mode": self.detection_mode.currentData(),
            "external_ai_backend_enabled": self.external_ai_enabled.isChecked(),
            "external_ai_enabled": self.external_ai_enabled.isChecked(),
            "external_ai_consent_accepted": self.external_ai_consent.isChecked(),
            "external_ai_provider": self.ai_provider.currentData(),
            "external_ai_model": self.openai_model.text() or DEFAULT_CONFIG["external_ai_model"],
            "local_ai_ollama_endpoint": self.ollama_endpoint.text() or DEFAULT_CONFIG["local_ai_ollama_endpoint"],
            "local_ai_ollama_model": self.ollama_model.text() or DEFAULT_CONFIG["local_ai_ollama_model"],
            "external_ai_request_interval_seconds": self.ai_interval.value(),
            "external_ai_timeout_seconds": self.ai_timeout.value(),
            "external_ai_send_cropped_face_only": self.ai_cropped.isChecked(),
            "external_ai_show_debug_info": self.ai_debug.isChecked(),
            "personalized_profile_enabled": self.profile_enabled.isChecked(),
            "store_raw_calibration_images": self.store_raw_images.isChecked(),
            "calibration_samples_per_expression": self.samples_per_expression.value(),
            "calibration_capture_seconds": self.capture_seconds.value(),
            "calibration_prepare_seconds": self.prepare_seconds.value(),
            "minimum_samples_per_expression": self.minimum_samples.value(),
        }
