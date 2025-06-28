import os
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="Weekly Momentum Stock Screener", layout="wide")
st.title("📈 Weekly Momentum Stock Screener")

@st.cache_data
def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    tables = pd.read_html(url)
    tickers = tables[0]['Symbol'].tolist()
    return [t.replace('.', '-') for t in tickers]

@st.cache_data
def calculate_momentum(ticker):
    try:
        df = yf.download(ticker, period='1y', interval='1h', progress=False)
        df = df['Close'].dropna()
        if df.empty or len(df) < 24*5:
            return None

        now = df.index[-1]
        def pct_change(period_hours):
            past_index = now - timedelta(hours=period_hours)
            past_data = df[df.index <= past_index]
            if not past_data.empty:
                return (df.iloc[-1] - past_data.iloc[-1]) / past_data.iloc[-1]
            return None

        return {
            'Ticker': ticker,
            '1H': pct_change(1),
            '1W': pct_change(24*7),
            '1M': pct_change(24*30),
            '1Y': pct_change(24*365)
        }
    except:
        return None

@st.cache_data
def generate_momentum_data():
    tickers = get_sp500_tickers()
    results = []
    for i, ticker in enumerate(tickers):
        st.text(f"[{i+1}/{len(tickers)}] Fetching {ticker}...")
        m = calculate_momentum(ticker)
        if m:
            results.append(m)
        time.sleep(0.2)
    df = pd.DataFrame(results).dropna()
    df.sort_values('1W', ascending=False, inplace=True)
    return df

df = generate_momentum_data()

st.markdown("### Top Momentum Stocks This Week (Based on 1-Week Returns)")
st.dataframe(df.sort_values("1W", ascending=False).reset_index(drop=True))

st.markdown("#### Filter by Minimum 1-Month Momentum")
threshold = st.slider("1M Return Threshold (%)", -50, 100, 0)
filtered = df[df["1M"] * 100 > threshold]
st.dataframe(filtered.reset_index(drop=True))
