r"""Test 7385 -- route #473 (expected FAIL): `c: List[int] = []; if b: return g(c)` -- the call on one branch (an early-return `try` body). PROVED at base 1f3aa3081; CPython `h(True)` IndexError; now FAILS.
"""
# pycsl-expected: FAIL
from typing import List, Tuple


#@ requires len(c) >= 1
#@ ensures \result == c[0]
#@ assigns \nothing
def g(c: List[int]) -> int:
    return c[0]


#@ ensures \result == len(c)
#@ assigns \nothing
def ln(c: List[int]) -> int:
    return len(c)



#@ ensures \result == 0
#@ assigns \nothing
def h(b: bool) -> int:
    c: List[int] = []
    if b:
        return g(c)
    return 0


if __name__ == "__main__":
    try:
        r = h(True)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
