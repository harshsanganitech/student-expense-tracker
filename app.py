"""
app.py - Main Streamlit app (the user interface).
Run with:  streamlit run app.py
"""
from datetime import date, datetime
import streamlit as st

import database as db
import utils as ut

# ---------- Page setup ----------
st.set_page_config(page_title="Student Expense Tracker", page_icon="💸", layout="wide")
db.init_db()  # make sure tables exist

# Small CSS tweak: turn metrics into rounded "cards"
st.markdown("""
<style>
[data-testid="stMetric"] {
    background: #FFFFFF; padding: 16px 20px; border-radius: 14px;
    box-shadow: 0 2px 10px rgba(108,99,255,0.12); border-left: 5px solid #6C63FF;
}
.block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)


def money(x):
    return f"{ut.CURRENCY}{x:,.2f}"


def flash(msg):
    """Remember a message to show after the page reruns."""
    st.session_state["flash"] = msg


# ---------- Header ----------
st.title("💸 Student Expense Tracker")
st.caption("Track spending, set a monthly budget, and understand where your money goes.")
if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

# ---------- Sidebar: filters + budget ----------
st.sidebar.header("🔎 Filters")
today = date.today()
picked = st.sidebar.date_input("Date range", value=(today.replace(day=1), today))
# date_input returns 1 date while the user is still choosing the second one
start, end = (picked[0], picked[1]) if len(picked) == 2 else (picked[0], picked[0])
cats = st.sidebar.multiselect("Categories", ut.CATEGORIES, default=[])

st.sidebar.header("🎯 Monthly Budget")
this_month = today.strftime("%Y-%m")
# Months we know about: current month + months with expenses or budgets
month_options = sorted(
    {this_month, *db.get_expenses()["date"].str[:7], *db.get_budgets()["month"]}, reverse=True
)
budget_month = st.sidebar.selectbox("Month", month_options)
new_budget = st.sidebar.number_input(
    f"Budget for {budget_month} ({ut.CURRENCY})",
    min_value=0.0, step=500.0, value=float(db.get_budget(budget_month)), key=f"budget_{budget_month}",
)
if st.sidebar.button("Save budget", width="stretch"):
    db.set_budget(budget_month, new_budget)
    flash("Budget saved!")
    st.rerun()

# Data for the selected filters
df = db.get_expenses(start, end, cats)

# ---------- Budget alert (always uses the current month) ----------
budget, spent = db.get_budget(this_month), db.get_month_total(this_month)
if budget > 0:
    used = spent / budget
    if used > 1:
        st.error(f"🚨 Budget exceeded! You spent {money(spent)} of {money(budget)} this month.")
    elif used >= 0.8:
        st.warning(f"⚠️ You've used {used:.0%} of this month's budget ({money(spent)} / {money(budget)}).")
    else:
        st.info(f"✅ On track: {used:.0%} of this month's budget used ({money(spent)} / {money(budget)}).")
    st.progress(min(used, 1.0))
else:
    st.info("Set a monthly budget in the sidebar to get spending alerts.")

# ---------- Tabs ----------
tab_dash, tab_add, tab_manage, tab_reports = st.tabs(
    ["📊 Dashboard", "➕ Add Expense", "✏️ Edit / Delete", "📅 Reports & Export"]
)

# ===== Dashboard =====
with tab_dash:
    # --- Monthly savings: Savings = Budget - Spent ---
    st.markdown("#### 💰 Monthly Savings")
    sel_month = st.selectbox("Choose month", month_options, key="savings_month")
    m_budget, m_spent = db.get_budget(sel_month), db.get_month_total(sel_month)
    s1, s2, s3 = st.columns(3)
    s1.metric("Budget", money(m_budget))
    s2.metric("Spent", money(m_spent))
    if m_budget > 0:
        saved = m_budget - m_spent
        s3.metric("Savings" if saved >= 0 else "Overspent", money(abs(saved)),
                  delta=f"{saved / m_budget:.0%} of budget", delta_color="normal")
    else:
        s3.metric("Savings", "—")
        st.caption("Set a budget for this month in the sidebar to see your savings.")
    st.divider()

    days = max((end - start).days + 1, 1)
    total = ut.category_summary(df)["Total"].sum() if not df.empty else 0
    top_cat = ut.category_summary(df).iloc[0]["Category"] if not df.empty else "—"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Spent", money(total))
    c2.metric("Transactions", len(df))
    c3.metric("Avg / Day", money(total / days))
    c4.metric("Top Category", top_cat)

    if df.empty:
        st.info("No expenses in this range. Add one in the **Add Expense** tab!")
    else:
        left, right = st.columns(2)
        left.plotly_chart(ut.pie_chart(df), width="stretch")
        right.plotly_chart(ut.daily_bar_chart(df), width="stretch")
        st.plotly_chart(ut.monthly_bar_chart(df), width="stretch")
        st.subheader("Recent transactions")
        st.dataframe(df.drop(columns="id").head(10), hide_index=True, width="stretch")

# ===== Add =====
with tab_add:
    st.subheader("Add a new expense")
    with st.form("add_form", clear_on_submit=True):
        a1, a2 = st.columns(2)
        d = a1.date_input("Date", value=today)
        cat = a2.selectbox("Category", ut.CATEGORIES)
        amt = a1.number_input(f"Amount ({ut.CURRENCY})", min_value=0.0, step=10.0)
        desc = a2.text_input("Description (optional)")
        if st.form_submit_button("Add expense", type="primary"):
            if amt <= 0:
                st.error("Amount must be greater than 0.")
            else:
                db.add_expense(d, cat, desc, amt)
                flash("Expense added!")
                st.rerun()

# ===== Edit / Delete =====
with tab_manage:
    st.subheader("Edit or delete a transaction")
    all_df = db.get_expenses()
    if all_df.empty:
        st.info("Nothing to edit yet.")
    else:
        options = {
            f"#{r.id} | {r.date} | {r.category} | {money(r.amount)} | {r.description}": r.id
            for r in all_df.itertuples()
        }
        chosen = st.selectbox("Select a transaction", list(options.keys()))
        row = all_df[all_df["id"] == options[chosen]].iloc[0]

        with st.form(f"edit_form_{row['id']}"):
            e1, e2 = st.columns(2)
            e_date = e1.date_input("Date", value=datetime.strptime(row["date"], "%Y-%m-%d").date())
            e_cat = e2.selectbox("Category", ut.CATEGORIES,
                                 index=ut.CATEGORIES.index(row["category"]) if row["category"] in ut.CATEGORIES else 0)
            e_amt = e1.number_input(f"Amount ({ut.CURRENCY})", min_value=0.0, step=10.0, value=float(row["amount"]))
            e_desc = e2.text_input("Description", value=row["description"] or "")
            b1, b2 = st.columns(2)
            save = b1.form_submit_button("💾 Save changes", type="primary", width="stretch")
            remove = b2.form_submit_button("🗑️ Delete", width="stretch")

        if save:
            if e_amt <= 0:
                st.error("Amount must be greater than 0.")
            else:
                db.update_expense(int(row["id"]), e_date, e_cat, e_desc, e_amt)
                flash("Transaction updated!")
                st.rerun()
        if remove:
            db.delete_expense(int(row["id"]))
            flash("Transaction deleted.")
            st.rerun()

# ===== Reports & Export =====
with tab_reports:
    st.subheader("Summaries (for the selected filters)")
    r1, r2 = st.columns(2)
    r1.markdown("**Daily summary**")
    r1.dataframe(ut.daily_summary(df), hide_index=True, width="stretch")
    r2.markdown("**Monthly summary**")
    r2.dataframe(ut.monthly_summary(df), hide_index=True, width="stretch")

    st.markdown("**Monthly budget & savings (all data, ignores date filter)**")
    st.dataframe(ut.monthly_summary(db.get_expenses(), db.get_budgets()), hide_index=True, width="stretch")

    st.markdown("**All matching transactions**")
    st.dataframe(df, hide_index=True, width="stretch")
    st.download_button(
        "⬇️ Download CSV", data=df.to_csv(index=False).encode("utf-8"),
        file_name=f"expenses_{start}_to_{end}.csv", mime="text/csv", disabled=df.empty,
    )
