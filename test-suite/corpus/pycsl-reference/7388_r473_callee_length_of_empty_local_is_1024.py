r"""Test 7388 -- route #473 (expected FAIL): `c: List[int] = []; return ln(c)` claiming `\result == 1024`, `ln` ensuring `\result == len(c)` -- the callee handed the caller the placeholder's length. PROVED at base 1f3aa3081; CPython 0; now FAILS (and 7391, the true `== 0`, PROVES).
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
    c: List[int] = []
    return ln(c)


if __name__ == "__main__":
    try:
        r = h()
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
