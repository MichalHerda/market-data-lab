# core/validate_structure.py
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd


TIME_COL_CANDIDATES = ("date", "time", "timestamp")


def gather_csv_files(root: Path) -> List[Path]:
    """Recursively collect all CSV files under root."""
    return sorted(root.rglob("*.csv"))


def load_columns(path: Path) -> Tuple[str, ...]:
    """Load CSV file and return column names."""
    df = pd.read_csv(path, sep=";")
    return tuple(df.columns)


def validate_csv_structure(root: Path) -> Dict:
    """
    Validate column structure of all CSV files under root.

    Returns:
        {
            "all_same": bool,
            "reference": List[str] | None,
            "differences": {
                path: {
                    "missing": set[str],
                    "extra": set[str],
                    "order_diff": bool,
                }
            },
            "load_errors": {path: error}
        }
    """
    csv_files = gather_csv_files(root)
    if not csv_files:
        raise ValueError("No CSV files found")

    structures: Dict[Path, Tuple[str, ...]] = {}
    load_errors: Dict[Path, str] = {}

    for path in csv_files:
        try:
            structures[path] = load_columns(path)
        except Exception as exc:
            load_errors[path] = str(exc)

    if not structures:
        raise ValueError("No valid CSV files to validate")

    # find most common structure
    freq: Dict[Tuple[str, ...], int] = {}
    for cols in structures.values():
        freq[cols] = freq.get(cols, 0) + 1

    reference = max(freq.items(), key=lambda x: x[1])[0]
    ref_set = set(reference)

    differences = {}

    for path, cols in structures.items():
        cols_set = set(cols)
        missing = ref_set - cols_set
        extra = cols_set - ref_set
        order_diff = not missing and not extra and cols != reference

        if missing or extra or order_diff:
            differences[path] = {
                "missing": missing,
                "extra": extra,
                "order_diff": order_diff,
            }

    return {
        "all_same": not differences,
        "reference": list(reference),
        "differences": differences,
        "load_errors": load_errors,
    }
