# Start the EmotionCam Demo Here

This is the fastest guide for presenting EmotionCam.

## Quick Start

1. Open EmotionCam.
2. Select **Help > Start Demo Guide** to reopen this page.
3. Keep raw calibration image storage off.
4. Do not type or display a real API key during a public demo.
5. If demonstrating Local Ollama, install Ollama and run `ollama pull llava:7b`
   before demo day.
6. Use the scripted flow below.

## Demo Flow

1. Show the final smiling camera-lens icon and startup privacy notice.
2. Start the camera and explain that estimates are visible-expression estimates,
   not true-emotion claims.
3. Smile and point out the blue positive-group rectangle.
4. Stop the camera and show the black `Camera stopped` preview.
5. Open Settings and demonstrate the visible numeric up/down arrows.
6. Switch to Light theme, save, and optionally switch back to Dark.
7. Show **Expression Detection Mode and AI Analysis**.
8. Choose **Local Ollama** and explain that it runs on this computer and does
   not need OpenAI quota.
9. Show endpoint `http://localhost:11434`, model `llava:7b`, and
   **Test Connection**.
10. Optionally switch to **OpenAI** and explain that it requires consent, an API
   key, quota, and internet access.
11. Switch to **Hybrid local + AI** and show the dashboard AI status/fallback
   behavior if no provider is ready.
12. Disable AI again or return to local/hybrid local mode.
13. Open calibration.
14. Select an expression from the dropdown.
15. Show the local example graphic and match helper.
16. Click **Start Capture**, then show sample progress and quality.
17. Use **Re-capture**, **Previous**, and **Next**.
18. Finish calibration and return to the dashboard.
19. Open Statistics and show local daily/weekly charts.
20. Show optional User Profile and disabled-by-default Daily Email Summary.
21. Run in background and explain tray behavior.
22. Open logs and close the app.

## Demo Screens

- `screenshots/01_startup_screen.png`
- `screenshots/02_main_dashboard_dark_theme.png`
- `screenshots/03_main_dashboard_light_theme.png`
- `screenshots/04_camera_stopped_screen.png`
- `screenshots/07_settings_numeric_arrows.png`
- `screenshots/09_calibration_overview.png`
- `screenshots/13_statistics_overview.png`
- `screenshots/19_background_mode_tray.png`
- `screenshots/23_external_ai_settings_disabled.png`
- `screenshots/26_dashboard_ai_status.png`

## Demo-Day Tips

- Close Camera, Teams, Zoom, browsers, and other webcam apps.
- Allow Windows desktop-app camera access.
- Use steady front lighting.
- Do not force negative expressions for a popup demo; explain the behavior.
- Use the generated documentation screenshots when you need a camera-free,
  public-safe version of the demo.
- Never show a real OpenAI API key. Use the masked placeholder screenshots for
  the AI portion of the demo.
- If Ollama is not installed, use the Test Connection failure as a clean
  teaching moment: "The app is ready, but the local AI runtime/model is not
  installed yet."
