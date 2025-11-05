import os
import pandas as pd
import libs.file_utils as fu
import libs.csv_utils as cu


def gather_csv_files(path: str):
    """Return list of CSV file paths from file or recursive directory."""
    if os.path.isfile(path) and path.lower().endswith(".csv"):
        return [path]

    csv_files = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(".csv"):
                csv_files.append(os.path.join(root, f))
    return csv_files


def analyze_file(file_path: str):
    """Count missing timestamp rows in a CSV."""
    try:
        df = cu.load_csv(file_path, sep=";")
    except Exception as e:
        print(f"Could not load {file_path}: {e}")
        return None

    if "timestamp" not in df.columns:
        print(f"File '{os.path.basename(file_path)}' has no 'timestamp' column. Skipped.")
        return None

    missing_count = df["timestamp"].isna().sum()
    return missing_count


def main():
    print("Missing Timestamp Finder")

    input_path = fu.get_valid_path("Enter path to CSV file or folder: ")

    csv_files = gather_csv_files(input_path)
    if not csv_files:
        print("No CSV files found. Nothing to process.")
        return

    output_dir = input("Enter output directory for results: ").strip()
    os.makedirs(output_dir, exist_ok=True)

    for file_path in csv_files:
        missing = analyze_file(file_path)
        if missing is None or missing == 0:
            continue

        filename = os.path.basename(file_path)
        output_file = os.path.join(output_dir, filename.replace(".csv", "_missing.csv"))

        report = pd.DataFrame({
            "column": ["timestamp"],
            "missing_count": [missing]
        })

        cu.save_csv(report, output_file, sep=";")
        print(f"{filename}: missing timestamps found → saved report to {output_file}")

    print("\nDone.")


if __name__ == "__main__":
    main()
