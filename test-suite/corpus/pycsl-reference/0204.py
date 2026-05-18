"""Test 0204 - bounded int64 arithmetic"""
_ = 0  # anchor
#@ assumes bounded_int(64)
#@ requires 0 <= x and x <= 1000000
#@ requires 0 <= y and y <= 1000000
#@ ensures \result == x * y
def multiply_bounded(x: int, y: int) -> int:
    return x * y
