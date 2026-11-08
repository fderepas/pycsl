r"""Test 7386 -- route #473 (expected FAIL): `c = []; x = g(c); return x` -- the call result bound to a local. PROVED at base 1f3aa3081; CPython IndexError; now FAILS.
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
def h() -> int:
    c = []
    x = g(c)
    return x


if __name__ == "__main__":
    try:
        r = h()
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
