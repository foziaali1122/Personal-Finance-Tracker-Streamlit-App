import streamlit as st
import pandas as pd
import os
from datetime import date
import uuid

# ------------ Page config ------------
st.set_page_config(
    page_title="Personal Finance Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------ Custom CSS (Modern, Attractive) ------------
st.markdown(
    """
    <style>
    :root {
      --bg-color: #050816;
      --card-color: rgba(15,23,42,0.85);
      --accent: #38bdf8;
      --accent-soft: rgba(56,189,248,0.18);
      --danger: #fb7185;
      --success: #4ade80;
      --warn: #facc15;
      --text: #e5e7eb;
      --muted: #9ca3af;
    }

    .stApp {
        background: radial-gradient(circle at top, #1e293b 0, #020617 45%, #000 100%);
        color: var(--text);
    }

    .main .block-container{
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1200px;
    }

    .glass-card {
        background: radial-gradient(circle at top left, rgba(56,189,248,0.15), transparent 55%),
                    linear-gradient(145deg, rgba(15,23,42,0.96), rgba(15,23,42,0.9));
        border-radius: 18px;
        padding: 18px 20px;
        box-shadow: 0 18px 45px rgba(15,23,42,0.9);
        border: 1px solid rgba(148,163,184,0.25);
    }

    .metric-card {
        background: radial-gradient(circle at top, rgba(56,189,248,0.2), rgba(15,23,42,0.95));
        border-radius: 16px;
        padding: 14px 16px;
        border: 1px solid rgba(148,163,184,0.4);
        box-shadow: 0 12px 30px rgba(15,23,42,0.9);
    }

    .metric-label {
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--muted);
        margin-bottom: 2px;
    }
    .metric-value {
        font-size: 22px;
        font-weight: 700;
    }
    .metric-sub {
        font-size: 12px;
        color: var(--muted);
    }

    .badge {
        display:inline-flex;
        align-items:center;
        padding:4px 10px;
        border-radius:999px;
        background: rgba(15,23,42,0.8);
        border: 1px solid rgba(148,163,184,0.45);
        margin-right:6px;
        margin-bottom:6px;
        font-size:11px;
        color: var(--muted);
    }
    .badge-dot {
        width:7px;
        height:7px;
        border-radius:999px;
        margin-right:6px;
    }

    .pill {
        display:inline-flex;
        align-items:center;
        padding:4px 12px;
        border-radius:999px;
        background: var(--accent-soft);
        font-size:12px;
        color: var(--accent);
        font-weight:500;
        margin-bottom:6px;
    }

    h1 {
        font-size: 32px !important;
        font-weight: 800 !important;
        letter-spacing: 0.03em;
    }

    .subtitle {
        font-size: 13px;
        color: var(--muted);
        margin-top: -4px;
        margin-bottom: 12px;
    }

    .section-title {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 4px;
    }

    .small {
        font-size:12px;
        color: var(--muted);
    }

    /* Tab styling */
    button[data-baseweb="tab"] {
        font-size:13px;
        padding-top:6px;
        padding-bottom:6px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

DATA_PATH = "transactions.csv"

# ------------ OOP classes ------------
class Transaction:
    def __init__(self, date: str, amount: float, category: str, note: str = ""):
        self.id = str(uuid.uuid4())
        self.date = date
        self.amount = float(amount)
        self.category = category.strip()
        self.note = note.strip()

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "type": self.__class__.__name__,
            "amount": self.amount,
            "category": self.category,
            "note": self.note,
        }

class Income(Transaction):
    pass

class Expense(Transaction):
    pass

class Investment(Transaction):
    pass

# ------------ File handling ------------
def load_data(path=DATA_PATH):
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
        except Exception:
            df = pd.DataFrame(columns=["id", "date", "type", "amount", "category", "note"])
    else:
        df = pd.DataFrame(columns=["id", "date", "type", "amount", "category", "note"])
        df.to_csv(path, index=False)
    return df

def save_data(df, path=DATA_PATH):
    df.to_csv(path, index=False)

df = load_data()

# ------------ Sidebar (transaction list + quick badges) ------------
with st.sidebar:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 💸 Recent Activity")
    if not df.empty:
        temp = df.copy()
        temp["date"] = pd.to_datetime(temp["date"], errors="coerce")
        recent = temp.sort_values("date", ascending=False).head(8)
        for _, row in recent.iterrows():
            d = row["date"]
            try:
                d = d.date()
            except:
                pass
            amt = float(row["amount"])
            emoji = "🟢" if row["type"] == "Income" else "🔴" if row["type"] == "Expense" else "🟣"
            st.markdown(
                f"{emoji} **{row['type']}** · {row['category']}  \n"
                f"<span class='small'>{d} · ₹{amt:.2f}</span>",
                unsafe_allow_html=True,
            )
            if str(row.get("note", "")).strip():
                st.markdown(
                    f"<span class='small'>💬 {row['note']}</span>",
                    unsafe_allow_html=True,
                )
            st.markdown("---")
    else:
        st.info("No transactions yet. Use the form to add.")

    # quick badges
    total_income = df[df["type"] == "Income"]["amount"].sum() if not df.empty else 0.0
    total_expense = df[df["type"] == "Expense"]["amount"].sum() if not df.empty else 0.0
    total_invest = df[df["type"] == "Investment"]["amount"].sum() if not df.empty else 0.0
    net_balance = total_income - total_expense - total_invest

    st.markdown("**Snapshot**")
    st.markdown(
        f"""
        <div class='badge'>
            <div class='badge-dot' style='background:#22c55e;'></div>Income: ₹{total_income:.0f}
        </div>
        <div class='badge'>
            <div class='badge-dot' style='background:#f97316;'></div>Expense: ₹{total_expense:.0f}
        </div>
        <div class='badge'>
            <div class='badge-dot' style='background:#a855f7;'></div>Invest: ₹{total_invest:.0f}
        </div>
        <div class='badge'>
            <div class='badge-dot' style='background:#38bdf8;'></div>Net: ₹{net_balance:.0f}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<p class='small'>Tip: Try to keep net positive and track your biggest expense categories every week.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ------------ Header ------------
st.markdown("<span class='pill'>Personal Finance · Streamlit · Python</span>", unsafe_allow_html=True)
st.markdown("## 💼 Personal Finance Dashboard")
st.markdown("<p class='subtitle'>Track income, expenses & investments with live insights, goals and clean visual analytics.</p>", unsafe_allow_html=True)

# ------------ Top metrics row ------------
col_a, col_b, col_c, col_d = st.columns(4)
if not df.empty:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    total_income = df[df["type"] == "Income"]["amount"].sum()
    total_expense = df[df["type"] == "Expense"]["amount"].sum()
    total_invest = df[df["type"] == "Investment"]["amount"].sum()
    net_balance = total_income - total_expense - total_invest
    savings_pct = (net_balance / total_income * 100) if total_income > 0 else 0
else:
    total_income = total_expense = total_invest = net_balance = savings_pct = 0

with col_a:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("<div class='metric-label'>Total Income</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-value'>₹{total_income:,.0f}</div>", unsafe_allow_html=True)
    st.markdown("<div class='metric-sub'>All recorded income</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_b:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("<div class='metric-label'>Total Expenses</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-value'>₹{total_expense:,.0f}</div>", unsafe_allow_html=True)
    st.markdown("<div class='metric-sub'>Money going out</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_c:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("<div class='metric-label'>Net Balance</div>", unsafe_allow_html=True)
    color = "var(--success)" if net_balance >= 0 else "var(--danger)"
    st.markdown(
        f"<div class='metric-value' style='color:{color}'>₹{net_balance:,.0f}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='metric-sub'>Income − Expenses − Investments</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col_d:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown("<div class='metric-label'>Savings %</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='metric-value'>{savings_pct:,.1f}%</div>", unsafe_allow_html=True)
    st.markdown("<div class='metric-sub'>Share of income saved</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("")  # spacing

# ------------ Tabs for layout ------------
tab1, tab2, tab3 = st.tabs(["➕ Add & Goals", "📊 Analytics", "ℹ️ About Project"])

# ===== TAB 1: ADD TRANSACTION + GOAL =====
with tab1:
    left, right = st.columns([1.1, 1])

    with left:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Add New Transaction</div>", unsafe_allow_html=True)
        st.markdown("<p class='small'>Record income, expenses or investments with category & optional note.</p>", unsafe_allow_html=True)

        with st.form("tx_form", clear_on_submit=True):
            t_type = st.selectbox("Type", ["Income", "Expense", "Investment"])
            t_date = st.date_input("Date", value=date.today())
            t_amount = st.number_input("Amount (PKR)", min_value=0.0, format="%.2f")
            t_category = st.text_input("Category (e.g., Salary, Groceries, Rent, Stocks)")
            t_note = st.text_area("Note (optional)", height=70)
            submitted = st.form_submit_button("Save Transaction")

            if submitted:
                errors = []
                if t_amount <= 0:
                    errors.append("Amount must be greater than zero.")
                if not t_category.strip():
                    errors.append("Category is required.")

                if errors:
                    for e in errors:
                        st.error(e)
                else:
                    if t_type == "Income":
                        tx = Income(t_date.isoformat(), t_amount, t_category, t_note)
                    elif t_type == "Expense":
                        tx = Expense(t_date.isoformat(), t_amount, t_category, t_note)
                    else:
                        tx = Investment(t_date.isoformat(), t_amount, t_category, t_note)

                    new_row = pd.DataFrame([tx.to_dict()])
                    df = pd.concat([df, new_row], ignore_index=True)
                    save_data(df)
                    st.success(f"{t_type} added: ₹{t_amount:.2f} — {t_category}")

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>Savings Goal</div>", unsafe_allow_html=True)
        st.markdown("<p class='small'>Set a monthly savings target as a percentage of your income.</p>", unsafe_allow_html=True)

        goal_pct = st.slider(
            "Monthly savings goal (% of income)",
            min_value=0,
            max_value=100,
            value=20,
            step=1,
        )

        if total_income <= 0:
            st.warning("Add at least one income transaction to evaluate your goal.")
        else:
            st.markdown("---")
            st.markdown("**Goal Evaluation**")
            # Nested conditionals
            if savings_pct >= goal_pct:
                if savings_pct >= goal_pct + 10:
                    st.success(
                        f"🔥 Excellent! You're exceeding your savings goal "
                        f"({savings_pct:.1f}% vs {goal_pct}%). Keep this momentum!"
                    )
                else:
                    st.success(
                        f"✅ Good job! You've met your savings goal "
                        f"({savings_pct:.1f}% vs {goal_pct}%). Try to build a small buffer."
                    )
            else:
                if savings_pct >= goal_pct * 0.8:
                    st.warning(
                        f"⚠️ Almost there. You're saving {savings_pct:.1f}% vs goal {goal_pct}%. "
                        f"Small cuts in expenses can help you reach your goal."
                    )
                else:
                    st.error(
                        f"❌ Below target. Saving {savings_pct:.1f}% vs goal {goal_pct}%. "
                        f"Consider reducing big expenses or increasing income."
                    )

        st.markdown("</div>", unsafe_allow_html=True)

# ===== TAB 2: ANALYTICS & INSIGHTS =====
with tab2:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Analytics & Insights</div>", unsafe_allow_html=True)
    if df.empty:
        st.info("No data yet. Add some transactions first.")
    else:
        # Expense category totals (dictionary)
        exp_cats = (
            df[df["type"] == "Expense"]
            .groupby("category")["amount"]
            .sum()
            .to_dict()
        )
        st.markdown("**Expense category totals (dictionary):**")
        st.write(exp_cats)

        # Highest spending category
        if exp_cats:
            highest_cat = max(exp_cats, key=exp_cats.get)
            st.markdown(
                f"**Highest spending category:** 🧾 {highest_cat} "
                f"(₹{exp_cats[highest_cat]:.2f})"
            )
        else:
            st.write("No expense categories yet.")

        # Most frequent category (all types)
        if not df["category"].mode().empty:
            most_freq = df["category"].mode().iloc[0]
            st.markdown(f"**Most frequent category:** 📌 {most_freq}")
        else:
            st.write("No categories yet.")

        # Unique categories set + string analysis
        unique_cats = set(df["category"].astype(str).str.strip().unique())
        st.markdown(f"**Unique categories ({len(unique_cats)}):** {unique_cats}")

        joined = " | ".join(sorted(unique_cats))
        joined_upper = joined.upper()
        count_a = joined_upper.count("A")
        st.markdown("**Categories (joined & uppercased):**")
        st.code(joined_upper)
        st.markdown(f"Letter **'A'** appears **{count_a}** times in this string.")

        st.markdown("---")
        st.markdown("#### 📊 Expenses by Category")

        if exp_cats:
            exp_df = (
                pd.DataFrame(list(exp_cats.items()), columns=["category", "amount"])
                .sort_values("amount", ascending=False)
            )
            st.bar_chart(exp_df.set_index("category")["amount"])
        else:
            st.info("No expense data available to visualize.")

        st.markdown("---")
        st.markdown("#### 📋 All Transactions")
        show_df = df.sort_values("date", ascending=False).reset_index(drop=True)
        st.dataframe(show_df, use_container_width=True)

        csv = show_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download transactions as CSV",
            data=csv,
            file_name="transactions_export.csv",
            mime="text/csv",
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ===== TAB 3: ABOUT / README STYLE =====
with tab3:
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("### 📚 About This Project")
    st.markdown(
        """
        **Personal Finance Tracking Application** built with:
        - Python 3.11  
        - Streamlit (for UI)  
        - Pandas (for data & calculations)  
        - File handling with CSV for persistent storage  

        **Covers Assignment Requirements:**
        - ✅ OOP: `Transaction` base class, `Income`, `Expense`, `Investment` subclasses  
        - ✅ File handling: Save & load `transactions.csv`  
        - ✅ Calculations: totals, net balance, savings percentage  
        - ✅ Goal evaluation with **nested if-else** logic  
        - ✅ Analytics: highest spending category, most frequent category, unique categories set, dictionary totals  
        - ✅ String processing: join categories, uppercase, count 'A'  
        - ✅ Streamlit UI: form, statistics, insights, bar chart, downloadable CSV  

        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

