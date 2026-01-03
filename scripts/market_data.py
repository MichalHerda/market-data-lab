import argparse
from pathlib import Path

from core.selection import filter_symbols
from core.merge_timeframes import merge_timeframes
from core.merge_ohlcv import merge_folders
from core.validate_structure import validate_csv_structure
from core.detect_duplicates import detect_timestamp_duplicates
from core.resolve_duplicates import resolve_duplicates
from core.drop_columns import drop_columns
from core.rename_columns import rename_columns


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

    # -----------------------------
    # Detect Duplicates
    # -----------------------------
    dd = sub.add_parser("detect-duplicates")
    dd.add_argument("input", type=Path)
    dd.add_argument("--no-report", action="store_true")
    dd.add_argument("--report", type=Path)

    # -----------------------------
    # Apply Duplicates
    # -----------------------------
    ad = sub.add_parser("resolve-duplicates")
    ad.add_argument("input", type=Path)
    ad.add_argument("--output", type=Path, required=True)
    ad.add_argument(
        "--strategy",
        choices=["keep_first", "keep_last", "use_reference"],
        required=True,
    )
    ad.add_argument("--reference", type=Path)

    # -----------------------------
    # Drop columns
    # -----------------------------
    dc = sub.add_parser("drop-columns")
    dc.add_argument("input", type=Path)
    dc.add_argument(
        "--columns",
        nargs="+",
        required=True,
        help="Column names to remove",
    )
    dc.add_argument("--output", type=Path, required=True)

    # -----------------------------
    # Rename columns
    # -----------------------------
    rc = sub.add_parser("rename-columns")
    rc.add_argument("input", type=Path)
    rc.add_argument(
        "--rename",
        nargs="+",
        required=True,
        help="List of old_name new_name pairs, e.g. open_M15 O_M15 high_M15 H_M15 ..."
    )
    rc.add_argument("--output", type=Path, required=True)

    # -----------------------------
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

    elif args.command == "detect-duplicates":
        result = detect_timestamp_duplicates(
            input_root=args.input,
            generate_report=not args.no_report,
            report_path=args.report,
        )

        print(f"Files with duplicate timestamps: {len(result)}")

    elif args.command == "resolve-duplicates":
        resolve_duplicates(
            input_root=args.input,
            output_root=args.output,
            strategy=args.strategy,
            reference_root=args.reference,
        )
    elif args.command == "drop-columns":
        drop_columns(
            input_root=args.input,
            output_root=args.output,
            columns=args.columns,
        )
    elif args.command == "rename-columns":
        pairs = args.rename
        if len(pairs) % 2 != 0:
            raise ValueError("Rename list must contain an even number of arguments: old1 new1 old2 new2 ...")
        rename_map = {pairs[i]: pairs[i+1] for i in range(0, len(pairs), 2)}
        rename_columns(
            input_root=args.input,
            output_root=args.output,
            rename_map=rename_map
        )


if __name__ == "__main__":
    main()
