r"""Test 7491 -- route #479 (expected FAIL): `1 if not ... else 1 // (n - n)` -- `not ...` in a ternary test was `not (0 <> 0)`. PROVED at base; CPython ZeroDivisionError; now FAILS.
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    return 1 if not ... else 1 // (n - n)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
