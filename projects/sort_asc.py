# projects/sort_asc.py
import os
import pandas as pd
import libs.csv_utils as cu
import libs.file_utils as fu


def sort_csv_by_column(input_path: str, column_name: str, output_folder: str):
    """Sort a CSV file by a given numeric column in ascending order."""
    try:
        df = cu.load_csv(input_path, sep=";")
    except Exception as e:
        print(f"Could not load {input_path}: {e}")
        return

    if column_name not in df.columns:
        print(f"Column '{column_name}' not found in {input_path}. Skipped.")
        return

    try:
        df[column_name] = pd.to_numeric(df[column_name], errors="coerce")
    except Exception as e:
        print(f"Could not convert column '{column_name}' to numeric in {input_path}: {e}")
        return

    df_sorted = df.sort_values(by=column_name, ascending=True)

    os.makedirs(output_folder, exist_ok=True)
    base_name = os.path.basename(input_path)
    save_path = os.path.join(output_folder, base_name)

    cu.save_csv(df_sorted, save_path, sep=";")
    print(f"Sorted file saved to {save_path}")


def find_first_sample_csv(path: str) -> str | None:
    """Return first CSV path from folder or the path itself if it is a CSV file."""
    if os.path.isfile(path) and path.lower().endswith(".csv"):
        return path
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for f in files:
                if f.lower().endswith(".csv"):
                    return os.path.join(root, f)
    return None


def main():
    print("This script sorts numeric column values in ascending order.")
    input_path = fu.get_valid_path("Enter path to CSV file or folder: ")

    # Display sample columns
    sample = find_first_sample_csv(input_path)
    if sample:
        try:
            df_sample = cu.load_csv(sample, sep=";")
            print("\nAvailable columns in sample file:")
            for col in df_sample.columns:
                print(" -", col)
        except Exception as e:
            print(f"Could not read sample file {sample}: {e}")

    column_name = input("\nEnter the column name to sort by: ").strip()
    output_folder = input("\nEnter output folder path to save sorted files: ").strip()
    if not output_folder:
        print("No output folder provided. Exiting.")
        return

    os.makedirs(output_folder, exist_ok=True)

    if os.path.isfile(input_path) and input_path.lower().endswith(".csv"):
        sort_csv_by_column(input_path, column_name, output_folder)
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.lower().endswith(".csv"):
                    sort_csv_by_column(os.path.join(root, f), column_name, output_folder)
    else:
        print("Invalid path. Must be a CSV file or folder containing CSV files.")


if __name__ == "__main__":
    main()
