from __future__ import annotations

from typing import Iterable, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT

from data.data_manager import PlotPayload
from plots.plotter import HoverDetails, Plotter


class PlotViewerWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.plotter = Plotter()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        self.toolbar = NavigationToolbar2QT(self.plotter.widget(), self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.plotter.widget(), stretch=1)

        self._hover_label = QLabel(self.plotter.widget())
        self._hover_label.setVisible(False)
        self._hover_label.setWordWrap(True)
        self._hover_label.setTextFormat(Qt.RichText)
        self._hover_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self._hover_label.setMargin(6)
        self._hover_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self._hover_label.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.88);"
            "border: 1px solid #b7c5d6;"
            "border-radius: 4px;"
            "color: #1c3324;"
            "font-size: 13px;"
        )

        self.plotter.set_hover_callback(self._handle_hover_update)

    def update_plot(self, payloads: Iterable[PlotPayload]) -> None:
        self.plotter.draw(payloads)

    def save_image(self, path: str, dpi: int) -> None:
        self.plotter.save(path, dpi)

    def _handle_hover_update(self, details: Optional[HoverDetails]) -> None:
        if not details or not details.entries:
            self._hover_label.hide()
            return

        row_template = (
            "<div>"
            "<span style='display:inline-block;width:10px;height:10px;background:{color};"
            "border-radius:50%;margin-right:6px;'></span>"
            "<span style='color:{color}; font-weight:600;'>Torque={torque:.3f}</span>"
            "</div>"
        )
        rows = [
            row_template.format(color=entry.color, torque=entry.y)
            for entry in details.entries
        ]

        header = f"<div style='font-weight:600; color:#1c3324;'>Angle {details.xdata:.3f}</div>"
        html_text = header + "".join(rows)
        self._hover_label.setText(html_text)
        self._hover_label.adjustSize()

        canvas = self.plotter.widget()
        margin = 12
        x = canvas.width() - self._hover_label.width() - margin
        y = margin
        if x < margin:
            x = margin

        self._hover_label.move(x, y)
        self._hover_label.show()
        self._hover_label.raise_()
