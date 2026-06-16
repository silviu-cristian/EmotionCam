# EmotionCam v1.1.0 AI-enabled Release Notes

EmotionCam v1.1.0-ai keeps the original local-first visible-expression
estimation app and adds an optional External AI Analysis backend.

## Highlights

- Optional OpenAI vision analysis through the Responses API.
- External AI is disabled by default.
- Explicit user consent is required before any AI request can run.
- An OpenAI API key is required.
- API keys are not stored in `config.json`.
- Secure key storage uses Windows credential storage through `keyring` when
  available.
- If secure storage is unavailable, the key can be used for the current app
  session only.
- Cropped-face-only sending is enabled by default.
- Hybrid local + AI mode keeps local detection running continuously and sends
  one selected image only at controlled intervals.
- Local detection continues if no key is configured, consent is missing, no face
  is detected, the API times out, the API rate-limits, or a response is invalid.

## Privacy Tradeoff

The v1.0.0 release remains fully local and remains available for download.

The v1.1.0-ai release is still local-first, but if the user explicitly enables
External AI Analysis, accepts consent, and provides an API key, selected cropped
face images or selected full frames may be sent to OpenAI for visible-expression
estimation.

EmotionCam never sends every webcam frame. It sends at most one selected image
per configured interval. The default interval is 10 seconds.

## What Is Sent In AI Mode

- One cropped face image by default.
- One selected full frame only if the user disables cropped-face-only mode.

## What Is Never Sent Or Logged

- API keys in logs or config JSON.
- Raw base64 image data in logs.
- Saved webcam video.
- Face identity data.
- Face matching data.
- Medical, psychological, or sensitive-trait conclusions.

## Installer

Recommended release asset:

```text
EmotionCam_Setup_v1.1.0_AI.exe
```

Do not commit the generated installer into the repository. Attach it to the
GitHub Release for tag `v1.1.0-ai`.
