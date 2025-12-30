# projects/rename_csv_columns_recursive.py
import os
from typing import List, Dict
import libs.file_utils as fu
import libs.csv_utils as cu


def gather_csv_files(path: str) -> List[str]:
    """Recursively gather all CSV files from path."""
    csv_files = []
    if os.path.isfile(path) and path.lower().endswith(".csv"):
        csv_files.append(path)
    elif os.path.isdir(path):
        for root, _, files in os.walk(path):
            for f in sorted(files):
                if f.lower().endswith(".csv"):
                    csv_files.append(os.path.join(root, f))
    return csv_files


def get_common_columns(csv_files: List[str]) -> List[str]:
    """Assume all CSVs have identical columns and return the first one's columns."""
    if not csv_files:
        raise RuntimeError("No CSV files found.")
    df = cu.load_csv(csv_files[0], sep=";")
    return list(df.columns)


def ask_for_column_changes(columns: List[str]) -> Dict[str, str]:
    """Interactively ask user for column renames."""
    print("\nAll files are assumed to have identical column structure.")
    print("You can rename columns one by one. Press Enter to skip a column.\n")

    rename_map = {}

    for col in columns:
        new_name = input(f"Rename column '{col}' (press Enter to skip): ").strip()
        if new_name and new_name != col:
            rename_map[col] = new_name

    if not rename_map:
        print("\nNo columns selected for renaming. Exiting.")
        return {}

    print("\nThe following columns will be renamed:")
    for old, new in rename_map.items():
        print(f"  {old} -> {new}")

    confirm = input("\nAre you sure you want to apply these changes? (y/n): ").strip().lower()
    if confirm != "y":
        print("Operation cancelled by user.")
        return {}

    return rename_map


def rename_columns_in_files(csv_files: List[str], rename_map: Dict[str, str], output_folder: str = None):
    """Apply column renames to all CSV files."""
    os.makedirs(output_folder, exist_ok=True) if output_folder else None

    for file_path in csv_files:
        df = cu.load_csv(file_path, sep=";")
        df.rename(columns=rename_map, inplace=True)

        if output_folder:
            relative = os.path.relpath(file_path, start=os.path.commonpath(csv_files))
            output_path = os.path.join(output_folder, relative)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            cu.save_csv(df, output_path)
        else:
            cu.save_csv(df, file_path)


def main():
    print("CSV Column Renamer — recursive version.")
    input_path = input("Enter path to a CSV file or folder: ").strip()

    if not os.path.exists(input_path):
        print("Path does not exist. Exiting.")
        return

    csv_files = gather_csv_files(input_path)
    if not csv_files:
        print("No CSV files found. Exiting.")
        return

    print(f"\nFound {len(csv_files)} CSV file(s) for processing.")

    try:
        columns = get_common_columns(csv_files)
    except Exception as e:
        print(f"Error while reading columns: {e}")
        return

    rename_map = ask_for_column_changes(columns)
    if not rename_map:
        return

    print("\nHow would you like to save the results?")
    print("  1. Overwrite original files")
    print("  2. Save to a new folder")
    choice = input("Your choice (1/2): ").strip()

    if choice == "2":
        output_folder = input("Enter output folder path: ").strip()
        if not output_folder:
            print("Invalid folder path. Exiting.")
            return
        if os.path.exists(output_folder):
            confirm = input("Output folder already exists. Overwrite contents? (y/n): ").strip().lower()
            if confirm != "y":
                print("Operation cancelled.")
                return
        rename_columns_in_files(csv_files, rename_map, output_folder)
        print(f"\nRenamed files saved to '{output_folder}'.")
    else:
        rename_columns_in_files(csv_files, rename_map)
        print("\nFiles have been overwritten with updated column names.")

    print("\nOperation completed.")


if __name__ == "__main__":
    main()
