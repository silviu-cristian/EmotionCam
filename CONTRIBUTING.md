# Contributing to EmotionCam

EmotionCam is a Windows-first, privacy-focused desktop app for local
visible-expression estimates.

## Local Setup

```powershell
cd emotioncam
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pytest
```

## Privacy Rules

- Do not add cloud analysis as a default behavior.
- Do not commit webcam images, video frames, logs, user profiles, SMTP secrets,
  calibration profiles, or raw calibration debug images.
- Keep user-facing language focused on visible-expression estimates, not true
  emotions or diagnoses.

## Release Artifacts

Generated installers are not committed. Build `release\EmotionCam_Setup.exe`
locally and attach it to a GitHub Release.
