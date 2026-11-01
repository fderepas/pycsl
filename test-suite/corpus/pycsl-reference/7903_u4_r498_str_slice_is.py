r"""Test 7903 -- route #498 (expected FAIL: PROVED at base, REFUSED PYCSL-R498-IS-ON-FRESH-VALUE): `s[0:2] is s[0:2]` claimed True; CPython f('abc') returns False (rt44 j51514)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ ensures \result == True
def f(s: str) -> bool:
    return s[0:2] is s[0:2]


if __name__ == "__main__":
    try:
        r = f('abc')
        if not (r == True):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
