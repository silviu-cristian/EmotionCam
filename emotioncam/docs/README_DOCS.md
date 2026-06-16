# Regenerating EmotionCam Documentation

The maintained sources are:

- `docs/user_manual.md`
- `docs/user_manual.html`
- `docs/START_DEMO_HERE.md`
- `docs/START_DEMO_HERE.html`
- `docs/demo_script.md`

Regenerate the camera-free Settings screenshots:

```powershell
$env:QT_QPA_PLATFORM="offscreen"
.\.venv\Scripts\python.exe docs\render_static_screens.py
```

Regenerate all placeholder screenshots:

```powershell
.\docs\generate_placeholders.ps1
```

Regenerate DOCX/PDF with a Python environment containing `python-docx` and `reportlab`:

```powershell
python docs\generate_manual_formats.py
python docs\generate_manual_pdf.py
```

For full DOCX visual QA or Word-based PDF conversion, install LibreOffice and run:

```powershell
python render_docx.py docs\EmotionCam_User_Manual.docx --output_dir docs\manual_render --emit_pdf
```

The checked-in HTML files are intentionally self-contained and use no external CDN or internet assets.
