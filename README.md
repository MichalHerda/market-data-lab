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


```
## 📂 Repository Structure 

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

# create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\Activate      # Windows

# install dependencies
pip install -r requirements.txt