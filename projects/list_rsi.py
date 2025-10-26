# projects/list_rsi.py
import pandas as pd
import libs.file_utils as fu
import libs.csv_utils as cu


def main():
    print("RSI Threshold Trigger Extractor")

    # Step 1: Load input CSV
    input_path = fu.get_valid_file("Enter path to CSV file: ")
    df = cu.load_csv(input_path, sep=",")

    # Step 2: Display available columns (one per line)
    print("\nAvailable columns:")
    for col in df.columns:
        print(" -", col)

    # Step 3: Ask user which RSI column to analyze
    column_name = input("\nEnter RSI column name: ").strip()
    while column_name not in df.columns:
        print(f"Column '{column_name}' not found. Try again.")
        column_name = input("Enter RSI column name: ").strip()

    # Step 4: Ask for RSI threshold
    while True:
        try:
            threshold = float(input("\nEnter RSI threshold value (e.g., 30): ").strip())
            break
        except ValueError:
            print("Please enter a valid number.")

    # Step 5: Find rows where RSI < threshold
    below_threshold = []
    last_below = False  # flag to skip consecutive below-threshold RSI

    for i in range(len(df)):
        rsi_val = df[column_name].iloc[i]
        if pd.isna(rsi_val):
            continue

        if not last_below and rsi_val < threshold:
            row = {
                "timestamp": df["timestamp"].iloc[i],
                "low": df[[c for c in df.columns if "low" in c.lower()][0]].iloc[i],
                "rsi": rsi_val,
            }
            below_threshold.append(row)
            last_below = True
        elif rsi_val > threshold:
            last_below = False

    # Step 6: Convert results to DataFrame
    result_df = pd.DataFrame(below_threshold)

    # Step 7: Save output CSV
    output_path = input("\nEnter output CSV file path: ").strip()
    if not output_path.lower().endswith(".csv"):
        output_path += ".csv"

    result_df.to_csv(output_path, sep=";", index=False)
    print(f"\nFound {len(result_df)} trigger rows. Saved to '{output_path}'.")


if __name__ == "__main__":
    main()
