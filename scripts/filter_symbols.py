import argparse
from pathlib import Path
from core.selection import filter_symbols


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--symbols", nargs="+", required=True)
    parser.add_argument("--mode", choices=["keep", "delete"], required=True)
    parser.add_argument("--output", type=Path)

    args = parser.parse_args()

    filter_symbols(
        input_root=args.input,
        output_root=args.output,
        symbols=set(args.symbols),
        mode=args.mode
    )


if __name__ == "__main__":
    main()
