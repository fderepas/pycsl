r"""Test 8146 -- route #511 (expected FAIL: PROVED at base, REFUSED PYCSL-R511-LOCAL-CLASS-NAME-NOT-UNIQUE): `x = 5; class x: pass; return x` under `ensures \result == 5`; CPython returns the class
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

#@ ensures \result == 5
def f() -> int:
    x = 5
    class x:
        pass
    return x


if __name__ == "__main__":
    try:
        r = f()
        if not (r == 5):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
