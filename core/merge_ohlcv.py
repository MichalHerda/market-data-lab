from pathlib import Path
import pandas as pd

TIME_COL_CANDIDATES = ("date", "time", "timestamp")


def detect_time_column(df: pd.DataFrame) -> str:
    for c in df.columns:
        if c.lower() in TIME_COL_CANDIDATES:
            return c
    raise ValueError("No valid time column found")


def merge_csv(file1: Path, file2: Path) -> pd.DataFrame:
    """Merge two CSVs on time column with forward-fill"""
    df1 = pd.read_csv(file1, sep=";")
    df2 = pd.read_csv(file2, sep=";")

    time_col1 = detect_time_column(df1)
    time_col2 = detect_time_column(df2)

    if time_col1 != time_col2:
        raise ValueError(f"Time column mismatch: {file1} vs {file2}")

    df1[time_col1] = pd.to_datetime(df1[time_col1])
    df2[time_col2] = pd.to_datetime(df2[time_col2])

    merged = pd.merge(df1, df2, on=time_col1, how="outer").sort_values(time_col1)
    merged = merged.ffill().reset_index(drop=True)
    return merged


def list_structure(folder: Path) -> dict[str, list[str]]:
    """Return dict {relative_subfolder: [files]}"""
    struct = {}
    for path in folder.rglob("*"):
        if path.is_file() and path.suffix == ".csv":
            rel = path.parent.relative_to(folder)
            struct.setdefault(str(rel), []).append(path.name)
    return struct


def merge_folders(folder1: Path, folder2: Path, output_base: Path):
    struct1 = list_structure(folder1)
    struct2 = list_structure(folder2)

    common_subfolders = set(struct1.keys()) & set(struct2.keys())
    if not common_subfolders:
        print("No common subfolders found.")
        return

    for sub in sorted(common_subfolders):
        files1 = set(struct1[sub])
        files2 = set(struct2[sub])
        common_files = sorted(files1 & files2)

        for f in common_files:
            path1 = folder1 / sub / f
            path2 = folder2 / sub / f

            print(f"Merging: {path1} + {path2}")
            try:
                merged = merge_csv(path1, path2)
                out_path = output_base / sub / f
                out_path.parent.mkdir(parents=True, exist_ok=True)
                merged.to_csv(out_path, sep=";", index=False)
                print(f"Saved: {out_path}")
            except Exception as e:
                print(f"Error merging {f}: {e}")

    print("\nAll possible files have been processed.")


def main():
    folder1 = Path(input("Enter path to the first folder: ").strip())
    folder2 = Path(input("Enter path to the second folder: ").strip())
    output_base = Path("merged_output")
    output_base.mkdir(exist_ok=True)

    merge_folders(folder1, folder2, output_base)


if __name__ == "__main__":
    main()
