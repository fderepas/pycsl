r"""Test 7902 -- route #498 (expected FAIL: PROVED at base, REFUSED PYCSL-R498-IS-ON-FRESH-VALUE): `(s + "x") is (s + "x")` claimed True; CPython f('ab') returns False (rt44 j51512)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ ensures \result == True
def f(s: str) -> bool:
    return (s + "x") is (s + "x")


if __name__ == "__main__":
    try:
        r = f('ab')
        if not (r == True):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
