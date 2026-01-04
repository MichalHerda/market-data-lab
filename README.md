# Market Data Lab

A collection of small projects and experiments for **financial market data analysis** using Python.  
The repository is designed as a personal learning lab and portfolio, covering areas such as:

- Data processing (NumPy, Pandas)  
- Visualization and charting  
- Statistical analysis and indicators  
- Backtesting trading strategies  
- Fetching data from APIs  
- Working with databases  

Each project is organized into thematic categories for clarity.

---

## 🧭 Project Status & Vision

This repository is undergoing an architectural refactor.

The long-term goal is to build a **clean, reusable and extensible data-processing and research pipeline**
for financial market data, with clear separation between:

- core domain logic (pure, reusable Python code)
- execution layers (CLI, pipelines, APIs)
- legacy / exploratory experiments

The current structure reflects both **exploratory research code** and **emerging production-ready components**.
Legacy scripts are being progressively extracted, refactored or archived.



## 📂 Repository Structure 

```
market-data-lab/
├── core/           # (in progress) core domain logic, reusable and headless
├── scripts/        # CLI entry points built on top of core
├── artifacts/      # legacy and exploratory code kept for reference
├── data/           # small sample datasets
├── notebooks/      # exploratory Jupyter notebooks
├── bt/             # experimental backtesting code 
├── fastapi/        # API experiments
└── README.md
```

## Pipeline

```
[MT4 export]
   ↓
[filter symbols]            (optional)
   ↓
[drop timeframes]           (optional, performance)
   ↓
[merge timeframes]
   ↓
[drop incomplete rows]      (multiframe integrity)
   ↓
[slice time range]          (backtest window)
   ↓
[validate structure]
   ↓
[detect duplicates]
   ↓
[resolve duplicates]
   ↓
[drop columns]              (optional, strategy-specific)
   ↓
[rename columns]            (optional)
   ↓
[detect gaps]   ← FINAL DATA QUALITY GATE
   ↓
[feature engineering]

```

---

## ⚙️ Requirements

- Python 3.11+
- Packages from `requirements.txt`

---

## 🚀 Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/MichalHerda/market-data-lab.git
cd market-data-lab
```

# create and activate virtual environment

```
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\Activate      # Windows
```

# install dependencies

```
pip install -r requirements.txt
```

---

## 🛠 DATA PROCESSING CLI

The `scripts/market_data.py` module provides a unified command-line interface
for **data preprocessing, validation and normalization**.

Each command is a thin execution layer built on top of reusable, headless
functions from the `core/` package.  
The CLI is designed to be **pipeline-friendly**, deterministic and explicit.

All commands operate on directory-based datasets containing CSV files
(exported for example from MT4 / MT5).

---

### General Usage

```bash
python3 -m scripts.market_data <command> [arguments]
```

Commands:

## merge-ohlcv

Purpose:
Merge two independent datasets with identical folder structures.

This command is typically used when:

combining historical + recent data

merging data from different sources

patching missing ranges

Files are merged on the time column with forward-fill.

Argumets:

```bash
input1 (Path, required)
First dataset root.

input2 (Path, required)
Second dataset root.

--output (Path, required)
Output directory for merged data.
```

## filter-symbols

Purpose:
Select or exclude specific market symbols (directory-level filtering).

This is typically used when working with large MT4/MT5 exports containing
many instruments, but only a subset is required for further processing.

Arguments:

```bash
input (Path, required)
Root directory containing symbol subdirectories.

--symbols (list[str], required)
List of symbol names (directory names).

--mode (keep | delete, required)

keep → keep only listed symbols

delete → remove listed symbols

--output (Path, required)
Output directory. Original data is never modified.
```

## drop-timeframes

Purpose:
Remove entire timeframe files before merging, reducing memory usage,
I/O overhead and merge complexity.

This step is typically used after symbol selection when certain timeframes
(e.g. M1/M5 noise or W1/MN1 overly coarse data) are not required for a strategy.

Detection is filename-based and non-destructive.

Arguments:

```bash
input (Path, required)
Root directory containing symbol subdirectories.

--timeframes (list[str], required)
Timeframe identifiers to remove (matched as substrings),
e.g. M1 M5 W1 MN1

--output (Path, required)
Output directory for filtered dataset.
```

Example:

```bash
python3 -m scripts.market_data drop-timeframes \
    /home/mh/Desktop/_merged_output \
    --timeframes M1 M5 W1 MN1 \
    --output /home/mh/Desktop/_merged_output_filtered

```

## merge-timeframes

Purpose:
Merge multiple timeframes of the same symbol into a single dataset.

Higher timeframes are forward-filled onto lower timeframes.
Columns are ordered from lowest to highest timeframe:

```
M1 → M5 → M15 → M30 → H1 → H4 → D1 → W1 → MN1
```

Arguments:

```bash
input (Path, required)
Root directory containing CSV files.

--output (Path, optional)
Output directory. If omitted, merged files are written next to input.
```

## drop-incomplete-rows

Purpose:
Remove rows with missing values (NaNs) from all CSV files.

This step is essential for **multi-timeframe strategies**, where
each row must contain a complete set of features across all timeframes.

It is typically applied after timeframe merging and before
backtest window slicing.

The operation is non-destructive — cleaned files are written to a new
output directory.

Arguments:

```bash
input (Path, required)
Root directory containing CSV files.

--output (Path, required)
Output directory for cleaned data.
```

Example: 

```bash
python3 -m scripts.market_data drop-incomplete-rows \
    /home/mh/Desktop/_merged_tf \
    --output /home/mh/Desktop/_merged_tf_complete

```

## slice-time

Purpose:
Restrict datasets to a specific datetime range for backtesting and research.

This step defines the backtest window and should be applied after data
normalization (duplicate resolution, timeframe merge).

The operation is non-destructive — filtered files are written to a new output directory.

Arguments:

```bash
input (Path, required)
Root directory containing CSV files.

--start (str, optional)
Start datetime: YYYY-MM-DD [HH[:MM[:SS]]]

--end (str, optional)
End datetime: YYYY-MM-DD [HH[:MM[:SS]]]

--output (Path, required)
Output directory for sliced data.

```

Example:

```bash
python3 -m scripts.market_data slice-time \
    /home/mh/Desktop/_merged_tf \
    --start 2025-01-01 \
    --end 2025-12-31 \
    --output /home/mh/Desktop/_merged_tf_2025

```

## validate-structure

Purpose:
Validate CSV column consistency across the entire dataset.

The command checks:

missing or extra columns

inconsistent column order

unreadable CSV files

This step is recommended before merging or feature engineering.

Arguments:

```bash
input (Path, required)
Root directory containing CSV files.
```

## detect-duplicates

Purpose:
Detect duplicate timestamps in CSV files.

This command performs read-only diagnostics and optionally generates
a report listing all detected duplicates.

Arguments:

```bash
input (Path, required)
Root directory containing CSV files.

--no-report (flag, optional)
Disable report generation.

--report (Path, optional)
Custom path for the CSV report file.
```

## resolve-duplicates

Purpose:
Resolve duplicate timestamps using a defined strategy.

This command produces a new cleaned dataset and never modifies input data.

Arguments:

```bash
input (Path, required)
Root directory with original CSV files.

--output (Path, required)
Output directory for cleaned files.

--strategy (required)
One of:

keep_first

keep_last

use_reference

--reference (Path, optional)
Required only when using use_reference strategy.
```

## drop-columns

Purpose:
Remove selected columns from all CSV files in the dataset.

This command is typically used after timeframe merging, when
lower-timeframe candles or noisy features (e.g. M1, M5) are no longer
required for strategy logic.

The operation is non-destructive — cleaned files are written to a new
output directory.

Arguments:

```bash
input (Path, required)
Root directory containing CSV files.

--columns (list[str], required)
Names of columns to remove.

--output (Path, required)
Output directory for cleaned data.

```

Example:

```bash
python3 -m scripts.market_data drop-columns \
    /home/mh/Desktop/_merged_tf \
    --columns \
        open_M1 high_M1 low_M1 close_M1 volume_M1 \
        open_M5 high_M5 low_M5 close_M5 volume_M5 \
    --output /home/mh/Desktop/_merged_tf_deleted_M1_M5

```

## rename-columns

Purpose:
Rename specified columns across all CSV files in a dataset.
This is typically used after merging timeframes, standardizing names for strategy logic or feature engineering.

The operation is non-destructive — renamed files are written to a new output directory.

Arguments:

```bash
input (Path, required)
Root directory containing CSV files.

--rename (list[str], required)
Pairs of old_name new_name, e.g.:

open_M15 O_M15 high_M15 H_M15 low_M15 L_M15 close_M15 C_M15 volume_M15 V_M15 \
open_M30 O_M30 high_M30 H_M30 low_M30 L_M30 close_M30 C_M30 volume_M30 V_M30

--output (Path, required)
Output directory for renamed files.

```

Example:

```bash
python3 -m scripts.market_data rename-columns \
    /home/mh/Desktop/_merged_output \
    --rename \
        open_M15 O_M15 high_M15 H_M15 low_M15 L_M15 close_M15 C_M15 volume_M15 V_M15 \
        open_M30 O_M30 high_M30 H_M30 low_M30 L_M30 close_M30 C_M30 volume_M30 V_M30 \
    --output /home/mh/Desktop/renamed

```

## detect-gaps

Purpose:
Detect time discontinuities (gaps) in OHLCV data based on the timestamp column
and the expected interval implied by the timeframe.

This step acts as a final data quality gate before feature engineering
and backtesting.

A gap is detected when the difference between two consecutive timestamps
is greater than the expected timeframe delta, for example:

H1 data: 04:00 → 06:00 → gap detected

M15 data: 10:15 → 10:45 → gap detected

The command does not modify input data.
Instead, it generates diagnostic gap reports for each instrument
and each timeframe.

Arguments:

```bash
input (Path, required)
Root directory containing symbol subdirectories with CSV files.

--output (Path, required)
Output directory for gap report files.

```

Example:

```bash
python3 -m scripts.market_data detect-gaps \
    /home/mh/market-data-lab/merged_output \
    --output /home/mh/market-data-lab/gap_reports

```