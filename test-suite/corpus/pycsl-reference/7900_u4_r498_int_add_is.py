r"""Test 7900 -- route #498 (expected FAIL: PROVED at base, REFUSED PYCSL-R498-IS-ON-FRESH-VALUE): `(n + 1) is (n + 1)` claimed True; CPython f(1000) returns False (rt44 g515/j51500)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ ensures \result == True
def f(n: int) -> bool:
    return (n + 1) is (n + 1)


if __name__ == "__main__":
    try:
        r = f(1000)
        if not (r == True):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
