from PySide6.QtWidgets import QApplication

from app.ui.expression_example import expression_example_pixmap, expressions_match


def test_example_graphic_changes_by_expression():
    application = QApplication.instance() or QApplication([])
    neutral = expression_example_pixmap("neutral")
    surprised = expression_example_pixmap("surprised")
    assert not neutral.isNull()
    assert neutral.toImage() != surprised.toImage()
    assert application is not None


def test_match_helper_is_permissive_for_related_expressions():
    assert expressions_match("smile_big", "happy")
    assert expressions_match("focused", "thinking")
    assert not expressions_match("angry", "happy")
