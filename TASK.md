# Four Fund Portfolio Planner - Task List

This document outlines the tasks required to build the Four Fund Portfolio Planner web application.

## Core Functionality

- [x] **Setup Project Environment:**
    - [x] Create `requirements.txt` with necessary dependencies (streamlit, yfinance, pandas, matplotlib, numpy, scikit-learn).
    - [x] Set up a virtual environment.
    - [x] Install dependencies.
- [x] **Data Fetching:**
    - [x] Implement a module (`data_fetcher.py`) to fetch fund data (details and historical prices) from Yahoo Finance using `yfinance`.
    - [x] Implement data caching to improve performance.
    - [x] Handle potential API errors or missing data.
- [x] **User Interface (Streamlit):**
    - [x] Create the main application file (`app.py`).
    - [x] Implement sliders for user inputs (Total Stocks %, International Stocks %, International Bonds %).
    - [x] Display fund details in a table.
    - [x] Display allocation pie charts.
    - [x] Display historical performance graph.
- [x] **Portfolio Calculation Engine:**
    - [x] Implement a module (`calculator.py`) to calculate fund allocations based on user inputs.
    - [x] Calculate weighted historical returns for the portfolio.
    - [x] Calculate risk metrics (volatility, Sharpe Ratio).
    - [x] Implement a simple projection model.
- [x] **Visualization:**
    - [x] Implement a module (`visualizer.py`) to generate the required charts using matplotlib or plotly.
    - [x] Integrate visualizations into the Streamlit app.

## Additional Features

- [ ] **Save/Load Portfolios:**
    - [ ] Implement functionality to save the current portfolio configuration.
    - [ ] Implement functionality to load saved portfolio configurations.
- [ ] **Portfolio Comparison:**
    - [ ] Implement a UI section to define multiple portfolios.
    - [ ] Display a comparison table or chart of key metrics and performance for selected portfolios.
- [x] **Add 1-week (1w) returns to Period Returns table:**
    - [x] Update `app.py` to include "1w" in the `PERIODS` list.
    - [x] Update `calculator.py` to handle "1w" period for individual fund and portfolio returns.

## Testing

- [x] **Unit Tests:**
    - [x] Write unit tests for the `data_fetcher.py` module.
    - [x] Write unit tests for the `calculator.py` module.
    - [x] Write unit tests for the `visualizer.py` module (data preparation).
- [ ] **Integration Tests:**
    - [ ] (Optional) Write integration tests for key components.

## Documentation

- [x] Update `README.md` with final installation and usage instructions.
- [x] Update `PLANNING.md` with any changes or refinements made during development.
- [x] Add docstrings and inline comments to the code.

## Allow manual update of historical data even if less than 31 days old

- [x] Add `force_update: bool = False` parameter to `data_fetcher.update_historical_data`.
- [x] In `app.py`, add a 'Force Update Historical Data' button.
- [x] Implement logic in `app.py` for the new button to call `update_historical_data` with `force_update=True`, bypassing the 31-day check.
- [x] Ensure existing unit tests for `data_fetcher.update_historical_data` pass and add new ones if the `force_update` flag implies different internal behavior (though not expected for this iteration).
- [x] Update `README.md` to mention the new manual update button.

## Discovered During Work

- [x] Add 'Selected Portfolio Details' table (Yield, ER, Beta, Period Returns) below 'Fund Details' table. (Date: 2025-05-07)
- [x] Change orientation of "Period Returns (%)" table in `app.py` so periods are columns and tickers/portfolio are rows. (Date: 2025-05-15)
- [x] Add YTD calculation based on historical data and add it to the "Period Returns" table. (Date: 2025-05-16)
- [ ] When 100% stocks, 0% US stocks, the periods return table portfolio row should mirror the "VTI" row. (Date: 2025-05-18)
- [ ] Fix "inf" values in `daily_portfolio_returns` for 2013-06-04, likely caused by division by zero when calculating percentage change due to missing historical data for BNDX. (Date: 2025-05-20)
(Add any new tasks or TODOs discovered during development here)

## Completed Tasks

- [x] Convert Matplotlib pie charts to Plotly donut charts in `visualizer.py` and `app.py` (Date: 2025-05-07)

- [x] Replace Matplotlib cumulative returns chart with an interactive Plotly chart in `visualizer.py` and `app.py` (Date: 2025-05-07)
    - [x] Add `plotly` to `requirements.txt` (Date: 2025-05-07)

- [x] Create `README.md`
- [x] Create `PLANNING.md`
- [x] Create `TASK.md`
- [x] Add Historic Stock vs. Bonds Returns table with interpolation
- [x] Fix NameError for portfolio_daily_returns in app.py (Date: 2025-05-07)
- [x] Fix failing tests in tests/test_calculator.py and tests/test_visualizer.py (Date: 2025-05-07)
- [x] Modify `app.py` to use `visualizer.generate_historical_performance_chart` for the cumulative returns display with correct title and Y-axis percentage formatting (Date: 2025-05-07)
- [x] In `data_fetcher.py`, ensure `load_historical_data` includes all dates and fills missing fund values with "0.0". (Date: 2025-05-19)

## Persistent Historical Data Storage & Update

- [x] Implement CSV storage for historical fund data (data/historical_fund_data.csv)
- [x] Create data_fetcher.fetch_and_store_max_history function
- [x] Create data_fetcher.get_last_data_date function
- [x] Create data_fetcher.update_historical_data function
- [x] Create data_fetcher.load_historical_data function
- [x] Integrate app-triggered update logic in app.py (check on load, prompt user)
- [x] Update app to use data_fetcher.load_historical_data for charts/calculations
- [x] Add unit tests for new data_fetcher functions
