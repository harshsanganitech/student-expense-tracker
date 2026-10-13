"""
utils.py - Helper functions: categories, summaries (Pandas) and charts (Plotly).
"""
import pandas as pd
import plotly.express as px

CURRENCY = "₹"
CATEGORIES = [
    "Food", "Transport", "Books & Stationery", "Rent & Hostel",
    "Entertainment", "Health", "Shopping", "Internet & Recharge", "Other",
]
COLORS = px.colors.qualitative.Pastel


# ---------- Summaries ----------
def daily_summary(df):
    """Total spent per day."""
    if df.empty:
        return pd.DataFrame(columns=["Date", "Total"])
    out = df.groupby("date", as_index=False)["amount"].sum()
    out.columns = ["Date", "Total"]
    return out.sort_values("Date", ascending=False)


def monthly_summary(df, budgets=None):
    """Total spent per month. If a budgets DataFrame is given, also adds
    Budget and Savings (= Budget - Total) columns."""
    if df.empty:
        return pd.DataFrame(columns=["Month", "Total", "Transactions"])
    tmp = df.assign(Month=df["date"].str[:7])
    out = tmp.groupby("Month").agg(Total=("amount", "sum"), Transactions=("id", "count")).reset_index()
    if budgets is not None:
        out = out.merge(budgets.rename(columns={"month": "Month", "budget": "Budget"}), on="Month", how="left")
        out["Savings"] = out["Budget"] - out["Total"]  # empty if no budget was set
    return out.sort_values("Month", ascending=False)


def category_summary(df):
    """Total spent per category."""
    if df.empty:
        return pd.DataFrame(columns=["Category", "Total"])
    out = df.groupby("category", as_index=False)["amount"].sum()
    out.columns = ["Category", "Total"]
    return out.sort_values("Total", ascending=False)


# ---------- Charts ----------
def _style(fig):
    """Common look for all charts."""
    fig.update_layout(
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", y=-0.15),
    )
    return fig


def pie_chart(df):
    data = category_summary(df)
    fig = px.pie(data, names="Category", values="Total", hole=0.45,
                 title="Spending by Category", color_discrete_sequence=COLORS)
    fig.update_traces(textinfo="percent+label")
    return _style(fig)


def daily_bar_chart(df):
    data = daily_summary(df).sort_values("Date")
    fig = px.bar(data, x="Date", y="Total", title="Daily Spending",
                 color_discrete_sequence=["#6C63FF"])
    return _style(fig)


def monthly_bar_chart(df):
    data = monthly_summary(df).sort_values("Month")
    fig = px.bar(data, x="Month", y="Total", title="Monthly Spending",
                 color_discrete_sequence=["#FF8C69"], text_auto=".0f")
    return _style(fig)
