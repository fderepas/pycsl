r"""Test 7920 -- route #499 (expected FAIL: PROVED at base, REFUSED PYCSL-R499-EXEC-IN-FUNCTION-SCOPE): `x = 1; exec("x = 2"); return x` claimed 2; CPython (PEP 667 locals snapshot) returns 1 (rt44 g517/e51700)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional


#@ ensures \result == 2
def f(n: int) -> int:
    x = 1
    exec("x = 2")
    return x


if __name__ == "__main__":
    try:
        r = f(0)
        if not (r == 2):
            print("VIOLATION contract", repr(r)[:60])
            raise SystemExit
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
