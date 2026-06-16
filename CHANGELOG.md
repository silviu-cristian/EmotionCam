# Changelog

## 1.2.0-ai - 2026-06-16

- Added optional **Local Ollama AI** provider for visible-expression estimates
  running on the user's own PC.
- Kept OpenAI as an optional cloud/external provider, still disabled by default
  and still requiring explicit consent plus a valid API key.
- Added Local Ollama settings for endpoint and vision model, defaulting to
  `http://localhost:11434` and `llava:7b`.
- Added loopback-only endpoint validation so Local Ollama mode cannot
  accidentally send frames to a remote server.
- Updated Test Connection to test either OpenAI or Local Ollama and report
  missing Ollama/model setup clearly.
- Added provider/source metadata to logs without logging images, base64 data, or
  API keys.
- Added tests for Local Ollama provider selection, endpoint validation, response
  parsing, and no-face/no-upload behavior.

## 1.1.3-ai - 2026-06-16

- Added clear Settings-dialog feedback for External AI Test Connection.
- The Test Connection button now changes to Testing while the request is
  running, then shows a success or failure message in the Settings dialog.
- Added popup confirmation for AI connection test success/failure.
- Added tests for AI connection test progress and result feedback.

## 1.1.2-ai - 2026-06-16

- Improved Windows camera startup reliability by trying DirectShow, Media
  Foundation, and OpenCV automatic camera backends instead of one backend only.
- Added fallback scanning of nearby camera indexes when the configured index
  cannot be opened.
- Verified the camera can actually return frames before starting analysis.
- Improved camera error guidance for Windows camera privacy settings,
  antivirus privacy blocking, and apps that may already be using the webcam.
- Added tests for camera backend fallback behavior.

## 1.1.1-ai - 2026-06-16

- Fixed External AI activation so enabling External AI automatically selects
  the Hybrid local + AI detection mode.
- Added migration for existing configs where External AI was enabled and
  consented but the detection mode was still local hybrid.
- Added dashboard wording for the case where External AI is enabled but not
  active in the selected detection mode.
- Added tests for External AI mode synchronization.

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
