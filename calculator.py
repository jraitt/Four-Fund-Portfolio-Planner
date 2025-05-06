import pandas as pd
import numpy as np

def calculate_allocations(total_stocks_allocation: float, international_stocks_allocation_within_stocks: float, international_bonds_allocation_within_bonds: float) -> dict:
    """
    Calculates the specific allocation percentages for each of the four funds.

    Args:
        total_stocks_allocation (float): The overall percentage allocated to stocks (0-100).
        international_stocks_allocation_within_stocks (float): The percentage of the stock allocation allocated to international stocks (0-100).
        international_bonds_allocation_within_bonds (float): The percentage of the bond allocation allocated to international bonds (0-100).

    Returns:
        dict: A dictionary with keys 'VTI', 'VEA', 'BND', 'BNDX' and their respective allocation percentages (0-100).
    """
    total_bonds_allocation = 100 - total_stocks_allocation

    us_stocks_allocation = total_stocks_allocation * (100 - international_stocks_allocation_within_stocks) / 100
    international_stocks_allocation_portfolio = total_stocks_allocation * international_stocks_allocation_within_stocks / 100
    us_bonds_allocation = total_bonds_allocation * (100 - international_bonds_allocation_within_bonds) / 100
    international_bonds_allocation_portfolio = total_bonds_allocation * international_bonds_allocation_within_bonds / 100

    return {
        "VTI": us_stocks_allocation,
        "VEA": international_stocks_allocation_portfolio,
        "BND": us_bonds_allocation,
        "BNDX": international_bonds_allocation_portfolio
    }

def calculate_portfolio_returns(historical_data: pd.DataFrame, allocations: dict) -> pd.Series:
    """
    Calculates the daily returns for the portfolio based on historical data and allocations.

    Args:
        historical_data (pd.DataFrame): DataFrame with historical adjusted close prices for each ticker.
        allocations (dict): Dictionary with ticker symbols as keys and allocation percentages (0-100) as values.

    Returns:
        pd.Series: Series containing the daily returns of the portfolio.
    """
    if historical_data.empty or not allocations:
        return pd.Series()

    # Calculate daily returns for individual assets
    # Calculate daily returns for individual assets, explicitly setting fill_method=None
    daily_returns = historical_data.pct_change(fill_method=None).dropna()

    # Ensure tickers in allocations match columns in daily_returns
    valid_tickers = [ticker for ticker in allocations if ticker in daily_returns.columns]
    if not valid_tickers:
        return pd.Series()

    # Create a Series of weights, ensuring they sum to 1
    total_allocation = sum(allocations[ticker] for ticker in valid_tickers)
    if total_allocation == 0:
        weights = pd.Series({ticker: 0 for ticker in valid_tickers})
    else:
        weights = pd.Series({ticker: allocations[ticker] / total_allocation for ticker in valid_tickers})

    # Calculate portfolio daily returns
    portfolio_daily_returns = daily_returns[valid_tickers].dot(weights)

    return portfolio_daily_returns

def calculate_cumulative_returns(daily_returns: pd.Series) -> pd.Series:
    """
    Calculates the cumulative returns from a series of daily returns.

    Args:
        daily_returns (pd.Series): Series containing the daily returns of the portfolio.

    Returns:
        pd.Series: Series containing the cumulative returns.
    """
    if daily_returns.empty:
        return pd.Series()

    cumulative_returns = (1 + daily_returns).cumprod() - 1
    return cumulative_returns

def calculate_volatility(daily_returns: pd.Series) -> float:
    """
    Calculates the annualized volatility (standard deviation) of daily returns.

    Args:
        daily_returns (pd.Series): Series containing the daily returns of the portfolio.

    Returns:
        float: Annualized volatility. Returns 0 if daily_returns is empty.
    """
    if daily_returns.empty:
        return 0.0

    # Annualize volatility (assuming 252 trading days in a year)
    annualized_volatility = daily_returns.std() * np.sqrt(252)
    return annualized_volatility

def calculate_sharpe_ratio(daily_returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """
    Calculates the annualized Sharpe Ratio.

    Args:
        daily_returns (pd.Series): Series containing the daily returns of the portfolio.
        risk_free_rate (float): The annualized risk-free rate. Defaults to 0.0.

    Returns:
        float: Annualized Sharpe Ratio. Returns 0 if volatility is 0 or daily_returns is empty.
    """
    if daily_returns.empty:
        return 0.0

    annualized_return = daily_returns.mean() * 252
    annualized_volatility = calculate_volatility(daily_returns)

    if annualized_volatility == 0:
        return 0.0

    sharpe_ratio = (annualized_return - risk_free_rate) / annualized_volatility
    return sharpe_ratio

def project_future_value(daily_returns: pd.Series, current_value: float, years: int) -> float:
    """
    Projects the future value of an investment based on historical annualized return.

    Args:
        daily_returns (pd.Series): Series containing the daily returns of the portfolio.
        current_value (float): The current value of the investment.
        years (int): The number of years to project into the future.

    Returns:
        float: The projected future value. Returns current_value if daily_returns is empty.
    """
    if daily_returns.empty or years <= 0:
        return current_value

    annualized_return = daily_returns.mean() * 252
    projected_value = current_value * (1 + annualized_return)**years

    return projected_value

from pandas.tseries.offsets import DateOffset

def calculate_individual_fund_period_return(prices: pd.Series, period_label: str) -> float | None:
    """
    Calculates the percentage return for a single fund over a specified period.

    Args:
        prices (pd.Series): Series of historical close prices for a single fund (indexed by Date).
        period_label (str): The period label (e.g., "1mo", "1y", "max").

    Returns:
        float | None: The percentage return for the period, or None if data is insufficient.
    """
    if prices.empty:
        return None

    prices = prices.sort_index() # Ensure prices are sorted by date
    end_date = prices.index[-1]
    end_price = prices.iloc[-1]

    if period_label == "max":
        start_price = prices.iloc[0]
        return (end_price / start_price) - 1
    else:
        offset = None
        if period_label == "1mo":
            offset = DateOffset(months=1)
        elif period_label == "3mo":
            offset = DateOffset(months=3)
        elif period_label == "6mo":
            offset = DateOffset(months=6)
        elif period_label == "1y":
            offset = DateOffset(years=1)
        elif period_label == "2y":
            offset = DateOffset(years=2)
        elif period_label == "5y":
            offset = DateOffset(years=5)
        elif period_label == "10y":
            offset = DateOffset(years=10)
        else:
            return None # Invalid period label

        target_start_date = end_date - offset

        # Find the price at the closest date on or before the target_start_date
        start_price_series = prices.loc[prices.index <= target_start_date]

        if start_price_series.empty:
            return None # Not enough historical data for the period

        start_price = start_price_series.iloc[-1]

        return (end_price / start_price) - 1

def calculate_portfolio_period_return(daily_portfolio_returns: pd.Series, period_label: str) -> float | None:
    """
    Calculates the cumulative return for the portfolio over a specified period.

    Args:
        daily_portfolio_returns (pd.Series): Series of daily returns for the portfolio (indexed by Date).
        period_label (str): The period label (e.g., "1mo", "1y", "max").

    Returns:
        float | None: The cumulative percentage return for the period, or None if data is insufficient.
    """
    if daily_portfolio_returns.empty:
        return None

    daily_portfolio_returns = daily_portfolio_returns.sort_index() # Ensure sorted by date
    end_date = daily_portfolio_returns.index[-1]

    if period_label == "max":
        cumulative_returns = (1 + daily_portfolio_returns).cumprod() - 1
        return cumulative_returns.iloc[-1]
    else:
        offset = None
        if period_label == "1mo":
            offset = DateOffset(months=1)
        elif period_label == "3mo":
            offset = DateOffset(months=3)
        elif period_label == "6mo":
            offset = DateOffset(months=6)
        elif period_label == "1y":
            offset = DateOffset(years=1)
        elif period_label == "2y":
            offset = DateOffset(years=2)
        elif period_label == "5y":
            offset = DateOffset(years=5)
        elif period_label == "10y":
            offset = DateOffset(years=10)
        else:
            return None # Invalid period label

        target_start_date = end_date - offset

        # Select daily returns within the period
        relevant_daily_returns = daily_portfolio_returns.loc[daily_portfolio_returns.index > target_start_date]

        if relevant_daily_returns.empty:
            return None # Not enough historical data for the period

        cumulative_returns_period = (1 + relevant_daily_returns).cumprod() - 1
        return cumulative_returns_period.iloc[-1]


# Historical stock vs bond allocation return data (Max, Avg, Min annual returns)
# Data provided by user for 10% stock allocation increments
_stock_bond_returns_data = pd.DataFrame({
    'Stocks_Percent': [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
    'Max_Return': [32.6, 31.2, 29.8, 28.4, 27.9, 32.3, 36.7, 41.1, 45.4, 49.8, 54.2],
    'Avg_Return': [5.3, 5.9, 6.5, 7.1, 7.7, 8.2, 8.8, 9.3, 9.7, 10.1, 10.4],
    'Min_Return': [-8.1, -8.2, -10.1, -14.2, -18.4, -22.5, -26.6, -30.7, -34.9, -39.0, -43.1]
})

def interpolate_returns(stock_allocation_percent: float) -> dict:
    """
    Interpolates Max, Avg, and Min annual returns for a given stock allocation percentage.

    Args:
        stock_allocation_percent (float): The percentage of the portfolio allocated to stocks (0-100).

    Returns:
        dict: A dictionary with interpolated 'Max_Return', 'Avg_Return', and 'Min_Return'.
              Returns the nearest data point if the allocation is outside the 0-100 range.
    """
    if stock_allocation_percent < 0:
        return _stock_bond_returns_data.iloc[0][['Max_Return', 'Avg_Return', 'Min_Return']].to_dict()
    if stock_allocation_percent > 100:
        return _stock_bond_returns_data.iloc[-1][['Max_Return', 'Avg_Return', 'Min_Return']].to_dict()

    # Use pandas interpolation
    interpolated_data = {}
    for col in ['Max_Return', 'Avg_Return', 'Min_Return']:
        interpolated_value = np.interp(
            stock_allocation_percent,
            _stock_bond_returns_data['Stocks_Percent'],
            _stock_bond_returns_data[col]
        )
        interpolated_data[col] = interpolated_value

    return interpolated_data


if __name__ == '__main__':
    # Example Usage (requires fetching historical data first)
    # This part would typically be run in your main app after fetching data
    pass
