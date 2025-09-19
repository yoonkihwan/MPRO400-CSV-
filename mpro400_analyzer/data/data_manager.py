from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import pandas as pd
import numpy as np

from .csv_loader import CsvData, CsvFormatError, load_csv

DEFAULT_COLORS = [
    "#4aa8ff",
    "#7bd87b",
    "#ffd166",
    "#ff7b7b",
    "#c792ea",
    "#64dfdf",
    "#ffa69e",
    "#80ed99",
    "#9d4edd",
    "#48bfe3",
]
LINE_STYLES = ["solid", "dash", "dot"]


@dataclass
class PlotPayload:
    label: str
    x: List[float]
    y: List[float]
    color: str
    line_style: str
    reference_hit: bool


@dataclass
class DataSet:
    identifier: int
    csv: CsvData
    enabled: bool = True
    color: str = DEFAULT_COLORS[0]
    line_style: str = LINE_STYLES[0]
    reference_hit: bool = True
    error: Optional[str] = None

    @property
    def name(self) -> str:
        return self.csv.path.name

    @property
    def metadata(self) -> Dict[str, str]:
        return self.csv.metadata

    @property
    def dataframe(self) -> pd.DataFrame:
        return self.csv.dataframe


class DataManager:
    MAX_FILES = 20

    def __init__(self) -> None:
        self._datasets: List[DataSet] = []
        self.reference_torque: float = 0.0
        self.torque_range: Tuple[Optional[float], Optional[float]] = (None, None)
        self.angle_range: Tuple[Optional[float], Optional[float]] = (None, None)
        self._id_counter = 0
        self.selected_id: Optional[int] = None

    # ------------------------------------------------------------------
    # Loading & bookkeeping
    # ------------------------------------------------------------------
    def clear(self) -> None:
        self._datasets.clear()
        self._id_counter = 0
        self.selected_id = None

    def load(self, paths: Sequence[Path], append: bool = False) -> List[str]:
        warnings: List[str] = []
        if not append:
            self.clear()

        for raw_path in paths:
            if len(self._datasets) >= self.MAX_FILES:
                warnings.append("파일은 최대 20개까지만 불러올 수 있습니다.")
                break

            path = Path(raw_path)
            try:
                csv = load_csv(path)
            except (FileNotFoundError, CsvFormatError) as exc:
                warnings.append(f"{path.name}: {exc}")
                continue

            dataset = DataSet(
                identifier=self._next_id(),
                csv=csv,
                color=self._color_for_index(len(self._datasets)),
            )
            self._datasets.append(dataset)
            self.selected_id = dataset.identifier

        return warnings

    def _next_id(self) -> int:
        self._id_counter += 1
        return self._id_counter

    def _color_for_index(self, index: int) -> str:
        if not DEFAULT_COLORS:
            return "#4aa8ff"
        return DEFAULT_COLORS[index % len(DEFAULT_COLORS)]

    # ------------------------------------------------------------------
    # State mutation helpers
    # ------------------------------------------------------------------
    def set_enabled(self, identifier: int, enabled: bool) -> None:
        dataset = self._find(identifier)
        if dataset:
            dataset.enabled = enabled

    def set_color(self, identifier: int, color: str) -> None:
        dataset = self._find(identifier)
        if dataset:
            dataset.color = color

    def set_line_style(self, identifier: int, style: str) -> None:
        if style not in LINE_STYLES:
            return
        dataset = self._find(identifier)
        if dataset:
            dataset.line_style = style

    def set_selected(self, identifier: Optional[int]) -> None:
        self.selected_id = identifier

    def remove(self, identifier: int) -> None:
        dataset = self._find(identifier)
        if not dataset:
            return
        self._datasets = [d for d in self._datasets if d.identifier != identifier]
        if self.selected_id == identifier:
            self.selected_id = self._datasets[0].identifier if self._datasets else None

    def update_reference(self, value: float) -> None:
        self.reference_torque = max(0.0, float(value))

    def update_ranges(
        self,
        torque: Tuple[Optional[float], Optional[float]],
        angle: Tuple[Optional[float], Optional[float]],
    ) -> None:
        self.torque_range = torque
        self.angle_range = angle

    # ------------------------------------------------------------------
    # Query APIs
    # ------------------------------------------------------------------
    def datasets(self) -> List[DataSet]:
        return list(self._datasets)

    def selected_dataset(self) -> Optional[DataSet]:
        if self.selected_id is None:
            return None
        return self._find(self.selected_id)

    def plot_payloads(self) -> List[PlotPayload]:
        payloads: List[PlotPayload] = []
        for dataset in self._datasets:
            if not dataset.enabled:
                continue
            payload = self._build_payload(dataset)
            if payload is not None:
                payloads.append(payload)
        return payloads

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_payload(self, dataset: DataSet) -> Optional[PlotPayload]:
        df = self._strip_reference_rows(dataset.dataframe)
        if df.empty:
            dataset.error = "데이터가 비어 있습니다."
            return None

        angles, reference_hit = self._correct_angles(df)
        dataset.reference_hit = reference_hit
        dataset.error = None if reference_hit or self.reference_torque <= 0 else "기준 토크 미달"

        mask = pd.Series(True, index=df.index)

        tmin, tmax = self.torque_range
        if tmin is not None:
            mask &= df["Torque"] >= tmin
        if tmax is not None:
            mask &= df["Torque"] <= tmax

        amin, amax = self.angle_range
        if amin is not None:
            mask &= angles >= amin
        if amax is not None:
            mask &= angles <= amax

        filtered_index = df.index[mask]
        if filtered_index.empty:
            return PlotPayload(
                label=dataset.name,
                x=[],
                y=[],
                color=dataset.color,
                line_style=dataset.line_style,
                reference_hit=reference_hit,
            )

        x_values = angles.loc[filtered_index].astype(float).tolist()
        y_values = df.loc[filtered_index, "Torque"].astype(float).tolist()

        return PlotPayload(
            label=dataset.name,
            x=x_values,
            y=y_values,
            color=dataset.color,
            line_style=dataset.line_style,
            reference_hit=reference_hit,
        )

    def _strip_reference_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        window_col = None
        for column in df.columns:
            normalized = ''.join(ch.lower() for ch in column if ch.isalnum())
            if not normalized:
                continue
            if normalized == 'windowid':
                window_col = column
                break
            if normalized.startswith('windowid') and window_col is None:
                window_col = column
            elif normalized.startswith('window') and window_col is None:
                window_col = column

        if window_col is not None:
            window_values = pd.to_numeric(df[window_col], errors='coerce')
            mask = window_values.isna() | (window_values == 0)
            if not mask.all():
                df = df.loc[mask].copy()

        return self._select_primary_angle_segment(df)


    def _select_primary_angle_segment(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or 'Angle' not in df.columns or 'Torque' not in df.columns:
            return df

        angles = pd.to_numeric(df['Angle'], errors='coerce')
        if angles.isna().all():
            return df

        angle_values = angles.to_numpy()
        if angle_values.size == 0:
            return df

        decreases = np.where(np.diff(angle_values) <= 0)[0] + 1
        if decreases.size == 0:
            return df

        segments = []
        start = 0
        for stop in decreases:
            segment = df.iloc[start:stop].copy()
            if not segment.empty:
                segments.append(segment)
            start = int(stop)
        tail = df.iloc[start:].copy()
        if not tail.empty:
            segments.append(tail)

        if not segments:
            return df

        def segment_score(segment: pd.DataFrame) -> tuple:
            torque = pd.to_numeric(segment['Torque'], errors='coerce')
            if torque.isna().all():
                return (0.0, len(segment))
            torque_range = torque.max() - torque.min()
            return (float(torque_range), len(segment))

        primary = max(segments, key=segment_score)
        return primary

    def _correct_angles(self, df: pd.DataFrame) -> Tuple[pd.Series, bool]:
        angles = df["Angle"].astype(float)
        if self.reference_torque <= 0:
            return angles, True

        hits = df[df["Torque"] >= self.reference_torque]
        if hits.empty:
            return angles, False

        angle0 = hits.iloc[0]["Angle"]
        corrected = angles - angle0
        return corrected, True

    def _find(self, identifier: int) -> Optional[DataSet]:
        for dataset in self._datasets:
            if dataset.identifier == identifier:
                return dataset
        return None


__all__ = [
    "DataManager",
    "DataSet",
    "PlotPayload",
    "LINE_STYLES",
]














