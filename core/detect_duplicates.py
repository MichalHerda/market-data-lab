from pathlib import Path
from typing import Dict, List
import pandas as pd


TIME_COL_CANDIDATES = ("timestamp", "time", "date", "datetime")


def detect_time_column(df: pd.DataFrame) -> str:
    """Detect time-related column in DataFrame."""
    for col in df.columns:
        if col.lower() in TIME_COL_CANDIDATES:
            return col
    raise ValueError("No time column found")


def detect_timestamp_duplicates(
    input_root: Path,
    *,
    generate_report: bool = True,
    report_path: Path | None = None,
) -> Dict[str, List[str]]:
    """
    Detect duplicate timestamps in CSV files under input_root.

    Returns:
        dict: {relative_path: [timestamp, ...]}
    """
    results: Dict[str, List[str]] = {}

    csv_files = list(input_root.rglob("*.csv"))
    if not csv_files:
        return results

    for path in csv_files:
        try:
            df = pd.read_csv(path, sep=";")
        except Exception:
            continue

        try:
            time_col = detect_time_column(df)
        except ValueError:
            continue

        ts = df[time_col]
        dup = ts[ts.duplicated()]

        if not dup.empty:
            rel = str(path.relative_to(input_root))
            results[rel] = sorted(set(dup.astype(str)))

    if generate_report:
        if report_path is None:
            report_path = input_root / "timestamp_duplicates_report.csv"

        rows = []
        for file, timestamps in results.items():
            for ts in timestamps:
                rows.append(
                    {
                        "file": file,
                        "timestamp": ts,
                    }
                )

        if rows:
            pd.DataFrame(rows).to_csv(report_path, sep=";", index=False)

    return results
