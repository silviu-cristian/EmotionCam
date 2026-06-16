"""Background webcam capture and local analysis."""

from __future__ import annotations

import time
from typing import Any

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from .expression_backends import create_expression_classifier
from .expression_profile import ExpressionProfile
from .face_detector import FaceDetector
from .smoothing import ExpressionSmoother


RECTANGLE_COLORS = {
    "positive": (255, 125, 45),
    "negative": (0, 145, 255),
    "neutral": (145, 145, 155),
}


class CameraWorker(QThread):
    frame_ready = Signal(QImage)
    result_ready = Signal(dict)
    status_changed = Signal(str)
    camera_error = Signal(str)

    def __init__(self, settings: dict[str, Any]) -> None:
        super().__init__()
        self.settings = dict(settings)
        self._running = True
        self._analysis_paused = False

    def stop(self) -> None:
        self._running = False
        self.requestInterruption()

    def set_analysis_paused(self, paused: bool) -> None:
        self._analysis_paused = paused

    def run(self) -> None:
        try:
            import cv2
        except ImportError:
            self.camera_error.emit("OpenCV is unavailable. Reinstall EmotionCam.")
            return

        capture = cv2.VideoCapture(int(self.settings["camera_index"]), cv2.CAP_DSHOW)
        if not capture.isOpened():
            self.camera_error.emit(
                "Could not open the built-in webcam. It may be unavailable, blocked, "
                "or already in use by another application."
            )
            return
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

        try:
            detector = FaceDetector(
                self.settings["detection_confidence_threshold"],
                self.settings["face_missing_grace_seconds"],
            )
            classifier = create_expression_classifier(self.settings)
            profile_active = (
                ExpressionProfile().exists
                and self.settings["personalized_profile_enabled"]
                and self.settings["expression_detection_mode"] in {"personalized", "hybrid"}
            )
            smoother = ExpressionSmoother(
                self.settings["smoothing_window_seconds"],
                self.settings["stable_expression_seconds"],
            )
        except Exception as exc:
            capture.release()
            self.camera_error.emit(f"Classifier unavailable: {exc}")
            return

        self.status_changed.emit("Camera running - analysis is local")
        last_frame_time = time.monotonic()
        failures = 0
        while self._running and not self.isInterruptionRequested():
            ok, frame = capture.read()
            now = time.monotonic()
            if not ok:
                failures += 1
                if failures >= 20:
                    self.camera_error.emit("OpenCV capture failure. The camera stream stopped.")
                    break
                self.msleep(30)
                continue
            failures = 0
            elapsed = max(0.001, now - last_frame_time)
            fps = 1.0 / elapsed
            last_frame_time = now

            if self._analysis_paused:
                result = {
                    "label": "unknown",
                    "group": "neutral",
                    "confidence": 0.0,
                    "face_detected": False,
                    "fps": fps,
                    "paused": True,
                }
            else:
                face = detector.detect(frame, now)
                if face is None:
                    raw = {
                        "label": "no_face",
                        "group": "neutral",
                        "confidence": 0.0,
                        "face_detected": False,
                        "probabilities": {},
                    }
                else:
                    raw = classifier.classify(frame, face.box, face).to_dict()
                smooth = smoother.add(raw["label"], raw["confidence"], raw["face_detected"], now)
                result = {
                    "label": smooth.label,
                    "group": smooth.group,
                    "confidence": smooth.confidence,
                    "face_detected": smooth.face_detected,
                    "fps": fps,
                    "paused": False,
                    "raw_label": raw["label"],
                    "face_detection_confidence": face.confidence if face else 0.0,
                    "using_face_grace": face.using_grace if face else False,
                    "detector_backend": face.backend if face else "none",
                    "probabilities": raw.get("probabilities", {}),
                    "classifier_source": raw.get("source", "heuristic"),
                    "classifier_debug": raw.get("debug", {}),
                    "detection_mode": self.settings["expression_detection_mode"],
                    "personalized_profile_active": profile_active,
                }
                if face and self.settings["show_face_rectangle"]:
                    x, y, width, height = face.box
                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + width, y + height),
                        RECTANGLE_COLORS[smooth.group],
                        3,
                    )

            if not self._running or self.isInterruptionRequested():
                break
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            height, width, channels = rgb.shape
            image = QImage(rgb.data, width, height, channels * width, QImage.Format_RGB888).copy()
            self.frame_ready.emit(image)
            self.result_ready.emit(result)
        capture.release()
        self.status_changed.emit("Camera stopped")
