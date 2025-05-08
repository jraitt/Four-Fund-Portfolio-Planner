import matplotlib.pyplot as plt
import pandas as pd
import numpy as np # Import numpy
import matplotlib.ticker as mticker # Import for percentage formatting on charts

def generate_pie_chart(sizes: list, labels: list, title: str):
    """
    Generates and returns a Plotly figure for a donut chart.

    Args:
        sizes (list): List of sizes for each wedge of the pie chart.
        labels (list): List of labels for each wedge.
        title (str): The title of the pie chart.

    Returns:
        plotly.graph_objects.Figure: The figure object containing the donut chart.
    """
    # Define a vibrant color palette with the specified color 1
    vibrant_colors = ['#ff401e', '#1e66ff', '#ff9048', '#1eeeff'] # Specified color 1

    # Define color mapping based on the new groupings
    color_map = {
        'Stocks': vibrant_colors[0],
        'US Stocks': vibrant_colors[0],
        'US': vibrant_colors[0], # US in US vs INT chart
        'Bonds': vibrant_colors[1],
        'US Bonds': vibrant_colors[1],
        'International': vibrant_colors[1], # INT in US vs INT chart
        'International Stocks': vibrant_colors[2],
        'International Bonds': vibrant_colors[3]
    }

    # Get colors in the order of labels
    colors = [color_map.get(label, 'gray') for label in labels] # Default to gray if label not in map

    fig = go.Figure(data=[go.Pie(labels=labels, values=sizes, hole=.4, marker=dict(colors=colors))]) # Use go.Pie with hole and colors
    fig.update_layout(title_text=title, title_x=0.5) # Center the title
    return fig

def generate_historical_performance_chart(cumulative_returns: pd.Series, title: str = "Historical Cumulative Returns"):
    """
    Generates and returns a matplotlib figure for the historical performance line chart.

    Args:
        cumulative_returns (pd.Series): Series containing the cumulative returns over time.
        title (str, optional): The title of the chart. Defaults to "Historical Cumulative Returns".

    Returns:
        matplotlib.figure.Figure: The figure object containing the line chart.
    """
    fig, ax = plt.subplots()
    ax.plot(cumulative_returns.index, cumulative_returns.values)
    ax.set_title(title)

    # Format y-axis as percentages
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(xmax=1.0))
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
        if metric in ["Yield"]:
            # Assuming value is a decimal representation of a percentage, multiply by 100 before formatting
            table_data["Value"].append(f"{value*100:.2f}%" if value is not None and not np.isnan(value) else "N/A")
            # Reason: Format Yield and Expense Ratio as percentages with 2 decimal places after multiplying by 100.
        elif metric in ["Beta", "Expense Ratio"]:
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
    # Transpose the DataFrame and reset index to make metrics columns
    df_transposed = df.set_index("Metric").T.reset_index(drop=True)
    st.table(df_transposed) # Display the transposed table without index


# TODO: Consider adding options for different time periods (1y, 3y, 5y, 10y) for the historical chart
# TODO: Consider using Plotly for interactive charts as mentioned in PLANNING.md

import plotly.express as px
import plotly.graph_objects as go

def generate_historical_performance_plotly_chart(cumulative_returns: pd.Series, title: str):
    """
    Generates and returns a Plotly figure for the historical performance line chart.

    Args:
        cumulative_returns (pd.Series): Series containing the cumulative returns over time.
        title (str): The title of the chart.

    Returns:
        plotly.graph_objects.Figure: The figure object containing the line chart.
    """
    # Convert Series to DataFrame for Plotly
    # Ensure the index is a proper datetime type if it's not already
    if not isinstance(cumulative_returns.index, pd.DatetimeIndex):
        cumulative_returns.index = pd.to_datetime(cumulative_returns.index)

    cumulative_returns_df = cumulative_returns.reset_index()
    cumulative_returns_df.columns = ['Date', 'Cumulative Return']

    fig = px.line(cumulative_returns_df, x='Date', y='Cumulative Return', title=title)

    # Format Y-axis as percentages
    fig.update_layout(yaxis_tickformat=".0%")

    return fig


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
