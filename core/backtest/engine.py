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

        if action == "OPEN" and position is None:
            position = {
                "entry_price": state["bars"]["M15"]["close"],      # TODO (this is temporary)
                "entry_index": state["index"],
            }

        elif action == "CLOSE" and position is not None:
            trades.append({
                "entry_price": position["entry_price"],
                "exit_price": state["bars"]["M15"]["close"],
                "entry_index": position["entry_index"],
                "exit_index": state["index"],
            })
            position = None

    return trades
