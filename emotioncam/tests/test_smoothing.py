from app.core.smoothing import ExpressionSmoother


def test_stable_expression_waits_then_changes():
    smoother = ExpressionSmoother(window_seconds=2.0, stable_seconds=0.5)
    first = smoother.add("happy", 0.8, True, now=0.0)
    second = smoother.add("happy", 0.8, True, now=0.6)
    assert first.label == "unknown"
    assert second.label == "happy"
    assert second.group == "positive"


def test_no_face_is_neutral_group():
    smoother = ExpressionSmoother(stable_seconds=0)
    result = smoother.add("no face detected", 1.0, False, now=1.0)
    assert result.face_detected is False
    assert result.group == "neutral"


def test_single_frame_prediction_does_not_flicker_stable_result():
    smoother = ExpressionSmoother(window_seconds=2.0, stable_seconds=0.4)
    smoother.add("smile", 0.9, True, now=0.0)
    stable = smoother.add("smile", 0.9, True, now=0.5)
    flicker = smoother.add("angry", 0.9, True, now=0.6)
    assert stable.label == "smile"
    assert flicker.label == "smile"


def test_validated_custom_label_is_retained_as_neutral_group():
    smoother = ExpressionSmoother(stable_seconds=0)
    result = smoother.add("half_smile", 0.8, True, now=1.0)
    assert result.label == "half_smile"
    assert result.group == "neutral"
