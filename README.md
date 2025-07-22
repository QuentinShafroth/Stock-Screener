# S&P 500 Momentum Analyzer

This is a Streamlit web application that fetches historical daily stock data for S&P 500 companies, calculates their price momentum over various periods, and displays the results in an interactive table. It's designed to help users quickly identify top and bottom performing stocks based on recent price changes.

## Features

* **S&P 500 Ticker Fetching:** Automatically retrieves the latest list of S&P 500 company tickers from Wikipedia.

* **Historical Data Download:** Downloads daily close price data for all S&P 500 tickers using `yfinance`.

* **Momentum Calculation:** Calculates percentage change over 1-day, 1-week, 1-month, and 2-month periods.

* **Interactive Display:** Presents results in a sortable and filterable table using Streamlit's `st.dataframe`.

* **User Controls:** Allows users to select the data download period, sort column, sort order, and the number of top/bottom tickers to display via a sidebar.

* **Caching:** Utilizes Streamlit's caching mechanisms (`st.cache_data`) to optimize performance and reduce API calls.

## Technologies Used

* **Python 3**

* **Streamlit:** For creating the interactive web application.

* **yfinance:** For fetching historical stock data.

* **pandas:** For data manipulation and analysis.

* **beautifulsoup4:** (Indirectly used by `pandas.read_html`) for parsing HTML tables from Wikipedia.

## Setup and Installation

To run this application locally, follow these steps:

1.  **Clone the repository** (or save the `momentum_app.py` file to your local machine).

2.  **Create a virtual environment** (recommended):

    ```
    python -m venv venv

    ```

3.  **Activate the virtual environment:**

    * **On Windows:**

        ```
        .\venv\Scripts\activate

        ```

    * **On macOS/Linux:**

        ```
        source venv/bin/activate

        ```

4.  **Install the required Python packages:**
    Create a file named `requirements.txt` in the same directory as your `momentum_app.py` with the following content:

    ```
    streamlit
    yfinance
    pandas
    beautifulsoup4

    ```

    Then, install them using pip:

    ```
    pip install -r requirements.txt

    ```

## How to Run the Application

1.  **Navigate to the directory** where you saved `momentum_app.py` (and `requirements.txt`).

2.  **Run the Streamlit application** from your terminal:

    ```
    streamlit run momentum_app.py

    ```

3.  This command will open a new tab in your web browser displaying the application. If it doesn't open automatically, it will provide a local URL (e.g., `http://localhost:8501`) that you can copy and paste into your browser.

## Usage

* Upon launching, the app will automatically fetch S&P 500 tickers and download the last 3 months of daily data.

* Use the **sidebar on the left** to customize:

    * **Data Period for Download:** Choose how much historical data to fetch (e.g., 2 Months, 1 Year).

    * **Sort by:** Select which momentum period (1D, 1W, 1M, 2M) to sort the results by.

    * **Sort Order:** Choose between "Highest First" (for top performers) or "Lowest First" (for bottom performers).

    * **Number of Top/Bottom Tickers to Display:** Adjust how many tickers are shown in each table.

* The main area will display two tables: "Top Tickers" and "Bottom Tickers" based on your selected sorting criteria.

## Notes

* Data is sourced from Yahoo Finance.

* Momentum is calculated based on daily close prices.

* The S&P 500 ticker list is fetched from Wikipedia and cached for 1 day to reduce repeated network requests.

* Historical stock data is cached for 4 hours to minimize API calls to Yahoo Finance.

* If the Wikipedia fetch fails, the app will fall back to a small hardcoded list of common S&P 500 tickers for demonstration purposes.











Deep Research

Canvas

Image

