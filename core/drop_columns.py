# core/drop_columns.py
from pathlib import Path
import pandas as pd


def _iter_csv_files(path: Path):
    if path.is_file():
        yield path
    else:
        yield from sorted(path.rglob("*.csv"))


def drop_columns(
    input_root: Path,
    output_root: Path,
    columns: list[str],
    sep: str = ";",
):
    """
    Remove selected columns from CSV files.

    Parameters
    ----------
    input_root : Path
        CSV file or directory with CSV files.
    output_root : Path
        Output directory where cleaned files will be written.
    columns : list[str]
        Column names to remove.
    sep : str
        CSV separator.
    """
    input_root = input_root.resolve()
    output_root = output_root.resolve()

    for src in _iter_csv_files(input_root):
        rel_path = src.relative_to(input_root) if input_root.is_dir() else src.name
        dst = output_root / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)

        df = pd.read_csv(src, sep=sep)

        cols_to_drop = [c for c in columns if c in df.columns]
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop)

        df.to_csv(dst, sep=sep, index=False)
