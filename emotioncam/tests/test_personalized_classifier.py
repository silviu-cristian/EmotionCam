from app.core.config import DEFAULT_CONFIG
from app.core.expression_backends import (
    ExpressionResult,
    HeuristicExpressionClassifier,
    HybridExpressionClassifier,
    PersonalizedExpressionClassifier,
    create_expression_classifier,
)
from app.core.expression_features import (
    FeatureSample,
    calibration_sample_acceptable,
    extract_expression_features,
)
from app.core.expression_profile import ExpressionProfile
from app.core.face_detector import FaceDetection


def landmark_detection():
    points = [(0.5, 0.5, 0.0) for _ in range(468)]
    positions = {
        33: (0.3, 0.4, 0.0), 263: (0.7, 0.4, 0.0),
        159: (0.35, 0.38, 0.0), 145: (0.35, 0.42, 0.0),
        386: (0.65, 0.38, 0.0), 374: (0.65, 0.42, 0.0),
        61: (0.38, 0.65, 0.0), 291: (0.62, 0.65, 0.0),
        13: (0.5, 0.62, 0.0), 14: (0.5, 0.68, 0.0), 1: (0.5, 0.5, 0.0),
    }
    for index, point in positions.items():
        points[index] = point
    return FaceDetection((0, 0, 100, 100), 0.9, points, {"mouthSmileLeft": 0.8})


def test_expression_feature_extraction_is_normalized():
    sample = extract_expression_features(landmark_detection())
    assert sample is not None
    assert len(sample.values) == 14
    assert sample.quality > 0.5


def test_profile_save_load_and_delete(tmp_path):
    path = tmp_path / "profile" / "expression_profile.json"
    profile = ExpressionProfile(path)
    profile.add_samples("smile_small", [[0.1] * 14, [0.2] * 14])
    loaded = ExpressionProfile(path)
    assert loaded.counts() == {"smile_small": 2}
    (path.parent / "debug_images").mkdir()
    labels = path.parent / "expression_labels.json"
    labels.write_text("{}", encoding="utf-8")
    loaded.delete()
    assert not path.exists()
    assert not (path.parent / "debug_images").exists()
    assert labels.exists()


def test_personalized_returns_unknown_when_confidence_low(tmp_path, monkeypatch):
    profile = ExpressionProfile(tmp_path / "profile.json")
    profile.samples = {"sad": [[0.0] * 14]}
    classifier = PersonalizedExpressionClassifier(profile, confidence_threshold=0.55)
    monkeypatch.setattr(
        "app.core.expression_backends.extract_expression_features",
        lambda detection: FeatureSample([10.0] * 14, 1.0, {}),
    )
    result = classifier.classify(None, landmarks=landmark_detection())
    assert result.label == "unknown"


def test_hybrid_falls_back_to_heuristic():
    class Personal:
        threshold = 0.55
        def classify(self, *args):
            return ExpressionResult("unknown", "neutral", 0.2, {}, "personalized", {})

    class Heuristic:
        def classify(self, *args):
            return ExpressionResult("smile", "positive", 0.8, {"smile": 0.8}, "heuristic", {})

    result = HybridExpressionClassifier(Heuristic(), Personal()).classify(None)
    assert result.label == "smile"
    assert result.source == "heuristic_fallback"


def test_classifier_mode_selection(tmp_path):
    profile = ExpressionProfile(tmp_path / "profile.json")
    profile.samples = {"neutral": [[0.0] * 14]}
    settings = dict(DEFAULT_CONFIG)
    settings["expression_detection_mode"] = "hybrid"
    assert isinstance(create_expression_classifier(settings, profile), HybridExpressionClassifier)
    settings["expression_detection_mode"] = "heuristic"
    assert isinstance(create_expression_classifier(settings, profile), HeuristicExpressionClassifier)


def test_calibration_rejects_no_face():
    accepted, reason = calibration_sample_acceptable(None, None, blur=100, brightness=100)
    assert accepted is False
    assert reason == "face_or_landmarks_unclear"


def test_raw_calibration_images_off_by_default():
    assert DEFAULT_CONFIG["store_raw_calibration_images"] is False
