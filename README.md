# Finance Tracker

A personal finance tracker built with Python. Import bank CSV statements, automatically categorize transactions, and view monthly income and spending reports through a CLI or a REST API.

## Features

- Import transactions from bank CSV files, with automatic duplicate detection (safe to re-import)
- Rule-based categorization (e.g. `SWIGGY` -> Food, `UBER` -> Transport)
- Monthly reports: income, expenses, net savings, and spending by category
- Command-line interface (Typer) and REST API (FastAPI)
- Exact money handling with `Decimal`, never floats

## Tech stack

Python 3.11, SQLAlchemy 2.0 (SQLite), Typer, FastAPI, pytest

## Setup

```bash
git clone https://github.com/premraaj036-tech/finance-tracker.git
cd finance-tracker
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
```

## Usage

### CLI

```bash
python -m src.finance.cli import-csv data/sample.csv --account "HDFC Savings"
python -m src.finance.cli categorize
python -m src.finance.cli report 2026-10
```

Example output:

```
Report for 2026-10
Income:       75,000.00
Expenses:      3,779.00
Net:          71,221.00

Spending by category:
  Bills             1,800.00  (47.6%)
  Shopping          1,299.00  (34.4%)
  Food                450.00  (11.9%)
  Transport           230.00  (6.1%)
```

### API

```bash
uvicorn src.finance.api:app --reload
```

Open http://127.0.0.1:8000/docs for interactive documentation.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/transactions?limit=50` | Latest transactions |
| POST | `/categorize` | Categorize uncategorized transactions |
| GET | `/report/{year}/{month}` | Monthly report |

## Tests

```bash
python -m pytest -v
```

## Project structure

```
src/finance/
  models.py       # SQLAlchemy models: Account, Category, Transaction
  importer.py     # CSV import with duplicate detection
  categorizer.py  # keyword-rule categorization
  reports.py      # monthly report generation
  cli.py          # Typer command-line interface
  api.py          # FastAPI application
tests/            # pytest suite
data/sample.csv   # fake sample data
```

## Roadmap

- Per-bank CSV parsers (separate debit/credit columns for HDFC, SBI, ICICI)
- User-defined categorization rules stored in the database
- Budget limits with alerts
- Charts and a simple web dashboard
