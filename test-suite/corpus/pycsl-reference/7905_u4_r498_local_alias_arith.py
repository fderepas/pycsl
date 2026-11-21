r"""Test 7905 -- route #498 (expected FAIL: PROVED at base, REFUSED PYCSL-R498-IS-ON-FRESH-VALUE): two locals bound to `n + 1000` compared by `is`, claimed True; CPython f(5) returns False (rt44 j51506)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ ensures \result == True
def f(n: int) -> bool:
    a = n + 1000
    b = n + 1000
    return a is b


if __name__ == "__main__":
    try:
        r = f(5)
        if not (r == True):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
