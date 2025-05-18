import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset

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

def calculate_portfolio_composite_metrics(fund_details_list: list[dict], allocations: dict) -> dict:
    """
    Calculates weighted average yield, expense ratio, and beta for the portfolio.

    Args:
        fund_details_list (list[dict]): A list of dictionaries, each containing fund details.
        allocations (dict): Dictionary with ticker symbols as keys and allocation percentages (0-100) as values.

    Returns:
        dict: A dictionary with weighted 'Yield', 'Expense Ratio', and 'Beta'.
              Returns NaN for a metric if data is missing for any allocated fund.
    """
    total_allocation = sum(allocations.values())
    if total_allocation == 0:
        return {"Yield": 0.0, "Expense Ratio": 0.0, "Beta": 0.0}

    weighted_yield = 0.0
    weighted_expense_ratio = 0.0
    weighted_beta = 0.0
    valid_allocation_sum_yield = 0.0
    valid_allocation_sum_er = 0.0
    valid_allocation_sum_beta = 0.0

    for fund_details in fund_details_list:
        ticker = fund_details.get("symbol")
        if ticker in allocations:
            allocation_percent = allocations[ticker] / 100.0 # Convert to decimal

            # Calculate weighted yield, handling missing data
            fund_yield = fund_details.get("yield")
            if fund_yield is not None and not np.isnan(fund_yield):
                weighted_yield += fund_yield * allocation_percent
                valid_allocation_sum_yield += allocation_percent
            # Reason: Accumulate weighted yield only if fund yield data is available.

            # Calculate weighted expense ratio, handling missing data
            fund_er = fund_details.get("expense_ratio")
            if fund_er is not None and not np.isnan(fund_er):
                weighted_expense_ratio += fund_er * allocation_percent
                valid_allocation_sum_er += allocation_percent
            # Reason: Accumulate weighted expense ratio only if fund expense ratio data is available.

            # Calculate weighted beta, handling missing data
            fund_beta = fund_details.get("beta")
            if fund_beta is not None and not np.isnan(fund_beta):
                weighted_beta += fund_beta * allocation_percent
                valid_allocation_sum_beta += allocation_percent
            # Reason: Accumulate weighted beta only if fund beta data is available.


    # Normalize by the sum of allocations for funds where data was available for that metric
    # This handles cases where some funds have missing data for certain metrics
    final_yield = weighted_yield / valid_allocation_sum_yield if valid_allocation_sum_yield > 0 else np.nan
    final_expense_ratio = weighted_expense_ratio / valid_allocation_sum_er if valid_allocation_sum_er > 0 else np.nan
    final_beta = weighted_beta / valid_allocation_sum_beta if valid_allocation_sum_beta > 0 else np.nan
    # Reason: Calculate final weighted average, returning NaN if no valid data was included in the sum.


    return {
        "Yield": final_yield,
        "Expense Ratio": final_expense_ratio,
        "Beta": final_beta
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
    elif period_label == "ytd":
        # Calculate Year-to-Date return
        end_year = end_date.year

        # Calculate Year-to-Date return using the last trading day of the previous year as the base
        start_of_current_year = pd.Timestamp(f'{end_year}-01-01')
        # Find the last trading day of the previous year
        previous_year_end_date_series = prices.loc[prices.index < start_of_current_year]

        if previous_year_end_date_series.empty:
            # If no data in the previous year, use the first available data point in the current year
            current_year_start_date_series = prices.loc[prices.index >= start_of_current_year]
            if current_year_start_date_series.empty:
                return None # No data points in the current year
            start_price = current_year_start_date_series.iloc[0]
        else:
            start_price = previous_year_end_date_series.iloc[-1]

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

        # Find the closest trading day on or before the target_start_date
        start_date_series = prices.loc[prices.index <= target_start_date]

        if start_date_series.empty:
            return None # Not enough historical data for the period

        # Use the price from the trading day *before* the start of the period
        # If the target_start_date is the very first date, use that date's price
        if start_date_series.index[-1] == prices.index[0]:
             start_price = start_date_series.iloc[-1]
        else:
            # Find the index of the closest date on or before target_start_date
            closest_date_index = prices.index.get_loc(start_date_series.index[-1])
            # Get the price from the day before
            start_price = prices.iloc[closest_date_index - 1]


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
    elif period_label == "ytd":
        # Calculate Year-to-Date return
        end_year = end_date.year

        # Check if there is any data within the current calendar year
        if not any(date.year == end_year for date in daily_portfolio_returns.index):
            return None # No data points in the current year

        start_of_year = pd.Timestamp(f'{end_year}-01-01')
        # Find the first trading day on or after the start of the year
        ytd_start_date = daily_portfolio_returns.index[daily_portfolio_returns.index >= start_of_year].min()

        # If ytd_start_date is NaN, it means there's no data from the start of the year onwards in the current year
        if pd.isna(ytd_start_date):
             return None

        # Select daily returns from the start of the year to the end date
        relevant_daily_returns = daily_portfolio_returns.loc[daily_portfolio_returns.index >= ytd_start_date]

        # This check might be redundant now, but keep for safety
        if relevant_daily_returns.empty:
             return None

        cumulative_returns_period = (1 + relevant_daily_returns).cumprod() - 1
        return cumulative_returns_period.iloc[-1]

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

        # Find the closest trading day on or before the target_start_date
        start_date_series = daily_portfolio_returns.loc[daily_portfolio_returns.index <= target_start_date]

        if start_date_series.empty:
            return None # Not enough historical data for the period

        actual_start_date = start_date_series.index[-1]

        # Select daily returns from the actual start date to the end date (inclusive)
        relevant_daily_returns = daily_portfolio_returns.loc[daily_portfolio_returns.index >= actual_start_date]

        if relevant_daily_returns.empty:
             return None # Should not happen if actual_start_date was found, but for safety

        # Calculate cumulative returns for the period
        # Need to adjust the calculation slightly since we are including the start date's return
        # The cumulative product should start from 1 before multiplying by (1 + returns)
        cumulative_returns_period = (1 + relevant_daily_returns).cumprod() - 1
        return cumulative_returns_period.iloc[-1]

def calculate_all_portfolio_returns(daily_portfolio_returns: pd.Series) -> dict:
    """
    Calculates portfolio returns for a predefined set of periods.

    Args:
        daily_portfolio_returns (pd.Series): Series of daily returns for the portfolio (indexed by Date).

    Returns:
        dict: A dictionary with period labels as keys and calculated returns as values.
    """
    periods = ["1mo", "3mo", "6mo", "ytd", "1y", "3y", "5y", "10y", "max"]
    returns = {}
    for period in periods:
        returns[period] = calculate_portfolio_period_return(daily_portfolio_returns, period)
    return returns


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
