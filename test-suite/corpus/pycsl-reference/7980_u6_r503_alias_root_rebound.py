r"""Test 7980 -- route #503 (expected FAIL: PROVED at base, REFUSED PYCSL-R503-IS-ALIAS-ROOT-REBOUND): `a = n + 1000; b = a; a = n + 1000; return a is b` claimed True; CPython f(5) returns False (rt45 g601/b60100)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ ensures \result == True
def f(n: int) -> bool:
    a = n + 1000
    b = a
    a = n + 1000
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
