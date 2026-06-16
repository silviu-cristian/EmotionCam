from app.core.expression_classifier import ExpressionClassifier
from app.core.smoothing import EXPRESSION_GROUPS


def test_expression_groups_cover_expanded_labels():
    assert EXPRESSION_GROUPS["smile"] == "positive"
    assert EXPRESSION_GROUPS["laughing"] == "positive"
    assert EXPRESSION_GROUPS["tired"] == "negative"
    assert EXPRESSION_GROUPS["focused"] == "neutral"
    assert EXPRESSION_GROUPS["no_face"] == "neutral"


def test_weak_negative_falls_back_to_neutral():
    classifier = ExpressionClassifier.__new__(ExpressionClassifier)
    classifier.threshold = 0.45
    classifier.negative_min = 0.65
    classifier.positive_min = 0.50
    result = classifier._safe_result("disgusted", 0.55, {"disgusted": 0.55, "neutral": 0.52})
    assert result["label"] == "neutral"
    assert result["group"] == "neutral"


def test_smile_blendshapes_prioritize_smile_not_disgust():
    classifier = ExpressionClassifier.__new__(ExpressionClassifier)
    classifier.threshold = 0.45
    classifier.negative_min = 0.65
    classifier.positive_min = 0.50
    probabilities = classifier._blendshape_probabilities(
        {
            "mouthSmileLeft": 0.9,
            "mouthSmileRight": 0.88,
            "cheekSquintLeft": 0.5,
            "cheekSquintRight": 0.48,
            "noseSneerLeft": 0.2,
            "noseSneerRight": 0.1,
            "mouthUpperUpLeft": 0.1,
            "mouthUpperUpRight": 0.1,
        }
    )
    label, confidence = max(probabilities.items(), key=lambda item: item[1])
    result = classifier._safe_result(label, confidence, probabilities)
    assert result["label"] in {"smile", "happy", "laughing"}
    assert result["label"] != "disgusted"
