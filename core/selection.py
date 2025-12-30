from pathlib import Path
import shutil


def list_symbols(root: Path) -> list[str]:
    return sorted([
        p.name for p in root.iterdir()
        if p.is_dir()
    ])


def filter_symbols(
    input_root: Path,
    output_root: Path | None,
    symbols: set[str],
    mode: str,  # "keep" | "delete"
):
    """
    mode:
      - keep   -> only symbols in `symbols`
      - delete -> all except `symbols`
    """

    if output_root:
        output_root.mkdir(parents=True, exist_ok=True)

    for sym_dir in input_root.iterdir():
        if not sym_dir.is_dir():
            continue

        match = sym_dir.name in symbols
        should_keep = match if mode == "keep" else not match

        if should_keep:
            if output_root:
                shutil.copytree(sym_dir, output_root / sym_dir.name, dirs_exist_ok=True)
        else:
            if not output_root:
                shutil.rmtree(sym_dir)
