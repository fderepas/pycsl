r"""Test 8144 -- route #511 (expected FAIL: PROVED at base, REFUSED PYCSL-R511-LOCAL-CLASS-NAME-NOT-UNIQUE): `class g: pass` in f hides the program function `g`; `g(n) + 1` was lowered as the call of the module `g`; CPython raises TypeError (g() takes no arguments)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

def g(n: int) -> int:
    return n


#@ no_exception \all
def f(n: int) -> int:
    class g:
        pass
    return g(n) + 1


if __name__ == "__main__":
    try:
        r = f(1)
        if not (r == 2):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
