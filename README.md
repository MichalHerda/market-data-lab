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

## 📂 Repository Structure

market-data-lab/
├── data/ # sample CSV files (small-sized only)
├── notebooks/ # Jupyter notebooks with analysis
├── projects/ # categorized subprojects
│ ├── api/
│ │ ├── fetch_yfinance/
│ │ └── fetch_mt4/
│ ├── backtest/
│ │ ├── sma_backtest/
│ │ └── breakout_strategy/
│ └── csv_edition/
│ ├── moving_averages/
│ └── normalize_prices/
├── requirements.txt
└── README.md

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