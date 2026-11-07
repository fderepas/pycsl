r"""Test 7901 -- route #498 (expected FAIL: PROVED at base, REFUSED PYCSL-R498-IS-ON-FRESH-VALUE): `(n * 2) is not (n + n)` claimed False; CPython f(1000) returns True (rt44 j51501 / j51502)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ ensures \result == False
def f(n: int) -> bool:
    return (n * 2) is not (n + n)


if __name__ == "__main__":
    try:
        r = f(1000)
        if not (r == False):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
