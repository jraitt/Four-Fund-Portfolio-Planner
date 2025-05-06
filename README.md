# Four Fund Portfolio Planner

This is an interactive web application built with Streamlit that allows users to plan investment portfolios using a simple four-fund model: VTI (US Stocks), VEA (International Stocks), BND (US Bonds), and BNDX (International Bonds).

## Features

- **Flexible Allocation:** Users can specify the percentage allocation for stocks, international stocks (within the stock allocation), and international bonds (within the bond allocation) in 5% increments.
- **Fund Details Table:** Displays key information for each of the four funds, including symbol, name, category, yield, expense ratio, and Beta, fetched using `yfinance`.
- **Allocation Visualizations:** Provides multiple pie charts to visualize the portfolio breakdown:
    - Stocks vs Bonds
    - US Stocks vs International Stocks
    - US Bonds vs International Bonds
    - US Stocks & Bonds vs International Stocks & Bonds
    - Four Funds (VTI, VEA, BND, BNDX)
- **Historical Performance Graph:** Graphs the cumulative returns for the selected portfolio based on historical data fetched from Yahoo Finance.
- **Risk Metrics:** Displays calculated annualized volatility and Sharpe Ratio for the selected portfolio.
- **Projections:** Projects future portfolio value based on historical annualized returns and user-defined initial investment and time horizon.
- **Historic Stock vs. Bonds Returns Table:** Displays interpolated historical maximum, average, and minimum annual returns for the currently selected stock/bond allocation.
- **Save/Load Portfolio:** Allows saving the current portfolio allocation to a JSON file and loading a previously saved configuration. (Note: Loading currently displays the configuration; manual slider adjustment is needed to apply.)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd Four Fund Portfolio Planner
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Activate your virtual environment** (if you haven't already).
2. **Run the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

3. Open your web browser and navigate to the provided local URL (usually `http://localhost:8501`).

## Running Tests

This project uses `pytest` for unit testing. If you encounter `ModuleNotFoundError` when running tests, the recommended way to resolve this is by installing the project in "editable" mode in your virtual environment.

1.  **Install the project in editable mode:**
    Open your terminal in the project's root directory and run:
    ```bash
    pip install -e .
    ```
    This command makes the project's modules discoverable by Python.

2.  **Run the tests:**
    After installing in editable mode, you should be able to run the tests simply by executing:
    ```bash
    pytest
    ```

## Dependencies

- streamlit
- yfinance
- pandas
- matplotlib
- numpy
- scikit-learn
- pytest (for running tests)

## Contributing

(Add contributing guidelines here if applicable)

## License

(Add license information here if applicable)
