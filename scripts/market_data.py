import argparse
from pathlib import Path

from core.selection import filter_symbols
from core.merge_timeframes import merge_timeframes
from core.merge_ohlcv import merge_folders  # <-- new import for OHLCV merge


def main():
    parser = argparse.ArgumentParser("market_data")
    sub = parser.add_subparsers(dest="command", required=True)

    # -----------------------------
    # Filter symbols command
    # -----------------------------
    fs = sub.add_parser("filter-symbols")
    fs.add_argument("input", type=Path)
    fs.add_argument("--symbols", nargs="+", required=True)
    fs.add_argument("--mode", choices=["keep", "delete"], required=True)
    fs.add_argument("--output", type=Path, required=True)

    # -----------------------------
    # Merge timeframes command
    # -----------------------------
    mt = sub.add_parser("merge-timeframes")
    mt.add_argument("input", type=Path)
    mt.add_argument("--output", type=Path)

    # -----------------------------
    # Merge OHLCV command (two folders)
    # -----------------------------
    mo = sub.add_parser("merge-ohlcv")
    mo.add_argument("input1", type=Path, help="Path to the first folder")
    mo.add_argument("input2", type=Path, help="Path to the second folder")
    mo.add_argument("--output", type=Path, required=True, help="Output folder for merged CSVs")

    args = parser.parse_args()

    if args.command == "filter-symbols":
        filter_symbols(
            input_root=args.input,
            output_root=args.output,
            symbols=set(args.symbols),
            mode=args.mode,
        )

    elif args.command == "merge-timeframes":
        merge_timeframes(
            input_root=args.input,
            output_root=args.output,
        )

    elif args.command == "merge-ohlcv":
        # Merge CSVs from exactly two folders
        merge_folders(
            folder1=args.input1,
            folder2=args.input2,
            output_base=args.output,
        )


if __name__ == "__main__":
    main()
