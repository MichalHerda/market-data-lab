# trend.py

from enum import Enum
from typing import Sequence
import math


class Trend(Enum):
    UP = "up"
    DOWN = "down"
    FLAT = "flat"


def trend(series: Sequence[float], lookback: int = 2) -> Trend:
    """
    Determine trend direction based on monotonicity
    of the last N values in a series.

    Parameters
    ----------
    series : Sequence[float]
        Series of values (e.g. moving average).
        Most recent value must be last.
    lookback : int
        Number of consecutive steps required to confirm a trend.
        lookback = 2 means: b0 vs b1
        lookback = 3 means: b0 vs b1 vs b2

    Returns
    -------
    Trend.UP | Trend.DOWN | Trend.FLAT
    """

    if lookback < 2:
        raise ValueError("lookback must be >= 2")

    if len(series) < lookback:
        return Trend.FLAT

    # take only the last N values
    window = list(series[-lookback:])

    # remove NaNs
    if any(x is None or (isinstance(x, float) and math.isnan(x)) for x in window):
        return Trend.FLAT

    increasing = True
    decreasing = True

    for prev, curr in zip(window, window[1:]):
        if curr <= prev:
            increasing = False
        if curr >= prev:
            decreasing = False

    if increasing:
        return Trend.UP
    if decreasing:
        return Trend.DOWN

    return Trend.FLAT
