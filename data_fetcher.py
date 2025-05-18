import yfinance as yf
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import os

# Basic in-memory cache
_data_cache = {}

def fetch_historical_data(ticker: str, period: str = "10y") -> pd.DataFrame:
    """
    Fetches historical data for a given ticker.

    Args:
        ticker (str): The stock ticker symbol.
        period (str): The period for which to fetch data (e.g., "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"). Defaults to "10y".

    Returns:
        pd.DataFrame: DataFrame containing historical data, or an empty DataFrame if fetching fails.
    """
    if ticker in _data_cache and period in _data_cache[ticker]:
        print(f"Fetching {ticker} data for {period} from cache.")
        return _data_cache[ticker][period]

    print(f"Fetching {ticker} data for {period} from Yahoo Finance.")
    try:
        # Fetch data
        data = yf.download(ticker, period=period, auto_adjust=False)

        # Store in cache
        if ticker not in _data_cache:
            _data_cache[ticker] = {}
        _data_cache[ticker][period] = data

        # Check if data is not empty and has 'Adj Close' column
        if not data.empty and 'Adj Close' in data.columns:
            return data
        else:
            print(f"Fetched empty data or missing 'Adj Close' for {ticker}.")
            return pd.DataFrame()
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return pd.DataFrame()

def fetch_fund_details(ticker: str) -> dict:
    """
    Fetches key details for a given fund.

    Args:
        ticker (str): The stock ticker symbol.

    Returns:
        dict: A dictionary containing fund details, or an empty dictionary if fetching fails.
    """
    # Details are less likely to change frequently, could add caching later if needed
    try:
        fund = yf.Ticker(ticker)
        details = {
            "symbol": fund.info.get("symbol"),
            "name": fund.info.get("shortName"),
            "category": fund.info.get("category"),
            "yield": fund.info.get("yield"),
            "expense_ratio": fund.info.get("netExpenseRatio"), # Using netExpenseRatio
            "beta": fund.info.get("beta3Year"), # Using beta3Year
            "ytd_return": fund.info.get('ytdReturn', np.nan), # Year-to-date return
            "52_week_change_percent": fund.info.get('fiftyTwoWeekChangePercent', np.nan), # 52-week change percentage
            "three_year_average_return": fund.info.get('threeYearAverageReturn', np.nan), # 3-year average return
            "five_year_average_return": fund.info.get('fiveYearAverageReturn', np.nan), # 5-year average return
        }


        return details
    except Exception as e:
        print(f"Error fetching details for {ticker}: {e}")
        return {}

DATA_DIR = "data"
HISTORICAL_DATA_FILE = "historical_fund_data.csv"

def _get_data_filepath() -> str:
    """
    Returns the full path to the historical data file, ensuring the data directory exists.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    return os.path.join(DATA_DIR, HISTORICAL_DATA_FILE)

def fetch_and_store_max_history(tickers: list[str]):
    """
    Fetches the maximum available historical data (Close price only) for a list of tickers
    and stores it in a CSV file in a wide format (Date, Ticker1_Close, Ticker2_Close, ...).

    Args:
        tickers (list[str]): A list of ticker symbols.
    """
    print(f"Fetching and storing max historical data (Close only) for: {tickers}")
    close_series = {} # Dictionary to hold 'Close' series for each ticker
    data_filepath = _get_data_filepath()

    for ticker in tickers:
        try:
            print(f"Fetching max data for {ticker}...")
            # Fetch data, auto_adjust=False keeps 'Close' and 'Adj Close' separate, we want 'Close'
            data = yf.download(ticker, period="max", auto_adjust=False)
            if not data.empty and 'Close' in data.columns:
                close_series[ticker] = data['Close'].squeeze() # Get the Close series
                print(f"Successfully fetched max data for {ticker}.")
            else:
                print(f"Fetched empty data or missing 'Close' for {ticker}.")
        except Exception as e:
            print(f"Error fetching max data for {ticker}: {e}")

    if close_series:
        # Combine all Close series into a single DataFrame, aligning by Date index
        all_close_data = pd.DataFrame(close_series)

        # Reset index to make Date a column
        all_close_data = all_close_data.reset_index().rename(columns={'index': 'Date'})

        # Ensure Date is datetime
        all_close_data['Date'] = pd.to_datetime(all_close_data['Date'])

        # Sort by Date for consistency
        all_close_data = all_close_data.sort_values(by=['Date'])

        try:
            all_close_data.to_csv(data_filepath, index=False)
            print(f"Successfully stored max historical data to {data_filepath}")
        except Exception as e:
            print(f"Error saving data to {data_filepath}: {e}")
    else:
        print("No data fetched for any ticker. Skipping save.")

def get_last_data_date(ticker: str = None) -> pd.Timestamp | None:
    """
    Reads the historical data file and returns the overall latest date or the last date for a specific ticker.

    Args:
        ticker (str, optional): The ticker symbol to get the last date for. If None, returns the overall latest date. Defaults to None.

    Returns:
        pd.Timestamp | None: The last date in the data for the specified ticker or overall, or None if the file doesn't exist, is empty, or the ticker is not found/has no data.
    """
    data_filepath = _get_data_filepath()
    if not os.path.exists(data_filepath):
        return None

    try:
        df = pd.read_csv(data_filepath, parse_dates=['Date'])

        if df.empty:
            return None

        if ticker:
            # Get the last non-NaN date for the specific ticker column
            if ticker in df.columns:
                # Ensure the ticker column is numeric (errors='coerce' will turn non-numeric into NaN)
                df[ticker] = pd.to_numeric(df[ticker], errors='coerce')
                # Find the max date where the ticker column is not NaN
                last_date_series = df.dropna(subset=[ticker])['Date']
                if not last_date_series.empty:
                    return last_date_series.max()
                else:
                    print(f"No valid data found for ticker {ticker} in the historical data file.")
                    return None
            else:
                print(f"Ticker {ticker} not found as a column in the historical data file.")
                return None
        else:
            # Return the overall latest date from the Date column
            return df['Date'].max()

    except Exception as e:
        print(f"Error reading data file to get last date: {e}")
        return None

def update_historical_data(tickers: list[str], force_update: bool = False):
    """
    Updates the historical data file with new data (Close price only) from the last stored date for each ticker.
    Loads existing data, fetches new data, combines them, and overwrites the file.

    Args:
        tickers (list[str]): A list of ticker symbols.
    """
    print(f"Updating historical data (Close only) for: {tickers}")
    data_filepath = _get_data_filepath()

    # Load existing data
    existing_data = load_historical_data(tickers) # Use the updated load function

    newly_fetched_close_series = {} # Dictionary to hold newly fetched 'Close' series

    for ticker in tickers:
        # Get the last date for this specific ticker from the existing data
        last_date = None
        if not existing_data.empty and ticker in existing_data.columns:
             # Find the last non-NaN date for this ticker
             last_date = existing_data.dropna(subset=[ticker])['Date'].max()


        if last_date:
            # Fetch data from the day after the last date
            start_date = last_date + timedelta(days=1)
            print(f"Fetching new data (Close only) for {ticker} from {start_date.strftime('%Y-%m-%d')} to today...")
            try:
                # Fetch data, auto_adjust=False keeps 'Close' and 'Adj Close' separate, we want 'Close'
                new_data = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), auto_adjust=False)
                if not new_data.empty and 'Close' in new_data.columns:
                    squeezed_data = new_data['Close'].squeeze()
                    if pd.api.types.is_scalar(squeezed_data):
                        # If squeeze returns a scalar, wrap it in a Series with the correct index
                        newly_fetched_close_series[ticker] = pd.Series([squeezed_data], index=[new_data.index[0]])
                    else:
                        newly_fetched_close_series[ticker] = squeezed_data # It's already a Series
                    print(f"Successfully fetched new data for {ticker}.")
                else:
                    print(f"No new data available for {ticker} since {last_date.strftime('%Y-%m-%d')}.")
            except Exception as e:
                print(f"Error fetching new data for {ticker}: {e}")
        else:
            # If no existing data for this ticker, fetch max history for it
            print(f"No existing data found for {ticker}. Fetching max history for this ticker.")
            try:
                 data = yf.download(ticker, period="max", auto_adjust=False)
                 if not data.empty and 'Close' in data.columns:
                      squeezed_data = data['Close'].squeeze()
                      if pd.api.types.is_scalar(squeezed_data):
                           # If squeeze returns a scalar, wrap it in a Series with the correct index
                           newly_fetched_close_series[ticker] = pd.Series([squeezed_data], index=[data.index[0]])
                      else:
                           newly_fetched_close_series[ticker] = squeezed_data # It's already a Series
                      print(f"Successfully fetched max data for {ticker}.")
                 else:
                      print(f"Fetched empty data or missing 'Close' for {ticker}.")
            except Exception as e:
                 print(f"Error fetching max data for {ticker}: {e}")


    if newly_fetched_close_series:
        # Combine all newly fetched Close series into a single DataFrame, aligning by Date index
        # Ensure all values in newly_fetched_close_series are Series before creating DataFrame
        series_dict = {k: (v if isinstance(v, pd.Series) else pd.Series([v])) for k, v in newly_fetched_close_series.items()}
        new_data_df = pd.DataFrame(series_dict)


        if not existing_data.empty:
            # Combine existing and new data
            # Set Date as index for combining
            existing_data = existing_data.set_index('Date')
            new_data_df.index = pd.to_datetime(new_data_df.index) # Ensure index is datetime for new data
            combined_data = new_data_df.combine_first(existing_data)
            combined_data = combined_data.reset_index().rename(columns={'index': 'Date'}) # Reset index back to column
        else:
            # If no existing data, the new data is the combined data
            combined_data = new_data_df.reset_index().rename(columns={'index': 'Date'}) # Reset index to make Date a column

        # Ensure Date is datetime and sort by Date
        combined_data['Date'] = pd.to_datetime(combined_data['Date'])
        combined_data = combined_data.sort_values(by=['Date'])

        # Ensure all original tickers are present as columns, even if no new data was fetched for them
        # Use the tickers list provided to the function for consistent column order
        column_order = ['Date'] + tickers
        combined_data = combined_data.reindex(columns=column_order)


        try:
            # Overwrite the entire file with the combined data
            combined_data.to_csv(data_filepath, index=False)
            print(f"Successfully updated historical data and saved to {data_filepath}")
        except Exception as e:
            print(f"Error saving updated data to {data_filepath}: {e}")
    else:
        print("No new data fetched for any ticker. Skipping update.")

def load_historical_data(tickers: list[str] = None) -> pd.DataFrame:
    """
    Loads historical data from the CSV file.

    Args:
        tickers (list[str], optional): A list of ticker symbols to filter by. If None, loads data for all tickers. Defaults to None.

    Returns:
        pd.DataFrame: DataFrame containing historical data, or an empty DataFrame if the file doesn't exist or is empty.
    """
    data_filepath = _get_data_filepath()
    if not os.path.exists(data_filepath):
        print(f"Historical data file not found at {data_filepath}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(data_filepath, parse_dates=['Date'])

        if df.empty:
            print("Historical data file is empty.")
            return pd.DataFrame()

        # The CSV is now in a wide format: Date, Ticker1, Ticker2, ...
        # We don't need to filter by ticker here, as all tickers are columns.
        # The 'tickers' argument can still be used by the caller to select specific columns if needed.

        # Ensure numeric columns (the ticker columns) are of the correct type
        # Use the provided tickers list to identify the numeric columns
        numeric_cols = tickers if tickers is not None else df.columns.tolist()
        # Exclude 'Date' from numeric conversion
        if 'Date' in numeric_cols:
            numeric_cols.remove('Date')

        for col in numeric_cols:
            if col in df.columns:
                # Use errors='coerce' to turn non-numeric values into NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Drop rows where essential numeric data (any of the ticker columns if tickers were specified) could not be converted
        subset_cols_to_check = tickers if tickers is not None else df.columns.tolist()
        if 'Date' in subset_cols_to_check:
             subset_cols_to_check.remove('Date')
        if subset_cols_to_check: # Only drop if there are columns to check
             df.dropna(subset=subset_cols_to_check, inplace=True)


        # Ensure data is sorted by Date
        df = df.sort_values(by=['Date'])

        return df

    except Exception as e:
        print(f"Error loading historical data from {data_filepath}: {e}")
        return pd.DataFrame()


if __name__ == '__main__':
    # Example Usage
    tickers = ["VTI", "VEA", "BND", "BNDX"]

    # Example of fetching and storing max history (can be run manually)
    # fetch_and_store_max_history(tickers)

    # Example of getting the last data date
    # last_date_overall = get_last_data_date()
    # print(f"Overall last data date: {last_date_overall}")
    # last_date_vti = get_last_data_date("VTI")
    # print(f"Last data date for VTI: {last_date_vti}")

    # Example of updating historical data (can be run manually)
    # update_historical_data(tickers)

    # Example of loading historical data
    # historical_data_all = load_historical_data()
    # print("\nLoaded Historical Data (all tickers):\n", historical_data_all.head())
    # print("\nLoaded Historical Data (all tickers):\n", historical_data_all.tail())

    # historical_data_vti_bnd = load_historical_data(["VTI", "BND"])
    # print("\nLoaded Historical Data (VTI and BND):\n", historical_data_vti_bnd.head())
    # print("\nLoaded Historical Data (VTI and BND):\n", historical_data_vti_bnd.tail())

    # Original example usage for fetching 1 year data and fund details
    for ticker in tickers:
        historical_data = fetch_historical_data(ticker, period="1y")
        if not historical_data.empty:
            print(f"\nHistorical Data for {ticker} (last 1 year):\n", historical_data.head())

        fund_details = fetch_fund_details(ticker)
        if fund_details:
            print(f"\nDetails for {ticker}:\n", fund_details)

    # Demonstrate caching
    print("\nFetching VTI data again to demonstrate caching:")
    fetch_historical_data("VTI", period="1y")
