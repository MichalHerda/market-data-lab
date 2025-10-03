import os
import pandas as pd
import libs.file_utils as fu
import libs.csv_utils as cu


def list_csv_files(folder_path: str):
    """List all CSV files in the given folder"""
    return [f for f in os.listdir(folder_path) if f.endswith(".csv")]


def extract_timeframes(files):
    """Extract timeframe labels from filenames (e.g. EURUSD_M5.csv -> M5)"""
    timeframes = {}
    for f in files:
        parts = f.split("_")
        if len(parts) > 1:
            tf = parts[-1].replace(".csv", "")
            timeframes[tf] = f
    return timeframes


def choose_timeframes(timeframes: dict):
    """Let user choose multiple timeframes to merge"""
    chosen = []
    while True:
        print("\nAvailable timeframes:")
        for tf in timeframes:
            print(f" - {tf}")
        print("Press ENTER to start processing if you have selected at least one timeframe.")
        choice = input("Enter timeframe to add: ").strip().upper()
        if choice == "" and len(chosen) > 0:
            return chosen
        elif choice in timeframes and choice not in chosen:
            chosen.append(choice)
            print(f"Added timeframe: {choice}")
        elif choice in chosen:
            print("This timeframe is already selected.")
        else:
            print("Invalid timeframe. Try again.")


def choose_action():
    """Ask user what to do with the result"""
    while True:
        print("\nWhat would you like to do with the result?")
        print(" 1. Overwrite original subfolders with merged CSVs")
        print(" 2. Save merged CSVs in a new output folder")
        try:
            choice = int(input("Your choice (1/2): ").strip())
            if choice in (1, 2):
                return choice
        except ValueError:
            pass
        print("Invalid option. Please enter 1 or 2.\n")


def merge_timeframes_in_folder(folder_path: str, chosen_tfs: list, output_folder: str = None):
    """Merge selected timeframes in a single instrument folder"""
    files = list_csv_files(folder_path)
    timeframes = extract_timeframes(files)

    merged_df = None
    for tf in chosen_tfs:
        if tf not in timeframes:
            print(f"  Skipping {tf} (not found in {folder_path})")
            continue
        file_path = os.path.join(folder_path, timeframes[tf])
        df = cu.load_csv(file_path, sep=";")

        # detect time column
        time_col = next((c for c in df.columns if c.lower() in ["date", "time", "timestamp"]), None)
        if not time_col:
            print(f"  No valid time column found in {file_path}. Skipping.")
            return None

        # rename columns except time
        df = df.rename(columns=lambda x: f"{x}_{tf}" if x != time_col else x)

        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on=time_col, how="outer")

    if merged_df is not None:
        merged_df = merged_df.sort_values(by=time_col).ffill()

        instrument_name = os.path.basename(folder_path)
        save_file = f"{instrument_name}_merged.csv"

        if output_folder:
            os.makedirs(output_folder, exist_ok=True)
            save_path = os.path.join(output_folder, save_file)
        else:
            save_path = os.path.join(folder_path, save_file)

        cu.save_csv(merged_df, save_path, sep=";")
        print(f"  Saved merged CSV for {instrument_name} -> {save_path}")


def main():
    # Step 1: Ask for parent folder
    parent_folder = fu.get_valid_folder("Enter the path to the parent folder (with instrument subfolders): ")

    # Detect first subfolder to get available timeframes
    subfolders = [os.path.join(parent_folder, d) for d in os.listdir(parent_folder)
                  if os.path.isdir(os.path.join(parent_folder, d))]
    if not subfolders:
        print("No subfolders found in the given folder.")
        return

    # Assume all subfolders share same TF structure -> use first one
    sample_files = list_csv_files(subfolders[0])
    sample_tfs = extract_timeframes(sample_files)
    if not sample_tfs:
        print("No valid timeframe CSV files found in sample folder.")
        return

    # Step 2: Choose timeframes
    chosen_tfs = choose_timeframes(sample_tfs)

    # Step 3: Choose action
    action = choose_action()

    if action == 2:
        output_folder = input("Enter path for new output folder: ").strip()
        os.makedirs(output_folder, exist_ok=True)
    else:
        output_folder = None

    # Step 4: Process all subfolders
    print("\nProcessing all subfolders...\n")
    for sub in sorted(subfolders):
        merge_timeframes_in_folder(sub, chosen_tfs, output_folder)


if __name__ == "__main__":
    main()
