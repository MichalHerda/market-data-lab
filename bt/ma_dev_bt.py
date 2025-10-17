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
    result: str = None  # 'TP' lub 'SL'
    lot_size: float = 0.1
    sl: float = 0.0
    tp: float = 0.0


MA_FAST_PERIOD = 50
MA_SLOW_PERIOD = 50
ENTRY_THRESHOLD = 0.0010
SL_PIPS = 100
TP_PIPS = 100
MA_DEVIATION = 5


trades: list[Trade] = []
in_position = False


def is_ma_deviation(price: float, deviation: float, mov_ave: float):
    return deviation < mov_ave - price


def process_row(row: pd.Series) -> None:
    global in_position, trades
    if row["up_D1_50_D1"] and row["up_H1_50_H1"] and not in_position and is_ma_deviation(row["open_H1"], row["MA_Deviation"], row["SMA_H1_50_H1"]):
        trade = Trade(
            open_time=row["timestamp"],
            open_price=row["open_H1"],
            sl=row["close_H1"] - SL_PIPS,
            tp=row["close_H1"] + TP_PIPS
        )
        trades.append(trade)


def main() -> None:
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


if __name__ == "__main__":
    main()
