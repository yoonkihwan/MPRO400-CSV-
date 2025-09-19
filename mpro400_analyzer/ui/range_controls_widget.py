from __future__ import annotations

from typing import Optional, Tuple

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)


class RangeControlsWidget(QWidget):
    referenceChanged = Signal(float)
    filtersChanged = Signal(tuple, tuple)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("range-controls")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.reference_spin = QDoubleSpinBox()
        self.reference_spin.setRange(0.0, 10000.0)
        self.reference_spin.setDecimals(2)
        self.reference_spin.setSuffix(" N-m")
        self.reference_spin.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.reference_spin.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.reference_spin.valueChanged.connect(self._on_reference_changed)

        ref_row = QFrame()
        ref_grid = QGridLayout(ref_row)
        ref_grid.setContentsMargins(0, 0, 0, 0)
        ref_grid.setHorizontalSpacing(8)

        ref_label = QLabel("Reference Torque")
        ref_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        unit_label = QLabel("N-m")
        unit_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        hint_label = QLabel("Set to 0 to disable reference.")
        hint_label.setObjectName("reference-hint")

        ref_grid.addWidget(ref_label, 0, 0)
        ref_grid.addWidget(self.reference_spin, 0, 1)
        ref_grid.addWidget(unit_label, 0, 2)
        ref_grid.addWidget(hint_label, 1, 0, 1, 3)
        ref_grid.setColumnStretch(2, 1)

        layout.addWidget(ref_row)

        self.torque_row = _RangeRow("Torque Range", "N-m", -10000.0, 10000.0)
        self.angle_row = _RangeRow("Angle Range", "deg", -3600.0, 3600.0)

        self.torque_row.changed.connect(self._emit_filters)
        self.angle_row.changed.connect(self._emit_filters)

        layout.addWidget(self.torque_row)
        layout.addWidget(self.angle_row)
        layout.addStretch(1)

    def _on_reference_changed(self, value: float) -> None:
        self.referenceChanged.emit(value)
        self._emit_filters()

    def _emit_filters(self) -> None:
        torque = self.torque_row.current_range()
        angle = self.angle_row.current_range()
        self.filtersChanged.emit(torque, angle)

    def reset(self) -> None:
        self.reference_spin.setValue(0.0)
        for row in (self.torque_row, self.angle_row):
            row.setChecked(False)


class _RangeRow(QFrame):
    changed = Signal()

    def __init__(
        self,
        label: str,
        unit: str,
        minimum: float,
        maximum: float,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.checkbox = QCheckBox(label)
        self.checkbox.toggled.connect(self._on_toggle)

        self.min_spin = QDoubleSpinBox()
        self.min_spin.setDecimals(2)
        self.min_spin.setRange(minimum, maximum)
        self.min_spin.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.min_spin.valueChanged.connect(self._on_changed)

        self.max_spin = QDoubleSpinBox()
        self.max_spin.setDecimals(2)
        self.max_spin.setRange(minimum, maximum)
        self.max_spin.setButtonSymbols(QDoubleSpinBox.NoButtons)
        self.max_spin.valueChanged.connect(self._on_changed)

        unit_label = QLabel(unit)
        unit_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(8)
        grid.addWidget(self.checkbox, 0, 0)
        grid.addWidget(QLabel("Min"), 0, 1)
        grid.addWidget(self.min_spin, 0, 2)
        grid.addWidget(QLabel("Max"), 0, 3)
        grid.addWidget(self.max_spin, 0, 4)
        grid.addWidget(unit_label, 0, 5)
        grid.setColumnStretch(5, 1)

        self._on_toggle(False)

    def setEnabled(self, enabled: bool) -> None:  # type: ignore[override]
        super().setEnabled(enabled)
        self.checkbox.setEnabled(enabled)
        self.min_spin.setEnabled(enabled and self.checkbox.isChecked())
        self.max_spin.setEnabled(enabled and self.checkbox.isChecked())

    def setChecked(self, checked: bool) -> None:
        self.checkbox.setChecked(checked)

    def current_range(self) -> Tuple[Optional[float], Optional[float]]:
        if not self.checkbox.isChecked() or not self.isEnabled():
            return (None, None)
        minimum = float(self.min_spin.value())
        maximum = float(self.max_spin.value())
        if minimum > maximum:
            minimum, maximum = maximum, minimum
        return (minimum, maximum)

    def _on_toggle(self, checked: bool) -> None:
        enabled = checked and self.isEnabled()
        self.min_spin.setEnabled(enabled)
        self.max_spin.setEnabled(enabled)
        self.changed.emit()

    def _on_changed(self, _value: float) -> None:
        if self.checkbox.isChecked():
            self.changed.emit()

