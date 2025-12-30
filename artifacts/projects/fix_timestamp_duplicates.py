import os
import libs.file_utils as fu
import libs.csv_utils as cu


def load_csv_map(path: str):
    """Load all CSVs from a file or folder, return dict {relative_path: dataframe}"""
    csv_map = {}

    if os.path.isfile(path) and path.endswith(".csv"):
        csv_map[os.path.basename(path)] = cu.load_csv(path, sep=";")
        return csv_map

    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith(".csv"):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, path)
                csv_map[rel] = cu.load_csv(full, sep=";")

    return csv_map


def check_no_duplicates(df_map: dict):
    """Ensure reference data contains no duplicate timestamps"""
    for name, df in df_map.items():
        if "timestamp" not in df.columns:
            continue
        if df["timestamp"].duplicated().any():
            print(f"Error: Reference file '{name}' contains duplicate timestamps. Aborting.")
            return False
    return True


def process_single(df1, df2):
    """Fix duplicates in df1 using df2"""
    if "timestamp" not in df1.columns:
        return df1

    counts = df1["timestamp"].value_counts()
    duplicate_ts = counts[counts > 1].index

    if len(duplicate_ts) == 0:
        return df1  # nothing to fix

    df1_fixed = df1.copy()
    df2_indexed = df2.set_index("timestamp") if df2 is not None and "timestamp" in df2.columns else None

    for ts in duplicate_ts:
        rows = df1_fixed[df1_fixed["timestamp"] == ts]

        if df2_indexed is not None and ts in df2_indexed.index:
            replacement = df2_indexed.loc[ts]
            df1_fixed = df1_fixed[df1_fixed["timestamp"] != ts]
            df1_fixed.loc[len(df1_fixed)] = replacement
        else:
            first_row = rows.iloc[0]
            df1_fixed = df1_fixed[df1_fixed["timestamp"] != ts]
            df1_fixed.loc[len(df1_fixed)] = first_row

    df1_fixed = df1_fixed.sort_values(by="timestamp").reset_index(drop=True)
    return df1_fixed


def main():
    print("Duplicate Timestamp Resolver Using Reference Data")

    input1 = fu.get_valid_path("Enter path to primary CSV file or folder (data to fix): ")
    input2 = fu.get_valid_path("Enter path to reference CSV file or folder: ")

    print("Loading reference data...")
    reference = load_csv_map(input2)

    if not check_no_duplicates(reference):
        return  # do not proceed

    print("Loading primary data...")
    primary = load_csv_map(input1)

    print("\nChoose output mode:")
    print(" 1. Overwrite original files")
    print(" 2. Save to new folder (preserve directory structure)")
    mode = input("Your choice (1/2): ").strip()

    output_root = None
    if mode == "2":
        output_root = input("Enter output folder path: ").strip()
        os.makedirs(output_root, exist_ok=True)

    for rel_path, df1 in primary.items():
        df2 = reference.get(rel_path, None)
        fixed = process_single(df1, df2)

        if mode == "1":
            save_path = os.path.join(os.path.dirname(input1), rel_path) if os.path.isdir(input1) else input1
        else:
            save_path = os.path.join(output_root, rel_path)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

        cu.save_csv(fixed, save_path, sep=";")
        print(f"Processed and saved: {save_path}")


if __name__ == "__main__":
    main()
