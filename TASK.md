# Four Fund Portfolio Planner - Task List

This document outlines the tasks required to build the Four Fund Portfolio Planner web application.

## Core Functionality

- [x] **Setup Project Environment:**
    - [x] Create `requirements.txt` with necessary dependencies (streamlit, yfinance, pandas, matplotlib, numpy, scikit-learn).
    - [ ] Set up a virtual environment.
    - [ ] Install dependencies.
- [x] **Data Fetching:**
    - [x] Implement a module (`data_fetcher.py`) to fetch fund data (details and historical prices) from Yahoo Finance using `yfinance`.
    - [x] Implement data caching to improve performance.
    - [ ] Handle potential API errors or missing data.
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

## Testing

- [ ] **Unit Tests:**
    - [ ] Write unit tests for the `data_fetcher.py` module.
    - [ ] Write unit tests for the `calculator.py` module.
    - [ ] Write unit tests for the `visualizer.py` module (data preparation).
- [ ] **Integration Tests:**
    - [ ] (Optional) Write integration tests for key components.

## Documentation

- [ ] Update `README.md` with final installation and usage instructions.
- [ ] Update `PLANNING.md` with any changes or refinements made during development.
- [ ] Add docstrings and inline comments to the code.

## Discovered During Work

- [ ] Add 'Selected Portfolio Details' table (Yield, ER, Beta, Period Returns) below 'Fund Details' table. (Date: 2025-05-07)
(Add any new tasks or TODOs discovered during development here)

## Completed Tasks

- [x] Create `README.md`
- [x] Create `PLANNING.md`
- [x] Create `TASK.md`
- [x] Add Historic Stock vs. Bonds Returns table with interpolation
- [x] Fix NameError for portfolio_daily_returns in app.py (Date: 2025-05-07)
- [x] Fix failing tests in tests/test_calculator.py and tests/test_visualizer.py (Date: 2025-05-07)

## Persistent Historical Data Storage & Update

- [ ] Implement CSV storage for historical fund data (data/historical_fund_data.csv)
- [ ] Create data_fetcher.fetch_and_store_max_history function
- [ ] Create data_fetcher.get_last_data_date function
- [ ] Create data_fetcher.update_historical_data function
- [ ] Create data_fetcher.load_historical_data function
- [ ] Integrate app-triggered update logic in app.py (check on load, prompt user)
- [ ] Update app to use data_fetcher.load_historical_data for charts/calculations
- [ ] Add unit tests for new data_fetcher functions
