import matplotlib.pyplot as plt
import pandas as pd

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
