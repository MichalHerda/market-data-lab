import os
import libs.csv_utils as cu
import libs.file_utils as fu
import pandas as pd


def calculate_ma_deviation(df, col_x, col_y):
    """Add MA Deviation column: difference between column X and column Y"""
    df["MA_Deviation"] = df.apply(
        lambda row: row[col_x] - row[col_y]
        if pd.notna(row[col_x]) and pd.notna(row[col_y])
        else None,
        axis=1,
    )
    return df


def process_csv(file_path: str, col_x: str, col_y: str, output_folder: str = None):
    """Add MA Deviation column to a single CSV"""
    try:
        df = cu.load_csv(file_path, sep=";")
    except Exception as e:
        print(f"Could not load {file_path}: {e}")
        return

    missing_cols = [c for c in [col_x, col_y] if c not in df.columns]
    if missing_cols:
        print(f"Missing columns {missing_cols} in {file_path}. Skipped.")
        return

    before = len(df)
    df = calculate_ma_deviation(df, col_x, col_y)
    after = len(df)

    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        save_path = os.path.join(output_folder, os.path.basename(file_path))
    else:
        save_path = file_path

    cu.save_csv(df, save_path, sep=";")
    print(
        f"Processed {os.path.basename(file_path)}: {before} rows → {after} rows. "
        f"Added MA_Deviation column. Saved to {save_path}"
    )


def main():
    # Input can be file or folder
    input_path = fu.get_valid_path("Enter path to CSV file or folder: ")

    # Get first file to preview columns
    sample_file = None
    if os.path.isfile(input_path) and input_path.endswith(".csv"):
        sample_file = input_path
    elif os.path.isdir(input_path):
        for f in os.listdir(input_path):
            if f.endswith(".csv"):
                sample_file = os.path.join(input_path, f)
                break

    if sample_file:
        try:
            df_sample = cu.load_csv(sample_file, sep=";")
            print("\nAvailable columns in sample file:")
            for col in df_sample.columns:
                print(" -", col)
        except Exception as e:
            print(f"Could not read columns from {sample_file}: {e}")

    # Ask user which columns to use
    col_x = input("\nEnter name of column X (e.g., CLOSE): ").strip()
    col_y = input("Enter name of column Y (e.g., MA_20): ").strip()

    # Choose action
    print("\nWhat would you like to do with the result?")
    print(" 1. Overwrite original files")
    print(" 2. Save processed files in a new folder")
    action = input("Your choice (1/2): ").strip()

    output_folder = None
    if action == "2":
        output_folder = input("Enter path for output folder: ").strip()
        os.makedirs(output_folder, exist_ok=True)

    if os.path.isfile(input_path) and input_path.endswith(".csv"):
        # Single file
        process_csv(input_path, col_x, col_y, output_folder)

    elif os.path.isdir(input_path):
        # Folder: process all .csv files
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.endswith(".csv"):
                    process_csv(os.path.join(root, f), col_x, col_y, output_folder)
    else:
        print("Invalid path. Must be a .csv file or folder containing .csv files.")


if __name__ == "__main__":
    main()
