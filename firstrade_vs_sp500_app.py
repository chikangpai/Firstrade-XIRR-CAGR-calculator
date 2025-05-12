# firstrade_vs_sp500_app.py
"""
Streamlit UI — Compare your personal brokerage performance against the S&P 500

How to run locally:
    1.  pip install streamlit pandas yfinance scipy
    2.  streamlit run firstrade_vs_sp500_app.py

The app lets you:
    • Upload a Firstrade CSV export (the standard **Trade History** file).
    • Enter your current portfolio market value and valuation date.
    • Instantly see:
        – Total cash invested (sum of outflows)
        – Your portfolio XIRR (cash‑flow IRR)
        – S&P 500 XIRR under identical cash‑flows (buying the index instead)
        – Portfolio CAGR (treating all cash as a lump‑sum on day 0)
        – S&P 500 lump‑sum CAGR
"""
from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
import yfinance as yf
from scipy.optimize import newton

TICKER = "^GSPC"  # S&P 500 index

# ─────────────────────────────────────────────────────────────
# Financial math helpers
# ─────────────────────────────────────────────────────────────

def xnpv(rate: float, cashflows: list[tuple[datetime, float]]) -> float:
    """Net present value of *irregular* cash‑flows at a given annual rate."""
    t0 = cashflows[0][0]
    return float(
        sum(
            cf / (1 + rate) ** ((date - t0).days / 365.0)
            for date, cf in cashflows
        )
    )


def xirr(cashflows: list[tuple[datetime, float]]) -> float:
    """Internal rate of return that makes XNPV==0 (Newton/secant solver)."""
    try:
        return float(newton(lambda r: xnpv(r, cashflows), 0.1))
    except RuntimeError:
        return float("nan")


def download_prices(ticker: str, start: datetime, end: datetime) -> pd.Series:
    """Daily adjusted close prices inclusive of *end* date."""
    data = yf.download(
        ticker,
        start=start.strftime("%Y-%m-%d"),
        end=(end + timedelta(days=1)).strftime("%Y-%m-%d"),
        auto_adjust=True,
        progress=False,
    )
    return data["Close"]


def total_invested(cashflows: list[tuple[datetime, float]]) -> float:
    return float(-sum(cf for _, cf in cashflows if cf < 0))


def lump_cagr(start_val: float, end_val: float, start_date: datetime, end_date: datetime) -> float:
    years = (end_date - start_date).days / 365.0
    return (end_val / start_val) ** (1 / years) - 1 if years else float("nan")


def portfolio_cagr(cashflows: list[tuple[datetime, float]], current_value: float) -> float:
    invested = total_invested(cashflows)
    return lump_cagr(invested, current_value, cashflows[0][0], cashflows[-1][0])


def sp500_cagr_lumpsum(cashflows: list[tuple[datetime, float]]) -> float:
    begin, end = cashflows[0][0], cashflows[-1][0]
    prices = download_prices(TICKER, begin, end)
    start_price = float(prices.iloc[0])  # Convert to float
    end_price = float(prices.iloc[-1])   # Convert to float
    return lump_cagr(start_price, end_price, begin, end)


def sp_xirr_equivalent(cashflows: list[tuple[datetime, float]]) -> float:
    """Build synthetic S&P cash‑flows (buy index instead of each trade) and XIRR."""
    begin, end = cashflows[0][0], cashflows[-1][0]
    prices = download_prices(TICKER, begin, end)

    shares = 0.0
    for date, amt in cashflows[:-1]:  # ignore final valuation
        if amt < 0:
            px = prices[prices.index <= date].iloc[-1]
            shares += (-amt) / px
    final_value = shares * prices.iloc[-1]
    synthetic = cashflows[:-1] + [(end, final_value)]
    return xirr(synthetic)

# ─────────────────────────────────────────────────────────────
# Streamlit UI
# ─────────────────────────────────────────────────────────────

st.set_page_config(page_title="Firstrade vs. S&P 500 Analyzer", layout="centered")
st.title("📈 Firstrade vs S&P 500 Performance")

with st.sidebar:
    st.header("Step 1 – Upload data")
    csv_file = st.file_uploader("Firstrade export (.csv)", type="csv")
    st.markdown(
        "*Tip: In Firstrade, go to **Accounts → Trade History → Export CSV**.*",
        help=None,
    )
    st.header("Step 2 – Current position")
    today = datetime.today().date()
    valuation_date = st.date_input("Valuation date", today)
    portfolio_now = st.number_input(
        "Current total market value ($)",
        min_value=0.0,
        value=0.0,
        step=1000.0,
        format="%0.2f",
    )

# ---- Main panel ----
if csv_file and portfolio_now > 0:
    # Load trades
    trades = pd.read_csv(csv_file)
    trades = trades[trades["RecordType"] == "Trade"].copy()
    trades["TradeDate"] = pd.to_datetime(trades["TradeDate"], errors="coerce")

    # Build cash‐flows list
    cflows: list[tuple[datetime, float]] = list(zip(trades["TradeDate"], trades["Amount"]))
    cflows.sort(key=lambda x: x[0])
    valuation_dt = datetime.combine(valuation_date, datetime.min.time())
    cflows.append((valuation_dt, float(portfolio_now)))

    # Calculations
    invested = total_invested(cflows)
    port_xirr = xirr(cflows)
    sp_xirr = sp_xirr_equivalent(cflows)
    port_cagr = portfolio_cagr(cflows, portfolio_now)
    sp_cagr = sp500_cagr_lumpsum(cflows)

    # Display
    st.subheader("Results")
    col1, col2 = st.columns(2)
    col1.metric("Total cash invested", f"${invested:,.2f}")
    col1.metric("Portfolio XIRR", f"{port_xirr:.2%}")
    col1.metric("Portfolio CAGR (lump‐sum)", f"{port_cagr:.2%}")
    col2.metric("S&P 500 XIRR (same cash‐flows)", f"{sp_xirr:.2%}")
    col2.metric("S&P 500 CAGR (lump‐sum)", f"{sp_cagr:.2%}")

    st.markdown("---")
    with st.expander("Show raw cash‑flows"):
        cf_df = pd.DataFrame(cflows, columns=["Date", "Cash Flow ($)"])
        st.dataframe(cf_df, use_container_width=True)
else:
    st.info("⬅️ Upload your CSV and enter today's portfolio value to see results.")
