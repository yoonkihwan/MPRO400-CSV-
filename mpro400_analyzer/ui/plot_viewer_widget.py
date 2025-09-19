from __future__ import annotations

from typing import Iterable, Optional

from PySide6.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT

from data.data_manager import PlotPayload
from plots.plotter import Plotter


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

    def update_plot(self, payloads: Iterable[PlotPayload]) -> None:
        self.plotter.draw(payloads)

    def save_image(self, path: str, dpi: int) -> None:
        self.plotter.save(path, dpi)
