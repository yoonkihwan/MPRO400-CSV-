from __future__ import annotations

from typing import Iterable

import numpy as np
from matplotlib import font_manager, rcParams
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from data.data_manager import PlotPayload
from .styles import to_matplotlib

_KOREAN_FONT_CANDIDATES = (
    "Malgun Gothic",
    "MalgunGothic",
    "NanumGothic",
    "AppleGothic",
    "Noto Sans CJK KR",
)
_FONT_INITIALIZED = False


def _configure_korean_font() -> None:
    global _FONT_INITIALIZED
    if _FONT_INITIALIZED:
        return

    selected_font = None
    for candidate in _KOREAN_FONT_CANDIDATES:
        try:
            font_manager.findfont(candidate, fallback_to_default=False)
        except ValueError:
            continue
        selected_font = candidate
        break

    if selected_font:
        rcParams["font.family"] = [selected_font]
    rcParams["axes.unicode_minus"] = False
    _FONT_INITIALIZED = True


_configure_korean_font()


class Plotter:
    def __init__(self) -> None:
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self._init_axes()

    def widget(self) -> FigureCanvasQTAgg:
        return self.canvas

    def draw(self, payloads: Iterable[PlotPayload]) -> None:
        self.axes.clear()
        self._init_axes()

        plotted = False

        for payload in payloads:
            linestyle = to_matplotlib(payload.line_style)
            if not payload.x or not payload.y:
                self.axes.plot([], [], linestyle=linestyle, color=payload.color, label=payload.label)
                continue

            alpha = 0.5 if not payload.reference_hit else 1.0
            self.axes.plot(
                payload.x,
                payload.y,
                linestyle=linestyle,
                color=payload.color,
                linewidth=1.8,
                label=payload.label,
                alpha=alpha,
            )
            plotted = True

        handles, labels = self.axes.get_legend_handles_labels()
        self._place_legend(handles, labels)
        if not plotted:
            self.axes.text(
                0.5,
                0.5,
                "No data to display",
                ha="center",
                va="center",
                transform=self.axes.transAxes,
                color="#333333",
            )

        self.figure.tight_layout()
        self.canvas.draw_idle()

    def save(self, path: str, dpi: int = 150) -> None:
        self.figure.savefig(path, dpi=dpi, facecolor=self.figure.get_facecolor())

    def _init_axes(self) -> None:
        self.axes.set_xlabel("Angle (deg)")
        self.axes.set_ylabel("Torque (N-m)")
        self.axes.grid(True, color="#d7dee9", alpha=0.8, linewidth=0.8)
        self.axes.set_facecolor("#ffffff")
        self.figure.set_facecolor("#ffffff")
        for spine in self.axes.spines.values():
            spine.set_color("#91a5c8")
            spine.set_linewidth(1.2)
        self.axes.tick_params(colors="#36435a")
        self.axes.xaxis.label.set_color("#111111")
        self.axes.yaxis.label.set_color("#111111")

    def _place_legend(self, handles, labels) -> None:
        if not labels:
            return

        legend = self.axes.legend(handles, labels, loc="upper left")
        self.canvas.draw()
        renderer = self.canvas.get_renderer()
        if renderer is not None:
            legend_bbox = legend.get_window_extent(renderer=renderer)
            if self._legend_overlaps_data(legend_bbox):
                legend.remove()
                legend = self.axes.legend(handles, labels, loc="best")

        self._style_legend(legend)

    def _legend_overlaps_data(self, legend_bbox) -> bool:
        for line in self.axes.lines:
            if not line.get_visible():
                continue

            xdata = np.asarray(line.get_xdata(), dtype=float)
            ydata = np.asarray(line.get_ydata(), dtype=float)
            if xdata.size == 0 or ydata.size == 0:
                continue

            step = max(1, xdata.size // 300)
            sample = np.column_stack((xdata[::step], ydata[::step]))
            if sample.size == 0:
                continue

            display_points = self.axes.transData.transform(sample)
            for x, y in display_points:
                if legend_bbox.contains(x, y):
                    return True

        return False

    def _style_legend(self, legend) -> None:
        if legend is None:
            return

        frame = legend.get_frame()
        frame.set_alpha(0.85)
        frame.set_facecolor("#f6f7fb")
        frame.set_edgecolor("#bdc7d6")


__all__ = ["Plotter"]

