"""Build a Windows EmotionCam application folder with PyInstaller."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main() -> int:
    command = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--onedir",
        "--name",
        "EmotionCam",
        "--icon",
        str(ROOT / "app" / "assets" / "icon.ico"),
        "--add-data",
        f"{ROOT / 'app' / 'assets'};app/assets",
        "--add-data",
        f"{ROOT / 'docs'};docs",
        "--collect-data",
        "cv2",
        "--collect-data",
        "mediapipe",
        "--collect-binaries",
        "mediapipe",
        "--hidden-import",
        "mediapipe.tasks.python.vision.face_landmarker",
        str(ROOT / "app" / "main.py"),
    ]
    return subprocess.call(command, cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
