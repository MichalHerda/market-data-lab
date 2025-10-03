import os
import libs.csv_utils as cu
import libs.file_utils as fu


def process_csv(file_path: str, output_folder: str = None):
    """Remove rows with missing values from a single CSV"""
    try:
        df = cu.load_csv(file_path, sep=";")
    except Exception as e:
        print(f"Could not load {file_path}: {e}")
        return

    before = len(df)
    df = df.dropna()
    after = len(df)

    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        save_path = os.path.join(output_folder, os.path.basename(file_path))
    else:
        save_path = file_path

    cu.save_csv(df, save_path, sep=";")
    print(f"Processed {os.path.basename(file_path)}: {before} → {after} rows. Saved to {save_path}")


def main():
    # Input can be a file or folder
    input_path = fu.get_valid_path("Enter path to CSV file or folder: ")

    # Choose action
    print("\nWhat would you like to do with the result?")
    print(" 1. Overwrite original files")
    print(" 2. Save cleaned files in a new folder")
    action = input("Your choice (1/2): ").strip()

    output_folder = None
    if action == "2":
        output_folder = input("Enter path for output folder: ").strip()
        os.makedirs(output_folder, exist_ok=True)

    if os.path.isfile(input_path) and input_path.endswith(".csv"):
        # Single file
        process_csv(input_path, output_folder)

    elif os.path.isdir(input_path):
        # Folder: process all .csv inside (recursively only 1 level down)
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.endswith(".csv"):
                    process_csv(os.path.join(root, f), output_folder)
    else:
        print("Invalid path. Must be a .csv file or folder containing .csv files.")


if __name__ == "__main__":
    main()
