# Changelog

## 1.1.0-ai - 2026-06-16

- Added optional External AI Analysis using OpenAI vision through the Responses
  API.
- Added explicit external-AI consent, OpenAI API-key field, secure key storage
  through Windows credential storage when available, and current-session key
  fallback when secure storage is unavailable.
- Added External AI only and Hybrid local + AI detection modes.
- Added cropped-face-only AI sending mode, enabled by default.
- Added AI request rate limiting and timeout fallback so the UI remains
  responsive and local detection continues.
- Added dashboard AI status, last AI result, local result, final result source,
  and debug visibility.
- Added AI metadata log fields while continuing to exclude images, base64 data,
  and API keys.
- Updated docs, screenshots, installer naming, and release guidance.
- The v1.0.0 local-only release remains available for privacy-focused/offline
  use.

## 1.0.0 - 2026-06-16

- Initial release-ready EmotionCam application.
- Added dark/light dashboard, settings, calibration, statistics, background
  mode, metadata logs, user profile, and optional text-only email summaries.
- Added camera-free documentation screenshots and polished user/demo guides.
- Added PyInstaller and Inno Setup release build flow.
