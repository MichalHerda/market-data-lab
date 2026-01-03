from pathlib import Path
import pandas as pd


def resolve_duplicates(
    input_root: Path,
    output_root: Path,
    *,
    strategy: str,                                          # strategies: first, last, use_reference
    reference_root: Path | None = None,
    timestamp_col: str = "timestamp",
):
    """
    Apply a duplicates resolution strategy to CSV files.
    """
    if strategy == "use_reference" and reference_root is None:
        raise ValueError("reference_root is required for use_reference strategy")

    for path in input_root.rglob("*.csv"):
        df = pd.read_csv(path, sep=";")

        if timestamp_col not in df.columns:
            continue

        if strategy == "keep_first":
            df = df.drop_duplicates(subset=timestamp_col, keep="first")

        elif strategy == "keep_last":
            df = df.drop_duplicates(subset=timestamp_col, keep="last")

        elif strategy == "use_reference":
            rel = path.relative_to(input_root)
            ref_path = reference_root / rel
            if not ref_path.exists():
                continue

            ref = pd.read_csv(ref_path, sep=";")
            if timestamp_col not in ref.columns:
                continue

            df = (
                df.drop_duplicates(subset=timestamp_col, keep="first")
                .set_index(timestamp_col)
            )
            ref = ref.set_index(timestamp_col)
            df.update(ref)
            df = df.reset_index()

        out_path = output_root / path.relative_to(input_root)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(out_path, sep=";", index=False)
