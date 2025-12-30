import os
import re
import libs.csv_utils as cu
import libs.file_utils as fu


def extract_tf_and_period(column_name: str):
    """Extract timeframe and period from a column name like SMA_H1_50 or EMA_D1_100"""
    tf_match = re.search(r'(MN\d+|W\d+|D\d+|H\d+|M\d+)', column_name, re.IGNORECASE)
    timeframe = tf_match.group(0).upper() if tf_match else None

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


def find_sma_column(df) -> str:
    """Find the first column whose name starts with SMA_"""
    for col in df.columns:
        if col.upper().startswith("SMA_"):
            return col
    return None


def calculate_trend(df, column_name):
    """Add Uptrend column based on changes in the chosen column"""
    new_col_name = generate_uptrend_name(column_name)
    df[new_col_name] = df[column_name].diff() > 0
    return df, new_col_name


def process_csv(file_path: str, output_folder: str = None):
    """Add Uptrend column to a single CSV"""
    try:
        df = cu.load_csv(file_path, sep=";")
    except Exception as e:
        print(f"Could not load {file_path}: {e}")
        return

    sma_col = find_sma_column(df)
    if not sma_col:
        print(f"No SMA column found in {os.path.basename(file_path)}. Skipped.")
        return

    before = len(df)
    df, new_col_name = calculate_trend(df, sma_col)
    after = len(df)

    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        save_path = os.path.join(output_folder, os.path.basename(file_path))
    else:
        save_path = file_path

    cu.save_csv(df, save_path, sep=";")
    print(
        f"Processed {os.path.basename(file_path)}: {before} rows → {after} rows. "
        f"Added column '{new_col_name}'."
    )


def main():
    print("\n--- Uptrend Column Generator ---")
    input_path = fu.get_valid_path("Enter path to CSV file or folder: ")

    # Ask what to do with results
    print("\nWhat would you like to do with the result?")
    print(" 1. Overwrite original files")
    print(" 2. Save processed files in a new folder")
    action = input("Your choice (1/2): ").strip()

    output_folder = None
    if action == "2":
        output_folder = input("Enter path for output folder: ").strip()
        os.makedirs(output_folder, exist_ok=True)

    csv_files = []
    if os.path.isfile(input_path) and input_path.lower().endswith(".csv"):
        csv_files.append(input_path)
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.lower().endswith(".csv"):
                    csv_files.append(os.path.join(root, f))

    if not csv_files:
        print("No CSV files found. Exiting.")
        return

    print(f"\nFound {len(csv_files)} CSV file(s) to process.\n")

    processed = 0
    for file_path in csv_files:
        process_csv(file_path, output_folder)
        processed += 1

    print(f"\nProcessing completed. {processed} file(s) processed.")


if __name__ == "__main__":
    main()
