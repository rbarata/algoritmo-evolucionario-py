"""Utility functions for mesh evolution algorithm."""

from typing import TypeVar

T = TypeVar('T', int, float)


def max_value(a: T, b: T) -> T:
    """Return maximum of two numbers.
    
    Args:
        a: First value
        b: Second value
        
    Returns:
        Maximum value
    """
    return a if a > b else b


def min_value(a: T, b: T) -> T:
    """Return minimum of two numbers.
    
    Args:
        a: First value
        b: Second value
        
    Returns:
        Minimum value
    """
    return a if a < b else b


def print_title(title: str, width: int = 80) -> None:
    """Print a formatted title with border.
    
    Args:
        title: Title text to print
        width: Width of the border (default: 80)
    """
    print("#")
    print("#")
    print("#" * width)
    print(f"#{title}")
    print("#" * width)
    print("#")
