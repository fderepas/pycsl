r"""Test 8149 -- route #511 (expected FAIL: NOT PROVED at base (opaque read), REFUSED by name PYCSL-R511-LOCAL-CLASS-NAME-NOT-UNIQUE): a local `class Q` of `mk` is read in ANOTHER function f, where CPython raises NameError; the model resolves the name to the lifted class
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

def mk() -> int:
    class Q:
        v = 1
    return 0


#@ ensures \result == 1
def f() -> int:
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
