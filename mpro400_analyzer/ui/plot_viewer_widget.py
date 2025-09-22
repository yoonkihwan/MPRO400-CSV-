from __future__ import annotations

from typing import Iterable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QSizePolicy,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT

from data.data_manager import PlotPayload
from plots.plotter import HoverDetails, Plotter


class HoverInfoPanel(QFrame):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("hoverInfoPanel")
        self.setMinimumWidth(190)
        self.setMaximumWidth(240)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.setStyleSheet(
            "background-color: #f6f8fb;"
            "border-left: 1px solid #d5dde8;"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        self.angle_label = QLabel("Angle –")
        self.angle_label.setAlignment(Qt.AlignLeft)
        self.angle_label.setStyleSheet("font-weight:600; color:#1c3324; font-size:14px;")
        layout.addWidget(self.angle_label)

        self._scroll = QScrollArea(self)
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        layout.addWidget(self._scroll, 1)

        body = QWidget(self._scroll)
        self._entries_layout = QVBoxLayout(body)
        self._entries_layout.setContentsMargins(0, 0, 0, 0)
        self._entries_layout.setSpacing(6)
        self._scroll.setWidget(body)

        self._placeholder = QLabel("그래프 위에 마우스를 올려 보세요.")
        self._placeholder.setWordWrap(True)
        self._placeholder.setStyleSheet("color:#6b7c8b; font-size:12px;")
        self._entries_layout.addWidget(self._placeholder)
        self._entries_layout.addStretch(1)

        self._entry_labels: list[QLabel] = []

    def update_details(self, details: Optional[HoverDetails]) -> None:
        for label in self._entry_labels:
            label.deleteLater()
        self._entry_labels.clear()

        if not details or not details.entries:
            self.angle_label.setText("Angle –")
            self._placeholder.setVisible(True)
            return

        self.angle_label.setText(f"Angle {details.xdata:.3f}")
        self._placeholder.setVisible(False)

        for entry in details.entries:
            label = QLabel(
                (
                    "<div>"
                    "<span style='display:inline-block;width:10px;height:10px;"
                    f"background:{entry.color};border-radius:50%;margin-right:6px;'></span>"
                    f"<span style='color:{entry.color}; font-weight:600;'>Torque={entry.y:.3f}</span>"
                    "</div>"
                )
            )
            label.setTextFormat(Qt.RichText)
            label.setStyleSheet("font-size:12px; color:#1c3324;")
            label.setWordWrap(True)
            self._entries_layout.insertWidget(self._entries_layout.count() - 1, label)
            self._entry_labels.append(label)

    def clear(self) -> None:
        self.update_details(None)


class PlotViewerWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.plotter = Plotter()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.toolbar = NavigationToolbar2QT(self.plotter.widget(), self)
        layout.addWidget(self.toolbar)

        content = QWidget(self)
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)
        layout.addWidget(content, stretch=1)

        canvas = self.plotter.widget()
        canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout.addWidget(canvas, stretch=1)

        self._info_panel = HoverInfoPanel()
        content_layout.addWidget(self._info_panel)

        self.plotter.set_hover_callback(self._handle_hover_update)

    def update_plot(self, payloads: Iterable[PlotPayload]) -> None:
        self.plotter.draw(payloads)

    def save_image(self, path: str, dpi: int) -> None:
        self.plotter.save(path, dpi)

    def _handle_hover_update(self, details: Optional[HoverDetails]) -> None:
        self._info_panel.update_details(details)
