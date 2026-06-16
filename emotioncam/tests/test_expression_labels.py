import json

import pytest

from app.core.expression_labels import ExpressionLabelRegistry, normalize_expression_label


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("half smile", "half_smile"),
        ("  very tired  ", "very_tired"),
        ("Confused Face!", "confused_face"),
        ("a___b", "a_b"),
    ],
)
def test_normalize_expression_label(raw, expected):
    assert normalize_expression_label(raw) == expected


def test_empty_custom_label_rejected():
    with pytest.raises(ValueError):
        normalize_expression_label(" !!! ")


def test_registry_saves_and_prevents_duplicates(tmp_path):
    path = tmp_path / "expression_labels.json"
    registry = ExpressionLabelRegistry(path)
    assert path.exists()
    assert registry.add_custom("Half Smile") == "half_smile"
    with pytest.raises(ValueError):
        registry.add_custom("half smile")
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved["custom_labels"] == ["half_smile"]
    assert "neutral" in saved["default_labels"]
