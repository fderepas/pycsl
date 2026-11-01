r"""Test 7908 -- route #498 (expected FAIL: PROVED at base, REFUSED PYCSL-R498-IS-ON-FRESH-VALUE): `a is b` on `object`-annotated parameters under `requires a == b`, claimed True; CPython g(1000 + n, 1001) with n = 1 returns False
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ requires a == b
#@ ensures \result == True
def g(a: object, b: object) -> bool:
    return a is b


if __name__ == "__main__":
    try:
        r = g(1000 + int('1'), 1001)
        if not (r == True):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
