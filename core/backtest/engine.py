# core/backtest/engine.py

def run_backtest(bars_stream, strategy, params):
    position = None
    trades = []

    for item in bars_stream:
        state = {
            "time": item["time"],
            "index": item["index"],
            "bars": item["bars"],
            "position": position,
        }

        action = strategy(state, params)

        # select TF - first available is default
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
