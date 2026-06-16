"""Background webcam capture and local analysis."""

from __future__ import annotations

import time
from concurrent.futures import Future, ThreadPoolExecutor
from datetime import datetime
from typing import Any

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from .ai_agent_classifier import ExternalAIExpressionClassifier, merge_ai_with_local
from .ai_rate_limiter import AIRateLimiter
from .expression_backends import create_expression_classifier
from .expression_backends import ExpressionResult
from .expression_profile import ExpressionProfile
from .face_detector import FaceDetector
from .smoothing import ExpressionSmoother


RECTANGLE_COLORS = {
    "positive": (255, 125, 45),
    "negative": (0, 145, 255),
    "neutral": (145, 145, 155),
}


def camera_indexes_to_try(configured_index: int, max_index: int = 3) -> list[int]:
    """Return configured camera index first, then nearby fallback indexes."""
    indexes = [int(configured_index)]
    indexes.extend(range(max_index + 1))
    return list(dict.fromkeys(index for index in indexes if index >= 0))


def camera_backends(cv2_module: Any) -> list[tuple[str, int]]:
    """Return Windows-friendly OpenCV camera backends in fallback order."""
    candidates = [
        ("DirectShow", getattr(cv2_module, "CAP_DSHOW", 700)),
        ("Media Foundation", getattr(cv2_module, "CAP_MSMF", 1400)),
        ("OpenCV automatic", getattr(cv2_module, "CAP_ANY", 0)),
    ]
    return list(dict.fromkeys(candidates))


def _open_capture_candidate(cv2_module: Any, index: int, backend_name: str, backend_id: int):
    capture = cv2_module.VideoCapture(index, backend_id)
    if not capture or not capture.isOpened():
        if capture:
            capture.release()
        return None, "not_opened"
    capture.set(cv2_module.CAP_PROP_FRAME_WIDTH, 960)
    capture.set(cv2_module.CAP_PROP_FRAME_HEIGHT, 540)
    for _ in range(5):
        ok, frame = capture.read()
        if ok and frame is not None:
            return capture, "ok"
    capture.release()
    return None, "opened_but_no_frames"


def open_camera_capture(cv2_module: Any, configured_index: int):
    """Open a camera capture using several Windows backend fallbacks."""
    attempts: list[str] = []
    for index in camera_indexes_to_try(configured_index):
        for backend_name, backend_id in camera_backends(cv2_module):
            try:
                capture, status = _open_capture_candidate(cv2_module, index, backend_name, backend_id)
            except Exception as exc:
                attempts.append(f"index {index} via {backend_name}: {type(exc).__name__}")
                continue
            attempts.append(f"index {index} via {backend_name}: {status}")
            if capture is not None:
                return capture, index, backend_name, attempts
    return None, None, "", attempts


def camera_unavailable_message(attempts: list[str]) -> str:
    detail = "; ".join(attempts[-6:]) if attempts else "no camera backends were attempted"
    return (
        "Could not open the built-in webcam after trying multiple Windows camera backends.\n\n"
        "Please close apps that may be using the camera, such as Camera, Teams, Zoom, "
        "a browser, or another EmotionCam window. Also check Windows Settings > Privacy "
        "& security > Camera and make sure camera access and desktop app access are enabled. "
        "If antivirus privacy protection is installed, allow EmotionCam to use the camera.\n\n"
        f"Attempt details: {detail}"
    )


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

        self.status_changed.emit("Opening camera...")
        capture, camera_index, backend_name, attempts = open_camera_capture(cv2, int(self.settings["camera_index"]))
        if capture is None:
            self.camera_error.emit(camera_unavailable_message(attempts))
            return
        self.status_changed.emit(f"Camera opened on index {camera_index} using {backend_name}")

        try:
            detector = FaceDetector(
                self.settings["detection_confidence_threshold"],
                self.settings["face_missing_grace_seconds"],
            )
            classifier = create_expression_classifier(self.settings)
            ai_mode = self.settings.get("expression_detection_mode") in {"external_ai", "hybrid_ai"}
            ai_classifier = (
                ExternalAIExpressionClassifier(
                    self.settings,
                    api_key=str(self.settings.get("_session_external_ai_api_key", "")),
                )
                if ai_mode
                else None
            )
            ai_limiter = AIRateLimiter(self.settings.get("external_ai_request_interval_seconds", 10.0))
            ai_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="EmotionCamAI") if ai_mode else None
            ai_future: Future | None = None
            last_ai_result: ExpressionResult | None = None
            last_ai_result_time = ""
            ai_status = "Off"
            ai_error = ""
            profile_active = (
                ExpressionProfile().exists
                and self.settings["personalized_profile_enabled"]
                and self.settings["expression_detection_mode"] in {"personalized", "hybrid", "hybrid_ai"}
            )
            smoother = ExpressionSmoother(
                self.settings["smoothing_window_seconds"],
                self.settings["stable_expression_seconds"],
            )
        except Exception as exc:
            capture.release()
            self.camera_error.emit(f"Classifier unavailable: {exc}")
            return

        if self.settings.get("expression_detection_mode") in {"external_ai", "hybrid_ai"}:
            provider = self.settings.get("external_ai_provider", "openai")
            if provider == "ollama":
                self.status_changed.emit("Camera running - local Ollama AI is optional and rate limited")
            else:
                self.status_changed.emit("Camera running - external AI is optional and rate limited")
        else:
            self.status_changed.emit("Camera running - analysis is local")
        last_frame_time = time.monotonic()
        failures = 0
        try:
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

                if ai_future and ai_future.done():
                    try:
                        last_ai_result = ai_future.result()
                        ai_status = "AI result received"
                        ai_error = ""
                    except Exception as exc:
                        last_ai_result = None
                        ai_status = "Error / fallback to local"
                        ai_error = type(exc).__name__
                    last_ai_result_time = datetime.now().astimezone().isoformat(timespec="seconds")
                    ai_future = None
                elif ai_future:
                    ai_status = "Analyzing"

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
                        local = ExpressionResult(
                            "no_face",
                            "neutral",
                            0.0,
                            {},
                            "local_no_face",
                            {"reason": "face_not_found"},
                            False,
                        )
                    else:
                        local = classifier.classify(frame, face.box, face)

                    ai_request_sent = False
                    if ai_classifier is not None:
                        if ai_future is not None:
                            ai_status = "Analyzing"
                        else:
                            ready, reason = ai_classifier.ready_to_send(face.box if face else None)
                            if ready and ai_limiter.due(now):
                                ai_limiter.mark_sent(now)
                                ai_request_sent = True
                                ai_status = (
                                    "Sending cropped face"
                                    if self.settings.get("external_ai_send_cropped_face_only", True)
                                    else "Sending selected frame"
                                )
                                frame_copy = frame.copy()
                                face_box = face.box if face else None
                                ai_future = ai_executor.submit(ai_classifier.classify, frame_copy, face_box, face)
                            elif ready:
                                ai_status = "Waiting"
                            else:
                                ai_status = {
                                    "external_ai_disabled": "Off",
                                    "consent_required": "Consent required",
                                    "missing_api_key": "Missing OpenAI API key",
                                    "face_not_found": "No face - AI not sent",
                                }.get(reason, "Waiting")

                    final = merge_ai_with_local(
                        self.settings.get("expression_detection_mode", "heuristic"),
                        local,
                        last_ai_result,
                        self.settings.get("external_ai_min_confidence", 0.55),
                    )
                    raw = final.to_dict()
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
                        "external_ai_enabled": bool(self.settings.get("external_ai_enabled", False)),
                        "ai_provider": self.settings.get("external_ai_provider", "openai"),
                        "ai_request_sent": ai_request_sent,
                        "ai_status": ai_status,
                        "last_ai_result_time": last_ai_result_time,
                        "ai_result_label": last_ai_result.label if last_ai_result else "",
                        "ai_result_confidence": last_ai_result.confidence if last_ai_result else 0.0,
                        "ai_result_source": last_ai_result.source if last_ai_result else "",
                        "ai_error": ai_error,
                        "local_result_label": local.label,
                        "local_result_confidence": local.confidence,
                        "local_result_source": local.source,
                        "final_result_source": raw.get("source", "heuristic"),
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
        finally:
            if "ai_executor" in locals() and ai_executor is not None:
                ai_executor.shutdown(wait=False, cancel_futures=True)
        capture.release()
        self.status_changed.emit("Camera stopped")
