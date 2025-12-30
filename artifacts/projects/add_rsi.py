import os
import pandas as pd
import libs.file_utils as fu
import libs.csv_utils as cu
from libs import rsi


def detect_close_column(df: pd.DataFrame) -> str:
    """Try to detect the 'close' column automatically."""
    for c in df.columns:
        if c.lower() in ["close", "close_h1", "close_d1"]:
            return c
    # fallback: first column containing 'close'
    for c in df.columns:
        if "close" in c.lower():
            return c
    raise ValueError("No column containing 'close' found in this CSV file.")


def add_rsi_to_file(file_path: str, period: int, output_folder: str = None, overwrite: bool = False):
    """Load a CSV file, calculate RSI on the close column, and save the result."""
    try:
        df = cu.load_csv(file_path, sep=";")
    except Exception as e:
        print(f"Could not load {file_path}: {e}")
        return

    try:
        close_col = detect_close_column(df)
    except ValueError as e:
        print(f"{e} ({file_path})")
        return

    df[f"RSI_{period}"] = rsi.rsi(df[close_col], period)

    # determine save path
    if overwrite:
        save_path = file_path
    else:
        os.makedirs(output_folder, exist_ok=True)
        base_name = os.path.basename(file_path)
        save_path = os.path.join(output_folder, base_name)

    cu.save_csv(df, save_path, sep=";")
    print(f"Saved file with RSI -> {save_path}")


def main():
    print("This script calculates RSI (Relative Strength Index) and adds it to CSV files.")
    input_path = fu.get_valid_path("Enter path to CSV file or folder: ")

    # detect mode
    if os.path.isfile(input_path):
        mode = "file"
    elif os.path.isdir(input_path):
        mode = "folder"
    else:
        print("Invalid path.")
        return

    try:
        period = int(input("Enter RSI period (default 14): ").strip() or 14)
    except ValueError:
        print("Invalid input. Using default RSI period = 14.")
        period = 14

    print("\nWhat would you like to do with the results?")
    print(" 1. Overwrite original files")
    print(" 2. Save processed files to a new folder")
    choice = input("Your choice (1/2): ").strip()

    if choice == "1":
        overwrite = True
        output_folder = None
    else:
        overwrite = False
        output_folder = input("Enter path for new output folder: ").strip()
        if not output_folder:
            print("No output folder specified. Exiting.")
            return

    if mode == "file":
        add_rsi_to_file(input_path, period, output_folder, overwrite)
    elif mode == "folder":
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.lower().endswith(".csv"):
                    add_rsi_to_file(os.path.join(root, f), period, output_folder, overwrite)


if __name__ == "__main__":
    main()
