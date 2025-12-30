# projects/find_timestamp_duplicates.py

import os
import pandas as pd
import libs.file_utils as fu
import libs.csv_utils as cu


def process_csv(file_path: str, output_folder: str):
    try:
        df = cu.load_csv(file_path, sep=";")
    except Exception as e:
        print(f"Could not load {file_path}: {e}")
        return

    if "timestamp" not in df.columns:
        print(f"File {os.path.basename(file_path)} does not contain 'timestamp' column. Skipped.")
        return

    duplicates = df["timestamp"].value_counts()
    duplicates = duplicates[duplicates > 1]

    if duplicates.empty:
        print(f"No duplicate timestamps in {os.path.basename(file_path)}.")
        return

    duplicate_timestamps = pd.DataFrame({"timestamp": duplicates.index})
    os.makedirs(output_folder, exist_ok=True)

    output_name = os.path.splitext(os.path.basename(file_path))[0] + "_duplicates.csv"
    output_path = os.path.join(output_folder, output_name)

    duplicate_timestamps.to_csv(output_path, sep=";", index=False)
    print(f"Found {len(duplicate_timestamps)} duplicate timestamps in {os.path.basename(file_path)}. Saved to {output_path}")


def main():
    print("Timestamp Duplicate Finder")

    input_path = fu.get_valid_path("Enter path to CSV file or folder: ")
    output_folder = input("Enter output folder path: ").strip()
    os.makedirs(output_folder, exist_ok=True)

    if os.path.isfile(input_path) and input_path.endswith(".csv"):
        process_csv(input_path, output_folder)

    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.endswith(".csv"):
                    process_csv(os.path.join(root, f), output_folder)
    else:
        print("Invalid path. Must be a .csv file or directory containing .csv files.")


if __name__ == "__main__":
    main()
