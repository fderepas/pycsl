r"""Test 7492 -- route #479 (expected FAIL): `ensures \result == 0` over `return 1 if ... else 0`. PROVED at base; CPython returns 1; now FAILS.
"""
# pycsl-expected: FAIL
from typing import List


#@ ensures \result == 0
def f(n: int) -> int:
    return 1 if ... else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
