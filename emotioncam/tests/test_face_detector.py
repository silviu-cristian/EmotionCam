from app.core.face_detector import FaceDetection, FaceDetector


def test_face_missing_grace_returns_last_detection():
    detector = FaceDetector.__new__(FaceDetector)
    detector.grace_seconds = 1.0
    detector._landmarker = None
    detector._last = None
    detector._last_seen = float("-inf")
    detected = FaceDetection((10, 20, 100, 100), 0.8)
    results = iter((detected, None, None))
    detector._detect_opencv = lambda frame: next(results)

    assert detector.detect(object(), now=0.0) == detected
    grace = detector.detect(object(), now=0.5)
    assert grace is not None
    assert grace.using_grace is True
    assert detector.detect(object(), now=1.1) is None
