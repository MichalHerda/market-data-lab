def run_backtest(data, strategy, params):
    position = None
    trades = []

    for i, row in data.iterrows():
        state = {
            "price": row["close"],
            "index": i,
            "position": position,
        }

        action = strategy(state, params)

        if action == "BUY" and position is None:
            position = {
                "entry_price": row["close"],
                "entry_index": i,
            }

        elif action == "SELL" and position is not None:
            trade = {
                "entry_price": position["entry_price"],
                "exit_price": row["close"],
                "entry_index": position["entry_index"],
                "exit_index": i,
            }
            trades.append(trade)
            position = None

    return trades
