import sys
import os
# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import pytest
import matplotlib.pyplot as plt
import pandas as pd
import visualizer

def test_generate_pie_chart():
    """Tests the generate_pie_chart function."""
    sizes = [60, 40]
    labels = ['Stocks', 'Bonds']
    title = "Stocks vs Bonds Allocation"
    fig = visualizer.generate_pie_chart(sizes, labels, title)

    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    ax = fig.axes[0]
    assert ax.get_title() == title
    # Basic check for patches (pie wedges)
    assert len(ax.patches) == len(sizes)

    plt.close(fig) # Close the figure to free up memory

def test_generate_historical_performance_chart():
    """Tests the generate_historical_performance_chart function."""
    dates = pd.to_datetime(['2020-01-01', '2021-01-01', '2022-01-01', '2023-01-01'])
    returns = pd.Series([0, 0.1, 0.15, 0.2], index=dates)
    fig = visualizer.generate_historical_performance_chart(returns)

    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    ax = fig.axes[0]
    assert ax.get_title() == "Historical Cumulative Returns"
    assert ax.get_xlabel() == "Date"
    assert ax.get_ylabel() == "Cumulative Return"
    # Basic check for lines
    assert len(ax.lines) > 0

    plt.close(fig) # Close the figure to free up memory

from unittest.mock import patch, MagicMock

@patch('visualizer.st') # Mock the streamlit module
@patch('visualizer.pd') # Mock the pandas module
def test_display_portfolio_details_table(mock_pd, mock_st):
    """Tests the display_portfolio_details_table function."""
    # Mock input data
    portfolio_metrics = {
        "Yield": 0.0185,
        "Expense Ratio": 0.00045,
        "Beta": 0.85
    }
    portfolio_returns = {
        "1mo": 0.01,
        "ytd": 0.05,
        "1y": 0.12,
        "max": 2.5
    }

    # Define the expected table data structure
    expected_table_data = {
        "Metric": [
            "Yield",
            "Expense Ratio",
            "Beta",
            "1 Month Return",
            "YTD Return",
            "1 Year Return",
            "Max Return"
        ],
            "Value": [
                "0.0185%", # Expected formatted string
                    "0.0004%", # Expected formatted string (rounding difference from 0.00045)
                "0.85",    # Expected formatted string
                "1.00%",   # Expected formatted string
                "5.00%",   # Expected formatted string
                "12.00%",  # Expected formatted string
                "250.00%"  # Expected formatted string
            ]
        }

    # Mock the DataFrame creation
    mock_df_instance = MagicMock()
    mock_pd.DataFrame.return_value = mock_df_instance

    # Call the function
    visualizer.display_portfolio_details_table(portfolio_metrics, portfolio_returns)

    # Assert that st.subheader was called
    mock_st.subheader.assert_called_once_with("Selected Portfolio Details")

    # Assert that pd.DataFrame was called with the correct data
    mock_pd.DataFrame.assert_called_once_with(expected_table_data)

    # Assert that st.table was called with the created DataFrame
    mock_st.table.assert_called_once_with(mock_df_instance)

# Note: Testing the exact formatting of floats in the 'Value' list can be tricky due to
# potential floating-point inaccuracies and formatting differences. The current assertion
# uses hardcoded expected strings based on the formatting logic in visualizer.py.
# If formatting logic changes, these expected strings will need to be updated.
# A more robust approach might involve checking the raw values before formatting,
# but this test specifically targets the display function's output structure and formatting.
# For now, this level of assertion is sufficient.
