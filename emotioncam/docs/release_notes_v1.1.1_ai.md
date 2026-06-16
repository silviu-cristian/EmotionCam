# EmotionCam v1.1.1 AI-enabled Hotfix Release Notes

EmotionCam v1.1.1-ai is a small hotfix for the AI-enabled release.

## What Changed

- Fixed External AI activation so enabling External AI Analysis automatically
  selects the Hybrid local + AI detection mode.
- Migrates existing configs where External AI was enabled and consent accepted
  but the detection mode was still local hybrid.
- Adds clearer dashboard wording when External AI is enabled but inactive
  because a local-only detection mode is selected.
- Adds tests for External AI mode synchronization.

## Privacy

External AI remains off by default. No images are sent unless the user
explicitly enables External AI Analysis, accepts consent, provides an API key,
and uses an AI detection mode.

The v1.0.0 local-only release remains available for privacy-focused/offline use.

## Installer

Recommended release asset:

```text
EmotionCam_Setup_v1.1.1_AI.exe
```
