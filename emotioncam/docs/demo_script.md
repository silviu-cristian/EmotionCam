# EmotionCam Presenter Script

Open **Help > Start Demo Guide** before presenting. Use good lighting, close other webcam apps, and keep raw calibration image storage off.

| Step | Presenter says | Presenter clicks/does | Expected screen | Screenshot |
|---:|---|---|---|---|
| 1 | "EmotionCam is a local Windows visible-expression estimator." | Launch EmotionCam. | Startup screen and simplified lens icon. | `screenshots/01_startup_screen.png` |
| 2 | "The same icon is used for the app, taskbar, tray, installer, and shortcuts." | Point to icon. | Consistent branding. | `screenshots/01_startup_screen.png` |
| 3 | "Frames stay local; metadata history can be disabled before starting." | Point to privacy text and logging checkbox. | Camera remains stopped. | `screenshots/01_startup_screen.png` |
| 4 | "I will start the built-in camera." | Click Start Camera. | Dark dashboard and live preview. | `screenshots/02_main_dashboard_dark_theme.png` |
| 5 | "This is a smoothed visible-expression estimate, not a true-emotion claim." | Hold neutral, then smile. | Estimate updates; positive group gives blue rectangle. | `screenshots/02_main_dashboard_dark_theme.png` |
| 6 | "Settings control detection, display, privacy, calibration, and themes." | Click Settings. | Settings dialog. | `screenshots/04_settings_numeric_arrows_dark.png` |
| 7 | "Every numeric value can be typed or changed with these visible arrows." | Click spinner up/down arrows and type a value. | Numeric value changes. | `screenshots/04_settings_numeric_arrows_dark.png` |
| 8 | "EmotionCam includes an app-wide light theme." | Set Theme to Light; click Save. | Dashboard changes to light. | `screenshots/03_main_dashboard_light_theme.png` |
| 9 | "The selected theme is saved locally." | Optionally set Dark and Save. | Dark theme returns. | `screenshots/06_settings_theme_toggle.png` |
| 10 | "Calibration learns local normalized facial-movement features." | Open calibration. | Unified calibration dialog. | `screenshots/07_calibration_expression_dropdown.png` |
| 11 | "The target is selected directly here." | Choose an expression in dropdown. | Target/prompt updates. | `screenshots/07_calibration_expression_dropdown.png` |
| 12 | "Each target has an offline example graphic." | Point to graphic. | Local visual guide. | `screenshots/08_calibration_example_graphic.png` |
| 13 | "The match helper is permissive and never blocks capture." | Perform roughly matching expression. | Match helper may appear. | `screenshots/09_calibration_match_checkmark.png` |
| 14 | "Capture begins only when I click Start Capture." | Click Start Capture. | Progress begins. | `screenshots/10_calibration_capture_progress.png` |
| 15 | "Only accepted feature samples count." | Point to progress/counts/quality. | Counts update. | `screenshots/10_calibration_capture_progress.png` |
| 16 | "Re-capture replaces this target's prior batch." | Click Re-capture. | Target returns to ready state. | `screenshots/11_calibration_recapture_button.png` |
| 17 | "I can move both directions; Skip and the separate unknown-label flow were removed." | Click Previous and Next. | Target changes both ways. | `screenshots/12_calibration_previous_next_buttons.png` |
| 18 | "Finish saves the local profile." | Capture valid batch; click Finish. | Completion message. | `screenshots/10_calibration_capture_progress.png` |
| 19 | "Hybrid mode uses personalized results when confident and falls back safely." | Return to dashboard. | Hybrid/profile active status. | `screenshots/02_main_dashboard_dark_theme.png` |
| 20 | "Background mode keeps processing local." | Click Run in background; open tray menu. | Tray menu. | `screenshots/14_background_mode_tray.png` |
| 21 | "Statistics are generated locally from metadata logs only." | Restore app; click Statistics. | Selected-day cards and local charts. | `screenshots/16_statistics_overview.png` |
| 22 | "This is today's balance, the weekly balance, and counts by visible-expression label." | Point to the charts. | Three requested chart views. | `screenshots/17_statistics_today_balance.png`, `screenshots/18_statistics_weekly_balance.png`, `screenshots/19_statistics_expression_counts.png` |
| 23 | "The optional local name personalizes safe messages." | Open Settings, enter a name, save, and demonstrate a later message. | Personalized message wording. | `screenshots/20_user_profile_settings.png` |
| 24 | "Email is optional and off by default. Only summary text is sent, never frames." | Enter email; show delivery method and Send Test control. | Explicit opt-in settings. | `screenshots/21_daily_email_summary_settings.png`, `screenshots/22_test_email_button.png` |
| 25 | "Logs contain metadata only, never frames." | Click Open Logs. | Logs folder. | `screenshots/15_logs_folder.png` |
| 26 | "Exit releases the camera and closes the app fully." | Click Exit. | App closes. | None |

## Popup Explanation

Do not force a negative expression for a demo. Explain that stable negative groups can show a cooldown-controlled supportive notification, and a later positive shift can show a recovery notification. These remain approximate visible-expression estimates.
