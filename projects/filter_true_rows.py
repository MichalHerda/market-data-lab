import os
import libs.csv_utils as cu
import libs.file_utils as fu
import pandas as pd


def filter_true_rows(df: pd.DataFrame, column_name: str):
    """Return only rows where the given column == True"""
    if column_name not in df.columns:
        print(f"  Column '{column_name}' not found. Skipped.")
        return df

    # Check if the column contains bool or 0/1 values
    col = df[column_name]
    if not col.dropna().isin([True, False, 1, 0]).any():
        print(f"  Column '{column_name}' has no boolean-like values. No filtering applied.")
        return df

    # Filtering
    return df.loc[df[column_name].eq(True)]


def process_csv(file_path: str, column_name: str, output_folder: str = None):
    """Process a single CSV file: keep only rows with True in the given column"""
    try:
        df = cu.load_csv(file_path, sep=";")
    except Exception as e:
        print(f"Could not load {file_path}: {e}")
        return

    before = len(df)
    df_filtered = filter_true_rows(df, column_name)
    after = len(df_filtered)

    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        save_path = os.path.join(output_folder, os.path.basename(file_path))
    else:
        save_path = file_path

    cu.save_csv(df_filtered, save_path, sep=";")
    print(f"Processed {os.path.basename(file_path)}: {before} → {after} rows. Saved to {save_path}")


def main():
    input_path = fu.get_valid_path("Enter path to CSV file or folder: ")

    # Column preview on the first file
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

    column_name = input("\nEnter column name to filter by (keep only True values): ").strip()

    print("\nWhat would you like to do with the result?")
    print(" 1. Overwrite original files")
    print(" 2. Save processed files in a new folder")
    action = input("Your choice (1/2): ").strip()

    output_folder = None
    if action == "2":
        output_folder = input("Enter path for output folder: ").strip()
        os.makedirs(output_folder, exist_ok=True)

    if os.path.isfile(input_path) and input_path.endswith(".csv"):
        process_csv(input_path, column_name, output_folder)
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.endswith(".csv"):
                    process_csv(os.path.join(root, f), column_name, output_folder)
    else:
        print("Invalid path. Must be a .csv file or folder containing .csv files.")


if __name__ == "__main__":
    main()
