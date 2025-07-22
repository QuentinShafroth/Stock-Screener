import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import io

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="S&P 500 Momentum Analyzer",
    page_icon="📈",
    layout="wide", # Use wide layout for more space
    initial_sidebar_state="expanded" # Keep sidebar expanded by default
)

# --- Custom CSS for a cleaner look and feel ---
st.markdown("""
<style>
    /* General styling for better readability and spacing */
    .stApp {
        background-color: #f0f2f6; /* Light grey background */
        color: #333333; /* Darker text */
    }
    .stButton>button {
        background-color: #4CAF50; /* Green button */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        transition: all 0.2s ease-in-out;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #45a049; /* Darker green on hover */
        box-shadow: 3px 3px 8px rgba(0,0,0,0.3);
        transform: translateY(-2px);
    }
    .stSlider > div > div > div:nth-child(1) {
        background-color: #4CAF50; /* Slider track color */
    }
    .stSlider > div > div > div:nth-child(2) {
        background-color: #4CAF50; /* Slider fill color */
    }
    .stSlider > div > div > div:nth-child(3) {
        background-color: #4CAF50; /* Slider handle color */
        border: 2px solid #4CAF50;
    }
    .stDataFrame {
        border-radius: 10px;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.1);
        overflow: hidden; /* Ensures rounded corners apply to content */
    }
    .stAlert {
        border-radius: 8px;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #2c3e50; /* Darker headings */
    }
    /* Adjust sidebar width for better readability of long options */
    section[data-testid="stSidebar"] {
        width: 300px !important;
    }
</style>
""", unsafe_allow_html=True)


# --- Cell 1: Import Libraries and Define Ticker Fetching Function ---

@st.cache_data(ttl=timedelta(days=1)) # Cache for 1 day to avoid frequent Wikipedia fetches
def get_sp500_tickers():
    """
    Fetches the list of S&P 500 tickers from Wikipedia.
    Handles the '. ' to '-' replacement for compatibility with yfinance.
    """
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    try:
        tables = pd.read_html(url)
        # Assuming the first table contains the S&P 500 list
        tickers = tables[0]['Symbol'].tolist()
        # yfinance uses '-' instead of '.' for some tickers (e.g., BRK.B -> BRK-B)
        return [t.replace('.', '-') for t in tickers]
    except Exception as e:
        st.error(f"Error fetching S&P 500 tickers from Wikipedia: {e}")
        st.warning("Falling back to a small hardcoded list for demonstration. Please check your internet connection or URL.")
        # Fallback to a small list if Wikipedia parsing fails
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'JPM', 'V', 'PG', 'UNH']

# --- Cell 2: Download All S&P 500 Daily Data ---

@st.cache_data(ttl=timedelta(hours=4)) # Cache data for 4 hours to reduce API calls
def download_sp500_data(tickers, period='3mo', interval='1d'):
    """
    Downloads historical stock data for a list of tickers.
    """
    st.info(f"Fetching {len(tickers)} S&P 500 tickers...")
    st.info(f"Downloading {period} of {interval} data for all tickers...")
    
    with st.spinner("Downloading data, this may take a moment..."):
        all_tickers_data = yf.download(tickers, period=period, interval=interval, progress=False, actions=False)

    if all_tickers_data.empty:
        st.warning("WARNING: No data downloaded. Please check ticker list and Yahoo Finance availability.")
        return pd.DataFrame() # Return empty DataFrame
    else:
        st.success("Data download complete.")
        return all_tickers_data

# --- Cell 3: Define Momentum Calculation Function ---

def calculate_momentum_for_all(data_df):
    """
    Calculates momentum for all tickers from a single DataFrame of downloaded data.
    This function is now separate from data downloading and can be called repeatedly
    on the `data_df` object.

    Args:
        data_df (pd.DataFrame): DataFrame containing historical stock data,
                                typically downloaded from yfinance.
                                Expected format is multi-index columns (e.g., 'Close', 'Ticker').

    Returns:
        pd.DataFrame: A DataFrame with momentum results for each ticker,
                      including 'Ticker', '1D', '1W', '1M', '2M' change.
    """
    momentum_results = []

    if data_df.empty:
        return pd.DataFrame()

    # Ensure data_df has a multi-level column index where one level is 'Close'
    # yfinance.download with multiple tickers typically returns a MultiIndex (Metric, Ticker)
    if isinstance(data_df.columns, pd.MultiIndex):
        if 'Close' in data_df.columns.get_level_values(0):
            close_prices_df = data_df['Close']
        else:
            # Handle case where 'Close' might be on the second level, though less common for direct yf.download output
            try:
                # This might result in a single-level index if only one ticker was downloaded
                close_prices_df = data_df.xs('Close', level=1, axis=1, drop_level=False)
                # If it's still multi-index, drop the 'Close' level to get just ticker
                if isinstance(close_prices_df.columns, pd.MultiIndex):
                    close_prices_df = close_prices_df.droplevel(1, axis=1)
                else: # If it became single-level (e.g., one ticker), then it's already just the ticker
                    pass
            except KeyError:
                st.error("Error: 'Close' prices not found in the expected column structure. Please verify data_df format.")
                return pd.DataFrame()
    else:
        # If it's a single-level index, assume it's already 'Close' prices per ticker
        close_prices_df = data_df
        # If there's only one column and it's not a ticker, try to find the 'Close' column
        if 'Close' in close_prices_df.columns:
            close_prices_df = close_prices_df[['Close']]
            if len(close_prices_df.columns) == 1:
                close_prices_df.columns = [data_df.columns[0]] # Rename to the ticker
            else:
                st.warning("Warning: Unrecognized single-level DataFrame structure. Attempting to proceed.")

    # Iterate through each ticker's 'Close' price series
    for ticker in close_prices_df.columns:
        df_ticker_close = close_prices_df[ticker].dropna()

        if df_ticker_close.empty or len(df_ticker_close) < 2:
            # st.write(f"Skipping {ticker}: Not enough data for momentum calculation.")
            continue

        # Ensure the index is sorted for reliable date lookups (already generally handled by yfinance)
        df_ticker_close = df_ticker_close.sort_index()

        current_price = df_ticker_close.iloc[-1]

        def get_past_price(series, days_ago):
            # We need at least `days_ago + 1` data points for a period of `days_ago`
            # (e.g., for 1 day ago, we need today and yesterday, so 2 points).
            if len(series) < days_ago + 1:
                return None
            return series.iloc[-(days_ago + 1)]

        def safe_pct_change(current, past):
            if past is not None and past != 0:
                return (current - past) / past
            return None

        momentum = {
            'Ticker': ticker,
            '1D': safe_pct_change(current_price, get_past_price(df_ticker_close, 1)),
            '1W': safe_pct_change(current_price, get_past_price(df_ticker_close, 5)),   # Approx 1 week (5 trading days)
            '1M': safe_pct_change(current_price, get_past_price(df_ticker_close, 22)),  # Approx 1 month (22 trading days)
            '2M': safe_pct_change(current_price, get_past_price(df_ticker_close, 44))   # Approx 2 months (44 trading days)
        }
        momentum_results.append(momentum)

    return pd.DataFrame(momentum_results)

# --- Main Streamlit App Logic ---
def main():
    st.title("📈 S&P 500 Momentum Analyzer")
    st.markdown("""
    This application fetches daily stock data for S&P 500 companies and calculates their price momentum
    over various periods (1-day, 1-week, 1-month, 2-months). Use the sidebar to customize your analysis.
    """)

    # --- User Inputs in Sidebar ---
    with st.sidebar:
        st.header("Analysis Settings")
        st.markdown("Adjust the parameters below to refine your momentum analysis.")

        data_period_options = {
            "2 Months": "2mo",
            "3 Months": "3mo",
            "6 Months": "6mo",
            "1 Year": "1y",
            "2 Years": "2y"
        }
        selected_period_label = st.selectbox(
            "Select Data Period for Download:",
            list(data_period_options.keys()),
            index=1, # Default to 3 Months
            help="Choose the historical period for which to download stock data."
        )
        selected_period = data_period_options[selected_period_label]

        sort_column = st.selectbox(
            "Sort Results by:",
            ['1M', '1W', '1D', '2M'],
            index=0, # Default to 1M
            help="Select the momentum period to sort the top and bottom lists."
        )
        sort_order = st.radio(
            "Sort Order:",
            ("Highest First", "Lowest First"),
            help="Choose to see tickers with the highest or lowest momentum first."
        )
        ascending = True if sort_order == "Lowest First" else False

        num_display = st.slider(
            "Number of Tickers to Display:",
            min_value=5,
            max_value=50,
            value=10,
            step=5,
            help="Set how many top and bottom tickers to show in each table."
        )

        st.markdown("---")
        st.markdown("Developed with ❤️ using Streamlit and yfinance.")

    # --- Data Download ---
    sp500_tickers = get_sp500_tickers()
    if not sp500_tickers:
        st.error("Could not retrieve S&P 500 tickers. Please try again later.")
        return

    all_tickers_data = download_sp500_data(sp500_tickers, period=selected_period)

    if all_tickers_data.empty:
        st.warning("No data available to calculate momentum.")
        return

    # --- Momentum Calculation ---
    st.subheader("Calculating Momentum...")
    momentum_df = calculate_momentum_for_all(all_tickers_data)

    if momentum_df.empty:
        st.warning("No momentum results generated. Check data validity or selected period.")
        return

    # Ensure momentum columns are numeric for sorting
    for col in ['1D', '1W', '1M', '2M']:
        momentum_df[col] = pd.to_numeric(momentum_df[col], errors='coerce')
    
    # Drop rows where all momentum values are NaN (e.g., if a ticker had no valid periods)
    initial_rows = len(momentum_df)
    momentum_df.dropna(subset=['1D', '1W', '1M', '2M'], how='all', inplace=True)
    final_rows = len(momentum_df)
    
    # Inform user about data completeness (retained for clarity, can be removed for final polish)
    if final_rows < initial_rows:
        st.info(f"Note: {initial_rows - final_rows} tickers were excluded due to incomplete data for all momentum periods. Displaying results for {final_rows} tickers.")
    else:
        st.success(f"Momentum calculated for all {final_rows} tickers.")


    # --- Display Results with User Controls ---
    st.subheader("Analysis Results")

    # Format percentage columns for display
    formatted_momentum_df = momentum_df.copy()
    for col in ['1D', '1W', '1M', '2M']:
        formatted_momentum_df[col] = formatted_momentum_df[col].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "N/A")

    # Use columns for a cleaner side-by-side display
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"#### Top {min(num_display, final_rows)} Tickers by {sort_column} Change")
        # Ensure we don't try to display more rows than available
        top_results = momentum_df.sort_values(sort_column, ascending=False).head(num_display)
        st.dataframe(formatted_momentum_df.loc[top_results.index].reset_index(drop=True), use_container_width=True)

    with col2:
        st.markdown(f"#### Bottom {min(num_display, final_rows)} Tickers by {sort_column} Change")
        # Ensure we don't try to display more rows than available
        bottom_results = momentum_df.sort_values(sort_column, ascending=True).head(num_display)
        st.dataframe(formatted_momentum_df.loc[bottom_results.index].reset_index(drop=True), use_container_width=True)

    st.markdown("---")
    st.info("Data provided by Yahoo Finance. Momentum is calculated based on daily close prices. Performance is not indicative of future results.")

if __name__ == '__main__':
    main()
