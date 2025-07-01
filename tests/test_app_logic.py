
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
from app import calculate_allocations, interpolate_returns

def test_calculate_allocations():
    """
    Tests the calculate_allocations function with a sample input.
    """
    allocations = calculate_allocations(70, 25, 25)
    assert allocations["VTI"] == 52.5
    assert allocations["VEA"] == 17.5
    assert allocations["BND"] == 22.5
    assert allocations["BNDX"] == 7.5

def test_interpolate_returns_zero_stocks():
    """
    Tests the interpolate_returns function with 0% stocks.
    """
    returns = interpolate_returns(0)
    assert returns["Max_Return"] == 32.6
    assert returns["Avg_Return"] == 5.3
    assert returns["Min_Return"] == -8.1

def test_interpolate_returns_hundred_stocks():
    """
    Tests the interpolate_returns function with 100% stocks.
    """
    returns = interpolate_returns(100)
    assert returns["Max_Return"] == 54.2
    assert returns["Avg_Return"] == 10.4
    assert returns["Min_Return"] == -43.1

def test_interpolate_returns_fifty_stocks():
    """
    Tests the interpolate_returns function with 50% stocks.
    """
    returns = interpolate_returns(50)
    assert returns["Max_Return"] == 32.3
    assert returns["Avg_Return"] == 8.2
    assert returns["Min_Return"] == -22.5
