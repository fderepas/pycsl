"""Test 0205 - raise statement with guard"""
_ = 0  # anchor
#@ requires n >= 0
#@ ensures \result >= 1
def safe_factorial(n: int) -> int:
    if n < 0:
        raise ValueError
    if n == 0:
        return 1
    r: int = 1
    i: int = 1
    #@ loop invariant 1 <= i and i <= n + 1
    #@ loop invariant r >= 1
    #@ loop variant n - i + 1
    while i <= n:
        r = r * i
        i = i + 1
    return r
