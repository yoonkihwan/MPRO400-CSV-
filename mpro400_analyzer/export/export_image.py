from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QLabel,
    QMessageBox,
    QWidget,
)

from ui.plot_viewer_widget import PlotViewerWidget


class ExportOptionsDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("이미지 내보내기 옵션")

        layout = QFormLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        self.dpi_combo = QComboBox()
        self.dpi_combo.addItem("1x (150 dpi)", userData=150)
        self.dpi_combo.addItem("2x (300 dpi)", userData=300)
        layout.addRow(QLabel("해상도"), self.dpi_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def selected_dpi(self) -> int:
        return int(self.dpi_combo.currentData())


def export_image_dialog(parent: QWidget, plot_widget: PlotViewerWidget) -> None:
    if plot_widget is None:
        return

    path, selected_filter = QFileDialog.getSaveFileName(
        parent,
        "이미지 내보내기",
        "",
        "PNG 이미지 (*.png);;JPEG 이미지 (*.jpg)",
    )
    if not path:
        return

    suffix = Path(path).suffix.lower()
    if not suffix:
        suffix = ".png" if "PNG" in selected_filter else ".jpg"
        path = f"{path}{suffix}"

    options = ExportOptionsDialog(parent)
    if options.exec() != QDialog.Accepted:
        return

    dpi = options.selected_dpi()
    try:
        plot_widget.save_image(path, dpi)
    except Exception as exc:  # pragma: no cover - GUI feedback path
        QMessageBox.critical(parent, "내보내기 오류", str(exc))
        return

    QMessageBox.information(parent, "내보내기 완료", f"이미지를 저장했습니다:\n{path}")
