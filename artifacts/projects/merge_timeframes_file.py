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
            timeframes[tf.upper()] = f
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
        print(" 1. Overwrite one of the input CSV files")
        print(" 2. Save as a new CSV file")
        try:
            choice = int(input("Your choice (1/2): ").strip())
            if choice in (1, 2):
                return choice
        except ValueError:
            pass
        print("Invalid option. Please enter 1 or 2.\n")


def detect_time_column(df):
    """Detect which column should be used as time index"""
    candidates = [c for c in df.columns if c.lower() in ("date", "timestamp", "time")]
    if not candidates:
        raise ValueError("No valid time column found (expected 'date', 'timestamp' or 'time').")
    return candidates[0]


def main():
    # Step 1: Ask for folder
    folder_path = fu.get_valid_folder("Enter the path to the folder with CSV files: ")

    files = list_csv_files(folder_path)
    if not files:
        print("No CSV files found in the given folder.")
        return

    timeframes = extract_timeframes(files)
    if not timeframes:
        print("No valid timeframe CSV files found.")
        return

    # Step 2: Choose timeframes
    chosen_tfs = choose_timeframes(timeframes)

    # Step 3: Load and merge CSVs
    merged_df = None
    time_column = None

    for tf in chosen_tfs:
        file_path = os.path.join(folder_path, timeframes[tf])
        df = cu.load_csv(file_path, sep=";")

        if time_column is None:
            time_column = detect_time_column(df)
            print(f"Using '{time_column}' as the time column.")

        # Upewnij się, że czas jest typu datetime
        df[time_column] = pd.to_datetime(df[time_column])

        # Rename all except the time column
        df = df.rename(columns=lambda x: x if x == time_column else f"{x}_{tf}")

        if merged_df is None:
            merged_df = df
        else:
            merged_df = pd.merge(merged_df, df, on=time_column, how="outer")

    # Sort and forward fill bigger TFs
    merged_df = merged_df.sort_values(by=time_column).reset_index(drop=True)
    merged_df = merged_df.ffill()  # <-- najważniejsze: wypełnia puste wartości

    # Step 4: Decide action
    action = choose_action()

    if action == 1:
        overwrite_file = os.path.join(folder_path, timeframes[chosen_tfs[0]])
        cu.save_csv(merged_df, overwrite_file, sep=";")
        print(f"File '{overwrite_file}' overwritten with merged data.")
    else:
        save_path = input("Enter output CSV path: ").strip()
        cu.save_csv(merged_df, save_path, sep=";")
        print(f"Merged data saved to '{save_path}'.")

    # Step 5: Preview
    print("\nResulting DataFrame (head):")
    print(merged_df.head())


if __name__ == "__main__":
    main()
