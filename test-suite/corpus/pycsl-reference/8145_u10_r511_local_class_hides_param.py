r"""Test 8145 -- route #511 (expected FAIL: PROVED at base, REFUSED PYCSL-R511-LOCAL-CLASS-NAME-NOT-UNIQUE): `class n: pass` rebinds the parameter `n`; `n + 1` was lowered over the int parameter; CPython raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

#@ no_exception \all
def f(n: int) -> int:
    class n:
        pass
    return n + 1


if __name__ == "__main__":
    try:
        r = f(1)
        if not (r == 2):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
