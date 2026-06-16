# EmotionCam

![EmotionCam icon](app/assets/icon.png)

EmotionCam is a Windows desktop app that estimates visible facial expressions
from a webcam feed. It is designed for one person using a built-in laptop webcam
and presents smoothed, approximate expression estimates such as neutral, smile,
focused, surprised, tired, or unknown.

EmotionCam estimates **visible expressions**, not guaranteed true emotions. It
does not diagnose mood or mental state and is not for medical, psychological,
legal, hiring, security, surveillance, or lie-detection decisions.

![EmotionCam dashboard](docs/screenshots/02_main_dashboard_dark_theme.png)

## Features

- Modern PySide6 dashboard with dark and light themes
- Visible, clickable numeric spinner arrows in Settings
- Local webcam processing with MediaPipe Face Landmarker and OpenCV fallback
- Conservative heuristic, personalized, and hybrid expression classifiers
- Optional AI analysis with explicit consent: Local Ollama or OpenAI
- Hybrid local + AI mode with rate-limited selected-frame analysis
- Cropped-face-only AI sending mode enabled by default
- Personalized calibration using local landmark/blendshape feature vectors
- Blue/orange/gray smoothed face rectangle groups
- Background tray mode with safe cooldown-controlled notifications
- Metadata-only local JSONL logs
- Local Statistics module with daily and weekly charts
- Optional local user profile name/email
- Optional daily summary email, disabled by default and text-only
- Offline demo guide and user manual
- PyInstaller and Inno Setup build support

## Download and install EmotionCam

Installer binaries are GitHub Releases artifacts. They are **not** committed into this
repository because generated `.exe` files are large binary files.

1. Go to
   [github.com/silviu-cristian/EmotionCam/releases](https://github.com/silviu-cristian/EmotionCam/releases).
2. Download the installer for the release you want.
3. Run the installer.
4. Launch EmotionCam from the Start Menu or optional desktop shortcut.
5. Allow Windows camera access for desktop apps if prompted.

SmartScreen note: the installer is unsigned, so Windows may display a warning.
Choose **More info > Run anyway** only if you trust the downloaded file.

EmotionCam installs per user under:

```text
%LOCALAPPDATA%\Programs\EmotionCam
```

Uninstall from **Windows Settings > Apps > Installed apps > EmotionCam**.

## Releases

### v1.0.0 - Local-only release

- Fully local visible-expression estimation.
- No external AI analysis.
- Best for privacy-focused and offline use.
- Download asset: `EmotionCam_Setup.exe`.

### v1.2.0-ai - Recommended AI-enabled release

- Keeps the local heuristic, personalized, and hybrid classifiers.
- Adds optional **Local Ollama AI** for AI-assisted visible-expression analysis
  on your own PC without OpenAI quota.
- Keeps optional **OpenAI External AI** for users who explicitly configure an
  API key and accept the cloud privacy tradeoff.
- Local Ollama mode only allows localhost/127.0.0.1 endpoints.
- Disabled by default, consent-gated, rate limited, and cropped-face-only by
  default.
- Download asset: `EmotionCam_Setup_v1.2.0_AI.exe`.

### v1.1.3-ai - Earlier AI-enabled hotfix

- Keeps the local heuristic, personalized, and hybrid classifiers.
- Adds optional **External AI Analysis** using OpenAI vision.
- External AI is disabled by default.
- Requires explicit consent and an OpenAI API key before any AI request can run.
- Sends one selected cropped face image by default, never every webcam frame.
- Can be switched to full-frame sending only by the user, with a warning that
  background details may be included.
- Falls back to local detection when the API key is missing, consent is missing,
  no face is found, the request times out, or the API fails.
- Includes the camera-opening hotfix for Windows webcam backend fallback.
- Includes clear Settings-dialog feedback for the External AI Test Connection
  button.
- Download asset: `EmotionCam_Setup_v1.1.3_AI.exe`.

### v1.1.2-ai - Earlier AI-enabled hotfix

- Added Windows webcam backend fallback for camera startup.
- Download asset: `EmotionCam_Setup_v1.1.2_AI.exe`.

### v1.1.1-ai - Earlier AI-enabled hotfix

- Includes the AI-mode activation hotfix so enabling External AI selects
  Hybrid local + AI mode automatically.
- Download asset: `EmotionCam_Setup_v1.1.1_AI.exe`.

### v1.1.0-ai - Earlier AI-enabled release

- First AI-enabled release.
- Kept available for history, but `v1.1.2-ai` is recommended.

## Which version should I download?

Choose **v1.0.0 Local-only** if privacy/offline use matters most.

Choose **v1.2.0-ai AI-enabled** if you want optional AI-assisted
visible-expression analysis. Choose **Local Ollama** inside Settings if you want
AI analysis without OpenAI quota or cloud upload. Choose **OpenAI** only if you
explicitly accept that selected cropped face images or frames may be sent to
OpenAI.

## Local Ollama AI setup

Local Ollama is the easiest no-OpenAI-quota AI backend. It runs on your own PC.
Install Ollama separately, then pull a vision model:

```powershell
ollama pull llava:7b
```

In EmotionCam:

1. Open **Settings**.
2. Find **Expression Detection Mode and AI Analysis**.
3. Set **API provider** to **Local Ollama (runs on this computer)**.
4. Keep **Local Ollama endpoint** as `http://localhost:11434`.
5. Keep **Local Ollama vision model** as `llava:7b`, unless you installed a
   different local vision model.
6. Click **Test Connection**.
7. Enable AI Analysis, accept the local Ollama consent checkbox, and select
   **Hybrid local + AI**.

## How to start the demo

1. Install EmotionCam or run it from source.
2. Open EmotionCam.
3. Select **Help > Start Demo Guide**.
4. Follow the local offline guide:
   [docs/START_DEMO_HERE.html](docs/START_DEMO_HERE.html).

The demo uses camera-free documentation screenshots with a generated avatar so
the public documentation does not expose a real webcam feed.

## Privacy design

> EmotionCam processes webcam frames locally. It stores only expression metadata
> and optional personalized calibration features locally. It does not identify
> people or upload webcam images.

Default behavior:

- No cloud analysis
- No telemetry or analytics
- No account system
- No identity recognition or face matching
- No automatic screenshots or video recording
- No saved webcam images or face images

AI behavior in v1.2.0-ai:

- Off by default.
- Requires both **Enable AI Analysis** and the consent checkbox.
- Local Ollama mode uses the local Ollama app on this PC and does not need an
  OpenAI key or OpenAI quota.
- OpenAI mode requires an OpenAI API key, billing/quota, and internet access.
- Uses cropped-face-only sending by default.
- Never logs images, base64 data, or API keys.
- Does not identify the user or infer sensitive traits.

Optional features:

- Metadata history logs can be disabled.
- Raw calibration images are saved only if the explicit debugging setting is
  enabled.
- Daily email summaries are off by default. If enabled, they use the network to
  send summary text only. They never include webcam frames or images.

## Local data paths

| Data | Path |
|---|---|
| Settings | `%LOCALAPPDATA%\EmotionCam\config.json` |
| Metadata logs | `%LOCALAPPDATA%\EmotionCam\logs\expression_history.jsonl` |
| Personalized expression profile | `%LOCALAPPDATA%\EmotionCam\profile\expression_profile.json` |
| User profile and email preferences | `%LOCALAPPDATA%\EmotionCam\profile\user_profile.json` |
| Optional debug calibration images | `%LOCALAPPDATA%\EmotionCam\profile\debug_images\` |

OpenAI API keys are not stored in `config.json`. When the user chooses secure
storage, EmotionCam uses Windows credential storage through `keyring`. If secure
storage is unavailable, the key can be used for the current app session only.

## Run from source

Requirements: Windows 10/11 and Python 3.11 or 3.12.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m app.main
```

Close other webcam apps if the camera cannot be opened.

## Build the app

```powershell
python build_exe.py
```

The packaged app folder is created at:

```text
release\app\EmotionCam\
```

Test `release\app\EmotionCam\EmotionCam.exe` before building the installer.

## Build the installer

Install Inno Setup 6, then run:

```powershell
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\emotioncam.iss
```

The installer is generated at:

```text
release\EmotionCam_Setup_v1.2.0_AI.exe
```

Do not commit the installer. Attach it to a GitHub Release.

## Regenerate documentation screenshots

```powershell
python docs\capture_docs_screenshots.py
python docs\generate_manual_formats.py
python docs\generate_manual_pdf.py
```

Screenshots are generated from local assets and a safe demo avatar, not a real
webcam feed.

## Test

```powershell
python -m pytest
python -m compileall -q app
```

## Architecture

- `app/main.py`: Qt application startup and icon/theme setup
- `app/ui/main_window.py`: dashboard, tray, settings, calibration, statistics
- `app/ui/settings_dialog.py`: settings, profile, email summary, calibration controls
- `app/ui/calibration_dialog.py`: guided local calibration flow
- `app/ui/statistics_window.py`: local metadata charts
- `app/core/camera_worker.py`: threaded webcam capture and analysis
- `app/core/face_detector.py`: MediaPipe/OpenCV local face detection
- `app/core/expression_backends.py`: shared classifier interface and local backends
- `app/core/ai_client.py`: OpenAI Responses API vision client and strict JSON validation
- `app/core/local_ai_client.py`: Local Ollama vision client for on-PC AI analysis
- `app/core/ai_agent_classifier.py`: optional AI provider selection, consent checks, fallback
- `app/core/ai_rate_limiter.py`: external AI request interval control
- `app/core/ai_settings.py`: secure API-key storage helpers
- `app/core/expression_features.py`: normalized expression feature extraction
- `app/core/statistics.py`: resilient log parsing and summaries
- `app/core/user_profile.py`: local optional name/email profile
- `app/core/email_summary.py`: optional text-only email summaries
- `installer/emotioncam.iss`: Inno Setup installer recipe

## Limitations

- Expression estimates are approximate and can be wrong.
- Lighting, blur, occlusion, distance, and head angle affect results.
- Personalized calibration helps but does not guarantee accuracy.
- The app is designed for one visible user and one local webcam.
- SMTP email summaries require user-supplied provider settings and network
  access.
- Local Ollama AI requires Ollama and a local vision model installed separately.
- OpenAI analysis requires network access, an OpenAI API key, quota, and
  explicit consent. AI can improve estimates, but it remains approximate and
  may be wrong.
