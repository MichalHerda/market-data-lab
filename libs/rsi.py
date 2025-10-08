import pandas as pd


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Calculate RSI (Relative Strength Index) from a pandas Series of closing prices.

    Parameters
    ----------
    series : pd.Series
        Series of closing prices.
    period : int, optional
        RSI period length (default is 14).

    Returns
    -------
    pd.Series
        RSI values for each point in the series.
    """
    delta = series.diff()

    # separate gains and losses
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    # Wilder’s smoothing (similar to exponential, but slower)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi
