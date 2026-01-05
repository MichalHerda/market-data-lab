# core/detect_gaps.py

from __future__ import annotations

from pathlib import Path
from datetime import timedelta
import pandas as pd


TIMEFRAME_DELTAS = {
    "M1": timedelta(minutes=1),
    "M5": timedelta(minutes=5),
    "M15": timedelta(minutes=15),
    "M30": timedelta(minutes=30),
    "H1": timedelta(hours=1),
    "H4": timedelta(hours=4),
    "D1": timedelta(days=1),
    "W1": timedelta(weeks=1),
}

TIME_COLUMNS = ("timestamp", "time", "datetime", "date")


def _extract_timeframe(path: Path) -> str | None:
    for tf in TIMEFRAME_DELTAS:
        if tf in path.stem:
            return tf
    return None


def _read_csv(csv_path: Path) -> pd.DataFrame:
    """
    Read CSV using MT4/MT5-compatible defaults.
    """
    return pd.read_csv(csv_path, sep=";")


def _detect_time_column(df: pd.DataFrame, path: Path) -> str:
    normalized = {
        col.strip().lower(): col
        for col in df.columns
    }

    for candidate in TIME_COLUMNS:
        if candidate in normalized:
            return normalized[candidate]

    raise ValueError(
        f"No valid time column found in {path}.\n"
        f"Available columns: {list(df.columns)}\n"
        f"Expected one of (case-insensitive): {', '.join(TIME_COLUMNS)}"
    )


def _format_days_of_week(start: pd.Timestamp, end: pd.Timestamp) -> str:
    days = pd.date_range(start.date(), end.date(), freq="D").day_name().str.lower()
    days = [d[:3] for d in days]

    if len(days) == 1:
        return days[0]
    return f"{days[0]} - {days[-1]}"


def detect_time_gaps(
    input_root: Path,
    output_root: Path,
) -> None:
    """
    Detect time gaps in OHLCV CSV files.
    """
    input_root = input_root.resolve()
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    for symbol_dir in sorted(p for p in input_root.iterdir() if p.is_dir()):
        out_symbol = output_root / symbol_dir.name
        out_symbol.mkdir(exist_ok=True)

        for csv_path in sorted(symbol_dir.glob("*.csv")):
            tf = _extract_timeframe(csv_path)
            if tf not in TIMEFRAME_DELTAS:
                continue

            df = _read_csv(csv_path)
            time_col = _detect_time_column(df, csv_path)

            df[time_col] = pd.to_datetime(df[time_col])
            df = df.sort_values(time_col)

            expected_delta = TIMEFRAME_DELTAS[tf]

            gaps = []
            prev_ts = None
            idx = 1

            for ts in df[time_col]:
                if prev_ts is not None:
                    delta = ts - prev_ts
                    if delta > expected_delta:
                        gaps.append(
                            {
                                "id": idx,
                                "begin": prev_ts,
                                "end": ts,
                                "days_of_week": _format_days_of_week(prev_ts, ts),
                            }
                        )
                        idx += 1
                prev_ts = ts

            if gaps:
                out_file = out_symbol / f"{tf}_gaps.csv"
                pd.DataFrame(gaps).to_csv(out_file, index=False)
