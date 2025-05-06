import sys
import os
# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import pytest
import pandas as pd
import numpy as np
import calculator

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
    # Basic check: the first return should be NaN due to pct_change()
    assert np.isnan(portfolio_returns.iloc[0])

def test_calculate_cumulative_returns():
    """Tests the calculate_cumulative_returns function."""
    daily_returns = pd.Series([0.01, 0.005, -0.002, 0.015])
    cumulative_returns = calculator.calculate_cumulative_returns(daily_returns)

    assert isinstance(cumulative_returns, pd.Series)
    assert not cumulative_returns.empty
    assert cumulative_returns.iloc[0] == 0.01
    assert cumulative_returns.iloc[1] == (1 + 0.01) * (1 + 0.005) - 1
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
