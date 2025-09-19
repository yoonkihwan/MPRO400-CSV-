from pathlib import Path

import pandas as pd
import pytest

from data.csv_loader import CsvFormatError, load_csv


def test_load_csv_parses_metadata_and_data():
    sample = Path(__file__).resolve().parent / "data" / "sample.csv"
    csv_data = load_csv(sample)

    assert csv_data.metadata["Date"] == "12.09.25"
    assert csv_data.metadata["Tool"] == "01"

    df = csv_data.dataframe
    assert list(df.columns)[:2] == ["Angle", "Torque"]
    assert len(df) == 4
    assert pd.api.types.is_float_dtype(df["Angle"])
    assert pd.api.types.is_float_dtype(df["Torque"])


def test_missing_header_raises(tmp_path):
    broken = tmp_path / "broken.csv"
    broken.write_text("Station;\nFoo;Bar", encoding="utf-8")

    with pytest.raises(CsvFormatError):
        load_csv(broken)
