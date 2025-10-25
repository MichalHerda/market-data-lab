import os
import pandas as pd
import libs.file_utils as fu
import libs.csv_utils as cu


def gather_csv_files(path: str) -> dict:
    """
    Recursively gather all .csv files in the given path.
    Returns mapping {basename: full_path}.
    """
    csv_map = {}
    if os.path.isfile(path) and path.lower().endswith(".csv"):
        csv_map[os.path.basename(path)] = path
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for f in files:
                if f.lower().endswith(".csv"):
                    csv_map[f] = os.path.join(root, f)
    else:
        raise RuntimeError(f"Invalid path: {path}")
    return csv_map


def compare_two_csvs(file1: str, file2: str) -> pd.DataFrame:
    """
    Compare two CSV summary files and return a DataFrame with differences.
    Produces a single diff_summary column:
    - prefix '-' → range missing in file2
    - prefix '+' → range extra in file2
    """
    df1 = cu.load_csv(file1, sep=";")
    df2 = cu.load_csv(file2, sep=";")

    if "symbol_tf" not in df1.columns or "symbol_tf" not in df2.columns:
        raise RuntimeError(f"Missing 'symbol_tf' column in one of the files: {file1} or {file2}")

    if not df1["symbol_tf"].equals(df2["symbol_tf"]):
        raise RuntimeError(f"Symbol rows do not match between files: {file1} and {file2}")

    results = []

    for _, row in df1.iterrows():
        symbol_tf = row["symbol_tf"]
        row2 = df2[df2["symbol_tf"] == symbol_tf].iloc[0]

        # Extract any *_first and *_last columns (only first found)
        first_1 = str(row.filter(like="_first").iloc[0]) if any("_first" in c for c in df1.columns) else None
        last_1 = str(row.filter(like="_last").iloc[0]) if any("_last" in c for c in df1.columns) else None
        first_2 = str(row2.filter(like="_first").iloc[0]) if any("_first" in c for c in df2.columns) else None
        last_2 = str(row2.filter(like="_last").iloc[0]) if any("_last" in c for c in df2.columns) else None

        identical_range = (first_1 == first_2) and (last_1 == last_2)

        if identical_range:
            diff_summary = ""
        else:
            diff_summary = ""
            if (first_1, last_1) != (first_2, last_2):
                if first_1 != first_2 or last_1 != last_2:
                    # Missing range (in file2 but present in file1)
                    diff_summary += f"-{first_1}→{last_1} "
                    # Extra range (in file2 but not in file1)
                    diff_summary += f"+{first_2}→{last_2}"

        results.append({
            "symbol_tf": symbol_tf,
            "first_1": first_1,
            "last_1": last_1,
            "first_2": first_2,
            "last_2": last_2,
            "identical_range": identical_range,
            "diff_summary": diff_summary.strip()
        })

    return pd.DataFrame(results)


def compare_sets(input1: str, input2: str, output_folder: str):
    """
    Compare two paths — directories or files.
    Produces one combined comparison CSV per matching file pair.
    """
    csvs_1 = gather_csv_files(input1)
    csvs_2 = gather_csv_files(input2)

    os.makedirs(output_folder, exist_ok=True)

    common_files = set(csvs_1.keys()) & set(csvs_2.keys())
    if not common_files:
        print("No matching CSV filenames found between the two inputs.")
        return

    print(f"\nFound {len(common_files)} matching CSV file(s). Processing...")

    for filename in sorted(common_files):
        file1 = csvs_1[filename]
        file2 = csvs_2[filename]
        try:
            comparison_df = compare_two_csvs(file1, file2)
            output_path = os.path.join(output_folder, f"compare_{filename}")
            cu.save_csv(comparison_df, output_path)
            print(f"Compared: {filename}")
        except Exception as e:
            print(f"Error comparing {filename}: {e}")

    print(f"\nAll comparisons saved in: {output_folder}")


def main():
    print("CSV Symbol-Timeframe Range Comparator (supports files or directories)")
    print("Compares data coverage between two CSV inputs and highlights differences.")
    print("Legend: '-' = range missing in second dataset, '+' = range extra in second dataset.\n")

    input1 = fu.get_valid_path("Enter path to first CSV file or folder: ")
    input2 = fu.get_valid_path("Enter path to second CSV file or folder: ")

    output_folder = input("\nEnter output folder path (will be created): ").strip()
    if not output_folder:
        print("Invalid output folder. Exiting.")
        return

    compare_sets(input1, input2, output_folder)
    print("\nOperation completed.")


if __name__ == "__main__":
    main()
