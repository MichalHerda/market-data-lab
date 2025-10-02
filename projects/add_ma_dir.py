import os
import pandas as pd
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


def process_csv(file_path: str, column: str, method: str, period: int) -> pd.DataFrame:
    """Load CSV, compute moving average, and return updated DataFrame"""
    df = cu.load_csv(file_path, sep=";")
    ma_series = ma.moving_average(df[column], period, method)
    df[f"{method.upper()}_{period}"] = ma_series
    return df


def main():
    # Step 1: Ask for folder path
    folder = fu.get_valid_folder("Enter the path to the parent folder: ")

    # Step 2: Collect CSV files
    csv_files = []
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(".csv"):
                csv_files.append(os.path.join(root, f))

    if not csv_files:
        print("No CSV files found in the given folder.")
        return

    print(f"\nFound {len(csv_files)} CSV files under {folder}.")

    # Step 3: Load first file to check columns
    sample_df = cu.load_csv(csv_files[0], sep=";")
    print(f"\nColumns available: {', '.join(sample_df.columns)}")

    column = input("Enter the column name for moving average: ").strip()
    while column not in sample_df.columns:
        print(f"Column '{column}' does not exist. Try again.\n")
        column = input("Enter the column name for moving average: ").strip()

    # Step 4: Choose method and period
    method = choose_method()
    period = choose_period(len(sample_df))

    # Step 5: Choose action
    action = choose_action()

    if action == 2:
        output_folder = fu.get_valid_folder("Enter the output folder path: ")
    else:
        output_folder = None

    # Step 6: Process files
    for file_path in csv_files:
        df = process_csv(file_path, column, method, period)

        if action == 1:
            # Overwrite original file
            cu.save_csv(df, file_path, sep=";")
            print(f"Updated {file_path}")
        else:
            # Save to new folder, keeping relative structure
            rel_path = os.path.relpath(file_path, folder)
            new_path = os.path.join(output_folder, rel_path)
            cu.save_csv(df, new_path, sep=";")
            print(f"Saved {new_path}")

    print("\n Processing finished.")


if __name__ == "__main__":
    main()
