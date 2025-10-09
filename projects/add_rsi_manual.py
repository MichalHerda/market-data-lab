import os
import libs.file_utils as fu
import libs.csv_utils as cu
from libs import rsi


def add_rsi_to_file(file_path: str, close_col: str, period: int, output_folder: str = None, overwrite: bool = False):
    """Load a CSV file, calculate RSI on the chosen column, and save the result."""
    try:
        df = cu.load_csv(file_path, sep=";")
    except Exception as e:
        print(f"Could not load {file_path}: {e}")
        return

    if close_col not in df.columns:
        print(f"Column '{close_col}' not found in {file_path}. Skipped.")
        return

    # Calculate RSI
    df[f"RSI_{period}_{close_col}"] = rsi.rsi(df[close_col], period)

    # Determine save path
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

    # show available columns for a sample file
    sample_file = input_path
    if mode == "folder":
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.lower().endswith(".csv"):
                    sample_file = os.path.join(root, f)
                    break
            break

    try:
        sample_df = cu.load_csv(sample_file, sep=";")
        print("\nAvailable columns in sample file:")
        for col in sample_df.columns:
            print(" -", col)
    except Exception as e:
        print(f"Could not read sample file {sample_file}: {e}")
        return

    close_col = input("\nEnter the column name to calculate RSI from (e.g. close_H1 or close_D1): ").strip()
    if not close_col:
        print("No column provided. Exiting.")
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
        add_rsi_to_file(input_path, close_col, period, output_folder, overwrite)
    elif mode == "folder":
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.lower().endswith(".csv"):
                    add_rsi_to_file(os.path.join(root, f), close_col, period, output_folder, overwrite)


if __name__ == "__main__":
    main()
