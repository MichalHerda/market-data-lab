import pandas as pd
from pathlib import Path


def load_csv(file_path: str, sep: str = ";") -> pd.DataFrame:
    """
    Load a CSV file into a DataFrame.
    Default separator is ';' to match MT4/MT5 OHLCV exports.
    """
    return pd.read_csv(file_path, sep=sep)


def validate_structure(df1: pd.DataFrame, df2: pd.DataFrame) -> None:
    """
    Ensure that two DataFrames have the same columns in the same order.
    Raises ValueError if structures differ.
    """
    if list(df1.columns) != list(df2.columns):
        raise ValueError("CSV files do not have matching column structures.")


def merge_csv_files(
    file1: str,
    file2: str,
    drop_duplicates: bool = True,
    validate_structures: bool = True,
    sep: str = ";"
) -> pd.DataFrame:
    """
    Merge two CSV files with OHLCV data into a single DataFrame.

    Args:
        file1 (str): Path to the first CSV file.
        file2 (str): Path to the second CSV file.
        drop_duplicates (bool): If True, remove duplicate rows.
        validate_structures (bool): If True, validate column structures
                                    before merging.
        sep (str): CSV separator (default: ';').

    Returns:
        pd.DataFrame: Merged DataFrame.
    """
    df1 = load_csv(file1, sep=sep)
    df2 = load_csv(file2, sep=sep)

    if validate_structures:
        validate_structure(df1, df2)

    merged = pd.concat([df1, df2], ignore_index=True)

    if drop_duplicates:
        merged = merged.drop_duplicates()

    return merged


def save_csv(df: pd.DataFrame, output_path: str, sep: str = ";") -> None:
    """
    Save DataFrame to a CSV file.
    Ensures parent directories exist.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, sep=sep, index=False)
