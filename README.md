
Markdown

# S&P 500 Momentum Analyzer

This is a Streamlit web application that fetches historical daily stock data for S&P 500 companies, calculates their price momentum over various periods, and displays the results in an interactive table. It's designed to help users quickly identify top and bottom performing stocks based on recent price changes.

## Features

* **S&P 500 Ticker Fetching:** Automatically retrieves the latest list of S&P 500 company tickers from Wikipedia.

* **Historical Data Download:** Downloads daily close price data for all S&P 500 tickers using `yfinance`.

* **Momentum Calculation:** Calculates percentage change over 1-day, 1-week, 1-month, and 2-month periods.

* **Interactive Display:** Presents results in a sortable and filterable table using Streamlit's `st.dataframe`.

* **User Controls:** Allows users to select the data download period, sort column, sort order, and the number of top/bottom tickers to display via a sidebar.

* **Caching:** Utilizes Streamlit's caching mechanisms (`st.cache_data`) to optimize performance and reduce API calls.

* **Improved UI/UX:** Enhanced visual design with custom CSS for better readability, cleaner layout, and more satisfying interactive elements.

## Technologies Used

* **Python 3**

* **Streamlit:** For creating the interactive web application.

* **yfinance:** For fetching historical stock data.

* **pandas:** For data manipulation and analysis.

* **beautifulsoup4:** (Indirectly used by `pandas.read_html`) for parsing HTML tables from Wikipedia.

## Setup and Installation

To run this application locally, follow these steps:

1. **Clone the repository** (or save the `momentum_app.py` file to your local machine).

2. **Create a virtual environment** (recommended):

   ```bash
   python -m venv venv
Activate the virtual environment:

On Windows:

Bash

.\venv\Scripts\activate
On macOS/Linux:

Bash

source venv/bin/activate
Install the required Python packages:
Create a file named requirements.txt in the same directory as your momentum_app.py with the following content:

streamlit
yfinance
pandas
beautifulsoup4
Then, install them using pip:

Bash

pip install -r requirements.txt
How to Run the Application
Navigate to the directory where you saved momentum_app.py (and requirements.txt).

Run the Streamlit application from your terminal:

Bash

streamlit run momentum_app.py
This command will open a new tab in your web browser displaying the application. If it doesn't open automatically, it will provide a local URL (e.g., http://localhost:8501) that you can copy and paste into your browser.

Usage
Upon launching, the app will attempt to fetch S&P 500 tickers and download historical data.

Important Note: If the application displays a warning about "Falling back to a small hardcoded list," it means it could not access the Wikipedia page to get the full S&P 500 list. In this case, the results will be limited to a small demonstration set of 10 tickers. Please ensure your internet connection is stable and there are no firewall/network restrictions blocking access to Wikipedia.

Use the sidebar on the left to customize:

Data Period for Download: Choose how much historical data to fetch (e.g., 2 Months, 1 Year).

Sort Results by: Select which momentum period (1D, 1W, 1M, 2M) to sort the top and bottom lists.

Sort Order: Choose between "Highest First" (for top performers) or "Lowest First" (for bottom performers).

Number of Tickers to Display: Adjust how many top and bottom tickers are shown in each table.

The main area will display two tables: "Top Tickers" and "Bottom Tickers" based on your selected sorting criteria.

Notes
Data is sourced from Yahoo Finance.

Momentum is calculated based on daily close prices.

The S&P 500 ticker list is fetched from Wikipedia and cached for 1 day to reduce repeated network requests.

Historical stock data is cached for 4 hours to minimize API calls to Yahoo Finance.

Performance is not indicative of future results.
