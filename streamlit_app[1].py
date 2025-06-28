import os
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Weekly Momentum Stock Screener", layout="wide")
st.title("📈 Weekly Momentum Stock Screener")

@st.cache_data
def load_data():
    file_path = "weekly_momentum.csv"
    if not os.path.exists(file_path):
        st.error(f"❌ File '{file_path}' not found. Please run the data download script first.")
        st.stop()
    return pd.read_csv(file_path)

df = load_data()

st.markdown("### Top Momentum Stocks This Week (Based on 1-Week Returns)")
st.dataframe(df.sort_values("1W", ascending=False).reset_index(drop=True))

st.markdown("#### Filter by Minimum 1-Month Momentum")
threshold = st.slider("1M Return Threshold (%)", -50, 100, 0)
filtered = df[df["1M"] * 100 > threshold]
st.dataframe(filtered.reset_index(drop=True))
