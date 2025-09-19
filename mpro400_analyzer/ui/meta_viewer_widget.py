from __future__ import annotations

from typing import Dict, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class MetaViewerWidget(QWidget):
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        title = QLabel("메타 정보")
        title.setObjectName("meta-title")
        layout.addWidget(title)

        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["항목", "값"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)
        layout.addWidget(self.table, stretch=1)

    def set_metadata(self, metadata: Optional[Dict[str, str]]) -> None:
        self.table.setRowCount(0)
        if not metadata:
            return

        for row, (key, value) in enumerate(metadata.items()):
            self.table.insertRow(row)
            key_item = QTableWidgetItem(str(key))
            value_item = QTableWidgetItem(str(value))
            self.table.setItem(row, 0, key_item)
            self.table.setItem(row, 1, value_item)
