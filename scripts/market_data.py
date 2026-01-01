import argparse
from pathlib import Path

from core.selection import filter_symbols
from core.merge_timeframes import merge_timeframes
from core.merge_ohlcv import merge_folders
from core.validate_structure import validate_csv_structure


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
    mo.add_argument("input1", type=Path)
    mo.add_argument("input2", type=Path)
    mo.add_argument("--output", type=Path, required=True)

    # -----------------------------
    # Validate CSV structure command
    # -----------------------------
    vs = sub.add_parser("validate-structure")
    vs.add_argument("input", type=Path)

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
        merge_folders(
            folder1=args.input1,
            folder2=args.input2,
            output_base=args.output,
        )

    elif args.command == "validate-structure":
        result = validate_csv_structure(args.input)

        if result["all_same"]:
            print("All CSV files share the same column structure.")
        else:
            print("Column structure mismatch detected.")

        print("\nReference columns:")
        print(", ".join(result["reference"]))

        if result["differences"]:
            print("\nFiles with differences:")
            for path, info in result["differences"].items():
                print(f"\n{path}")
                if info["missing"]:
                    print("  Missing:", ", ".join(sorted(info["missing"])))
                if info["extra"]:
                    print("  Extra:", ", ".join(sorted(info["extra"])))
                if info["order_diff"]:
                    print("  Same columns, different order")

        if result["load_errors"]:
            print("\nFiles that could not be loaded:")
            for path, err in result["load_errors"].items():
                print(f"{path}: {err}")


if __name__ == "__main__":
    main()
