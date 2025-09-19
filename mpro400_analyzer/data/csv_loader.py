from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple

import pandas as pd

try:
    import chardet  # type: ignore
except ImportError:  # pragma: no cover - optional dependency
    chardet = None

METRIC_COLUMNS = ("Angle", "Torque")
OPTIONAL_COLUMNS = ("Time", "Window ID")


@dataclass
class CsvData:
    path: Path
    metadata: Dict[str, str]
    dataframe: pd.DataFrame


class CsvFormatError(Exception):
    """Raised when the CSV structure does not match the documented contract."""


def detect_encoding(path: Path) -> str:
    """Best-effort encoding detection with sensible defaults."""

    default_encoding = "utf-8-sig"
    if chardet is None:
        return default_encoding

    try:
        raw = path.read_bytes()
    except OSError:
        return default_encoding

    result = chardet.detect(raw)
    encoding = result.get("encoding") if isinstance(result, dict) else None
    if not encoding:
        return default_encoding
    return encoding


def _extract_metadata(lines: list[str]) -> Tuple[Dict[str, str], int]:
    metadata: Dict[str, str] = {}
    header_index = -1

    for idx, raw_line in enumerate(lines):
        line = raw_line.strip()
        if not line:
            continue
        parts = [part.strip() for part in raw_line.split(";")]
        if parts and parts[0].lower() == "angle":
            header_index = idx
            break
        if parts and parts[0]:
            value = parts[1] if len(parts) > 1 else ""
            metadata[parts[0]] = value

    if header_index == -1:
        raise CsvFormatError("Angle/Torque header row not found")

    return metadata, header_index


def load_csv(path: Path) -> CsvData:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    encoding = detect_encoding(path)
    try:
        text = path.read_text(encoding=encoding)
    except (UnicodeDecodeError, OSError):
        # Fall back to cp949 which is common for legacy MPRO exports.
        encoding = "cp949"
        text = path.read_text(encoding=encoding)

    lines = text.splitlines()
    metadata, header_index = _extract_metadata(lines)

    df = pd.read_csv(
        path,
        sep=";",
        decimal=",",
        skiprows=header_index,
        header=0,
        encoding=encoding,
        engine="python",
        on_bad_lines="skip",
    )

    df = df.rename(columns=lambda name: str(name).strip())

    missing = [col for col in METRIC_COLUMNS if col not in df.columns]
    if missing:
        raise CsvFormatError(f"Required columns missing: {missing}")

    for col in METRIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    for optional in OPTIONAL_COLUMNS:
        if optional in df.columns and df[optional].dtype == object:
            cleaned = df[optional].astype(str).str.replace(",", ".")
            df[optional] = pd.to_numeric(cleaned, errors="ignore")

    df = df.dropna(subset=list(METRIC_COLUMNS))
    df = df.reset_index(drop=True)

    metadata.setdefault("File", path.name)

    return CsvData(path=path, metadata=metadata, dataframe=df)
