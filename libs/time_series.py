import pandas as pd

TIMEFRAME_TO_DELTA = {
    "M1": pd.Timedelta(minutes=1),
    "M5": pd.Timedelta(minutes=5),
    "M15": pd.Timedelta(minutes=15),
    "M30": pd.Timedelta(minutes=30),
    "H1": pd.Timedelta(hours=1),
    "H4": pd.Timedelta(hours=4),
    "D1": pd.Timedelta(days=1),
    "W1": pd.DateOffset(weeks=1),
    "MN1": pd.DateOffset(months=1),
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

    if isinstance(expected_delta, pd.Timedelta):
        return diffs.eq(expected_delta).all()

    if isinstance(expected_delta, pd.DateOffset):
        shifted = df["timestamp"].shift(1) + expected_delta
        return (df["timestamp"].dropna() == shifted.dropna()).all()

    return False


def get_timeseries_break(df: pd.DataFrame, timeframe: str) -> list[dict]:
    if timeframe not in TIMEFRAME_TO_DELTA:
        raise ValueError(f"Unsupported timeframe: {timeframe}")

    expected_delta = TIMEFRAME_TO_DELTA[timeframe]
    breaks: list[dict] = []

    prev_ts = None
    current_break = None

    for idx, row in df.iterrows():
        ts = row["timestamp"]

        if prev_ts is None:
            prev_ts = ts
            continue

        diff = ts - prev_ts

        if isinstance(expected_delta, pd.Timedelta):
            gap_detected = diff != expected_delta
        else:  # DateOffset (np. miesiące)
            gap_detected = ts != prev_ts + expected_delta

        if gap_detected:
            if current_break is None:
                current_break = {"start":
                                 prev_ts.strftime("%Y-%m-%d %H:%M:%S"),
                                 "end": ts.strftime("%Y-%m-%d %H:%M:%S")}
            else:
                current_break["end"] = ts.strftime("%Y-%m-%d %H:%M:%S")
        else:
            if current_break is not None:
                breaks.append(current_break)
                current_break = None

        prev_ts = ts

    if current_break is not None:
        breaks.append(current_break)

    return breaks
