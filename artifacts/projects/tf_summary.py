# projects/generate_symbol_timeframes_summary.py
import os
import pandas as pd
from typing import Dict, List
import libs.file_utils as fu
import libs.csv_utils as cu


# Predefined timeframe order (from highest to lowest)
TF_ORDER = ["MN1", "W1", "D1", "H4", "H1", "M30", "M15", "M5", "M1"]


def gather_folder_structure(base_path: str) -> Dict[str, List[str]]:
    """
    Returns mapping: {folder_name: [csv_files]} for all first-level folders inside base_path.
    Ignores non-directory items.
    """
    folder_map = {}
    for entry in sorted(os.listdir(base_path)):
        full_path = os.path.join(base_path, entry)
        if os.path.isdir(full_path):
            csvs = []
            for root, _, files in os.walk(full_path):
                for f in sorted(files):
                    if f.lower().endswith(".csv"):
                        csvs.append(os.path.join(root, f))
            if csvs:
                folder_map[entry] = csvs
    return folder_map


def extract_symbol_tf(filename: str) -> str:
    """
    Extracts symbol and timeframe from filename.
    Expected pattern: SYMBOL_TF.csv or SYMBOL-TF.csv
    Returns string like 'EURUSD_W1'.
    """
    base = os.path.basename(filename)
    name = os.path.splitext(base)[0]
    for sep in ["_", "-"]:
        parts = name.split(sep)
        if len(parts) >= 2 and parts[-1] in TF_ORDER:
            return f"{sep.join(parts[:-1])}_{parts[-1]}"
    return name  # fallback if no TF detected


def extract_first_last_timestamps(csv_file: str) -> tuple:
    """
    Reads CSV and returns (first_timestamp, last_timestamp)
    based on the 'timestamp' column.
    """
    df = cu.load_csv(csv_file, sep=";")
    if "timestamp" not in df.columns:
        raise RuntimeError(f"No 'timestamp' column in {csv_file}")
    df_sorted = df.sort_values("timestamp")
    return df_sorted["timestamp"].iloc[0], df_sorted["timestamp"].iloc[-1]


def build_summary(folder_map: Dict[str, List[str]]) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Builds nested mapping:
    {symbol_tf: {folder_name: {"first": ts, "last": ts}}}
    """
    summary = {}
    for folder_name, csv_files in folder_map.items():
        for csv_file in csv_files:
            symbol_tf = extract_symbol_tf(csv_file)
            first_ts, last_ts = extract_first_last_timestamps(csv_file)
            if symbol_tf not in summary:
                summary[symbol_tf] = {}
            summary[symbol_tf][folder_name] = {"first": first_ts, "last": last_ts}
    return summary


def order_symbols(symbols: List[str]) -> List[str]:
    """Sorts by TF importance, then alphabetically."""
    def sort_key(x: str):
        for tf in TF_ORDER:
            if x.endswith(tf):
                return (TF_ORDER.index(tf), x)
        return (len(TF_ORDER), x)
    return sorted(symbols, key=sort_key)


def save_summary_per_symbol(summary: Dict[str, Dict[str, Dict[str, str]]], output_folder: str):
    """Saves one CSV per symbol."""
    os.makedirs(output_folder, exist_ok=True)

    # Group by base symbol
    grouped = {}
    for symbol_tf in summary.keys():
        if "_" in symbol_tf:
            base_symbol = symbol_tf.split("_")[0]
        else:
            base_symbol = symbol_tf
        grouped.setdefault(base_symbol, []).append(symbol_tf)

    for base_symbol, tf_list in grouped.items():
        tf_list = order_symbols(tf_list)
        rows = []
        all_columns = []

        for symbol_tf in tf_list:
            row_data = {"symbol_tf": symbol_tf}
            for folder_name, data in summary[symbol_tf].items():
                first_col = f"{folder_name}_first"
                last_col = f"{folder_name}_last"
                row_data[first_col] = data["first"]
                row_data[last_col] = data["last"]
                if first_col not in all_columns:
                    all_columns.extend([first_col, last_col])
            rows.append(row_data)

        # Ensure consistent column order
        columns = ["symbol_tf"] + all_columns
        df = pd.DataFrame(rows, columns=columns)
        output_path = os.path.join(output_folder, f"{base_symbol}.csv")
        cu.save_csv(df, output_path)

    print(f"\nSummary files saved to: {output_folder}")


def main():
    print("CSV Symbol-Timeframe Summary Generator")
    base_path = fu.get_valid_folder("Enter base folder path: ")
    output_folder = input("Enter output folder path (will be created): ").strip()
    if not output_folder:
        print("Invalid path. Exiting.")
        return
    if os.path.exists(output_folder):
        print("Output folder already exists. Cannot overwrite.")
        return

    folder_map = gather_folder_structure(base_path)
    if not folder_map:
        print("No subfolders with CSV files found. Exiting.")
        return

    print(f"\nFound {len(folder_map)} folder(s) to process.")

    summary = build_summary(folder_map)
    if not summary:
        print("No valid CSV data found. Exiting.")
        return

    save_summary_per_symbol(summary, output_folder)
    print("\nOperation completed.")


if __name__ == "__main__":
    main()
