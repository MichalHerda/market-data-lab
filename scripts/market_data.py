import argparse
from pathlib import Path

from core.selection import filter_symbols
from core.merge_timeframes import merge_timeframes


def main():
    parser = argparse.ArgumentParser("market_data")
    sub = parser.add_subparsers(dest="command", required=True)

    fs = sub.add_parser("filter-symbols")
    fs.add_argument("input", type=Path)
    fs.add_argument("--symbols", nargs="+", required=True)
    fs.add_argument("--mode", choices=["keep", "delete"], required=True)
    fs.add_argument("--output", type=Path, required=True)

    mt = sub.add_parser("merge-timeframes")
    mt.add_argument("input", type=Path)
    mt.add_argument("--output", type=Path)

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


if __name__ == "__main__":
    main()
