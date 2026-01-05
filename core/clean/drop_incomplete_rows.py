# core/drop_incomplete_rows.py
from pathlib import Path
import pandas as pd


def _process_file(input_path: Path, output_path: Path):
    df = pd.read_csv(input_path, sep=";")

    before = len(df)
    df = df.dropna()
    after = len(df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, sep=";", index=False)

    return before, after


def drop_incomplete_rows(input_root: Path, output_root: Path):
    """
    Remove rows containing any NaN values from all CSV files.

    - input_root: directory with CSV files
    - output_root: directory for cleaned output
    """
    input_root = input_root.resolve()
    output_root = output_root.resolve()

    csv_files = list(input_root.rglob("*.csv"))
    if not csv_files:
        raise ValueError(f"No CSV files found in {input_root}")

    for csv_path in csv_files:
        rel_path = csv_path.relative_to(input_root)
        out_path = output_root / rel_path

        before, after = _process_file(csv_path, out_path)
        print(
            f"{rel_path}: {before} → {after} rows "
            f"({(after / before * 100) if before else 0:.1f}% kept)"
        )
