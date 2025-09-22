from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Tuple

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


@dataclass
class HoverSeriesInfo:
    label: str
    color: str
    x: float
    y: float


@dataclass
class HoverDetails:
    xdata: float
    canvas_pos: Tuple[int, int]
    entries: List[HoverSeriesInfo]


@dataclass
class _SeriesSnapshot:
    label: str
    color: str
    xdata: np.ndarray
    ydata: np.ndarray


HoverCallback = Callable[[Optional[HoverDetails]], None]


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
        self.canvas.setMouseTracking(True)

        self._hover_callback: Optional[HoverCallback] = None
        self._cursor_line = None
        self._series_snapshots: List[_SeriesSnapshot] = []

        self._motion_cid = self.canvas.mpl_connect("motion_notify_event", self._on_mouse_move)
        self._leave_cid = self.canvas.mpl_connect("figure_leave_event", self._on_mouse_leave)

        self._init_axes()
        self._init_cursor_line()

    def widget(self) -> FigureCanvasQTAgg:
        return self.canvas

    def set_hover_callback(self, callback: Optional[HoverCallback]) -> None:
        self._hover_callback = callback

    def draw(self, payloads: Iterable[PlotPayload]) -> None:
        self.axes.clear()
        self._init_axes()
        self._init_cursor_line()
        self._series_snapshots.clear()

        plotted = False

        for payload in payloads:
            linestyle = to_matplotlib(payload.line_style)
            line_color = payload.color

            line, = self.axes.plot(
                payload.x,
                payload.y,
                linestyle=linestyle,
                color=line_color,
                linewidth=1.8,
                label=payload.label,
                alpha=1.0 if payload.reference_hit else 0.5,
            )

            xdata = np.asarray(line.get_xdata(), dtype=float)
            ydata = np.asarray(line.get_ydata(), dtype=float)
            mask = np.isfinite(xdata) & np.isfinite(ydata)
            if mask.any():
                snapshot = _SeriesSnapshot(
                    label=payload.label,
                    color=line_color,
                    xdata=xdata[mask],
                    ydata=ydata[mask],
                )
                self._series_snapshots.append(snapshot)
                plotted = plotted or snapshot.xdata.size > 0
            else:
                self._series_snapshots.append(
                    _SeriesSnapshot(label=payload.label, color=line_color, xdata=np.array([]), ydata=np.array([]))
                )

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
        self._hide_cursor()
        self._notify_hover(None)

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

    def _init_cursor_line(self) -> None:
        if self._cursor_line is not None and self._cursor_line.axes is not None:
            self._cursor_line.remove()
        self._cursor_line = self.axes.axvline(color="#36435a", linewidth=1.2, alpha=0.7)
        self._cursor_line.set_visible(False)

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

    def _on_mouse_move(self, event) -> None:
        if event.inaxes != self.axes or not self._series_snapshots:
            self._hide_cursor()
            self._notify_hover(None)
            return

        if event.xdata is None:
            self._hide_cursor()
            self._notify_hover(None)
            return

        hover_entries: List[HoverSeriesInfo] = []
        for snapshot in self._series_snapshots:
            if snapshot.xdata.size == 0:
                continue

            idx = int(np.argmin(np.abs(snapshot.xdata - event.xdata)))
            x_val = float(snapshot.xdata[idx])
            y_val = float(snapshot.ydata[idx])
            if not np.isfinite(x_val) or not np.isfinite(y_val):
                continue
            hover_entries.append(
                HoverSeriesInfo(label=snapshot.label, color=snapshot.color, x=x_val, y=y_val)
            )

        if not hover_entries:
            self._hide_cursor()
            self._notify_hover(None)
            return

        aligned_x = float(event.xdata)
        self._cursor_line.set_xdata((aligned_x, aligned_x))
        if not self._cursor_line.get_visible():
            self._cursor_line.set_visible(True)
        self.canvas.draw_idle()

        if event.guiEvent is not None and hasattr(event.guiEvent, "position"):
            qt_pos = event.guiEvent.position()
            canvas_pos = (int(qt_pos.x()), int(qt_pos.y()))
        else:
            canvas_height = self.canvas.height()
            canvas_pos = (int(event.x), int(canvas_height - event.y))

        details = HoverDetails(xdata=float(aligned_x), canvas_pos=canvas_pos, entries=hover_entries)
        self._notify_hover(details)

    def _on_mouse_leave(self, _event) -> None:
        self._hide_cursor()
        self._notify_hover(None)

    def _hide_cursor(self) -> None:
        if self._cursor_line is not None and self._cursor_line.get_visible():
            self._cursor_line.set_visible(False)
            self.canvas.draw_idle()

    def _notify_hover(self, details: Optional[HoverDetails]) -> None:
        if self._hover_callback is not None:
            self._hover_callback(details)


__all__ = [
    "Plotter",
    "HoverDetails",
    "HoverSeriesInfo",
]
