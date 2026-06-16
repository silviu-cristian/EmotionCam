# EmotionCam

![EmotionCam icon](emotioncam/app/assets/icon.png)

EmotionCam is a Windows desktop app that estimates visible facial expressions
from a local webcam feed. It is built with Python, PySide6, OpenCV, and
MediaPipe, and it is designed for one person using a built-in laptop webcam.

EmotionCam estimates visible expressions only. It does not know true emotions,
diagnose mood or mental state, identify people, or perform face matching.

![EmotionCam dashboard](emotioncam/docs/screenshots/02_main_dashboard_dark_theme.png)

## Download and install EmotionCam

Installer binaries are distributed through GitHub Releases, not committed into
the source repository.

1. Open the repository Releases page:
   [github.com/silviu-cristian/EmotionCam/releases](https://github.com/silviu-cristian/EmotionCam/releases)
2. Download `EmotionCam_Setup.exe` from the latest release.
3. Double-click the installer and follow the prompts.
4. Launch EmotionCam from the Start Menu or the optional desktop shortcut.
5. If Windows SmartScreen appears because the app is unsigned, choose
   **More info > Run anyway** only if you trust the downloaded file.

The app installs per user under:

```text
%LOCALAPPDATA%\Programs\EmotionCam
```

Uninstall it from **Windows Settings > Apps > Installed apps > EmotionCam**.

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
The installer is generated at:

```text
emotioncam\release\EmotionCam_Setup.exe
```

Do not commit the generated installer. Attach it to a GitHub Release instead.
