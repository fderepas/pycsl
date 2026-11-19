r"""Test 7981 -- route #503 (expected FAIL: PROVED at base, REFUSED PYCSL-R503-IS-ALIAS-ROOT-REBOUND): `a = n * 1000; b = a; a = n * 1000; return a is not b` claimed False; CPython f(7) returns True (rt45 g601/b60102)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ ensures \result == False
def f(n: int) -> bool:
    a = n * 1000
    b = a
    a = n * 1000
    return a is not b


if __name__ == "__main__":
    try:
        r = f(7)
        if not (r == False):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
