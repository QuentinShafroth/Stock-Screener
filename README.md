

Install the required Python packages:
Create a file named requirements.txt in the same directory as your momentum_app.py with the following content:

streamlit
yfinance
pandas
beautifulsoup4

Then, install them using pip:

pip install -r requirements.txt

How to Run the Application
Navigate to the directory where you saved momentum_app.py (and requirements.txt).

Run the Streamlit application from your terminal:

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

Historical stock data is cached for 4 hours to minimize
