r"""Test 8148 -- route #511 (expected FAIL: NOT PROVED at base (opaque read), REFUSED by name PYCSL-R511-LOCAL-CLASS-NAME-NOT-UNIQUE): two functions each define their own local `class Q` (v = 1 and v = 2); the model keeps one program-wide `Q`; `ensures \result == 1` over `Q.v` in f
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

#@ ensures \result == 1
def f() -> int:
    class Q:
        v = 1
    return Q.v


def mk() -> int:
    class Q:
        v = 2
    return Q.v


if __name__ == "__main__":
    try:
        r = f()
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
