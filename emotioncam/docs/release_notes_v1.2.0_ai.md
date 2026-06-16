# EmotionCam v1.2.0 AI-enabled

This release adds a second AI provider: **Local Ollama AI**.

## What changed

- Added **Local Ollama** as an optional AI backend.
- Local Ollama runs on your own computer and does not need OpenAI credits.
- OpenAI remains available as an optional cloud provider.
- AI is still off by default.
- AI still requires explicit consent before EmotionCam sends selected images to
  any AI provider.
- Cropped-face-only mode remains enabled by default.
- Local Ollama endpoints are restricted to `localhost` / `127.0.0.1` to prevent
  accidental remote uploads.
- Test Connection now works for either OpenAI or Local Ollama.

## How to use Local Ollama

1. Install Ollama separately from the official Ollama app/site.
2. Open PowerShell and install a local vision model:

   ```powershell
   ollama pull llava:7b
   ```

3. Open EmotionCam.
4. Go to **Settings > Expression Detection Mode and AI Analysis**.
5. Set provider to **Local Ollama (runs on this computer)**.
6. Keep endpoint `http://localhost:11434`.
7. Keep model `llava:7b`, unless you installed a different vision model.
8. Click **Test Connection**.
9. Enable AI Analysis, accept consent, and select **Hybrid local + AI**.

## Privacy notes

- Local Ollama mode sends selected cropped face images or frames only to Ollama
  running on this computer.
- OpenAI mode may send selected cropped face images or frames to OpenAI.
- EmotionCam never logs images, base64 image data, API keys, or raw webcam
  frames.
- EmotionCam estimates visible expressions only. It does not know true internal
  emotions, identify people, or diagnose mood or mental state.

## Previous releases

The initial **v1.0.0 local-only** release remains available in GitHub Releases.
The earlier OpenAI-only AI releases remain available for history.
