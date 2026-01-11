# core/backtest/engine.py

def run_backtest(bars_stream, strategy, params):
    position = None
    trades = []

    # -----------------------------------------
    # INIT HISTORY STORAGE
    # -----------------------------------------
    history = {}

    for item in bars_stream:
        # -----------------------------------------
        # Update history with current bar
        # -----------------------------------------
        for tf, bar in item["bars"].items():
            if tf not in history:
                history[tf] = {
                    "open": [],
                    "high": [],
                    "low": [],
                    "close": [],
                    "volume": [],
                }

            for k in history[tf]:
                if k in bar:
                    history[tf][k].append(bar[k])

        # -----------------------------------------
        # Build state
        # -----------------------------------------
        state = {
            "time": item["time"],
            "index": item["index"],
            "bars": item["bars"],
            "position": position,
        }

        # expose history to strategy
        params["_history"] = history

        action = strategy(state, params)

        # -----------------------------------------
        # Execution (still single-position model)
        # -----------------------------------------
        tf = next(iter(state["bars"]))
        close_price = state["bars"][tf]["close"]

        if action == "OPEN" and position is None:
            position = {
                "entry_price": close_price,
                "entry_index": state["index"],
                "timeframe": tf,
            }

        elif action == "CLOSE" and position is not None:
            trades.append({
                "entry_price": position["entry_price"],
                "exit_price": close_price,
                "entry_index": position["entry_index"],
                "exit_index": state["index"],
                "timeframe": position["timeframe"],
            })
            position = None

    return trades
