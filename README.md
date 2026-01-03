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
[filter symbols]        (optional)
   ↓
[data cleaning]         (ENTRY POINT pipeline)
   ↓
[merge timeframes]      (HTF → LTF forward-fill)
   ↓
[feature engineering]   (RSI, MA, etc. )
   ↓
[validation / bt / ML]

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
python -m scripts.market_data <command> [arguments]
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

# Arguments:

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

## apply-duplicates

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