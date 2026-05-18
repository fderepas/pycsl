"""Test 0200 - PyCSL Annotation Reference 2.1 (division by zero guard)"""
_ = 0  # anchor
#@ requires y != 0
#@ ensures \result * y + x - \result * y == x
def safe_div(x: int, y: int) -> int:
    return x // y
