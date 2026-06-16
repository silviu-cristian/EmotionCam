"""OpenAI vision client for optional external visible-expression estimates."""

from __future__ import annotations

import base64
import json
from typing import Any

from .ai_privacy import AI_SUPPORTED_GROUPS, AI_SUPPORTED_LABELS, group_for_label
from .expression_backends import ExpressionResult


AI_SYSTEM_PROMPT = (
    "Analyze the visible facial expression in the image. Do not infer true internal "
    "emotion, mental health, identity, age, gender, ethnicity, or any sensitive trait. "
    "Return only a visible expression estimate."
)

AI_USER_PROMPT = (
    "Return only JSON for one visible expression estimate. Supported labels: "
    + ", ".join(sorted(AI_SUPPORTED_LABELS))
    + ". Supported groups: positive, neutral, negative."
)

AI_RESPONSE_FORMAT = {
    "type": "json_schema",
    "name": "emotioncam_expression_estimate",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "required": ["label", "group", "confidence", "reason", "alternatives"],
        "properties": {
            "label": {"type": "string", "enum": sorted(AI_SUPPORTED_LABELS)},
            "group": {"type": "string", "enum": sorted(AI_SUPPORTED_GROUPS)},
            "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            "reason": {"type": "string", "maxLength": 220},
            "alternatives": {
                "type": "array",
                "maxItems": 3,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["label", "confidence"],
                    "properties": {
                        "label": {"type": "string", "enum": sorted(AI_SUPPORTED_LABELS)},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    },
                },
            },
        },
    },
}


def clamp_confidence(value: Any) -> float:
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return 0.0


def sanitize_reason(value: Any, limit: int = 180) -> str:
    text = " ".join(str(value or "").split())
    return text[:limit]


def unknown_result(reason: str, source: str = "external_ai", confidence: float = 0.0) -> ExpressionResult:
    return ExpressionResult(
        "unknown",
        "neutral",
        clamp_confidence(confidence),
        {},
        source,
        {"ai_status": "fallback", "reason": reason},
        True,
    )


def parse_ai_response_json(text: str, min_confidence: float = 0.55) -> ExpressionResult:
    """Validate the model's JSON and convert it to an ExpressionResult."""
    try:
        payload = json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return unknown_result("invalid_json")
    if not isinstance(payload, dict):
        return unknown_result("invalid_payload")

    label = str(payload.get("label", "unknown")).strip().lower().replace(" ", "_")
    group = str(payload.get("group", "neutral")).strip().lower()
    confidence = clamp_confidence(payload.get("confidence", 0.0))
    if label not in AI_SUPPORTED_LABELS:
        return unknown_result("invalid_label", confidence=confidence)
    expected_group = group_for_label(label)
    if group not in AI_SUPPORTED_GROUPS or (label not in {"unknown", "no_face"} and group != expected_group):
        group = expected_group
    if confidence < min_confidence:
        return unknown_result("low_confidence", confidence=confidence)

    probabilities = {label: confidence}
    alternatives = payload.get("alternatives", [])
    if isinstance(alternatives, list):
        for item in alternatives[:3]:
            if not isinstance(item, dict):
                continue
            alt_label = str(item.get("label", "")).strip().lower().replace(" ", "_")
            if alt_label in AI_SUPPORTED_LABELS:
                probabilities[alt_label] = clamp_confidence(item.get("confidence", 0.0))
    return ExpressionResult(
        label,
        group,
        confidence,
        dict(sorted(probabilities.items(), key=lambda item: item[1], reverse=True)[:4]),
        "external_ai",
        {
            "ai_status": "result_received",
            "reason": sanitize_reason(payload.get("reason", "")),
        },
        label != "no_face",
    )


def crop_frame_for_ai(
    frame: Any,
    face_box: tuple[int, int, int, int] | None,
    send_cropped_face_only: bool = True,
    margin_ratio: float = 0.28,
) -> tuple[Any | None, dict[str, Any]]:
    """Return a privacy-conscious frame crop plus debug metadata."""
    if frame is None:
        return None, {"error": "frame_unavailable"}
    if send_cropped_face_only and face_box is None:
        return None, {"error": "face_not_found", "cropped": True}
    if not send_cropped_face_only or face_box is None:
        return frame, {"cropped": False}

    height, width = frame.shape[:2]
    x, y, box_width, box_height = face_box
    margin_x = int(box_width * margin_ratio)
    margin_y = int(box_height * margin_ratio)
    left = max(0, x - margin_x)
    top = max(0, y - margin_y)
    right = min(width, x + box_width + margin_x)
    bottom = min(height, y + box_height + margin_y)
    if right <= left or bottom <= top:
        return None, {"error": "invalid_face_crop", "cropped": True}
    return frame[top:bottom, left:right].copy(), {
        "cropped": True,
        "crop_box": (left, top, right - left, bottom - top),
    }


def encode_frame_data_url(frame: Any, max_side: int = 768, jpeg_quality: int = 82) -> str:
    """Resize/compress an OpenCV BGR image and return a JPEG data URL."""
    import cv2

    if frame is None or getattr(frame, "size", 0) == 0:
        raise ValueError("No image data is available for AI analysis.")
    height, width = frame.shape[:2]
    scale = min(1.0, max_side / max(height, width))
    prepared = frame
    if scale < 1.0:
        prepared = cv2.resize(frame, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)
    ok, encoded = cv2.imencode(".jpg", prepared, [int(cv2.IMWRITE_JPEG_QUALITY), int(jpeg_quality)])
    if not ok:
        raise ValueError("Could not encode the selected frame for AI analysis.")
    payload = base64.b64encode(encoded.tobytes()).decode("ascii")
    return f"data:image/jpeg;base64,{payload}"


class OpenAIExpressionClient:
    """Thin wrapper around the OpenAI Responses API."""

    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        self.model = model

    def analyze_frame(
        self,
        frame: Any,
        api_key: str,
        *,
        face_box: tuple[int, int, int, int] | None = None,
        send_cropped_face_only: bool = True,
        timeout_seconds: float = 20.0,
        min_confidence: float = 0.55,
    ) -> ExpressionResult:
        selected, crop_debug = crop_frame_for_ai(frame, face_box, send_cropped_face_only)
        if selected is None:
            return ExpressionResult(
                "no_face" if crop_debug.get("error") == "face_not_found" else "unknown",
                "neutral",
                0.0,
                {},
                "external_ai",
                {"ai_status": "not_sent", **crop_debug},
                False,
            )
        image_url = encode_frame_data_url(selected)
        text = self._responses_create(api_key, image_url, timeout_seconds)
        result = parse_ai_response_json(text, min_confidence)
        result.debug.update(crop_debug)
        return result

    def test_connection(self, api_key: str, timeout_seconds: float = 20.0) -> bool:
        if not api_key:
            raise ValueError("Enter an OpenAI API key first.")
        from openai import OpenAI

        client = OpenAI(api_key=api_key).with_options(timeout=timeout_seconds)
        response = client.responses.create(
            model=self.model,
            input="Return the exact JSON object {\"ok\": true}.",
            text={
                "format": {
                    "type": "json_schema",
                    "name": "emotioncam_connection_test",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["ok"],
                        "properties": {"ok": {"type": "boolean"}},
                    },
                }
            },
        )
        payload = json.loads(response.output_text)
        return bool(payload.get("ok"))

    def _responses_create(self, api_key: str, image_url: str, timeout_seconds: float) -> str:
        if not api_key:
            raise ValueError("OpenAI API key is missing.")
        from openai import OpenAI

        client = OpenAI(api_key=api_key).with_options(timeout=timeout_seconds)
        response = client.responses.create(
            model=self.model,
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": AI_SYSTEM_PROMPT}],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": AI_USER_PROMPT},
                        {"type": "input_image", "image_url": image_url},
                    ],
                },
            ],
            text={"format": AI_RESPONSE_FORMAT},
        )
        return response.output_text
