# EmotionCam

![EmotionCam icon](emotioncam/app/assets/icon.png)

EmotionCam is a Windows desktop app that estimates visible facial expressions
from a webcam feed. It is built with Python, PySide6, OpenCV, and MediaPipe, and
it is designed for one person using a built-in laptop webcam. Version 1.2.0 adds
optional AI analysis with two providers: OpenAI cloud analysis or Local Ollama
analysis running on your own PC. The app remains local-first and AI is off until
the user enables it and accepts the warning.

EmotionCam estimates visible expressions only. It does not know true emotions,
diagnose mood or mental state, identify people, or perform face matching.

![EmotionCam dashboard](emotioncam/docs/screenshots/02_main_dashboard_dark_theme.png)

## Download and install EmotionCam

Installer binaries are distributed through GitHub Releases, not committed into
the source repository.

1. Open the repository Releases page:
   [github.com/silviu-cristian/EmotionCam/releases](https://github.com/silviu-cristian/EmotionCam/releases)
2. Download the installer for the version you want.
3. Double-click the installer and follow the prompts.
4. Launch EmotionCam from the Start Menu or the optional desktop shortcut.
5. If Windows SmartScreen appears because the app is unsigned, choose
   **More info > Run anyway** only if you trust the downloaded file.

The app installs per user under:

```text
%LOCALAPPDATA%\Programs\EmotionCam
```

Uninstall it from **Windows Settings > Apps > Installed apps > EmotionCam**.

## Releases

### v1.0.0 - Local-only release

- Fully local visible-expression estimation.
- No external AI analysis.
- Best for privacy-focused or offline use.
- Installer asset: `EmotionCam_Setup.exe`.

### v1.2.0-ai - Recommended AI-enabled release

- Keeps all local detection features.
- Adds **Local Ollama AI** as an optional provider for AI-assisted visible
  expression estimates without OpenAI credits.
- Still supports optional OpenAI vision analysis for users who configure a valid
  API key and accept the cloud privacy tradeoff.
- Local Ollama mode is restricted to localhost/127.0.0.1 endpoints to avoid
  accidental remote uploads.
- Disabled by default, rate limited, and cropped-face-only by default.
- Installer asset: `EmotionCam_Setup_v1.2.0_AI.exe`.

### v1.1.3-ai - Earlier AI-enabled hotfix

- Keeps all local detection features.
- Adds optional **External AI Analysis** using OpenAI vision through the
  Responses API.
- Disabled by default.
- Requires explicit consent and an OpenAI API key.
- Can send cropped face images by default, or selected full frames only if the
  user changes that setting.
- Falls back to local detection when no key, no consent, no face, timeout, or
  API error occurs.
- Includes the camera-opening hotfix for Windows webcam backend fallback.
- Includes clear Settings-dialog feedback for the External AI Test Connection
  button.
- Installer asset: `EmotionCam_Setup_v1.1.3_AI.exe`.

### v1.1.2-ai - Earlier AI-enabled hotfix

- Added Windows webcam backend fallback for camera startup.
- Installer asset: `EmotionCam_Setup_v1.1.2_AI.exe`.

### v1.1.1-ai - Earlier AI-enabled hotfix

- Includes the AI-mode activation hotfix so enabling External AI selects
  Hybrid local + AI mode automatically.
- Installer asset: `EmotionCam_Setup_v1.1.1_AI.exe`.

### v1.1.0-ai - Earlier AI-enabled release

- First AI-enabled release.
- Kept available for history, but `v1.1.2-ai` is recommended.

## Which version should I download?

Choose **v1.0.0 Local-only** if privacy/offline use matters most and you do not
want any external AI option in the app.

Choose **v1.2.0-ai AI-enabled** if you want the same local app plus optional
AI-assisted visible-expression analysis. Use **Local Ollama** if you want AI
analysis without OpenAI quota. Use **OpenAI** only if you explicitly accept the
cloud privacy tradeoff and have a working API key.

## Use Local Ollama AI

Local Ollama mode needs the Ollama desktop/runtime installed separately.
After installing Ollama, open PowerShell and pull a vision model:

```powershell
ollama pull llava:7b
```

Then in EmotionCam:

1. Open **Settings**.
2. In **Expression Detection Mode and AI Analysis**, choose
   **Local Ollama (runs on this computer)**.
3. Keep endpoint `http://localhost:11434`.
4. Keep model `llava:7b`, or enter another local vision model you installed.
5. Click **Test Connection**.
6. Enable AI Analysis, accept the local Ollama consent checkbox, and choose
   **Hybrid local + AI**.

## Project files

The application source is in the [`emotioncam/`](emotioncam/) folder.

Useful links:

- [Main project README](emotioncam/README.md)
- [User manual](emotioncam/docs/user_manual.html)
- [Start demo guide](emotioncam/docs/START_DEMO_HERE.html)
- [Presenter script](emotioncam/docs/demo_script.md)
- [Screenshot checklist](emotioncam/docs/screenshot_checklist.md)

## Privacy summary

- Webcam processing is local by default.
- AI analysis is off by default and never sends images without explicit
  consent. Local Ollama mode sends selected images only to the local Ollama
  service on this computer. OpenAI mode sends selected images to OpenAI and
  requires an API key.
- No telemetry, analytics, accounts, identity recognition, or face matching.
- Logs contain expression metadata only, never webcam frames.
- Calibration stores local feature data and labels.
- Optional daily email summaries are off by default and send text only.
- Raw calibration images are saved only if the explicit debugging option is
  enabled.

## Run from source

```powershell
cd emotioncam
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m app.main
```

## Test

```powershell
cd emotioncam
python -m pytest
```

## Build a release installer

```powershell
cd emotioncam
python build_exe.py
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\emotioncam.iss
```

The packaged app folder is generated at `emotioncam\release\app\EmotionCam`.
The AI-enabled installer is generated at:

```text
emotioncam\release\EmotionCam_Setup_v1.2.0_AI.exe
```

Do not commit the generated installer. Attach it to a GitHub Release instead.
