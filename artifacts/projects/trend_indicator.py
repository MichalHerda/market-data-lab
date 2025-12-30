import os
import re
import libs.csv_utils as cu
import libs.file_utils as fu


def extract_tf_and_period(column_name: str):
    """Extract timeframe and period from a column name like SMA_H1_50_H1 or EMA_D1_100"""
    # Try to find timeframe (H1, M15, D1, W1, MN1, etc.)
    tf_match = re.search(r'(M\d+|H\d+|D\d+|W\d+|MN\d+)', column_name, re.IGNORECASE)
    timeframe = tf_match.group(0).upper() if tf_match else None

    # Try to find period (sequence of digits)
    period_match = re.search(r'_(\d+)_', column_name)
    if not period_match:
        period_match = re.search(r'(\d+)$', column_name)
    period = period_match.group(1) if period_match else None

    return timeframe, period


def generate_uptrend_name(column_name: str) -> str:
    """Generate uptrend column name based on input column naming pattern"""
    timeframe, period = extract_tf_and_period(column_name)
    parts = ["up"]
    if timeframe:
        parts.append(timeframe)
    if period:
        parts.append(period)
    return "_".join(parts)


def calculate_trend(df, column_name):
    """Add Uptrend column based on changes in the chosen column"""
    new_col_name = generate_uptrend_name(column_name)
    df[new_col_name] = df[column_name].diff() > 0
    return df, new_col_name


def process_csv(file_path: str, column_name: str, output_folder: str = None):
    """Add Uptrend column to a single CSV"""
    try:
        df = cu.load_csv(file_path, sep=";")
    except Exception as e:
        print(f"Could not load {file_path}: {e}")
        return

    if column_name not in df.columns:
        print(f"Column '{column_name}' not found in {file_path}. Skipped.")
        return

    before = len(df)
    df, new_col_name = calculate_trend(df, column_name)
    after = len(df)

    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        save_path = os.path.join(output_folder, os.path.basename(file_path))
    else:
        save_path = file_path

    cu.save_csv(df, save_path, sep=";")
    print(
        f"Processed {os.path.basename(file_path)}: {before} rows → {after} rows. "
        f"Added column '{new_col_name}'. Saved to {save_path}"
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

    # Ask user which column to use
    column_name = input("\nEnter column name to calculate trend: ").strip()

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
        process_csv(input_path, column_name, output_folder)

    elif os.path.isdir(input_path):
        # Folder: process all .csv files
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.endswith(".csv"):
                    process_csv(os.path.join(root, f), column_name, output_folder)
    else:
        print("Invalid path. Must be a .csv file or folder containing .csv files.")


if __name__ == "__main__":
    main()
