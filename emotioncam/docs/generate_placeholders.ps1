param([string]$OutputDir = "$PSScriptRoot\screenshots")

Add-Type -AssemblyName System.Drawing
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$items = @(
  @("01_startup_screen.png", "Startup Screen", "Privacy notice, logging choice, Start Camera, Settings, Exit"),
  @("02_main_dashboard_dark_theme.png", "Main Dashboard - Dark Theme", "Live preview, expression estimate, timeline, dashboard controls"),
  @("03_main_dashboard_light_theme.png", "Main Dashboard - Light Theme", "Same dashboard after Settings > Theme > Light"),
  @("04_settings_numeric_arrows_dark.png", "Settings Arrows - Dark Theme", "Visible and clickable numeric up/down spinner arrows"),
  @("05_settings_numeric_arrows_light.png", "Settings Arrows - Light Theme", "Visible and clickable arrows with light-theme contrast"),
  @("06_settings_theme_toggle.png", "Settings Theme Selector", "Appearance > Theme: Dark / Light"),
  @("07_calibration_expression_dropdown.png", "Calibration Expression Dropdown", "Choose the target expression directly"),
  @("08_calibration_example_graphic.png", "Calibration Example Graphic", "Bundled offline visual guide for the target"),
  @("09_calibration_match_checkmark.png", "Calibration Match Helper", "Permissive match indicator; capture remains allowed"),
  @("10_calibration_capture_progress.png", "Calibration Capture Progress", "Progress, valid/rejected samples, and quality"),
  @("11_calibration_recapture_button.png", "Calibration Re-capture", "Re-capture replaces the selected target batch"),
  @("12_calibration_previous_next_buttons.png", "Calibration Navigation", "Previous, Start Capture, Re-capture, Next, Finish; no Skip"),
  @("13_camera_stopped_screen.png", "Camera Stopped", "Black preview with centered Camera stopped text"),
  @("14_background_mode_tray.png", "Background Mode Tray", "Show EmotionCam, Stop Camera, Exit"),
  @("15_logs_folder.png", "Local Logs Folder", "Metadata-only expression_history.jsonl"),
  @("16_statistics_overview.png", "Statistics Overview", "Local summary cards and charts"),
  @("17_statistics_today_balance.png", "Today's Expression Balance", "Positive, neutral, and serious-expression percentages"),
  @("18_statistics_weekly_balance.png", "Weekly Expression Balance", "Last-7-days stacked expression-group chart"),
  @("19_statistics_expression_counts.png", "Expression Counts", "Selected-day counts by visible-expression label"),
  @("20_user_profile_settings.png", "User Profile Settings", "Optional local user name and email"),
  @("21_daily_email_summary_settings.png", "Daily Email Summary Settings", "Explicit opt-in, delivery method, SMTP, TLS, and send time"),
  @("22_test_email_button.png", "Test Email Control", "Send Test Email or Open Test Draft")
)

foreach ($item in $items) {
  $bitmap = [System.Drawing.Bitmap]::new(1280, 720)
  $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
  $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
  $graphics.Clear([System.Drawing.Color]::FromArgb(17, 20, 27))
  $panel = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(25, 30, 40))
  $blue = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(40, 120, 215))
  $white = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(240, 244, 250))
  $muted = [System.Drawing.SolidBrush]::new([System.Drawing.Color]::FromArgb(170, 184, 205))
  $border = [System.Drawing.Pen]::new([System.Drawing.Color]::FromArgb(72, 87, 112), 3)
  $graphics.FillRectangle($panel, 52, 52, 1176, 616)
  $graphics.DrawRectangle($border, 52, 52, 1176, 616)
  $graphics.FillRectangle($blue, 52, 52, 1176, 12)
  $titleFont = [System.Drawing.Font]::new("Segoe UI", 28, [System.Drawing.FontStyle]::Bold)
  $bodyFont = [System.Drawing.Font]::new("Segoe UI", 16)
  $labelFont = [System.Drawing.Font]::new("Segoe UI", 12, [System.Drawing.FontStyle]::Bold)
  $graphics.DrawString("SCREENSHOT PLACEHOLDER", $labelFont, $blue, 90, 100)
  $graphics.DrawString($item[1], $titleFont, $white, 90, 155)
  $graphics.DrawString($item[2], $bodyFont, $muted, 94, 235)
  $graphics.DrawRectangle($border, 94, 315, 1088, 225)
  $graphics.DrawString("Replace this local placeholder with the real EmotionCam screen.", $bodyFont, $muted, 170, 400)
  $graphics.DrawString($item[0], $labelFont, $white, 94, 590)
  $path = Join-Path $OutputDir $item[0]
  $bitmap.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
  $titleFont.Dispose(); $bodyFont.Dispose(); $labelFont.Dispose()
  $panel.Dispose(); $blue.Dispose(); $white.Dispose(); $muted.Dispose(); $border.Dispose()
  $graphics.Dispose(); $bitmap.Dispose()
}
