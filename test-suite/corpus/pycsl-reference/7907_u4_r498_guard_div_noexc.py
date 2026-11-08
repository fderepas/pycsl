r"""Test 7907 -- route #498 (expected FAIL: PROVED at base, REFUSED PYCSL-R498-IS-ON-FRESH-VALUE): `d = 0 if a is b else 1; return 10 // (1 - d)` with fresh `a`, `b` claimed `no_exception \\all`; CPython f(1) raises ZeroDivisionError (rt44 g521/k52110)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ no_exception \all
def f(n: int) -> int:
    a = n + 1000
    b = n + 1000
    d = 0 if a is b else 1
    return 10 // (1 - d)


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
