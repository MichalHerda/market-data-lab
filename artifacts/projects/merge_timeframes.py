import os
import pandas as pd
import libs.file_utils as fu
import libs.csv_utils as cu


def list_csv_files(folder_path: str):
    """List all CSV files in a folder"""
    return [f for f in os.listdir(folder_path) if f.endswith(".csv")]


def extract_symbol_and_tf(filename: str):
    """Extract symbol and timeframe from filename like EURUSD_H1.csv"""
    name = os.path.basename(filename).replace(".csv", "")
    parts = name.split("_")
    if len(parts) >= 2:
        symbol = "_".join(parts[:-1])
        tf = parts[-1].upper()
        return symbol, tf
    else:
        return name, None


def detect_time_column(df):
    """Detect time column"""
    for c in df.columns:
        if c.lower() in ["date", "time", "timestamp"]:
            return c
    raise ValueError("No valid time column found (expected date/time/timestamp)")


def choose_action():
    """Ask user what to do with the result"""
    while True:
        print("\nWhat would you like to do with the result?")
        print(" 1. Overwrite original files/folders")
        print(" 2. Save processed results in a new folder")
        choice = input("Your choice (1/2): ").strip()
        if choice in ("1", "2"):
            return int(choice)
        print("Invalid option. Try again.")


def merge_group(symbol: str, files: list, folder_path: str, output_folder: str = None):
    """Merge all timeframes for one symbol"""
    print(f"\nMerging symbol: {symbol}")

    merged_df = None
    time_col = None

    for f in sorted(files):
        file_path = os.path.join(folder_path, f)
        df = cu.load_csv(file_path, sep=";")
        tf = extract_symbol_and_tf(f)[1]
        if not tf:
            print(f"  Skipping {f} (no timeframe found)")
            continue

        if time_col is None:
            time_col = detect_time_column(df)
            print(f"  Using '{time_col}' as time column")

        df[time_col] = pd.to_datetime(df[time_col])
        df = df.rename(columns=lambda x: x if x == time_col else f"{x}_{tf}")

        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on=time_col, how="outer")

    if merged_df is not None:
        merged_df = merged_df.sort_values(by=time_col).ffill()
        save_name = f"{symbol}_merged.csv"

        if output_folder:
            os.makedirs(output_folder, exist_ok=True)
            save_path = os.path.join(output_folder, save_name)
        else:
            save_path = os.path.join(folder_path, save_name)

        cu.save_csv(merged_df, save_path, sep=";")
        print(f"  Saved merged CSV -> {save_path}")


def process_flat_folder(folder_path: str, output_folder: str = None):
    """Process folder containing multiple symbols (flat structure)"""
    files = list_csv_files(folder_path)
    if not files:
        print("No CSV files found.")
        return

    # group files by symbol
    symbol_groups = {}
    for f in files:
        symbol, tf = extract_symbol_and_tf(f)
        if symbol not in symbol_groups:
            symbol_groups[symbol] = []
        symbol_groups[symbol].append(f)

    print(f"\nDetected {len(symbol_groups)} symbols to merge:")
    for sym in symbol_groups:
        print(f" - {sym}: {[extract_symbol_and_tf(f)[1] for f in symbol_groups[sym]]}")

    for sym, group_files in symbol_groups.items():
        merge_group(sym, group_files, folder_path, output_folder)


def process_nested_folder(parent_folder: str, output_folder: str = None):
    """Process parent folder containing instrument subfolders"""
    subdirs = [os.path.join(parent_folder, d) for d in os.listdir(parent_folder)
               if os.path.isdir(os.path.join(parent_folder, d))]

    if not subdirs:
        print("No subfolders found.")
        return

    for sub in sorted(subdirs):
        process_flat_folder(sub, output_folder)


def merge_single_file(file_path: str, output_folder: str = None):
    """Simply copies a single CSV"""
    df = cu.load_csv(file_path, sep=";")
    save_path = file_path if not output_folder else os.path.join(output_folder, os.path.basename(file_path))
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
    cu.save_csv(df, save_path, sep=";")
    print(f"Single CSV processed -> {save_path}")


def main():
    input_path = fu.get_valid_path("Enter path to CSV file or folder: ")

    action = choose_action()
    output_folder = None
    if action == 2:
        output_folder = input("Enter path for new output folder: ").strip()
        os.makedirs(output_folder, exist_ok=True)

    if os.path.isfile(input_path) and input_path.endswith(".csv"):
        merge_single_file(input_path, output_folder)
    elif os.path.isdir(input_path):
        # detect if nested structure
        subdirs = [os.path.join(input_path, d) for d in os.listdir(input_path)
                   if os.path.isdir(os.path.join(input_path, d))]
        if subdirs:
            process_nested_folder(input_path, output_folder)
        else:
            process_flat_folder(input_path, output_folder)
    else:
        print("Invalid path. Must be a CSV file or folder.")


if __name__ == "__main__":
    main()
