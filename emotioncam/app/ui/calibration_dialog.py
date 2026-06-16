"""Step-based local personalized expression calibration."""

from __future__ import annotations

import time

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)

from app.core.expression_backends import HeuristicExpressionClassifier
from app.core.expression_features import calibration_sample_acceptable, extract_expression_features
from app.core.expression_profile import ExpressionProfile
from app.core.face_detector import FaceDetector
from app.core.paths import profile_dir
from app.core.smoothing import ExpressionSmoother
from app.core.user_profile import UserProfile
from app.ui.expression_example import expression_example_pixmap, expressions_match


CALIBRATION_PROMPTS = [
    ("neutral", "Prepare: look neutral"),
    ("smile_small", "Prepare: smile slightly"),
    ("smile_big", "Prepare: smile a lot"),
    ("happy", "Prepare: show a happy-looking visible expression"),
    ("laughing", "Prepare: laugh"),
    ("amused", "Prepare: look amused"),
    ("surprised", "Prepare: look surprised"),
    ("sad", "Prepare: look sad"),
    ("angry", "Prepare: show an angry-looking expression"),
    ("fearful", "Prepare: show a fearful-looking expression"),
    ("disgusted", "Prepare: show a disgusted-looking expression"),
    ("tired", "Prepare: look tired"),
    ("bored", "Prepare: look bored"),
    ("frustrated", "Prepare: look frustrated"),
    ("concerned", "Prepare: look concerned"),
    ("focused", "Prepare: look focused"),
    ("confused", "Prepare: look confused"),
    ("skeptical", "Prepare: look skeptical"),
    ("thinking", "Prepare: show a thinking expression"),
    ("relaxed", "Prepare: look relaxed"),
]


class CalibrationDialog(QDialog):
    profile_changed = Signal()

    def __init__(self, settings: dict, parent=None, add_more: bool = False) -> None:
        super().__init__(parent)
        self.settings = settings
        self.add_more = add_more
        self.profile = ExpressionProfile()
        self.user_profile = UserProfile()
        if not add_more:
            self.profile.samples = {}
        self.index = 0
        self.state = "ready"
        self.state_started = 0.0
        self.current_samples: list[list[float]] = []
        self.rejected = 0
        self.last_rejection = ""
        self.batch_saved = False
        self.pending_debug_images = []
        self.saved_batch: list[list[float]] = []
        self.saved_label = ""
        self.saved_debug_images = []
        self.capture = None
        self.detector = None
        self.classifier = None
        self.smoother = ExpressionSmoother(window_seconds=1.0, stable_seconds=0.25)
        self.setWindowTitle("Personalized Expression Calibration")
        self.resize(1180, 800)

        layout = QVBoxLayout(self)
        title = QLabel("Personalized expression calibration")
        title.setObjectName("title")
        privacy = QLabel(
            "Calibration stores local expression feature data and labels. EmotionCam does not "
            "save camera images unless debug image storage is explicitly enabled."
        )
        privacy.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(privacy)

        user_row = QHBoxLayout()
        user_row.addWidget(QLabel("User name"))
        self.user_name = QLineEdit(self.user_profile.data["name"])
        self.user_name.setMaxLength(80)
        user_row.addWidget(self.user_name)
        user_row.addWidget(QLabel("Email address"))
        self.user_email = QLineEdit(self.user_profile.data["email"])
        self.user_email.setPlaceholderText("Optional; used only for enabled email summaries")
        user_row.addWidget(self.user_email)
        layout.addLayout(user_row)

        target_row = QHBoxLayout()
        target_row.addWidget(QLabel("Target expression"))
        self.target_selector = QComboBox()
        for label, _ in CALIBRATION_PROMPTS:
            self.target_selector.addItem(label.replace("_", " ").title(), label)
        self.target_selector.currentIndexChanged.connect(self._target_changed)
        target_row.addWidget(self.target_selector, 1)
        self.step_label = QLabel()
        target_row.addWidget(self.step_label)
        layout.addLayout(target_row)

        self.prompt = QLabel()
        self.prompt.setObjectName("metric")
        layout.addWidget(self.prompt)

        visual_row = QHBoxLayout()
        example_card = QFrame()
        example_card.setObjectName("card")
        example_layout = QVBoxLayout(example_card)
        example_layout.addWidget(QLabel("Example expression graphic"))
        self.example = QLabel()
        self.example.setAlignment(Qt.AlignCenter)
        self.example.setMinimumSize(240, 240)
        example_layout.addWidget(self.example)
        self.live_detected = QLabel("Live detected expression: waiting")
        self.live_detected.setWordWrap(True)
        self.match_indicator = QLabel("Helper match: waiting")
        self.match_indicator.setObjectName("matchIndicator")
        self.match_indicator.setAlignment(Qt.AlignCenter)
        self.match_indicator.setMinimumHeight(42)
        example_layout.addWidget(self.live_detected)
        example_layout.addWidget(self.match_indicator)
        visual_row.addWidget(example_card, 1)

        self.preview = QLabel("Opening local webcam...")
        self.preview.setObjectName("camera")
        self.preview.setAlignment(Qt.AlignCenter)
        self.preview.setMinimumSize(680, 460)
        visual_row.addWidget(self.preview, 3)
        layout.addLayout(visual_row, 1)

        self.status = QLabel()
        self.status.setWordWrap(True)
        self.quality = QLabel("Quality summary: waiting")
        self.counts = QLabel()
        self.progress = QProgressBar()
        layout.addWidget(self.status)
        layout.addWidget(self.quality)
        layout.addWidget(self.counts)
        layout.addWidget(self.progress)

        buttons = QHBoxLayout()
        self.previous_button = QPushButton("Previous")
        self.start_button = QPushButton("Start Capture")
        self.start_button.setObjectName("primary")
        self.retake_button = QPushButton("Re-capture")
        self.next_button = QPushButton("Next")
        self.finish_button = QPushButton("Finish")
        self.previous_button.clicked.connect(self.previous_expression)
        self.start_button.clicked.connect(self.start_capture)
        self.retake_button.clicked.connect(self.retake)
        self.next_button.clicked.connect(self.next_expression)
        self.finish_button.clicked.connect(self.finish)
        for button in (
            self.previous_button, self.start_button, self.retake_button,
            self.next_button, self.finish_button
        ):
            buttons.addWidget(button)
        layout.addLayout(buttons)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self._open_camera()

    @property
    def selected_label(self) -> str:
        return CALIBRATION_PROMPTS[self.index][0]

    def _open_camera(self) -> None:
        import cv2

        self.cv2 = cv2
        self.capture = cv2.VideoCapture(int(self.settings["camera_index"]), cv2.CAP_DSHOW)
        if not self.capture.isOpened():
            QMessageBox.warning(self, "Calibration", "Could not open the webcam for calibration.")
            self.reject()
            return
        self.detector = FaceDetector(
            self.settings["detection_confidence_threshold"],
            self.settings["face_missing_grace_seconds"],
        )
        self.classifier = HeuristicExpressionClassifier(
            self.settings["expression_confidence_threshold"],
            self.settings["negative_expression_min_confidence"],
            self.settings["positive_expression_min_confidence"],
        )
        self._show_ready_state()
        self.timer.start(50)

    def _show_ready_state(self) -> None:
        self.state = "ready"
        self.current_samples = []
        self.rejected = 0
        self.last_rejection = ""
        self.batch_saved = False
        self.smoother.reset()
        self._discard_pending_debug_images()
        self.progress.setRange(0, self.settings["calibration_samples_per_expression"])
        self.progress.setValue(0)
        self.prompt.setText(CALIBRATION_PROMPTS[self.index][1])
        self.example.setPixmap(expression_example_pixmap(self.selected_label))
        self.step_label.setText(f"Step {self.index + 1} of {len(CALIBRATION_PROMPTS)}")
        self.status.setText("Prepare manually, then click Start Capture.")
        self.quality.setText("Quality summary: waiting for a clear face")
        self._refresh_counts()
        self._refresh_buttons()

    def start_capture(self) -> None:
        if self.state != "ready":
            return
        self.current_samples = []
        self.rejected = 0
        self.last_rejection = ""
        self.progress.setValue(0)
        self.state = "capturing"
        self.state_started = time.monotonic()
        self.status.setText(f"Capturing local feature samples for: {self.selected_label}")
        self._refresh_buttons()

    def _tick(self) -> None:
        ok, frame = self.capture.read()
        if not ok:
            self.status.setText("Camera frame unavailable. Waiting...")
            return
        now = time.monotonic()
        detection = self.detector.detect(frame, now)
        self._update_live_helper(frame, detection, now)
        if self.state == "capturing":
            self._consider_sample(frame, detection)
            remaining = max(0.0, self.settings["calibration_capture_seconds"] - (now - self.state_started))
            self.status.setText(f"Capturing {self.selected_label}: {remaining:.1f}s remaining")
            if (
                len(self.current_samples) >= self.settings["calibration_samples_per_expression"]
                or remaining <= 0
            ):
                self._complete_capture()
        self._show_frame(frame, detection)

    def _update_live_helper(self, frame, detection, now: float) -> None:
        if detection and self.classifier:
            raw = self.classifier.classify(frame, detection.box, detection)
            smooth = self.smoother.add(raw.label, raw.confidence, True, now)
            detected = smooth.label
            confidence = smooth.confidence
        else:
            smooth = self.smoother.add("no_face", 0.0, False, now)
            detected, confidence = smooth.label, smooth.confidence
        self.live_detected.setText(
            f"Live detected expression: {detected.replace('_', ' ')} ({confidence:.0%})"
        )
        if expressions_match(self.selected_label, detected):
            self.match_indicator.setText("✓ Helper match")
            self.match_indicator.setStyleSheet(
                "background:#dff7e8;color:#17633a;border:1px solid #54a878;border-radius:8px;font-weight:700;"
            )
        else:
            self.match_indicator.setText("○ Not matched yet - capture is still allowed")
            self.match_indicator.setStyleSheet(
                (
                    "background:#edf1f6;color:#536176;border:1px solid #bdc7d5;border-radius:8px;"
                    if self.settings.get("theme") == "light"
                    else "background:#252b37;color:#aeb8c8;border:1px solid #465168;border-radius:8px;"
                )
            )

    def _complete_capture(self) -> None:
        self.state = "review"
        if len(self.current_samples) >= self.settings["minimum_samples_per_expression"]:
            self._save_current_batch()
            self.status.setText(
                f"Capture saved locally for {self.selected_label}. Review quality or re-capture."
            )
        else:
            self.status.setText(
                f"Capture completed with too few valid samples for {self.selected_label}. "
                "Adjust lighting/position and re-capture."
            )
        self._refresh_buttons()

    def _consider_sample(self, frame, detection) -> None:
        gray = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2GRAY)
        blur = float(self.cv2.Laplacian(gray, self.cv2.CV_64F).var())
        brightness = float(gray.mean())
        sample = extract_expression_features(detection) if detection else None
        accepted, reason = calibration_sample_acceptable(detection, sample, blur, brightness)
        if not accepted:
            self.rejected += 1
            self.last_rejection = reason
            self.quality.setText(f"Quality summary: rejected - {reason.replace('_', ' ')}")
            self._refresh_counts()
            return
        self.current_samples.append(sample.values)
        self.progress.setValue(len(self.current_samples))
        self.quality.setText(f"Quality summary: good landmarks ({sample.quality:.0%})")
        self._refresh_counts()
        if self.settings["store_raw_calibration_images"]:
            folder = profile_dir() / "debug_images"
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / f"{self.selected_label}_{time.time_ns()}.jpg"
            self.cv2.imwrite(str(path), frame)
            self.pending_debug_images.append(path)

    def _save_current_batch(self) -> None:
        if self.add_more:
            self.profile.add_samples(self.selected_label, self.current_samples)
        else:
            self.profile.samples[self.selected_label] = list(self.current_samples)
            self.profile.save()
        self.batch_saved = True
        self.saved_batch = list(self.current_samples)
        self.saved_label = self.selected_label
        self.saved_debug_images = list(self.pending_debug_images)
        self.pending_debug_images = []
        self.profile_changed.emit()

    def _refresh_counts(self) -> None:
        stored = len(self.profile.samples.get(self.selected_label, []))
        rejection = f" | Last rejection: {self.last_rejection.replace('_', ' ')}" if self.last_rejection else ""
        self.counts.setText(
            f"Valid this capture: {len(self.current_samples)} | Rejected: {self.rejected} | "
            f"Stored for target: {stored}{rejection}"
        )

    def _refresh_buttons(self) -> None:
        capturing = self.state == "capturing"
        self.previous_button.setEnabled(not capturing and self.index > 0)
        self.start_button.setEnabled(self.state == "ready")
        self.retake_button.setEnabled(not capturing and (self.state == "review" or self.batch_saved))
        self.next_button.setEnabled(not capturing and self.index < len(CALIBRATION_PROMPTS) - 1)
        self.finish_button.setEnabled(not capturing)

    def retake(self) -> None:
        if self.batch_saved:
            self._remove_saved_batch()
        self._show_ready_state()

    def previous_expression(self) -> None:
        if self.state == "capturing" or self.index == 0:
            return
        self._discard_pending_debug_images()
        self.index -= 1
        self.target_selector.blockSignals(True)
        self.target_selector.setCurrentIndex(self.index)
        self.target_selector.blockSignals(False)
        self._show_ready_state()

    def next_expression(self) -> None:
        if self.state == "capturing" or self.index >= len(CALIBRATION_PROMPTS) - 1:
            return
        self._discard_pending_debug_images()
        self.index += 1
        self.target_selector.blockSignals(True)
        self.target_selector.setCurrentIndex(self.index)
        self.target_selector.blockSignals(False)
        self._show_ready_state()

    def _target_changed(self, index: int) -> None:
        if self.state == "capturing" or index < 0:
            self.target_selector.blockSignals(True)
            self.target_selector.setCurrentIndex(self.index)
            self.target_selector.blockSignals(False)
            return
        self._discard_pending_debug_images()
        self.index = index
        self._show_ready_state()

    def _show_frame(self, frame, detection) -> None:
        if detection:
            x, y, width, height = detection.box
            self.cv2.rectangle(frame, (x, y), (x + width, y + height), (145, 145, 155), 2)
        rgb = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
        height, width, channels = rgb.shape
        image = QImage(rgb.data, width, height, channels * width, QImage.Format_RGB888).copy()
        self.preview.setPixmap(
            QPixmap.fromImage(image).scaled(self.preview.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def finish(self) -> None:
        if self.profile.exists:
            try:
                self.user_profile.update(
                    {"name": self.user_name.text(), "email": self.user_email.text()}
                )
            except ValueError as exc:
                QMessageBox.warning(self, "User Profile", str(exc))
                return
            self.profile.save()
            self.profile_changed.emit()
            QMessageBox.information(
                self, "Calibration Completed",
                "Calibration completed. EmotionCam will now use your personalized expression "
                "profile when possible."
            )
            self.accept()
        else:
            QMessageBox.warning(self, "Calibration", "No valid expression samples have been saved.")

    def closeEvent(self, event) -> None:
        self._release_camera()
        event.accept()

    def done(self, result: int) -> None:
        self._release_camera()
        super().done(result)

    def _release_camera(self) -> None:
        self.timer.stop()
        if self.capture:
            self.capture.release()
        if not self.batch_saved:
            self._discard_pending_debug_images()

    def _discard_pending_debug_images(self) -> None:
        for path in self.pending_debug_images:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        self.pending_debug_images = []

    def _remove_saved_batch(self) -> None:
        existing = self.profile.samples.get(self.saved_label, [])
        if self.add_more:
            count = len(self.saved_batch)
            if count and existing[-count:] == self.saved_batch:
                del existing[-count:]
                if not existing:
                    self.profile.samples.pop(self.saved_label, None)
        else:
            self.profile.samples.pop(self.saved_label, None)
        self.profile.save()
        for path in self.saved_debug_images:
            try:
                path.unlink()
            except FileNotFoundError:
                pass
        self.saved_batch = []
        self.saved_label = ""
        self.saved_debug_images = []
        self.batch_saved = False
