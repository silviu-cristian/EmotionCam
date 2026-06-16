"""Generate public-safe EmotionCam documentation screenshots.

The generated images are camera-free screen examples for docs and demos. They
use the official local icon and a clean demo avatar instead of webcam frames, so
the screenshots are repeatable and safe to publish.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "screenshots"
ICON = ROOT / "app" / "assets" / "icon.png"
W, H = 1280, 800


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = ["segoeuib.ttf" if bold else "segoeui.ttf", "arialbd.ttf" if bold else "arial.ttf"]
    for name in names:
        path = Path("C:/Windows/Fonts") / name
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


F_TITLE = font(34, True)
F_H1 = font(25, True)
F_H2 = font(18, True)
F_BODY = font(16)
F_SMALL = font(13)
F_TINY = font(11)


THEMES = {
    "dark": {
        "bg": "#111620", "panel": "#1b2432", "panel2": "#141b26",
        "text": "#f3f7ff", "muted": "#aab7c8", "line": "#34445e",
        "input": "#0f1520", "button": "#26344a", "primary": "#2878d7",
    },
    "light": {
        "bg": "#f3f6fa", "panel": "#ffffff", "panel2": "#eef3f8",
        "text": "#182236", "muted": "#5d6b80", "line": "#d3dce8",
        "input": "#ffffff", "button": "#e8eef6", "primary": "#2878d7",
    },
}


def draw_wrapped(draw: ImageDraw.ImageDraw, text: str, xy: tuple[int, int], width: int, fill: str, fnt=F_BODY, spacing: int = 4) -> int:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=fnt) <= width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    x, y = xy
    for line in lines:
        draw.text((x, y), line, fill=fill, font=fnt)
        y += fnt.size + spacing
    return y


def base(theme: str = "dark") -> tuple[Image.Image, ImageDraw.ImageDraw, dict]:
    colors = THEMES[theme]
    image = Image.new("RGB", (W, H), colors["bg"])
    return image, ImageDraw.Draw(image), colors


def panel(draw, box, colors, radius=18):
    draw.rounded_rectangle(box, radius=radius, fill=colors["panel"], outline=colors["line"], width=2)


def button(draw, box, label, colors, primary=False):
    fill = colors["primary"] if primary else colors["button"]
    text = "#ffffff" if primary or colors["bg"] == "#111620" else colors["text"]
    draw.rounded_rectangle(box, radius=9, fill=fill, outline=colors["line"])
    tw = draw.textlength(label, font=F_BODY)
    draw.text((box[0] + (box[2] - box[0] - tw) / 2, box[1] + 10), label, fill=text, font=F_BODY)


def icon(draw, x, y, size):
    src = Image.open(ICON).convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    draw._image.paste(src, (x, y), src)


def save(image: Image.Image, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    image.save(OUT / name, quality=95)


def avatar(draw, box, group="positive"):
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=20, fill="#0b1018", outline="#27364d", width=3)
    face_box = (x1 + 255, y1 + 85, x1 + 590, y1 + 420)
    draw.ellipse(face_box, fill="#202b3d", outline="#2a3a55", width=3)
    accent = {"positive": "#3d8ee6", "negative": "#e68a3d", "neutral": "#9aa5b5"}[group]
    draw.rounded_rectangle((x1 + 225, y1 + 55, x1 + 620, y1 + 450), radius=16, outline=accent, width=7)
    cx, cy = x1 + 422, y1 + 255
    draw.arc((cx - 95, cy + 20, cx + 95, cy + 115), start=20, end=160, fill="#70d7ff", width=10)
    draw.arc((cx - 95, cy - 70, cx - 25, cy - 15), start=200, end=340, fill="#70d7ff", width=9)
    draw.arc((cx + 25, cy - 70, cx + 95, cy - 15), start=200, end=340, fill="#70d7ff", width=9)
    draw.text((x1 + 270, y2 - 55), "Demo avatar preview - no webcam frame", fill="#dce8f8", font=F_BODY)


def startup():
    image, draw, c = base("dark")
    icon(draw, 92, 82, 150)
    draw.text((275, 94), "EmotionCam", fill=c["text"], font=F_TITLE)
    draw.text((278, 142), "Local visible-expression estimates", fill=c["muted"], font=F_H2)
    panel(draw, (85, 260, 1195, 610), c)
    y = draw_wrapped(draw, "EmotionCam processes webcam frames locally. It stores only expression metadata in local logs. It does not save images, identify people, or upload data.", (125, 295), 1000, c["text"], F_H2)
    y = draw_wrapped(draw, "Visible expressions are approximate estimates, not guaranteed true emotions or mental-state diagnoses.", (125, y + 24), 1000, c["muted"])
    draw.rectangle((126, y + 34, 146, y + 54), fill=c["primary"], outline=c["line"])
    draw.text((160, y + 29), "Save local expression metadata history", fill=c["text"], font=F_BODY)
    draw_wrapped(draw, "Only timestamps, expression labels, confidence scores, and status metadata are saved. EmotionCam never saves webcam images, video frames, or face images.", (160, y + 60), 850, c["muted"], F_SMALL)
    button(draw, (470, 660, 650, 710), "Start Camera", c, True)
    button(draw, (670, 660, 830, 710), "Settings", c)
    button(draw, (850, 660, 1010, 710), "Exit", c)
    save(image, "01_startup_screen.png")


def dashboard(theme, name, stopped=False):
    image, draw, c = base(theme)
    icon(draw, 26, 22, 50)
    draw.text((90, 27), "EmotionCam", fill=c["text"], font=F_H1)
    draw.text((400, 42), "LOCAL PROCESSING | NO IMAGE SAVING | NO IDENTITY RECOGNITION", fill=c["muted"], font=F_SMALL)
    panel(draw, (18, 86, 918, 720), c)
    panel(draw, (932, 86, 1262, 720), c)
    if stopped:
        draw.rounded_rectangle((80, 165, 860, 640), radius=24, fill="#000000", outline=c["line"], width=2)
        draw.text((410, 380), "Camera stopped", fill="#ffffff", font=F_H1)
        expression, group, conf, msg = "Camera stopped", "--", "--", "No frames are being analyzed."
    else:
        avatar(draw, (80, 150, 860, 650), "positive")
        expression, group, conf, msg = "Smile", "Positive", "82%", "Positive expression detected. Processing stays local."
    x = 955
    draw.text((x, 110), "Current likely expression", fill=c["muted"], font=F_BODY)
    draw.text((x, 140), expression, fill=c["text"], font=F_TITLE)
    for offset, line in enumerate([
        f"Expression group: {group}", f"Confidence: {conf}", "Detection mode: Hybrid",
        "Personalized profile: active", "Local metadata logging: enabled", "Background mode: inactive",
    ]):
        draw.text((x, 200 + offset * 30), line, fill=c["text"], font=F_BODY)
    draw.rounded_rectangle((955, 400, 1238, 500), radius=12, fill=c["panel2"], outline=c["line"])
    draw_wrapped(draw, msg, (975, 420), 240, c["text"], F_BODY)
    draw.text((955, 530), "Recent expression timeline", fill=c["muted"], font=F_BODY)
    for i, color in enumerate(["#8a93a3", "#3d8ee6", "#8a93a3", "#3d8ee6"]):
        draw.rounded_rectangle((955 + i * 36, 566, 980 + i * 36, 650), radius=8, fill=color)
    labels = ["Start Camera", "Stop Camera", "Pause Analysis", "Settings", "Open Logs", "Statistics", "Run in background", "Exit"]
    x0 = 18
    for i, label in enumerate(labels):
        button(draw, (x0, 735, x0 + 140, 778), label, c, i == 0)
        x0 += 151
    save(image, name)


def settings(theme, name, section="general"):
    image, draw, c = base(theme)
    draw.text((50, 38), "EmotionCam Settings", fill=c["text"], font=F_TITLE)
    y = 95
    sections = [
        ("Appearance", [("Theme", "Dark / Light"), ("Interface", "Polished dashboard, dialogs, controls")]),
        ("User Profile", [("User name", "Optional"), ("Email address", "Optional; used only for enabled summaries")]),
        ("Daily Email Summary", [("Enabled", "Off by default"), ("Delivery", "Default mail draft or SMTP"), ("Send time", "20:00"), ("SMTP TLS", "On")]),
        ("Camera and Detection", [("Camera index", "0"), ("Detection confidence", "0.45"), ("Smoothing window", "1.5 s"), ("Face-missing grace", "1.0 s")]),
    ]
    if section == "numeric":
        sections = sections[-1:] + sections[:1]
    for title, rows in sections:
        panel(draw, (50, y, 1230, y + 140), c)
        draw.text((80, y + 18), title, fill=c["text"], font=F_H2)
        x = 80
        yy = y + 58
        for label, value in rows:
            draw.text((x, yy), label, fill=c["muted"], font=F_SMALL)
            draw.rounded_rectangle((360, yy - 8, 610, yy + 26), radius=6, fill=c["input"], outline=c["line"])
            draw.text((372, yy - 4), value, fill=c["text"], font=F_SMALL)
            if any(key in label.lower() for key in ("confidence", "window", "grace", "index", "time")):
                draw.rectangle((572, yy - 7, 609, yy + 25), fill=c["button"], outline=c["line"])
                draw.polygon([(590, yy - 1), (582, yy + 7), (598, yy + 7)], fill=c["text"])
                draw.polygon([(590, yy + 20), (582, yy + 12), (598, yy + 12)], fill=c["text"])
            yy += 35
        y += 158
    button(draw, (820, 735, 990, 778), "Save", c, True)
    button(draw, (1010, 735, 1180, 778), "Cancel", c)
    save(image, name)


def calibration(name, target="smile small", match=False):
    image, draw, c = base("dark")
    draw.text((40, 30), "Personalized expression calibration", fill=c["text"], font=F_TITLE)
    draw_wrapped(draw, "Calibration stores local expression feature data and labels. EmotionCam does not save camera images unless debug image storage is explicitly enabled.", (42, 78), 1120, c["muted"], F_BODY)
    draw.text((42, 125), "Target expression", fill=c["muted"], font=F_BODY)
    draw.rounded_rectangle((210, 118, 520, 154), radius=8, fill=c["input"], outline=c["line"])
    draw.text((225, 124), target.title(), fill=c["text"], font=F_BODY)
    draw.polygon([(492, 132), (505, 132), (498, 142)], fill=c["text"])
    panel(draw, (40, 180, 355, 650), c)
    draw.text((62, 202), "Example expression graphic", fill=c["text"], font=F_H2)
    draw.ellipse((100, 260, 295, 455), fill="#202b3d", outline="#3d8ee6", width=5)
    draw.arc((148, 365, 250, 430), 20, 160, fill="#70d7ff", width=7)
    draw.arc((132, 320, 190, 365), 200, 340, fill="#70d7ff", width=6)
    draw.arc((205, 320, 263, 365), 200, 340, fill="#70d7ff", width=6)
    state = "Match" if match else "Preparing"
    fill = "#153b2b" if match else c["panel2"]
    outline = "#46d38c" if match else c["line"]
    draw.rounded_rectangle((70, 515, 325, 570), radius=12, fill=fill, outline=outline, width=2)
    draw.text((105, 532), f"Match helper: {state}", fill="#dfffea" if match else c["text"], font=F_BODY)
    panel(draw, (380, 180, 1240, 650), c)
    avatar(draw, (430, 220, 1185, 595), "positive")
    draw.text((420, 665), "Valid samples: 32 | Rejected samples: 3 | Quality summary: good", fill=c["text"], font=F_BODY)
    draw.rounded_rectangle((420, 700, 1185, 724), radius=12, fill="#27364d")
    draw.rounded_rectangle((420, 700, 940 if match else 540, 724), radius=12, fill="#2878d7")
    for i, label in enumerate(["Previous", "Start Capture", "Re-capture", "Next", "Finish"]):
        button(draw, (160 + i * 190, 742, 320 + i * 190, 782), label, c, i == 1)
    save(image, name)


def statistics(name, focus="overview"):
    image, draw, c = base("dark")
    draw.text((42, 35), "Statistics", fill=c["text"], font=F_TITLE)
    draw.text((42, 82), "Statistics are generated from local expression metadata logs only.", fill=c["muted"], font=F_BODY)
    cards = [
        ("Today's balance", "Positive 41% | Neutral 44% | Serious 15%"),
        ("Most frequent", "Neutral"),
        ("Analyzed entries", "190 entries | ~15.8 min"),
        ("Most positive period", "13:00"),
        ("Most serious period", "16:00"),
    ]
    for i, (title, value) in enumerate(cards):
        x = 42 + (i % 3) * 400
        y = 125 + (i // 3) * 112
        panel(draw, (x, y, x + 360, y + 88), c)
        draw.text((x + 18, y + 14), title, fill=c["muted"], font=F_SMALL)
        draw.text((x + 18, y + 42), value, fill=c["text"], font=F_H2)
    panel(draw, (42, 360, 610, 742), c)
    panel(draw, (645, 360, 1238, 742), c)
    draw.text((70, 382), "Selected-day expression balance", fill=c["text"], font=F_H2)
    draw.pieslice((170, 430, 430, 690), 0, 145, fill="#3d8ee6")
    draw.pieslice((170, 430, 430, 690), 145, 305, fill="#8a93a3")
    draw.pieslice((170, 430, 430, 690), 305, 360, fill="#e68a3d")
    draw.text((680, 382), "Expression counts and weekly balance", fill=c["text"], font=F_H2)
    labels = [("neutral", 130), ("smile", 95), ("focused", 78), ("tired", 35), ("concerned", 22)]
    for i, (label, value) in enumerate(labels):
        y = 430 + i * 45
        draw.text((690, y), label, fill=c["muted"], font=F_SMALL)
        draw.rounded_rectangle((790, y, 790 + value * 2, y + 20), radius=5, fill="#3d8ee6")
    for day in range(7):
        x = 700 + day * 68
        draw.rectangle((x, 690 - day * 8, x + 36, 710), fill="#8a93a3")
        draw.rectangle((x, 650 - day * 4, x + 36, 690 - day * 8), fill="#3d8ee6")
        draw.rectangle((x, 632 - day * 2, x + 36, 650 - day * 4), fill="#e68a3d")
    save(image, name)


def static_card(name, title, lines):
    image, draw, c = base("dark")
    panel(draw, (85, 90, 1195, 700), c)
    icon(draw, 125, 128, 82)
    draw.text((230, 140), title, fill=c["text"], font=F_TITLE)
    y = 245
    for line in lines:
        draw.text((150, y), line, fill=c["text"], font=F_H2)
        y += 58
    save(image, name)


def ai_settings(name, enabled=False, consent=False, mode="Local only"):
    image, draw, c = base("dark")
    draw.text((50, 38), "Settings > Expression Detection Mode and External AI", fill=c["text"], font=F_TITLE)
    panel(draw, (50, 105, 1230, 705), c)
    draw_wrapped(
        draw,
        "External AI analysis sends selected cropped face images or selected frames to an external AI service. It is disabled by default and requires explicit consent.",
        (85, 140),
        1080,
        c["muted"],
        F_BODY,
    )
    rows = [
        ("Detection mode", mode),
        ("Enable External AI Analysis", "On" if enabled else "Off"),
        ("Consent accepted", "Yes" if consent else "No - no images are sent"),
        ("API provider", "OpenAI"),
        ("OpenAI API key", "•••••••• (not shown)"),
        ("Send cropped face only", "On - recommended"),
        ("AI request interval", "10 seconds"),
        ("AI timeout", "20 seconds"),
        ("Show AI debug info", "Off"),
    ]
    y = 235
    for label, value in rows:
        draw.text((95, y), label, fill=c["muted"], font=F_BODY)
        draw.rounded_rectangle((390, y - 8, 960, y + 30), radius=7, fill=c["input"], outline=c["line"])
        draw.text((405, y - 3), value, fill=c["text"], font=F_BODY)
        y += 50
    button(draw, (965, 600, 1165, 648), "Test Connection", c, True)
    save(image, name)


def dashboard_ai(name, mode="Hybrid local + AI", status="Missing API key"):
    image, draw, c = base("dark")
    icon(draw, 26, 22, 50)
    draw.text((90, 27), "EmotionCam", fill=c["text"], font=F_H1)
    draw.text((400, 42), "LOCAL BY DEFAULT | EXTERNAL AI ENABLED BY CONSENT | NO IMAGE SAVING", fill=c["muted"], font=F_SMALL)
    panel(draw, (18, 86, 918, 720), c)
    panel(draw, (932, 86, 1262, 720), c)
    avatar(draw, (80, 150, 860, 650), "positive")
    x = 955
    draw.text((x, 110), "Current likely expression", fill=c["muted"], font=F_BODY)
    draw.text((x, 140), "Smile Small", fill=c["text"], font=F_TITLE)
    for offset, line in enumerate([
        "Expression group: Positive",
        "Confidence: 78%",
        f"Detection mode: {mode}",
        "Personalized profile: active",
        f"External AI: enabled | {status}",
        "AI result: --",
        "Final source: local fallback",
    ]):
        draw.text((x, 200 + offset * 30), line, fill=c["text"], font=F_BODY)
    draw.rounded_rectangle((955, 440, 1238, 530), radius=12, fill=c["panel2"], outline=c["line"])
    draw_wrapped(draw, "If no key is configured, EmotionCam keeps using local detection.", (975, 460), 240, c["text"], F_BODY)
    labels = ["Start Camera", "Stop Camera", "Settings", "Statistics", "Run in background", "Exit"]
    x0 = 32
    for i, label in enumerate(labels):
        button(draw, (x0, 735, x0 + 170, 778), label, c, i == 0)
        x0 += 182
    save(image, name)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for file in OUT.glob("*.png"):
        file.unlink()
    startup()
    dashboard("dark", "02_main_dashboard_dark_theme.png")
    dashboard("light", "03_main_dashboard_light_theme.png")
    dashboard("dark", "04_camera_stopped_screen.png", stopped=True)
    settings("dark", "05_settings_general_dark.png")
    settings("light", "06_settings_general_light.png")
    settings("dark", "07_settings_numeric_arrows.png", "numeric")
    settings("light", "08_theme_toggle.png")
    calibration("09_calibration_overview.png")
    calibration("10_calibration_expression_dropdown.png", "surprised")
    calibration("11_calibration_example_graphic.png", "focused")
    calibration("12_calibration_match_checkmark.png", "smile small", True)
    statistics("13_statistics_overview.png")
    statistics("14_statistics_today_balance.png", "today")
    statistics("15_statistics_weekly_balance.png", "week")
    statistics("16_statistics_expression_counts.png", "counts")
    settings("dark", "17_user_profile_settings.png")
    settings("dark", "18_daily_email_summary_settings.png")
    static_card("19_background_mode_tray.png", "Background Mode Tray", [
        "EmotionCam is running locally in the system tray.",
        "Tray menu: Show EmotionCam | Stop Camera | Exit",
        "Stable notifications use cooldowns and safe wording.",
    ])
    static_card("20_logs_folder.png", "Local Logs Folder", [
        "%LOCALAPPDATA%\\EmotionCam\\logs",
        "expression_history.jsonl stores metadata only.",
        "No webcam images, videos, or face images are saved in logs.",
    ])
    ai_settings("23_external_ai_settings_disabled.png")
    ai_settings("24_external_ai_consent_warning.png", enabled=True, consent=False, mode="Hybrid local + AI")
    ai_settings("25_external_ai_settings_enabled_no_key.png", enabled=True, consent=True, mode="Hybrid local + AI")
    dashboard_ai("26_dashboard_ai_status.png", "External AI only", "Missing API key")
    dashboard_ai("27_dashboard_hybrid_local_ai_mode.png", "Hybrid local + AI", "Waiting")


if __name__ == "__main__":
    main()
