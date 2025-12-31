from pathlib import Path
import pandas as pd

TIME_COL_CANDIDATES = ("date", "time", "timestamp")
TF_ORDER = ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"]


def detect_time_column(df: pd.DataFrame) -> str:
    for c in df.columns:
        if c.lower() in TIME_COL_CANDIDATES:
            return c
    raise ValueError("No valid time column found")


def extract_symbol_tf(path: Path):
    parts = path.stem.split("_")
    if len(parts) < 2:
        return path.stem, None
    return "_".join(parts[:-1]), parts[-1].upper()


def merge_symbol(files: list[Path]) -> pd.DataFrame:
    merged = None
    time_col = None

    for f in sorted(files):
        symbol, tf = extract_symbol_tf(f)
        if not tf:
            continue

        df = pd.read_csv(f, sep=";")

        if time_col is None:
            time_col = detect_time_column(df)

        df[time_col] = pd.to_datetime(df[time_col])
        df = df.rename(
            columns=lambda c: c if c == time_col else f"{c}_{tf}"
        )

        merged = df if merged is None else pd.merge(
            merged, df, on=time_col, how="outer"
        )

    if merged is None:
        raise ValueError("Nothing to merge")

    # sort by time
    merged = merged.sort_values(time_col).ffill().reset_index(drop=True)

    # reorder columns: time first, then by TF_ORDER
    tf_cols = {tf: [] for tf in TF_ORDER}
    for col in merged.columns:
        if col == time_col:
            continue
        for tf in TF_ORDER:
            if col.endswith(f"_{tf}"):
                tf_cols[tf].append(col)
                break

    ordered_cols = [time_col] + [c for tf in TF_ORDER for c in tf_cols[tf]]
    merged = merged[ordered_cols]

    return merged


def merge_timeframes(
    input_root: Path,
    output_root: Path | None = None,
):
    if output_root:
        output_root.mkdir(parents=True, exist_ok=True)

    csv_files = list(input_root.rglob("*.csv"))
    if not csv_files:
        raise ValueError("No CSV files found")

    groups: dict[str, list[Path]] = {}
    for f in csv_files:
        symbol, _ = extract_symbol_tf(f)
        groups.setdefault(symbol, []).append(f)

    for symbol, files in groups.items():
        merged = merge_symbol(files)
        out_dir = output_root or input_root
        out_path = out_dir / f"{symbol}_merged.csv"
        merged.to_csv(out_path, sep=";", index=False)
