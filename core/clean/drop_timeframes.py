# core/drop_timeframes.py

from pathlib import Path
import shutil
from typing import Iterable


def extract_timeframe(filename: str) -> str | None:
    """
    Extract timeframe token from filename.

    Example:
    GOLD_M15.csv -> M15
    EURUSD_H1.csv -> H1
    """
    stem = Path(filename).stem  # GOLD_M15
    parts = stem.split("_")
    if len(parts) < 2:
        return None
    return parts[-1]


def drop_timeframes(
    input_root: Path,
    output_root: Path,
    timeframes: Iterable[str],
) -> None:
    """
    Remove CSV files whose extracted timeframe matches specified identifiers.
    """

    input_root = input_root.resolve()
    output_root = output_root.resolve()
    tf_set = set(timeframes)

    if not input_root.exists():
        raise FileNotFoundError(f"Input directory does not exist: {input_root}")

    output_root.mkdir(parents=True, exist_ok=True)

    for symbol_dir in input_root.iterdir():
        if not symbol_dir.is_dir():
            continue

        out_symbol_dir = output_root / symbol_dir.name
        out_symbol_dir.mkdir(parents=True, exist_ok=True)

        for file in symbol_dir.iterdir():
            if not file.is_file() or file.suffix.lower() != ".csv":
                continue

            tf = extract_timeframe(file.name)

            if tf in tf_set:
                continue  # drop this timeframe

            shutil.copy2(file, out_symbol_dir / file.name)
