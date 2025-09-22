import pandas as pd
import libs.file_utils as fu
import libs.time_series as ts


if __name__ == "__main__":
    file = fu.get_valid_file("Enter the file location: ")
    df = pd.read_csv(file, sep=";", parse_dates=["timestamp"])

    for key, tf in ts.MENU_TO_TIMEFRAME.items():
        print(f"     {key} - {tf}")

    while True:
        choice = input("Select timeframe: ").strip()
        if choice.isdigit():
            choice = int(choice)
            if choice in ts.MENU_TO_TIMEFRAME:
                tf_str = ts.MENU_TO_TIMEFRAME[choice]
                break
        print("Invalid timeframe. Try again.")

    result = ts.is_timeseries_continuous(df, tf_str)
    print("Continuity check:", result)

    if not result:
        breaks = ts.get_timeseries_break(df, tf_str)

        if breaks:
            print("\nDetected breaks:")
            for br in breaks:
                print(f"  start: {br['start']}   end: {br['end']}")

            # zapis do CSV
            breaks_df = pd.DataFrame(breaks)
            output_file = "timeseries_breaks.csv"
            breaks_df.to_csv(output_file, index=False)
            print(f"\nBreaks saved to: {output_file}")
        else:
            print("\nNo breaks detected (unexpected).")
