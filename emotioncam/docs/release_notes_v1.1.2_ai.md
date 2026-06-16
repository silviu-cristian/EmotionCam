# EmotionCam v1.1.2 AI-enabled Camera Hotfix Release Notes

EmotionCam v1.1.2-ai improves Windows webcam startup reliability.

## What Changed

- Tries multiple Windows OpenCV camera backends instead of DirectShow only:
  DirectShow, Media Foundation, and OpenCV automatic mode.
- Tries nearby camera indexes if the configured index cannot be opened.
- Verifies that the camera can actually return frames before analysis starts.
- Shows a more useful error message when the camera is blocked, busy, or
  unavailable.
- Adds tests for camera fallback behavior.

## If The Camera Still Does Not Open

Check these Windows-side blockers:

- Close Camera, Teams, Zoom, browsers, or any other app using the webcam.
- Check **Windows Settings > Privacy & security > Camera**.
- Enable camera access and desktop app camera access.
- If antivirus privacy protection is installed, allow EmotionCam to use the
  camera.
- Restart Windows if another process is holding the camera driver.

## Privacy

This hotfix does not change privacy behavior. External AI remains off by default
and still requires explicit consent and an API key.

The v1.0.0 local-only release remains available for privacy-focused/offline use.

## Installer

Recommended release asset:

```text
EmotionCam_Setup_v1.1.2_AI.exe
```
