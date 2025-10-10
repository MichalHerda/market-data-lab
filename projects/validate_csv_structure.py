# projects/validate_csv_structure_recursive.py
import os
from typing import Dict, List, Tuple
import libs.file_utils as fu
import libs.csv_utils as cu


def gather_all_csv_files(root_folder: str) -> List[str]:
    """Recursively collect all CSV files within the folder structure."""
    csv_files = []
    for current_root, dirs, files in os.walk(root_folder):
        for file in sorted(files):
            if file.lower().endswith(".csv"):
                csv_files.append(os.path.join(current_root, file))
    return csv_files


def get_columns_of_file(path: str) -> Tuple[str]:
    """Load CSV and return tuple of column names."""
    try:
        df = cu.load_csv(path, sep=";")
        return tuple(df.columns)
    except Exception as e:
        raise RuntimeError(f"Could not load '{path}': {e}")


def compare_structures(col_map: Dict[str, Tuple[str]]):
    """Compare columns between all loaded CSVs."""
    if not col_map:
        return {"all_same": True, "reference": None, "differences": {}}

    # Pick most common column structure as reference
    freq: Dict[Tuple[str], int] = {}
    for cols in col_map.values():
        freq[cols] = freq.get(cols, 0) + 1
    reference = max(freq.items(), key=lambda x: (x[1], x[0]))[0]

    ref_set = set(reference)
    differences = {}

    for path, cols in col_map.items():
        cols_set = set(cols)
        missing = ref_set - cols_set
        extra = cols_set - ref_set
        order_diff = False

        if not missing and not extra and tuple(cols) != tuple(reference):
            order_diff = True

        if missing or extra or order_diff:
            differences[path] = {
                "missing": missing,
                "extra": extra,
                "order_diff": order_diff,
                "columns": list(cols),
            }

    return {"all_same": len(differences) == 0, "reference": list(reference), "differences": differences}


def validate_folder_structure(folder: str):
    """Validate CSV structure in the given folder (recursively)."""
    csv_files = gather_all_csv_files(folder)
    if not csv_files:
        print(f"\nNo CSV files found in '{folder}'. Skipping.")
        return

    print(f"\nValidating {len(csv_files)} CSV file(s) found under '{folder}' ...")

    col_map = {}
    load_errors = []
    for path in csv_files:
        try:
            cols = get_columns_of_file(path)
            col_map[path] = cols
        except Exception as exc:
            load_errors.append((path, str(exc)))

    if load_errors:
        print("\nSome files could not be loaded:")
        for p, err in load_errors:
            print(f" - {p}: {err}")

    if not col_map:
        print("No valid CSVs to compare. Exiting.")
        return

    result = compare_structures(col_map)

    if result["all_same"]:
        print("\nAll CSV files share the same column structure.")
        print("Reference columns:")
        print("  " + ", ".join(result["reference"]))
    else:
        print("\nColumn structure mismatch detected.")
        print("Reference columns:")
        print("  " + ", ".join(result["reference"]))
        print("\nFiles with differences:")
        for path, info in sorted(result["differences"].items()):
            print(f"\n - {path}")
            if info["order_diff"]:
                print("    Note: same columns but different order.")
            if info["missing"]:
                print(f"    Missing columns: {', '.join(sorted(info['missing']))}")
            if info["extra"]:
                print(f"    Extra columns: {', '.join(sorted(info['extra']))}")


def main():
    print("CSV Structure Validator — recursive version.")
    root = fu.get_valid_folder("Enter path to the root folder: ")

    print("\nStarting recursive validation...")
    validate_folder_structure(root)
    print("\nValidation finished.")


if __name__ == "__main__":
    main()
