import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

# --- Streamlit App Configuration (rest of your existing code) ---
st.set_page_config(
    page_title="S&P 500 Momentum Analyzer",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ... (Your CSS and existing functions: get_sp500_tickers, download_sp500_data, calculate_momentum_for_all) ...

# --- NEW: Function to fetch company description ---
@st.cache_data(ttl=timedelta(weeks=1)) # Cache for a week as descriptions don't change often
def get_company_description(ticker):
    """
    Fetches the company description for a given ticker using Financial Modeling Prep API.
    Replace YOUR_FMP_API_KEY with your actual API key.
    """
    # Replace with your actual FMP API Key
    FMP_API_KEY = "YOUR_FMP_API_KEY" # <<< IMPORTANT: Get your API key from financialmodelingprep.com

    if FMP_API_KEY == "YOUR_FMP_API_KEY":
        st.warning("Please replace 'YOUR_FMP_API_KEY' with your actual Financial Modeling Prep API key in the code for company descriptions.")
        return "API Key not set."

    url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={FMP_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if data and isinstance(data, list) and len(data) > 0 and 'description' in data[0]:
            return data[0]['description']
        else:
            return "Description not found."
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching description for {ticker}: {e}")
        return "Error fetching description."
    except IndexError: # Handle case where data might be an empty list if ticker not found
        return "Description not found for this ticker."

# --- Main Streamlit App Logic ---
def main():
    st.title("📈 S&P 500 Momentum Analyzer")
    st.markdown("""
    This application fetches daily stock data for S&P 500 companies and calculates their price momentum
    over various periods (1-day, 1-week, 1-month, 2-months). Use the sidebar to customize your analysis.
    """)

    # ... (Your sidebar and data download/momentum calculation code) ...

    # --- News Fetching and Display ---
    st.header("Latest News Headlines and Company Descriptions for Top/Bottom Momentum Tickers")

    # Determine top and bottom 1W tickers for news fetching
    momentum_df_sorted_1w_top = momentum_df.sort_values('1W', ascending=False).dropna(subset=['1W'])
    top_1w_tickers = momentum_df_sorted_1w_top.head(10)['Ticker'].to_list()

    momentum_df_sorted_1w_bottom = momentum_df.sort_values('1W', ascending=True).dropna(subset=['1W'])
    bottom_1w_tickers = momentum_df_sorted_1w_bottom.head(10)['Ticker'].to_list()
    
    all_news_tickers = list(set(top_1w_tickers + bottom_1w_tickers)) # Use set to avoid duplicates

    if not all_news_tickers:
        st.info("No tickers available to fetch news or descriptions for. Please ensure momentum data is present.")
    else:
        st.info(f"Fetching news and descriptions for {len(all_news_tickers)} top/bottom 1-week momentum tickers...")
        finviz_url = 'https://finviz.com/quote.ashx?t='
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        news_tables = {}
        n_headlines = 3 # Number of article headlines displayed per ticker

        # Get News Data
        st.subheader("Fetching News...")
        with st.spinner("Downloading news data, this may take a moment..."):
            for ticker in all_news_tickers:
                url = finviz_url + ticker
                try:
                    response = requests.get(url, headers=headers)
                    response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

                    html = BeautifulSoup(response.text, features="lxml")
                    news_table = html.find(id='news-table')
                    if news_table:
                        news_tables[ticker] = news_table
                    else:
                        st.warning(f"Could not find 'news-table' for {ticker} from Finviz.")

                except requests.exceptions.RequestException as err:
                    st.error(f"Error fetching news for {ticker}: {err}")
        st.success("News data fetching attempt complete.")

        st.markdown("### Company Information")
        # Display Data
        for ticker in all_news_tickers:
            st.markdown(f"#### {ticker}:")
            
            # Get and display description
            description = get_company_description(ticker)
            if description and description != "Description not found." and description != "Error fetching description.":
                st.markdown(f"**Description:** {description}")
            else:
                st.info(f"Description not available for {ticker} ({description}).")

            # Display news headlines
            df = news_tables.get(ticker)
            if df:
                df_tr = df.findAll('tr')
                st.markdown(f"**Latest Headlines:**")
                news_count = 0
                for i, table_row in enumerate(df_tr):
                    if news_count >= n_headlines:
                        break

                    a_tag = table_row.find('a')
                    td_tag = table_row.find('td')

                    if a_tag and td_tag:
                        a_text = a_tag.text
                        td_text = td_tag.text.strip()
                        st.markdown(f"- **{a_text}** ({td_text})")
                        news_count += 1
                if news_count == 0:
                    st.info(f"No headlines found for {ticker} from Finviz.")
            else:
                st.info(f"No news data available to display for {ticker}.")
            st.markdown("---") # Separator for each ticker's info
        
    st.info("Data provided by Yahoo Finance, Finviz, and Financial Modeling Prep. Momentum is calculated based on daily close prices. Performance is not indicative of future results.")

if __name__ == '__main__':
    main()
