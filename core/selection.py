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
    mode: str,                              # "keep" | "delete"
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


"""
# Alternative (for readability):


def filter_symbols(
    input_root: Path,
    output_root: Path | None,
    symbols: set[str],
    mode: str,
):
    copy_mode = output_root is not None

    if copy_mode:
        output_root.mkdir(parents=True, exist_ok=True)

    for sym_dir in input_root.iterdir():
        if not sym_dir.is_dir():
            continue

        is_selected = sym_dir.name in symbols

        if mode == "keep":
            should_keep = is_selected
        elif mode == "delete":
            should_keep = not is_selected
        else:
            raise ValueError(f"Unknown mode: {mode}")

        if copy_mode:
            if should_keep:
                shutil.copytree(
                    sym_dir,
                    output_root / sym_dir.name,
                    dirs_exist_ok=True
                )
        else:
            if not should_keep:
                shutil.rmtree(sym_dir)


"""
