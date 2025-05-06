import sys
import os
# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

import pytest
import matplotlib.pyplot as plt
import pandas as pd
import visualizer

def test_generate_pie_chart():
    """Tests the generate_pie_chart function."""
    sizes = [60, 40]
    labels = ['Stocks', 'Bonds']
    title = "Stocks vs Bonds Allocation"
    fig = visualizer.generate_pie_chart(sizes, labels, title)

    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    ax = fig.axes[0]
    assert ax.get_title() == title
    # Basic check for patches (pie wedges)
    assert len(ax.patches) == len(sizes)

    plt.close(fig) # Close the figure to free up memory

def test_generate_historical_performance_chart():
    """Tests the generate_historical_performance_chart function."""
    dates = pd.to_datetime(['2020-01-01', '2021-01-01', '2022-01-01', '2023-01-01'])
    returns = pd.Series([0, 0.1, 0.15, 0.2], index=dates)
    fig = visualizer.generate_historical_performance_chart(returns)

    assert isinstance(fig, plt.Figure)
    assert len(fig.axes) == 1
    ax = fig.axes[0]
    assert ax.get_title() == "Historical Cumulative Returns"
    assert ax.get_xlabel() == "Date"
    assert ax.get_ylabel() == "Cumulative Return"
    # Basic check for lines
    assert len(ax.lines) > 0

    plt.close(fig) # Close the figure to free up memory
