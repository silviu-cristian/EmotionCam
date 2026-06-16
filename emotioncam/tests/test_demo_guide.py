from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_demo_guide_is_packaged_and_wired():
    assert (ROOT / "docs" / "START_DEMO_HERE.html").exists()
    main_window = (ROOT / "app" / "ui" / "main_window.py").read_text(encoding="utf-8")
    assert "Start Demo Guide" in main_window
    assert "START_DEMO_HERE.html" in main_window
    assert "'docs'};docs" in (ROOT / "build_exe.py").read_text(encoding="utf-8")
