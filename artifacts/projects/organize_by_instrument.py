import os
import shutil
import libs.file_utils as fu


def extract_instrument_and_tf(filename: str):
    """
    Extract instrument and timeframe from filename.
    Example:
      'EURUSD_M1.csv' -> ('EURUSD', 'M1')
      '[SP500]_H4.csv' -> ('[SP500]', 'H4')
      'I.EURX_M30.csv' -> ('I.EURX', 'M30')
    """
    name = filename.replace(".csv", "")
    if "_" not in name:
        return None, None

    instrument, timeframe = name.rsplit("_", 1)
    return instrument, timeframe


def main():
    print("Instrument Folder Organizer")

    input_dir = fu.get_valid_path("Enter path to folder containing CSV files: ")

    output_dir = input("Enter output base directory (will be created if needed): ").strip()
    os.makedirs(output_dir, exist_ok=True)

    files = [f for f in os.listdir(input_dir) if f.lower().endswith(".csv")]

    if not files:
        print("No CSV files found. Exiting.")
        return

    for filename in files:
        instrument, timeframe = extract_instrument_and_tf(filename)
        if instrument is None:
            print(f"Skipping file (could not parse): {filename}")
            continue

        source_path = os.path.join(input_dir, filename)
        target_folder = os.path.join(output_dir, instrument)
        os.makedirs(target_folder, exist_ok=True)

        target_path = os.path.join(target_folder, filename)

        shutil.move(source_path, target_path)
        print(f"Moved {filename} → {target_folder}")

    print("\nDone.")


if __name__ == "__main__":
    main()
