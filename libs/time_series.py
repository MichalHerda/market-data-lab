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
