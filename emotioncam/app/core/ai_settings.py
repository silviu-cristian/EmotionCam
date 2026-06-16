"""Secure settings helpers for optional external AI analysis."""

from __future__ import annotations


AI_CREDENTIAL_SERVICE = "EmotionCam External AI"
AI_CREDENTIAL_USERNAME = "openai_api_key"


def normalize_api_key(value: str) -> str:
    """Normalize a typed API key without validating provider-specific prefixes."""
    return str(value or "").strip()


def load_api_key() -> str:
    """Load the OpenAI API key from secure OS credential storage when available."""
    try:
        import keyring

        return keyring.get_password(AI_CREDENTIAL_SERVICE, AI_CREDENTIAL_USERNAME) or ""
    except Exception:
        return ""


def store_api_key(api_key: str) -> bool:
    """Store the API key with keyring. Returns False when secure storage is unavailable."""
    normalized = normalize_api_key(api_key)
    if not normalized:
        return False
    try:
        import keyring

        keyring.set_password(AI_CREDENTIAL_SERVICE, AI_CREDENTIAL_USERNAME, normalized)
        return True
    except Exception:
        return False


def delete_api_key() -> bool:
    """Remove the stored API key if present."""
    try:
        import keyring

        keyring.delete_password(AI_CREDENTIAL_SERVICE, AI_CREDENTIAL_USERNAME)
        return True
    except Exception:
        return False


def has_stored_api_key() -> bool:
    """Return True when a key appears to be stored securely."""
    return bool(load_api_key())
