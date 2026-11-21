r"""Test 7906 -- route #498 (expected FAIL: PROVED at base, REFUSED PYCSL-R498-IS-ON-FRESH-VALUE): `-n is -n` in an if-expression test claimed 1; CPython f(1000) returns 0 (rt44 j51510 / j51505)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ ensures \result == 1
def f(n: int) -> int:
    return 1 if -n is -n else 0


if __name__ == "__main__":
    try:
        r = f(1000)
        if not (r == 1):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
