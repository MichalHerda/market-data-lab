# projects/find_missing_timestamps.py

import os
import re
import pandas as pd
import libs.file_utils as fu
import libs.csv_utils as cu


TIMEFRAMES = ["MN1", "W1", "D1", "H4", "H1", "M30", "M15", "M5", "M1"]


def gather_csv_files(path: str):
    """Return list of CSV file paths from file or recursive directory."""
    if os.path.isfile(path) and path.lower().endswith(".csv"):
        return [path]

    csv_files = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.lower().endswith(".csv"):
                csv_files.append(os.path.join(root, f))
    return csv_files


def extract_timeframe(filename: str):
    """Try to find a known timeframe token anywhere in filename (case-insensitive)."""
    for tf in TIMEFRAMES:
        if re.search(re.escape(tf), filename, re.IGNORECASE):
            return tf
    return None


def normalize_instrument_name(filename: str, timeframe: str | None):
    """
    Return instrument name extracted from filename without the timeframe suffix.
    Examples:
      'EURUSD_H1.csv' -> 'EURUSD'
      '[SP500]_H1.csv' -> '[SP500]'
      'USDJPY-H4.csv' -> 'USDJPY'
    If timeframe not found, return base name (without extension).
    """
    base = os.path.splitext(os.path.basename(filename))[0]
    if timeframe:
        # remove trailing _TF or -TF or TF (if last token)
        pattern = re.compile(rf'[_\-]?(?:{re.escape(timeframe)})$', re.IGNORECASE)
        base = pattern.sub('', base).strip()
    return base


def analyze_file(file_path: str):
    """Return (first_timestamp_min, missing_count) or (None, None) on error / no timestamp column."""
    try:
        df = cu.load_csv(file_path, sep=";")
    except Exception as e:
        # Could not load — skip
        return None, None

    if "timestamp" not in df.columns:
        return None, None

    # Convert timestamp column to datetime if possible (non-destructive)
    try:
        ts = pd.to_datetime(df["timestamp"], errors="coerce")
    except Exception:
        ts = df["timestamp"]

    missing_count = ts.isna().sum()
    # earliest non-null timestamp (or "N/A" if none)
    if ts.notna().any():
        first_timestamp = ts[ts.notna()].min()
    else:
        first_timestamp = "N/A"

    return first_timestamp, int(missing_count)


def main():
    print("Missing Timestamp Overview Generator")

    input_path = fu.get_valid_path("Enter path to CSV file or folder: ")

    csv_files = gather_csv_files(input_path)
    if not csv_files:
        print("No CSV files found. Nothing to process.")
        return

    output_dir = input("Enter output directory for summary file: ").strip()
    # always create output dir (even if not existing)
    os.makedirs(output_dir, exist_ok=True)

    # summary dict keyed by instrument name
    summary = {}

    for file_path in sorted(csv_files):
        filename = os.path.basename(file_path)
        tf = extract_timeframe(filename)
        if tf is None:
            # skip files where timeframe cannot be determined (intentional decision)
            continue

        instrument = normalize_instrument_name(filename, tf)
        first_ts, missing = analyze_file(file_path)
        if missing is None:
            continue

        if instrument not in summary:
            # initialize row
            summary[instrument] = {"timestamp": first_ts}
            for t in TIMEFRAMES:
                summary[instrument][f"missing_{t}"] = 0

        # store missing count for this timeframe
        summary[instrument][f"missing_{tf}"] = missing

        # update earliest timestamp if we found an earlier one
        current_ts = summary[instrument]["timestamp"]
        # only compare datetimes when both are datetimes
        try:
            if current_ts != "N/A" and first_ts != "N/A":
                # normalize to pandas Timestamp for comparison
                cur = pd.to_datetime(current_ts)
                new = pd.to_datetime(first_ts)
                if new < cur:
                    summary[instrument]["timestamp"] = new
            elif current_ts == "N/A" and first_ts != "N/A":
                summary[instrument]["timestamp"] = first_ts
        except Exception:
            # keep existing if comparison fails
            pass

    if not summary:
        print("No valid data found. Exiting.")
        return

    # Build DataFrame in desired column order
    cols = ["instrument", "timestamp"] + [f"missing_{t}" for t in TIMEFRAMES]
    result_df = pd.DataFrame.from_dict(summary, orient="index").reset_index()
    result_df.rename(columns={"index": "instrument"}, inplace=True)
    # ensure timestamp column formatting: convert Timestamp -> ISO string

    def fmt_ts(x):
        if pd.isna(x) or x == "N/A":
            return "N/A"
        try:
            return pd.to_datetime(x).isoformat(sep=' ')
        except Exception:
            return str(x)

    result_df["timestamp"] = result_df["timestamp"].apply(fmt_ts)

    # reindex columns to exact order (if any missing, they'll be created)
    for c in cols:
        if c not in result_df.columns:
            result_df[c] = ""
    result_df = result_df[cols]

    save_path = os.path.join(output_dir, "missing_overview.csv")
    cu.save_csv(result_df, save_path, sep=";")

    print(f"\nSummary saved to: {save_path}")
    print("Done.")


if __name__ == "__main__":
    main()
