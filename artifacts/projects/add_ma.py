import os
import libs.moving_average as ma
import libs.file_utils as fu
import libs.csv_utils as cu


def choose_method() -> str:
    """Ask user to choose type of moving average"""
    methods = {1: "sma", 2: "ema", 3: "wma"}
    while True:
        print("\nChoose moving average type:")
        print(" 1. SMA (Simple Moving Average)")
        print(" 2. EMA (Exponential Moving Average)")
        print(" 3. WMA (Weighted Moving Average)")
        try:
            choice = int(input("Your choice (1/2/3): ").strip())
            if choice in methods:
                return methods[choice]
            print("Invalid option. Please enter 1, 2 or 3.\n")
        except ValueError:
            print("Please enter a valid number (1/2/3).\n")


def choose_period(max_period: int) -> int:
    """Ask user to choose period for moving average"""
    while True:
        try:
            period = int(input(f"Enter the moving average period (1-{max_period}): ").strip())
            if period < 1:
                print("Period must be a positive number.\n")
            elif period > max_period:
                print(f"Period cannot be greater than the number of available rows ({max_period}).\n")
            else:
                return period
        except ValueError:
            print("Please enter a valid integer.\n")


def choose_action() -> int:
    """Ask user what to do with the result"""
    while True:
        print("\nWhat would you like to do with the result?")
        print(" 1. Add moving average column to input CSVs (overwrite originals)")
        print(" 2. Save modified CSVs into a new folder (keep originals unchanged)")
        try:
            choice = int(input("Your choice (1/2): ").strip())
            if choice in (1, 2):
                return choice
            print("Invalid option. Please enter 1 or 2.\n")
        except ValueError:
            print("Please enter a valid number (1 or 2).\n")


def process_csv(file_path: str, column: str, method: str, period: int, timeframe: str, output_folder: str = None):
    """Load CSV, compute moving average, and save result"""
    try:
        df = cu.load_csv(file_path, sep=";")
    except Exception as e:
        print(f"Could not load {file_path}: {e}")
        return

    if column not in df.columns:
        print(f"Column '{column}' not found in {file_path}. Skipped.")
        return

    ma_series = ma.moving_average(df[column], period, method)
    new_col_name = f"{method.upper()}_{timeframe.upper()}_{period}"
    df[new_col_name] = ma_series

    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        save_path = os.path.join(output_folder, os.path.basename(file_path))
    else:
        save_path = file_path

    cu.save_csv(df, save_path, sep=";")
    print(f"Processed {os.path.basename(file_path)} → added column '{new_col_name}'.")


def main():
    # Step 1: Ask for file or folder
    input_path = fu.get_valid_path("Enter path to CSV file or folder: ")

    # Step 2: Gather CSVs
    csv_files = []
    if os.path.isfile(input_path) and input_path.lower().endswith(".csv"):
        csv_files.append(input_path)
    elif os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.lower().endswith(".csv"):
                    csv_files.append(os.path.join(root, f))
    else:
        print("Invalid path. Must be a CSV file or folder containing CSVs.")
        return

    if not csv_files:
        print("No CSV files found in the given path.")
        return

    print(f"\nFound {len(csv_files)} CSV file(s) to process.")

    # Step 3: Inspect first file
    sample_df = cu.load_csv(csv_files[0], sep=";")
    print(f"\nColumns available: {', '.join(sample_df.columns)}")

    column = input("Enter the column name for moving average: ").strip()
    while column not in sample_df.columns:
        print(f"Column '{column}' does not exist. Try again.\n")
        column = input("Enter the column name for moving average: ").strip()

    # Step 4: Ask for timeframe
    timeframe = input("Enter timeframe label (e.g., MN1, W1, D1, H4, H1, M30, M15, M5, M1): ").strip().upper()

    # Step 5: Choose method and period
    method = choose_method()
    period = choose_period(len(sample_df))

    # Step 6: Choose save mode
    action = choose_action()
    output_folder = None
    if action == 2:
        output_folder = input("Enter output folder path: ").strip()
        os.makedirs(output_folder, exist_ok=True)

    # Step 7: Process only matching files
    processed = 0
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        # Process only files matching the chosen timeframe
        if f"_{timeframe.upper()}" in filename:
            process_csv(file_path, column, method, period, timeframe, output_folder)
            processed += 1
        else:
            print(f"Skipped {filename} (does not match timeframe {timeframe}).")

    if processed == 0:
        print(f"\n No files matching timeframe '{timeframe}' were found.")
    else:
        print(f"\n Processing finished. {processed} file(s) updated.")


if __name__ == "__main__":
    main()
