r"""Test 7490 -- route #479 (expected FAIL): `1 // (n - n) if ... else 1` under `no_exception \all` -- the ternary TEST `...` lowered to the integer 0 (route #40's marker dropped by the typed re-read). PROVED at base 8aaa864ca; CPython ZeroDivisionError; now FAILS (opaque `pycsl_ellipsis`).
"""
# pycsl-expected: FAIL
from typing import List


#@ no_exception \all
def f(n: int) -> int:
    return 1 // (n - n) if ... else 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
