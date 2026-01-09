import core.indicators as indicators                # noqa


def buy_and_hold(state, params):
    if state["index"] == 0:
        return "OPEN"
    if state["index"] == params["last_index"]:
        return "CLOSE"
    return "HOLD"


STRATEGIES = {
    "buy_and_hold": buy_and_hold,
}
