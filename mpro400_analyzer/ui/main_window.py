from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence, Tuple

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QToolBar,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSizePolicy,
)

from app.config import AppConfig
from data.data_manager import DataManager
from export.export_image import export_image_dialog
from ui.file_loader_widget import FileLoaderWidget
from ui.guide_dialog import GuideDialog
from ui.plot_viewer_widget import PlotViewerWidget
from ui.range_controls_widget import RangeControlsWidget


class MainWindow(QMainWindow):
    def __init__(self, manager: DataManager, config: AppConfig, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.manager = manager
        self.config = config

        self.setWindowTitle("MPRO400 CSV 그래프 뷰어")
        self.setWindowIcon(QIcon("app.ICO"))
        self.resize(1200, 800)

        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        self.toolbar = QToolBar("메인 툴바")
        self.toolbar.setMovable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)

        self.action_open = QAction("파일 열기", self)
        self.action_append = QAction("추가 로드", self)
        self.action_clear = QAction("파일 초기화", self)
        self.action_export = QAction("이미지 내보내기", self)

        for action in (self.action_open, self.action_append, self.action_clear, self.action_export):
            self.toolbar.addAction(action)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        self.range_controls = RangeControlsWidget()
        layout.addWidget(self.range_controls)

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)
        layout.addWidget(content, stretch=1)

        self.file_loader = FileLoaderWidget()
        self.file_loader.setMinimumWidth(380)
        self.file_loader.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        self.plot_viewer = PlotViewerWidget()
        self.plot_viewer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        content_layout.addWidget(self.file_loader, stretch=0)
        content_layout.addWidget(self.plot_viewer, stretch=1)

        self.setCentralWidget(central)

        status = QStatusBar()
        self.setStatusBar(status)
        status.showMessage("CSV 파일을 불러오세요.")

    def _connect_signals(self) -> None:
        self.action_open.triggered.connect(lambda: self._open_files(replace=True))
        self.action_append.triggered.connect(lambda: self._open_files(replace=False))
        self.action_clear.triggered.connect(self._clear_all_files)
        self.action_export.triggered.connect(self._export_plot)

        self.file_loader.datasetToggled.connect(self._on_dataset_toggled)
        self.file_loader.datasetSelected.connect(self._on_dataset_selected)
        self.file_loader.datasetColorChanged.connect(self._on_dataset_color_changed)
        self.file_loader.datasetStyleChanged.connect(self._on_dataset_style_changed)

        self.range_controls.referenceChanged.connect(self._on_reference_changed)
        self.range_controls.filtersChanged.connect(self._on_filters_changed)

    def _open_files(self, replace: bool) -> None:
        start_dir = Path(self.config.last_dir) if self.config.last_dir else Path.home()
        if not start_dir.exists():
            start_dir = Path.home()

        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "MPRO400 CSV 불러오기",
            str(start_dir),
            "CSV 파일 (*.csv);;모든 파일 (*.*)",
        )
        if not paths:
            return

        warnings = self.manager.load([Path(p) for p in paths], append=not replace)
        self.config.last_dir = str(Path(paths[-1]).parent)
        self._after_data_mutation(warnings)

    def _after_data_mutation(self, warnings: Sequence[str]) -> None:
        self._refresh_file_list()
        self._redraw_plot()
        self._show_warnings(warnings)

    def _refresh_file_list(self) -> None:
        datasets = self.manager.datasets()
        self.file_loader.set_datasets(datasets, self.manager.selected_id)
        self.statusBar().showMessage(f"불러온 파일: {len(datasets)}")

    def _redraw_plot(self) -> None:
        payloads = self.manager.plot_payloads()
        self.plot_viewer.update_plot(payloads)
        for dataset in self.manager.datasets():
            self.file_loader.update_dataset(dataset)

    def _show_warnings(self, warnings: Sequence[str]) -> None:
        if not warnings:
            return
        QMessageBox.warning(self, "불러오기 경고", "\n".join(str(w) for w in warnings))

    def _refresh_after_change(self) -> None:
        self._refresh_file_list()
        self._redraw_plot()

    def _clear_all_files(self) -> None:
        if not self.manager.datasets():
            return
        self.manager.clear()
        self.range_controls.reset()
        self._refresh_after_change()

    def _on_dataset_toggled(self, identifier: int, enabled: bool) -> None:
        self.manager.set_enabled(identifier, enabled)
        self._redraw_plot()

    def _on_dataset_selected(self, identifier: int) -> None:
        self.manager.set_selected(identifier)

    def _on_dataset_color_changed(self, identifier: int, color: str) -> None:
        self.manager.set_color(identifier, color)
        self._redraw_plot()

    def _on_dataset_style_changed(self, identifier: int, style: str) -> None:
        self.manager.set_line_style(identifier, style)
        self._redraw_plot()

    def _on_reference_changed(self, value: float) -> None:
        self.manager.update_reference(value)
        self._redraw_plot()

    def _on_filters_changed(
        self,
        torque: Tuple[Optional[float], Optional[float]],
        angle: Tuple[Optional[float], Optional[float]],
    ) -> None:
        self.manager.update_ranges(torque, angle)
        self._redraw_plot()

    def _export_plot(self) -> None:
        export_image_dialog(self, self.plot_viewer)

    def maybe_show_onboarding(self) -> None:
        if not self.config.show_onboarding:
            return
        dialog = GuideDialog(self)
        dialog.exec()
        if dialog.skip_requested():
            self.config.show_onboarding = False


