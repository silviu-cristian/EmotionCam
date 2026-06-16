# EmotionCam Screenshot Checklist

The screenshots in this folder are generated with:

```powershell
python docs\capture_docs_screenshots.py
```

They are camera-free screen examples using a demo avatar, not real webcam
frames. This keeps the documentation safe for public release.

| Filename | Screen | What should be visible |
|---|---|---|
| `01_startup_screen.png` | Startup | Icon, privacy notice, logging checkbox, Start Camera, Settings, Exit |
| `02_main_dashboard_dark_theme.png` | Dashboard dark | Demo avatar, positive estimate, blue rectangle, dashboard controls |
| `03_main_dashboard_light_theme.png` | Dashboard light | Same dashboard in light theme |
| `04_camera_stopped_screen.png` | Stopped camera | Black preview with `Camera stopped` |
| `05_settings_general_dark.png` | Settings dark | Appearance, profile, email, detection sections |
| `06_settings_general_light.png` | Settings light | Readable light theme settings |
| `07_settings_numeric_arrows.png` | Numeric controls | Visible spinner arrow buttons |
| `08_theme_toggle.png` | Theme toggle | Dark / Light theme control |
| `09_calibration_overview.png` | Calibration overview | Dropdown, preview, example card, controls |
| `10_calibration_expression_dropdown.png` | Calibration dropdown | Selected expression target |
| `11_calibration_example_graphic.png` | Example graphic | Local expression guide |
| `12_calibration_match_checkmark.png` | Match helper | Match helper and progress/counts |
| `13_statistics_overview.png` | Statistics overview | Summary cards and charts |
| `14_statistics_today_balance.png` | Today balance | Positive/neutral/serious balance |
| `15_statistics_weekly_balance.png` | Weekly balance | Seven-day chart |
| `16_statistics_expression_counts.png` | Expression counts | Counts by visible-expression label |
| `17_user_profile_settings.png` | User profile | Optional name/email fields |
| `18_daily_email_summary_settings.png` | Email summary | Disabled-by-default email settings |
| `19_background_mode_tray.png` | Background mode | Tray menu behavior explanation |
| `20_logs_folder.png` | Logs folder | Metadata-only logs explanation |

## Rules

- Do not use internet images.
- Do not expose a real webcam feed.
- Do not include private names, email addresses, logs, or profile data.
- Regenerate screenshots before publishing a release if UI layout changes.
