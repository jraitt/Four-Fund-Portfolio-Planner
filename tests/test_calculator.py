import sys
import os
# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import pytest
import pandas as pd
import numpy as np
import calculator
from unittest.mock import patch # Import patch

def test_calculate_allocations():
    """Tests the calculate_allocations function."""
    allocations = calculator.calculate_allocations(60, 30, 20)
    assert isinstance(allocations, dict)
    assert allocations["VTI"] == 60 * (100 - 30) / 100
    assert allocations["VEA"] == 60 * 30 / 100
    assert allocations["BND"] == 40 * (100 - 20) / 100
    assert allocations["BNDX"] == 40 * 20 / 100
    assert sum(allocations.values()) == pytest.approx(100.0)

def test_calculate_portfolio_returns():
    """Tests the calculate_portfolio_returns function."""
    historical_data = pd.DataFrame({
        'VTI': [100, 101, 102, 103, 104],
        'VEA': [50, 51, 52, 53, 54],
        'BND': [20, 20.1, 20.2, 20.3, 20.4],
        'BNDX': [10, 10.05, 10.1, 10.15, 10.2]
    })
    allocations = {"VTI": 40, "VEA": 30, "BND": 20, "BNDX": 10}
    portfolio_returns = calculator.calculate_portfolio_returns(historical_data, allocations)

    assert isinstance(portfolio_returns, pd.Series)
    assert not portfolio_returns.empty
    # The first return should be the weighted average of the first non-NaN daily returns
    # Calculated as: 0.01*0.4 + 0.02*0.3 + 0.005*0.2 + 0.005*0.1 = 0.0115
    assert portfolio_returns.iloc[0] == pytest.approx(0.0115)

def test_calculate_cumulative_returns():
    """Tests the calculate_cumulative_returns function."""
    daily_returns = pd.Series([0.01, 0.005, -0.002, 0.015])
    cumulative_returns = calculator.calculate_cumulative_returns(daily_returns)

    assert isinstance(cumulative_returns, pd.Series)
    assert not cumulative_returns.empty
    assert cumulative_returns.iloc[0] == pytest.approx(0.01)
    assert cumulative_returns.iloc[1] == pytest.approx((1 + 0.01) * (1 + 0.005) - 1)
    assert cumulative_returns.iloc[3] == (1 + 0.01) * (1 + 0.005) * (1 - 0.002) * (1 + 0.015) - 1

def test_calculate_volatility():
    """Tests the calculate_volatility function."""
    # Sample data with known standard deviation
    daily_returns = pd.Series(np.random.randn(252) * 0.01) # Simulate 1 year of daily returns with std dev 0.01
    volatility = calculator.calculate_volatility(daily_returns)

    assert isinstance(volatility, float)
    assert volatility >= 0

def test_calculate_sharpe_ratio():
    """Tests the calculate_sharpe_ratio function."""
    # Sample data with a positive average return
    daily_returns = pd.Series(np.random.randn(252) * 0.01 + 0.0005) # Simulate positive drift
    sharpe_ratio = calculator.calculate_sharpe_ratio(daily_returns, risk_free_rate=0.01)

    assert isinstance(sharpe_ratio, float)

def test_project_future_value():
    """Tests the project_future_value function."""
    daily_returns = pd.Series([0.001] * 252) # Simulate constant daily return
    current_value = 1000.0
    years = 5
    projected_value = calculator.project_future_value(daily_returns, current_value, years)

    annualized_return = 0.001 * 252
    expected_value = current_value * (1 + annualized_return)**years

    assert isinstance(projected_value, float)
    assert projected_value == pytest.approx(expected_value)

def test_calculate_portfolio_composite_metrics():
    """Tests the calculate_portfolio_composite_metrics function."""
    # Mock fund details data
    fund_details_list = [
        {"symbol": "VTI", "yield": 0.015, "expense_ratio": 0.0003, "beta": 1.0},
        {"symbol": "VEA", "yield": 0.018, "expense_ratio": 0.0005, "beta": 1.1},
        {"symbol": "BND", "yield": 0.020, "expense_ratio": 0.0004, "beta": 0.05},
        {"symbol": "BNDX", "yield": 0.022, "expense_ratio": 0.0006, "beta": 0.1}
    ]
    # Mock allocations
    allocations = {"VTI": 40, "VEA": 30, "BND": 20, "BNDX": 10} # Sums to 100

    # Calculate expected weighted metrics
    total_allocation = sum(allocations.values()) / 100.0 # 1.0
    expected_yield = (0.015 * 0.4) + (0.018 * 0.3) + (0.020 * 0.2) + (0.022 * 0.1)
    expected_expense_ratio = (0.0003 * 0.4) + (0.0005 * 0.3) + (0.0004 * 0.2) + (0.0006 * 0.1)
    expected_beta = (1.0 * 0.4) + (1.1 * 0.3) + (0.05 * 0.2) + (0.1 * 0.1)

    # Call the function
    composite_metrics = calculator.calculate_portfolio_composite_metrics(fund_details_list, allocations)

    # Assert the results
    assert isinstance(composite_metrics, dict)
    assert composite_metrics.get("Yield") == pytest.approx(expected_yield / total_allocation)
    assert composite_metrics.get("Expense Ratio") == pytest.approx(expected_expense_ratio / total_allocation)
    assert composite_metrics.get("Beta") == pytest.approx(expected_beta / total_allocation)

def test_calculate_portfolio_composite_metrics_missing_data():
    """Tests calculate_portfolio_composite_metrics with missing data."""
    fund_details_list = [
        {"symbol": "VTI", "yield": 0.015, "expense_ratio": 0.0003, "beta": 1.0},
        {"symbol": "VEA", "yield": None, "expense_ratio": 0.0005, "beta": 1.1}, # Missing yield
        {"symbol": "BND", "yield": 0.020, "expense_ratio": np.nan, "beta": 0.05}, # Missing expense_ratio
        {"symbol": "BNDX", "yield": 0.022, "expense_ratio": 0.0006, "beta": None} # Missing beta
    ]
    allocations = {"VTI": 25, "VEA": 25, "BND": 25, "BNDX": 25} # Sums to 100

    # Calculate expected weighted metrics, excluding missing data
    # Yield: (0.015 * 0.25) + (0.020 * 0.25) + (0.022 * 0.25) / (0.25 + 0.25 + 0.25) = (0.00375 + 0.005 + 0.0055) / 0.75 = 0.01425 / 0.75 = 0.019
    expected_yield = (0.015 * 0.25 + 0.020 * 0.25 + 0.022 * 0.25) / 0.75
    # Expense Ratio: (0.0003 * 0.25) + (0.0005 * 0.25) + (0.0006 * 0.25) / (0.25 + 0.25 + 0.25) = (0.000075 + 0.000125 + 0.00015) / 0.75 = 0.00035 / 0.75 = 0.000466...
    expected_expense_ratio = (0.0003 * 0.25 + 0.0005 * 0.25 + 0.0006 * 0.25) / 0.75
    # Beta: (1.0 * 0.25) + (1.1 * 0.25) + (0.05 * 0.25) / (0.25 + 0.25 + 0.25) = (0.25 + 0.275 + 0.0125) / 0.75 = 0.5375 / 0.75 = 0.7166...
    expected_beta = (1.0 * 0.25 + 1.1 * 0.25 + 0.05 * 0.25) / 0.75


    # Call the function
    composite_metrics = calculator.calculate_portfolio_composite_metrics(fund_details_list, allocations)

    # Assert the results
    assert isinstance(composite_metrics, dict)
    assert composite_metrics.get("Yield") == pytest.approx(expected_yield)
    assert composite_metrics.get("Expense Ratio") == pytest.approx(expected_expense_ratio)
    assert composite_metrics.get("Beta") == pytest.approx(expected_beta)

def test_calculate_portfolio_composite_metrics_zero_allocation():
    """Tests calculate_portfolio_composite_metrics with zero allocation."""
    fund_details_list = [
        {"symbol": "VTI", "yield": 0.015, "expense_ratio": 0.0003, "beta": 1.0},
        {"symbol": "VEA", "yield": 0.018, "expense_ratio": 0.0005, "beta": 1.1},
    ]
    allocations = {"VTI": 0, "VEA": 0, "BND": 0, "BNDX": 0} # Zero allocation

    composite_metrics = calculator.calculate_portfolio_composite_metrics(fund_details_list, allocations)

    assert isinstance(composite_metrics, dict)
    assert composite_metrics.get("Yield") == 0.0
    assert composite_metrics.get("Expense Ratio") == 0.0
    assert composite_metrics.get("Beta") == 0.0

def test_calculate_portfolio_period_return_ytd():
    """Tests the calculate_portfolio_period_return function for YTD."""
    # Create daily returns data spanning across a year boundary
    dates = pd.to_datetime(['2022-12-29', '2022-12-30', '2023-01-03', '2023-01-04', '2023-01-05'])
    daily_returns = pd.Series([0.001, 0.002, 0.005, -0.001, 0.003], index=dates)

    # Calculate YTD return for 2023
    ytd_return = calculator.calculate_portfolio_period_return(daily_returns, "ytd")

    # Expected YTD return for 2023: (1+0.005)*(1-0.001)*(1+0.003) - 1
    expected_ytd_return = (1 + 0.005) * (1 - 0.001) * (1 + 0.003) - 1

    assert ytd_return == pytest.approx(expected_ytd_return)

def test_calculate_portfolio_period_return_ytd_no_data_current_year():
    """Tests calculate_portfolio_period_return for YTD when no data in current year."""
    dates = pd.to_datetime(['2022-12-29', '2022-12-30'])
    daily_returns = pd.Series([0.001, 0.002], index=dates)

    ytd_return = calculator.calculate_portfolio_period_return(daily_returns, "ytd")

    # The test data ends in 2022, so YTD should be calculated for 2022
    # Expected YTD return for 2022: (1+0.001)*(1+0.002) - 1
    expected_ytd_return = (1 + 0.001) * (1 + 0.002) - 1

    assert ytd_return == pytest.approx(expected_ytd_return) # Update assertion

def test_calculate_individual_fund_period_return_ytd():
    """Tests the calculate_individual_fund_period_return function for YTD."""
    # Create price data spanning across a year boundary
    dates = pd.to_datetime(['2022-12-29', '2022-12-30', '2023-01-03', '2023-01-04', '2023-01-05'])
    prices = pd.Series([100, 101, 101.5, 101.4, 101.7], index=dates)

    # Calculate YTD return for 2023
    ytd_return = calculator.calculate_individual_fund_period_return(prices, "ytd")

    # Expected YTD return for 2023: (End price / Price on last trading day of previous year) - 1
    # End price is on 2023-01-05 (101.7), Price on last trading day of 2022 is on 2022-12-30 (101)
    expected_ytd_return = (101.7 / 101) - 1

    assert ytd_return == pytest.approx(expected_ytd_return)

def test_calculate_individual_fund_period_return_ytd_no_data_current_year():
    """Tests calculate_individual_fund_period_return for YTD when no data in current year."""
    dates = pd.to_datetime(['2022-12-29', '2022-12-30'])
    prices = pd.Series([100, 101], index=dates)

    ytd_return = calculator.calculate_individual_fund_period_return(prices, "ytd")

    # If no data in the current year, YTD should be calculated from the first available data point.
    # Start price is on 2022-12-29 (100), End price is on 2022-12-30 (101)
    expected_ytd_return = (101 / 100) - 1

    assert ytd_return == pytest.approx(expected_ytd_return)

def test_calculate_all_portfolio_returns():
    """Tests the calculate_all_portfolio_returns function."""
    # Mock daily returns data
    dates = pd.to_datetime(pd.date_range(start='2010-01-01', periods=3000, freq='B')) # Business days
    daily_returns = pd.Series(np.random.randn(3000) * 0.005, index=dates) # Random daily returns

    # Mock calculate_portfolio_period_return to check if it's called correctly
    with patch('calculator.calculate_portfolio_period_return') as mock_period_return:
        mock_period_return.side_effect = lambda returns, period: f"mock_return_{period}" # Return a distinct value for each period

        all_returns = calculator.calculate_all_portfolio_returns(daily_returns)

        # Define the expected periods
        expected_periods = ["1mo", "3mo", "6mo", "ytd", "1y", "3y", "5y", "10y", "max"]

        # Assert that calculate_portfolio_period_return was called for each expected period
        assert mock_period_return.call_count == len(expected_periods)
        called_periods = [call_args[0][1] for call_args in mock_period_return.call_args_list]
        assert sorted(called_periods) == sorted(expected_periods)

        # Assert the returned dictionary has the correct keys and values from the mock
        assert isinstance(all_returns, dict)
        assert sorted(list(all_returns.keys())) == sorted(expected_periods)
        for period in expected_periods:
            assert all_returns[period] == f"mock_return_{period}"
