"""Generate a readable offline PDF from the maintained EmotionCam Markdown manual."""

from pathlib import Path
import os
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image, ListFlowable, ListItem, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
)


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SOURCE = DOCS / "user_manual.md"
OUTPUT = Path(os.environ.get("EMOTIONCAM_MANUAL_PDF", DOCS / "EmotionCam_User_Manual.pdf"))
ICON = ROOT / "app" / "assets" / "icon.png"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="CoverTitle", parent=styles["Title"], fontSize=28, leading=33, alignment=TA_CENTER, textColor=colors.HexColor("#203748"), spaceAfter=12))
styles.add(ParagraphStyle(name="CoverSub", parent=styles["Normal"], fontSize=13, leading=18, alignment=TA_CENTER, textColor=colors.HexColor("#52687C"), spaceAfter=12))
styles["Heading1"].textColor = colors.HexColor("#2E74B5")
styles["Heading2"].textColor = colors.HexColor("#2E74B5")
styles["BodyText"].leading = 15
styles.add(ParagraphStyle(name="Callout", parent=styles["BodyText"], leftIndent=12, borderColor=colors.HexColor("#D69B2D"), borderWidth=1, borderPadding=8, backColor=colors.HexColor("#FFF8E8")))

story = [
    Spacer(1, 0.55 * inch),
    Image(str(ICON), width=1.35 * inch, height=1.35 * inch),
    Spacer(1, 0.2 * inch),
    Paragraph("EmotionCam User Manual", styles["CoverTitle"]),
    Paragraph("Local visible-expression estimates with privacy-first personalized calibration", styles["CoverSub"]),
    Paragraph("Version 1.0.0 | Updated June 16, 2026", styles["CoverSub"]),
    PageBreak(),
]

lines = SOURCE.read_text(encoding="utf-8").splitlines()
index = 0
while index < len(lines):
    stripped = lines[index].strip()
    if stripped.startswith("|"):
        raw = []
        while index < len(lines) and lines[index].strip().startswith("|"):
            raw.append([item.strip().replace("`", "") for item in lines[index].strip().strip("|").split("|")])
            index += 1
        if len(raw) > 1 and all(re.fullmatch(r":?-{3,}:?", item) for item in raw[1]):
            raw.pop(1)
        table = Table(raw, repeatRows=1, hAlign="LEFT")
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8EEF5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#203748")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#B8C3D2")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("LEADING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.extend([table, Spacer(1, 8)])
        continue
    image = re.fullmatch(r"!\[(.*?)\]\((.*?)\)", stripped)
    if image:
        path = (DOCS / image.group(2)).resolve()
        if path.exists():
            story.extend([Image(str(path), width=6.2 * inch, height=3.49 * inch), Spacer(1, 8)])
    elif stripped.startswith("# "):
        pass
    elif stripped.startswith("## "):
        story.append(Paragraph(stripped[3:], styles["Heading1"]))
    elif stripped.startswith("### "):
        story.append(Paragraph(stripped[4:], styles["Heading2"]))
    elif stripped.startswith("> "):
        story.append(Paragraph(stripped[2:].replace("**", "").replace("`", ""), styles["Callout"]))
    elif stripped.startswith("- "):
        text = stripped[2:].replace("**", "").replace("`", "")
        story.append(ListFlowable([ListItem(Paragraph(text, styles["BodyText"]))], bulletType="bullet", leftIndent=18))
    elif re.match(r"^\d+\.\s", stripped):
        text = re.sub(r"^\d+\.\s+", "", stripped).replace("**", "").replace("`", "")
        story.append(ListFlowable([ListItem(Paragraph(text, styles["BodyText"]))], bulletType="1", leftIndent=18))
    elif stripped and not stripped.startswith("```"):
        story.append(Paragraph(stripped.replace("**", "").replace("`", ""), styles["BodyText"]))
    index += 1

document = SimpleDocTemplate(str(OUTPUT), pagesize=letter, rightMargin=0.65 * inch, leftMargin=0.65 * inch, topMargin=0.7 * inch, bottomMargin=0.7 * inch, title="EmotionCam User Manual", author="EmotionCam")
document.build(story)
print(OUTPUT)
