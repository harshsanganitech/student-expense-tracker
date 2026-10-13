# 💸 Student Expense Tracker (Streamlit + SQLite)

A beginner-friendly web app to track student expenses, set a monthly budget, and view charts.

## Project structure
```
expense_tracker/
├── app.py            # UI (Streamlit pages, forms, charts)
├── database.py       # SQLite: tables, add/edit/delete, queries
├── utils.py          # Categories, Pandas summaries, Plotly charts
├── requirements.txt
├── .streamlit/config.toml   # Theme colours
└── expenses.db       # Created automatically on first run
```

## Setup (step by step)
1. **Install Python 3.9+** from python.org (tick "Add Python to PATH" on Windows).
2. **Open a terminal** in the `expense_tracker` folder.
3. **Create a virtual environment** (recommended):
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv venv` then `source venv/bin/activate`
4. **Install dependencies:** `pip install -r requirements.txt`
5. **Run the app:** `streamlit run app.py`
6. Your browser opens at **http://localhost:8501**. Press `Ctrl+C` in the terminal to stop.

## How to use
- **Sidebar:** pick a date range, filter by category, and set this month's budget.
- **Add Expense:** fill the form and submit.
- **Edit / Delete:** select a transaction, change it, then save or delete.
- **Dashboard:** summary cards, pie chart (categories), bar charts (daily/monthly).
- **Reports & Export:** daily/monthly tables and CSV download.
- **Monthly Savings:** the Dashboard shows Budget, Spent and Savings (Budget − Spent) for any month.
- **Budget alerts:** info (<80%), warning (≥80%), error (>100%).

## Ideas to extend (for your PBL report)
Per-category budgets, user login, recurring expenses, receipt upload, dark mode.

## Troubleshooting
- `streamlit: command not found` → use `python -m streamlit run app.py`.
- Reset all data → stop the app and delete `expenses.db`.
