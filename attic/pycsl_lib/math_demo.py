"""Formal driver for the math stub (the my_os_demo.py analog).

Exercises the real, body-verified integer functions (gcd, sqrt, ceil, floor) end-to-end. The
postconditions are discharged from the callees' contracts — no `\trusted`."""
from math import gcd, sqrt, ceil, floor


#@ requires a >= 0 and b >= 0
#@ ensures \result >= 0
def demo_gcd(a: int, b: int) -> int:
    """gcd of two non-negatives is non-negative."""
    return gcd(a, b)


#@ requires x >= 0
#@ ensures \result * \result <= x
#@ ensures (\result + 1) * (\result + 1) > x
def demo_isqrt(x: int) -> int:
    """sqrt(x) is the integer square root: r² <= x < (r+1)²."""
    return sqrt(x)


#@ ensures \result >= x
#@ ensures \result <= x + 1
def demo_ceil(x: int) -> int:
    """ceil(x) lands in [x, x+1]."""
    return ceil(x)


#@ ensures \result <= x
def demo_floor(x: int) -> int:
    """floor(x) is at most x."""
    return floor(x)
