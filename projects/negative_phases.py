# projects/negative_phases.py
import os
import pandas as pd
from typing import List, Dict, Optional
import libs.csv_utils as cu
import libs.file_utils as fu


def detect_time_column(df: pd.DataFrame) -> str:
    """Detect which column should be used as time index (date/timestamp/time)."""
    for c in df.columns:
        if c.lower() in ("date", "timestamp", "time"):
            return c
    raise ValueError("No valid time column found (expected 'date', 'timestamp' or 'time').")


def find_low_column(df: pd.DataFrame) -> Optional[str]:
    """Try to find a column that represents 'low' (case-insensitive)."""
    for c in df.columns:
        if c.lower() == "low":
            return c
    # fallback: common variants
    for c in df.columns:
        if "low" in c.lower():
            return c
    return None


def find_negative_phases(df: pd.DataFrame, deviation_col: str, price_col: Optional[str] = None) -> List[Dict]:
    """
    Identify ranges where 'deviation_col' goes from positive -> negative -> positive.
    Returns list of dicts with keys: startDate, endDate, lowestPrice, biggestMADeviation.
    """
    results: List[Dict] = []

    # ensure numeric deviation column
    series = pd.to_numeric(df[deviation_col], errors="coerce")

    # detect time column and ensure datetime
    time_col = detect_time_column(df)
    timestamps = pd.to_datetime(df[time_col], errors="coerce")

    # ensure price_col if provided exists; otherwise try to detect
    if price_col and price_col not in df.columns:
        price_col = None
    if price_col is None:
        price_col = find_low_column(df)

    in_negative = False
    start_idx: Optional[int] = None

    # iterate rows by integer position
    for i in range(1, len(series)):
        prev_val = series.iloc[i - 1]
        curr_val = series.iloc[i]

        # skip if either is NaN
        if pd.isna(prev_val) or pd.isna(curr_val):
            continue

        # start: prev > 0 and curr < 0
        if not in_negative and prev_val > 0 and curr_val < 0:
            in_negative = True
            start_idx = i  # start at current (first negative)
            continue

        # end: prev < 0 and curr > 0
        if in_negative and prev_val < 0 and curr_val > 0 and start_idx is not None:
            end_idx = i - 1  # last negative index
            # slice inclusive start_idx..end_idx
            sub_df = df.iloc[start_idx:end_idx + 1].copy()
            sub_series = series.iloc[start_idx:end_idx + 1]

            start_date = timestamps.iloc[start_idx]
            end_date = timestamps.iloc[end_idx]

            lowest_price = None
            if price_col and price_col in sub_df.columns:
                lowest_price = pd.to_numeric(sub_df[price_col], errors="coerce").min()

            biggest_ma_dev = sub_series.min()  # most negative in range

            results.append({
                "startDate": start_date,
                "endDate": end_date,
                "lowestPrice": lowest_price,
                "biggestMADeviation": biggest_ma_dev
            })

            # reset
            in_negative = False
            start_idx = None

    return results


def process_csv(file_path: str, deviation_col: str, output_folder: str):
    """Process a single CSV file and write negative phases CSV to output_folder."""
    try:
        df = cu.load_csv(file_path, sep=";")
    except Exception as e:
        print(f"Could not load {file_path}: {e}")
        return

    if deviation_col not in df.columns:
        print(f"Column '{deviation_col}' not found in {file_path}. Skipped.")
        return

    try:
        # validate that we have a time column
        _ = detect_time_column(df)
    except ValueError as e:
        print(f"{e} in {file_path}. Skipped.")
        return

    results = find_negative_phases(df, deviation_col)

    if not results:
        print(f"No negative phases found in {os.path.basename(file_path)}.")
        return

    result_df = pd.DataFrame(results)

    os.makedirs(output_folder, exist_ok=True)
    base_name = os.path.basename(file_path)
    symbol_name = base_name.replace(".csv", "")
    save_path = os.path.join(output_folder, f"{symbol_name}_negative_phases.csv")

    cu.save_csv(result_df, save_path, sep=";")
    print(f"Saved results for {symbol_name} to {save_path} ({len(result_df)} segments).")


def find_first_sample_csv(path: str) -> Optional[str]:
    """Return first CSV path under `path` (if file -> return it; if folder -> search recursively)."""
    if os.path.isfile(path) and path.lower().endswith(".csv"):
        return path
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for f in files:
                if f.lower().endswith(".csv"):
                    return os.path.join(root, f)
    return None


def main():
    print("This script identifies negative phases in a numeric column (e.g., MA_Deviation).")
    input_path = fu.get_valid_path("Enter path to CSV file or folder: ")

    # show sample columns from first available CSV
    sample = find_first_sample_csv(input_path)
    if sample:
        try:
            df_sample = cu.load_csv(sample, sep=";")
            print("\nAvailable columns in sample file:")
            for col in df_sample.columns:
                print(" -", col)
        except Exception as e:
            print(f"Could not read sample file {sample}: {e}")

    deviation_col = input("\nEnter the column name for MA deviation (e.g. MA_Deviation): ").strip()
    output_folder = input("\nEnter output folder path to save results: ").strip()
    if not output_folder:
        print("No output folder provided. Exiting.")
        return
    os.makedirs(output_folder, exist_ok=True)

    # process single file or all CSVs under folder
    if os.path.isfile(input_path) and input_path.lower().endswith(".csv"):
        process_csv(input_path, deviation_col, output_folder)
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.lower().endswith(".csv"):
                    process_csv(os.path.join(root, f), deviation_col, output_folder)
    else:
        print("Invalid path. Must be a CSV file or folder containing CSV files.")


if __name__ == "__main__":
    main()
