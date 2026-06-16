"""MediaPipe-first single-face detection with OpenCV fallback and tracking grace."""

from __future__ import annotations

import time
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FaceDetection:
    box: tuple[int, int, int, int]
    confidence: float
    landmarks: list[tuple[float, float, float]] | None = None
    blendshapes: dict[str, float] | None = None
    backend: str = "opencv"
    using_grace: bool = False


class FaceDetector:
    def __init__(self, min_confidence: float = 0.45, grace_seconds: float = 1.0) -> None:
        import cv2

        self.cv2 = cv2
        self.min_confidence = min_confidence
        self.grace_seconds = max(0.0, grace_seconds)
        root = cv2.data.haarcascades
        self.frontal = cv2.CascadeClassifier(root + "haarcascade_frontalface_default.xml")
        self.profile = cv2.CascadeClassifier(root + "haarcascade_profileface.xml")
        self._last: FaceDetection | None = None
        self._last_seen = float("-inf")
        self._landmarker = self._create_landmarker()

    @staticmethod
    def _create_landmarker() -> Any | None:
        try:
            import mediapipe as mp

            root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
            model = root / "app" / "assets" / "face_landmarker.task"
            options = mp.tasks.vision.FaceLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(model)),
                running_mode=mp.tasks.vision.RunningMode.VIDEO,
                num_faces=1,
                min_face_detection_confidence=0.45,
                min_face_presence_confidence=0.45,
                min_tracking_confidence=0.45,
                output_face_blendshapes=True,
            )
            return mp.tasks.vision.FaceLandmarker.create_from_options(options)
        except (ImportError, AttributeError, RuntimeError, ValueError):
            return None

    def detect(self, frame: Any, now: float | None = None) -> FaceDetection | None:
        current = time.monotonic() if now is None else now
        detection = self._detect_landmarker(frame, current) if self._landmarker is not None else None
        if detection is None:
            detection = self._detect_opencv(frame)
        if detection is not None:
            self._last = detection
            self._last_seen = current
            return detection
        if self._last and current - self._last_seen <= self.grace_seconds:
            decay = 1.0 - (current - self._last_seen) / max(0.001, self.grace_seconds)
            return FaceDetection(
                self._last.box,
                max(0.15, self._last.confidence * decay),
                self._last.landmarks,
                self._last.blendshapes,
                self._last.backend,
                True,
            )
        return None

    def _detect_landmarker(self, frame: Any, now: float) -> FaceDetection | None:
        import mediapipe as mp

        height, width = frame.shape[:2]
        rgb = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        results = self._landmarker.detect_for_video(image, int(now * 1000))
        if not results.face_landmarks:
            return None
        points = [(item.x, item.y, item.z) for item in results.face_landmarks[0]]
        blendshapes = {}
        if results.face_blendshapes:
            blendshapes = {
                item.category_name: float(item.score) for item in results.face_blendshapes[0]
            }
        xs = [point[0] for point in points]
        ys = [point[1] for point in points]
        pad_x, pad_y = (max(xs) - min(xs)) * 0.12, (max(ys) - min(ys)) * 0.15
        left = max(0, int((min(xs) - pad_x) * width))
        top = max(0, int((min(ys) - pad_y) * height))
        right = min(width, int((max(xs) + pad_x) * width))
        bottom = min(height, int((max(ys) + pad_y) * height))
        return FaceDetection(
            (left, top, right - left, bottom - top),
            0.92,
            points,
            blendshapes,
            "mediapipe",
        )

    def _detect_opencv(self, frame: Any) -> FaceDetection | None:
        gray = self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2GRAY)
        gray = self.cv2.equalizeHist(gray)
        options: list[tuple[int, int, int, int]] = []
        neighbors = max(3, round(3 + self.min_confidence * 5))
        for cascade, image, mirrored in (
            (self.frontal, gray, False),
            (self.profile, gray, False),
            (self.profile, self.cv2.flip(gray, 1), True),
        ):
            faces = cascade.detectMultiScale(
                image, scaleFactor=1.08, minNeighbors=neighbors, minSize=(70, 70)
            )
            for x, y, width, height in faces:
                if mirrored:
                    x = gray.shape[1] - x - width
                options.append((int(x), int(y), int(width), int(height)))
        if not options:
            return None
        box = max(options, key=lambda item: item[2] * item[3])
        confidence = min(0.82, 0.55 + (box[2] * box[3]) / max(1, gray.size))
        return FaceDetection(box, confidence, None, None, "opencv")
