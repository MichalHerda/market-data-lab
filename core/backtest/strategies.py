def buy_and_hold(state, params):
    if state["index"] == 0:
        return "BUY"
    if state["index"] == params["last_index"]:
        return "SELL"
    return "HOLD"


STRATEGIES = {
    "buy_and_hold": buy_and_hold,
}
