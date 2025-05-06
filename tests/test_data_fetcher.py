import sys
import os
# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import data_fetcher

# Mock data for yfinance.download
MOCK_HISTORICAL_DATA = pd.DataFrame({
    'Adj Close': [100, 101, 102, 103, 104]
}, index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']))

# Mock data for yfinance.Ticker().info
MOCK_FUND_INFO = {
    "symbol": "VTI",
    "shortName": "Vanguard Total Stock Market ETF",
    "category": "Domestic Equity",
    "yield": 0.015,
    "expenseRatio": 0.0003, # Example, may not be accurate or consistently available
    "beta": 1.0
}

@patch('yfinance.download')
def test_fetch_historical_data_success(mock_download):
    """Tests successful fetching of historical data."""
    mock_download.return_value = MOCK_HISTORICAL_DATA
    data = data_fetcher.fetch_historical_data("VTI", period="1y")
    mock_download.assert_called_once_with("VTI", period="1y")
    assert not data.empty
    assert isinstance(data, pd.DataFrame)
    assert 'Adj Close' in data.columns

@patch('yfinance.download')
def test_fetch_historical_data_invalid_ticker(mock_download):
    """Tests fetching historical data for an invalid ticker."""
    mock_download.return_value = pd.DataFrame() # yfinance returns empty DataFrame for invalid tickers
    data = data_fetcher.fetch_historical_data("INVALID_TICKER", period="1y")
    mock_download.assert_called_once_with("INVALID_TICKER", period="1y")
    assert data.empty
    assert isinstance(data, pd.DataFrame)

@patch('yfinance.Ticker')
def test_fetch_fund_details_success(mock_ticker):
    """Tests successful fetching of fund details."""
    mock_ticker_instance = MagicMock()
    mock_ticker_instance.info = MOCK_FUND_INFO
    mock_ticker.return_value = mock_ticker_instance

    details = data_fetcher.fetch_fund_details("VTI")
    mock_ticker.assert_called_once_with("VTI")
    assert isinstance(details, dict)
    assert details.get("symbol") == "VTI"
    assert details.get("name") == "Vanguard Total Stock Market ETF"

@patch('yfinance.Ticker')
def test_fetch_fund_details_invalid_ticker(mock_ticker):
    """Tests fetching fund details for an invalid ticker."""
    # yfinance.Ticker for an invalid ticker might raise an exception or return an object with empty info
    mock_ticker.side_effect = Exception("Invalid ticker")

    details = data_fetcher.fetch_fund_details("INVALID_TICKER")
    mock_ticker.assert_called_once_with("INVALID_TICKER")
    assert isinstance(details, dict)
    assert not details # Should return an empty dictionary on failure

# Mock data for file operations
MOCK_CSV_CONTENT = """Date,Open,High,Low,Close,Volume,Ticker
2023-01-01,100.0,101.0,99.0,100.0,1000000,VTI
2023-01-02,101.0,102.0,100.0,101.0,1100000,VTI
2023-01-01,50.0,51.0,49.0,50.0,500000,VEA
2023-01-02,51.0,52.0,50.0,51.0,550000,VEA
"""

MOCK_NEW_CSV_CONTENT = """Date,Open,High,Low,Close,Volume,Ticker
2023-01-03,102.0,103.0,101.0,102.0,1200000,VTI
2023-01-03,52.0,53.0,51.0,52.0,600000,VEA
"""

@patch('os.path.exists')
@patch('os.makedirs')
def test__get_data_filepath_creates_directory(mock_makedirs, mock_exists):
    """Tests that _get_data_filepath creates the data directory if it doesn't exist."""
    mock_exists.return_value = False
    data_fetcher._get_data_filepath()
    mock_makedirs.assert_called_once_with(data_fetcher.DATA_DIR)

@patch('os.path.exists')
@patch('os.makedirs')
def test__get_data_filepath_returns_correct_path(mock_makedirs, mock_exists):
    """Tests that _get_data_filepath returns the correct file path."""
    mock_exists.return_value = True # Directory exists
    filepath = data_fetcher._get_data_filepath()
    assert filepath == os.path.join(data_fetcher.DATA_DIR, data_fetcher.HISTORICAL_DATA_FILE)
    mock_makedirs.assert_not_called() # Should not create directory if it exists

@patch('yfinance.download')
@patch('pandas.DataFrame.to_csv')
@patch('data_fetcher._get_data_filepath')
def test_fetch_and_store_max_history_success(mock_get_filepath, mock_to_csv, mock_download):
    """Tests successful fetching and storing of max historical data."""
    mock_get_filepath.return_value = "fake/data/path.csv"
    mock_download.side_effect = [
        pd.DataFrame({'Close': [100, 101]}, index=pd.to_datetime(['2023-01-01', '2023-01-02'])), # VTI data
        pd.DataFrame({'Close': [50, 51]}, index=pd.to_datetime(['2023-01-01', '2023-01-02']))  # VEA data
    ]
    tickers = ["VTI", "VEA"]

    data_fetcher.fetch_and_store_max_history(tickers)

    assert mock_download.call_count == len(tickers)
    mock_to_csv.assert_called_once()
    # Further assertions could check the content of the DataFrame passed to to_csv

@patch('yfinance.download')
@patch('pandas.DataFrame.to_csv')
@patch('data_fetcher._get_data_filepath')
def test_fetch_and_store_max_history_empty_data(mock_get_filepath, mock_to_csv, mock_download):
    """Tests fetching and storing when yfinance returns empty data."""
    mock_get_filepath.return_value = "fake/data/path.csv"
    mock_download.return_value = pd.DataFrame() # Empty data for all tickers
    tickers = ["VTI", "VEA"]

    data_fetcher.fetch_and_store_max_history(tickers)

    assert mock_download.call_count == len(tickers)
    mock_to_csv.assert_not_called() # Should not save if no data is fetched

@patch('os.path.exists')
@patch('pandas.read_csv')
@patch('data_fetcher._get_data_filepath')
def test_get_last_data_date_file_not_exists(mock_get_filepath, mock_read_csv, mock_exists):
    """Tests get_last_data_date when the data file does not exist."""
    mock_get_filepath.return_value = "fake/data/path.csv"
    mock_exists.return_value = False
    last_date = data_fetcher.get_last_data_date()
    mock_exists.assert_called_once()
    mock_read_csv.assert_not_called()
    assert last_date is None

@patch('os.path.exists')
@patch('pandas.read_csv')
@patch('data_fetcher._get_data_filepath')
def test_get_last_data_date_empty_file(mock_get_filepath, mock_read_csv, mock_exists):
    """Tests get_last_data_date when the data file is empty."""
    mock_get_filepath.return_value = "fake/data/path.csv"
    mock_exists.return_value = True
    mock_read_csv.return_value = pd.DataFrame() # Empty DataFrame
    last_date = data_fetcher.get_last_data_date()
    mock_exists.assert_called_once()
    mock_read_csv.assert_called_once()
    assert last_date is None

@patch('os.path.exists')
@patch('pandas.read_csv')
@patch('data_fetcher._get_data_filepath')
def test_get_last_data_date_overall(mock_get_filepath, mock_read_csv, mock_exists):
    """Tests get_last_data_date for the overall latest date."""
    mock_get_filepath.return_value = "fake/data/path.csv"
    mock_exists.return_value = True
    mock_data = pd.DataFrame({
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']),
        'Ticker': ['VTI', 'VTI', 'VEA'] # VEA has a later date
    })
    mock_read_csv.return_value = mock_data
    last_date = data_fetcher.get_last_data_date()
    mock_exists.assert_called_once()
    mock_read_csv.assert_called_once()
    assert last_date == pd.to_datetime('2023-01-03')

@patch('os.path.exists')
@patch('pandas.read_csv')
@patch('data_fetcher._get_data_filepath')
def test_get_last_data_date_by_ticker(mock_get_filepath, mock_read_csv, mock_exists):
    """Tests get_last_data_date for a specific ticker."""
    mock_get_filepath.return_value = "fake/data/path.csv"
    mock_exists.return_value = True
    mock_data = pd.DataFrame({
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']),
        'Ticker': ['VTI', 'VTI', 'VEA']
    })
    mock_read_csv.return_value = mock_data
    last_date = data_fetcher.get_last_data_date("VTI")
    mock_exists.assert_called_once()
    mock_read_csv.assert_called_once()
    assert last_date == pd.to_datetime('2023-01-02')

@patch('os.path.exists')
@patch('pandas.read_csv')
@patch('data_fetcher._get_data_filepath')
def test_get_last_data_date_ticker_not_found(mock_get_filepath, mock_read_csv, mock_exists):
    """Tests get_last_data_date when the ticker is not in the file."""
    mock_get_filepath.return_value = "fake/data/path.csv"
    mock_exists.return_value = True
    mock_data = pd.DataFrame({
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02']),
        'Ticker': ['VTI', 'VTI']
    })
    mock_read_csv.return_value = mock_data
    last_date = data_fetcher.get_last_data_date("BND")
    mock_exists.assert_called_once()
    mock_read_csv.assert_called_once()
    assert last_date is None

@patch('data_fetcher.get_last_data_date')
@patch('yfinance.download')
@patch('pandas.DataFrame.to_csv')
@patch('data_fetcher._get_data_filepath')
def test_update_historical_data_success(mock_get_filepath, mock_to_csv, mock_download, mock_get_last_date):
    """Tests successful updating of historical data."""
    mock_get_filepath.return_value = "fake/data/path.csv"
    mock_get_last_date.side_effect = [
        pd.to_datetime('2023-01-02'), # Last date for VTI
        pd.to_datetime('2023-01-02')  # Last date for VEA
    ]
    mock_download.side_effect = [
        pd.DataFrame({'Close': [102]}, index=pd.to_datetime(['2023-01-03'])), # New VTI data
        pd.DataFrame({'Close': [52]}, index=pd.to_datetime(['2023-01-03']))  # New VEA data
    ]
    tickers = ["VTI", "VEA"]

    data_fetcher.update_historical_data(tickers)

    assert mock_get_last_date.call_count == len(tickers)
    assert mock_download.call_count == len(tickers)
    mock_to_csv.assert_called_once_with(
        "fake/data/path.csv",
        mode='a',
        header=False,
        index=False
    )
    # Further assertions could check the content of the DataFrame passed to to_csv

@patch('data_fetcher.get_last_data_date')
@patch('yfinance.download')
@patch('pandas.DataFrame.to_csv')
@patch('data_fetcher._get_data_filepath')
def test_update_historical_data_no_new_data(mock_get_filepath, mock_to_csv, mock_download, mock_get_last_date):
    """Tests updating when no new data is available."""
    mock_get_filepath.return_value = "fake/data/path.csv"
    mock_get_last_date.side_effect = [
        pd.to_datetime('2023-01-03'), # Last date for VTI
        pd.to_datetime('2023-01-03')  # Last date for VEA
    ]
    mock_download.return_value = pd.DataFrame() # No new data
    tickers = ["VTI", "VEA"]

    data_fetcher.update_historical_data(tickers)

    assert mock_get_last_date.call_count == len(tickers)
    assert mock_download.call_count == len(tickers)
    mock_to_csv.assert_not_called() # Should not append if no new data is fetched

@patch('data_fetcher.get_last_data_date')
@patch('yfinance.download')
@patch('pandas.DataFrame.to_csv')
@patch('data_fetcher._get_data_filepath')
def test_update_historical_data_no_existing_data(mock_get_filepath, mock_to_csv, mock_download, mock_get_last_date):
    """Tests updating when no existing data is found."""
    mock_get_filepath.return_value = "fake/data/path.csv"
    mock_get_last_date.return_value = None # No existing data
    tickers = ["VTI", "VEA"]

    data_fetcher.update_historical_data(tickers)

    assert mock_get_last_date.call_count == len(tickers)
    mock_download.assert_not_called() # Should not try to download if no last date
    mock_to_csv.assert_not_called() # Should not append

@patch('os.path.exists')
@patch('pandas.read_csv')
@patch('data_fetcher._get_data_filepath')
def test_load_historical_data_file_not_exists(mock_get_filepath, mock_read_csv, mock_exists):
    """Tests load_historical_data when the data file does not exist."""
    mock_get_filepath.return_value = "fake/data/path.csv"
    mock_exists.return_value = False
    df = data_fetcher.load_historical_data()
    mock_exists.assert_called_once()
    mock_read_csv.assert_not_called()
    assert df.empty

@patch('os.path.exists')
@patch('pandas.read_csv')
@patch('data_fetcher._get_data_filepath')
def test_load_historical_data_empty_file(mock_get_filepath, mock_read_csv, mock_exists):
    """Tests load_historical_data when the data file is empty."""
    mock_get_filepath.return_value = "fake/data/path.csv"
    mock_exists.return_value = True
    mock_read_csv.return_value = pd.DataFrame() # Empty DataFrame
    df = data_fetcher.load_historical_data()
    mock_exists.assert_called_once()
    mock_read_csv.assert_called_once()
    assert df.empty

@patch('os.path.exists')
@patch('pandas.read_csv')
@patch('data_fetcher._get_data_filepath')
def test_load_historical_data_success_all_tickers(mock_get_filepath, mock_read_csv, mock_exists):
    """Tests successful loading of historical data for all tickers."""
    mock_get_filepath.return_value = "fake/data/path.csv"
    mock_exists.return_value = True
    mock_data = pd.DataFrame({
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-01', '2023-01-02']),
        'Open': [100, 101, 50, 51],
        'High': [101, 102, 51, 52],
        'Low': [99, 100, 49, 50],
        'Close': [100, 101, 50, 51],
        'Volume': [1000000, 1100000, 500000, 550000],
        'Ticker': ['VTI', 'VTI', 'VEA', 'VEA']
    })
    mock_read_csv.return_value = mock_data
    df = data_fetcher.load_historical_data()
    mock_exists.assert_called_once()
    mock_read_csv.assert_called_once()
    assert not df.empty
    assert len(df) == 4
    assert list(df['Ticker'].unique()) == ['VTI', 'VEA'] # Check tickers present
    # Check sorting
    assert df.iloc[0]['Date'] <= df.iloc[1]['Date']
    assert df.iloc[2]['Date'] <= df.iloc[3]['Date']


@patch('os.path.exists')
@patch('pandas.read_csv')
@patch('data_fetcher._get_data_filepath')
def test_load_historical_data_success_filtered_tickers(mock_get_filepath, mock_read_csv, mock_exists):
    """Tests successful loading of historical data for filtered tickers."""
    mock_get_filepath.return_value = "fake/data/path.csv"
    mock_exists.return_value = True
    mock_data = pd.DataFrame({
        'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-01', '2023-01-02']),
        'Open': [100, 101, 50, 51],
        'High': [101, 102, 51, 52],
        'Low': [99, 100, 49, 50],
        'Close': [100, 101, 50, 51],
        'Volume': [1000000, 1100000, 500000, 550000],
        'Ticker': ['VTI', 'VTI', 'VEA', 'VEA']
    })
    mock_read_csv.return_value = mock_data
    df = data_fetcher.load_historical_data(["VTI"])
    mock_exists.assert_called_once()
    mock_read_csv.assert_called_once()
    assert not df.empty
    assert len(df) == 2
    assert list(df['Ticker'].unique()) == ['VTI'] # Only VTI data
    # Check sorting
    assert df.iloc[0]['Date'] <= df.iloc[1]['Date']
