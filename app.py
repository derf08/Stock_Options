import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta

# App Header
st.set_page_config(page_title="Stock 40% Target Scanner", layout="wide")
st.title("🚀 1-Week Opportunity Scanner")
st.subheader("Targeting 40% Gains via High Volatility")

# List of high-growth/volatile tickers to monitor
WATCHLIST = ['PLTR', 'NVDA', 'TSLA', 'IREN', 'SOC', 'APLD', 'SOXL', 'MARA', 'MSTR']

def get_trading_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        if hist.empty: return None
        
        current_price = hist['Close'].iloc[-1]
        # Calculate 7-day volatility (annualized)
        returns = np.log(hist['Close'] / hist['Close'].shift(1))
        volatility = returns.std() * np.sqrt(252)
        
        # Expected Move formula: Price * IV * sqrt(Days/365)
        expected_move_7d = current_price * volatility * np.sqrt(7 / 365)
        
        return {
            "Ticker": ticker,
            "Price": round(current_price, 2),
            "7D Volatility": f"{round(volatility * 100, 2)}%",
            "Expected Move ($)": round(expected_move_7d, 2),
            "Target Price (+40% Option Move)": round(current_price + (expected_move_7d * 1.5), 2),
            "Hold Time": "5-7 Days"
        }
    except:
        return None

# Sidebar for controls
if st.button('Run Daily Scan'):
    results = []
    with st.spinner('Scanning market data...'):
        for t in WATCHLIST:
            data = get_trading_data(t)
            if data: results.append(data)
    
    df = pd.DataFrame(results)
    
    # Highlight high-potential stocks
    st.table(df)
    
    st.success("Scan Complete. Focus on Tickers with Volatility > 80% for 40% gain potential.")
else:
    st.info("Click the button above to analyze the current watchlist.")

st.markdown("---")
st.caption("Strategy based on your 'Options and Trading' folder: Focusing on Writing Naked Puts for entry and High-IV Calls for exit.")
