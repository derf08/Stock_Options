# ======================================================
# Dependency expectations (Option A)
# Requires requirements.txt with:
# streamlit
# yfinance
# pandas
# numpy
# ======================================================

import streamlit as st

# --- Dependency Guard ---
try:
    import yfinance as yf
except ModuleNotFoundError:
    st.error(
        "❌ Missing dependency: **yfinance**\n\n"
        "This app requires `yfinance`.\n\n"
        "If deploying, ensure it is listed in **requirements.txt**:\n"
        "`yfinance`"
    )
    st.stop()

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# App Header
st.set_page_config(page_title="Stock 40% Target Scanner", layout="wide")
st.title("🚀 1-Week Opportunity Scanner")
st.subheader("Targeting 40% Gains via High Volatility")

# List of high-growth/volatile tickers to monitor
WATCHLIST = ['PLTR', 'NVDA', 'TSLA', 'IREN', 'SOC', 'APLD', 'SOXL', 'MARA', 'MST]()

