"""First/startup screen."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.core.privacy import APPROXIMATION_NOTICE, LOGGING_EXPLANATION, PRIVACY_NOTICE


class StartupScreen(QWidget):
    start_requested = Signal(bool)
    settings_requested = Signal()
    exit_requested = Signal()

    def __init__(self, logging_enabled: bool) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(70, 55, 70, 55)
        layout.setSpacing(18)
        layout.addStretch()
        title = QLabel("EmotionCam")
        title.setObjectName("title")
        subtitle = QLabel("Local, approximate facial-expression detection")
        subtitle.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 22, 24, 22)
        for text in (PRIVACY_NOTICE, APPROXIMATION_NOTICE):
            label = QLabel(text)
            label.setWordWrap(True)
            card_layout.addWidget(label)
        self.logging_checkbox = QCheckBox("Save local expression metadata history")
        self.logging_checkbox.setChecked(logging_enabled)
        card_layout.addWidget(self.logging_checkbox)
        explanation = QLabel(LOGGING_EXPLANATION)
        explanation.setWordWrap(True)
        explanation.setObjectName("subtitle")
        card_layout.addWidget(explanation)
        layout.addWidget(card)

        buttons = QHBoxLayout()
        start = QPushButton("Start Camera")
        start.setObjectName("primary")
        settings = QPushButton("Settings")
        exit_button = QPushButton("Exit")
        exit_button.setObjectName("danger")
        start.clicked.connect(lambda: self.start_requested.emit(self.logging_checkbox.isChecked()))
        settings.clicked.connect(self.settings_requested)
        exit_button.clicked.connect(self.exit_requested)
        buttons.addWidget(start)
        buttons.addWidget(settings)
        buttons.addWidget(exit_button)
        buttons.addStretch()
        layout.addLayout(buttons)
        layout.addStretch()
