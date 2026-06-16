# EmotionCam

EmotionCam is a Windows-only, local-only Python desktop application that shows
approximate visible facial-expression estimates from one person using the
built-in laptop webcam.

EmotionCam does **not** know true emotions or diagnose mood or mental state. It
does not identify people, perform face matching, make medical or psychological claims, or support
lie detection, security, hiring, or surveillance use cases.

> EmotionCam processes webcam frames locally. It stores only expression metadata
> and optional personalized calibration features locally. It does not identify
> people or upload data. Raw calibration debug images are off by default.

## Features

- Modern dark/light PySide6 dashboard with live OpenCV webcam preview
- Visible, clickable numeric spinner arrows in both themes
- MediaPipe Face Landmarker detection with normalized landmarks and blendshapes,
  plus an OpenCV frontal/profile fallback
- Approximate categories: neutral, happy, smile, laughing, sad, angry, surprised,
  fearful, disgusted, confused, focused, tired, unknown, low confidence, and no face
- Brief face-missing grace tracking to avoid instant no-face flicker
- Smoothed positive blue, negative orange, and neutral gray face rectangles
- Safe, cooldown-controlled interaction messages
- Optional metadata-only JSONL history, enabled by default with first-start choice
- Local settings, clear logs, open logs folder, and graceful camera errors
- Optional system-tray background mode with cooldown-controlled safe notifications
- Personalized local expression calibration with heuristic, personalized, and hybrid modes
- Local Statistics window with selected-day and last-7-days expression summaries
- Optional local user name/email profile and opt-in daily summary email
- No cloud APIs, network requests, telemetry, or accounts; no saved camera frames by default

## Accuracy note

MediaPipe landmarks and blendshape scores improve tilted-face and smile handling,
while OpenCV remains a conservative fallback. Visible expression estimates are
still approximate and can be wrong, especially with poor lighting, unusual angles,
partial faces, or facial differences. `unknown` and `low confidence` are expected.

## Install for development

Requirements: Windows 10/11 and Python 3.11 or 3.12, 64-bit recommended.

```powershell
cd emotioncam
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m app.main
```

Windows may ask for camera permission. Enable camera access for desktop apps in
Windows Settings if the camera cannot be opened. Close other camera applications
if the webcam is already in use.

## Local data

Configuration:

```text
%LOCALAPPDATA%\EmotionCam\config.json
```

Optional metadata history:

```text
%LOCALAPPDATA%\EmotionCam\logs\expression_history.jsonl
```

History lines contain only timestamps, visible expression labels/groups,
confidence, face-detected status, displayed message text, popup status, and FPS.
Images, video frames, face images, biometric templates, and identity data are
not written by default. The optional **Store raw calibration images for debugging**
setting is off by default and is the only feature that can save calibration frames.

## Personalized expression calibration

Personalized calibration can improve visible-expression estimates by learning
normalized facial-movement feature vectors from your own prompted expressions.
It does not learn identity and does not claim to know true emotions.

Open **Settings > Train / Calibrate Expressions** or press **Improve detection
with calibration** on the dashboard. The unified calibration screen includes a
target-expression dropdown, Previous/Next navigation, a bundled local example
graphic, live visible-expression estimate, and a permissive helper match
indicator. Each target waits until you manually click **Start Capture**.

After capture, review valid/rejected counts and quality. Re-capture replaces the
captured batch instead of silently mixing it. Frames with no clear face, poor
landmarks, blur, poor lighting, or excessive rotation are rejected. Example
graphics are rendered from local assets and never fetched from the internet.

By default, calibration stores only normalized landmark/blendshape feature
vectors and labels at:

```text
%LOCALAPPDATA%\EmotionCam\profile\expression_profile.json
```

After training, EmotionCam switches to **Hybrid recommended** mode. Hybrid mode
uses the personalized profile when confidence is sufficient and falls back to
the conservative heuristic classifier otherwise. Personalized classification
also works while EmotionCam runs in background mode.

Profile controls in Settings can add samples, retrain, delete, export, or import
the profile using local files only. Deleting the profile removes local training
data and returns detection to heuristic mode.

Calibration stores local expression feature data and labels. EmotionCam does not
save camera images unless debug image storage is explicitly enabled.

The future external AI agent backend is an interface-only placeholder. It is
disabled and cannot send frames or make network requests. Enabling such a
backend in the future would require explicit user consent to send images outside
the app.

## Background mode

Press **Run in background** to keep camera analysis and optional metadata logging
active locally while hiding EmotionCam in the Windows system tray. The tray menu
can show the app, stop the camera, or exit. Optional notifications use only stable
smoothed visible-expression groups and configurable cooldowns. No data is uploaded.

## Statistics and optional daily email

Press **Statistics** on the dashboard to view local-only balance, timeline,
label-count, and last-7-days charts derived from metadata history. Corrupted or
old log lines are skipped safely.

Optional user name and email fields are stored at:

```text
%LOCALAPPDATA%\EmotionCam\profile\user_profile.json
```

Daily email summaries are off by default. Enabling SMTP uses the network to send
summary text only; no frames or images are sent. SMTP passwords are stored with
the system credential store when `keyring` is available and are never written
to the JSON profile. The default-mail-client option opens a draft and never
sends automatically.

The official `app\assets\icon.png` is used in the application, documentation,
taskbar, and tray. The generated `icon.ico` contains 16, 32, 48, 64, 128, and
256 pixel Windows icon sizes and is used by PyInstaller and Inno Setup.

## How to start the demo

1. Install EmotionCam or run `python -m app.main`.
2. Open EmotionCam.
3. Select **Help > Start Demo Guide**.
4. Follow the offline `docs\START_DEMO_HERE.html` guide.

The demo guide covers the app icon, dark/light theme switch, visible numeric
spinner arrows, current unified calibration flow, background mode, and logs.

## Test

```powershell
python -m pytest
```

## Build the Windows app

Install requirements, then run:

```powershell
python build_exe.py
```

The unpackaged app folder is created at `dist\EmotionCam\`. Test
`dist\EmotionCam\EmotionCam.exe` before building the installer.

## Build the installer

Install [Inno Setup 6](https://jrsoftware.org/isinfo.php), build the app first,
then compile `installer\emotioncam.iss` in Inno Setup. The installer is written
to `installer\output\`.

The per-user installer needs no administrator access and installs under
`%LOCALAPPDATA%\Programs\EmotionCam`.

## Architecture

- `app/core/camera_worker.py`: background capture and analysis thread
- `app/core/face_detector.py`: local single-face detector
- `app/core/expression_classifier.py`: lightweight local approximation heuristic
- `app/core/expression_backends.py`: heuristic, personalized, hybrid, and disabled external interfaces
- `app/core/expression_features.py`: normalized calibration features and quality checks
- `app/core/expression_profile.py`: local profile persistence and management
- `app/core/smoothing.py`: temporal stabilization and expression grouping
- `app/core/interaction_engine.py`: safe message cooldown logic
- `app/core/config.py`: local JSON settings
- `app/core/logger.py`: metadata-only JSONL history
- `app/ui/`: startup screen, dashboard, settings, camera view, and timeline

## Privacy design

The default application flow makes no network requests. The only implemented
network feature is the explicitly enabled SMTP daily text summary; it never
includes webcam frames or images. Webcam frames exist only in memory while
processing and displaying the live preview. Stopping or closing the camera
discards them. Logging can be disabled before the camera starts or at any time
in Settings. Raw calibration frame storage requires an explicit opt-in setting
and remains local.
