import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import io
import requests
from bs4 import BeautifulSoup

# --- Streamlit App Configuration ---
st.set_page_config(
    page_title="S&P 500 Momentum Analyzer",
    page_icon="📈",
    layout="wide",  # Use wide layout for more space
    initial_sidebar_state="expanded"  # Keep sidebar expanded by default
)

# --- Custom CSS for a cleaner look and feel ---
st.markdown("""
<style>
    /* Harmonize with Streamlit's default dark theme (as seen in screenshot) or provide a consistent dark theme */
    .stApp {
        background-color: #1a1a1a; /* Dark background */
        color: #e0e0e0; /* Light grey text for better readability */
    }
    /* Ensure all text within the main app body is readable */
    .stApp, .stMarkdown, .stText, .stCode, .stAlert > div > div, .st-emotion-cache-16txtv3 {
        color: #e0e0e0; /* Consistent light text color for main content and general widgets */
    }

    /* Specific adjustments for text within sidebar widgets */
    section[data-testid="stSidebar"] .st-emotion-cache-1hbv09k, /* Selectbox label */
    section[data-testid="stSidebar"] .st-emotion-cache-10qgysq, /* Radio button labels */
    section[data-testid="stSidebar"] .st-emotion-cache-1g610q5, /* Slider label */
    section[data-testid="stSidebar"] .st-emotion-cache-10qgysq /* General sidebar text */
     {
        color: #e0e0e0 !important; /* Force light text color in sidebar */
    }


    .stButton>button {
        background-color: #4CAF50; /* Green button */
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-size: 16px;
        transition: all 0.2s ease-in-out;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.4); /* Stronger shadow for dark theme */
    }
    .stButton>button:hover {
        background-color: #45a049; /* Darker green on hover */
        box_shadow: 3px 3px 8px rgba(0,0,0,0.5);
        transform: translateY(-2px);
    }
    /* Slider colors - keep them vibrant */
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
    /* DataFrame styling */
    .stDataFrame {
        border-radius: 10px;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.3); /* Adjust shadow for dark theme */
        overflow: hidden; /* Ensures rounded corners apply to content */
        /* Streamlit's dataframe should adapt text color, but if not, uncomment below */
        /* color: #e0e0e0; */
    }
    /* Alert styling for readability */
    .stAlert {
        border-radius: 8px;
        /* Ensure text is readable on default alert backgrounds */
        /* Overriding Streamlit's default alert text color */
        color: #333333 !important; /* Darker text for info/success/warning alerts */
    }
    .stAlert.stAlert--info {
        background-color: #d1ecf1; /* Light blue */
        color: #0c5460 !important; /* Dark blue text */
    }
    .stAlert.stAlert--success {
        background-color: #d4edda; /* Light green */
        color: #155724 !important; /* Dark green text */
    }
    .stAlert.stAlert--warning {
        background-color: #fff3cd; /* Light yellow */
        color: #856404 !important; /* Dark yellow text */
    }
    .stAlert.stAlert--error {
        background-color: #f8d7da; /* Light red */
        color: #721c24 !important; /* Dark red text */
    }
    /* Headings for better contrast */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #f0f0f0; /* Lighter headings for dark theme */
    }
    /* Adjust sidebar width for better readability of long options */
    section[data-testid="stSidebar"] {
        width: 300px !important;
        background-color: #2c2c2c; /* Slightly lighter dark for sidebar */
        color: #e0e0e0; /* Light text in sidebar */
    }
    /* Ensure text within sidebar widgets is also readable */
    /* These specific selectors target various Streamlit widget text elements */
    [data-testid="stSelectbox"] label,
    [data-testid="stRadio"] label,
    [data-testid="stSlider"] label,
    [data-testid="stTextInput"] label,
    [data-testid="stCheckbox"] label,
    .st-emotion-cache-10qgysq /* General label text */
    {
        color: #e0e0e0 !important; /* Force light text color in sidebar */
    }
    /* Ensure input fields themselves have readable text */
    .st-emotion-cache-1g610q5 div div input { /* For selectbox input */
        color: #e0e0e0 !important;
    }
    .st-emotion-cache-1g610q5 div div { /* For radio button text */
        color: #e0e0e0 !important;
    }
    /* Specific styling for the slider value display */
    .st-emotion-cache-1g610q5 div div div div:nth-child(2) { /* Targeting the slider value text */
        color: #e0e0e0 !important;
    }
    /* Force all sidebar text to be light gray */
section[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;

</style>
""", unsafe_allow_html=True)


# --- Cell 1: Import Libraries and Define Ticker Fetching Function ---

@st.cache_data(ttl=timedelta(days=1))  # Cache for 1 day to avoid frequent Wikipedia fetches
def get_sp500_tickers():
    """
    Fetches the list of S&P 500 tickers from Wikipedia.
    Handles the '. ' to '-' replacement for compatibility with yfinance.
    """
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        html = requests.get(url, headers=headers).text
        tables = pd.read_html(html)
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

@st.cache_data(ttl=timedelta(hours=4))  # Cache data for 4 hours to reduce API calls
def download_sp500_data(tickers, period='3mo', interval='1d'):
    """
    Downloads historical stock data for a list of tickers.
    """
    # Check if using fallback tickers and inform the user clearly
    if len(tickers) == 10 and tickers[0] == 'AAPL':  # Assuming the hardcoded list starts with AAPL
        st.warning("Using a small hardcoded list of tickers due to Wikipedia fetch error. "
                   "To see full S&P 500 results, please ensure your internet connection is stable "
                   "and the Wikipedia URL is accessible.")

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
            '1W': safe_pct_change(current_price, get_past_price(df_ticker_close, 5)),    # Approx 1 week (5 trading days)
            '1M': safe_pct_change(current_price, get_past_price(df_ticker_close, 22)),   # Approx 1 month (22 trading days)
            '2M': safe_pct_change(current_price, get_past_price(df_ticker_close, 44))    # Approx 2 months (44 trading days)
        }
        momentum_results.append(momentum)

    return pd.DataFrame(momentum_results)

# --- NEW: Function to fetch company description and sector using yfinance ---
@st.cache_data(ttl=timedelta(weeks=1)) # Cache for a week as descriptions and sectors don't change often
def get_company_description_and_sector_yf(ticker_symbol):
    """
    Fetches the company's long business summary (description) and sector using yfinance.
    Returns a tuple (description, sector).
    """
    try:
        ticker_obj = yf.Ticker(ticker_symbol)
        info = ticker_obj.info
        description = info.get('longBusinessSummary', 'Description not available.')
        sector = info.get('sector', 'Sector not available.')
        return description, sector
    except Exception as e:
        return f"Description not available (Error: {e})", "Sector not available."


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
    # Corrected the typo from '1M' to '2M' in the dropna subset as per typical momentum calculations
    momentum_df.dropna(subset=['1D', '1W', '1M', '2M'], how='all', inplace=True) 
    final_rows = len(momentum_df)
    
    # Inform user about data completeness (retained for clarity, can be removed for final polish)
    if final_rows < initial_rows:
        st.info(f"Note: {initial_rows - final_rows} tickers were excluded due to incomplete data for all momentum periods. Displaying results for {final_rows} tickers.")
    else:
        st.success(f"Momentum calculated for all {final_rows} tickers.")


    # --- Display Results with User Controls (Tables First) ---
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

    # --- Company Descriptions and Sector Summaries (Second) ---
    st.header("Detailed Company Information (Description & Sector)")

    # Determine top and bottom tickers for details fetching based on user's sort_column and num_display
    # Filter out NaNs in the sort_column before sorting
    momentum_df_filtered = momentum_df.dropna(subset=[sort_column])

    momentum_df_sorted_top = momentum_df_filtered.sort_values(sort_column, ascending=False)
    top_tickers = momentum_df_sorted_top.head(num_display)['Ticker'].to_list()

    momentum_df_sorted_bottom = momentum_df_filtered.sort_values(sort_column, ascending=True)
    bottom_tickers = momentum_df_sorted_bottom.head(num_display)['Ticker'].to_list()
    # Combine the lists and remove duplicates using set for efficient fetching
    all_tickers_for_details = list(set(top_tickers + bottom_tickers))

    if not all_tickers_for_details:
        st.info("No tickers available to fetch descriptions or sectors for. Please ensure momentum data is present.")
    else:
        st.info(f"Fetching news for {len(all_tickers_for_details)} top/bottom tickers by {sort_column} momentum...")
        with st.spinner("Retrieving company details..."):
            for ticker in all_tickers_for_details:
                description, sector = get_company_description_and_sector_yf(ticker)
                st.markdown(f"#### {ticker}:")
                if sector and sector != 'Sector not available.':
                    st.markdown(f"**Sector:** {sector}")
                else:
                    st.info(f"Sector not available for {ticker}.")

                if description and description != 'Description not available.':
                    st.markdown(f"**Description:** {description}")
                else:
                    st.info(f"Company description not available for {ticker}.")
                st.markdown("---") # Separator for each ticker's info


    # --- News Headlines (Third) ---
    st.header("Latest News Headlines")

    if not all_tickers_for_details: # Re-use the list from above
        st.info("No tickers available to fetch news for. Please ensure momentum data is present.")
    else:
        st.info(f"Fetching news for {len(all_tickers_for_details)} top/bottom 1-week momentum tickers...")
        finviz_url = 'https://finviz.com/quote.ashx?t='
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
        news_tables = {}
        n_headlines = 3 # Number of article headlines displayed per ticker

        with st.spinner("Downloading news data, this might take a moment."):
            for ticker in all_tickers_for_details:
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

        st.markdown("### Latest Headlines")
        # Display News Data
        if news_tables:
            for ticker in all_tickers_for_details:
                df = news_tables.get(ticker) # Use .get() to avoid KeyError if ticker is not in news_tables
                if df:
                    df_tr = df.findAll('tr')
                    st.markdown(f"#### {ticker}:")
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
                st.markdown("---") # Separator for each ticker's news


    st.markdown("---")
    st.info("Data provided by Yahoo Finance and Finviz. Momentum is calculated based on daily close prices. Performance is not indicative of future results.")

if __name__ == '__main__':
    main()
