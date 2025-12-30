import os
import shutil
import libs.file_utils as fu


def list_symbols(base_path: str):
    """Return a list of available symbols (folders or CSV file names without extension)."""
    symbols = []

    if os.path.isdir(base_path):
        items = os.listdir(base_path)
        for item in items:
            full_path = os.path.join(base_path, item)
            if os.path.isdir(full_path):
                symbols.append(item)  # folder = symbol
            elif os.path.isfile(full_path) and item.endswith(".csv"):
                # file name without extension and _merged if present
                sym = item.replace("_merged.csv", "").replace(".csv", "")
                symbols.append(sym)

    return sorted(symbols)


def filter_symbols(base_path: str, selected: list, output_folder: str = None):
    """Copy or keep only selected symbols from the folder."""
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)

    if os.path.isdir(base_path):
        for item in os.listdir(base_path):
            full_path = os.path.join(base_path, item)

            # Folder = symbol
            if os.path.isdir(full_path):
                if item in selected:
                    dest = os.path.join(output_folder or base_path, item)
                    if output_folder:
                        shutil.copytree(full_path, dest, dirs_exist_ok=True)
                    # overwrite = do nothing (keep as is)
                else:
                    if not output_folder:
                        shutil.rmtree(full_path)

            # CSV file = symbol
            elif os.path.isfile(full_path) and item.endswith(".csv"):
                sym = item.replace("_merged.csv", "").replace(".csv", "")
                if sym in selected:
                    dest = os.path.join(output_folder or base_path, item)
                    if output_folder:
                        shutil.copy2(full_path, dest)
                    # overwrite = keep as is
                else:
                    if not output_folder:
                        os.remove(full_path)


def main():
    base_path = fu.get_valid_folder("Enter path to folder with CSV files or symbol subfolders: ")

    # 1. Show available symbols
    symbols = list_symbols(base_path)
    if not symbols:
        print("No symbols found.")
        return

    print("\nAvailable symbols:")
    print(" ".join(symbols))

    # 2. Ask user to pick
    selected = []
    while True:
        choice = input("Enter symbol to keep (ENTER to finish): ").strip()
        if choice == "":
            break
        if choice in symbols:
            selected.append(choice)
            print(f" Added {choice}")
        else:
            print(" Not found, try again.")

    if not selected:
        print("No symbols selected. Exiting.")
        return

    # 3. Ask user what to do
    print("\nWhat would you like to do with the result?")
    print(" 1. Overwrite original folder (remove everything else)")
    print(" 2. Save only selected symbols in a new folder")
    action = input("Your choice (1/2): ").strip()

    output_folder = None
    if action == "2":
        output_folder = input("Enter path for output folder: ").strip()
        os.makedirs(output_folder, exist_ok=True)

    # 4. Run filter
    filter_symbols(base_path, selected, output_folder)
    print("\n Processing finished.")


if __name__ == "__main__":
    main()
