"""Formal driver for the enum stub (the my_os_demo.py analog).

Exercises the module's contracts end-to-end. Verifies with **zero** `\trusted`."""
from enum import bin, show_flag_values


#@ requires max_bits >= 1
#@ ensures \result >= 0
def demo_bin(num: int, max_bits: int) -> int:
    """`bin` returns a non-negative encoding under the max_bits precondition."""
    return bin(num, max_bits)


#@ ensures True
def demo_show_flags(value: int) -> int:
    """`show_flag_values` is total (its only postcondition is True)."""
    return show_flag_values(value)
