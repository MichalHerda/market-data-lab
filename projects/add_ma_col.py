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
        print(" 1. Add moving average column to the input CSV (overwrite input)")
        print(" 2. Save moving average to a new CSV file")
        try:
            choice = int(input("Your choice (1/2): ").strip())
            if choice in (1, 2):
                return choice
            print("Invalid option. Please enter 1 or 2.\n")
        except ValueError:
            print("Please enter a valid number (1 or 2).\n")


def main():
    # Step 1: Ask for DataFrame file
    file_path = fu.get_valid_file("Enter the path to the DataFrame file (CSV): ")
    df = cu.load_csv(file_path, sep=";")

    print("\nDataFrame loaded successfully!")
    print(f"Columns available: {', '.join(df.columns)}")

    # Step 2: Ask which column to use
    column = input("Enter the column name for moving average: ").strip()
    while column not in df.columns:
        print(f"Column '{column}' does not exist in DataFrame. Try again.\n")
        column = input("Enter the column name for moving average: ").strip()

    # Step 3: Choose method
    method = choose_method()

    # Step 4: Choose period
    period = choose_period(len(df))

    # Step 5: Compute moving average
    ma_series = ma.moving_average(df[column], period, method)
    ma_column_name = f"{method.upper()}_{period}"

    # Step 6: Decide action
    action = choose_action()

    if action == 1:
        # Overwrite input CSV with new column
        df[ma_column_name] = ma_series
        cu.save_csv(df, file_path, sep=";")
        print(f"\n✅ Input file updated with new column '{ma_column_name}'.")
    else:
        # Save new CSV
        new_df = pd.DataFrame({ma_column_name: ma_series})
        save_path = fu.get_valid_file("Enter output CSV path to save new file: ")
        cu.save_csv(new_df, save_path, sep=";")
        print(f"\n✅ New file saved at {save_path}.")

    # Step 7: Show preview
    print("\nResulting DataFrame (head):")
    print(df.head() if action == 1 else new_df.head())


if __name__ == "__main__":
    main()
