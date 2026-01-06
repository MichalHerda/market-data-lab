# scripts/backtest.py

import argparse
import pandas as pd
from pathlib import Path

from core.backtest.schema import infer_schema
from core.backtest.adapters import dataframe_to_bars_stream
from core.backtest.engine import run_backtest
from core.backtest.strategies import STRATEGIES


def main():
    parser = argparse.ArgumentParser("backtest")

    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--strategy", required=True)

    args = parser.parse_args()

    # 1️⃣ load CSV
    df = pd.read_csv(args.data, sep=None, engine="python")

    # 2️⃣ infer schema from headers
    schema = infer_schema(df.columns)

    # 3️⃣ build bars stream
    bars_stream = dataframe_to_bars_stream(df, schema)

    # 4️⃣ select strategy
    strategy_fn = STRATEGIES[args.strategy]

    # 5️⃣ run engine
    trades = run_backtest(
        bars_stream=bars_stream,
        strategy=strategy_fn,
        params={},
    )

    print(trades)


if __name__ == "__main__":
    main()
