"""Theme-aware local expression statistics dialog."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from PySide6.QtCore import QDate, Qt
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.core.statistics import export_summary, read_expression_history, summarize_day, weekly_balance
from app.core.user_profile import UserProfile


class StatisticsWindow(QDialog):
    def __init__(self, theme: str = "dark", parent=None) -> None:
        super().__init__(parent)
        self.theme = theme
        self.entries = []
        self.summary = None
        self.setWindowTitle("EmotionCam Statistics")
        self.resize(1180, 820)

        layout = QVBoxLayout(self)
        title = QLabel("Statistics")
        title.setObjectName("title")
        privacy = QLabel("Statistics are generated from local expression metadata logs only.")
        privacy.setObjectName("subtitle")
        layout.addWidget(title)
        layout.addWidget(privacy)

        controls = QHBoxLayout()
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        today = QPushButton("Today")
        last_week = QPushButton("Last 7 days")
        refresh = QPushButton("Refresh")
        export = QPushButton("Export Summary")
        today.clicked.connect(lambda: self.date_edit.setDate(QDate.currentDate()))
        last_week.clicked.connect(self._show_week)
        refresh.clicked.connect(self.refresh)
        export.clicked.connect(self.export)
        self.date_edit.dateChanged.connect(self.refresh)
        controls.addWidget(QLabel("Selected day"))
        controls.addWidget(self.date_edit)
        controls.addWidget(today)
        controls.addWidget(last_week)
        controls.addWidget(refresh)
        controls.addWidget(export)
        controls.addStretch()
        layout.addLayout(controls)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        self.empty = QLabel()
        self.empty.setAlignment(Qt.AlignCenter)
        self.empty.setObjectName("message")
        self.content_layout.addWidget(self.empty)

        cards = QGridLayout()
        self.cards = {}
        for index, (key, label) in enumerate(
            (
                ("balance", "Today's expression balance"),
                ("frequent", "Most frequent expression"),
                ("entries", "Valid log entries / estimated minutes"),
                ("positive_period", "Most positive period"),
                ("serious_period", "Most serious-expression period"),
            )
        ):
            card = QFrame()
            card.setObjectName("card")
            card_layout = QVBoxLayout(card)
            card_layout.addWidget(QLabel(label))
            value = QLabel("--")
            value.setObjectName("metric")
            value.setWordWrap(True)
            card_layout.addWidget(value)
            cards.addWidget(card, index // 3, index % 3)
            self.cards[key] = value
        self.content_layout.addLayout(cards)

        self.canvas = self._create_canvas()
        self.content_layout.addWidget(self.canvas)
        self.refresh()

    def _create_canvas(self):
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        from matplotlib.figure import Figure

        self.figure = Figure(figsize=(10, 8), constrained_layout=True)
        return FigureCanvasQTAgg(self.figure)

    def refresh(self, *_args) -> None:
        selected = self.date_edit.date().toPython()
        self.entries = read_expression_history()
        self.summary = summarize_day(self.entries, selected)
        percentages = self.summary.group_percentages
        self.cards["balance"].setText(
            f"Positive {percentages['positive']:.0f}% | Neutral {percentages['neutral']:.0f}% | "
            f"Serious {percentages['negative']:.0f}%"
        )
        self.cards["frequent"].setText(self.summary.most_frequent_expression.replace("_", " ").title())
        self.cards["entries"].setText(
            f"{self.summary.analyzed_entries} entries | ~{self.summary.estimated_minutes:.1f} min"
        )
        self.cards["positive_period"].setText(self.summary.most_positive_period)
        self.cards["serious_period"].setText(self.summary.most_serious_period)
        self.empty.setText(
            "" if self.summary.analyzed_entries else
            "No local expression metadata exists for the selected day."
        )
        self._draw(selected)

    def _show_week(self) -> None:
        self.date_edit.setDate(QDate.currentDate())
        self.refresh()

    def _draw(self, selected: date) -> None:
        self.figure.clear()
        dark = self.theme == "dark"
        foreground = "#e9edf5" if dark else "#202633"
        background = "#191e28" if dark else "#ffffff"
        grid = "#465168" if dark else "#d1d8e3"
        colors = {"positive": "#3d8ee6", "neutral": "#8a93a3", "negative": "#e68a3d"}
        self.figure.set_facecolor(background)
        axes = self.figure.subplots(2, 2)
        for axis in axes.flat:
            axis.set_facecolor(background)
            axis.tick_params(colors=foreground)
            axis.title.set_color(foreground)
            for spine in axis.spines.values():
                spine.set_color(grid)

        axes[0, 0].pie(
            [self.summary.group_counts[group] for group in ("positive", "neutral", "negative")]
            if self.summary.analyzed_entries else [1],
            labels=("Positive", "Neutral", "Serious") if self.summary.analyzed_entries else ("No data",),
            colors=[colors[group] for group in ("positive", "neutral", "negative")]
            if self.summary.analyzed_entries else [grid],
            textprops={"color": foreground},
            autopct="%1.0f%%" if self.summary.analyzed_entries else None,
        )
        axes[0, 0].set_title("Selected-day expression balance")

        labels = list(self.summary.label_counts)
        axes[0, 1].bar(
            [label.replace("_", " ") for label in labels],
            [self.summary.label_counts[label] for label in labels],
            color="#3d8ee6",
        )
        axes[0, 1].set_title("Expression counts by label")
        axes[0, 1].tick_params(axis="x", labelrotation=35, labelsize=8)

        timeline = self.summary.entries
        axes[1, 0].scatter(
            [entry["timestamp"] for entry in timeline],
            [{"negative": -1, "neutral": 0, "positive": 1}[entry["group"]] for entry in timeline],
            c=[colors[entry["group"]] for entry in timeline],
            s=22,
        )
        axes[1, 0].set_yticks([-1, 0, 1], ["Serious", "Neutral", "Positive"])
        axes[1, 0].set_title("Daily expression timeline")
        axes[1, 0].grid(color=grid, alpha=0.35)

        week = weekly_balance(self.entries, selected)
        xs = [item["date"].strftime("%a") for item in week]
        bottom = [0.0] * len(week)
        for group in ("positive", "neutral", "negative"):
            values = [item[group] for item in week]
            axes[1, 1].bar(xs, values, bottom=bottom, color=colors[group], label=group.title())
            bottom = [left + right for left, right in zip(bottom, values)]
        axes[1, 1].set_ylim(0, 100)
        axes[1, 1].set_title("Last 7 days expression balance")
        axes[1, 1].legend(facecolor=background, labelcolor=foreground)
        self.canvas.draw_idle()

    def export(self) -> None:
        if not self.summary or not self.summary.analyzed_entries:
            QMessageBox.information(self, "Export Summary", "There is no selected-day data to export.")
            return
        destination, _ = QFileDialog.getSaveFileName(
            self, "Export Statistics Summary", "emotioncam-statistics-summary.txt", "Text (*.txt)"
        )
        if destination:
            export_summary(self.summary, Path(destination), UserProfile().data["name"])
            QMessageBox.information(self, "Export Summary", "Local statistics summary exported.")
