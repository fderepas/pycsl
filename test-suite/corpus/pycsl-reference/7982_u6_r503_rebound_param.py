r"""Test 7982 -- route #503 (expected FAIL: NOT PROVED at base, REFUSED PYCSL-R503-IS-ALIAS-ROOT-REBOUND by name): a rebound PARAMETER is no single-binding root: `b = a; a = b + 0; return a is b` claimed True; CPython f(5000) returns False
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ ensures \result == True
def f(a) -> bool:
    b = a
    a = b + 0
    return a is b


if __name__ == "__main__":
    try:
        r = f(5000)
        if not (r == True):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
