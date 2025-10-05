import os
import pandas as pd
import libs.csv_utils as cu
import libs.file_utils as fu


def normalize_floats(df: pd.DataFrame, column_name: str, decimals: int):
    """Round and format float values in the given column to N decimals"""
    if column_name not in df.columns:
        print(f"  Column '{column_name}' not found. Skipped.")
        return df

    # Spróbuj skonwertować kolumnę na float (jeśli nie jest)
    try:
        df[column_name] = pd.to_numeric(df[column_name], errors="coerce")
    except Exception:
        print(f"  Could not convert column '{column_name}' to float. Skipped.")
        return df

    # Zaokrąglenie i formatowanie z ustaloną ilością miejsc po przecinku
    df[column_name] = df[column_name].round(decimals).apply(
        lambda x: f"{x:.{decimals}f}" if pd.notnull(x) else ""
    )

    return df


def process_csv(file_path: str, column_name: str, decimals: int, output_folder: str = None):
    """Process single CSV file"""
    try:
        df = cu.load_csv(file_path, sep=";")
    except Exception as e:
        print(f"Could not load {file_path}: {e}")
        return

    df_norm = normalize_floats(df, column_name, decimals)

    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        save_path = os.path.join(output_folder, os.path.basename(file_path))
    else:
        save_path = file_path

    cu.save_csv(df_norm, save_path, sep=";")
    print(f"Processed {os.path.basename(file_path)} → saved to {save_path}")


def main():
    input_path = fu.get_valid_path("Enter path to CSV file or folder: ")

    # Podgląd kolumn (z pierwszego pliku)
    sample_file = None
    if os.path.isfile(input_path) and input_path.endswith(".csv"):
        sample_file = input_path
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.endswith(".csv"):
                    sample_file = os.path.join(root, f)
                    break
            if sample_file:
                break

    if sample_file:
        try:
            df_sample = cu.load_csv(sample_file, sep=";")
            print("\nAvailable columns in sample file:")
            for col in df_sample.columns:
                print(" -", col)
        except Exception as e:
            print(f"Could not read columns from {sample_file}: {e}")

    column_name = input("\nEnter column name to normalize: ").strip()

    while True:
        try:
            decimals = int(input("Enter number of decimal places to round to: ").strip())
            if decimals >= 0:
                break
        except ValueError:
            pass
        print("Please enter a non-negative integer.\n")

    print("\nWhat would you like to do with the result?")
    print(" 1. Overwrite original files")
    print(" 2. Save processed files in a new folder")
    action = input("Your choice (1/2): ").strip()

    output_folder = None
    if action == "2":
        output_folder = input("Enter path for output folder: ").strip()
        os.makedirs(output_folder, exist_ok=True)

    if os.path.isfile(input_path) and input_path.endswith(".csv"):
        process_csv(input_path, column_name, decimals, output_folder)
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.endswith(".csv"):
                    process_csv(os.path.join(root, f), column_name, decimals, output_folder)
    else:
        print("Invalid path. Must be a .csv file or folder containing .csv files.")


if __name__ == "__main__":
    main()
