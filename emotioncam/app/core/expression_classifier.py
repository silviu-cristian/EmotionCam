"""Conservative local visible-expression estimator."""

from __future__ import annotations

import math
from typing import Any

from .face_detector import FaceDetection
from .smoothing import EXPRESSION_GROUPS


NEGATIVE_LABELS = {
    "sad", "angry", "fearful", "disgusted", "tired", "bored", "frustrated", "concerned"
}
POSITIVE_LABELS = {
    "happy", "smile", "smile_small", "smile_big", "laughing", "amused", "surprised"
}


class ExpressionClassifier:
    """Estimate visible expressions without inferring true internal emotions."""

    def __init__(
        self,
        confidence_threshold: float = 0.45,
        negative_min_confidence: float = 0.65,
        positive_min_confidence: float = 0.50,
    ) -> None:
        import cv2

        self.cv2 = cv2
        self.threshold = confidence_threshold
        self.negative_min = negative_min_confidence
        self.positive_min = positive_min_confidence
        self.smile = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

    def classify(self, frame: Any, face: FaceDetection | tuple[int, int, int, int]) -> dict[str, Any]:
        detection = face if isinstance(face, FaceDetection) else FaceDetection(face, 0.6)
        if detection.blendshapes:
            probabilities = self._blendshape_probabilities(detection.blendshapes)
        elif detection.landmarks:
            probabilities = self._landmark_probabilities(detection.landmarks)
        else:
            probabilities = self._opencv_probabilities(frame, detection.box)
        label, confidence = max(probabilities.items(), key=lambda item: item[1])
        return self._safe_result(label, confidence, probabilities)

    def _blendshape_probabilities(self, scores: dict[str, float]) -> dict[str, float]:
        average = lambda left, right: (scores.get(left, 0.0) + scores.get(right, 0.0)) / 2
        smile = average("mouthSmileLeft", "mouthSmileRight")
        cheek = average("cheekSquintLeft", "cheekSquintRight")
        jaw_open = scores.get("jawOpen", 0.0)
        eye_wide = average("eyeWideLeft", "eyeWideRight")
        eye_squint = average("eyeSquintLeft", "eyeSquintRight")
        eye_blink = average("eyeBlinkLeft", "eyeBlinkRight")
        brow_down = average("browDownLeft", "browDownRight")
        brow_up = scores.get("browInnerUp", 0.0)
        frown = average("mouthFrownLeft", "mouthFrownRight")
        nose_sneer = average("noseSneerLeft", "noseSneerRight")
        upper_up = average("mouthUpperUpLeft", "mouthUpperUpRight")
        asymmetry = abs(scores.get("browOuterUpLeft", 0.0) - scores.get("browOuterUpRight", 0.0))
        return {
            "smile": self._clamp(smile * 1.15),
            "happy": self._clamp(smile * 0.8 + cheek * 0.35),
            "laughing": self._clamp(smile * 0.8 + jaw_open * 0.55 + cheek * 0.2),
            "surprised": self._clamp(jaw_open * 0.55 + eye_wide * 0.45 + brow_up * 0.25),
            "sad": self._clamp(frown * 0.65 + brow_up * 0.25),
            "angry": self._clamp(brow_down * 0.65 + scores.get("mouthPressLeft", 0.0) * 0.2),
            "fearful": self._clamp(eye_wide * 0.5 + brow_up * 0.35 + jaw_open * 0.2),
            "disgusted": self._clamp(min(nose_sneer, upper_up) * 0.85),
            "confused": self._clamp(asymmetry * 1.2),
            "focused": self._clamp(eye_squint * 0.45 + brow_down * 0.25),
            "tired": self._clamp(eye_blink * 0.55),
            "neutral": self._clamp(scores.get("_neutral", 0.0) * 0.85 + 0.42),
        }

    @staticmethod
    def _distance(points: list[tuple[float, float, float]], left: int, right: int) -> float:
        a, b = points[left], points[right]
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def _landmark_probabilities(self, points: list[tuple[float, float, float]]) -> dict[str, float]:
        eye_distance = max(0.001, self._distance(points, 33, 263))
        mouth_width = self._distance(points, 61, 291) / eye_distance
        mouth_open = self._distance(points, 13, 14) / eye_distance
        left_eye_open = self._distance(points, 159, 145) / eye_distance
        right_eye_open = self._distance(points, 386, 374) / eye_distance
        eye_open = (left_eye_open + right_eye_open) / 2
        mouth_corner_height = ((points[61][1] + points[291][1]) / 2 - points[13][1]) / eye_distance
        eye_asymmetry = abs(left_eye_open - right_eye_open)

        smile = self._clamp((mouth_width - 0.72) * 2.2 + mouth_corner_height * 1.5)
        laughing = self._clamp((smile - 0.55) * 1.7 + (mouth_open - 0.10) * 3.0)
        surprised = self._clamp((mouth_open - 0.16) * 3.2 + (eye_open - 0.055) * 4.0)
        tired = self._clamp((0.040 - eye_open) * 8.0)
        confused = self._clamp((eye_asymmetry - 0.012) * 8.0)
        focused = self._clamp((0.060 - eye_open) * 4.0 + (0.10 - mouth_open) * 1.5)

        # Strong negative labels require conservative, combined geometric evidence.
        angry = self._clamp((focused - 0.65) * 0.75)
        sad = self._clamp((0.68 - mouth_width) * 1.5 + (0.055 - eye_open) * 2.0)
        fearful = self._clamp((surprised - 0.78) * 0.65)
        disgusted = 0.0  # A reliable disgust estimate needs stronger evidence than these landmarks.
        happy = self._clamp(smile * 0.90 + eye_open * 1.2)
        neutral = self._clamp(0.72 - max(smile, laughing, surprised, tired, confused) * 0.45)
        return {
            "neutral": neutral,
            "happy": happy,
            "smile": smile,
            "laughing": laughing,
            "surprised": surprised,
            "focused": focused,
            "confused": confused,
            "tired": tired,
            "angry": angry,
            "sad": sad,
            "fearful": fearful,
            "disgusted": disgusted,
        }

    def _opencv_probabilities(
        self, frame: Any, box: tuple[int, int, int, int]
    ) -> dict[str, float]:
        x, y, width, height = box
        roi = frame[y : y + height, x : x + width]
        probabilities = {"neutral": 0.62, "unknown": 0.28}
        if roi.size == 0:
            return {"unknown": 1.0}
        gray = self.cv2.equalizeHist(self.cv2.cvtColor(roi, self.cv2.COLOR_BGR2GRAY))
        smiles = self.smile.detectMultiScale(
            gray[int(height * 0.42) :, :],
            scaleFactor=1.45,
            minNeighbors=14,
            minSize=(max(25, width // 4), max(12, height // 12)),
        )
        if len(smiles):
            widest = max(item[2] for item in smiles) / max(1, width)
            probabilities["smile"] = min(0.88, 0.55 + widest * 0.45)
            probabilities["happy"] = min(0.78, probabilities["smile"] - 0.08)
            probabilities["neutral"] = 0.30
        return probabilities

    def _safe_result(
        self, label: str, confidence: float, probabilities: dict[str, float]
    ) -> dict[str, Any]:
        if label in NEGATIVE_LABELS and confidence < self.negative_min:
            label = "neutral" if probabilities.get("neutral", 0.0) >= self.threshold else "unknown"
            confidence = max(probabilities.get(label, 0.0), 0.35)
        elif label in POSITIVE_LABELS and confidence < self.positive_min:
            label, confidence = "unknown", confidence
        elif confidence < self.threshold:
            label = "low_confidence"
        top = sorted(probabilities.items(), key=lambda item: item[1], reverse=True)[:5]
        return {
            "label": label,
            "group": EXPRESSION_GROUPS.get(label, "neutral"),
            "confidence": confidence,
            "face_detected": True,
            "probabilities": {key: round(value, 3) for key, value in top},
        }

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(0.98, value))
