import os
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
TP_PIPS = 1000


def is_rsi_entry(rsi_val: float, level: float = RSI_ENTRY_LEVEL) -> bool:
    return rsi_val <= level


def calculate_sl(price: float) -> float:
    return price - SL_PIPS


def calculate_tp(price: float) -> float:
    return price + TP_PIPS


def is_sl(price: float, current_sl: float) -> bool:
    return price <= current_sl


def is_tp(price: float, current_tp: float) -> bool:
    return price >= current_tp


def process_file(file_path: str, overwrite: bool, output_folder: str) -> None:
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

    # Normalize column names to lowercase
    df.columns = [c.lower() for c in df.columns]

    # Required columns (in lowercase)
    required_cols = ["timestamp", "open_h1", "close_h1", "rsi_14_close_h1", "up_d1_50_d1"]
    for col in required_cols:
        if col not in df.columns:
            print(f"Missing required column '{col}' in {file_path}. Skipped.")
            return

    # Ensure UP_D1_50_D1 is boolean
    df["up_d1_50_d1"] = df["up_d1_50_d1"].astype(str).str.lower().map({"true": True, "false": False})
    df["up_d1_50_d1"] = df["up_d1_50_d1"].fillna(False)

    # Process rows
    for _, row in df.iterrows():
        price = row["open_h1"]

        if not in_position and is_rsi_entry(row["rsi_14_close_h1"]) and bool(row["up_d1_50_d1"]):
            trade = Trade(
                open_time=row["timestamp"],
                open_price=row["close_h1"],
                sl=calculate_sl(row["close_h1"]),
                tp=calculate_tp(row["close_h1"])
            )
            trades.append(trade)
            current_sl = trade.sl
            current_tp = trade.tp
            in_position = True

        if in_position and trades:
            if is_sl(price, current_sl):
                trades[-1].close_time = row["timestamp"]
                trades[-1].close_price = price
                trades[-1].result = "SL"
                in_position = False
                sl_total += 1
                current_sl = 0
                current_tp = 0

            elif is_tp(price, current_tp):
                trades[-1].close_time = row["timestamp"]
                trades[-1].close_price = price
                trades[-1].result = "TP"
                in_position = False
                tp_total += 1
                current_sl = 0
                current_tp = 0

    # Save trades
    if trades:
        trades_df = pd.DataFrame(trades)
        base_name = os.path.basename(file_path)
        if overwrite:
            signals_path = file_path.replace(".csv", "_signals.csv")
        else:
            os.makedirs(output_folder, exist_ok=True)
            signals_path = os.path.join(output_folder, base_name.replace(".csv", "_signals.csv"))

        trades_df.to_csv(signals_path, index=False)
        print(f"Saved {len(trades)} trades to: {signals_path}")

        # Save summary
        total_trades = sl_total + tp_total
        sl_percent = (sl_total / total_trades * 100) if total_trades > 0 else 0
        tp_percent = (tp_total / total_trades * 100) if total_trades > 0 else 0

        summary_df = pd.DataFrame([{
            "file": base_name,
            "SL_total": sl_total,
            "TP_total": tp_total,
            "SL_percent": round(sl_percent, 2),
            "TP_percent": round(tp_percent, 2)
        }])

        summary_folder = os.path.join(output_folder if not overwrite else os.path.dirname(file_path), "summaries")
        os.makedirs(summary_folder, exist_ok=True)
        summary_path = os.path.join(summary_folder, f"summary_{base_name}")
        summary_df.to_csv(summary_path, index=False)
        print(f"Saved summary to: {summary_path}")
    else:
        print(f"No trades found in {file_path}.")


def main():
    print("RSI Backtest Processor — supports both single files and folders.")
    input_path = fu.get_valid_path("Enter path to CSV file or folder: ")

    # Detect mode
    if os.path.isfile(input_path):
        mode = "file"
    elif os.path.isdir(input_path):
        mode = "folder"
    else:
        print("Invalid path.")
        return

    print("\nWhat would you like to do with results?")
    print(" 1. Overwrite original files")
    print(" 2. Save results to a new folder")
    choice = input("Your choice (1/2): ").strip()

    if choice == "1":
        overwrite = True
        output_folder = None
    else:
        overwrite = False
        output_folder = input("Enter output folder path: ").strip()
        if not output_folder:
            print("No output folder provided. Exiting.")
            return

    if mode == "file":
        process_file(input_path, overwrite, output_folder)
    else:
        for root, _, files in os.walk(input_path):
            for f in files:
                if f.lower().endswith(".csv"):
                    file_path = os.path.join(root, f)
                    process_file(file_path, overwrite, output_folder)


if __name__ == "__main__":
    main()
