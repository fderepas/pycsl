"""Test 0058 — Multi-file: external module import (warning, no crash)"""
_ = 0  # anchor
from math import factorial

#@ requires x >= 0
#@ ensures \result >= 1
def at_least_one(x: int) -> int:
    """Returns x + 1, which is always >= 1 for non-negative x."""
    return x + 1

if __name__ == "__main__":
    assert at_least_one(0) == 1
    print("PASS")
