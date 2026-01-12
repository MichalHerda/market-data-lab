# strategies.py

import core.indicators as indicators


def buy_and_hold(state, params):
    if state["index"] == 0:
        return "OPEN"
    if state["index"] == params["last_index"]:
        return "CLOSE"
    return "HOLD"


def trend_rsi_strategy(state, params):
    bars = state["bars"]                        # noqa
    position = state["position"]

    # --------------------------------------------------
    # Do not open new position if one already exists
    # --------------------------------------------------
    if position is not None:
        return "HOLD"

    # --------------------------------------------------
    # Check all trend conditions
    # --------------------------------------------------
    for cfg in params["trends"]:
        tf = cfg["timeframe"]

        closes = params["_history"][tf]["close"]

        ma = indicators.moving_average(
            closes,
            cfg["ma_period"],
            cfg.get("ma_type", "sma"),
        )

        t = indicators.trend(ma, cfg["trend_lookback"])

        required = indicators.Trend(cfg["required"])

        if t != required:
            return "HOLD"

    # --------------------------------------------------
    # Check RSI condition
    # --------------------------------------------------
    rsi_cfg = params["rsi"]
    tf = rsi_cfg["timeframe"]

    closes = params["_history"][tf]["close"]
    r = indicators.rsi(closes, rsi_cfg["period"]).iloc[-1]

    if params["direction"] == "BUY":
        if not (r < rsi_cfg["threshold"]):
            return "HOLD"
    else:  # SELL
        if not (r > rsi_cfg["threshold"]):
            return "HOLD"

    # --------------------------------------------------
    # All conditions met → OPEN
    # --------------------------------------------------
    return "OPEN"


STRATEGIES = {
    "buy_and_hold": buy_and_hold,
    "trend_rsi_strategy": trend_rsi_strategy
}
