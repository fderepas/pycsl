"""Test 0206 - raises contract with exceptional postcondition"""
_ = 0  # anchor
#@ requires 1 == 1
#@ ensures \result >= 0
#@ raises ValueError when n < 0
def checked_abs(n: int) -> int:
    if n < 0:
        raise ValueError
    return n
