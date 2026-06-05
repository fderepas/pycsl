"""PyCSL mock for Python's enum module — Implementation of an enumeration class."""
_ = 0  # anchor

# cite: https://github.com/python/cpython/blob/main/Lib/enum.py
#@ requires True
#@ ensures True
def show_flag_values(value: int) -> int:
    """Mock: Return a list of all power-of-two integers contained in a flag *value*. .. versionadded:: 3.11"""
    return 0

# cite: https://github.com/python/cpython/blob/main/Lib/enum.py#L130
#@ requires max_bits >= 1
#@ ensures \result >= 0
def bin(num: int, max_bits: int) -> int:
    """Mock: Like built-in :func:`bin`, except negative values are represented in two's complement, and the leading bit always indica..."""
    return 0
