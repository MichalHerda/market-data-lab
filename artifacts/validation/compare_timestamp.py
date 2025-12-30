import os
import pandas as pd
import libs.file_utils as fu

# available TFs to detect in file names
TIMEFRAMES = ["M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"]


def map_timeframes(folder: str) -> dict:
    """
    Maps subfolder -> {TF: file path}
    """
    tf_map = {}
    for root, dirs, files in os.walk(folder):
        rel_path = os.path.relpath(root, folder)
        if rel_path == ".":
            continue
        tf_map[rel_path] = {}
        for f in files:
            for tf in TIMEFRAMES:
                if tf in f:
                    tf_map[rel_path][tf] = os.path.join(root, f)
    return tf_map


def get_oldest_timestamp(file_path: str) -> str:
    """Returns the oldest timestamp from an MT4
    CSV file (semicolon separated)"""
    try:
        df = pd.read_csv(file_path, sep=";")
        if "timestamp" not in df.columns:
            return " Missing 'timestamp' column"
        if df.empty:
            return " Empty file"
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        return df["timestamp"].min()
    except Exception as e:
        return f" Read error: {e}"


def compare_folders(
    folder1: str, folder2: str, output_file: str = "timestamp_comparison.txt"
):
    map1 = map_timeframes(folder1)
    map2 = map_timeframes(folder2)

    differences = []

    with open(output_file, "w", encoding="utf-8") as f:
        for subfolder in sorted(set(map1.keys()) | set(map2.keys())):
            f.write(f"\n=== Subfolder: {subfolder} ===\n")
            tf1 = set(map1.get(subfolder, {}).keys())
            tf2 = set(map2.get(subfolder, {}).keys())

            # differences in TF structure
            only1 = tf1 - tf2
            only2 = tf2 - tf1
            if only1:
                f.write(f"   TF only in folder1: "
                        f"{', '.join(sorted(only1))}\n")
                differences.append((subfolder, "folder1", only1))
            if only2:
                f.write(f"   TF only in folder2: "
                        f"{', '.join(sorted(only2))}\n")
                differences.append((subfolder, "folder2", only2))

            # compare timestamps for common TFs
            common = tf1 & tf2
            for tf in sorted(common, key=lambda x: TIMEFRAMES.index(x)):
                t1 = get_oldest_timestamp(map1[subfolder][tf])
                t2 = get_oldest_timestamp(map2[subfolder][tf])
                status = "OK" if t1 == t2 else "DIFFERENCE"
                f.write
                (f"  TF: {tf} | Folder1: {t1} | Folder2: {t2} | {status}\n")

        # summary
        f.write("\n=== SUMMARY ===\n")
        if differences:
            f.write("⚠ TF structure differs in the following subfolders:\n")
            for sub, where, tfs in differences:
                f.write(f"  - {sub}: only in {where} -> "
                        f"{', '.join(sorted(tfs))}\n")
        else:
            f.write(" TF structure is identical across all subfolders.\n")

    print(f"\n Comparison finished. Results saved to file: {output_file}")


if __name__ == "__main__":
    print("=== Comparing oldest timestamps in OHLCV files ===\n")
    folder1 = fu.get_valid_folder("Enter path to folder 1: ")
    folder2 = fu.get_valid_folder("Enter path to folder 2: ")

    compare_folders(folder1, folder2)
