import pandas as pd
import libs.file_utils as fu
import libs.csv_utils as cu
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Trade:
    open_time: datetime
    open_price: float
    close_time: datetime = None
    close_price: float = None
    result: str = None
    lot_size: float = 0.1
    sl: float = 0.0
    tp: float = 0.0


RSI_ENTRY_LEVEL = 35
SL_PIPS = 100
TP_PIPS = 100


trades: list[Trade] = []
in_position = False
current_sl = 0
current_tp = 0
sl_total = 0
tp_total = 0


def is_rsi_entry(rsi_val: float, level: float = RSI_ENTRY_LEVEL) -> bool:
    return rsi_val <= level


def calculate_sl(price: float) -> float:
    global SL_PIPS
    return price - SL_PIPS


def calculate_tp(price: float) -> float:
    global TP_PIPS
    return price + TP_PIPS


def is_sl(price: float):
    global current_sl
    return price <= current_sl


def is_tp(price: float):
    global current_tp
    return price >= current_tp


def process_row(row: pd.Series) -> None:
    global in_position, trades, current_sl, current_tp, sl_total, tp_total
    price = row["open"]
    if not in_position and is_rsi_entry(row["RSI_14"]):
        trade = Trade(
            open_time=row["timestamp"],
            open_price=row["close"],
            sl=row["close"] - SL_PIPS,
            tp=row["close"] + TP_PIPS
        )
        trades.append(trade)
        current_sl = trade.open_price - SL_PIPS
        current_tp = trade.open_price + TP_PIPS
        in_position = True
    if in_position and trades:
        if is_sl(price):
            trades[-1].close_time = row["timestamp"]
            trades[-1].close_price = price
            trades[-1].result = "SL"
            in_position = False
            current_sl = 0
            current_tp = 0
            sl_total += 1
        elif is_tp(price):
            trades[-1].close_time = row["timestamp"]
            trades[-1].close_price = price
            trades[-1].result = "TP"
            in_position = False
            current_sl = 0
            current_tp = 0
            tp_total += 1


def main() -> None:
    global sl_total, tp_total
    print("opened as main")
    input_path = fu.get_valid_file("enter the path to CSV file: ")
    data = cu.load_csv(input_path)
    for index, row in data.iterrows():
        process_row(row)
    if trades:
        output_path = "signals_output.csv"
        pd.DataFrame(trades).to_csv(output_path, index=False)
        print(f"\n Zapisano {len(trades)} sygnałów do pliku: {output_path}")
    else:
        print("\n Nie znaleziono żadnych sygnałów do zapisania.")
    print("sl total: ", sl_total)
    print("tp_total: ", tp_total)


if __name__ == "__main__":
    main()
