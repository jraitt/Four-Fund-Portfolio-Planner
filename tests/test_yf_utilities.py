import sys
import os
import pytest
from unittest.mock import patch, MagicMock
import pandas as pd

# Add project root for module imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to be tested
from YahooFinance import yf_utilities

# --- Mock Data ---
MOCK_TICKER_INFO = {
    "symbol": "VTI",
    "shortName": "Vanguard Total Stock Market ETF",
    "quoteType": "ETF",
    "category": "US Equity",
    "regularMarketPrice": 250.00,
    "regularMarketPreviousClose": 249.00,
    "fiftyTwoWeekHigh": 260.00,
    "fiftyTwoWeekLow": 220.00,
    "fiftyDayAverage": 255.00,
    "twoHundredDayAverage": 240.00,
    "yield": 0.015,
    "netExpenseRatio": 0.03,
}

MOCK_TICKER_FAST_INFO = {
    "last_price": 250.00,
    "regularMarketPreviousClose": 249.00,
}

# --- Tests ---

@patch('YahooFinance.yf_utilities.yf.Ticker')
def test_fetch_fund_details_success(mock_yf_ticker):
    """
    Tests successful fetching of fund details.
    """
    # Configure the mock yf.Ticker object
    mock_ticker_instance = MagicMock()
    mock_yf_ticker.return_value = mock_ticker_instance

    mock_ticker_instance.info = MOCK_TICKER_INFO
    mock_ticker_instance.fast_info = MOCK_TICKER_FAST_INFO

    fund_details_df = yf_utilities.fetch_fund_details(["VTI"])

    mock_yf_ticker.assert_called_once_with("VTI")
    assert isinstance(fund_details_df, pd.DataFrame)
    assert not fund_details_df.empty

    # Access the row for VTI by filtering the 'Symbol' column
    # The 'Symbol' column is set as index in the actual function, so we need to access it differently
    vti_row = fund_details_df.loc["VTI"]

    assert vti_row['Name'] == "Vanguard Total Stock Market ETF"
    assert vti_row['Price'] == 250.00
    assert vti_row['ER'] == 0.0003 # 0.03 / 100
    assert vti_row['D Ch'] == 1.00
    assert vti_row['D Ch%'] == (250.00 / 249.00) - 1

@patch('YahooFinance.yf_utilities.yf.Ticker')
def test_fetch_fund_details_api_failure(mock_yf_ticker):
    """
    Tests API failure by mocking yf.Ticker to raise an exception.
    """
    mock_yf_ticker.side_effect = Exception("API Error")

    fund_details_df = yf_utilities.fetch_fund_details(["INVALID"])

    mock_yf_ticker.assert_called_once_with("INVALID")
    assert isinstance(fund_details_df, pd.DataFrame)
    assert fund_details_df.empty

@patch('YahooFinance.yf_utilities._get_data_filepath')
@patch('pandas.read_csv')
@patch('os.path.exists')
def test_get_historical_returns_success(mock_exists, mock_read_csv, mock_get_path):
    """
    Tests successful return retrieval from a mocked CSV file.
    """
    mock_get_path.return_value = 'mock/path/data.csv'
    mock_exists.return_value = True
    mock_data = pd.DataFrame({
        'Date': pd.to_datetime(['2023-01-01', '2023-01-08']),
        'VTI': [100.00, 105.00]
    })
    mock_read_csv.return_value = mock_data

    returns_df = yf_utilities.get_historical_returns(["VTI"])

    mock_read_csv.assert_called_once_with('mock/path/data.csv', parse_dates=['Date'])
    assert isinstance(returns_df, pd.DataFrame)
    assert 'VTI' in returns_df.index
    assert '1w' in returns_df.columns
    assert isinstance(returns_df.loc['VTI', '1w'], float)

@patch('YahooFinance.yf_utilities._get_data_filepath')
@patch('os.path.exists')
def test_get_historical_returns_no_file(mock_exists, mock_get_path):
    """
    Tests behavior when the data file does not exist.
    """
    mock_get_path.return_value = 'mock/path/data.csv'
    mock_exists.return_value = False

    returns_df = yf_utilities.get_historical_returns(["VTI"])

    assert isinstance(returns_df, pd.DataFrame)
    assert returns_df.empty