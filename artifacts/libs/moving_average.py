import numpy as np


def sma(series, period):
    return series.rolling(window=period).mean()


def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()


def wma(series, period):
    weights = np.arange(1, period+1)
    return series.rolling(period).apply(lambda x: np.dot(x, weights)
                                        / weights.sum(), raw=True)


def moving_average(series, period, method="sma"):
    methods = {
        "sma": sma,
        "ema": ema,
        "wma": wma,
    }
    if method not in methods:
        raise ValueError(f"Unknown method: {method}")
    return methods[method](series, period)
