import os
import libs.file_utils as fu
import libs.csv_utils as cu


def choose_column(df) -> str:
    """Ask user which column to delete"""
    print("\nAvailable columns:")
    for col in df.columns:
        print(f" - {col}")
    column = input("\nEnter the column name to delete: ").strip()
    while column not in df.columns:
        print(f"Column '{column}' does not exist in DataFrame. Try again.\n")
        column = input("Enter the column name to delete: ").strip()
    return column


def choose_action() -> int:
    """Ask user what to do with results"""
    while True:
        print("\nWhat would you like to do with the result?")
        print(" 1. Overwrite all original CSV files")
        print(" 2. Save modified files to a new folder (keep structure)")
        try:
            choice = int(input("Your choice (1/2): ").strip())
            if choice in (1, 2):
                return choice
            print("Invalid option. Please enter 1 or 2.\n")
        except ValueError:
            print("Please enter a valid number (1 or 2).\n")


def main():
    # Step 1: Ask for folder with CSV files
    folder = fu.get_valid_folder("Enter the path to the folder with CSV files: ")

    # Collect all CSV files recursively
    csv_files = []
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(".csv"):
                csv_files.append(os.path.join(root, f))

    if not csv_files:
        print("\n❌ No CSV files found in the provided folder.")
        return

    print(f"\n✅ Found {len(csv_files)} CSV files.")

    # Step 2: Load first CSV to let user choose column
    first_df = cu.load_csv(csv_files[0], sep=";")
    print(f"\nColumns in sample file ({os.path.basename(csv_files[0])}): {', '.join(first_df.columns)}")
    column = choose_column(first_df)

    # Step 3: Choose action
    action = choose_action()

    if action == 2:
        output_folder = input("\nEnter the path for the output folder: ").strip()
        os.makedirs(output_folder, exist_ok=True)
    else:
        output_folder = None

    # Step 4: Process all CSV files
    for file_path in csv_files:
        df = cu.load_csv(file_path, sep=";")
        if column not in df.columns:
            print(f"⚠️ Column '{column}' not in {file_path}, skipping.")
            continue
        result = df.drop(columns=[column])

        if action == 1:
            # Overwrite
            cu.save_csv(result, file_path, sep=";")
        else:
            # Mirror structure in new folder
            rel_path = os.path.relpath(file_path, folder)
            save_path = os.path.join(output_folder, rel_path)
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cu.save_csv(result, save_path, sep=";")

    print("\n Processing finished.")


if __name__ == "__main__":
    main()
