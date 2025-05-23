"""
Streamlit web application for the Four Fund Portfolio Planner.

Allows users to plan investment portfolios using a simple four-fund model
and visualize historical performance and risk metrics.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import data_fetcher
import calculator
import visualizer
import json
import os
from datetime import datetime, timedelta

# Set page config for wide layout
st.set_page_config(layout="wide")

# Set the title of the application
st.title("📈 Four Fund Portfolio Planner")
st.write("Use the sliders in the left panel to select your desired equity allocation between Stocks / Bonds, and US vs. International funds.")
# --- Data Loading and Update Logic ---
# Load configured tickers from portfolio_config.json
CONFIG_FILE = "portfolio_config.json"
try:
    with open(CONFIG_FILE, 'r') as f:
        config_data = json.load(f)
        CONFIGURED_HELPERS = list(config_data.keys()) # Assuming keys are tickers
except FileNotFoundError:
    st.error(f"Configuration file not found: {CONFIG_FILE}")
    st.stop() # Stop execution if config is missing
except json.JSONDecodeError:
    st.error(f"Error decoding JSON from {CONFIG_FILE}")
    st.stop()
except Exception as e:
    st.error(f"An error occurred loading {CONFIG_FILE}: {e}")
    st.stop()

data_filepath = data_fetcher._get_data_filepath()
today = datetime.now().date()

# Use session state to manage data download/update status
if 'data_initialized' not in st.session_state:
    st.session_state['data_initialized'] = False

if not st.session_state['data_initialized']:
    if not os.path.exists(data_filepath):
        st.warning("Historical data file not found.")
        if st.button("Download All Historical Data"):
            with st.spinner("Downloading historical data... This may take a few minutes."):
                data_fetcher.fetch_and_store_max_history(CONFIGURED_HELPERS)
            st.success("Historical data downloaded successfully!")
            st.session_state['data_initialized'] = True
            st.rerun() # Rerun to load the data
    else:
        last_data_date = data_fetcher.get_last_data_date()
        if last_data_date:
            days_since_last_update = (today - last_data_date.date()).days
            if days_since_last_update > 31:
                st.warning(f"Historical data is {days_since_last_update} days old.")
                if st.button("Update Historical Data"):
                    with st.spinner("Updating historical data..."):
                        data_fetcher.update_historical_data(CONFIGURED_HELPERS)
                    st.success("Historical data updated successfully!")
                    st.session_state['data_initialized'] = True
                    st.rerun() # Rerun to load the data
            else:
                st.info(f"Historical data is up to date (last entry: {last_data_date.strftime('%Y-%m-%d')}).")
                st.session_state['data_initialized'] = True
        else:
            # This case should ideally not happen if the file exists but is empty or has errors
            st.warning("Could not determine the last data date from the existing file.")
            if st.button("Attempt to Re-download All Historical Data"):
                 with st.spinner("Downloading historical data... This may take a few minutes."):
                    data_fetcher.fetch_and_store_max_history(CONFIGURED_HELPERS)
                 st.success("Historical data downloaded successfully!")
                 st.session_state['data_initialized'] = True
                 st.rerun() # Rerun to load the data

    # If data is not initialized, stop further execution until it is
    if not st.session_state['data_initialized']:
        st.stop()

# --- End Data Loading and Update Logic ---

# Add a button for manual data update
if st.button("Force Update Historical Data"):
    with st.spinner("Updating historical data..."):
        data_fetcher.update_historical_data(CONFIGURED_HELPERS, force_update=True)
    st.success("Historical data updated successfully!")
    st.session_state['data_initialized'] = True
    st.rerun() # Rerun to load the data



# Placeholders for input sliders
total_stocks_allocation = st.sidebar.slider("Total Stocks (%)", 0, 100, 70, 5)
international_stocks_allocation = st.sidebar.slider("International Stocks (%) within Stocks", 0, 100, 25, 5)
international_bonds_allocation = st.sidebar.slider("International Bonds (%) within Bonds", 0, 100, 25, 5)

# Calculate bond allocation
total_bonds_allocation = 100 - total_stocks_allocation

# Add a section for user inputs
st.header(f"Selected Portfolio: &nbsp;&nbsp;&nbsp;Stocks: {total_stocks_allocation}% / Bonds: {total_bonds_allocation}%")

# Get current stock allocation
current_stock_allocation = total_stocks_allocation

# Interpolate returns for the current allocation
interpolated_returns = calculator.interpolate_returns(current_stock_allocation)

# Add a section for Historic Stock vs. Bonds Returns
st.subheader(f"Historic Returns:&nbsp;&nbsp;&nbsp;Min:&nbsp;&nbsp;&nbsp;{interpolated_returns['Min_Return']:.1f}%&nbsp;&nbsp;&nbsp;Avg:&nbsp;&nbsp;&nbsp; {interpolated_returns['Avg_Return']:.1f}%&nbsp;&nbsp;&nbsp;Max:&nbsp;&nbsp;&nbsp; {interpolated_returns['Max_Return']:.1f}%")

# Calculate specific fund allocations using calculator.py
allocations = calculator.calculate_allocations(
    total_stocks_allocation,
    international_stocks_allocation,
    international_bonds_allocation
)

# Retrieve portfolio_daily_returns from session state for use in multiple sections
portfolio_daily_returns = st.session_state.get('portfolio_daily_returns', pd.Series())

# Define the periods to display returns for
PERIODS = ["1w", "1mo", "3mo", "6mo", "ytd", "1y", "2y", "5y", "10y", "max"]

# Fetch and display fund details
tickers = ["VTI", "VEA", "BND", "BNDX"]
fund_details_list = []
for ticker in tickers:
    details = data_fetcher.fetch_fund_details(ticker)
    if details:
        fund_details_list.append(details)

if fund_details_list:
    fund_details_df = pd.DataFrame(fund_details_list)

    # Add Portfolio % column using the 'allocations' dictionary
    # Ensure the order matches the tickers list used for fetching
    fund_details_df['Portfolio %'] = [f"{allocations[ticker]:.2f}%" for ticker in tickers]

    # Rename other columns
    fund_details_df = fund_details_df.rename(columns={
        "symbol": "Symbol", # Rename for consistency
        "name": "Name",
        "category": "Category",
        "expense_ratio": "ER",
        "yield": "Yield",
    })

    # Format percentage columns (excluding the new 'Portfolio %' which is already formatted)
    percentage_columns = ["ER", "Yield"]
    for col in percentage_columns:
        if col in fund_details_df.columns:
            if col in ["ER"]:
                fund_details_df[col] = fund_details_df[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/A")
            else:
                fund_details_df[col] = fund_details_df[col].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "N/A")

    # Reorder columns to put Portfolio % first
    desired_order = ['Symbol', 'Name', 'Category', 'Portfolio %', 'Yield', 'ER']
    # Filter order based on actual columns present (in case some data wasn't fetched)
    actual_order = [col for col in desired_order if col in fund_details_df.columns]
    fund_details_df = fund_details_df[actual_order]


    # Create a MultiIndex for columns (adjusting for the new column order)
    new_columns = []
    for col in fund_details_df.columns:
        new_columns.append(("", col)) # All columns at top level

    fund_details_df.columns = pd.MultiIndex.from_tuples(new_columns)

    st.subheader("Fund Details") # Keep a simple subheader
    # Display the table, hiding the default index
    st.dataframe(fund_details_df, hide_index=True)

    # Load historical data from the CSV file
    historical_data_df = data_fetcher.load_historical_data(CONFIGURED_HELPERS)

    if not historical_data_df.empty:
        # The data is already in the wide format (Date, Ticker1, Ticker2, ...)
        # Set the 'Date' column as the index for calculations
        combined_data = historical_data_df.set_index('Date')

        # Ensure columns used in calculation are numeric (should be handled by load_historical_data, but double check)
        numeric_cols = [col for col in CONFIGURED_HELPERS if col in combined_data.columns]
        for col in numeric_cols:
             combined_data[col] = pd.to_numeric(combined_data[col], errors='coerce')
        combined_data.dropna(subset=numeric_cols, inplace=True) # Drop rows with NaN in ticker columns

        # Calculate daily portfolio returns
        portfolio_daily_returns = calculator.calculate_portfolio_returns(combined_data, allocations)

        # Prepare data for the returns table
        returns_data = {}
        returns_data["Period"] = PERIODS

        # Get earliest date for each fund and calculate individual fund returns
        # Get earliest non-zero date for each fund and calculate individual fund returns
        fund_earliest_dates = {}
        for ticker in CONFIGURED_HELPERS:
            if ticker in combined_data.columns:
                fund_prices = combined_data[ticker]
                # Find the index of the first non-zero price
                first_non_zero_index = fund_prices[fund_prices != 0].first_valid_index()

                if first_non_zero_index is not None:
                    earliest_date = fund_prices.index[fund_prices.index.get_loc(first_non_zero_index)]
                    fund_earliest_dates[ticker] = earliest_date.strftime('%#m/%#d/%Y') # Format as M/D/YYYY
                    #print(fund_earliest_dates[ticker])
                else:
                    fund_earliest_dates[ticker] = "N/A" # No non-zero prices found

                fund_returns = []
                for period in PERIODS:
                    # Use the original combined_data for calculations, not the dropna version used for finding earliest date
                    ret = calculator.calculate_individual_fund_period_return(combined_data[ticker], period) # Pass the full series
                    fund_returns.append(f"{ret:.2%}" if ret is not None else "N/A")
                returns_data[ticker] = fund_returns
            else:
                # If ticker data is not in the loaded data (shouldn't happen with current load logic, but as a fallback)
                fund_earliest_dates[ticker] = "N/A"
                returns_data[ticker] = ["N/A"] * len(PERIODS)


        # Calculate portfolio returns for each period
        portfolio_returns = []
        if not portfolio_daily_returns.empty:
            for period in PERIODS:
                ret = calculator.calculate_portfolio_period_return(portfolio_daily_returns, period)
                portfolio_returns.append(f"{ret:.2%}" if ret is not None else "N/A")
        else:
            portfolio_returns = ["N/A"] * len(PERIODS)

        returns_data["Portfolio"] = portfolio_returns

        # Create and display the returns DataFrame
        returns_df = pd.DataFrame(returns_data)
        returns_df = returns_df.set_index("Period") # Set Period as the index

        # Modify column names to include earliest date
        new_column_names = {}
        for ticker in CONFIGURED_HELPERS:
            new_column_names[ticker] = f"{ticker} ({fund_earliest_dates[ticker]})"
        # Add Portfolio column name
        new_column_names["Portfolio"] = "Portfolio"
        returns_df = returns_df.rename(columns=new_column_names)
        returns_df = returns_df.T
        st.subheader("Period Returns")
        st.dataframe(returns_df)

# Add a section for allocation visualizations
st.header("Allocation Visualizations")

# Create pie charts using visualizer.py
pie_chart_data = {
    "Stocks vs Bonds": ([total_stocks_allocation, total_bonds_allocation], ["Stocks", "Bonds"]),
    "US Stocks vs International Stocks": ([allocations["VTI"], allocations["VEA"]], ["US Stocks", "International Stocks"]),
    "US Bonds vs International Bonds": ([allocations["BND"], allocations["BNDX"]], ["US Bonds", "International Bonds"]),
    "US vs International": ([allocations["VTI"] + allocations["BND"], allocations["VEA"] + allocations["BNDX"]], ["US", "International"]),
    "Four Funds": ([allocations["VTI"], allocations["VEA"], allocations["BND"], allocations["BNDX"]], ["US Stocks", "International Stocks", "US Bonds", "International Bonds"])
}

# Create columns for displaying charts
cols = st.columns(2)
chart_index = 0
for chart_title, (sizes, chart_labels) in pie_chart_data.items():
    # Determine which column to place the chart in
    col = cols[chart_index % 2]

    with col:
        # Ensure sizes are not all zero before generating chart
        if any(size > 0 for size in sizes):
            fig = visualizer.generate_pie_chart(sizes, chart_labels, chart_title)
            st.plotly_chart(fig, use_container_width=True) # Display the Plotly figure
        else:
            st.subheader(chart_title) # Keep this subheader for the "No data" case
            st.write(f"No data to display for {chart_title}.")

    chart_index += 1


# Add a section for historical performance
st.header("Historical Performance")

if not portfolio_daily_returns.empty:
    cumulative_returns_series = calculator.calculate_cumulative_returns(portfolio_daily_returns) # Renamed for clarity
    st.subheader("Cumulative Returns (Max History)")

    # Use the visualizer function to generate Plotly chart
    fig = visualizer.generate_historical_performance_plotly_chart(cumulative_returns_series, title="Cumulative Returns (Max History)")
    st.plotly_chart(fig, use_container_width=True) # Display the Plotly figure

    # Store portfolio_daily_returns in session state for risk metrics and projections
    st.session_state['portfolio_daily_returns'] = portfolio_daily_returns
else:
     st.warning("Could not calculate portfolio returns for cumulative chart.")


# Save/Load Portfolios
st.subheader("Save/Load Portfolio")

def save_portfolio(allocations: dict):
    """
    Saves the current portfolio allocation to a JSON file.

    Args:
        allocations (dict): A dictionary containing the portfolio allocation percentages.
    """
    import json
    file_path = "portfolio_config.json"
    try:
        with open(file_path, "w") as f:
            json.dump(allocations, f, indent=4)
        st.success(f"Portfolio configuration saved to {file_path}")
    except Exception as e:
        st.error(f"Error saving portfolio configuration: {e}")


def load_portfolio(uploaded_file):
    """
    Loads a portfolio allocation from a JSON file uploaded by the user.

    Args:
        uploaded_file: The file object uploaded by the user via st.file_uploader.

    Returns:
        dict or None: A dictionary containing the loaded allocation if successful, otherwise None.
    """
    import json
    try:
        data = json.load(uploaded_file)
        # Validate loaded data (basic check)
        if isinstance(data, dict) and all(ticker in data for ticker in ["VTI", "VEA", "BND", "BNDX"]):
            # Update sliders based on loaded data - This requires a way to programmatically set slider values,
            # which is not directly supported by Streamlit's st.slider in a simple way that updates the UI state
            # without a rerun. A more advanced approach using session state and callbacks would be needed for
            # seamless slider updates upon loading. For now, we'll just display the loaded allocation.
            st.write("Loaded Portfolio Allocation:")
            st.json(data)
            st.warning("Note: Updating sliders based on loaded configuration requires a page rerun. Manually adjust sliders to match loaded values for now.")
            return data # Return loaded data for potential use, though not directly updating sliders yet
        else:
            st.error("Invalid portfolio configuration file.")
            return None
    except Exception as e:
        st.error(f"Error loading portfolio configuration: {e}")
        return None

# Save button
if st.button("Save Current Portfolio"):
    # Need to get the current allocation values from the sliders to save
    current_allocations_to_save = calculator.calculate_allocations(
        total_stocks_allocation,
        international_stocks_allocation,
        international_bonds_allocation
    )
    save_portfolio(current_allocations_to_save)

# Load file uploader
uploaded_file = st.file_uploader("Load Portfolio Configuration (.json)", type=["json"])
if uploaded_file is not None:
    loaded_allocations = load_portfolio(uploaded_file)
    # If loaded_allocations is not None, you could potentially store it in session state
    # and use a callback with the sliders to update their values on rerun.
