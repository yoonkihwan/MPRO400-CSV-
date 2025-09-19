from pathlib import Path

from PySide6.QtWidgets import QApplication

from data.data_manager import PlotPayload
from plots.plotter import Plotter


def _ensure_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


def test_plotter_draws_lines(tmp_path):
    _ensure_app()
    plotter = Plotter()

    payload = PlotPayload(
        label="샘플",
        x=[0.0, 1.0, 2.0],
        y=[0.0, 0.5, 1.0],
        color="#4aa8ff",
        line_style="solid",
        reference_hit=True,
    )

    plotter.draw([payload])
    assert len(plotter.axes.lines) >= 1

    target = tmp_path / "out.png"
    plotter.save(str(target), dpi=100)
    assert target.exists()
