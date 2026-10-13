"""
database.py - All SQLite logic lives here (create tables, add/edit/delete, queries).
SQLite stores data in a single file (expenses.db), so data survives app restarts.
"""
import sqlite3
import pandas as pd

DB_PATH = "expenses.db"


def get_conn():
    """Open a connection to the SQLite database file."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """Create tables the first time the app runs."""
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT NOT NULL,      -- stored as YYYY-MM-DD
                category    TEXT NOT NULL,
                description TEXT,
                amount      REAL NOT NULL
            )""")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                month  TEXT PRIMARY KEY,        -- e.g. 2026-10
                amount REAL NOT NULL
            )""")


# ---------- CRUD for expenses ----------
def add_expense(date, category, description, amount):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO expenses (date, category, description, amount) VALUES (?, ?, ?, ?)",
            (str(date), category, description, amount),
        )


def update_expense(expense_id, date, category, description, amount):
    with get_conn() as conn:
        conn.execute(
            "UPDATE expenses SET date=?, category=?, description=?, amount=? WHERE id=?",
            (str(date), category, description, amount, expense_id),
        )


def delete_expense(expense_id):
    with get_conn() as conn:
        conn.execute("DELETE FROM expenses WHERE id=?", (expense_id,))


def get_expenses(start=None, end=None, categories=None):
    """Return expenses as a DataFrame, optionally filtered by date range and categories."""
    query, params = "SELECT * FROM expenses WHERE 1=1", []
    if start:
        query += " AND date >= ?"
        params.append(str(start))
    if end:
        query += " AND date <= ?"
        params.append(str(end))
    if categories:
        query += f" AND category IN ({','.join('?' * len(categories))})"
        params += list(categories)
    query += " ORDER BY date DESC, id DESC"
    with get_conn() as conn:
        return pd.read_sql_query(query, conn, params=params)


# ---------- Budget ----------
def set_budget(month, amount):
    """Insert or replace the budget for a month (format 'YYYY-MM')."""
    with get_conn() as conn:
        conn.execute("INSERT OR REPLACE INTO budgets (month, amount) VALUES (?, ?)", (month, amount))


def get_budget(month):
    with get_conn() as conn:
        row = conn.execute("SELECT amount FROM budgets WHERE month=?", (month,)).fetchone()
    return row[0] if row else 0.0


def get_month_total(month):
    """Total spent in a given month (format 'YYYY-MM')."""
    with get_conn() as conn:
        row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE substr(date, 1, 7)=?", (month,)
        ).fetchone()
    return row[0]


def get_budgets():
    """All saved budgets as a DataFrame with columns: month, budget."""
    with get_conn() as conn:
        return pd.read_sql_query("SELECT month, amount AS budget FROM budgets", conn)
