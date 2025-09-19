from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from data.data_manager import DataSet, LINE_STYLES

LINE_STYLE_LABELS = {
    "solid": "Solid",
    "dash": "Dash",
    "dot": "Dot",
}


class FileLoaderWidget(QWidget):
    datasetToggled = Signal(int, bool)
    datasetSelected = Signal(int)
    datasetColorChanged = Signal(int, str)
    datasetStyleChanged = Signal(int, str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setMinimumWidth(380)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 16)
        layout.setSpacing(10)

        title = QLabel("Measurement Files")
        title.setObjectName("filelist-title")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.list_widget.setMinimumHeight(340)
        self.list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.list_widget, stretch=1)

        self._items: Dict[int, QListWidgetItem] = {}

    def set_datasets(self, datasets: list[DataSet], selected_id: Optional[int]) -> None:
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        self._items.clear()

        for dataset in datasets:
            item = QListWidgetItem()
            widget = _FileItemWidget(dataset)
            widget.toggled.connect(lambda checked, ident=dataset.identifier: self.datasetToggled.emit(ident, checked))
            widget.colorChanged.connect(lambda color, ident=dataset.identifier: self.datasetColorChanged.emit(ident, color))
            widget.styleChanged.connect(lambda style, ident=dataset.identifier: self.datasetStyleChanged.emit(ident, style))
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            self._items[dataset.identifier] = item

        self.list_widget.blockSignals(False)

        if selected_id is not None and selected_id in self._items:
            item = self._items[selected_id]
            item.setSelected(True)
        elif self.list_widget.count():
            self.list_widget.item(0).setSelected(True)

    def update_dataset(self, dataset: DataSet) -> None:
        item = self._items.get(dataset.identifier)
        if not item:
            return
        widget = self.list_widget.itemWidget(item)
        if isinstance(widget, _FileItemWidget):
            widget.refresh(dataset)

    def _on_selection_changed(self) -> None:
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        item = selected_items[0]
        for identifier, list_item in self._items.items():
            if list_item is item:
                self.datasetSelected.emit(identifier)
                break


class _FileItemWidget(QFrame):
    toggled = Signal(bool)
    colorChanged = Signal(str)
    styleChanged = Signal(str)

    def __init__(self, dataset: DataSet, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("file-item")

        self.checkbox = QCheckBox(dataset.name)
        self.checkbox.setChecked(dataset.enabled)
        self.checkbox.toggled.connect(self.toggled.emit)
        self.checkbox.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        self.meta_label = QLabel(_build_meta_summary(dataset))
        self.meta_label.setObjectName("file-meta")
        self.meta_label.setWordWrap(True)

        self.color_button = QPushButton()
        self.color_button.setFixedSize(32, 22)
        self.color_button.clicked.connect(self._choose_color)

        self.style_combo = QComboBox()
        self.style_combo.setMinimumWidth(120)
        for style in LINE_STYLES:
            self.style_combo.addItem(LINE_STYLE_LABELS.get(style, style), userData=style)
        self.style_combo.setCurrentIndex(max(self.style_combo.findData(dataset.line_style), 0))
        self.style_combo.currentIndexChanged.connect(self._on_style_changed)

        self.status_label = QLabel()
        self.status_label.setObjectName("file-status")
        self.status_label.setWordWrap(True)

        top = QVBoxLayout(self)
        top.setContentsMargins(14, 10, 14, 10)
        top.setSpacing(8)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(12)
        header.addWidget(self.checkbox, stretch=1)
        header.addWidget(self.color_button)
        header.addWidget(self.style_combo)
        top.addLayout(header)
        top.addWidget(self.meta_label)
        top.addWidget(self.status_label)

        self._dataset = dataset
        self.refresh(dataset)

    def refresh(self, dataset: DataSet) -> None:
        self._dataset = dataset
        self.checkbox.blockSignals(True)
        self.checkbox.setChecked(dataset.enabled)
        self.checkbox.setText(dataset.name)
        self.checkbox.blockSignals(False)
        self.meta_label.setText(_build_meta_summary(dataset))
        self._set_color(dataset.color)
        index = self.style_combo.findData(dataset.line_style)
        if index >= 0:
            self.style_combo.blockSignals(True)
            self.style_combo.setCurrentIndex(index)
            self.style_combo.blockSignals(False)
        if dataset.error:
            self.status_label.setText(dataset.error)
            self.status_label.setProperty("alert", True)
        else:
            message = ""
            if not dataset.reference_hit:
                message = "Reference torque not reached"
            self.status_label.setText(message)
            self.status_label.setProperty("alert", bool(message))
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def _set_color(self, color: str) -> None:
        qcolor = QColor(color)
        self.color_button.setStyleSheet(
            f"background-color: {qcolor.name()}; border: 1px solid #c6cfdb; border-radius: 6px;"
        )

    def _choose_color(self) -> None:
        current = QColor(self._dataset.color)
        color = QColorDialog.getColor(current, self, "Select line color")
        if color.isValid():
            self._dataset.color = color.name()
            self._set_color(color.name())
            self.colorChanged.emit(color.name())

    def _on_style_changed(self, index: int) -> None:
        style = self.style_combo.itemData(index)
        if style:
            self.styleChanged.emit(style)


def _build_meta_summary(dataset: DataSet) -> str:
    meta = dataset.metadata
    components = []
    for key in ("Date", "Time", "Tool", "Application"):
        value = meta.get(key)
        if value:
            components.append(f"{key}: {value}")
    return " · ".join(components) if components else ""
