# core/backtest/adapters.py

from typing import Dict, Iterator, Any
import pandas as pd

from .schema import MarketSchema


def dataframe_to_bars_stream(
    df: pd.DataFrame,
    schema: MarketSchema,
) -> Iterator[Dict[str, Any]]:
    """
    Convert a DataFrame into a stream of multi-timeframe market snapshots.
    """

    for i, row in df.iterrows():
        bars = {}

        for tf, field_map in schema.fields.items():
            tf_bar = {}
            for field, col_name in field_map.items():
                tf_bar[field] = row[col_name]
            bars[tf] = tf_bar

        yield {
            "time": row[schema.time_column],
            "bars": bars,
            "index": i,
        }
