import pandas as pd
import libs.file_utils as fu
import libs.csv_utils as cu
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


@dataclass
class Trade:
    open_time: datetime
    open_price: float
    close_time: datetime = None
    close_price: float = None
    result: str = None  # 'TP' lub 'SL'
    lot_size: float = 0.1
    sl: float = 0.0
    tp: float = 0.0


class Timeframe(Enum):
    MN1 = "MN1"
    W1 = "W1"
    D1 = "D1"
    H4 = "H4"
    H1 = "H1"
    M30 = "M30"
    M15 = "M15"
    M5 = "M5"
    M1 = "M1"


RSI_ENTRY_LEVEL = None
HIGH_TREND = None
MEDIUM_TREND = None
LOW_TREND = None


def select_timeframe(timeframe: str) -> enumerate:
    print(f"Select {timeframe} timeframe:")
    for i, tf in enumerate(Timeframe, start=1):
        print(f"{i}. {tf.value}")
    choice = int(input("Your choice: "))
    selected_tf = list(Timeframe)[choice - 1]
    print(f"Selected timeframe: {selected_tf.value}")
    return selected_tf


def process_file(file_path: str) -> None:
    trades: list[Trade] = []
    in_position = False
    current_sl = 0.0
    current_tp = 0.0
    sl_total = 0
    tp_total = 0

    try:
        df = cu.load_csv(file_path)
    except Exception as e:
        print(f"Could not load {file_path}: {e}")
        return


def main() -> None:
    global HIGH_TREND, MEDIUM_TREND, LOW_TREND
    print("Multiframe Uptrend Rsi Tester")
    input_path = fu.get_valid_file("enter the path to CSV file: ")
    data = cu.load_csv(input_path)
    HIGH_TREND = select_timeframe("HIGH_TREND")
    MEDIUM_TREND = select_timeframe("MEDIUM_TREND")
    LOW_TREND = select_timeframe("LOW_TREND")
    process_file(input_path)


if __name__ == "__main__":
    main()
    print(HIGH_TREND)
    print(MEDIUM_TREND)
    print(LOW_TREND)
