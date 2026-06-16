"""Normalized landmark and blendshape features for personalized calibration."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .face_detector import FaceDetection


FEATURE_NAMES = (
    "mouth_width",
    "mouth_open",
    "mouth_corner_lift",
    "left_eye_open",
    "right_eye_open",
    "eye_asymmetry",
    "brow_raise",
    "brow_furrow",
    "cheek_raise",
    "head_roll",
    "yaw_proxy",
    "smile",
    "jaw_open",
    "nose_sneer",
)


@dataclass(frozen=True)
class FeatureSample:
    values: list[float]
    quality: float
    debug: dict[str, float]


def _distance(points: list[tuple[float, float, float]], left: int, right: int) -> float:
    a, b = points[left], points[right]
    return math.hypot(a[0] - b[0], a[1] - b[1])


def extract_expression_features(detection: FaceDetection) -> FeatureSample | None:
    points = detection.landmarks
    if not points or len(points) < 468:
        return None
    eye_distance = _distance(points, 33, 263)
    if eye_distance < 0.02:
        return None
    scale = max(0.001, eye_distance)
    blend = detection.blendshapes or {}
    average = lambda left, right: (blend.get(left, 0.0) + blend.get(right, 0.0)) / 2
    left_eye = _distance(points, 159, 145) / scale
    right_eye = _distance(points, 386, 374) / scale
    eye_line_x = points[263][0] - points[33][0]
    eye_line_y = points[263][1] - points[33][1]
    roll = math.atan2(eye_line_y, eye_line_x) / math.pi
    nose_offset = (points[1][0] - (points[33][0] + points[263][0]) / 2) / scale
    corner_lift = ((points[61][1] + points[291][1]) / 2 - points[13][1]) / scale
    values = [
        _distance(points, 61, 291) / scale,
        _distance(points, 13, 14) / scale,
        corner_lift,
        left_eye,
        right_eye,
        abs(left_eye - right_eye),
        blend.get("browInnerUp", 0.0),
        average("browDownLeft", "browDownRight"),
        average("cheekSquintLeft", "cheekSquintRight"),
        roll,
        nose_offset,
        average("mouthSmileLeft", "mouthSmileRight"),
        blend.get("jawOpen", 0.0),
        average("noseSneerLeft", "noseSneerRight"),
    ]
    rotation_penalty = min(0.7, abs(roll) * 1.8 + max(0.0, abs(nose_offset) - 0.22))
    quality = max(0.0, min(1.0, detection.confidence * (1.0 - rotation_penalty)))
    return FeatureSample(
        [round(float(item), 6) for item in values],
        quality,
        {"head_roll": roll, "yaw_proxy": nose_offset, "landmark_confidence": detection.confidence},
    )


def centroid(samples: list[list[float]]) -> list[float]:
    return np.asarray(samples, dtype=float).mean(axis=0).round(6).tolist()


def feature_distance(left: list[float], right: list[float]) -> float:
    return float(np.linalg.norm(np.asarray(left, dtype=float) - np.asarray(right, dtype=float)))


def calibration_sample_acceptable(
    detection: FaceDetection | None,
    sample: FeatureSample | None,
    blur: float,
    brightness: float,
) -> tuple[bool, str]:
    if not detection or detection.using_grace or detection.confidence < 0.65:
        return False, "face_or_landmarks_unclear"
    if not sample or sample.quality < 0.55:
        return False, "rotation_or_landmark_quality"
    if blur < 45:
        return False, "too_blurry"
    if brightness < 35 or brightness > 225:
        return False, "poor_lighting"
    return True, "good"
