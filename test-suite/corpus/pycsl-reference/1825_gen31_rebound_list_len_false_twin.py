r"""Test 1825 — gen #31 FALSE TWIN of 1823: the un-rebound path is 3, not 2.

Without this file, 1823/1824 would be indistinguishable from a counter that answers
whatever the contract asks for. CPython: with `n == 0`, `len(a)` is 3.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires n == 0
#@ ensures \result == 2
def f(n: int) -> int:
    a: list = [7, 8, 9]
    if n > 0:
        a = [1, 2]
    return len(a)
