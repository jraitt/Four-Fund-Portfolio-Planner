import matplotlib.pyplot as plt
import pandas as pd
import numpy as np # Import numpy

def generate_pie_chart(sizes: list, labels: list, title: str):
    """
    Generates and returns a matplotlib figure for a pie chart.

    Args:
        sizes (list): List of sizes for each wedge of the pie chart.
        labels (list): List of labels for each wedge.
        title (str): The title of the pie chart.

    Returns:
        matplotlib.figure.Figure: The figure object containing the pie chart.
    """
    fig, ax = plt.subplots() # Remove figsize
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.set_title(title, fontweight='bold', fontsize=14) # Make title bold and larger
    plt.tight_layout() # Add tight_layout
    return fig

def generate_historical_performance_chart(cumulative_returns: pd.Series):
    """
    Generates and returns a matplotlib figure for the historical performance line chart.

    Args:
        cumulative_returns (pd.Series): Series containing the cumulative returns over time.

    Returns:
        matplotlib.figure.Figure: The figure object containing the line chart.
    """
    fig, ax = plt.subplots()
    ax.plot(cumulative_returns.index, cumulative_returns.values)
    ax.set_title("Historical Cumulative Returns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return")
    plt.xticks(rotation=45)
    plt.tight_layout()
    return fig

import streamlit as st # Import streamlit

def display_portfolio_details_table(portfolio_metrics: dict, portfolio_returns: dict):
    """
    Displays a table of selected portfolio details (Yield, ER, Beta, Period Returns) in Streamlit.

    Args:
        portfolio_metrics (dict): Dictionary containing weighted 'Yield', 'Expense Ratio', and 'Beta'.
        portfolio_returns (dict): Dictionary with period labels and calculated returns.
    """
    st.subheader("Selected Portfolio Details")

    # Prepare data for the table
    table_data = {
        "Metric": [],
        "Value": []
    }

    # Add composite metrics
    for metric, value in portfolio_metrics.items():
        table_data["Metric"].append(metric)
        # Format as percentage if it's ER or Yield, otherwise format Beta
        if metric in ["Yield", "Expense Ratio"]:
            table_data["Value"].append(f"{value:.4f}%" if value is not None and not np.isnan(value) else "N/A")
            # Reason: Format Yield and Expense Ratio as percentages with 4 decimal places.
        elif metric == "Beta":
             table_data["Value"].append(f"{value:.2f}" if value is not None and not np.isnan(value) else "N/A")
             # Reason: Format Beta with 2 decimal places.
        else:
            table_data["Value"].append(str(value) if value is not None and not np.isnan(value) else "N/A")
            # Reason: Handle other metrics (shouldn't be any based on current plan, but good practice).


    # Add period returns
    # Define display labels for periods
    period_labels = {
        "1mo": "1 Month Return",
        "3mo": "3 Month Return",
        "6mo": "6 Month Return",
        "ytd": "YTD Return",
        "1y": "1 Year Return",
        "3y": "3 Year Return",
        "5y": "5 Year Return",
        "10y": "10 Year Return",
        "max": "Max Return"
    }

    for period_key, display_label in period_labels.items():
        if period_key in portfolio_returns:
            return_value = portfolio_returns[period_key]
            table_data["Metric"].append(display_label)
            table_data["Value"].append(f"{return_value:.2%}" if return_value is not None and not np.isnan(return_value) else "N/A")
            # Reason: Format returns as percentages with 2 decimal places.


    df = pd.DataFrame(table_data)
    st.table(df)


# TODO: Consider adding options for different time periods (1y, 3y, 5y, 10y) for the historical chart
# TODO: Consider using Plotly for interactive charts as mentioned in PLANNING.md

if __name__ == '__main__':
    # Example Usage (requires sample data)
    # Example Pie Chart
    # sizes = [60, 40]
    # labels = ['Stocks', 'Bonds']
    # pie_fig = generate_pie_chart(sizes, labels, "Stocks vs Bonds Allocation")
    # plt.show()

    # Example Historical Performance Chart
    # dates = pd.to_datetime(['2020-01-01', '2021-01-01', '2022-01-01', '2023-01-01'])
    # returns = pd.Series([0, 0.1, 0.15, 0.2], index=dates)
    # hist_fig = generate_historical_performance_chart(returns)
    # plt.show()
    pass
