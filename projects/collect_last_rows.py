import os
import pandas as pd
import libs.file_utils as fu
import libs.csv_utils as cu


def gather_csv_files(path: str):
    """Return list of CSV file paths from a directory (recursively)."""
    csv_files = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(".csv"):
                csv_files.append(os.path.join(root, f))
    return csv_files


def get_last_row(file_path: str):
    """Return filename and last row of CSV file as a list of values."""
    try:
        df = cu.load_csv(file_path, sep=";")
    except Exception as e:
        print(f"Could not load {file_path}: {e}")
        return None

    if df.empty:
        print(f"{file_path} is empty. Skipped.")
        return None

    last_row = df.iloc[-1].tolist()
    filename = os.path.basename(file_path)
    return [filename] + last_row


def main():
    print("Last Row Collector")

    input_dir = fu.get_valid_path("Enter path to folder containing CSV files: ")
    output_file = input("Enter output CSV file path: ").strip()

    csv_files = gather_csv_files(input_dir)
    if not csv_files:
        print("No CSV files found. Exiting.")
        return

    collected_rows = []
    columns = None

    for file_path in csv_files:
        result = get_last_row(file_path)
        if result is None:
            continue

        # Extract column names from the first valid file
        if columns is None:
            try:
                df_temp = cu.load_csv(file_path, sep=";")
                columns = ["source_file"] + list(df_temp.columns)
            except Exception:
                continue

        collected_rows.append(result)

    if not collected_rows:
        print("No valid data to write. Exiting.")
        return

    summary_df = pd.DataFrame(collected_rows, columns=columns)
    cu.save_csv(summary_df, output_file, sep=";")

    print(f"\nSummary file saved to: {output_file}")
    print("Done.")


if __name__ == "__main__":
    main()
