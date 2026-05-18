"""Test 0202 - bounded int32 overflow checking"""
_ = 0  # anchor
#@ assumes bounded_int(32)
#@ requires -100 <= x and x <= 100
#@ requires -100 <= y and y <= 100
#@ ensures \result == x + y
def add_bounded(x: int, y: int) -> int:
    return x + y
