"""PyCSL mock for Python's enum module — Implementation of an enumeration class."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def show_flag_values(value: int) -> int:
    """Mock: Return a list of all power-of-two integers contained in a flag *value*. .. versionadded:: 3.11"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def bin(num: int, max_bits: int) -> int:
    """Mock: Like built-in :func:`bin`, except negative values are represented in two's complement, and the leading bit always indica..."""
    return 0
