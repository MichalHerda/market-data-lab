import os
import pandas as pd
from datetime import datetime
import libs.csv_utils as cu
import libs.file_utils as fu


def parse_datetime_input(text: str):
    """Try to parse flexible datetime input like:
    2024-02-25
    2024-02-25 01
    2024-02-25 01:00
    2024-02-25 01:00:00
    """
    if not text.strip():
        return None
    formats = [
        "%Y-%m-%d",
        "%Y-%m-%d %H",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S"
    ]
    for fmt in formats:
        try:
            return datetime.strptime(text.strip(), fmt)
        except ValueError:
            continue
    print(f"⚠️  Could not parse '{text}'. Expected formats like YYYY-MM-DD or YYYY-MM-DD HH[:MM[:SS]]")
    return None


def detect_time_column(df):
    """Detect time column"""
    candidates = [c for c in df.columns if c.lower() in ("date", "time", "timestamp")]
    if not candidates:
        raise ValueError("No valid time column found (expected 'date', 'timestamp' or 'time').")
    return candidates[0]


def filter_time_range(df: pd.DataFrame, time_col: str, start_dt, end_dt):
    """Filter DataFrame rows between start and end datetimes"""
    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")

    mask = pd.Series(True, index=df.index)

    if start_dt:
        mask &= df[time_col] >= start_dt
    if end_dt:
        mask &= df[time_col] <= end_dt

    filtered = df.loc[mask]
    return filtered


def process_csv(file_path: str, start_dt, end_dt, output_folder: str = None):
    """Process single CSV file"""
    try:
        df = cu.load_csv(file_path, sep=";")
    except Exception as e:
        print(f"Could not load {file_path}: {e}")
        return

    try:
        time_col = detect_time_column(df)
    except ValueError as e:
        print(f"{e} in {file_path}. Skipped.")
        return

    before = len(df)
    df_filtered = filter_time_range(df, time_col, start_dt, end_dt)
    after = len(df_filtered)

    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        save_path = os.path.join(output_folder, os.path.basename(file_path))
    else:
        save_path = file_path

    cu.save_csv(df_filtered, save_path, sep=";")
    print(
        f"Processed {os.path.basename(file_path)}: {before} → {after} rows "
        f"({after / before * 100:.1f}% kept). Saved to {save_path}"
    )


def main():
    input_path = fu.get_valid_path("Enter path to CSV file or folder: ")

    print("\nEnter time range filters (leave empty to skip):")
    start_input = input("From (YYYY-MM-DD [HH[:MM[:SS]]]): ").strip()
    end_input = input("To   (YYYY-MM-DD [HH[:MM[:SS]]]): ").strip()

    start_dt = parse_datetime_input(start_input)
    end_dt = parse_datetime_input(end_input)

    print("\nWhat would you like to do with the result?")
    print(" 1. Overwrite original files")
    print(" 2. Save filtered files in a new folder")
    action = input("Your choice (1/2): ").strip()

    output_folder = None
    if action == "2":
        output_folder = input("Enter path for output folder: ").strip()
        os.makedirs(output_folder, exist_ok=True)

    if os.path.isfile(input_path) and input_path.endswith(".csv"):
        process_csv(input_path, start_dt, end_dt, output_folder)
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.endswith(".csv"):
                    process_csv(os.path.join(root, f), start_dt, end_dt, output_folder)
    else:
        print("Invalid path. Must be a .csv file or folder containing .csv files.")


if __name__ == "__main__":
    main()
