r"""Test 7387 -- route #473 (expected FAIL): `d: List[int] = [0] * 1024; c: List[int] = []; return g(c) + len(d)` -- the empty local and a REAL 1024-element list emit the same `(Array.make 1024 0)`; the IR attributes each binding (only `c`'s is `[]`). PROVED at base 1f3aa3081; CPython IndexError; now FAILS.
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



#@ ensures \result == 1024
#@ assigns \nothing
def h() -> int:
    d: List[int] = [0] * 1024
    c: List[int] = []
    return g(c) + len(d)


if __name__ == "__main__":
    try:
        r = h()
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
