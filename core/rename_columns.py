from pathlib import Path
import pandas as pd


def _iter_csv_files(path: Path):
    if path.is_file():
        yield path
    else:
        yield from sorted(path.rglob("*.csv"))


def rename_columns(
    input_root: Path,
    output_root: Path,
    rename_map: dict[str, str],
    sep: str = ";",
):
    """
    Rename specified columns in CSV files.

    Parameters
    ----------
    input_root : Path
        CSV file or directory.
    output_root : Path
        Output directory where renamed files will be saved.
    rename_map : dict[str,str]
        Mapping old_name -> new_name
    sep : str
        CSV separator
    """
    input_root = input_root.resolve()
    output_root = output_root.resolve()

    for src in _iter_csv_files(input_root):
        rel_path = src.relative_to(input_root) if input_root.is_dir() else src.name
        dst = output_root / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)

        df = pd.read_csv(src, sep=sep)
        existing_map = {k: v for k, v in rename_map.items() if k in df.columns}
        if existing_map:
            df.rename(columns=existing_map, inplace=True)

        df.to_csv(dst, sep=sep, index=False)
