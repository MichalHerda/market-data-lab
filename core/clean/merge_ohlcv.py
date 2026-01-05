# core/merge_ohlcv.py

from pathlib import Path
import pandas as pd

TIME_COL_CANDIDATES = ("date", "time", "timestamp")


def detect_time_column(df: pd.DataFrame) -> str:
    for c in df.columns:
        if c.lower() in TIME_COL_CANDIDATES:
            return c
    raise ValueError("No valid time column found")


def merge_csv(file1: Path, file2: Path) -> pd.DataFrame:
    """
    Merge two OHLCV CSV files by patching missing data on a common time axis.

    Semantics:
    - same schema expected
    - values from file1 take priority
    - missing rows / values are filled from file2
    """

    df1 = pd.read_csv(file1, sep=";")
    df2 = pd.read_csv(file2, sep=";")

    time_col1 = detect_time_column(df1)
    time_col2 = detect_time_column(df2)

    if time_col1 != time_col2:
        raise ValueError(
            f"Time column mismatch: {file1} ({time_col1}) vs {file2} ({time_col2})"
        )

    time_col = time_col1

    df1[time_col] = pd.to_datetime(df1[time_col])
    df2[time_col] = pd.to_datetime(df2[time_col])

    # set time as index
    df1 = df1.set_index(time_col)
    df2 = df2.set_index(time_col)

    # patch missing values instead of duplicating columns
    merged = df1.combine_first(df2)

    # restore time column
    merged = merged.sort_index().reset_index()

    return merged


def list_structure(folder: Path) -> dict[str, list[str]]:
    """Return dict {relative_subfolder: [csv files]}"""
    struct: dict[str, list[str]] = {}
    for path in folder.rglob("*.csv"):
        rel = path.parent.relative_to(folder)
        struct.setdefault(str(rel), []).append(path.name)
    return struct


def merge_folders(folder1: Path, folder2: Path, output_base: Path) -> None:
    folder1 = folder1.resolve()
    folder2 = folder2.resolve()
    output_base = output_base.resolve()

    struct1 = list_structure(folder1)
    struct2 = list_structure(folder2)

    common_subfolders = set(struct1) & set(struct2)
    if not common_subfolders:
        print("No common subfolders found.")
        return

    for sub in sorted(common_subfolders):
        files1 = set(struct1[sub])
        files2 = set(struct2[sub])
        common_files = sorted(files1 & files2)

        for fname in common_files:
            path1 = folder1 / sub / fname
            path2 = folder2 / sub / fname

            print(f"Merging: {path1} + {path2}")

            try:
                merged = merge_csv(path1, path2)
                out_path = output_base / sub / fname
                out_path.parent.mkdir(parents=True, exist_ok=True)
                merged.to_csv(out_path, sep=";", index=False)
                print(f"Saved: {out_path}")
            except Exception as e:
                print(f"Error merging {fname}: {e}")

    print("\nAll possible files have been processed.")
