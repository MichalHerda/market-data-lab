import argparse
import pandas as pd
from pathlib import Path

from core.backtest.engine import run_backtest
from core.backtest.strategies import STRATEGIES


def main():
    parser = argparse.ArgumentParser("backtest")

    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--strategy", type=str, required=True)
    parser.add_argument("--capital", type=float, default=10_000)

    args = parser.parse_args()

    if args.strategy not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {args.strategy}")

    strategy_fn = STRATEGIES[args.strategy]

    df = pd.read_csv(args.data)

    params = {
        "last_index": len(df) - 1,
        "capital": args.capital,
    }

    trades = run_backtest(
        data=df,
        strategy=strategy_fn,
        params=params,
    )

    print(f"Trades: {len(trades)}")
    for t in trades:
        print(t)


if __name__ == "__main__":
    main()
