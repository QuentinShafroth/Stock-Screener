import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import time

def get_sp500_tickers():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    tables = pd.read_html(url)
    tickers = tables[0]['Symbol'].tolist()
    return [t.replace('.', '-') for t in tickers]

def calculate_momentum(ticker):
    try:
        df = yf.download(ticker, period='1y', interval='1h', progress=False)
        df = df['Close'].dropna()
        if df.empty or len(df) < 24*5:
            return None

        now = df.index[-1]
        def pct_change(hours):
            past_index = now - timedelta(hours=hours)
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

tickers = get_sp500_tickers()
results = []
for i, ticker in enumerate(tickers):
    print(f"[{i+1}/{len(tickers)}] Fetching {ticker}...")
    m = calculate_momentum(ticker)
    if m:
        results.append(m)
    time.sleep(0.2)

df = pd.DataFrame(results).dropna()
df.sort_values('1W', ascending=False, inplace=True)
df.to_csv("weekly_momentum.csv", index=False)
print("✅ Saved weekly_momentum.csv with", len(df), "rows")
