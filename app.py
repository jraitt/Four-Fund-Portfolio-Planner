"""
Streamlit web application for the Four Fund Portfolio Planner.

Allows users to plan investment portfolios using a simple four-fund model
and visualize historical performance and risk metrics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import visualizer
import json
import os
from datetime import datetime, timedelta
from YahooFinance import yf_utilities

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

# Add a button for manual data update
if st.button("Force Update Historical Data"):
    with st.spinner("Updating historical data..."):
        yf_utilities.update_historical_data(CONFIGURED_HELPERS, force_update=True)
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
interpolated_returns = interpolate_returns(current_stock_allocation)

# Add a section for Historic Stock vs. Bonds Returns
st.subheader(f"Historic Returns:&nbsp;&nbsp;&nbsp;Min:&nbsp;&nbsp;&nbsp;{interpolated_returns['Min_Return']:.1f}%&nbsp;&nbsp;&nbsp;Avg:&nbsp;&nbsp;&nbsp; {interpolated_returns['Avg_Return']:.1f}%&nbsp;&nbsp;&nbsp;Max:&nbsp;&nbsp;&nbsp; {interpolated_returns['Max_Return']:.1f}%")

# Calculate specific fund allocations using calculator.py
allocations = calculate_allocations(
    total_stocks_allocation,
    international_stocks_allocation,
    international_bonds_allocation
)


# Fetch and display fund details
tickers = ["VTI", "VEA", "BND", "BNDX"]
fund_details_df = yf_utilities.fetch_fund_details(tickers)

# Multiply percentage columns by 100 for display
if 'Yield' in fund_details_df.columns:
    fund_details_df['Yield'] = fund_details_df['Yield'] * 100
if 'ER' in fund_details_df.columns:
    fund_details_df['ER'] = fund_details_df['ER'] * 100
if 'D Ch%' in fund_details_df.columns:
    fund_details_df['D Ch%'] = fund_details_df['D Ch%'] * 100

st.subheader("Fund Details") # Keep a simple subheader# Display the table, hiding the default index
column_config_details = {
    "Price": st.column_config.NumberColumn(format="$%.2f"),
    "P Close": st.column_config.NumberColumn(format="$%.2f"),
    "52 High": st.column_config.NumberColumn(format="$%.2f"),
    "52 Low": st.column_config.NumberColumn(format="$%.2f"),
    "50 Day": st.column_config.NumberColumn(format="$%.2f"),
    "200 Day": st.column_config.NumberColumn(format="$%.2f"),
    "D Ch": st.column_config.NumberColumn(format="$%.2f"),
    "Yield": st.column_config.NumberColumn(format="%.2f%%"),
    "ER": st.column_config.NumberColumn(format="%.2f%%"),
    "D Ch%": st.column_config.NumberColumn(format="%.2f%%"),
}
# Filter to only include columns that exist in the DataFrame
column_config_details = {k: v for k, v in column_config_details.items() if k in fund_details_df.columns}
st.dataframe(fund_details_df, hide_index=True, column_config=column_config_details)

returns_df = yf_utilities.get_historical_returns(tickers)

# Multiply percentage columns by 100 for display
for col in ["1w", "1mo", "3mo", "6mo", "ytd", "1y", "2y", "3y", "5y", "10y", "max"]:
    if col in returns_df.columns:
        # Ensure the column is numeric before multiplication, coercing errors to NaN
        returns_df[col] = pd.to_numeric(returns_df[col], errors='coerce')
        # Only multiply if the value is not NaN (i.e., it was successfully converted to a number)
        returns_df[col] = returns_df[col].apply(lambda x: x * 100 if pd.notna(x) else x)

st.subheader("Period Returns")
column_config_returns = {
    col: st.column_config.NumberColumn(format="%.2f%%")
    for col in returns_df.columns if col != "Symbol"
}
st.dataframe(returns_df, column_config=column_config_returns)

# Display Year-to-Date return


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
    current_allocations_to_save = calculate_allocations(
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
