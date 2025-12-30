import os
import shutil
import libs.file_utils as fu


def delete_symbols(input_path: str, symbols: list, output_folder: str = None):
    """Delete selected symbols from files or folders"""
    if os.path.isdir(input_path):
        for item in os.listdir(input_path):
            item_path = os.path.join(input_path, item)
            matched = any(sym in item for sym in symbols)

            if matched:
                # Skip matched symbols, remove them if overwrite
                if output_folder:
                    # Copy everything except matched
                    continue
                else:
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.remove(item_path)
            else:
                if output_folder:
                    os.makedirs(output_folder, exist_ok=True)
                    dest_path = os.path.join(output_folder, item)
                    if os.path.isdir(item_path):
                        shutil.copytree(item_path, dest_path)
                    else:
                        shutil.copy2(item_path, dest_path)

    elif os.path.isfile(input_path) and input_path.endswith(".csv"):
        file_name = os.path.basename(input_path)
        matched = any(sym in file_name for sym in symbols)

        if matched:
            if not output_folder:
                os.remove(input_path)
            # If output folder given, we just don’t copy matched file
        else:
            if output_folder:
                os.makedirs(output_folder, exist_ok=True)
                shutil.copy2(input_path, os.path.join(output_folder, file_name))


def main():
    input_path = fu.get_valid_path("Enter path to CSV file or folder: ")

    # Show available items
    items = os.listdir(input_path) if os.path.isdir(input_path) else [os.path.basename(input_path)]
    print("\nAvailable items:")
    for it in sorted(items):
        print(" ", it)

    # Select symbols to delete
    print("\nEnter symbols you want to DELETE (one per line).")
    print("Press ENTER on empty line to finish.")
    symbols = []
    while True:
        sym = input("Symbol: ").strip()
        if not sym:
            break
        symbols.append(sym)

    if not symbols:
        print("No symbols entered. Nothing to do.")
        return

    # Choose action
    print("\nWhat would you like to do with the result?")
    print(" 1. Overwrite original location (delete symbols)")
    print(" 2. Save into a new folder (symbols excluded)")
    action = input("Your choice (1/2): ").strip()

    output_folder = None
    if action == "2":
        output_folder = input("Enter path for output folder: ").strip()
        os.makedirs(output_folder, exist_ok=True)

    delete_symbols(input_path, symbols, output_folder)

    print(f"\nProcessing finished. Symbols deleted: {', '.join(symbols)}")


if __name__ == "__main__":
    main()
