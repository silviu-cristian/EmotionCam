from pathlib import Path
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]


def test_icon_assets_and_build_wiring_exist():
    assert (ROOT / "app" / "assets" / "icon.png").stat().st_size > 0
    assert (ROOT / "app" / "assets" / "icon.ico").stat().st_size > 0
    assert "icon.ico" in (ROOT / "build_exe.py").read_text(encoding="utf-8")
    installer = (ROOT / "installer" / "emotioncam.iss").read_text(encoding="utf-8")
    assert "SetupIconFile" in installer
    assert "IconFilename" in installer
    with Image.open(ROOT / "app" / "assets" / "icon.ico") as icon:
        assert set(icon.info["sizes"]) == {
            (16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)
        }
