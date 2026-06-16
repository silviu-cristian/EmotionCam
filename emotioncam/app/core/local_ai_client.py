"""Local Ollama vision client for optional on-device AI expression estimates."""

from __future__ import annotations

import json
from typing import Any
from urllib import error, parse, request

from .ai_client import (
    AI_SYSTEM_PROMPT,
    AI_USER_PROMPT,
    crop_frame_for_ai,
    encode_frame_jpeg_base64,
    parse_ai_response_json,
)
from .expression_backends import ExpressionResult


DEFAULT_OLLAMA_ENDPOINT = "http://localhost:11434"
DEFAULT_OLLAMA_MODEL = "llava:7b"
LOCAL_AI_SOURCE = "local_ai"


def normalize_ollama_endpoint(value: str | None) -> str:
    """Normalize a user-entered Ollama base URL."""
    endpoint = str(value or DEFAULT_OLLAMA_ENDPOINT).strip().rstrip("/")
    if not endpoint:
        endpoint = DEFAULT_OLLAMA_ENDPOINT
    if endpoint.endswith("/api"):
        endpoint = endpoint[:-4]
    return endpoint.rstrip("/")


def is_loopback_endpoint(endpoint: str) -> bool:
    """Return True when an endpoint points at this computer."""
    parsed = parse.urlparse(normalize_ollama_endpoint(endpoint))
    host = (parsed.hostname or "").lower()
    return parsed.scheme in {"http", "https"} and host in {"localhost", "127.0.0.1", "::1"}


def _api_url(endpoint: str, path: str) -> str:
    return f"{normalize_ollama_endpoint(endpoint)}/api/{path.lstrip('/')}"


def _model_names(payload: dict[str, Any]) -> set[str]:
    models = payload.get("models", [])
    if not isinstance(models, list):
        return set()
    names: set[str] = set()
    for item in models:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        model = str(item.get("model", "")).strip()
        if name:
            names.add(name)
        if model:
            names.add(model)
    return names


def model_is_available(model: str, names: set[str]) -> bool:
    """Return True when an Ollama tag list contains the configured model."""
    normalized = str(model or "").strip()
    if not normalized:
        return False
    if normalized in names:
        return True
    if ":" not in normalized and f"{normalized}:latest" in names:
        return True
    return False


class LocalOllamaExpressionClient:
    """Use a local Ollama vision model through the loopback API."""

    def __init__(
        self,
        endpoint: str = DEFAULT_OLLAMA_ENDPOINT,
        model: str = DEFAULT_OLLAMA_MODEL,
    ) -> None:
        self.endpoint = normalize_ollama_endpoint(endpoint)
        self.model = str(model or DEFAULT_OLLAMA_MODEL).strip() or DEFAULT_OLLAMA_MODEL

    def test_connection(self, timeout_seconds: float = 8.0) -> bool:
        """Check that Ollama is reachable locally and the selected model exists."""
        self._ensure_local_endpoint()
        payload = self._request_json("tags", method="GET", timeout_seconds=timeout_seconds)
        names = _model_names(payload)
        if not model_is_available(self.model, names):
            installed = ", ".join(sorted(names)) or "none"
            raise ValueError(
                f"Ollama is running, but model '{self.model}' is not installed. "
                f"Run this in PowerShell: ollama pull {self.model}. "
                f"Installed models: {installed}."
            )
        return True

    def analyze_frame(
        self,
        frame: Any,
        api_key: str = "",
        *,
        face_box: tuple[int, int, int, int] | None = None,
        send_cropped_face_only: bool = True,
        timeout_seconds: float = 20.0,
        min_confidence: float = 0.55,
    ) -> ExpressionResult:
        """Analyze one selected frame with a local Ollama vision model."""
        del api_key
        self._ensure_local_endpoint()
        selected, crop_debug = crop_frame_for_ai(frame, face_box, send_cropped_face_only)
        if selected is None:
            return ExpressionResult(
                "no_face" if crop_debug.get("error") == "face_not_found" else "unknown",
                "neutral",
                0.0,
                {},
                LOCAL_AI_SOURCE,
                {"ai_status": "not_sent", **crop_debug, "provider": "ollama"},
                False,
            )

        image_payload = encode_frame_jpeg_base64(selected)
        response = self._request_json(
            "generate",
            method="POST",
            timeout_seconds=timeout_seconds,
            payload={
                "model": self.model,
                "system": AI_SYSTEM_PROMPT,
                "prompt": (
                    AI_USER_PROMPT
                    + " Return only a compact JSON object with label, group, confidence, reason, "
                    "and alternatives. Do not include markdown."
                ),
                "images": [image_payload],
                "stream": False,
                "format": "json",
                "options": {"temperature": 0},
            },
        )
        text = str(response.get("response", ""))
        result = parse_ai_response_json(text, min_confidence, source=LOCAL_AI_SOURCE)
        result.debug.update(crop_debug)
        result.debug["provider"] = "ollama"
        result.debug["model"] = self.model
        return result

    def _ensure_local_endpoint(self) -> None:
        if not is_loopback_endpoint(self.endpoint):
            raise ValueError(
                "Local Ollama mode only allows localhost/127.0.0.1 endpoints. "
                "This prevents accidental uploads to a remote server."
            )

    def _request_json(
        self,
        path: str,
        *,
        method: str,
        timeout_seconds: float,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        data = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = request.Request(_api_url(self.endpoint, path), data=data, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=float(timeout_seconds)) as response:
                body = response.read().decode("utf-8", errors="replace")
        except error.URLError as exc:
            reason = getattr(exc, "reason", exc)
            raise ConnectionError(
                "Could not reach Ollama at "
                f"{self.endpoint}. Start Ollama first, then try Test Connection again. "
                f"Details: {reason}"
            ) from exc
        except TimeoutError as exc:
            raise TimeoutError("Local Ollama request timed out.") from exc
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError as exc:
            raise ValueError("Ollama returned invalid JSON.") from exc
        if not isinstance(parsed, dict):
            raise ValueError("Ollama returned an unexpected response.")
        return parsed
