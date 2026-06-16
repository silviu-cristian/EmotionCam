"""Central privacy wording and guarantees."""

PRIVACY_NOTICE = (
    "EmotionCam processes webcam frames locally. It stores only expression "
    "metadata and optional personalized calibration features locally. It does not "
    "identify people or upload data. Raw calibration images are off by default."
)

LOGGING_EXPLANATION = (
    "Only timestamps, visible expression labels, confidence scores, popup status, and status metadata "
    "are saved. EmotionCam does not save webcam images, video frames, or face images "
    "unless raw calibration debug images are explicitly enabled."
)

APPROXIMATION_NOTICE = (
    "Visible expression estimates are approximate observations of facial features. "
    "EmotionCam does not know true emotions or diagnose mood or mental state."
)
