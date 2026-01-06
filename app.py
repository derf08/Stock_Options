import yfinance as yf
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
import time

# Mobile-optimized configuration
st.set_page_config(
    page_title="Stock Scanner",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"  # Better for mobile
)

# Custom CSS for mobile responsiveness
st.markdown("""
    <style>
    /* Mobile-first responsive design */
    .stButton>button {
        width: 100%;
        height: 3rem;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    /* Improve table readability on mobile */
    table {
        font-size: 0.9rem;
    }
    @media (max-width: 640px) {
        .block-container {
            padding: 1rem 0.5rem;
        }
        h1 {
            font-size: 1.5rem !important;
        }
        h3 {
            font-size: 1.1rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# App Header
st.title("🚀 1-Week Opportunity Scanner")
st.markdown("**Targeting 40% Gains via High Volatility**")

# Watchlist with ability to customize
DEFAULT_WATCHLIST = ['PLTR', 'NVDA', 'TSLA', 'IREN', 'SOC', 'APLD', 'SOXL', 'MARA', 'MSTR']

# Expandable settings section
with st.expander("⚙️ Scanner Settings", expanded=False):
    watchlist_input = st.text_input(
        "Customize Watchlist (comma-separated)",
        value=", ".join(DEFAULT_WATCHLIST),
        help="Enter stock tickers separated by commas"
    )
    WATCHLIST = [t.strip().upper() for t in watchlist_input.split(',') if t.strip()]
    
    volatility_threshold = st.slider(
        "Minimum Volatility Threshold (%)",
        min_value=50,
        max_value=150,
        value=80,
        step=10,
        help="Highlight stocks with volatility above this threshold"
    )

@st.cache_data(ttl=300)  # Cache for 5 minutes to reduce API calls
def get_trading_data(ticker):
    """Fetch and calculate trading metrics for a given ticker"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        
        if hist.empty or len(hist) < 7:
            return None
        
        current_price = hist['Close'].iloc[-1]
        prev_close = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
        
        # Calculate daily change
        daily_change = ((current_price - prev_close) / prev_close) * 100
        
        # Calculate 7-day volatility (annualized)
        returns = np.log(hist['Close'] / hist['Close'].shift(1))
        volatility = returns.std() * np.sqrt(252)
        
        # Expected Move formula: Price * IV * sqrt(Days/365)
        expected_move_7d = current_price * volatility * np.sqrt(7 / 365)
        
        # Calculate target price (conservative and aggressive)
        conservative_target = current_price + expected_move_7d
        aggressive_target = current_price + (expected_move_7d * 1.5)
        
        # Calculate potential gain percentages
        conservative_gain = ((conservative_target - current_price) / current_price) * 100
        aggressive_gain = ((aggressive_target - current_price) / current_price) * 100
        
        return {
            "Ticker": ticker,
            "Price": current_price,
            "Daily %": daily_change,
            "7D Vol (%)": volatility * 100,
            "Expected Move": expected_move_7d,
            "Conservative Target": conservative_target,
            "Conservative Gain (%)": conservative_gain,
            "Aggressive Target": aggressive_target,
            "Aggressive Gain (%)": aggressive_gain,
            "Hold Time": "5-7 Days"
        }
    except Exception as e:
        st.warning(f"⚠️ Could not fetch data for {ticker}: {str(e)}")
        return None

def format_dataframe(df):
    """Format dataframe for display with proper styling"""
    display_df = df.copy()
    
    # Format numeric columns
    display_df['Price'] = display_df['Price'].apply(lambda x: f"${x:.2f}")
    display_df['Daily %'] = display_df['Daily %'].apply(lambda x: f"{x:+.2f}%")
    display_df['7D Vol (%)'] = display_df['7D Vol (%)'].apply(lambda x: f"{x:.1f}%")
    display_df['Expected Move'] = display_df['Expected Move'].apply(lambda x: f"${x:.2f}")
    display_df['Conservative Target'] = display_df['Conservative Target'].apply(lambda x: f"${x:.2f}")
    display_df['Conservative Gain (%)'] = display_df['Conservative Gain (%)'].apply(lambda x: f"{x:.1f}%")
    display_df['Aggressive Target'] = display_df['Aggressive Target'].apply(lambda x: f"${x:.2f}")
    display_df['Aggressive Gain (%)'] = display_df['Aggressive Gain (%)'].apply(lambda x: f"{x:.1f}%")
    
    return display_df

# Main scan button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    scan_button = st.button('🔍 Run Daily Scan', use_container_width=True, type="primary")

if scan_button:
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, ticker in enumerate(WATCHLIST):
        status_text.text(f"Scanning {ticker}... ({idx + 1}/{len(WATCHLIST)})")
        data = get_trading_data(ticker)
        if data:
            results.append(data)
        progress_bar.progress((idx + 1) / len(WATCHLIST))
        time.sleep(0.1)  # Small delay to avoid rate limiting
    
    progress_bar.empty()
    status_text.empty()
    
    if results:
        df = pd.DataFrame(results)
        
        # Sort by volatility (highest first)
        df = df.sort_values('7D Vol (%)', ascending=False)
        
        # Display summary metrics
        st.markdown("### 📊 Scan Summary")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Stocks Scanned", len(results))
        with col2:
            high_vol_count = len(df[df['7D Vol (%)'] > volatility_threshold])
            st.metric("High Volatility", high_vol_count, 
                     delta=f">{volatility_threshold}%")
        with col3:
            avg_vol = df['7D Vol (%)'].mean()
            st.metric("Avg Volatility", f"{avg_vol:.1f}%")
        
        st.markdown("---")
        
        # Display high-potential stocks
        high_potential = df[df['7D Vol (%)'] > volatility_threshold]
        
        if not high_potential.empty:
            st.markdown(f"### 🎯 High-Potential Stocks (Vol > {volatility_threshold}%)")
            st.dataframe(
                format_dataframe(high_potential),
                use_container_width=True,
                hide_index=True
            )
        
        # Display all stocks
        st.markdown("### 📈 All Scanned Stocks")
        st.dataframe(
            format_dataframe(df),
            use_container_width=True,
            hide_index=True
        )
        
        # Trading recommendations
        st.markdown("---")
        st.markdown("### 💡 Trading Strategy")
        st.info("""
        **Entry Strategy:** Write Naked Puts on high-volatility stocks at support levels
        
        **Exit Strategy:** Buy High-IV Calls when momentum confirms uptrend
        
        **Risk Management:** 
        - Focus on stocks with Vol > 80% for maximum 40% gain potential
        - Hold time: 5-7 days
        - Set stop-loss at 20% below entry
        """)
        
        # Download option
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name=f"stock_scan_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.success(f"✅ Scan Complete! Found {len(high_potential)} high-potential opportunities.")
        
    else:
        st.error("❌ No data retrieved. Please check your internet connection and try again.")

else:
    st.info("👆 Click the button above to analyze the current watchlist.")
    
    # Show watchlist preview
    with st.container():
        st.markdown("### 📋 Current Watchlist")
        cols = st.columns(min(len(WATCHLIST), 3))
        for idx, ticker in enumerate(WATCHLIST):
            with cols[idx % 3]:
                st.markdown(f"**{ticker}**")

# Footer
st.markdown("---")
st.caption(f"""
📱 **Mobile & Web Optimized** | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Strategy: Writing Naked Puts for entry + High-IV Calls for exit
""")
