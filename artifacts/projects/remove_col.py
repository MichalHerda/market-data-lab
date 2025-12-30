import libs.file_utils as fu
import libs.csv_utils as cu


def choose_column(df) -> str:
    """Ask user to choose which column to delete"""
    print("\nAvailable columns:")
    for col in df.columns:
        print(f" - {col}")
    column = input("\nEnter the column name to delete: ").strip()
    while column not in df.columns:
        print(f"Column '{column}' does not exist in DataFrame. Try again.\n")
        column = input("Enter the column name to delete: ").strip()
    return column


def choose_action() -> int:
    """Ask user what to do with the result"""
    while True:
        print("\nWhat would you like to do with the result?")
        print(" 1. Overwrite the original CSV file")
        print(" 2. Save as a new CSV file")
        try:
            choice = int(input("Your choice (1/2): ").strip())
            if choice in (1, 2):
                return choice
            else:
                print("Invalid option. Please enter 1 or 2.\n")
        except ValueError:
            print("Please enter a valid number (1 or 2).\n")


def main():
    # Step 1: Ask for DataFrame file
    file_path = fu.get_valid_file("Enter the path to the DataFrame file (CSV): ")
    df = cu.load_csv(file_path, sep=";")

    print("\nDataFrame loaded successfully!")
    print(f"Columns available: {', '.join(df.columns)}")

    # Step 2: Ask which column to delete
    column = choose_column(df)

    # Step 3: Remove column
    result = df.drop(columns=[column])
    print(f"\nColumn '{column}' removed successfully!")

    # Step 4: Decide what to do
    action = choose_action()

    if action == 1:
        cu.save_csv(result, file_path, sep=";")
        print(f"Original file '{file_path}' overwritten.")
    else:
        save_path = input("\nEnter output CSV path: ").strip()
        cu.save_csv(result, save_path, sep=";")
        print(f"Result saved to {save_path}")

    # Step 5: Show preview
    print("\nResulting DataFrame (head):")
    print(result.head())


if __name__ == "__main__":
    main()
