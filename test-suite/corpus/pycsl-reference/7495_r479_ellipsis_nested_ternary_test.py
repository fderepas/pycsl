r"""Test 7495 -- route #479 (expected FAIL): `...` in a NESTED ternary test (`X if (... if n else 0) else 1`). PROVED at base; CPython ZeroDivisionError; now FAILS.
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    return 1 // (n - n) if (... if n else 0) else 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
