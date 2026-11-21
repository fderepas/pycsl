r"""Test 7389 -- route #473 (expected FAIL): `c: List[int] = list([]); return len(c)` claiming `\result == 1024` -- `list([])` is the placeholder too and the size fold does not run, so the function's OWN `len(c)` read 1024. PROVED at base 1f3aa3081; CPython 0; now FAILS.
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
    c: List[int] = list([])
    return len(c)


if __name__ == "__main__":
    try:
        r = h()
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
