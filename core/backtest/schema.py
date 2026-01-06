# core/backtest/schema.py

import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable


# ============================================================
# Canonical field names (we operate ONLY on these internally)
# ============================================================

CANONICAL_FIELDS = ("open", "high", "low", "close", "volume")


# ============================================================
# Accepted column name candidates (case-insensitive)
# ============================================================

FIELD_CANDIDATES = {
    "open": ("open", "o"),
    "high": ("high", "h"),
    "low": ("low", "l"),
    "close": ("close", "c"),
    "volume": ("volume", "v"),
}


# ============================================================
# Timeframe detection (suffix-based)
# ============================================================

TIMEFRAME_PATTERN = re.compile(r"(M\d+|H\d+|D1|W1|MN1)$", re.IGNORECASE)


# ============================================================
# MarketSchema
# ============================================================

@dataclass(frozen=True)
class MarketSchema:
    """
    Maps a flat CSV row into a multi-timeframe OHLCV structure.

    Example:
        fields = {
            "M15": {"open": "open_M15", "close": "close_M15"},
            "H1":  {"open": "open_H1",  "close": "close_H1"},
        }
    """

    time_column: str
    fields: Dict[str, Dict[str, str]]
    # fields[timeframe][canonical_field] -> column name


# ============================================================
# Schema inference
# ============================================================

def infer_schema(columns: Iterable[str]) -> MarketSchema:
    """
    Infer MarketSchema from CSV headers.

    This function is intentionally defensive:
    - forces all column names to strings
    - ignores unknown columns
    - does NOT assume any fixed set of timeframes
    """

    # ---- force string column names (IMPORTANT)
    columns = [str(c) for c in columns]

    # --------------------------------------------------------
    # Detect time column
    # --------------------------------------------------------

    time_candidates = ("timestamp", "time", "datetime", "date")

    time_column = None
    for col in columns:
        if col.lower() in time_candidates:
            time_column = col
            break

    if time_column is None:
        raise ValueError(
            "infer_schema: no time column found "
            "(expected one of: timestamp, time, datetime, date)"
        )

    # --------------------------------------------------------
    # Detect OHLCV columns per timeframe
    # --------------------------------------------------------

    tf_map: Dict[str, Dict[str, str]] = defaultdict(dict)

    for col in columns:
        if col == time_column:
            continue

        # expected pattern: <field>_<TF>
        parts = col.split("_")
        if len(parts) < 2:
            continue

        field_raw = parts[0].lower()
        tf_raw = parts[-1].upper()

        if not TIMEFRAME_PATTERN.fullmatch(tf_raw):
            continue

        for canonical, candidates in FIELD_CANDIDATES.items():
            if field_raw in candidates:
                tf_map[tf_raw][canonical] = col
                break

    if not tf_map:
        raise ValueError(
            "infer_schema: no OHLCV timeframe columns detected"
        )

    return MarketSchema(
        time_column=time_column,
        fields=dict(tf_map),
    )
