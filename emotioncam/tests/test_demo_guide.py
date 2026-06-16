from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_demo_guide_is_packaged_and_wired():
    assert (ROOT / "docs" / "START_DEMO_HERE.html").exists()
    main_window = (ROOT / "app" / "ui" / "main_window.py").read_text(encoding="utf-8")
    assert "Start Demo Guide" in main_window
    assert "START_DEMO_HERE.html" in main_window
    assert "'docs'};docs" in (ROOT / "build_exe.py").read_text(encoding="utf-8")


def test_release_docs_use_current_screenshots_and_releases():
    required = {
        "01_startup_screen.png",
        "02_main_dashboard_dark_theme.png",
        "03_main_dashboard_light_theme.png",
        "04_camera_stopped_screen.png",
        "05_settings_general_dark.png",
        "06_settings_general_light.png",
        "07_settings_numeric_arrows.png",
        "08_theme_toggle.png",
        "09_calibration_overview.png",
        "10_calibration_expression_dropdown.png",
        "11_calibration_example_graphic.png",
        "12_calibration_match_checkmark.png",
        "13_statistics_overview.png",
        "14_statistics_today_balance.png",
        "15_statistics_weekly_balance.png",
        "16_statistics_expression_counts.png",
        "17_user_profile_settings.png",
        "18_daily_email_summary_settings.png",
        "19_background_mode_tray.png",
        "20_logs_folder.png",
        "23_external_ai_settings_disabled.png",
        "24_external_ai_consent_warning.png",
        "25_external_ai_settings_enabled_no_key.png",
        "26_dashboard_ai_status.png",
        "27_dashboard_hybrid_local_ai_mode.png",
    }
    screenshots = {path.name for path in (ROOT / "docs" / "screenshots").glob("*.png")}
    assert required <= screenshots
    manual = (ROOT / "docs" / "user_manual.md").read_text(encoding="utf-8")
    demo = (ROOT / "docs" / "demo_script.md").read_text(encoding="utf-8")
    for old_name in ("16_statistics_window.png", "17_user_profile_email_settings.png", "EmotionCam_User_Manual_updated.pdf"):
        assert old_name not in manual
        assert old_name not in demo
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "GitHub Releases" in readme
    assert "EmotionCam_Setup_v1.1.3_AI.exe" in readme


def test_docs_do_not_contain_real_api_keys():
    docs = [
        ROOT / "README.md",
        ROOT / "docs" / "user_manual.md",
        ROOT / "docs" / "user_manual.html",
        ROOT / "docs" / "START_DEMO_HERE.md",
        ROOT / "docs" / "START_DEMO_HERE.html",
        ROOT / "docs" / "demo_script.md",
    ]
    text = "\n".join(path.read_text(encoding="utf-8") for path in docs)
    assert "sk-test" not in text
    assert "sk-proj-" not in text
    assert "sk-" not in text
