import pandas as pd
import os

TIMEFRAME_TO_DELTA = {
    "M1": pd.Timedelta(minutes=1),
    "M5": pd.Timedelta(minutes=5),
    "M15": pd.Timedelta(minutes=15),
    "M30": pd.Timedelta(minutes=30),
    "H1": pd.Timedelta(hours=1),
    "H4": pd.Timedelta(hours=4),
    "D1": pd.Timedelta(days=1),
    "W1": pd.DateOffset(weeks=1),
    "MN1": pd.DateOffset(months=1)
}

MENU_TO_TIMEFRAME = {
    1: "M1",
    2: "M5",
    3: "M15",
    4: "M30",
    5: "H1",
    6: "H4",
    7: "D1",
    8: "W1",
    9: "MN1",
}


def is_timeseries_continuous(df: pd.DataFrame, timeframe: str) -> bool:
    if timeframe not in TIMEFRAME_TO_DELTA:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    expected_delta = TIMEFRAME_TO_DELTA[timeframe]

    diffs = df["timestamp"].diff().dropna()
    print(diffs)

    # timedelta (np. dla minut, godzin, dni)
    if isinstance(expected_delta, pd.Timedelta):
        return diffs.eq(expected_delta).all()

    # dateoffset (np. tygodnie, miesiące)
    if isinstance(expected_delta, pd.DateOffset):
        shifted = df["timestamp"].shift(1) + expected_delta
        return (df["timestamp"].dropna() == shifted.dropna()).all()

    return False


def get_valid_file(prompt: str) -> str:
    """Gets the path to an existing file from the user"""
    while True:
        file_path = input(prompt).strip('"').strip("'")
        if os.path.isfile(file_path):
            return file_path
        else:
            print(f" Path '{file_path}' does not exist. Try again \n")


if __name__ == "__main__":
    file = get_valid_file("Enter the file location: ")
    df = pd.read_csv(file, sep=";", parse_dates=["timestamp"])

    for key, tf in MENU_TO_TIMEFRAME.items():
        print(f"     {key} - {tf}")

    while True:
        choice = input("Select timeframe: ").strip()
        if choice.isdigit():
            choice = int(choice)
            if choice in MENU_TO_TIMEFRAME:
                tf_str = MENU_TO_TIMEFRAME[choice]
                result = is_timeseries_continuous(df, tf_str)
                print("Continuity check:", result)
                break
        print("Invalid timeframe. Try again.")
