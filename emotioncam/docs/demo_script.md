# EmotionCam Presenter Script

Use this script for a live or recorded demo. The screenshots are camera-free
screen examples generated from local assets and a demo avatar.

| Step | What to say | What to click/do | Expected result | Screenshot |
|---:|---|---|---|---|
| 1 | "EmotionCam is a Windows app for local visible-expression estimates." | Launch EmotionCam. | Startup screen appears with final icon. | `screenshots/01_startup_screen.png` |
| 2 | "It estimates visible expressions, not true emotions." | Point to privacy notice. | Local-processing explanation is visible. | `screenshots/01_startup_screen.png` |
| 3 | "I will start local camera processing." | Click Start Camera. | Dashboard opens. | `screenshots/02_main_dashboard_dark_theme.png` |
| 4 | "A positive group uses a blue rectangle." | Smile or use the screenshot. | Blue positive rectangle and smile estimate. | `screenshots/02_main_dashboard_dark_theme.png` |
| 5 | "Stopping clears the last frame." | Click Stop Camera. | Black `Camera stopped` preview. | `screenshots/04_camera_stopped_screen.png` |
| 6 | "Settings are organized by appearance, profile, email, detection, optional external AI, calibration, background, privacy, and debug options." | Open Settings. | Settings dialog. | `screenshots/05_settings_general_dark.png` |
| 7 | "Numeric values can be typed or changed with visible arrows." | Click spinner arrows. | Value changes. | `screenshots/07_settings_numeric_arrows.png` |
| 8 | "The app supports dark and light themes." | Select Theme: Light and Save. | Light dashboard. | `screenshots/03_main_dashboard_light_theme.png` |
| 9 | "External AI is off by default." | Show External AI settings. | Enable checkbox is off. | `screenshots/23_external_ai_settings_disabled.png` |
| 10 | "It requires consent before any selected image can leave the app." | Point to consent warning. | Consent warning is visible. | `screenshots/24_external_ai_consent_warning.png` |
| 11 | "It also requires an OpenAI API key. Do not show a real key in public demos." | Point to API key and Test Connection. | Key field is masked; Test Connection is visible. | `screenshots/25_external_ai_settings_enabled_no_key.png` |
| 12 | "Hybrid local + AI keeps local detection running and uses AI only at controlled intervals." | Select Hybrid local + AI. | Dashboard can show AI status/fallback. | `screenshots/27_dashboard_hybrid_local_ai_mode.png` |
| 13 | "If no key is configured, the app falls back to local detection." | Return to dashboard. | AI status shows missing key/fallback. | `screenshots/26_dashboard_ai_status.png` |
| 14 | "Calibration learns local feature samples from your face." | Open calibration. | Unified calibration screen. | `screenshots/09_calibration_overview.png` |
| 15 | "The target expression is chosen from this dropdown." | Select a target. | Prompt and graphic update. | `screenshots/10_calibration_expression_dropdown.png` |
| 16 | "The graphic is a local guide; it does not need to be copied perfectly." | Point to graphic. | Example graphic is visible. | `screenshots/11_calibration_example_graphic.png` |
| 17 | "The match helper is guidance only and never blocks capture." | Show match helper. | Helper/checkmark is visible. | `screenshots/12_calibration_match_checkmark.png` |
| 18 | "Capture starts only after Start Capture." | Click Start Capture. | Progress and counts update. | `screenshots/09_calibration_overview.png` |
| 19 | "Re-capture replaces this target's previous batch." | Click Re-capture. | Capture state resets for that target. | `screenshots/12_calibration_match_checkmark.png` |
| 20 | "Statistics are generated from metadata logs only." | Click Statistics. | Local charts and cards. | `screenshots/13_statistics_overview.png` |
| 21 | "Daily and weekly summaries are approximate visible-expression summaries." | Point to charts. | Balance, weekly chart, counts. | `screenshots/14_statistics_today_balance.png`, `screenshots/15_statistics_weekly_balance.png`, `screenshots/16_statistics_expression_counts.png` |
| 22 | "The optional name can personalize safe messages." | Show User Profile settings. | Optional name/email fields. | `screenshots/17_user_profile_settings.png` |
| 23 | "Email summaries are off by default and send text only." | Show email settings. | Opt-in email settings. | `screenshots/18_daily_email_summary_settings.png` |
| 24 | "Background mode keeps analysis active in the tray. External AI still respects consent, key, and rate limits." | Run in background. | Tray behavior explanation. | `screenshots/19_background_mode_tray.png` |
| 25 | "Logs are metadata-only, including AI status fields but no images or keys." | Click Open Logs. | Logs folder explanation. | `screenshots/20_logs_folder.png` |
| 26 | "Exit releases the camera and closes EmotionCam." | Click Exit. | App closes. | None |

## Popup Note

Do not force a negative expression just to trigger a notification. Explain that
stable serious-expression estimates can show cooldown-controlled supportive
messages, and later positive shifts can show recovery messages.
