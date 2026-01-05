from pathlib import Path
from datetime import datetime
import pandas as pd

TIME_COL_CANDIDATES = ("date", "time", "timestamp")


def _iter_csv_files(path: Path):
    if path.is_file():
        yield path
    else:
        yield from sorted(path.rglob("*.csv"))


def _detect_time_column(df: pd.DataFrame) -> str:
    for c in df.columns:
        if c.lower() in TIME_COL_CANDIDATES:
            return c
    raise ValueError("No valid time column found (date, time, timestamp).")


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None

    formats = (
        "%Y-%m-%d",
        "%Y-%m-%d %H",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
    )

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    raise ValueError(
        f"Invalid datetime format: '{value}'. "
        "Expected YYYY-MM-DD [HH[:MM[:SS]]]"
    )


def slice_time(
    input_root: Path,
    output_root: Path,
    start: str | None = None,
    end: str | None = None,
    sep: str = ";",
):
    """
    Filter CSV rows by datetime range.
    """
    start_dt = parse_datetime(start)
    end_dt = parse_datetime(end)

    input_root = input_root.resolve()
    output_root = output_root.resolve()

    for src in _iter_csv_files(input_root):
        rel = src.relative_to(input_root) if input_root.is_dir() else src.name
        dst = output_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)

        df = pd.read_csv(src, sep=sep)
        time_col = _detect_time_column(df)

        df[time_col] = pd.to_datetime(df[time_col], errors="coerce")

        mask = pd.Series(True, index=df.index)
        if start_dt:
            mask &= df[time_col] >= start_dt
        if end_dt:
            mask &= df[time_col] <= end_dt

        df.loc[mask].to_csv(dst, sep=sep, index=False)
