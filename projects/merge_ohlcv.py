from pathlib import Path
from libs.csv_utils import merge_csv_files, save_csv
from libs.file_utils import get_valid_folder, list_structure


def main():
    # 1. Ask the user for two existing folder paths
    folder1 = get_valid_folder("Enter the path to the first folder: ")
    folder2 = get_valid_folder("Enter the path to the second folder: ")

    # 2. Build file structures for both folders
    struct1 = list_structure(folder1)
    struct2 = list_structure(folder2)

    # 3. Determine the common subfolders
    common_folders = set(struct1.keys()) & set(struct2.keys())

    # 4. Create the output base folder
    output_base = Path("merged_output")
    output_base.mkdir(exist_ok=True)

    # 5. Iterate over common subfolders
    for subfolder in sorted(common_folders):
        files1 = set(struct1[subfolder])
        files2 = set(struct2[subfolder])

        # Find files with the same name in both folders
        common_files = files1 & files2

        for file in sorted(common_files):
            file1 = Path(folder1, subfolder, file)
            file2 = Path(folder2, subfolder, file)

            print(f" Merging: {file1}  +  {file2}")

            try:
                # Merge two CSV files using default options
                merged = merge_csv_files(str(file1), str(file2))

                # Save result in the output folder
                output_path = output_base / subfolder / file
                save_csv(merged, str(output_path))
                print(f"Saved: {output_path}")
            except Exception as e:
                print(f"Error while merging {file}: {e}")

    print("\n All possible files have been processed.")


if __name__ == "__main__":
    main()
